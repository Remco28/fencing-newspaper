# Visual Review — En Garde Gazette (HTML + PDF)

**Reviewer:** DeepSeek V4.1 Flash
**Date:** 2026-10-06
**Scope:** `prototype/monday-v5.html` (current template) and `prototype/render.py` → the rendered PDF.
**Companion to:** `REVIEW-FROM-BUFFY-REVIEWER.md` (that one covers process/architecture; this one is the visual pass).
**Nature:** read-only. No repo file was changed by this review; this document is the only write.

Everything below was measured, not eyeballed. Reproduce commands are in §4.

---

## 0. What the render actually does today

```
$ python3 prototype/render.py prototype/monday-v5.html /tmp/gazette-v5-check.pdf
wrote /tmp/gazette-v5-check.pdf
page 1: gap above footer 0.57in [OK]
page 2: gap above footer 0.68in [OK]
row 1: column spread 0.00in [OK]
row 2: column spread 0.00in [OK]
row 3: column spread 0.00in [OK]
row 4: column spread 0.00in [OK]
pdf Pages:           2
```

Exit code **0**. Page size 612 × 792 pt (Letter), 2 pages, no browser chrome — those are correct, and the masthead artwork is pure grayscale (0% colored pixels), so it is B&W-safe. The good news ends there: **"all green" is not true.** The measurements that look healthy are either wrong or incomplete. The six findings below are why.

Priority order: **V1 and V2 are correctness bugs** (the paper is wrong / the tool lies). V3–V6 are visible layout defects. V7–V11 are spec compliance.

---

## V1 — Every right-aligned header renders LEFT. `class="r"` on `<th>` is dead. (highest impact)

The template puts `class="r"` on the numeric/date headers, clearly intending §14 ("numeric and date columns right-align **BOTH** the header and the data"). It has no effect. Measured text positions (inches from page-left), header vs its data row:

| Board | Column | Header text x | Data text x | Header | Data |
|---|---|---|---|---|---|
| Ratings Earned | Rating | 5.91 → 6.31 | 6.21 → 6.40 | **left** | right |
| Ratings Earned | Event | 6.46 → 6.81 | 6.87 → 7.35 | **left** | right |
| Signup Board | Closes | 4.20 → 4.63 | 4.53 → 4.84 | **left** | right |
| Where to Watch | When | 0.81 → 1.13 | 1.06 → 1.55 | **left** | right |
| Deadlines | Date | 0.09 → 0.37 | 0.37 → 0.69 | **left** | right |
| Club Results | Finish | 6.11 → 6.46 | 6.22 → 7.35 | **left** | right |

So `DATE` sits flush left over dates that are flush right — exactly the "reads as broken" case §14 was written to prevent. Six column pairs across five boards.

**Cause — CSS specificity, not markup.** In `monday-v5.html`:

```css
table.board th { …; text-align: left; }   /* (0,1,2) — one class + two elements */
td.r, th.r     { text-align: right; }     /* (0,1,1) — one class + one element  */
```

`table.board th` is *more specific* than `th.r`, so its `left` always wins. (`td.r`/`td.num` work only because `table.board td` never declares `text-align`.)

**Fix (one line):** give the right-alignment rule matching specificity:

```css
table.board th.r { text-align: right; }        /* (0,2,2) beats (0,1,2) */
```

Both header and data already use `padding-right: 4pt`, so they will line up once the header is right-aligned. Then re-check §14 on every board — this is precisely the "one template rule, all boards fixed" the guide asks for.

---

## V2 — The region-balance instrument is tautological; it can never report anything but 0.00in.

§18 claims `render.py` "reports per-row column-bottom spread" so a two-column hole can't ship. It doesn't. The instrument (`render.py` ~line 183) measures each `.cols3` child's **box height**:

```js
const hs = [...r.children].map(c => c.getBoundingClientRect().height);
return Math.max(...hs) - Math.min(...hs);
```

But `.cols3` is `display:flex` and the browser default is `align-items: stretch`, so **every child is forced to the tallest child's height.** The box heights are equal by construction; the spread is 0 by definition. That is why the output shows `0.00in [OK]` for all four rows on both pages, always.

Measuring what actually matters — each column's *content* depth (deepest descendant bottom) — the real spreads are **not** zero:

| Row | Columns | Real content depths (in) | Real spread | Instrument |
|---|---|---|---|---|
| Page 1, lead + rail | 2 | 2.702 \| 3.932 | **1.23in** | 0.00 [OK] |
| Page 1, 3 shorts | 3 | 1.820 \| 1.374 \| 1.671 | 0.446in | 0.00 [OK] |
| Page 2, passivity + joke | 2 | 1.072 \| 1.374 | 0.302in | 0.00 [OK] |
| Page 2, 3 rails | 3 | 7.417 \| 7.135 \| 6.693 | **0.73in** | 0.00 [OK] |

Two of four rows exceed §18's 0.5in limit and the tool calls both OK.

**Fix:** measure content bottoms, not box heights:

```js
const depth = c => { const top = c.getBoundingClientRect().top; let b = top;
  c.querySelectorAll('*').forEach(e => { const r = e.getBoundingClientRect(); if (r.bottom > b) b = r.bottom; });
  return b - top; };
const ds = [...r.children].map(depth);
return Math.round((Math.max(...ds) - Math.min(...ds)) * 100) / 100;
```

---

## V3 — The front page has a 1.33in hole under the lead, beside a full-height rail.

This is the exact defect §18 names ("a two-column-wide hole under a short lead next to a tall rail"). Rasterized at 150 dpi, the lead column's longest blank vertical band runs **5.12in → 6.45in = 1.33in tall and ~4.97in wide** (two columns). The lead text ends around 5.1in; the rail's two boxes run to ~6.4in; the `<hr>` follows at 6.45in. So the bottom two-thirds of the lead area is empty paper while the rail runs on beside it.

Below the threshold, the 3-shorts row is 0.45in spread — inside §18, but only just.

**Fix:** the front-page lead needs ~1.3in more body (≈ 100–130 words at 8.5pt over a ~4.97in measure, or one more rail box). This is a word-budget/oversupply problem (§11/§16), not a CSS problem — the template is fine, the front-page copy is short. Rebalance the lead against rail height per §17.

---

## V4 — Page 1 starts 0.20in low: `masthead001.png` carries invisible transparent padding.

§1 says margins "0.5in sides/top. No more, no less." Page 2's dateline rule starts at exactly 0.50in. **Page 1's first ink starts at 0.70in.** Measured content bbox:

```
page 1: margins L 0.493  R 0.500  T 0.700  B 0.440   ← top is 0.20in too deep
page 2: margins L 0.500  R 0.500  T 0.500  B 0.440
```

Cause: `masthead001.png` is 2170×725 RGBA and the artwork does **not** fill the canvas.

```
opaque bbox: x 45–2124, y 96–636   (of 2170×725)
transparent padding: left 45px, right 45px, top 96px, bottom 88px
→ 13.2% of the image height is blank above the logo, 12.1% below
```

Rendered at `width:62%` (4.65in box, 1.554in tall), the top 0.206in is transparent white — hence the 0.70in first-ink row. Two consequences:

1. **Page 1 violates the 0.5in top margin** and pushes everything down 0.20in.
2. A further ~0.19in of blank sits under the logo before the dateline. Together the masthead block wastes ~0.39in of vertical space — which is roughly the 0.4in the front page needs for V3's hole.

Also note the *visible* logo is 95.9% of 62% = **59.4% of the page width**, not the 62% §12 asks for (close enough visually, but the number in the guide is measuring the transparent box, not the mark).

**Fix (pick one):**
- **Crop the asset** to its opaque bbox (offset 45,96, size 2080×541) — then the image element's box equals the artwork and 62% is honest. Best.
- Or keep the asset and pull it up in CSS: `margin-top: -0.206in;` (fragile — breaks if the PNG is re-exported).

---

## V5 — "Where to Watch" has a 0.72in column and 5-line wrapped rows.

`table-layout: fixed` with `<colgroup><col><col style="width:0.8in"><col></colgroup>` splits the *remaining* width equally between the two unsized columns. Measured column widths:

```
Where to Watch — Epee on Screen (table 2.236in):
   Event = 0.718in | When = 0.8in | Watch = 0.718in
```

"October NAC, Orlando — Div I epee finals" in a 0.72in measure wraps to **5 lines**; the whole row is stretched to match. It is the tallest, most cramped board on the back page and drags the rail down. §15's intent ("content columns take the rest") is not achieved because *both* content columns are unsized.

**Fix:** size the Event column so it owns the leftover, e.g.

```html
<colgroup><col style="width:1.0in"><col style="width:0.7in"><col></colgroup>
```

Verify after: no row should exceed ~3 lines at 8.5pt.

---

## V6 — The left masthead flank wraps to a 4th line; the flanks don't align.

Measured: left flank height **0.625in = 4 lines**; right flank **0.469in = 3 lines**. The text layer confirms it:

```
VOL. I — NO. 005                    MONDAY EDITION
CHATHAM, N.J.                       OCTOBER 13, 2026
EPEE ONLY, AS                       PRICE: ONE TOUCH
ALWAYS
```

"EPEE ONLY, AS ALWAYS" doesn't fit one 1.31in line at 7.5pt + 0.4pt letter-spacing, so it breaks. Because `.masthead` is `align-items: center`, the two flanks are centered against each other and their lines no longer correspond — the classic "flanks look hand-made" tell.

**Fix:** shorten the line (e.g. "EPEE ONLY" / "AS ALWAYS" as two intentional lines, or "EPEE ALWAYS"), drop letter-spacing to ~0.2pt, or widen the flanks by trimming the logo from 62% to ~58%.

---

## V7 — `render.py` exits 0 even when the instrument FLAGs. A green run proves nothing.

Both instruments print `FLAG` and then the process ends normally (`finally: chrome.terminate()`, no `sys.exit`). A CI/print gate that can't fail is decoration — and per V2 the region instrument can't even FLAG.

**Fix:**

```python
flags = []
# … append to flags on each FLAG line instead of only printing …
if flags and "--allow-flag" not in sys.argv:
    print("FAIL:", "; ".join(flags), file=sys.stderr)
    sys.exit(1)
```

Also add a hard check for the §4 type floor (nothing below 7pt) by evaluating computed font-sizes in the same CDP session.

---

## V8 — Headings are below the locked §4 type scale.

Measured computed sizes vs the guide:

| Element | Template | §4 spec | |
|---|---|---|---|
| H1 (lead) | **16pt** | 17–19pt | under |
| H2 (shorts) | **10.5pt** | 11–12pt | under |
| Box title | **9.5pt** | 10pt | under |
| Body | 8.5pt | 8.5–9.3pt | ok |
| Byline / footer / th | 7pt | ≥7pt | ok (no headroom) |

Body, dek, byline and tables are within spec, but the three headline tiers each sit ~0.5–1pt under the locked range. §6 forbids "shrink below the type minimums to force a fit" — that is plausibly what happened in the v2 "small version". Either restore H1 17 / H2 11 / boxtitle 10 and recover the height elsewhere, or amend §4 on purpose.

---

## V9 — §10's table width variants don't exist.

§10 requires "`.w1` (1 col rail), `.w2`, `.w3`" on every board. Grepping `monday-v5.html` for `.w1/.w2/.w3` (and `column-rule` / CSS `columns:`) returns nothing. Boards are sized with ad-hoc inline `colgroup` widths instead (which is fine on its own — see §15 — but the locked class contract is unimplemented). Either build the classes into the template or delete §10 and say per-board `colgroup`s are the rule.

---

## V10 — §8 says box-free articles; five prose pieces are still boxed.

§8: "Articles flow WITHOUT bounding boxes… Borders are reserved for TABULAR data." But these prose blocks still carry a 1.5pt `.box` border: **Next Gazette — Thursday, New Faces, Fencing 101 — The Double Touch, Milestones, About This Paper.** (Tabular boxes — Ratings Earned, Scoreboard, Signup Board, Where to Watch, Deadlines, Club This Week, Club Results — are correct.) `.comicbox` additionally uses a *dashed* border.

Either §8 is superseded by §3's "rails/boxes take the third" and should be amended, or the prose boxes should lose their borders and use column rules. Right now the template and the locked guide disagree, and §8 is the later lock. Flagging for a decision, not guessing.

Related: `.comicbox` is a fixed `min-height: 1.6in`. When the real panel (a different aspect ratio) lands, the entire back-page rail reflows. Define the comic slot as an aspect-ratio box, not a min-height.

---

## V11 — Minor spec widths and gutters.

- **Scoreboard `Src` = 0.45in**, under §15's 0.5–0.8in meta-width band. (`Closes` 0.7, `When` 0.8, `Date` 0.65 are fine.)
- Ruled rows use `border-left` + `padding-left: 9pt` instead of `column-rule`. The *text* measures come out equal (2.323in each — I checked), so line lengths are fine, but the visual gutter between ruled columns is ~0.26in versus the 9pt (0.125in) the non-ruled rows get, so ruled and unruled rows don't share a horizontal rhythm.
- **Doc contradiction:** §2 (line 12) still says masthead "~80% width"; §12 (line 96) says "~62%". Both are "LOCKED". The template follows §12. Fix §2.

---

## 1. Other errors found (not visual)

**E1 — The date is the wrong weekday.** 2026-10-13 is a **Tuesday**, but the title, the right flank ("MONDAY EDITION"), and the dateline ("MONDAY RESULTS EDITION · OCTOBER 13, 2026") all say Monday. A Monday edition dated Oct 13 is internally false. Use **Oct 12** (Mon) or **Oct 19** (Mon). §7's checklist explicitly requires "dates/days consistent".

**E2 — Date-relative copy is stale for a Monday paper.** With the paper dated Oct 12/13, the front-page short "NAC Season Opens in Orlando This Week" and its "October NAC runs Oct. 9–12" are the *just-finished* weekend (Oct 9–12 = Fri–Mon), and "Where to Watch … Div I epee finals, Oct 11–12" lists an event that already happened. "New Passivity Rule **Starts** Oct 1" is also wrong tense by publication. Either move the date or rewrite the tense.

**E3 — Winter Camp dates can't contain a Friday.** "Winter Camp Returns Dec 27–31" — 2026-12-27 is a **Sunday**, so Dec 27–31 is Sun–Thu. The copy promises "a Friday team tournament". No Friday in range.

**E4 — The documented render entry point renders the wrong paper.** `prototype/render.sh` still defaults to `prototype/monday-v2.html` (comment and `SRC="${1:-prototype/monday-v2.html}"`). Running it with no args produces the old v2 prototype while the current template is v5. Point the default at the current template (or require the argument).

**E5 — An internal working label is printed on the paper.** The box title reads "Signup Board — Who's In **(Compact)**". "Compact" is a template variant note, not reader-facing.

**E6 — Placeholder drift.** Milestones says "this issue marks our second prototype… squinted at v1" while the issue is No. 005 and the artifact is v5. Sample-content sloppiness, but it undermines the "looks purpose-built" test.

**E7 — Two factual claims need a source before print.** (a) The passivity-rule box asserts "first call → red card (touch), second → black card (exclusion), yellow cards gone entirely." (b) Fencing 101 says a tied DE "goes to a one-minute priority round after a draw… you only need one light." The project's own rule is *facts never from model memory*, and both are rules-with-numbers. Also (b) is imprecise: in a priority round, a double touch also wins for the priority holder, so "only need one light" isn't the full condition. Verify both against the current FIE/USA Fencing text (SOURCES.md) or cut.

**E8 — PLAN.md doc drift persists.** The heading "**Thursday — Signup edition (front / back), no rehash**" still appears twice, at lines 82 and 92, with divergent bodies. (Carried over from the first review; still open.)

**E9 — Dead code.** `render.py` line 22: `HTML2PDF_JS = None  # (placeholder, unused)`.

---

## 2. Ranked fix list (cheapest-impact first)

1. **V1** — one CSS line: `table.board th.r { text-align: right; }`. Fixes six header/data pairs; §14 done.
2. **V2 + V7** — make the region instrument measure content depth, and make `render.py` exit non-zero on any FLAG. Without these, every other check is unfalsifiable.
3. **V4** — crop `masthead001.png` to its opaque bbox; page 1's top margin and ~0.4in of dead space both fall out.
4. **V3** — add ~110 words to the front-page lead (or one rail box) to close the 1.33in hole.
5. **V5** — widen the Where to Watch Event column.
6. **V6** — de-wrap the left flank.
7. **V8/V9/V10/V11** — reconcile the template with §4/§8/§10/§15 and fix the §2-vs-§12 contradiction.
8. **E1–E9** — date/weekday, stale dates, Winter Camp Friday, `render.sh` default, "(Compact)", sourcing, PLAN drift, dead code.

---

## 3. What's already good (keep it)

- Exactly 2 pages, Letter, zero browser chrome, `print-color-adjust: exact` — §1 holds.
- Footers are pinned with flex + `margin-top:auto` (§13); footer gaps 0.57in / 0.68in are honest numbers.
- Masthead artwork is 100% grayscale → genuinely B&W-safe (§2).
- Body/dek/tables/byline/footer sizes are all within the §4 scale and at or above the 7pt floor.
- `colgroup` + `table-layout: fixed` + `tabular-nums` are in place; no board overflows its box.
- Headline/dek/byline live inside the lead columns — §17 is satisfied.

---

## 4. Reproduce

```bash
cd ~/Dev/fencing-newspaper
python3 prototype/render.py prototype/monday-v5.html /tmp/gazette-v5-check.pdf   # instrument output
pdfinfo /tmp/gazette-v5-check.pdf | grep -E 'Pages|Page size'
pdftoppm -r 150 -png /tmp/gazette-v5-check.pdf /tmp/v5page                        # for the pixel checks
```

- **V1** — in the page: `getComputedStyle(th.r).textAlign` returns `left`; the data cell returns `right`. Text-Range x-extents in §V1 table above.
- **V2** — compare `[...r.children].map(c => c.getBoundingClientRect().height)` (all equal) with the content-depth map in §V2.
- **V4** — first ink row on the 150 dpi page-1 PNG is at 105px (= 0.70in), not 75px; `masthead001.png` opaque bbox is (45,96)–(2124,636).
- **E1** — `date -d 2026-10-13 +%A` → Tuesday.

---

## 5. Note for the next agent

This is a **review**, not a patch — the template and `render.py` are unchanged. The five highest-value edits (V1, V2, V7, V4, V5) are each a handful of lines. If you apply them, re-run §4 and confirm: header/data alignment matches on all six columns, the region instrument can now actually FLAG, a FLAG makes `render.py` exit non-zero, page 1's first ink is at 0.50in, and no board row exceeds ~3 lines.
