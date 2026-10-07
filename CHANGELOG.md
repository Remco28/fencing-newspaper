# Changelog — En Garde Gazette docs

Newest first. Earlier versions (v3.3–v3.19) are summarized in PLAN.md (status line, §8, §9).

## v3.21 — 2026-10-07 (budget page v2)

Frank: the practice budget page was hasty and hard to read, even on desktop. Redesigned for how he
uses it — the box desktop browser through the computer tab, 1280×800, with some remote lag.

- **`budget-demo/practice.html` v2:** fixed left bar (issue, publish-day field, rough fit meter,
  Included / Need Vet / Questions counts that jump to the first match, section nav, Submit);
  sections in reading order (Lead & features · Club · Shorts & fill · Photos · Held, merged & next
  week); one card per slot with headline, one-line summary, words/rows + budget, status badges,
  **Questions for Frank** answer boxes, big Include toggle, note box, Vet, ↑/↓ reorder (replaces
  drag). Draft text (readable serif block, `[NEED]` highlighted) and provenance are collapsed and
  built only when opened. 16px body, ~68ch lines. No animations, transitions, shadows, blur, or
  smooth scroll; updates touch only the changed card and the counters.
- **Lineup schema 2** (`practice-lineup.json`): `issue`, `desk_summary`, `sections`, `slots` with
  `summary` / `questions`; staging items not in the file are auto-placed (not proposed). Issue No. 1's
  lineup and the v1 page moved to `budget-demo/archive/`. Lineup rewritten for Issue No. 2.
- **Server:** `GET /thumb/<file>?w=&bw=` (small cached JPEGs in gitignored `budget-demo/.thumbs/`),
  `/api/media` adds pixel sizes, `/api/lineup` alias, env overrides for testing on a throwaway copy
  (`GAZETTE_STAGING_WEEK`, `GAZETTE_SUBMISSIONS`, `GAZETTE_LINEUP`, `GAZETTE_PORT`). `/vet` and
  `/submit` unchanged; submit JSON keeps v1 keys and adds `answers`, `issue`, `pageVersion`.
- **`screenshot.py`:** viewport mode (`… <out> 1280 800`) shoots what Frank sees, per section.
- Docs: STAGING.md Budget step (Monday routine + schema), PLAN §10, README.

## v3.20 — 2026-10-07 (after Issue No. 1)

Issue No. 1 (Thursday Edition, Oct 8, 2026) approved by Frank in chat at 18:40 ET after proof v2;
Frank printed the PDF himself. Decisions from that first real run, locked:

- **Epee is assumed** (STYLE-GUIDE §0c; PLAN §1): no “Epee” / “(Epee)” labels in club context —
  box titles, table headings, our fencers’ event names, captions. Keep the word only for
  outside-world multi-weapon stories, proper names, and contrasts (rule explainers, HS primer).
  Frank will say if foil/sabre is ever added. Cleaned labels: `prototype/monday-v6.html`
  (“Events (Epee)” → “Events”), `issues/2026-10-14/issue.html` sample labels (HTML only; the
  locked `paper-v3.14.pdf` reference is unchanged), `budget-demo/index.html` (demo club results +
  Medeo row), `budget-demo/practice-lineup.json` (Medeo events, Morris Cup title).
- **Content-heavy cut order** (CONTENT-HIERARCHY; STYLE-GUIDE §11; SECTIONS-MENU; PLAN §3):
  standing/utility boxes give way to stories — drop the regular Weekly Classes table (changed or
  special class → one-line note), shrink tournament boards to nearest/most important events and
  Elite FC entries, trim other utility boxes, then cut stories. Page 1/2 placement stays flexible.
- **Budget slot note overrides `publishDate`** (STAGING Budget).
- **Desk fill** with Frank-vetted items when stories run short; Frank can veto at proof
  (CONTENT-HIERARCHY stretch; STYLE-GUIDE §11).
- **Late add past 2 pages → trim Desk-fill stories first**, never shrink type
  (CONTENT-HIERARCHY; STYLE-GUIDE §6).
- **Caption naming**: only Frank-confirmed people; no left/right order unless verifiable;
  others are “other medalists” or similar (STYLE-GUIDE §19, §7).
- **Chat spelling beats scrape**; scraped form → roster alias (STAGING Clean; roster/README).
- **FencingTracker / scraped registrations stage unvetted** until Frank confirms (STAGING Tips/mail).
- **Proof round**: v1 → Frank’s answers → v2 → approval → print; Frank prints the PDF himself;
  proof status lives in `issue.json` (+ `proofApproval` in `approvals.json`); approved PDFs frozen
  (STAGING Proof; PLAN §6).
- **PNG inspection before a proof is called done** — already in STYLE-GUIDE §7 (“Render… rasterize
  to PNG, and LOOK”); reaffirmed with an explicit “no proof-ready doorbell before PNGs are inspected”.
- **Staging roll-forward** after approval: `next/` → `staging/weeks/2026-10-08/`, `after-next/`
  → `next/` (THE WEAPON now in `next` for Issue No. 2, week of Oct 12), fresh `after-next/`.
