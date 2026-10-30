# Standalone budget page — requirements (Frank-approved 2026-10-26)

## Why
Frank reviews the Gazette budget each week. The box cannot expose a tunnel (only outbound 443), so the
page must be ONE self-contained `.html` file Frank opens on his own laptop or phone — offline, no server,
no network requests. He submits by downloading/copying a JSON file and sending it to the Gazette inbox or
pasting it in chat; a script on the box then applies it.

## HARD CONSTRAINTS
- Do NOT modify or break `budget-demo/practice.html` or `budget-demo/server.py` (old page stays as fallback).
  Don't modify `practice-lineup.json`, `staging/**`, `issues/**`, `docs/**`, `site/**`.
- Do not read, print, or commit `.env`. Do not `git push`, do not `git commit` (the parent will review and commit).
- Generated HTML contains unvetted content and minors' names: output goes to `budget-demo/out/` which must be
  gitignored (add `budget-demo/out/` to `.gitignore`). Never write generated HTML anywhere tracked.
- Python stdlib + Pillow only (already on the box). No npm/CDN/web fonts. The generated page makes ZERO network
  requests (no fetch of remote or local URLs, no external fonts/images; system font stacks only).
- Reuse the SAME lineup schema (`practice-lineup.json`, schema 2) so the Monday routine doesn't change.
  Read `practice.html` carefully — it is the reference implementation of how the lineup + items + media are
  interpreted (buildSlots, auto-placed unslotted items, questionsFor, badges, cost/fit meter, photoList,
  held list, payload). Port that logic faithfully.

## Deliverables
1. `scripts/build_budget_html.py` — generator.
   - Defaults: lineup `budget-demo/practice-lineup.json`, items `staging/weeks/next/items.json`,
     media `staging/weeks/next/media/manifest.json` (+ the media files beside it for thumbnails).
   - CLI flags: `--lineup`, `--staging-week` (dir holding items.json + media/), `--out` (file or dir),
     `--thumb-width` (default ~360), `--quality`. Default output:
     `budget-demo/out/budget-no-<N>-<publish-date>.html` where N = lineup `issue.number`, date = lineup `publish.date`.
   - Inline ALL data as JSON in the file (lineup, items, media manifest), thumbnails as small compressed
     data-URIs (JPEG; B&W like practice.html shows photos "as printed" where it does; WebP ok if smaller),
     all CSS and JS inline. Keep file size reasonable (target < 2 MB; thumbnails ~320–400px wide, q≈70).
     Escape `</script>` / `<!--` / U+2028 inside inlined JSON.
   - Items missing on disk / missing from items.json must degrade gracefully (card says "item not in staging"),
     since a lineup can reference items that were rolled out of `next`. Media files missing -> no thumbnail.
   - Print the output path, size, counts to stdout. Exit non-zero with a clear message on bad input.
2. The page itself (generated). Keep EVERY feature of the current page:
   - Issue/week header; publish-date picker with Clark's suggested day + reason (`publish.date/alt/why/note`);
     "Clark's read on this week" bullets (`desk_summary`).
   - Fit meter: % of two pages, words of room/over, projected if proposals vetted (same cost model as practice.html).
   - Counters (in / need vet / open questions) with jump-to-next buttons.
   - Jump-to section list with "X of Y in".
   - Section-grouped cards (lineup `sections`): slot, size, budget, headline, summary, status badges
     (vetted / unvetted / facts pending / waiting on results / needs Frank / Clark proposes / auto-placed),
     expandable draft text or tables (tournament board `panels`, class schedule `table`) or figure description,
     expandable source & provenance, thumbnail, Include checkbox LOCKED until vetted, note-to-Clark field,
     Vet button, reorder up/down, "Questions for Frank" answer fields, empty slots with reason,
     unslotted staging items (auto-placed), Photos section (caption, vetted, size, source, include, vet),
     Held / not-proposed list with reasons, overall notes, Submit.
3. `scripts/ingest_budget_submission.py <submission.json>` — applies a submission exactly like the server's
   `/submit` and `/vet` (see `server.py`): writes `submissions/budget-<stamp>.json` and `submissions/approvals.json`
   (adds `submittedAt`, `pretend` default as server does), and for every `vets` entry sets `vetted=True,
   vetted_at, vetted_by="frank", vet_notes` on the item in `<staging-week>/items.json`, appends the same
   vet-log entry (to the staging week's `vet-log.jsonl` AND `submissions/vet-log.jsonl`, `source` = "budget-page-standalone").
   Also set `vetted: true` on a photo's manifest entry? -> NO: photos are vetted via their item like today;
   check how practice.html vets photos (it POSTs /vet with the photo/media id) and mirror what the server does
   for that case (server only finds items in items.json; unknown ids -> report as "not found", don't crash).
   - Flags: `--dry-run` (print what would change, write nothing), `--staging-week`, `--submissions` (same env
     defaults as server.py: GAZETTE_STAGING_WEEK, GAZETTE_SUBMISSIONS), `--now` optional for deterministic tests.
   - Validate payload (JSON object; required keys publishDate, includedSlots, excludedSlots; vets items need string id).
     Refuse a submission whose `targetWeek`/issue doesn't match the lineup unless `--force`. Idempotent-friendly:
     re-ingesting the same file just re-applies (note `already_vetted`).
   - Print a human summary: issue, publish date, N included, N vets applied/not-found, answers, notes.

## New behavior of the page
1. **Vet is local.** Clicking Vet on a card/photo no longer POSTs; it sets a local "vetted by you (pending submit)"
   state on the card (visibly distinct from "vetted already on file"), unlocks the Include checkbox, updates the
   counters/fit meter ("projected if proposals vetted" -> real), lets Frank add an optional vet note, and can be
   undone (Un-vet) until submitted. Vets are included in the submission.
2. **Submit** builds the payload and BOTH (a) triggers a file download named
   `budget-submission-no-<N>-<publish-date>.json` and (b) copies the same JSON text to the clipboard
   (`navigator.clipboard` with `execCommand('copy')` fallback). Show a clear confirmation ("Downloaded + copied — send
   this file to the Gazette inbox or paste it in chat"). If the clipboard fails (e.g. file:// on some phones) or the
   download is blocked, show the JSON in a selectable read-only textarea with a "Select all" / "Copy" button
   and instructions. Always show the JSON box on demand ("Show JSON").
   Payload = the existing `/submit` payload shape exactly (publishDate, practice, pretend, targetWeek, issue,
   includedSlots, excludedSlots, photoIncludes, notes, slotNotes, answers, order, pageVersion
   (use "budget-standalone-v1"), submittedAt (ISO with local offset, set client-side)) PLUS
   `vets: [{id, vet_notes}]` for every item/photo Frank vetted in this session, and `vetted` flag on slot entries
   reflecting vets. Unsubmitted changes after a submit should be clearly flagged ("changed since last submit").
3. **Autosave** to localStorage, keyed by issue (e.g. `gazette-budget:<issue.number>:<publish.date>:<hash of data>`
   or similar so a regenerated page with new data doesn't load stale state wrongly — but DO keep Frank's notes/answers
   if only data changed: key by issue number + week, and store a version stamp; on mismatch keep answers/notes/includes/
   order/vets for ids still present). Autosave on every change (debounced). Restore on load with a small
   "Restored your progress from <time>" notice. **Reset** button with confirm that clears state for this issue.
   If localStorage is unavailable (private mode / file:// quirks) the page must still work, with a small notice.
4. **Responsive**, phone (390px) and laptop (1280px) both first-class:
   - Cleaner hierarchy, **sticky summary bar** (fit % + words room/over, counters in/need vet/questions, jump buttons,
     Submit) that stays compact on phone (single row or two compact rows). Jump-to section list becomes a
     collapsible/horizontal chip row on phone, sidebar on desktop.
   - Fewer competing badges: one primary status pill per card (Vetted / Needs your vet / Waiting on results /
     Question for you), secondary info as muted text. Larger touch targets (>=44px) for Include, Vet, up/down.
   - Smooth expand/collapse (use `<details>`/CSS transitions; no layout jank), fast first paint (render cards
     from inlined JSON; no heavy work on input — debounce totals).
   - Newspaper-ish but plain: serif headings (Georgia/"Times New Roman" stack), clean sans body (system-ui),
     ink-black/paper-white palette with one accent colour, thin rules. No gimmicks, no animations beyond expand/collapse.
   - Respect `prefers-color-scheme` only if cheap; not required. Accessible labels, focus states, keyboard usable.
   - Make sure nothing overflows horizontally at 390px (tables in drafts scroll inside their own container).
5. Reorder up/down works within a section and is saved in `order`.
6. Include is locked until vetted (on file OR vetted locally); un-vetting a locally vetted card re-locks and unchecks it.

## Testing you must do yourself before finishing
- Generate the page from the real lineup + `--staging-week staging/weeks/2026-10-26` (the No. 4 pile, which matches
  the current lineup) and from the default `staging/weeks/next` (No. 5 pile, many lineup items will be missing —
  must not crash). Sanity-check the HTML (no `http(s)://` resource loads; parse the inlined JSON).
- Run the JS in a headless Chrome if possible (`/usr/bin/google-chrome --headless=new --dump-dom` or similar),
  at least a smoke test with no JS errors. Pure-JS logic (cost model, payload) should be written so it can be
  exercised.
- Test `ingest_budget_submission.py` ONLY against a throwaway copy (`cp -r` staging week + submissions to /tmp and
  pass `--staging-week/--submissions`), and with `--dry-run` against the live paths. Never write to the live
  `staging/` or `budget-demo/submissions/` while testing.
- Add `budget-demo/out/` to `.gitignore`.
- Add a short `budget-demo/STANDALONE-README.md`: how Monday routine generates it, how Frank submits, how Clark ingests.
