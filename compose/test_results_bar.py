#!/usr/bin/env python3
"""STYLE-GUIDE §0d results-bar unit tests (no Chrome)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from results_bar import (
    clears_bar, event_tier, find_weak_places, format_flags, is_weak_finish,
)
import gazette as g


def check(name, cond, detail=None):
    if not cond:
        raise SystemExit(f"FAIL: {name}" + (f" — {detail}" if detail else ""))
    print("  ok", name)


def test_bar():
    print("bar and tier")
    check("NAC is national", event_tier("at the November NAC in Columbus") == "national")
    check("SYC is national", event_tier("Y14 Men's Epee at the Super Youth Circuit") == "national")
    check("RYC is regional", event_tier("at the Star Cup RYC") == "regional")
    check("Freehold is local when no circuit hint", event_tier("Freehold Fencing") == "local")

    check("15th of 136 cadet national clears",
          clears_bar(15, 136, "national") and not is_weak_finish(15, 136, "national"))
    check("32nd of 200 national clears",
          clears_bar(32, 200, "national") and not is_weak_finish(32, 200, "national"))
    check("33rd of 200 national is weak", is_weak_finish(33, 200, "national"))
    # 55th of 229 is top-half (55 <= 114.5) but below top 32
    check("55th of 229 national is below the bar even in the top half",
          is_weak_finish(55, 229, "national"))
    check("83rd of 116, 90th of 235, 85th of 107 are weak",
          all(is_weak_finish(p, f, "national") for p, f in ((83, 116), (90, 235), (85, 107))))
    check("medal always prints", not is_weak_finish(3, 200, "local"))
    check("9th of 12 in a small local field is weak", is_weak_finish(9, 12, "local"))
    check("8th of 12 is weak (top-8 bar but bottom half)", is_weak_finish(8, 12, "local"))
    check("5th of 12 small field clears (top 8 and not bottom half)",
          not is_weak_finish(5, 12, "local"))
    check("rating earned nearby is not weak",
          not is_weak_finish(40, 62, "local", context="40th of 62 and earned C26"))


def test_scan():
    print("scan of printed copy")
    old = (
        "Nico Ng finished 15th of 136 in Cadet Men's Epee (Challenger) at the November NAC. "
        "He also placed 90th of 235 in Junior Men's Epee (Challenger). "
        "Athreya Aravind was 83rd of 116 in Junior Men's Epee (Elite) and 55th of 229 "
        "in Division I Men's Epee (Challenger). Anayaa Sheth was 85th of 107 in "
        "Junior Women's Epee (Challenger). None of the five Elite FC results earned a rating."
    )
    weak = find_weak_places(old)
    texts = {w["text"] for w in weak}
    check("old NAC short flags the four below-bar places",
          texts == {"90th of 235", "83rd of 116", "55th of 229", "85th of 107"}, texts)
    check("15th of 136 is not flagged", "15th of 136" not in texts)

    new = (
        "The November NAC was held at the Greater Columbus Convention Center in Columbus, Ohio, "
        "Nov. 20–23. The four-day event drew 257 official competitors in Cadet Men, 357 in Junior Men, "
        "221 in Junior Women and 358 in Division I Men. Nico Ng finished 15th of 136 in Cadet Men's "
        "Epee (Challenger) on Saturday, Nov. 21. Three Elite FC fencers were in Columbus: Nico, "
        "Athreya Aravind and Anayaa Sheth, across Cadet, Junior and Division I events."
    )
    weak2 = find_weak_places(new)
    check("rewritten NAC short has no weak places", weak2 == [], weak2)

    html = '<p>Nico was <span data-results-bar-ok>90th of 235</span> at the NAC.</p>'
    waived = find_weak_places("Nico was 90th of 235 at the NAC.", html=html)
    check("data-results-bar-ok waives a below-bar place", waived == [], waived)
    unwaived = find_weak_places("Nico was 90th of 235 at the NAC.",
                                html="<p>Nico was 90th of 235 at the NAC.</p>")
    check("the same place fails without a waiver",
          any(w["text"] == "90th of 235" for w in unwaived), unwaived)


def test_check_issue_fails():
    print("check_issue")
    bad = g.document("x", ['<div class="page"><p>At the NAC she finished 85th of 107.</p></div>'])
    try:
        g.check_issue(bad)
    except SystemExit as e:
        check("check_issue fails a below-bar printed place",
              "results bar" in str(e).lower() and "85th of 107" in str(e), e)
    else:
        raise SystemExit("FAIL: check_issue did not fail the below-bar place")

    good = g.document("x", ['<div class="page"><p>At the NAC he finished 15th of 136.</p></div>'])
    g.check_issue(good)
    check("check_issue accepts a national 15th of 136", True)

    waived = g.document(
        "x",
        ['<div class="page"><p data-results-bar-ok>At the NAC she finished 85th of 107.</p></div>'],
    )
    g.check_issue(waived)
    check("check_issue accepts a Frank-waived below-bar place", True)


if __name__ == "__main__":
    test_bar()
    test_scan()
    test_check_issue_fails()
    print("test_results_bar: ok")
