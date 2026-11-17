# Shared Template A composer

Going-forward home for the print compositor (adopted 2026-11-11 from the Fable design review, general changes only). An issue recipe is data plus block order; typography, boards, furniture and the stylesheet live here so a design fix reaches every future issue.

| File | What it is |
|---|---|
| `template-a.css` | The one stylesheet. New issues must not scrape CSS out of `issues/2026-10-13/issue.html`. |
| `gazette.py` | Composer helpers. The repo root is derived from this file (never a hardcoded absolute path). |
| `render.py` | HTML to PDF via Chrome CDP, plus the fill instrument and the art-fit pass. |
| `art.py` | Art-fit policy: eligibility, candidate list, `choose()`. No Chrome. |
| `fit.js` | Dumb apply/reset/measure helpers, evaluated once per Chrome session. |
| `balance.py` | Row-balance pass, **report-only** since 2026-11-16 (lists holes with suggestions; `--balance=pair` may pair two stacked photos; never moves boxes, dissolves rows or crops). |
| `eyecheck.py` | The eye check every proof must pass before it goes to Frank: previews, pixel blank map, instrument FLAGs, length targets, and a vision critique by a different model (`sonnet`). `--verify <pdf>` is the send gate. |
| `arrange.py` | Renders a recipe's candidate ARRANGEMENTS and ranks them by the eye check's numbers (`--eye=2` adds the vision critique for the top two). |
| `test_spacing.py` | Spacing tokens, the unwrap fix, copy lengths, and the eye check's offline parts (Chrome). |
| `test_gazette.py` | Golden checks: `python3 compose/test_gazette.py`. |
| `test_art.py` | Art-fit unit tests (no Chrome): `python3 compose/test_art.py`. |
| `test_art_fixtures.py` | Chrome fixtures (writes only under `/tmp/gz-fixtures/`): `python3 compose/test_art_fixtures.py`. |
| `recipe_template.py` | Starter recipe for the next issue. Copy it to `issues/<date>/recipe/compose.py` after the budget is approved. |
| `vendor/` | `pyphen` (hyphenation), installed with `pip install --target compose/vendor pyphen`. |

`prototype/render.py` is a thin shim that runs `compose/render.py`, so older commands still work. `prototype/` otherwise stays the historical layout sandbox (`monday-vN.html`).

## Build an issue

```
python3 compose/arrange.py issues/<date>                      # optional: rank the recipe's arrangements
python3 issues/<date>/recipe/compose.py x                     # recipe/arrangement.json + recipe/lengths.json
python3 compose/render.py issues/<date>/issue.html issues/<date>/en-garde-gazette-no-<N>-<date>.pdf --author="Nico's Dad" --report=issues/<date>/fit-report.json
python3 compose/eyecheck.py issues/<date>/en-garde-gazette-no-<N>-<date>.pdf --report=issues/<date>/fit-report.json
#   -> eye-check.json / eye-check.md and 200 dpi preview-p1/p2.png; FAIL lists fixes and length targets
python3 compose/eyecheck.py --verify issues/<date>/en-garde-gazette-no-<N>-<date>.pdf   # SENDABLE or not
```

Then Clark opens every preview himself before the proof goes out. A render that FLAGs writes
`<name>.FAILED.pdf` and leaves the proof path untouched.

**Copy lengths.** A recipe can offer an item in `short` / `standard` / `long` copy
(`copy_length(item, {...}, picks)`), all from vetted sources; `recipe/lengths.json` or
`--len=item:long` picks per issue. Grow/shrink is the editor's call after the eye check.

**Arrangements.** A recipe can declare `ARRANGEMENTS` and `build(name, picks)`: tall vs wide
boxes (`box_table(shape=)`), photo pair (`photo_pair()`) vs float, rail vs full width.
`recipe/arrangement.json` names the one the proof uses.

- `x` loads the issue's `recipe/overrides.json`, as before.
- An issue whose `issue.json` status starts with APPROVED is frozen. Composing it in place needs `--force`, or `--out=PATH` to write a trial copy somewhere else. `render.py` uses the same rule for the PDF path. Published Nos. 1–7 stay frozen.
- Previews are 200 dpi (STYLE-GUIDE §7).
- Fitting is on by default when the HTML has `[data-art]` slots (`--no-fit` skips it). `--fit-report=FILE.json` writes the art decisions; `--report` includes them under `art_fit`.

## Rules the helpers apply

**Kickers** (`piece(..., kicker=)`, `stack()`). A kicker is 7.25pt bold sans caps, smaller than any headline, never underlined. When two adjacent pieces in a `stack()` share a kicker, it prints once.

**Hyphenation** (`paras()`). Body paragraphs get soft hyphens from `pyphen`. Skipped: capitalised words (names, places), words joined by a hyphen or apostrophe, anything touching a digit, slash or dot, and the last word of a paragraph. Headlines, deks, captions and table cells are not auto-hyphenated. Existing hard hyphens in letter-letter compounds (`regular-fee`, `triple-fee`) are stored as U+2011 (non-breaking hyphen) so they stay visible and do not disappear at a line break. The CSS uses `hyphens: manual`, so the result does not depend on the browser.

**Club Results** (`results_table()`). Rows come in as vetted: fencer, "Tournament, Event (Date)", finish. The tournament and date print once as a sub-row; each fencer then gets one row. A new sub-row starts when the tournament or the date changes.

**Tournament blocks** (`tourney()`). One block per tournament, as in STYLE-GUIDE §10a. With `layout="auto"`, a Day column replaces the day sub-rows when the sub-rows would outnumber half the data rows (most days hold one event). Busy tournaments keep sub-rows.

**Split boards** (`board_split()`). Box notes go under the shorter half rather than full width under both. The split ratio is chosen from 50/50, 45/55, 40/60 and 3:5 (and their mirrors) to give the shortest box. `render.py` measures the real result.

**Photo credit** (`credit_line()`, `check_credit()`). For new work, one short black line under the caption: author / source, licence with version, "(cropped)" if changed. Do not file-name or URL a printed credit. The full attribution stays in `sources.json`. Published issues keep the credit they already printed.

**Photo placement** (`photo_span()`). A results photo runs two columns wide under the lead only if, uncropped at that width, it stays within the hard 4.5in cap (the 2.2in ceiling of STYLE-GUIDE §19 is now a soft WARN to mention to Frank) and still has 150 dpi. Otherwise it runs one column in the rail. Layout never silently CSS-crops, and the balancer no longer crops. `photo_pair()` puts two photos side by side with no column rule between them.

**Art-fit** (`art()`, `load_art_manifest()`). For No. 7 onward, put scalable pictures in `recipe/art.json` and emit them with `art()`. Required fields: `id`, `src`, `kind` (`photo` / `comic` / `diagram` / `illustration`), `alt`, `region`. Photos still need a caption and a credit. The fitter measures leftover room and picks a grid width (stack, then a float beside following prose, then a last-resort gutter of at most 0.25in, flush left). A legal stack always wins. Wordless comics may go as small as 1.6in; lettered comics stay at 3.0in hard / 4.5in soft. Diagrams stay stack-only by default; full width needs `allow_full`. The art must come before any prose that should wrap beside it. Do not use `.fill-art` or a hard `max-height`. Nothing in the pipeline crops. Details: STYLE-GUIDE §19.

**Row balance** (`compose/balance.py`). After art-fit, a report-only pass lists every remaining in-row hole with a plain-words suggestion (grow/trim copy, scale art, another arrangement). It moves nothing. `--balance=pair` opts in to the one move left (two stacked photos side by side, kept only if the page gets better). It never dissolves a row, strips a neighbour or crops. `--no-balance` skips the pass.

**Spacing tokens** (`template-a.css`). `--gap-block` 7pt between stacked blocks (one page-level rule, one column rule), `--gap-gutter` 9pt side by side, `--gap-inner` 3pt inside a block, `--gap-tight` 1.5pt for captions. Do not hand-set block margins elsewhere.

**Checks at compose time.** Weapon spelled both "épée" and "epee" in running text: warning. A credit that still contains a file name or URL: warning (the strict check is on `photo()` / `credit_line()` so a published long credit is not rewritten).

## What the fill instrument reports

- **Gap above the footer, per column**, including `.page2-lower` and other multi-column splits. The worst column is the page's number. FLAG over 0.75in, or if the page is too deep.
- **Footer pin.** The footer's bottom edge vs the expected 10.1in content-box bottom, measured from the top of `.page` (not the element's used height). FLAG if the footer is more than 0.15in away from that bottom — this catches a shrink-wrapped page whose content-to-footer gap looks fine but leaves blank paper below the footer.
- **Column bottom gaps** for every column, rail and box in every row band (the row content-box bottom minus that column's ink). FLAG over 0.35in. This is the in-row hole the footer-gap check cannot see.
- **Float holes** beside a floated art slot (art vs wrapping text). FLAG over 0.35in.
- **Column spread** for every multi-column row, including board halves and prose columns. FLAG over 0.5in.
- **Type floor** across every element that holds text, including ears, captions, credits and kickers. FLAG under 7pt.
- **Hyphenated line breaks.** Zero on a page with justified text prints a WARN.
- **Inter-block gaps** in the page stack and in every column, ink to ink (box borders count as ink). FLAG outside 5–12.5pt (the token is 7pt).
- **Side holes** beside stacked art with nothing next to it (over 0.25in), words per square inch (for the eye check's length targets), and picture rectangles (masked out of the pixel blank map).
- **Send gate.** The PDF is written as `<name>.draft.pdf`; any FLAG renames it `<name>.FAILED.pdf` and leaves the proof path untouched (`--allow-flag` overrides, for trials).

`--report=FILE.json` saves the raw measurements (and `art_fit` when a fit ran). `--fit-report=FILE.json` saves only the art decisions.

## Budget page hand-off: `manualLayout` (not packed yet)

Budget version 2 (`pageVersion: budget-paper-v2`) can send an optional placement contract on a
submission and on the decision log ingest writes to `budget-versions.json`:

- `mode`: `'auto'` or `'manual'`. Older submissions omit it; treat a missing field as auto.
- `manualLayout`: `{slotKey|mediaId: {page, col, span, topIn, heightIn}}` when mode is manual.
  `page` is `1` or `2`, `col` is 0-based (`0`, `1` or `2`), `span` is `1`, `2` or `3` columns,
  and `topIn` / `heightIn` are inches from the top of the column well (below the folio furniture).
  Positions snap to the column grid and a 0.05-inch vertical grid. Blocks may overlap; ingest
  reports overlaps and overset as warnings and does not move them.

The existing `pages`, `resize`, and `layout` fields still apply. `manualLayout` is the frozen
geometry Frank set in Manual placement. **Compose does not yet read `manualLayout`.** Until a
later change teaches the composer to honor those positions, Clark matches a Manual budget by
hand when composing the proof, and flags anything that will not fit instead of moving it.

