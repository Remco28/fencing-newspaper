# En Garde Gazette — Elite Fencers Club weekly (1 sheet, front + back, B&W, epee-only)

## Doc map (canonical homes — on conflict, the home wins)
- **PLAN.md §1a — Gazette Desk is the product:** after budget approve, the bot *composes*
  a tailor-made Elite FC sheet (pleasant, fun), not a slot dump. STYLE-GUIDE §0 is the bar.
- **PLAN.md §1b — voice:** newsletter-aware, selective words, reporter default; tone matches
  the piece. STYLE-GUIDE §0a for the weekly checklist.
- **PLAN.md §1c — reality / provenance:** real issues invent nothing; every printed fact →
  staging + `sources.json`; no model memory; sample/pretend labeled only. STYLE-GUIDE §0b +
  STAGING.md.
- PLAN.md — narrative, decisions, open questions, next steps
- **Locked sample taste (v3.14):** `issues/2026-10-14/` (`paper-v3.14.pdf`) — furniture
  reference for dateline, flanks, §8 boxes vs rails. STYLE-GUIDE §2/§8/§12. PLAN §4:
  dynamic layout **PAUSED / deferred** (Template A only).
- **STAGING.md** — Staging→Clean→Budget→Proof, tip vetting, item schema, folder layout,
  **ops cadence / gather loop** (v3.15); **Parent Q&A** category (v3.18)
- CONTENT-HIERARCHY.md — slot order + word budgets for the weekly issue (Frank sorts this file)
- STYLE-GUIDE.md — all visual rules + mandatory QA checklist
- SOURCES.md — standing fetch checklist + **cadence header** (Wed skim / publish-morning full pass) + AskFRED API/`scripts/askfred.py`
- SECTIONS-MENU.md — option menu + past verdicts (history, not spec)
- REDDIT-SETUP.md — Reddit OAuth path (approval-gated; fallbacks are default)
- REVIEW-FROM-BUFFY-REVIEWER.md / VISUAL-REVIEW-DEEPSEEK-V4.1-FLASH.md — outside reviews

## Render a prototype
```bash
./prototype/render.sh prototype/monday-v6.html
```
`render.py` uses Chrome CDP (headers off), then prints per-page footer gaps
(FLAG > 0.75in) and per-row column spread (FLAG > 0.5in). Any FLAG fails the build
unless `--allow-flag` is passed. See STYLE-GUIDE.md §7 for the full QA checklist.

## Ops (locked 2026-10-06; gather loop v3.15; publish wording v3.19)
- **Publish cadence:** one weekly newsletter. Try Monday or Tuesday; later is fine (no rule broken). Soft preference to hold for Monday club results when easy. Dateline = actual publish day (`<Weekday> Edition`). No Mon/Thu split.
- **Parent Q&A (v3.18):** recurring category — parent → Frank → Desk; anonymous; `kind: qa`; see CONTENT-HIERARCHY + STYLE-GUIDE §8a.
- **Gather loop (v3.15):** chat → staging anytime (next week default); email = daily morning + pre-budget second pass; self-gather = Wed skim + publish-morning full pass. Detail: **STAGING.md § Ops cadence** + **SOURCES.md**.
- **Mail:** AgentMail `efc.weekly@agentmail.to` only (not Gmail). Tips/photos OK there. **Auto-vet allowlist:** `frankcng@gmail.com`, `chunkymonkey@agentmail.to`, club Mailchimp; other senders stage as **unvetted** (never reject unknown apps/bots).
- **Pipeline:** Staging → Clean → **Budget → Frank approve → Desk compose → Proof → Frank approve → print**. Budget may show unvetted labeled; include blocked until Frank vets. Chat is doorbell only for budget/proof. Provenance → `sources.json`.
- **Working copy:** `/workspace/fencing-newspaper` on Musketeer's computer.
- **Durable store:** sync this repo to GitHub weekly (and after a finished issue if you care). Everything except raw email bodies.

## Repo layout
- `prototype/` — layout sandbox (versioned `monday-vN.html` + PDFs, `render.py`)
- `masthead001.png` — nameplate art (cropped to opaque bbox)
- `budget-demo/` — local budget page at `http://127.0.0.1:8766/` (`cd budget-demo && python3 server.py`). `/` = **PRACTICE budget** (`practice.html`) built from REAL `staging/weeks/next/items.json` + media manifest, driven by Desk's proposed lineup `practice-lineup.json` (slot → item ids, dedupes, flags, fit-estimate calibration); seed/pretend items sit in a collapsed excluded drawer. `/demo` = old PRETEND demo (`index.html` + `photos/`). Vet → `staging/weeks/next/items.json` + vet-log; Submit → `submissions/budget-*.json` + `approvals.json` (gitignored). Screens: `python3 budget-demo/screenshot.py` → `budget-demo/screens/practice-<date>-*.png`. Not full production ingest; see STAGING.md.
- `scripts/` — helpers; **`scripts/askfred.py`** = gentle AskFRED gather client (key in `.env`, see SOURCES.md)
- `staging/weeks/` — upcoming material (`YYYY-MM-DD/` or `next/` + `media/`); see STAGING.md. **Email media extract (v3.5):** MIME attachments + remote/inline HTML images → `media/` with provenance; filter logos/icons/pixels.
- `issues/` — per weekly issue (`issues/<YYYY-MM-DD>/` with `issue.json`, `sources.json`, derived `inputs/`, `approvals.json`, `paper.pdf`); committed. **Taste reference:** `issues/2026-10-14/` (sample v3.14). Raw emails stay in AgentMail.
