# Standalone budget page

One self-contained `.html` file Frank opens on his laptop or phone. It works offline, needs no server,
and makes no network requests (a CSP `default-src 'none'` blocks them). It replaces the tunnel and server
for the weekly budget. `practice.html` + `server.py` still work and are kept as the fallback.

Requirements: `STANDALONE-REQUIREMENTS.md`. Code: `scripts/build_budget_html.py` (generator),
`scripts/budget_page/` (page template, CSS, `core.js` logic, `ui.js`), and `scripts/ingest_budget_submission.py`.

## 1. Monday routine: generate the page

After the lineup (`budget-demo/practice-lineup.json`, schema 2, unchanged) is written for the week:

```sh
python3 scripts/build_budget_html.py
# -> budget-demo/out/budget-no-<N>-<publish-date>-<pile>.html   (prints size, counts, missing items)
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
issue, includedSlots, excludedSlots, photoIncludes, notes, slotNotes, answers, order, pageVersion
`budget-standalone-v1`, and submittedAt with a local offset), plus `vets: [{id, vet_notes}]`.

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
  "budget-page-standalone"`).
- reports ids not in items.json as "not found" (for example, a photo's media id; the manifest isn't
  changed, as with the server). The vet is still recorded in approvals.json.
- prints a summary: issue, publish date, included slots, vets applied/not found, answers, notes, and
  warnings (for example, an included item that isn't vetted).

Flags: `--staging-week`, `--submissions`, `--lineup` (defaults follow `GAZETTE_STAGING_WEEK`,
`GAZETTE_SUBMISSIONS` and `GAZETTE_LINEUP`, as in server.py), `--now ISO` (for tests), `--dry-run`, and
`--force`. If the submission's issue number or `targetWeek` doesn't match the lineup, the script refuses
it (exit 2) unless you pass `--force`. Ingesting the same file again just re-applies it; the vet-log
records `already_vetted: true`.

Test against a throwaway copy, never the live paths:

```sh
cp -r staging/weeks/next /tmp/wk && cp -r budget-demo/submissions /tmp/subs
python3 scripts/ingest_budget_submission.py sub.json --staging-week /tmp/wk --submissions /tmp/subs
```

## Notes (Oct 26 follow-up)

- The headline counter counts items only ("3 need vet"); photos are shown separately ("4 photos"). Photos can still be vetted on the page.
- Ingest: photo vets (media ids) are recorded in `approvals.json` and the vet log; like the old `/vet` flow, `items.json` and the media manifest are not changed for photos.
- Ingest appends vet notes to an item's existing `vet_notes` as `[YYYY-MM-DD] Frank: <note>` on a new line instead of replacing them.
- Output name: `budget-no-<N>-<date>-<pile>.html` (pile = staging-week folder name, omitted when it equals the date). `--out` still overrides.
