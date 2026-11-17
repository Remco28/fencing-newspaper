# Composing Issue No. 8

Use the shared Template A composer, not a copy of an old `issues/*/recipe/compose.py` and not CSS scraped from `issues/2026-10-13/issue.html`.

1. After Frank approves the budget and the publish date is set, copy `compose/recipe_template.py` to `issues/<date>/recipe/compose.py`.
2. Point it at this pile (`staging/weeks/next`, or the dated folder after roll-forward) and a frozen lineup snapshot when you have one.
3. Build with `python3 issues/<date>/recipe/compose.py x` then `python3 compose/render.py …`, then the eye check: `python3 compose/eyecheck.py <pdf> --report=<fit-report.json>`. Clark looks at both previews too. A proof goes to Frank only when `python3 compose/eyecheck.py --verify <pdf>` says SENDABLE.
4. Keep the No. 7 proof v3 workflow (Frank t232u, 2026-11-17: "whatever you did, let's keep it up next week as well"): spacing tokens only, short/standard/long copy per item (`recipe/lengths.json`), candidate `ARRANGEMENTS` ranked with `compose/arrange.py`, report-only balancer, no crops, vetted copy only. See `issues/2026-11-17/recipe/compose.py` for a worked example.

Details: `compose/README.md`. Published Nos. 1–7 are frozen and cannot be overwritten in place.

Art (photos, comics, diagrams, illustrations) is fitted automatically: place a `recipe/art.json` manifest and call `art()` from this recipe (see `compose/README.md` and STYLE-GUIDE §19). Do not hand-space with `.fill-art` or a hard `max-height`. Render with `compose/render.py` as usual; the fit pass is on by default when slots are present. `--fit-report=FILE.json` writes the decisions. Published Nos. 1–7 stay frozen.

