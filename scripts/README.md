# scripts/

- **`fencingapi.py`** — Frank's fencing-api client (AskFRED / USA Fencing / FencingTracker). Key via `FENCING_API_KEY` in gitignored `.env`. See **SOURCES.md § fencing-api**.
- **`askfred.py`** — AskFRED API helper for Clark Kent's gather (epee near Chatham). Key via `ASKFRED_API_KEY` / gitignored `.env`. See **SOURCES.md § AskFRED API**.
- **`build_budget_html.py`**: builds the standalone budget page. Each build is numbered per week: `budget-demo/out/budget-no-<N>-<date>-v<K>.html`, with the counter and Frank's decision log in `staging/weeks/<pile>/budget-versions.json`. A rebuild with unchanged data keeps the number. The page starts from the latest captured decisions and shows "Budget vK · decisions captured through <time ET>". `--preview` builds an unnumbered copy. The build refuses while a dropped submission is un-ingested (`--allow-pending` to override). See **budget-demo/STANDALONE-README.md**.
- **`ingest_budget_submission.py <file> [--dry-run]`**: records a budget-page submission. It applies the vets to `items.json` and appends the decisions to `budget-versions.json`. Always dry-run first, apply, then rebuild for the next version.
