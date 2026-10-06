# En Garde Gazette — Visual Style Guide (LOCKED)
Authoritative for every issue, template, and prototype. Locked 2026-10-06 by Frank.
If a render violates any rule below, it does not print — fix and re-render.

## 1. Page
- US Letter, 1 sheet front + back = exactly 2 PDF pages. Never 1.5, never 3.
- Margins: 0.5in sides/top, 0.4in bottom. No more, no less.
- Chrome printing: ALWAYS `--print-to-pdf-no-header` (or equivalent). No browser date/URL/title
  headers or footers — they waste space and serve nothing. The paper's own dateline/footer carry that info.

## 2. Look: old-time newspaper
- Masthead logo (`masthead001.png`) at ~80% width, centered. Nothing above it, ever.
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

## 4. Type scale (v2 baseline — the "small" version)
- Body 8.5–9.3pt, leading ~1.26. Front-page lead may run 0.5pt larger than the shorts; never larger.
- H1 (lead) ~17–19pt black, tight leading. H2 (shorts) ~11–12pt. Box titles 10pt caps.
- Tables/boards 8.5pt. Footer/dateline 7–8.5pt sans caps. Nothing below 7pt, ever.

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
- If content runs long, cut words (shorts first, scoreboard lines second) — never shrink below
  the type minimums to force a fit.

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
