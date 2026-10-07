# En Garde Gazette — Elite Fencers Club weekly (1 sheet, front + back, B&W, epee-only)

## Doc map (canonical homes — on conflict, the home wins)
- PLAN.md — narrative, decisions, open questions, next steps
- CONTENT-HIERARCHY.md — slot order + word budgets per edition (Frank sorts this file)
- STYLE-GUIDE.md — all visual rules + mandatory QA checklist
- SOURCES.md — standing fetch checklist for the bot
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

## Ops (locked 2026-10-06 evening)
- **Mail:** AgentMail `efc.weekly@agentmail.to` only (not Gmail). Tips/forwards go there.
- **Working copy:** `/workspace/fencing-newspaper` on Musketeer's computer.
- **Durable store:** sync this repo to GitHub weekly (and after a finished issue if you care). Everything except raw email bodies.
- **Approvals:** local HTML budget/proof page on the box; chat is doorbell only.

## Repo layout
- `prototype/` — layout sandbox (versioned `monday-vN.html` + PDFs, `render.py`)
- `masthead001.png` — nameplate art (cropped to opaque bbox)
- `scripts/` (future) — fetch, ingest, writer
- `issues/` (future) — per-edition output (`issue.json`, `sources.json`, derived `inputs/`, `approvals.json`, `paper.pdf`); committed. Raw emails stay in AgentMail.
