# Budget fill calibration

`measure_issues.py` opens each composed `issues/<date>/issue.html` in Chrome and records block sizes.
`calibrate_fill.py` fits `scripts/budget_page/calibration.json`, which `build_budget_html.py` lays over `lineup.capacity`.

  python3 scripts/calibration/measure_issues.py
  python3 scripts/calibration/calibrate_fill.py --report

Do not edit `compose/`. The fitted numbers in `calibration.json` (Nos. 1–7, 2026-11-16) are what the Budget page ships with. A longer write-up of the fit is in the review folder, not this repo.
