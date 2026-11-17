#!/usr/bin/env python3
"""Apply a submission from the standalone budget page (budget-submission-no-<N>-<date>.json).

Does exactly what budget-demo/server.py does for POST /submit and POST /vet:
  - writes <submissions>/budget-<stamp>.json and <submissions>/approvals.json
    (pretend defaults to true if absent; submittedAt = ingest time, as the server stamps it;
    the page's own timestamp is kept as clientSubmittedAt)
  - for every `vets` entry: sets vetted/vetted_at/vetted_by="frank"/vet_notes on the item in
    <staging-week>/items.json and appends the vet-log entry to <staging-week>/vet-log.jsonl AND
    <submissions>/vet-log.jsonl (source "budget-page-standalone"). A photo's media id is not in
    items.json: its vet is written to <staging-week>/media/manifest.json the same way (vetted,
    vetted_at, vetted_by, vet_notes) and logged with kind "media", so the next budget build shows
    it vetted and does not ask again. Ids found in neither file are reported as not found.
  - refuses (exit 4, writes nothing) if an included slot's item, or a photo in photoIncludes, is
    in staging and still unvetted after this submission's vets are applied. Missing ids (an older
    issue's items) stay warnings, so Nos. 1–6 submissions still ingest.
  - appends the decisions (includes/excludes, photo picks, optional pages / resize / layout, slot notes,
    answers, notes, vets) to <staging-week>/budget-versions.json "decisions"; build_budget_html.py
    starts the next numbered budget (vN) from the latest entry, so a rebuild never drops what
    Frank already decided. Unvetted photos are never recorded in photoIncludes, so they are never
    queued for the next build.

Usage:
  python3 scripts/ingest_budget_submission.py SUBMISSION.json [--dry-run] [--force]
         [--staging-week DIR] [--submissions DIR] [--lineup FILE] [--now ISO]
SUBMISSION may be "-" (stdin); text pasted from chat with ``` fences or chatter around the JSON is OK.
Defaults match server.py: GAZETTE_STAGING_WEEK (staging/weeks/next), GAZETTE_SUBMISSIONS
(budget-demo/submissions), GAZETTE_LINEUP (budget-demo/practice-lineup.json).
Refuses a submission whose issue number / targetWeek doesn't match the lineup unless --force.
Re-ingesting the same file just re-applies (vet-log notes already_vetted).

Optional fields from the Budget page (pageVersion budget-paper-v1); submissions without them ingest as before:
  publishDateAlt  YYYY-MM-DD or null — Frank's alternate run date; stored on the decision when present.
  budgetVersion   the vN the page was built as, and
  dataVersion     the build's data hash — both recorded on the decision for the record. Neither is checked:
                  a missing or older budgetVersion never stops an ingest.
  pages           {slots: {slotKey: 1|2 or {page, span, widthIn, heightIn}}, photos: {mediaId: same}} —
                  where Frank put each included block, and (when he resized art) its column span and
                  size in inches. A bare 1|2 means page only. Stored when present; ignored when absent.
  resize          {slotKey: {direction: 'expand'|'shrink', target, ...}} — grow/shrink requests for
                  Clark to rewrite to length. Stored when present; ignored when absent.
  layout          {slotKey|mediaId: 'wide'|'tall'} — chosen layout variant (names shared with compose/).
                  Stored when present; ignored when absent.
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
    alt = p.get("publishDateAlt")  # optional; null = "no alternate"
    if alt is not None and not (isinstance(alt, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", alt)):
        errs.append("publishDateAlt must be YYYY-MM-DD or null")
    if isinstance(p.get("issue"), (str, int, float, list)):
        errs.append("issue must be an object")
    errs.extend(validate_pages(p.get("pages")))
    errs.extend(validate_resize(p.get("resize")))
    errs.extend(validate_layout(p.get("layout")))
    return errs


def page_value_ok(v) -> bool:
    """A page placement is 1 or 2, or {page: 1|2, span?, widthIn?, heightIn?} when art was resized."""
    if v in (1, 2):
        return True
    if not isinstance(v, dict):
        return False
    if v.get("page") not in (1, 2):
        return False
    if "span" in v and not (isinstance(v["span"], int) and 1 <= v["span"] <= 3):
        return False
    for k in ("widthIn", "heightIn"):
        if k in v and not isinstance(v[k], (int, float)):
            return False
    return True


def validate_pages(pages) -> list[str]:
    """Optional. Absent or null is fine (older submissions). Shape: {slots:{key:1|2 or size object},
    photos:{id: same}}. A flat map is also accepted and stored as pages.slots."""
    if pages is None:
        return []
    if not isinstance(pages, dict):
        return ["pages must be an object or null"]
    errs = []
    def check_map(g, label):
        if not isinstance(g, dict):
            errs.append(f"{label} must be an object")
            return
        for k, v in g.items():
            if not isinstance(k, str) or not k.strip():
                errs.append(f"{label} keys must be non-empty strings")
            elif not page_value_ok(v):
                errs.append(f"{label}.{k} must be 1 or 2, or an object {{page, span?, widthIn?, heightIn?}}")
    if "slots" in pages or "photos" in pages:
        if "slots" in pages and pages["slots"] is not None:
            check_map(pages["slots"], "pages.slots")
        if "photos" in pages and pages["photos"] is not None:
            check_map(pages["photos"], "pages.photos")
    else:
        check_map(pages, "pages")
    return errs


def validate_resize(resize) -> list[str]:
    """Optional. {slotKey: {direction: 'expand'|'shrink', target?, toWords?, ...}}."""
    if resize is None:
        return []
    if not isinstance(resize, dict):
        return ["resize must be an object or null"]
    errs = []
    for k, v in resize.items():
        if not isinstance(k, str) or not k.strip():
            errs.append("resize keys must be non-empty strings")
            continue
        if not isinstance(v, dict):
            errs.append(f"resize.{k} must be an object")
            continue
        d = v.get("direction")
        if d is not None and d not in ("expand", "shrink"):
            errs.append(f"resize.{k}.direction must be 'expand' or 'shrink'")
        if "target" in v and v["target"] is not None and not isinstance(v["target"], (str, int, float)):
            errs.append(f"resize.{k}.target must be a string or number")
    return errs


def validate_layout(layout) -> list[str]:
    """Optional. {slotKey|mediaId: 'wide'|'tall'}. Names are shared with compose/."""
    if layout is None:
        return []
    if not isinstance(layout, dict):
        return ["layout must be an object or null"]
    errs = []
    for k, v in layout.items():
        if not isinstance(k, str) or not k.strip():
            errs.append("layout keys must be non-empty strings")
        elif v not in ("wide", "tall"):
            errs.append(f"layout.{k} must be 'wide' or 'tall'")
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
    manifest_path, manifest, media_by_id = week / "media" / "manifest.json", None, {}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        media_by_id = {m.get("id"): m for m in manifest.get("items", []) if isinstance(m, dict) and m.get("id")}
    except (OSError, json.JSONDecodeError, AttributeError):
        manifest = None
    manifest_ids = set(media_by_id)

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
    applied, media_applied, not_found, photo_vets, log_entries = [], [], [], [], []
    for item_id, vet_notes in vets:
        found = by_id.get(item_id)
        if found is None and item_id in manifest_ids:
            # A photo (media) id: the vet goes on its media/manifest.json entry, which is where the
            # budget page reads a photo's vetted flag from. Same fields and note-append rule as an item.
            found, target = media_by_id[item_id], "media"
            photo_vets.append(item_id)
        elif found is None:
            not_found.append(item_id)
            continue
        else:
            target = "item"
        already = bool(found.get("vetted"))
        before = {k: found.get(k) for k in ("vetted", "vetted_at", "vetted_by", "vet_notes")}
        found["vetted"] = True
        found["vetted_at"] = now_iso
        found["vetted_by"] = "frank"
        if vet_notes:
            # append (never replace) so Clark's own history notes survive; skip an identical re-ingest
            line = f"[{now_iso[:10]}] Frank: {vet_notes}"
            old = found.get("vet_notes")
            if not old:
                found["vet_notes"] = line
            elif line not in old.split("\n"):
                found["vet_notes"] = old.rstrip("\n") + "\n" + line
        elif "vet_notes" not in found:
            found["vet_notes"] = None
        if target == "item":
            applied.append((item_id, already, before, vet_notes))
        else:
            media_applied.append((item_id, already, before, vet_notes))
        log_entries.append({
            "id": item_id, "vetted": True, "vetted_at": found["vetted_at"], "vetted_by": "frank",
            "vet_notes": found.get("vet_notes"), "already_vetted": already,
            "kind": found.get("kind") if target == "item" else "media",
            "body": found.get("body") if target == "item" else (found.get("caption") or found.get("filename")),
            "source": SOURCE,
        })

    # ---- warnings, then refuse unvetted includes (exit 4, write nothing) ----
    warnings = [f"lineup mismatch ignored (--force): {m}" for m in mism]
    if items_doc is None:
        warnings.append(f"no items.json at {rel(items_path)}: vets can't be applied")
    vetted_now = {a[0] for a in applied} | {a[0] for a in media_applied}
    unvetted = []
    for e in payload["includedSlots"]:
        iid = e.get("itemId")
        if not iid:
            continue
        if iid not in by_id:
            warnings.append(f"included slot {e.get('slot')!r} item {iid} is not in staging")
        elif iid not in vetted_now and not by_id[iid].get("vetted"):
            unvetted.append(f"included slot {e.get('slot')!r} item {iid} is not vetted")
    for pid in payload.get("photoIncludes") or []:
        if pid not in media_by_id:
            warnings.append(f"photoIncludes {pid} is not in the media manifest")
        elif pid not in vetted_now and not media_by_id[pid].get("vetted"):
            unvetted.append(f"photoIncludes {pid} is not vetted")
    if unvetted:
        die("unvetted items cannot run (vet them in this submission or leave them out):\n  - " +
            "\n  - ".join(unvetted) + "\n  Nothing written.", 4)

    # ---- decision log entry (budget versions; build_budget_html.py reads the latest) ----
    versions_path = week / "budget-versions.json"
    decision = {
        "at": now_iso, "client_submitted_at": payload.get("submittedAt"), "source": src_name, "stored": rel(stamped),
        "publishDate": payload["publishDate"],
        "included": [e.get("slot") for e in payload["includedSlots"]],
        # unticked on purpose (vetted but left out); unvetted-and-out isn't a decision to keep it out
        "excluded": [e.get("slot") for e in payload["excludedSlots"] if not e.get("empty") and e.get("vetted")],
        "photoIncludes": payload.get("photoIncludes") or [], "slotNotes": payload.get("slotNotes") or {},
        "answers": payload.get("answers") or [], "notes": payload.get("notes") or "", "order": payload.get("order") or [],
        "vets": [v[0] for v in vets],
    }
    # optional, recorded only when the page sent them (older pages and Nos. 1-6 don't)
    if "publishDateAlt" in payload:
        decision["publishDateAlt"] = payload["publishDateAlt"]
    for k in ("budgetVersion", "dataVersion", "pageVersion"):
        if payload.get(k) is not None:
            decision[k] = payload[k]
    if "pages" in payload:
        decision["pages"] = payload["pages"]
    if "resize" in payload:
        decision["resize"] = payload["resize"]
    if "layout" in payload:
        decision["layout"] = payload["layout"]
    vdoc = None
    if versions_path.is_file():
        try:
            vdoc = json.loads(versions_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            die(f"{versions_path} is not valid JSON: {exc}")
    iss_n, pub_d = (lineup.get("issue") or {}).get("number"), (lineup.get("publish") or {}).get("date")
    if not isinstance(vdoc, dict) or (iss_n is not None and vdoc.get("issue") != iss_n):
        vdoc = {"issue": iss_n, "publish": pub_d, "versions": [], "decisions": []}
    vdoc.setdefault("versions", []); vdoc.setdefault("decisions", [])
    vdoc["decisions"].append(decision)

    # ---- write ----
    if not args.dry_run:
        versions_path.write_text(json.dumps(vdoc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        subs.mkdir(parents=True, exist_ok=True)
        stamped.write_text(stored_text, encoding="utf-8")
        approvals.write_text(stored_text, encoding="utf-8")
        if media_applied:
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if applied:
            items_doc["updated_at"] = now_iso
            items_path.write_text(json.dumps(items_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if log_entries:
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
    print(f"  Publish date: {payload['publishDate']}" +
          (f" · alternate {payload['publishDateAlt'] or 'none'}" if "publishDateAlt" in payload else "") +
          f" · submitted on page {payload.get('submittedAt') or '?'}" +
          (f" · built as budget v{payload['budgetVersion']}" if payload.get("budgetVersion") is not None else "") +
          (f" · data {payload['dataVersion']}" if payload.get("dataVersion") else ""))
    inc = payload["includedSlots"]
    exc = [e for e in payload["excludedSlots"] if not e.get("empty")]
    print(f"  Included ({len(inc)}):")
    for e in inc:
        print(f"    + {e.get('slot')}: {e.get('headline') or e.get('name')}")
    print(f"  Excluded: {len(exc)} (+ {len(payload['excludedSlots']) - len(exc)} empty slots)")
    if payload.get("photoIncludes"):
        print(f"  Photos in: {', '.join(payload['photoIncludes'])}")
    print(f"  Vets: {len(applied)} item(s) applied, {len(media_applied)} photo(s) applied, {len(not_found)} not found")
    for item_id, already, before, notes in applied + media_applied:
        print(f"    ✓ {item_id}: vetted {before['vetted']} -> True" + (" (already vetted; re-applied)" if already else "") +
              (f" · note: {notes}" if notes else ""))
    for item_id in not_found:
        print(f"    ? {item_id}: not found in items.json or media/manifest.json (recorded in approvals.json only)")
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
    print(f"  {verb}: {rel(versions_path)} (decision #{len(vdoc['decisions'])}; next build is the next budget version), {rel(stamped)}, {rel(approvals)}" +
          (f", {rel(items_path)}" if applied else "") +
          (f", {rel(manifest_path)}" if media_applied else "") +
          (f", {rel(week / 'vet-log.jsonl')}, {rel(subs / 'vet-log.jsonl')} (+{len(log_entries)} lines)" if log_entries else ""))


if __name__ == "__main__":
    main()
