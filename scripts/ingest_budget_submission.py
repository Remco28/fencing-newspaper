#!/usr/bin/env python3
"""Apply a submission from the standalone budget page (budget-submission-no-<N>-<date>.json).

Does exactly what budget-demo/server.py does for POST /submit and POST /vet:
  - writes <submissions>/budget-<stamp>.json and <submissions>/approvals.json
    (pretend defaults to true if absent; submittedAt = ingest time, as the server stamps it;
    the page's own timestamp is kept as clientSubmittedAt)
  - for every `vets` entry: sets vetted/vetted_at/vetted_by="frank"/vet_notes on the item in
    <staging-week>/items.json and appends the vet-log entry to <staging-week>/vet-log.jsonl AND
    <submissions>/vet-log.jsonl (source "budget-page-standalone"). Ids not in items.json (e.g. a
    photo's media id) are reported as not found, like the server's 404 — nothing else is touched.

Usage:
  python3 scripts/ingest_budget_submission.py SUBMISSION.json [--dry-run] [--force]
         [--staging-week DIR] [--submissions DIR] [--lineup FILE] [--now ISO]
SUBMISSION may be "-" (stdin); text pasted from chat with ``` fences or chatter around the JSON is OK.
Defaults match server.py: GAZETTE_STAGING_WEEK (staging/weeks/next), GAZETTE_SUBMISSIONS
(budget-demo/submissions), GAZETTE_LINEUP (budget-demo/practice-lineup.json).
Refuses a submission whose issue number / targetWeek doesn't match the lineup unless --force.
Re-ingesting the same file just re-applies (vet-log notes already_vetted).
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = "budget-page-standalone"


def die(msg: str, code: int = 1) -> None:
    print(f"ingest_budget_submission: error: {msg}", file=sys.stderr)
    sys.exit(code)


def rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(REPO))
    except ValueError:
        return str(p)


def parse_submission(text: str) -> dict:
    """The JSON object; tolerates ```json fences / chat text around it (pasted submissions)."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            die("submission is not JSON (no {...} object found)")
        try:
            data = json.loads(text[start:end + 1])
        except json.JSONDecodeError as exc:
            die(f"submission is not valid JSON: {exc}")
    if not isinstance(data, dict):
        die("submission must be a JSON object")
    return data


def validate(p: dict) -> list[str]:
    errs = []
    for k in ("publishDate", "includedSlots", "excludedSlots"):
        if k not in p:
            errs.append(f"missing required key '{k}'")
    if "publishDate" in p and not (isinstance(p["publishDate"], str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p["publishDate"])):
        errs.append("publishDate must be YYYY-MM-DD")
    for k in ("includedSlots", "excludedSlots"):
        if k in p:
            if not isinstance(p[k], list) or not all(isinstance(e, dict) for e in p[k]):
                errs.append(f"{k} must be a list of objects")
    vets = p.get("vets", [])
    if not isinstance(vets, list):
        errs.append("vets must be a list")
    else:
        for i, v in enumerate(vets):
            if not isinstance(v, dict) or not isinstance(v.get("id"), str) or not v["id"].strip():
                errs.append(f"vets[{i}] needs a non-empty string id")
            elif v.get("vet_notes") is not None and not isinstance(v["vet_notes"], str):
                errs.append(f"vets[{i}].vet_notes must be a string")
    shapes = {"photoIncludes": list, "slotNotes": dict, "answers": list, "order": list, "notes": str}
    for k, t in shapes.items():
        if p.get(k) is not None and not isinstance(p[k], t):
            errs.append(f"{k} must be a {t.__name__}")
    if isinstance(p.get("issue"), (str, int, float, list)):
        errs.append("issue must be an object")
    return errs


def lineup_mismatch(p: dict, lineup: dict) -> list[str]:
    out = []
    want_n = (lineup.get("issue") or {}).get("number")
    got_n = (p.get("issue") or {}).get("number") if isinstance(p.get("issue"), dict) else None
    if want_n is not None and got_n != want_n:
        out.append(f"issue number {got_n!r} != lineup issue {want_n!r}")
    want_w, got_w = lineup.get("target_week") or "next", p.get("targetWeek")
    if got_w != want_w:
        out.append(f"targetWeek {got_w!r} != lineup target_week {want_w!r}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Apply a standalone budget-page submission (like server.py /submit + /vet).")
    ap.add_argument("submission", help="submission .json file, or - for stdin")
    ap.add_argument("--staging-week", type=Path, default=Path(os.environ.get("GAZETTE_STAGING_WEEK") or (REPO / "staging" / "weeks" / "next")))
    ap.add_argument("--submissions", type=Path, default=Path(os.environ.get("GAZETTE_SUBMISSIONS") or (REPO / "budget-demo" / "submissions")))
    ap.add_argument("--lineup", type=Path, default=Path(os.environ.get("GAZETTE_LINEUP") or (REPO / "budget-demo" / "practice-lineup.json")))
    ap.add_argument("--now", help="ISO timestamp to use instead of the clock (tests)")
    ap.add_argument("--dry-run", action="store_true", help="print what would change; write nothing")
    ap.add_argument("--force", action="store_true", help="apply even if issue/targetWeek don't match the lineup")
    args = ap.parse_args()

    if args.now:
        try:
            now = datetime.fromisoformat(args.now)
        except ValueError:
            die(f"--now is not an ISO timestamp: {args.now}")
        now = now if now.tzinfo else now.astimezone()
    else:
        now = datetime.now().astimezone()
    stamp = now.strftime("%Y%m%d-%H%M%S")
    now_iso = now.isoformat(timespec="seconds")

    if args.submission == "-":
        text, src_name = sys.stdin.read(), "<stdin>"
    else:
        src = Path(args.submission)
        if not src.is_file():
            die(f"submission file not found: {src}")
        text, src_name = src.read_text(encoding="utf-8"), src.name
    payload = parse_submission(text)
    errs = validate(payload)
    if errs:
        die("invalid submission:\n  - " + "\n  - ".join(errs))

    lineup = {}
    if args.lineup.is_file():
        try:
            lineup = json.loads(args.lineup.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            die(f"lineup is not valid JSON ({args.lineup}): {exc}")
    else:
        print(f"warning: lineup not found ({args.lineup}); skipping the issue/targetWeek check", file=sys.stderr)
    mism = lineup_mismatch(payload, lineup) if lineup else []
    if mism and not args.force:
        die("submission doesn't match the lineup (" + "; ".join(mism) + "). Wrong week's file? Re-run with --force to apply anyway.", 2)

    week, subs = args.staging_week.resolve(), args.submissions.resolve()
    items_path = week / "items.json"
    items_doc = None
    if items_path.is_file():
        try:
            items_doc = json.loads(items_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            die(f"{items_path} is not valid JSON: {exc}")
        if not isinstance(items_doc, dict) or not isinstance(items_doc.get("items"), list):
            die(f"{items_path} malformed (no 'items' list)")
    manifest_ids = set()
    try:
        manifest = json.loads((week / "media" / "manifest.json").read_text(encoding="utf-8"))
        manifest_ids = {m.get("id") for m in manifest.get("items", []) if isinstance(m, dict)}
    except (OSError, json.JSONDecodeError, AttributeError):
        pass

    # ---- the stored submission (server /submit) ----
    stored = copy.deepcopy(payload)
    stored.setdefault("pretend", True)
    if payload.get("submittedAt"):
        stored["clientSubmittedAt"] = payload["submittedAt"]
    stored["submittedAt"] = now_iso
    stored_text = json.dumps(stored, indent=2, ensure_ascii=False) + "\n"
    stamped = subs / f"budget-{stamp}.json"
    approvals = subs / "approvals.json"

    # ---- vets (server /vet, once per id) ----
    vets, seen = [], {}
    for v in payload.get("vets", []):
        seen[v["id"].strip()] = (v.get("vet_notes") or "").strip()
    vets = list(seen.items())
    by_id = {i.get("id"): i for i in (items_doc or {}).get("items", []) if isinstance(i, dict)}
    applied, not_found, log_entries = [], [], []
    for item_id, vet_notes in vets:
        found = by_id.get(item_id)
        if found is None:
            not_found.append(item_id)
            continue
        already = bool(found.get("vetted"))
        before = {k: found.get(k) for k in ("vetted", "vetted_at", "vetted_by", "vet_notes")}
        found["vetted"] = True
        found["vetted_at"] = now_iso
        found["vetted_by"] = "frank"
        if vet_notes:
            found["vet_notes"] = vet_notes
        elif "vet_notes" not in found:
            found["vet_notes"] = None
        applied.append((item_id, already, before, vet_notes))
        log_entries.append({
            "id": item_id, "vetted": True, "vetted_at": found["vetted_at"], "vetted_by": "frank",
            "vet_notes": found.get("vet_notes"), "already_vetted": already, "kind": found.get("kind"),
            "body": found.get("body"), "source": SOURCE,
        })

    # ---- warnings: included slots whose item isn't vetted on file or in this submission ----
    warnings = [f"lineup mismatch ignored (--force): {m}" for m in mism]
    if items_doc is None:
        warnings.append(f"no items.json at {rel(items_path)}: vets can't be applied")
    vetted_now = {a[0] for a in applied}
    for e in payload["includedSlots"]:
        iid = e.get("itemId")
        if iid and iid not in vetted_now and not (by_id.get(iid) or {}).get("vetted"):
            warnings.append(f"included slot {e.get('slot')!r} item {iid} is " + ("not in staging" if iid not in by_id else "not vetted"))

    # ---- write ----
    if not args.dry_run:
        subs.mkdir(parents=True, exist_ok=True)
        stamped.write_text(stored_text, encoding="utf-8")
        approvals.write_text(stored_text, encoding="utf-8")
        if applied:
            items_doc["updated_at"] = now_iso
            items_path.write_text(json.dumps(items_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            week.mkdir(parents=True, exist_ok=True)
            lines = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in log_entries)
            for log in (week / "vet-log.jsonl", subs / "vet-log.jsonl"):
                with log.open("a", encoding="utf-8") as fh:
                    fh.write(lines)

    # ---- summary ----
    iss = payload.get("issue") or {}
    tag = "DRY RUN — nothing written" if args.dry_run else "applied"
    print(f"Budget submission {src_name}: {tag}")
    print(f"  Issue: {iss.get('label') or iss.get('number', '?')} ({iss.get('week', '')}) · targetWeek {payload.get('targetWeek')} · "
          f"page {payload.get('pageVersion', '?')} · {'PRACTICE' if payload.get('practice') else 'real'}"
          f"{' · pretend' if stored.get('pretend') else ''}")
    print(f"  Publish date: {payload['publishDate']} · submitted on page {payload.get('submittedAt') or '?'}")
    inc = payload["includedSlots"]
    exc = [e for e in payload["excludedSlots"] if not e.get("empty")]
    print(f"  Included ({len(inc)}):")
    for e in inc:
        print(f"    + {e.get('slot')}: {e.get('headline') or e.get('name')}")
    print(f"  Excluded: {len(exc)} (+ {len(payload['excludedSlots']) - len(exc)} empty slots)")
    if payload.get("photoIncludes"):
        print(f"  Photos in: {', '.join(payload['photoIncludes'])}")
    print(f"  Vets: {len(applied)} applied, {len(not_found)} not found")
    for item_id, already, before, notes in applied:
        print(f"    ✓ {item_id}: vetted {before['vetted']} -> True" + (" (already vetted; re-applied)" if already else "") +
              (f" · note: {notes}" if notes else ""))
    for item_id in not_found:
        kind = "media id (photo) — " if item_id in manifest_ids else ""
        print(f"    ? {item_id}: not found in items.json ({kind}recorded in approvals.json only)")
    answers = payload.get("answers") or []
    if answers:
        print(f"  Answers ({len(answers)}):")
        for a in answers:
            print(f"    {a.get('slot')}: {a.get('question')}\n      -> {a.get('answer')}")
    for k, v in (payload.get("slotNotes") or {}).items():
        print(f"  Note on {k}: {v}")
    if payload.get("notes"):
        print(f"  Notes: {payload['notes']}")
    for w in warnings:
        print(f"  warning: {w}")
    verb = "would write" if args.dry_run else "wrote"
    print(f"  {verb}: {rel(stamped)}, {rel(approvals)}" +
          (f", {rel(items_path)}, {rel(week / 'vet-log.jsonl')}, {rel(subs / 'vet-log.jsonl')} (+{len(log_entries)} lines)" if applied else ""))


if __name__ == "__main__":
    main()
