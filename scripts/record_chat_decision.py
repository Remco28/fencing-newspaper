#!/usr/bin/env python3
"""Record budget decisions Frank gives in chat (not via the budget page) as the next decision entry.

The budget page starts from the LAST entry in staging/weeks/<pile>/budget-versions.json, so a chat
decision must carry the full page state forward. This copies the previous decision (includes,
excludes, order, photo picks, slot notes, answers, notes, publish date), applies the slot changes
you pass, and appends it with source "chat" and Frank's words verbatim. Item/lineup edits that the
decision implies (closing questions, new rows) are still made by hand in items.json and the lineup.

  python3 scripts/record_chat_decision.py --at 2026-11-02T20:56:00-05:00 \
      --text "Frank's words, verbatim" [--include SLOT ...] [--exclude SLOT ...] \
      [--answer SLOT "question" "answer"] [--change "what Clark applied"] [--dry-run]

Then rebuild: python3 scripts/build_budget_html.py  (the new decision bumps the version).
"""
import argparse, copy, json, os
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CARRY = ("publishDate", "included", "excluded", "photoIncludes", "slotNotes", "answers", "notes", "order")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--staging-week", type=Path, default=Path(os.environ.get("GAZETTE_STAGING_WEEK") or (REPO / "staging" / "weeks" / "next")))
    ap.add_argument("--at", required=True, help="when Frank said it (ISO with offset); shown as 'decisions captured through'")
    ap.add_argument("--text", required=True, help="Frank's chat message, verbatim")
    ap.add_argument("--from", dest="who", default="frank")
    ap.add_argument("--include", action="append", default=[], metavar="SLOT")
    ap.add_argument("--exclude", action="append", default=[], metavar="SLOT")
    ap.add_argument("--after", action="append", default=[], metavar="SLOT=PREV", help="place a newly included slot after PREV in the order")
    ap.add_argument("--answer", action="append", nargs=3, default=[], metavar=("SLOT", "QUESTION", "ANSWER"))
    ap.add_argument("--change", action="append", default=[], help="one line per edit Clark applied for this decision")
    ap.add_argument("--now", help="ISO timestamp instead of the clock (tests)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    datetime.fromisoformat(a.at)  # validate
    path = a.staging_week / "budget-versions.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    decs = doc.setdefault("decisions", [])
    prev = decs[-1] if decs else {}
    d = {k: copy.deepcopy(prev[k]) for k in CARRY if k in prev}
    inc, exc, order = d.setdefault("included", []), d.setdefault("excluded", []), d.setdefault("order", [])
    for s in a.include:
        if s in exc: exc.remove(s)
        if s not in inc: inc.append(s)
    for s in a.exclude:
        if s in inc: inc.remove(s)
        if s not in exc: exc.append(s)
    for pair in a.after:
        s, p = pair.split("=", 1)
        if s in order: order.remove(s)
        order.insert(order.index(p) + 1 if p in order else len(order), s)
    for s in a.include:
        if s not in order: order.append(s)
    ans = d.setdefault("answers", [])
    for slot, q, ansr in a.answer:
        ans.append({"slot": slot, "question": q, "answer": ansr, "via": "chat"})
    now = a.now or datetime.now().astimezone().isoformat(timespec="seconds")
    entry = {"at": now, "client_submitted_at": a.at, "source": f"chat:{a.who}:{a.at}", "kind": "chat",
             "chat": {"from": a.who, "at": a.at, "text": a.text}, "carried_from": len(decs), **d,
             "changes": a.change}
    print(f"decision #{len(decs) + 1} (chat, {a.at}); carried from #{len(decs)}")
    print(f"  include +{a.include}  exclude +{a.exclude}  answers +{len(a.answer)}  changes {len(a.change)}")
    if a.dry_run:
        print("  DRY RUN — nothing written"); return
    decs.append(entry)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log = a.staging_week / "vet-log.jsonl"
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"at": now, "kind": "chat-decision", "decision": len(decs), "from": a.who, "said_at": a.at, "text": a.text, "changes": a.change}, ensure_ascii=False) + "\n")
    print(f"  wrote {path.relative_to(REPO)} and {log.relative_to(REPO)} (+1 line)")


if __name__ == "__main__":
    main()
