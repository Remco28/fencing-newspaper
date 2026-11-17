# Standalone budget page

> **The page is the Budget spread** (`pageVersion: budget-paper-v2`; Budget version 2, with v2.1 Manual
> placement as of 2026-11-17). Always called **Budget**, never Dummy. Same builder, same one-file page, same ingest.
> What Frank sees: the two pages of the issue with each included item as a block sized by the capacity model,
> a bank of what isn't running, hatched holes for unfilled space (column-inches and words), and a slip per item (click or tap).
> A page that oversets hangs the overflow in red below a trim line (a spill well), with the overset in col-in and ≈words.
> Desktop: drag between the bank and the pages. Phone: open the slip and use Page 1 / Page 2 / Bank.
> - **Sign off the budget** shows the submission JSON; Download or Copy, then ingest as before.
> - Placement is **Auto** by default (the packer places and sizes blocks). A header switch freezes the current layout
>   into **Manual**: nothing re-packs on its own. Grab a block anywhere (a photo moves like any block — the browser's
>   own image drag is off in Manual); a dashed outline shows the snapped landing spot and the pages stay still while
>   you drag. Releasing over the bank, or anywhere left of page 1, takes the block off the pages; Esc cancels. Width
>   and height handles, Wide/Tall, and Expand/Shrink/Clear change only that block. Overlapping blocks get a red outline
>   and a banner (warnings only — nothing is auto-fixed). Undo goes back up to 40 steps; Back to Auto asks first.
> - Each block is a frame. Text re-flows on a new width, and its bottom edge asks Clark for the length that fills the
>   frame. Photos and comics keep their shape and are scaled to fit the frame, never cropped; depth is free on the
>   0.05 in grid. The slip has Smaller, Bigger and Natural size buttons. The 2.2 in photo guide and the 4.5 in hard
>   cap are notes on the slip, not a Manual resize limit. Sections with a tall/wide variant (from
>   `scripts/budget_page/layouts.json`, inlined by the builder; compose/ does not yet expose a registry) switch on
>   the block. On a phone, the slip has the same controls.
> - Optional submission fields: `publishDateAlt` (YYYY-MM-DD or null), `budgetVersion`, `dataVersion`, `pages`
>   (`{slots: {slotKey: 1|2 or {page, span, widthIn, heightIn}}, photos: {mediaId: same}}` — a bare 1|2 means page only;
>   the object is used when art was resized), `resize` (`{slotKey: {direction: 'expand'|'shrink', target, ...}}`),
>   `layout` (`{slotKey|mediaId: 'wide'|'tall'}`, names shared with compose/), `mode` (`'auto'|'manual'`), and, when
>   manual, `manualLayout` (`{slotKey|mediaId: {page, col, span, topIn, heightIn}}`; `col` is 0-based). Ingest records
>   them on the decision when present and never requires them. A stale `budgetVersion` does not block an ingest.
>   Older submissions without these fields still ingest. Overlaps and overset in a manual layout are warnings, never
>   silently fixed. Compose does not yet pack from `manualLayout` (Clark matches it by hand; see `compose/README.md`).
> - User-facing copy says “Clark” (or “Clark Kent” / “layout editor”), not “desk”. Internal ids and CSS classes (`desk`,
>   `data-tab="desk"`) are unchanged. “Desktop” (the computer) is unchanged.
> - Thumbnails in the standalone HTML are small B&W JPEGs inlined as data-URIs by the builder (CSP `default-src 'none'`;
>   no network).
> - Placement is `pages`, not `notes`. A lineup slot may still carry an optional `page: 1|2` to set its starting page when
>   no ingested `pages` field is on file.
> - Unvetted items and photos cannot be placed on the pages until they are vetted on the slip (drag and the p.1/p.2 buttons
>   are disabled). Ingest rejects (exit 4) a submission that includes an unvetted staging item or photo; a vet in the same
>   payload is enough. Missing ids from an older issue stay warnings.
> - Section history (the Sections tab) is derived on every build by `scripts/build_section_history.py` from the published issues.
> - Block sizes use `lineup.capacity` with `scripts/budget_page/calibration.json` laid over it (fill calibration against Nos. 1–7).
> - Photo vets in `vets` are written to `media/manifest.json` (vetted, vetted_at, vetted_by, vet_notes) so the next build — and
>   next week — shows the photo already vetted. An unvetted photo is never auto-queued: not from a lineup `proposed` flag, not
>   from last sitting's `photoIncludes`, and not in the submission's `photoIncludes`.
> - Tests use the frozen No. 7 snapshot in `scripts/tests/fixtures/` (never live staging):
>   `python3 scripts/tests/test_budget_page.py`, `python3 scripts/tests/test_section_history.py`,
>   `python3 scripts/tests/test_budget_interactions.py` (headless Chrome, real pointer events, including Manual;
>   skipped without Playwright). Optional smoke: `python3 scripts/tests/smoke_budget_chrome.py PAGE.html [SCREENSHOT_DIR]`.

One self-contained `.html` file Frank opens on his laptop or phone. It works offline, needs no server,
and makes no network requests (a CSP `default-src 'none'` blocks them). It replaces the tunnel and server
for the weekly budget. `practice.html` + `server.py` still work and are kept as the fallback.

Requirements: `STANDALONE-REQUIREMENTS.md`. Code: `scripts/build_budget_html.py` (generator),
`scripts/budget_page/` (page template, CSS, `core.js` logic, `ui.js`), and `scripts/ingest_budget_submission.py`.

## 1. Generate the page

Usual moment is the Monday full pass, but the weekly rhythm (Frank, 2026-11-17) is: curate through
the week, Clark preps sections ahead, and generate the Budget when it is ready. Auto placement is
the default; Frank uses Manual only for final layout tweaks or to push one layout harder.


After the lineup (`budget-demo/practice-lineup.json`, schema 2, unchanged) is written for the week:

```sh
python3 scripts/build_budget_html.py
# -> budget-demo/out/budget-no-<N>-<publish-date>-v<K>.html   (prints version, size, counts, missing items; --preview = unnumbered)
```

Defaults: lineup `budget-demo/practice-lineup.json`, staging `staging/weeks/next` (items.json + media/).
Flags: `--lineup FILE`, `--staging-week DIR`, `--out FILE|DIR`, `--thumb-width 360`, `--quality 70`.

- `budget-demo/out/` is gitignored. The page contains unvetted content and minors' names, so the generator
  refuses to write anywhere in the repo that git would track.
- If lineup items aren't in the staging week (for example, rolled out of `next`), they are listed in the
  output, and their cards say "Not in staging" and can't be vetted or included. Missing media files just
  get no thumbnail.
- Thumbnails are B&W JPEGs ("as printed"), about 360 px wide. A typical page is about 150–350 KB.
- Each build stamps a data version (a hash of lineup + items + manifest). Frank's saved progress survives
  a rebuild (see below).

Send Frank the `.html` file (email attachment, Drive, AirDrop, etc.). Don't commit it or publish it to the site.

## 2. Frank: review and submit

Open the file in any browser. On a phone, open it from Files/Downloads.

- Tick **Include** for what goes in. Include stays locked until an item is vetted (on file, or by you on
  this page).
- **Vet** is local. It marks the card "Vetted by you · not sent yet", unlocks Include (proposed items switch
  in automatically), updates the fit meter, and gives you an optional vet note. **Un-vet** undoes it until
  you submit. Photos can be vetted the same way.
- Answer the red **Questions for Frank** in place. Add notes per card and overall notes at the bottom.
  Use ↑/↓ to reorder within a section. Change the publish day at the top.
- The sticky bar shows how full the issue is (percent of two pages, words of room or over, and the
  projection if you vet what Clark proposes). Its **in / to vet / Qs** buttons jump to the next matching card.
- Progress autosaves in the browser (localStorage) and is restored on reopen ("Restored your progress
  from …"). If Clark sends a rebuilt page for the same issue, your answers, notes, includes, order and
  vets are kept for items still on the page. **Reset this issue…** at the bottom clears it. In private
  mode the page still works but shows a notice that it can't save.
- **Submit** downloads `budget-submission-no-<N>-<publish-date>.json` and copies the same JSON to the
  clipboard. Send the file to the Gazette inbox, or paste it into chat. If copy or download fails, the
  JSON opens in a box with Select all / Copy / Download / Share. **Show JSON** at the bottom always
  opens it. If you change anything after submitting, the bar says "Changed since your last submit", and
  you should submit again.

The payload has the same shape as the server's `/submit` (publishDate, practice, pretend, targetWeek,
issue, includedSlots, excludedSlots, photoIncludes, notes, slotNotes, answers, order, and submittedAt
with a local offset), plus `vets: [{id, vet_notes}]`. `pageVersion` is `budget-paper-v2`. Optional
Budget fields (`publishDateAlt`, `budgetVersion`, `dataVersion`, `pages`, `resize`, `layout`, `mode`,
`manualLayout`) are included when set; see the callout above.

## 3. Clark: ingest the submission

Save the file Frank sent, or paste his chat JSON into a file (code fences or chatter around it are fine;
`-` reads stdin). Check it first:

```sh
python3 scripts/ingest_budget_submission.py ~/budget-submission-no-5-2026-11-02.json --dry-run
python3 scripts/ingest_budget_submission.py ~/budget-submission-no-5-2026-11-02.json
```

This does what `server.py` did for `/submit` + `/vet`:

- writes `budget-demo/submissions/budget-<stamp>.json` and `approvals.json`. `submittedAt` is the ingest
  time, as the server stamped it. The page's own time is kept as `clientSubmittedAt`.
- for each `vets` entry, sets `vetted`, `vetted_at`, `vetted_by: "frank"` and `vet_notes` on the item in
  `<staging-week>/items.json`, and appends the vet-log line to both `vet-log.jsonl` files (`source:
  "budget-page-standalone"`). A photo's media id is not in items.json: the same fields are written to
  `<staging-week>/media/manifest.json` and logged with kind `"media"`, so the next build — and next
  week — shows the photo already vetted.
- reports ids found in neither items.json nor the media manifest as "not found". The vet is still
  recorded in approvals.json.
- refuses (exit 4, writes nothing) if an included slot's item, or a photo in `photoIncludes`, is in
  staging and still unvetted after this submission's vets are applied. Missing ids from an older
  issue stay warnings.
- prints a summary: issue, publish date, included slots, vets applied/not found, answers, notes, and
  warnings (overlaps or overset in a manual layout are warnings, never silently fixed).

Flags: `--staging-week`, `--submissions`, `--lineup` (defaults follow `GAZETTE_STAGING_WEEK`,
`GAZETTE_SUBMISSIONS` and `GAZETTE_LINEUP`, as in server.py), `--now ISO` (for tests), `--dry-run`, and
`--force`. If the submission's issue number or `targetWeek` doesn't match the lineup, the script refuses
it (exit 2) unless you pass `--force`. Ingesting the same file again just re-applies it; the vet-log
records `already_vetted: true`.

Optional Budget version 2 fields (`mode: 'auto'|'manual'` and, when manual, `manualLayout` mapping
each included slot or photo to `{page, col, span, topIn, heightIn}`) are stored on the decision when
present. Older submissions without them still ingest. Overlaps and overset past the trim are printed
as warnings and are not moved. Compose does not yet pack from `manualLayout` (see `compose/README.md`).

Manual placement on the page (2026-11-17): one pointer drag moves page blocks and bank strips (the
browser's own drag is off in Manual, so a photo moves like any block); the dashed outline is where it
lands; releasing over the bank or left of page 1 pulls it off the pages; Esc cancels. Each block is a
frame. Text re-flows on a new width, and its bottom edge asks Clark for the length that fills the frame.
A photo or comic keeps its shape and is scaled to fit its frame, never cropped; the 2.2in photo guide
is a note on the slip, not a limit. For art, `manualLayout.heightIn` is the frame (picture plus caption
allowance) and, in Manual, `pages.photos` `widthIn`/`heightIn` give the picture as it sits in that frame.


Test against a throwaway copy, never the live paths:

```sh
cp -r staging/weeks/next /tmp/wk && cp -r budget-demo/submissions /tmp/subs
python3 scripts/ingest_budget_submission.py sub.json --staging-week /tmp/wk --submissions /tmp/subs
```

### Decisions Frank gives in chat

When Frank answers in chat instead of submitting the page, log it as the next decision so the page
version and "decisions captured through" stay honest:

```sh
python3 scripts/record_chat_decision.py --at 2026-11-02T20:56:00-05:00 --text "his words, verbatim" \
    --include club-results --answer camp "the question" "his answer" --change "what you applied" --dry-run
```

It copies the previous decision's page state (includes, excludes, order, photo picks, slot notes,
answers, notes), applies `--include/--exclude/--after SLOT=PREV`, and appends an entry with
`kind: "chat"`, `source: "chat:frank:<time>"`, `chat.text` verbatim and `changes[]`, plus one
`chat-decision` line in the week's `vet-log.jsonl`. `--at` is when Frank said it; the page uses it as
"decisions captured through" and drops browser-saved progress older than it. The script does not edit
items or the lineup: close questions, add rows and update facts by hand, then rebuild.

## Notes (Oct 26 follow-up)

- The headline counter counts items only ("3 need vet"); photos are shown separately ("4 photos"). Photos can still be vetted on the page.
- Ingest: photo vets (media ids) are written to `media/manifest.json` (vetted, vetted_at, vetted_by, vet_notes) as well as `approvals.json` and the vet log, so they persist into the next build and the next week.
- Ingest appends vet notes to an item's existing `vet_notes` as `[YYYY-MM-DD] Frank: <note>` on a new line instead of replacing them.
- Output name: `budget-no-<N>-<date>-v<K>.html`. K is the per-week budget version, kept with Frank's decision log in `<staging-week>/budget-versions.json`. The page starts from the latest ingested decisions and shows "Budget vK · decisions captured through <time ET>". Rebuilding unchanged data keeps K. `--preview` writes `-preview.html` without a number. `--out` still overrides. The build stops if a submission JSON for this issue is waiting un-ingested (uploads, ~/Downloads, `budget-demo/submissions/inbox/`).
