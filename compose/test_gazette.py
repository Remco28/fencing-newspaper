#!/usr/bin/env python3
"""Golden checks for the shared composer. Run: python3 compose/test_gazette.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gazette as g

SHY = g.SHY
NBH = g.NBH

# ty(): quotes, non-breaking joins, run-in bold — and no soft hyphens unless asked
assert g.ty('He said "go" on Nov. 8 at 5 p.m.') == 'He said “go” on Nov.&nbsp;8 at 5&nbsp;p.m.'
assert g.ty("**Fact check:** it's fine") == '<b class="run">Fact check:</b> it’s fine'
assert SHY not in g.ty("competition classification")

# Existing hard hyphens in letter-letter compounds become U+2011 and must survive hyphenation
fee = g.ty("The Junior Olympics regular-fee deadline is today.", hyph=True)
assert "regular" + NBH + "fee" in fee, fee
assert "regular-fee" not in fee
assert "regularfee" not in fee.replace(SHY, "")  # NBH still present, so this stays regular<NBH>fee
assert g.plain(fee) == "The Junior Olympics regular-fee deadline is today."
# table cells (hyph=False, the default) get the same treatment
assert NBH in g.ty("regular-fee deadline")
assert "regular-fee" not in g.ty("regular-fee deadline")

if g._DIC:
    src = "A competition’s classification depends on Peterfreund and r/Fencing commenters. Ratings determine seeding."
    h = g.hyphenate(src)
    assert "clas" + SHY in h                       # ordinary long word: hyphenated
    assert "Peterfreund" in h and "Ratings" in h   # capitalised words: untouched
    assert "r/Fencing" in h and "competition’s" in h
    assert h.endswith("seeding.")                  # last word of the paragraph: untouched
    assert h.replace(SHY, "") == src               # nothing but soft hyphens added
    # hyphenate() itself never eats a hard hyphen
    raw = "A regular-fee deadline plus classification."
    h2 = g.hyphenate(raw)
    assert "regular-fee" in h2
    assert "regularfee" not in h2.replace(SHY, "")

# kicker shared by adjacent pieces prints once
a = g.piece("A", "<p>x</p>", kicker="For the Parents"); b = g.piece("B", "<p>y</p>", kicker="For the Parents")
assert g.stack(a, b).count("rail-title") == 1 and g.stack(a, "<hr>", b).count("rail-title") == 2

# Club Results: tournament/date once, one row per fencer, nothing dropped
t = g.results_table([["A One", "NYFA #1, Y8 Mixed (Nov. 8)", "3rd of 4"], ["B Two", "NYFA #1, Y10 Mixed (Nov. 8)", "8th of 17"],
                     ["C Three", "Ultimate Cup RJCC, Junior Men (Nov. 1)", "10th of 87"]])
assert t.count('class="day"') == 2 and t.count("NYFA") == 1 and "<td>Y8 Mixed</td>" in t and "Nov.&nbsp;1" in t

# thin days become a Day column; busy tournaments keep sub-rows
thin = g.tourney("X", "Town", "d", ["Event", "Elite FC"], ["0.9in", None], [("Sat", [["Y14", "A"]]), ("Sun", [["Y12", "B"]])])
busy = g.tourney("Y", "Town", "d", ["Event", "Elite FC"], ["0.9in", None], [("Sat", [["Y14", "A"], ["Y12", "B"]]), ("Sun", [["Y10", "C"], ["Y8", "D"]])])
assert "<th>Day</th>" in thin and 'class="day"' not in thin
assert "<th>Day</th>" not in busy and busy.count('class="day"') == 2

# box notes go under the shorter half
m, info = g.board_split([thin], [busy], notes=["A note about the venue."], ratio=(50, 50))
assert info["notes"] == ["L"] and m.index("A note") < m.index("Y <")

# credit: one short line, no file names or URLs (helper only; published credits are not rewritten)
c = g.credit_line("Photo: © A B / Wikimedia Commons, “X Y.jpg”, CC BY 2.5 (creativecommons.org/licenses/by/2.5). Source: commons.wikimedia.org/wiki/File:X_Y.jpg. Cropped.")
assert c == "Photo: © A B / Wikimedia Commons, CC BY 2.5 (cropped)", c
try:
    g.check_credit("Photo: commons.wikimedia.org/wiki/File:X.jpg"); raise AssertionError("bad credit passed")
except SystemExit:
    pass

# repo root is derived from this file, not a hardcoded workspace path
assert g.ROOT.name == "fencing-newspaper" or (g.ROOT / "compose" / "gazette.py").is_file()
assert "/tmp/fable-sample" not in str(g.ROOT)

print("gazette: all checks passed")
# table() / protect_hyphens: recipes may pass raw cells (No. 5 deadlines did).
tab = g.table(["Date", "What closes"], [["Wed 11/11", "Junior Olympics: regular-fee deadline"]], ["0.62in", None])
assert "regular" + NBH + "fee" in tab, tab
assert "regular-fee" not in tab
assert g.plain(tab).count("regular-fee") == 1
# Do not rewrite hyphens inside tags/attributes.
raw = '<img src="media/regular-fee-chart.jpg" alt="x">'
assert g.protect_hyphens(raw) == raw
