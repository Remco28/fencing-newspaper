# Review — suggestions for the next agent

**Written by:** buffy-reviewer (2026-10-06, evening)
**For:** fencing-planner (office work #22) or whoever picks this project up next
**How to read:** Part 1 proves I understood the project; skim it. Part 3 is the payload —
ordered by impact, highest first. Nothing else in this repo was touched: the only write is
this file, and I rendered the prototype to /tmp for verification, not into the repo.

---

## Part 1 — What this project is

A weekly **printed club newspaper** ("En Garde Gazette", Elite Fencers Club, Chatham NJ,
epee-only) for kids and parents. One physical sheet, front + back, B&W, US Letter, two
editions: **Monday = results**, **Thursday = signups**. Editorial control is Frank alone;
email is the single input channel; fetched sources (FIE, USA Fencing, NJ.com, AskFRED,
FencingTracker) supply every printed fact, never model memory.

Architecture intent: **content/layout split** — an AI fills `issue.json` (strict schema,
word budgets, epee-only), a deterministic HTML/CSS template renders `paper.pdf` via Chrome
CDP (`render.py`), a human approves, a scheduler (Grok Bot / OpenAI Dots) runs it later.

State as of the last commit (V4, `2a9d850`): planning docs locked (PLAN / SOURCES /
SECTIONS-MENU / STYLE-GUIDE / REDDIT-SETUP), and a **Monday-results prototype** through 4
revisions — 3-column box-free articles with column rules, masthead flanks, pinned footer,
a gap instrument that measures unfilled space, and a mandatory zoomed visual QA checklist.

Verified during this review: `render.py` runs clean on this machine — exactly 2 Letter
pages, gaps above footer 0.50in / 0.68in (both under the 0.75in flag), fonts resolve to
real Arial / Arial Black / Times New Roman, masthead PNG is ~467dpi at print width.

## Part 2 — What's already good (don't re-litigate)

- The content/layout split is the right architecture and the docs hold the line on it
  (select-don't-invent patterns, frozen templates, word budgets).
- The style guide is unusually operational: budgets calibrated to ~40 words/column-inch,
  fill-or-flag rule, alignment rules that name the exact CSS (`tabular-nums`, `.r` on
  th *and* td), "the instrument decides, the eye decides beauty."
- The gap instrument in `render.py` is the best artifact in the repo — mechanical fill
  measurement beats eyeballing, and it's already wired.
- Source reality-testing is honest and dated: Reddit/X/IG walls confirmed by experiment,
  Devvit ruled out with reasons, AskFRED staleness warnings carried into the doc rules.
- Sample-content hygiene: every prototype page is marked "Sample content — not for
  distribution" in dateline and footer.

## Part 3 — Suggestions, ordered by impact

### 1. Build the correctness gate before the writer (biggest gap)

Nothing in the repo yet enforces the plan's most important promise: *"Scores, names, signup
lists come from fetched/emailed sources, never model memory."* Once a scheduled bot writes
the paper unattended, one hallucinated kid's name or wrong close-date in print is a trust
breaker. Before building fetch or the writer, build the gate:

- `issue.json` gets its **schema + validator** first (JSON Schema or a ~50-line check).
  Require **per-claim provenance**: every score/date/name/rating carries
  `{source_url | email_message_id, retrieved_at}`. No provenance → render refused.
- Add a deterministic **fact-regression pass**: extract numbers, names, and dates from the
  rendered text and regex-check each against `sources.json` / input files (now trivial to
  add in `render.py` — it already runs `Runtime.evaluate`).
- A **daily diff test** on sample content: if names/dates in the HTML change between runs,
  the test fails. Trains the failure mode early.
- Adopt a hard **rule to print in the docs**: any fact not in `sources.json` never renders,
  regardless of how good the prose is.
- Consider putting a machine-readable "verified" stamp in the footer for Frank's approve
  step (e.g. `QC: 2pp, gaps 0.50/0.68, 42/42 claims sourced`).

### 2. Refetch AskFRED the morning of print — stale prereg lists are the core product's failure mode

SOURCES.md records AskFRED's own warning that entry lists may be stale, and Thursday's
signup board is the paper's reason to exist. "Who's already entered" from a stale list
reads as a broken promise. Plan a **~7am Thursday refetch** (or right before render), keep
`retrieved_at` per row, and render a visible "as of" line on the signup board
(e.g. "entries as of Wed 8:10pm"). This also settles PLAN's still-open "Thursday data
cutoff" question — I'd propose Wed 8pm for the Monday board and a fresh Thursday-morning
pull for the Thursday board.

### 3. Print-friendly URLs need a shortener decision now

Thursday spec says "short print-friendly entry URLs" but AskFRED/USFA URLs are long query
strings that turn into unusable QR-adjacent mush at 8.5pt. Options, cheapest first:
(a) the results-app email includes a pre-shortened slug per tournament; (b) generate
`<club-domain>/go/<slug>` redirects; (c) drop URLs on the Thursday board and let the
 Monday edition + email carry them. Decide before the template work, not after.

### 4. Make the fill-or-flag rule mechanical, not aspirational

The stretch/cut hierarchy lives in prose; under deadline pressure a bot will take the lazy
exit (or worse, shrink type). Enforce in code:

- Every layout pattern slot gets an explicit word budget in the template (a small JS/JSON
  manifest: slot → min/max words). The writer receives exactly these budgets — this is
  already the style guide's intent; make the manifest the single source both sides read.
- Render pass **fails the build** if body type renders below the 7pt floor or leading
  exceeds the baseline (measurable via CDP computed styles, same pattern as the gap
  instrument).
- `render.py`'s gap check currently prints FLAG but **exits 0** — when the scheduler
  arrives, a flagged page must produce a non-zero exit (or an explicit `--allow-flag`
  override for Frank) so a short page can't silently reach "PDF ready, awaiting approve."

### 5. Fix documentation drift (small, do it before it multiplies)

- **PLAN.md duplicates the entire Thursday section** (lines 82 and 92 are two divergent
  copies: one says TV/streaming + comic, the other says trivia + no TV). Keep one.
- **PLAN.md line 96** puts trivia on Thursday's back page, but the locked v1 lineup cut
  trivia (line 90). Kill the stray mention.
- **PLAN.md line 153** still lists "Paper name?" as open — it was locked hours later
  (En Garde Gazette). Stale open-questions lists mislead the next agent *first*; that's
  exactly what they read.
- PLAN.md §3 and SECTIONS-MENU.md now overlap heavily; declare one of them canonical for
  section definitions (suggest SECTIONS-MENU for the option menu + verdicts, PLAN for the
  per-edition lineup only).
- Word budgets are stated in PLAN (600–700/issue), §4 (~600–700), and STYLE-GUIDE §11
  (~40/column-inch ≈ 650) — consolidate into the §11 manifest table and have the other
  docs point at it.
- No README: the repo is five docs + a prototype. A 20-line README (what this is, doc map,
  how to render, where the review lives) would have saved me ten minutes. Low priority.

### 6. Repo hygiene before automation starts

- `.gitignore` has `data/` but nothing for future per-issue output — `issues/` will be full
  of generated PDFs and email dumps. Decide the archive question (PLAN open item #5: git vs
  local-only) *now* and pre-write the ignore rule; otherwise the first scheduled run litters
  the repo. (My take: commit `issue.json` + `sources.json`, ignore PDFs and email bodies.)
- When real scripts arrive (fetch, ingest, writer), create `scripts/` — `prototype/` should
  stay the layout sandbox it is.
- REDDIT-SETUP.md correctly demands env-only credentials; add `.env.example` with blank
  keys when the first env var actually exists, so the shape is documented without secrets.
- No CI exists; when it does, a smoke job = render the current prototype and assert 2 pages
  + no gap flags. Cheap, catches Chrome deprecations (the repo already carries one —
  `--print-to-pdf-no-header` being ignored — so this class of surprise is proven).

### 7. Template robustness notes (low priority, note for the design pass)

- Style guide says "flex thirds **or CSS columns**"; v4 uses flex. CSS `columns` gives real
  balanced newspaper flow but is flakier across print engines — if a future pattern
  switches, re-run the zoomed QA, and prefer `column-fill: auto` with explicit height.
- The gap instrument assumes `.footer`'s `previousElementSibling` exists; a malformed
  template silently reports `measure skipped`. Fine now; revisit if templates multiply.
- Portability: fonts are real MS fonts on this machine. The eventual runner needs the same
  (or accept Liberation metric-compatible fallbacks already in the stacks — do one test
  print from the fallback stack so it's a known-good degradation, not a surprise).
- `masthead001.png` at 467dpi is great for print; consider committing a compressed variant
  if repo size ever matters (309KB today — ignore this until it isn't fine).

### 8. Reddit: the analysis is done — just sequence it

The verdicts are right (Devvit wrong tool; script app approval-gated; fallbacks stand).
The only improvement: put the **fallback as the default in the runbook** — "Reddit OAuth:
pending approval; until then r/Fencing arrives only as Frank-forwarded links" — so a future
agent doesn't re-litigate a settled question or block on it. The ~60 req/min OAuth limit is
already documented in REDDIT-SETUP.md; nothing more needed until approval lands.

### 9. Sources ops: two small runbook items

- **Timezone**: "Monday ~6am" — whose Monday? Weekend FIE results in US time zones land
  late Sunday night ET; pin the timezone (and the Fetch-Until timestamp) in PLAN so Monday's
  lead isn't missing the biggest result.
- **Fetch failures are normal**: searxng/firecrawl services are local (office tools list);
  when one is down mid-run the paper should still assemble from the remaining sources and
  *flag the gap to Frank* rather than fail the whole run. Write the degrade-path down once.

### 10. V1 operating loop: give Frank a cheap red-pen feedback path

Two dry-run issues per edition are planned with Frank red-pen. Add: after each dry run,
edits flow back as **structured notes against issue.json** ("club results box: Sofia L.
placed 3rd, not 2nd — fix source row"), not free-form prose. The SECTIONS-MENU corrections
box idea pairs with this: corrections are the visible output of this loop, and the loop is
also what trains the schema (every red-pen fix either becomes a validation rule or a
template fix).

## Part 4 — Suggested order for the next work session

1. Doc-drift pass (Part 3.5) — 20 minutes, prevents the next agent from reading stale rules.
2. `issue.json` schema + validator + provenance rule (3.1) — the correctness gate.
3. Template manifest: pattern/slot/word-budgets as data (3.4), incl. gap-check exit code.
4. Thursday refetch + "as of" board line (3.2) and the shortener decision (3.3).
5. Fetchers per SOURCES.md, in Tier order, with per-source degrade behavior (3.9).
6. Thursday signup template (none exists yet — only Monday does), reusing the locked
   patterns; zoomed QA per the style guide.
7. Two dry-run issues per edition with Frank's structured red-pen loop (3.10).

---

*Review scope: all five planning docs, `.gitignore`, `render.py`, `render.sh`,
`monday-v4.html` (and diff-level awareness of v1–v3 via the style-guide changelog), git
history 8 commits, plus a live render verification to /tmp. No repo file was modified and
nothing was committed; this file is untracked on purpose — commit it if it's useful.*
