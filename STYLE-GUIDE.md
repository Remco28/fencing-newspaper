# En Garde Gazette — Visual Style Guide (LOCKED)
Authoritative for every issue, template, and prototype. Locked 2026-10-06 by Frank;
article size-by-importance + stretch hierarchy refreshed 2026-10-07 (plan v3.7).
If a render violates any rule below, it does not print — fix and re-render.

## 1. Page
- US Letter, 1 sheet front + back = exactly 2 PDF pages. Never 1.5, never 3.
- Margins: 0.5in sides/top, 0.4in bottom. No more, no less.
- Chrome printing: ALWAYS `--print-to-pdf-no-header` (or equivalent). No browser date/URL/title
  headers or footers — they waste space and serve nothing. The paper's own dateline/footer carry that info.

## 2. Look: old-time newspaper
- Masthead logo (`masthead001.png`, cropped to opaque bbox) with §12 flanks. Nothing above it, ever.
- Dateline bar: 2.5pt rules top and bottom, bold sans caps, date · edition · issue no.
- Headings: PLAIN TEXT ONLY. No icons, no emojis, no ★≡✎▶!♦§◉✉ kickers, no symbols in or
  before headlines and box titles. Reasons: old-time look; symbols render inconsistently in B&W.
- Box titles: small bold sans caps with a 1pt rule beneath. Hierarchy comes from size and rules,
  not decoration.
- Body: Times New Roman / Liberation Serif. Headlines: Arial Black / Arial bold. Nothing else.
- B&W only. 100% black headlines and rules (1–2.5pt). No gray text under 10pt.

## 3. Grid: 3 columns
- Body content flows in 3 columns (flex thirds or CSS columns). Rationale: reads like a newspaper,
  eyes scan shorter line lengths faster.
- Lead story may span 2 columns; rails/boxes take the third. Signup board and footer span full width.
- Column gaps 9pt. Boxes: 1.5pt border, 3–4pt padding, 4pt bottom margin.

## 4. Type scale (v2 baseline — the "small" version; per-slot lock 2026-10-07)
- **Size-by-importance is template CSS, not weekly judgment.** Each CONTENT-HIERARCHY
  slot owns a fixed type scale + column span; the writer only fills the word budget.
  Do not invent a new hierarchy each issue.
- Lead (slot 1): 2-column span; H1 ~17–19pt black, tight leading; body may run **+0.5pt**
  vs shorts; optional **one-line dek under the lead only** (no dek on shorts).
- Secondary A (slot 4): medium — H2 ~11–12pt, body 8.5–9.3pt, leading ~1.26.
- Secondary B + NJ HS (slots 5–6): smaller presence — same H2 tier or slightly tighter;
  shorter grafs within budget. Never enlarge shorts to match the lead.
- Box titles 10pt caps. Tables/boards 8.5pt. Footer/dateline 7–8.5pt sans caps.
  Nothing below 7pt, ever.

## 5. Alignment (be anal — this is what looks professional)
- Boards (ratings, scoreboard, signups) are TABLES with fixed layout, never loose lists:
  - columns line up vertically across every row; dates/ratings right-aligned or in their own column;
  - `font-variant-numeric: tabular-nums` anywhere numbers stack;
  - consistent cell padding; row rules 0.5pt, header rule 1.5pt.
- Names in Ratings Earned align in a column — never ragged free text.
- Hanging indents for multi-line scoreboard items so wrapped lines align under the text, not the label.
- Baselines across adjacent columns should end within a line of each other; no orphaned headers
  stranded at a column bottom.

## 6. Fill rule
- EVERY page must be filled entirely, top footer to bottom footer. A half-empty page looks broken.
- If content runs short, the bot must TELL FRANK what and how much is missing ("back page needs
  ~150 words or one box") so he can fill the blanks — never stretch type, never widen leading,
  never ship white space to fake fullness.
- If content runs long, cut bottom-up per §11 / CONTENT-HIERARCHY (never furniture,
  never shrink type) — never shrink below the type minimums to force a fit.

## 7. Mandatory visual QA (every render, no exceptions — human or bot)
Render to PDF, rasterize pages to PNG, and LOOK at them. Checklist:
- [ ] Exactly 2 pages for 1 sheet?
- [ ] Header/footer chrome absent?
- [ ] No icons/emojis/symbols in any heading?
- [ ] 3-column flow intact, no column widowed/orphaned?
- [ ] Both pages filled top-to-bottom (no dead zones > ~0.75in)?
- [ ] Every board table: columns aligned, numbers tabular, rules consistent?
- [ ] Masthead crisp, dateline on one line, footer complete?
- [ ] B&W-safe: no washed gray text, no muddy fills?
- [ ] Proofread: names spelled right, dates/days consistent, no foil/saber leaks?
Any NO = fix, re-render, re-check. Fitting on the page is necessary but NOT sufficient —
it must look purpose-built.
Board-level QA must be done on zoomed crops (150dpi+) of each table, not full-page
thumbnails — alignment cannot be judged through frosted glass.

## 8. Box-free articles; bordered utility boxes (locked 2026-10-06, clarified 2026-10-07)
- ARTICLE text flows WITHOUT bounding boxes: headline, optional dek, justified text, nothing else.
- UTILITY boxes (Milestones, New Faces, About, Fencing 101, Next Gazette, comic slot) MAY carry
  borders — they are furniture, not articles. Borders on tabular-data boxes always.
- Columns are separated by `column-rule` (1pt vertical rule) — the classic newspaper divider.
- Lead headline lives inside the lead columns per §17 (never full-bleed over a rail).
- Comic slot: define as an aspect-ratio box when real panels land (fixed min-height reflows
  the rail on swap); placeholder min-height is prototype-only.

## 9. Layout patterns — select, never invent (locked 2026-10-06)
- The template offers a small pre-defined set of layout patterns (e.g. FRONT-A: lead + rail;
  FRONT-B: 3 equal shorts; BACK-A: 3 rails). The agent SELECTS a pattern per issue based on
  content shape — it never hand-places boxes or invents arrangements per issue.
- A new pattern is created only as a design task with a test render; once good, it is LOCKED
  and added to the set. Patterns are vocabulary, not improvisation.

## 10. Flexible table widths (locked 2026-10-06)
- Every board supports width variants: `.w1` (1 col rail), `.w2` (2 cols), `.w3` (full width).
- Width is chosen by CONTENT volume (few rows = rail, many rows = full width), never forced.
  A 3-row signup board is a rail; a 10-row Thursday board earns full width.
- Fixed table layout, declared column widths, tabular numerals, right-aligned dates/ratings —
  alignment is template property, not per-issue tweaking.

## 11. Word budgets — measure once, write to fit (locked 2026-10-06; stretch refresh 2026-10-07)
- Each pattern slot carries a WORD BUDGET calibrated once per template. Current calibration
  (8.5pt, ~2.4in columns): ~40 words per column-inch. Recalibrate if type or columns change.
- The writer receives exact budgets per slot (see CONTENT-HIERARCHY.md) — **no weekly
  guessing.** Visual scale (type + column span) follows the slot's CSS (§4); words follow
  the Budget column. Template enforces importance; writer fills the range.
- **Stretch hierarchy (when short):** (1) grow lead toward the top of its 150–180w range;
  (2) grow Secondary A toward top of 80–100w; (3) add TV/streaming rows or club-events
  items. If still short after that → **FLAG TO FRANK** with what and how much is missing
  (inches/words). Never stretch type or leading to fake fullness.
- **Cut hierarchy (when long):** drop Secondary B first, then trim NJ HS / TV / comic;
  then trim Secondary A / lead toward their minima. Never cut furniture (masthead,
  dateline, footer, club results, ratings, signup board when core). Never shrink type
  or cheat margins. Oversupply ~115% then cut is mandatory (§16).
- Killed fillers (do not stretch with these): Fencing 101, Milestones, scoreboard strip.

## 12. Masthead flanks (locked 2026-10-06)
- Logo at ~62% width, centered, flanked by two info blocks: LEFT "Vol. I — No. N /
  Chatham, N.J. / Epee Only, As Always", RIGHT edition day / full date / "Price: One Touch".
- Flanks: 7.5pt bold sans caps, 2pt side rules (left block left-ruled, right block right-ruled).
  This is the classic-paper answer to side whitespace — never widen the logo to fill it.

## 13. Footer pinning + gap instrument (locked 2026-10-06; copy lock 2026-10-07)
- `.page` is a flex column with min-height 10.1in (Letter minus our @page margins);
  footer uses margin-top:auto so it always sits at the page bottom. Shortfalls appear as
  honest daylight ABOVE the footer, never hidden below it.
- **Footer copy:** issue number + for-fun disclaimer only (e.g. tips path / "just for fun").
  No "printed at the club" language; no print-timestamp line. Masthead flanks already carry
  Vol/No and date — do not restate a full dateline in the footer.
- `render.py` measures the gap above each footer via CDP element boxes and reports inches:
  FLAG above 0.75in. Thumbnails are for taste; NUMBERS are for fill. Eyeballing fill is banned.
- The instrument (not the eye) decides whether a page passes; the eye decides whether it is beautiful.

## 14. Header/data alignment (locked 2026-10-06)
- Numeric and date columns right-align BOTH the header and the data (`.r` on th and td).
  A left-aligned DATE header over right-aligned dates reads as broken even when rows align.
- Audit every header/data pair on every render — one template rule, all boards fixed.

## 15. Meta columns get fixed narrow widths (locked 2026-10-06)
- Right-aligned dates/ratings must sit SNUG against their row content, not float at the far
  edge of a wide equal column. Every board declares a `<colgroup>`: meta columns
  (dates, ratings, SRC) get fixed narrow widths (0.5–0.8in), content columns take the rest.
- Equal-width columns are banned on boards. A date hugging the right edge of a 2-inch
  column, detached from its row, is the exact defect this rule exists to kill.

## 16. Oversupply, then cut (locked 2026-10-06)
- The writer ALWAYS generates ~115% of page capacity. Cutting is a designed step, not a failure.
- Cut strictly bottom-up per CONTENT-HIERARCHY.md order (lowest priority goes first).
  Never cut furniture, never shrink type, never cheat margins. The refinement to the
  standing rule: oversupply is mandatory, and 115% (not 200%) keeps cuts cheap and fast.
- Sections are built size-flexible (rows/words grow and shrink) so any hierarchy-compliant
  selection fits — provided the oversupply exists. No oversupply, no fit guarantee.

## 17. Headline scoping (locked 2026-10-06)
- The lead headline, dek, and byline live INSIDE the lead columns — never full-bleed above
  a rail. Full-width headlines visually collide with top-right rail boxes.
- The rail rises to the very top beside the dek. Rebalance lead word budget against rail
  height whenever this arrangement changes (see §11 budgets).

## 18. Region balance (locked 2026-10-06)
- Page-level fill is necessary but not sufficient: columns WITHIN a row must end within
  ~0.5in of each other. A two-column-wide hole under a short lead next to a tall rail is
  a defect even when the footer reaches the bottom.
- `render.py` reports per-row column-bottom spread alongside the footer gap. Fixes in order:
  retune the short column's word budget, then pull-quote, then restructure — never leave
  a region void larger than 0.5in.
