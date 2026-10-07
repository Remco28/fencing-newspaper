# Changelog — En Garde Gazette docs

Newest first. Earlier versions (v3.3–v3.19) are summarized in PLAN.md (status line, §8, §9).

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
