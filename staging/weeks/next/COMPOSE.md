# Composing Issue No. 7

Use the shared Template A composer, not a copy of an old `issues/*/recipe/compose.py` and not CSS scraped from `issues/2026-10-13/issue.html`.

1. After Frank approves the budget and the publish date is set, copy `compose/recipe_template.py` to `issues/<date>/recipe/compose.py`.
2. Point it at this pile (`staging/weeks/next`, or the dated folder after roll-forward) and a frozen lineup snapshot when you have one.
3. Build with `python3 issues/<date>/recipe/compose.py x` then `python3 compose/render.py …` and `pdftoppm -r 200`.

Details: `compose/README.md`. Published Nos. 1–6 are frozen and cannot be overwritten in place.
