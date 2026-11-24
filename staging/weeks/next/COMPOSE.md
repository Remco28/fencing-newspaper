# Composing Issue No. 9

Use the shared Template A composer, not a copy of an old `issues/*/recipe/compose.py` and not CSS scraped from `issues/2026-10-13/issue.html`.

1. After Frank approves the budget and the publish date is set, copy `compose/recipe_template.py` to `issues/<date>/recipe/compose.py`.
2. Point it at this pile (`staging/weeks/next`, or the dated folder after roll-forward) and a frozen lineup snapshot when you have one.
3. Build with `python3 issues/<date>/recipe/compose.py x` then `python3 compose/render.py …`, then the eye check: `python3 compose/eyecheck.py <pdf> --report=<fit-report.json>`. Clark looks at both previews too. A proof goes to Frank only when `python3 compose/eyecheck.py --verify <pdf>` says SENDABLE.
4. Keep the No. 7 proof v3 workflow (Frank t232u, 2026-11-17: "whatever you did, let's keep it up next week as well"): spacing tokens only, short/standard/long copy per item (`recipe/lengths.json`), candidate `ARRANGEMENTS` ranked with `compose/arrange.py`, report-only balancer, no crops, vetted copy only. See `issues/2026-11-17/recipe/compose.py` and `issues/2026-11-24/recipe/compose.py` for worked examples. If Frank submitted a Manual layout, match `manualLayout` by hand — compose does not yet pack from it.
5. **Results tone (STYLE-GUIDE §0d) — every proof, every page.** Do not print a club member's place that is below the inclusion bar (top 32 national, top 16 regional, top 8 local; small fields under ~16: top 8 or a medal) or in the bottom half of the field. The rule covers the Club Results box, captions, leads, shorts, notes, and deadlines — not only the box. A fact being vetted, or a staging note that parks weak finishes "in the article," is not permission to print them. Frank has to clear a below-bar place for print explicitly (`data-results-bar-ok`). Compose fails on an unmarked "Nth of M" that misses the bar (`compose/results_bar.py`). When a result is dropped, fill with other verified facts about the event, not a weak place.
6. **Header-rule gap.** First content on each page (including page-2 boxes under PAGE TWO) must sit a full `--gap-block` below the dateline's bottom rule. Shared CSS in `compose/template-a.css` supplies this; do not close it with a recipe override. A too-tight gap FLAGs the fill instrument and fails the eye check.

Details: `compose/README.md`. Published Nos. 1–8 are frozen and cannot be overwritten in place.

Art (photos, comics, diagrams, illustrations) is fitted automatically: place a `recipe/art.json` manifest and call `art()` from this recipe (see `compose/README.md` and STYLE-GUIDE §19). Do not hand-space with `.fill-art` or a hard `max-height`. Render with `compose/render.py` as usual; the fit pass is on by default when slots are present. `--fit-report=FILE.json` writes the decisions. Published Nos. 1–8 stay frozen.

