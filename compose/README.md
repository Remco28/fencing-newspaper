# Shared Template A composer

Going-forward home for the print compositor (adopted 2026-11-11 from the Fable design review, general changes only). An issue recipe is data plus block order; typography, boards, furniture and the stylesheet live here so a design fix reaches every future issue.

| File | What it is |
|---|---|
| `template-a.css` | The one stylesheet. New issues must not scrape CSS out of `issues/2026-10-13/issue.html`. |
| `gazette.py` | Composer helpers. The repo root is derived from this file (never a hardcoded absolute path). |
| `render.py` | HTML to PDF via Chrome CDP, plus the fill instrument and the art-fit pass. |
| `art.py` | Art-fit policy: eligibility, candidate list, `choose()`. No Chrome. |
| `fit.js` | Dumb apply/reset/measure helpers, evaluated once per Chrome session. |
| `test_gazette.py` | Golden checks: `python3 compose/test_gazette.py`. |
| `test_art.py` | Art-fit unit tests (no Chrome): `python3 compose/test_art.py`. |
| `test_art_fixtures.py` | Chrome fixtures (writes only under `/tmp/gz-fixtures/`): `python3 compose/test_art_fixtures.py`. |
| `recipe_template.py` | Starter recipe for the next issue. Copy it to `issues/<date>/recipe/compose.py` after the budget is approved. |
| `vendor/` | `pyphen` (hyphenation), installed with `pip install --target compose/vendor pyphen`. |

`prototype/render.py` is a thin shim that runs `compose/render.py`, so older commands still work. `prototype/` otherwise stays the historical layout sandbox (`monday-vN.html`).

## Build an issue

```
python3 issues/<date>/recipe/compose.py x
python3 compose/render.py issues/<date>/issue.html issues/<date>/en-garde-gazette-no-<N>-<date>.pdf --author="Nico's Dad" --report=issues/<date>/fit-report.json
pdftoppm -r 200 -png <out.pdf> issues/<date>/preview
```

- `x` loads the issue's `recipe/overrides.json`, as before.
- An issue whose `issue.json` status starts with APPROVED is frozen. Composing it in place needs `--force`, or `--out=PATH` to write a trial copy somewhere else. `render.py` uses the same rule for the PDF path. Published Nos. 1–6 stay frozen.
- Previews are 200 dpi (STYLE-GUIDE §7).
- Fitting is on by default when the HTML has `[data-art]` slots (`--no-fit` skips it). `--fit-report=FILE.json` writes the art decisions; `--report` includes them under `art_fit`.

## Rules the helpers apply

**Kickers** (`piece(..., kicker=)`, `stack()`). A kicker is 7.25pt bold sans caps, smaller than any headline, never underlined. When two adjacent pieces in a `stack()` share a kicker, it prints once.

**Hyphenation** (`paras()`). Body paragraphs get soft hyphens from `pyphen`. Skipped: capitalised words (names, places), words joined by a hyphen or apostrophe, anything touching a digit, slash or dot, and the last word of a paragraph. Headlines, deks, captions and table cells are not auto-hyphenated. Existing hard hyphens in letter-letter compounds (`regular-fee`, `triple-fee`) are stored as U+2011 (non-breaking hyphen) so they stay visible and do not disappear at a line break. The CSS uses `hyphens: manual`, so the result does not depend on the browser.

**Club Results** (`results_table()`). Rows come in as vetted: fencer, "Tournament, Event (Date)", finish. The tournament and date print once as a sub-row; each fencer then gets one row. A new sub-row starts when the tournament or the date changes.

**Tournament blocks** (`tourney()`). One block per tournament, as in STYLE-GUIDE §10a. With `layout="auto"`, a Day column replaces the day sub-rows when the sub-rows would outnumber half the data rows (most days hold one event). Busy tournaments keep sub-rows.

**Split boards** (`board_split()`). Box notes go under the shorter half rather than full width under both. The split ratio is chosen from 50/50, 45/55, 40/60 and 3:5 (and their mirrors) to give the shortest box. `render.py` measures the real result.

**Photo credit** (`credit_line()`, `check_credit()`). For new work, one short black line under the caption: author / source, licence with version, "(cropped)" if changed. Do not file-name or URL a printed credit. The full attribution stays in `sources.json`. Published issues keep the credit they already printed.

**Photo placement** (`photo_span()`). A results photo runs two columns wide under the lead only if, uncropped at that width, it stays within the 2.2in ceiling of STYLE-GUIDE §19 and still has 150 dpi. Otherwise it runs one column in the rail. Layout never crops.

**Art-fit** (`art()`, `load_art_manifest()`). For No. 7 onward, put scalable pictures in `recipe/art.json` and emit them with `art()`. Required fields: `id`, `src`, `kind` (`photo` / `comic` / `diagram` / `illustration`), `alt`, `region`. Photos still need a caption and a credit. The fitter measures leftover room and picks a grid width (stack, then a float beside following prose, then a last-resort gutter of at most 0.25in, flush left). A legal stack always wins. Wordless comics may go as small as 1.6in; lettered comics stay at 3.0in hard / 4.5in soft. Diagrams stay stack-only by default; full width needs `allow_full`. The art must come before any prose that should wrap beside it. Never crop, and do not use `.fill-art` or a hard `max-height`. Details: STYLE-GUIDE §19.

**Checks at compose time.** Weapon spelled both "épée" and "epee" in running text: warning. A credit that still contains a file name or URL: warning (the strict check is on `photo()` / `credit_line()` so a published long credit is not rewritten).

## What the fill instrument reports

- **Gap above the footer, per column**, including `.page2-lower` and other multi-column splits. The worst column is the page's number. FLAG over 0.75in, or if the page is too deep.
- **Column spread** for every multi-column row, including board halves and prose columns. FLAG over 0.5in.
- **Type floor** across every element that holds text, including ears, captions, credits and kickers. FLAG under 7pt.
- **Hyphenated line breaks.** Zero on a page with justified text prints a WARN.

`--report=FILE.json` saves the raw measurements (and `art_fit` when a fit ran). `--fit-report=FILE.json` saves only the art decisions.
