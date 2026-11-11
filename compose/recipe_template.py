#!/usr/bin/env python3
"""Starter recipe for a new En Garde Gazette issue.

Copy this file to issues/<YYYY-MM-DD>/recipe/compose.py after Frank approves the
budget, then fill in data and block order. Do not scrape CSS from an old issue.html.
Do not hardcode an absolute repo path.

    python3 issues/<date>/recipe/compose.py x
    python3 compose/render.py issues/<date>/issue.html issues/<date>/en-garde-gazette-no-<N>-<date>.pdf --author="Nico's Dad"
    pdftoppm -r 200 -png issues/<date>/en-garde-gazette-no-<N>-<date>.pdf issues/<date>/preview

`x` loads recipe/overrides.json. An APPROVED issue.json refuses an in-place write
unless you pass --force; use --out=PATH for a trial.
"""
import sys
from pathlib import Path

def _repo():
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "compose" / "gazette.py").is_file():
            return parent
    raise SystemExit("compose/gazette.py not found above " + str(here))

REPO = _repo()
sys.path.insert(0, str(REPO / "compose"))
from gazette import *  # noqa: E402

ISSUE = "issues/YYYY-MM-DD"          # publish-date folder
# Prefer a frozen lineup snapshot when one exists; the live practice-lineup.json
# is whatever week is in progress and will corrupt a later rebuild.
LINEUP = "budget-demo/archive/practice-lineup-issueN-YYYY-MM-DD.json"
WEEK = "staging/weeks/YYYY-MM-DD"    # or staging/weeks/next before the roll

# items = {i["id"]: i for i in load(WEEK + "/items.json")["items"]}
# lineup = load(LINEUP if (ROOT / LINEUP).is_file() else "budget-demo/practice-lineup.json")

def main():
    # Build with piece(), paras(), results_table(), tourney(), board_split(), box(),
    # photo(), textcols(), cols3(), page(), masthead(), dateline(), footer().
    # Keep slot order to the approved budget; do not invent copy to fill space.
    title = "En Garde Gazette — Vol. I No. N — Month D, YYYY"
    pages = [
        # page(masthead() + "\n" + dateline("Weekday Edition", "Vol. I — No. N · Chatham, N.J. · Month D, YYYY") + ... + footer(N)),
        # page(..., cls="fit"),
    ]
    doc = document(title, pages)
    write_issue(ISSUE, doc)


if __name__ == "__main__":
    main()
