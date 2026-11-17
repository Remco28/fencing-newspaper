# En Garde Gazette — Elite Fencers Club weekly (1 sheet, front + back, B&W, epee-only)

## Doc map (canonical homes — on conflict, the home wins)
- **PLAN.md §1a — Clark Kent is the product:** after budget approve, the bot *composes*
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
  **ops cadence / gather loop** (v3.15) and the **weekly Budget rhythm** (v3.50)
- **budget-demo/STANDALONE-README.md** — how to build, review, and ingest the Budget page
  (`pageVersion: budget-paper-v2`, Auto / Manual)
- **compose/README.md** — shared Template A composer, eye check, `--verify` send gate
- CONTENT-HIERARCHY.md — slot order + word budgets for the weekly issue (Frank sorts this file)
- STYLE-GUIDE.md — all visual rules + mandatory QA checklist
- SOURCES.md — standing fetch checklist + **cadence header** (Wed skim / Monday full pass) + AskFRED API/`scripts/askfred.py` + **X (Twitter) rules** (v3.22)
- sources/x-accounts.md — vetted X accounts (tier A/B/C, rejected, not-found), vetted 2026-10-08
- SECTIONS-MENU.md — option menu + past verdicts (history, not spec)
- **CHANGELOG.md** — doc version history (v3.20 onward; earlier in PLAN.md)
- REDDIT-SETUP.md — Reddit OAuth path (approval-gated; fallbacks are default)
- REVIEW-FROM-BUFFY-REVIEWER.md / VISUAL-REVIEW-DEEPSEEK-V4.1-FLASH.md — outside reviews

## Compose and render an issue
Shared Template A composer (v3.47): typography, boards, stylesheet and fill instrument live in `compose/`. Start a new issue from `compose/recipe_template.py` (see `compose/README.md` and `staging/weeks/next/COMPOSE.md`).
```bash
python3 issues/<date>/recipe/compose.py x
python3 compose/render.py issues/<date>/issue.html issues/<date>/en-garde-gazette-no-<N>-<date>.pdf --author="Nico's Dad"
python3 compose/eyecheck.py issues/<date>/en-garde-gazette-no-<N>-<date>.pdf --report=issues/<date>/fit-report.json
python3 compose/eyecheck.py --verify issues/<date>/en-garde-gazette-no-<N>-<date>.pdf
```
`compose/render.py` uses Chrome CDP (headers off), then prints the footer gap **per column**
(FLAG > 0.75in), per-row column spread (FLAG > 0.5in), the 7pt type floor, and hyphenated line breaks.
A FLAG writes `<name>.FAILED.pdf` and leaves the proof path untouched unless `--allow-flag` is passed.
`--verify` is the send gate. Clark also opens every preview himself. See STYLE-GUIDE.md §7 and `compose/README.md`.
`prototype/render.py` is a shim to the same renderer. Historical monday-v* pages:
```bash
./prototype/render.sh prototype/monday-v6.html
```

## Ops (locked 2026-10-06; gather loop v3.15; publish wording v3.19; first-run decisions v3.20)
- **Publish cadence:** one weekly newsletter. Try Monday or Tuesday; later is fine (no rule broken). Soft preference to hold for Monday club results when easy. Dateline = actual publish day (`<Weekday> Edition`). No Mon/Thu split.
- **Parent Q&A (v3.18):** recurring category — parent → Frank → Clark; anonymous; `kind: qa`; see CONTENT-HIERARCHY + STYLE-GUIDE §8a.
- **Gather loop (v3.15):** chat → staging anytime (next week default); email = daily morning + pre-budget second pass; self-gather = Wed skim + publish-morning full pass. Detail: **STAGING.md § Ops cadence** + **SOURCES.md**.
- **Mail:** AgentMail `efc.weekly@agentmail.to` only (not Gmail). Tips/photos OK there. **Auto-vet allowlist:** `frankcng@gmail.com`, `chunkymonkey@agentmail.to`, club Mailchimp; other senders stage as **unvetted** (never reject unknown apps/bots).
- **Pipeline:** Staging → Clean → **Budget → Frank approve → Clark compose → Proof → Frank approve → print**. Clark and Frank curate through the week; Clark preps sections ahead; when ready, generate the Budget (Auto placement is the default). Frank modifies and adds on the page. **Manual** is only for final layout tweaks or to push one layout harder. Unvetted items and photos stay in the bank until Frank vets them — they cannot be placed, and unvetted photos are never auto-queued for next week. After approval, compose with the proof v3 process (eye check, `--verify` send gate). If Frank used Manual, Clark matches `manualLayout` by hand (compose does not yet pack from it). Chat is doorbell only for budget/proof. Provenance → `sources.json`. Detail: STAGING.md.
- **Proof round (v3.20, process as of v3.49):** proof v1 → Frank’s answers → v2 (v3… if needed) → Frank approves → Frank prints the PDF himself. Every proof is eye-checked and `--verify`'d before it goes to Frank; Clark also opens every preview. Proof status lives in `issue.json`. Epee is assumed — no “(Epee)” labels in club context (STYLE-GUIDE §0c).
- **Working copy:** `/workspace/fencing-newspaper` on Musketeer's computer.
- **Durable store:** sync this repo to GitHub weekly (and after a finished issue if you care). Everything except raw email bodies.

## Repo layout
- `compose/` — shared Template A composer (`gazette.py`, `template-a.css`, `render.py`, recipe template). New issues start here.
- `prototype/` — historical layout sandbox (versioned `monday-vN.html` + PDFs). `render.py` is a shim to `compose/render.py`.
- `masthead001.png` — nameplate art (cropped to opaque bbox)
- `budget-demo/` — weekly **Budget** is a standalone HTML file: `python3 scripts/build_budget_html.py` → `budget-demo/out/budget-no-<N>-<date>-v<K>.html` (gitignored; send the file, don't commit it). `pageVersion` is `budget-paper-v2`. The page is the two-page paper plus a bank; Auto placement is the default, with a Manual switch for final tweaks. Lineup: `practice-lineup.json` (schema 2). See **budget-demo/STANDALONE-README.md** and STAGING.md. `practice.html` + `server.py` (`http://127.0.0.1:8766/`) remain as the fallback; `/demo` is the old PRETEND demo. Previous issue's lineup: `budget-demo/archive/`.
- `scripts/` — helpers; **`scripts/askfred.py`** = gentle AskFRED gather client (key in `.env`, see SOURCES.md)
- `staging/weeks/` — upcoming material (`YYYY-MM-DD/` or `next/` + `media/`); see STAGING.md. **Email media extract (v3.5):** MIME attachments + remote/inline HTML images → `media/` with provenance; filter logos/icons/pixels.
- `issues/` — per weekly issue (`issues/<YYYY-MM-DD>/` with `issue.json`, `sources.json`, derived `inputs/`, `approvals.json`, `paper.pdf`); committed. **Taste reference:** `issues/2026-10-14/` (sample v3.14). Raw emails stay in AgentMail.

## License

Copyright Team Remco (https://teamremco.org).

Free to use, and free to build on for your own use. You may use, copy and change this for personal, educational and other noncommercial purposes under the [PolyForm Noncommercial License 1.0.0](LICENSE.md).

Commercial use needs permission. If you'd like to use this commercially, email [support@teamremco.org](mailto:support@teamremco.org) and we can talk.

Quotes, photos, names, results and other material from third-party sources belong to their owners and are not covered by this license.

Third-party libraries keep their own licenses.
