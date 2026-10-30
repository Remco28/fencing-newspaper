# En Garde Gazette — Visual Style Guide (LOCKED)
Authoritative for every issue, template, and prototype. Locked 2026-10-06 by Frank;
**reference sample (taste locked 2026-10-07, plan v3.14):** `issues/2026-10-14/` —
`paper-v3.14.pdf` / `paper.pdf`, `preview-p1.png`, `preview-p2.png`. Match that sheet’s
furniture (dateline, flanks, §8 boxes vs rails) unless Frank reopens a rule.
article size-by-importance + stretch hierarchy refreshed 2026-10-07 (plan v3.7);
masthead flanks = publisher + rotating quip ears (v3.8 → v3.14); dateline = centered
Playfair `<Weekday> Edition` (from actual publish day) / `Page Two` + meta (v3.12); photo fit no silent crop (v3.9);
Clark Kent composition §0 (v3.10); voice §0a (v3.11); §8 tabular-only `.box` +
`.rail-title` no underline (v3.12–v3.14); guests-only bylines; reality/provenance §0b (v3.16); **Parent Q&A** category + `.qa` pattern (v3.18); **epee assumed — no weapon labels in club context** §0c + captions name only Frank-confirmed people §19 + content-heavy cut order §11 (v3.20).
If a render violates any rule below, it does not print — fix and re-render.


## 0. Composition bar — Clark Kent (locked 2026-10-07, plan v3.10)

**Who:** Clark Kent (this bot, formerly Gazette Desk, and every future version) builds each issue after Frank
approves the budget. Frank owns editorial gates; you own composition and taste inside
locked Template A.

**Bar:** The sheet must feel tailor-made for Elite Fencers Club — pleasant, fun, carefully
put together — **not** approved content dumped into slots. Club kids and parents should
recognize themselves and their sport; the lead carries weight; shorts stay shorts; boards
are glanceable; something earns a smile; dense without feeling forced.

**Rails vs judgment:**
- Rails (do not invent weekly): page geometry, 3-col grid, per-slot type scale, word/row
  budgets, furniture (masthead / dateline / footer), pattern vocabulary, B&W rules, photo
  fit, fill/gap instruments.
- Judgment (required every issue): article order and pairing within pattern slots, pacing,
  flank quip choice and presentation, photo slotting, cut/stretch decisions per §11 and
  CONTENT-HIERARCHY, self-critique until the page feels designed.

**Done loop (mandatory):** render → look (and instruments) → self-critique against this
§0 + the checklist in §7 → fix → re-render. “Fits” without purpose is a fail.

**Cooperation:** Prefer rewriting unclear docs over improvising a private house style.
PLAN §1a is the narrative home for this role; this section is the visual/composition home.


## 0a. Voice (locked 2026-10-07, plan v3.11)

Write like a **newsletter with a hard page limit**: every word competes for space.
- Selective word choice; cut fat before you cut facts. Verbose only when the **lead** (or another
  budgeted long slot) has room — never inflate a short to “sound newspaper-y.”
- Default voice = **reporter**: clean, concrete, sourced. Opinion / guest pieces may differ;
  credit guests. Tone is **per article** (levity, serious, somber, etc.) — match the story,
  don’t apply one house mood to every slot.
- **No byline** unless a real guest wrote the piece. Never print “Gazette Staff,” “Club Desk,”
  or other fake house bylines. Frank has none. Guests get a real name.
- Full narrative home: PLAN §1b. Ban list and FK 8–10 rules still bind.


## 0b. Reality — invent nothing (locked 2026-10-07, plan v3.16)

Layout samples may use labeled fiction. **A real issue may not.**
- Do not invent names, results, ratings, dates, entries, or quotes about real people.
- Compose only from vetted, provenance-backed staging (and the approved budget). Every printed fact must be traceable in issue `sources.json`.
- Never treat sample / PRETEND / demo copy as club or competition fact.
- **Names (v3.35, Frank 2026-10-18):** print fencers' names as the official club or tournament page lists them (capitalization included, e.g. "SarroWaite"), unless Frank's chat or the roster house form says otherwise. No birth years, ever. See STAGING.md § Names + pending entries and roster/README.
- Full rule: PLAN §1c + §2 Sourcing rules; STAGING.md provenance fields.

## 0c. Epee is assumed — no weapon labels in club context (locked 2026-10-07, plan v3.20)

Elite FC is **epee-only**, so the word is redundant on anything about our club and fencers.
- **Never** label club material “Epee” / “(Epee)”: box titles (“Elite FC Entries (All Epee)”
  → “Elite FC Entries”), table headings (“Finish (Epee)” → “Finish”; “Events (Epee)” →
  “Events”), and event names for our fencers (“Y12 Women’s Epee” → “Y12 Women”; “Y10 Mixed
  Epee” → “Y10 Mixed”; abbreviations like “Y12 WE” → “Y12 Women”). Captions and boardnotes too.
- **Keep the word only when it is genuinely needed:** outside-world stories where other
  weapons exist (an FIE/NAC field size, “women’s epee gold” at a multi-weapon Games), proper
  names (“Hub City Fall Epee Open”, “Epee World Cup”), and contrasts such as rule explainers or
  the three-weapon high-school primer (“sabre, foil and epee”). If dropping it would leave the
  reader unsure which weapon, keep it.
- Foil or sabre are never added on our own; **Frank will say** if the club ever adds a weapon.
- QA: §7 proofread item checks this. Template labels / budget page / sample labels were
  cleaned in v3.20 — do not reintroduce them when copying a past issue (the approved
  2026-10-08 issue still carries “(All Epee)” and “Finish (Epee)”; drop them when reusing it).

## 0d. Results tone — strong finishes only (locked 2026-10-12, plan v3.23; inclusion bar 2026-10-26)

**Never print a weak finish or place.** Policy from Frank (chat 2026-10-12), permanent.
- **Inclusion bar by event level (Frank 2026-10-26; supersedes the vaguer podium/top-8/climb list):**
  a finish prints if it is **top 32 at a national** (FIE/international events count as national or higher),
  **top 16 at a regional**, or **top 8 at a local**. **Small fields** (under ~16 fencers): only top 8 or a medal counts.
- **Always print, at any level:** a medal (top 3), a qualification, or a rating earned.
- Everyone else is simply **not printed** — **no "also fenced" / "also attended" line**
  (Frank, 2026-10-20; supersedes the 2026-10-12 also-fenced line). Nobody embarrassed.
- **When unsure, leave it out.** Never print a place to fill a row.
- Master for Club Results rules: `sections.json` (`club-results.rules`).
- Applies to the club results box, captions, lead/secondary copy about our fencers, and boards.

## 1. Page
- US Letter, 1 sheet front + back = exactly 2 PDF pages. Never 1.5, never 3.
- Margins: 0.5in sides/top, 0.4in bottom. No more, no less.
- Chrome printing: ALWAYS `--print-to-pdf-no-header` (or equivalent). No browser date/URL/title
  headers or footers — they waste space and serve nothing. The paper's own dateline/footer carry that info.

## 2. Look: old-time newspaper
- Masthead logo (`masthead001.png`, cropped to opaque bbox) with §12 flanks. Nothing above it, ever.
- Dateline (below masthead): **centered edition word** in a display face + one meta line under it — not a three-span flex bar. Top rule **3pt double**, bottom rule **2pt solid**. Edition: **`<Weekday> Edition`** from the actual publish day (e.g. `Monday Edition`, `Tuesday Edition`) — or `Page Two` on the back — in **Playfair Display SC / Cinzel** ~12.5–14pt, tracked, uppercase. Meta line: serif small-caps (**Libre Caslon Text** / Times) ~8pt — `Vol. I — No. N · Chatham, N.J. · Month D, YYYY` (page 2: section topic · Vol/No). No SAMPLE / Pretend / middle badge. Vol/No and date live HERE — not in the flanks. Do **not** revert to Arial three-span.
- Headings: PLAIN TEXT ONLY. No icons, no emojis, no ★≡✎▶!♦§◉✉ kickers, no symbols in or
  before headlines and box titles. Reasons: old-time look; symbols render inconsistently in B&W.
- **Tabular** box titles (`.box > .boxtitle` only): small bold sans caps with a 1pt rule
  beneath. **Prose rail titles** use `.rail-title` — **no** underline (see §8). Hierarchy
  comes from size and rules, not decoration.
- Body: Times New Roman / Liberation Serif. Headlines: Arial Black / Arial bold. **Exception:** dateline edition word uses Playfair Display SC / Cinzel; dateline meta uses Libre Caslon Text (see §12).
- B&W only. 100% black headlines and rules (1–2.5pt). No gray text under 10pt.

## 3. Grid: 3 columns
- Body content flows in 3 columns (flex thirds or CSS columns). Rationale: reads like a newspaper,
  eyes scan shorter line lengths faster.
- Lead story may span 2 columns; rails/boxes take the third. Nearby Tournaments board (signup board; formerly "Go Cheer") and footer span full width.
- Educational figures (e.g. exploded-weapon): default **span 2 columns** (not 3 / not full-bleed) unless Frank says otherwise.
- Column gaps 9pt. Boxes: 1.5pt border, 3–4pt padding, 4pt bottom margin.

## 4. Type scale (v2 baseline — the "small" version; per-slot lock 2026-10-07)
- **Size-by-importance is template CSS, not weekly freehand.** Each CONTENT-HIERARCHY
  slot owns a fixed type scale + column span; the writer fills the word budget. Gazette
  Clark still composes pairing/pacing within those scales (§0) — do not invent a new type
  hierarchy each issue.
- Lead (slot 1): 2-column span; H1 ~17–19pt black, tight leading; body may run **+0.5pt**
  vs shorts; optional **one-line dek under the lead only** (no dek on shorts).
- Secondary A (slot 4): medium — H2 ~11–12pt, body 8.5–9.3pt, leading ~1.26.
- Secondary B + NJ HS (slots 5–6): smaller presence — same H2 tier or slightly tighter;
  shorter grafs within budget. Never enlarge shorts to match the lead.
- Box titles 10pt caps. Tables/boards 8.5pt. Footer 7pt sans caps. Dateline: edition ~12.5–14pt display; meta ~8pt serif small-caps (§2/§12).
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
- If content runs long, cut per §11 / CONTENT-HIERARCHY (never furniture,
  never shrink type) — never shrink below the type minimums to force a fit. If a late add
  would make 3 pages, reflow and trim **Clark fill** stories first (v3.20).

## 7. Mandatory visual QA (every render, no exceptions — human or bot)
Render to PDF, rasterize pages to PNG, and LOOK at them. Checklist:
- [ ] Reality / provenance (§0b / PLAN §1c): no invented facts about real people; every printed fact traceable; sample/pretend not treated as real?
- [ ] Exactly 2 pages for 1 sheet?
- [ ] Header/footer chrome absent?
- [ ] No icons/emojis/symbols in any heading?
- [ ] 3-column flow intact, no column widowed/orphaned?
- [ ] Both pages filled top-to-bottom (no dead zones > ~0.75in)?
- [ ] Every board table: columns aligned, numbers tabular, rules consistent?
- [ ] Masthead crisp; dateline = centered edition + meta (Playfair SC, not three-span Arial); footer complete; flanks have air from logo?
- [ ] B&W-safe: no washed gray text, no muddy fills?
- [ ] Proofread: names spelled right, dates/days consistent, no foil/saber leaks? No
      “Epee”/“(Epee)” labels on club boxes, headings, captions or our fencers’ events (§0c)?
- [ ] Captions (§19): only Frank-confirmed names; no left/right order unless verifiable;
      others = “other medalists”/similar?
- [ ] Composition bar (§0): tailor-made for Elite FC — not slot-dump; hierarchy alive;
      flanks/dateline designed; page 2 not equal tiles?
- [ ] Voice (§0a): newsletter-tight; reporter unless guest/opinion; tone fits each piece;
      no fake Gazette Staff bylines (guests only)?
- [ ] §8: prose never in `.box`; `.rail-title` has no underline; no `<hr>` between page-2
      article bands (Read preview-p2.png — confirm)?
- [ ] Parent Q&A (§8a): if present, `.rail-block.qa` (no border); anonymous unless named;
      no Frank byline; 40–70w; usually one?
Any NO = fix, re-render, re-check. Fitting on the page is necessary but NOT sufficient —
it must look purpose-built for this club. **A proof is not “done” (and no “proof ready”
doorbell goes out) until Clark has opened and inspected every page PNG** of the current render
(v3.20 — reaffirmed from the first real run).
Board-level QA must be done on zoomed crops (150dpi+) of each table, not full-page
thumbnails — alignment cannot be judged through frosted glass.

## 8. Box-free articles; borders only on tables (locked 2026-10-06; **tightened 2026-10-07**)
- ARTICLE text flows WITHOUT bounding boxes: headline, optional dek, justified text, nothing else.
- **Borders (`class="box"`) ONLY on tabular utility** — ratings, scoreboard, signup board,
  club calendar table, Where-to-Watch table, and any other board. If it is primarily a
  `<table class="board">`, it may sit in `.box`.
- **Prose furniture is NOT a box.** Tips, About blurbs, Next-week asks, one-sentence
  explainers, Cheer Tips, Fencing 101-style copy — even when they live in a rail — use
  `.rail-block` (or bare flow): **`.rail-title`** + paragraphs, **no outer border** and
  **no title underline**. Putting article-shaped copy inside `.box` is the recurring defect
  Frank flagged across versions. Title underlines (`border-bottom` on `.boxtitle`) belong
  **only** inside `.box` tabular utilities — never on rail prose. Stacked `.rail-block`s
  separate by margin only; never insert `<hr>` or a fake rule between them.
- Do **not** treat “utility” as a license to draw a rectangle around prose. Killed sections
  (About / Fencing 101 / Milestones / Next Gazette placeholders) stay killed in live weeks;
  samples must still follow the no-prose-border rule.
- Columns are separated by `column-rule` (1pt vertical rule) — the classic newspaper divider.
- Lead headline lives inside the lead columns per §17 (never full-bleed over a rail).
- Comic slot: dashed/aspect-ratio frame when real panels land (that frame is the comic, not
  an article); placeholder min-height is prototype-only.

## 8a. Parent Q&A — `.qa` pattern (locked 2026-10-07, plan v3.18)

Recurring **content category** (CONTENT-HIERARCHY slot **Parent Q&A**). Not a boxed board.

- **Markup:** `<div class="rail-block qa">` + `<div class="rail-title">Parent Q&A</div>` +
  `<p class="q">…</p>` + `<p class="a">…</p>`. **No** `.box` border, **no** title underline,
  **no** `<hr>` under the block (same prose-rail rules as §8).
- **Type:** `.q` = bold italic body (question). `.a` = justified body (answer). Optional
  `Q.` / `A.` labels via CSS `::before` (small sans bold) or plain text — keep quiet.
- **Identity:** default **anonymous asker**; **no Frank byline**. Name someone only when
  they asked to be named. Guests elsewhere still follow §0a.
- **Budget:** 40–70 words for the pair. **Default one** Q&A per issue; a second only if
  space remains after the cut hierarchy.
- **Voice:** clear parent-facing reporter answer; tone per the question (PLAN §1b). No
  invented rules or points — cite/staging provenance required (§0b).
- **Prototype:** `prototype/qa-block.html`.

## 9. Layout patterns — select, never invent (locked 2026-10-06; OPEN 2026-10-07)
- **Today (V1):** ship **Template A only**. Match the locked sample `issues/2026-10-14`
  (v3.14). Varied article spans/heights inside that shell are composition (PLAN §1a), not a
  new template — still no freehand box placement.
- The long-term idea: a small pre-defined pattern vocabulary (e.g. FRONT-A: lead + rail;
  FRONT-B: 3 equal shorts; BACK-A: 3 rails). The agent SELECTS a pattern per issue based on
  content shape — it never hand-places boxes or invents arrangements per issue.
- A new pattern is created only as a design task with a test render; once good, it is LOCKED
  and added to the set. Patterns are vocabulary, not improvisation.
- **OPEN (Frank deciding — PLAN §4):** keep **2–3 locked full templates** and rotate weeks,
  vs **one Template A shell + constrained pattern selection** so the page feels more dynamic
  each time (real-newspaper energy) without unconstrained chaos. Another agent warned that
  open-ended dynamism gets messy. Until Frank picks: do not add Template B/C and do not
  invent layouts. Document the decision here when it lands.

## 10. Flexible table widths (locked 2026-10-06)
- Every board supports width variants: `.w1` (1 col rail), `.w2` (2 cols), `.w3` (full width).
- Width is chosen by CONTENT volume (few rows = rail, many rows = full width), never forced.
  A 3-row signup board is a rail; a 10-row board earns full width.
- Fixed table layout, declared column widths, tabular numerals, right-aligned dates/ratings —
  alignment is template property, not per-issue tweaking.

## 10a. Nearby Tournaments — one block per tournament (locked 2026-10-18, Frank)

- Each tournament is ONE block: `.tourney` → `.tourney-head` = **NAME** · town · dates (once), then a
  single `table.board`. Days are sub-rows inside it (`tr.day`, e.g. `SATURDAY, OCT. 24`, or
  `NO. 5 · SUNDAY, NOV. 8` for a numbered series), in chronological order. Never split one tournament's
  days across columns or repeat its heading per day (readers took Sat/Sun halves as two events).
- Columns: `Time · Event · Elite FC` when times are sourced (check-in close per USA Fencing),
  otherwise `Event · Elite FC`. No guessed times.
- Arrangement inside the full-width box: blocks flow top-to-bottom in `.board-split` halves; the
  biggest tournament takes the left half (or the full width if it is tall enough), smaller
  ones stack in the right half in date order. Venue/count note (`.boxnote`) stays under the board.
- CSS: `prototype/template-a-v2.css` (append to Template A). Helper: `tourney()` in the issue composer
  (`issues/2026-10-19/build/compose.py`).

## 11. Word budgets — measure once, write to fit (locked 2026-10-06; stretch refresh 2026-10-07)
- Each pattern slot carries a WORD BUDGET calibrated once per template. Current calibration
  (8.5pt, ~2.4in columns): ~40 words per column-inch. Recalibrate if type or columns change.
- The writer receives exact budgets per slot (see CONTENT-HIERARCHY.md) — **no weekly
  guessing.** Visual scale (type + column span) follows the slot's CSS (§4); words follow
  the Budget column. Template enforces importance; writer fills the range.
- **Stretch hierarchy (when short):** (1) grow lead toward the top of its 150–180w range;
  (2) grow Secondary A toward top of 80–100w; (3) add TV/streaming rows or club-events
  items; (4) **Clark fill** with Frank-vetted items (Frank may veto at proof — v3.20). If
  still short after that → **FLAG TO FRANK** with what and how much is missing
  (inches/words). Never stretch type or leading to fake fullness.
- **Cut hierarchy (when long) — v3.20 content-heavy order (canonical: CONTENT-HIERARCHY):**
  standing / utility boxes give way to stories. (1) drop the regular Weekly Classes table
  (changed/special class → one-line note instead); (2) shrink tournament boards to the
  nearest / most important events and Elite FC entries only; (3) trim then drop other
  utility boxes (deadlines, TV, glance, comic); (4) then stories — Clark fill / Secondary B
  first, then NJ HS, then Secondary A / lead toward minima. Never cut furniture (masthead,
  dateline, footer), club results, ratings, or the signup board entirely (it shrinks).
  Page 1 vs page 2 placement stays flexible. Never shrink type or cheat margins.
  Oversupply ~115% then cut is mandatory (§16).
- Killed fillers (do not stretch with these): Fencing 101, Milestones, scoreboard strip.

## 12. Masthead flanks + dateline (locked 2026-10-07; dateline v3.12; flanks v3.14)
- Logo ~58–62% width, centered in `.masthead` (retune if quotes wrap badly).
  Nothing above the masthead row, ever.
- **Flanks (beside the logo) — prose quotes, not Vol/No/date:**
  - LEFT (fixed): `Published by a fencing parent and his bot.` (from No. 3; Nos. 1–2 printed "with a bot"). One-line config: `flank-quotes.json` → `left_flank_fixed`; Frank may reword "his bot".
  - RIGHT (default from No. 2, v3.32): `It is better to deserve a rating than to have one.`
    (`flank-quotes.json` → `right_flank_default`). No. 1 printed "Know yourself, know your
    enemy, know where you left your glove." Other quips in `right_flank_quips` only if Frank
    picks one for an issue. Wrap is OK (two lines at Template A widths).
- **Flank presentation (v3.13 ears; v3.14 gap):**
  Serif face (**Libre Caslon Text** / Times), **not** bold Arial side-rules.
  Each ear: thin **0.75pt** top + bottom hairlines (no chunky 2pt side borders).
  Text centered in its ear. Left: **small-caps**, ~6.5pt, light tracking.
  Right: **italic**, ~6.8pt, sentence case. Never widen the logo to fill whitespace.
  Do **not** revert to Arial + 2pt side rules.
  **Clear air from the masthead logo:** logo ~**50%** width with **`margin: 0 10pt`**
  on the img (PNG flourishes run to the image edges — CSS flex gap alone is not enough),
  `.masthead` gap ~**18pt**, flank padding ≥ **5pt 7pt**. Closest hairline-to-art air
  should read ~**28–32pt** (≥ ~0.4in). Hairlines must **not** kiss the nameplate.
  Retune margin/gap before shrinking type.
- **Dateline** (v3.12 — replaces three-span Arial bar): centered stack, not flex spans.
  - Top: **3pt double** rule; bottom: **2pt solid** rule.
  - `.edition`: **`<Weekday> Edition`** from actual publish day (page 1) or **`Page Two`** (page 2) — Playfair Display SC
    / Cinzel, ~12.5–14pt, tracked uppercase.
  - `.meta` under it: Libre Caslon Text / Times, ~8pt small-caps —
    `Vol. I — No. N · Chatham, N.J. · Month D, YYYY` (page 2: `Club Calendar & Notes · Vol/No`).
  - No SAMPLE / Pretend / middle badge. Do **not** revert to three-span `space-between` Arial.
- Price / "Epee Only, As Always" flank lines: killed (v3.8).
- **Page 2 article bands + rail furniture:** no `<hr class="rule">` between article rows
  or between stacked rail-blocks. No `.boxtitle` underline on prose rails — use
  `.rail-title` (borderless). Column rules (`.cols3.ruled`) and utility `.box` borders
  (with `.box > .boxtitle` underline) stay. Page 1 may still use rules between major
  bands when they help. **Visual QA:** after render, Read preview-p2.png and confirm
  About / Cheer Tip / Youth Points / Next Week titles have **no** horizontal line under
  the heading.

## 13. Footer pinning + gap instrument (locked 2026-10-06; copy lock 2026-10-07)
- `.page` is a flex column with min-height 10.1in (Letter minus our @page margins);
  footer uses margin-top:auto so it always sits at the page bottom. Shortfalls appear as
  honest daylight ABOVE the footer, never hidden below it.
- **Footer copy:** issue number + for-fun disclaimer only (e.g. tips path / "just for fun").
  No "printed at the club" language; no print-timestamp line. Dateline already carries
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
- The lead headline and dek live INSIDE the lead columns — never full-bleed above
  a rail. Full-width headlines visually collide with top-right rail boxes.
  Byline only if a real guest wrote it (see §0a); omit otherwise.
- The rail rises to the very top beside the dek. Rebalance lead word budget against rail
  height whenever this arrangement changes (see §11 budgets).

## 18. Region balance (locked 2026-10-06)
- Page-level fill is necessary but not sufficient: columns WITHIN a row must end within
  ~0.5in of each other. A two-column-wide hole under a short lead next to a tall rail is
  a defect even when the footer reaches the bottom.
- `render.py` reports per-row column-bottom spread alongside the footer gap. Fixes in order:
  retune the short column's word budget, then pull-quote, then restructure — never leave
  a region void larger than 0.5in.

## 19. Photos — fit, no silent crop (locked 2026-10-07, plan v3.9)
- Default CSS: `width: 100%; height: auto;` — preserve the original aspect ratio. **Never**
  use `object-fit: cover` or a hard `max-height` that silently crops the frame.
- Grayscale filter (`filter: grayscale(100%)`) may stay for B&W print.
- Soft ceiling: if a photo would print taller than **~2.2in** in its column, FLAG to Frank
  (crop on the photo desk, pick a smaller slot, or swap the image). Do not auto-crop in CSS.
  Measure **as displayed** (honor EXIF orientation) — a 640×480 file with orientation=6
  renders as portrait and can exceed the ceiling even when the file header looks landscape.
  Sample note (2026-10-14): `club-newsletter-photo-1.jpeg` FLAGS at ~3.1in in a 1-col;
  issue used landscape `club-newsletter-photo-2.jpeg` (~1.8in) instead.
- Caption under the image (sans ~7pt). Photo desk still chooses which frames run; layout
  only scales to column width.
- **Caption naming (v3.20, first real run):** name **only people Frank has confirmed** (chat /
  vetted source). No left/right order unless Clark can actually tell who is who from the
  image. People from other clubs are “other medalists” (or similar) — never imply they are
  Elite FC. Don’t call a placing “podium” unless the photo shows one; tie the caption to
  results already printed. Look at the image before writing.

## PDF filename & download (locked 2026-10-15)

Each published issue has **one** canonical PDF, uniquely named:

`en-garde-gazette-no-<N>-<YYYY-MM-DD>.pdf`

Examples: `en-garde-gazette-no-1-2026-10-08.pdf`, `en-garde-gazette-no-2-2026-10-13.pdf`.

- Lives in `issues/<date>/` (and the site/docs copies). Do **not** use a bare `paper.pdf` for published issues.
- Render with: `python3 prototype/render.py issues/<date>/issue.html issues/<date>/en-garde-gazette-no-<N>-<date>.pdf`
- Site `issues.json` `pdf` field and the Download button must point at that filename so browsers save the unique name.
- PDF Author field (when set): **Nico's Dad** (Frank's joke byline).

## Archive whisper on the printed page (locked 2026-10-15; restyled 2026-10-18)

Every page footer is a trio on the 2.5pt rule — left `En Garde Gazette · Issue No. N`, centre
`Past issues · newsletter.teamremco.org`, right the for-fun disclaimer — all in the **same footer
type** (7pt sans caps, same tracking and colour). CSS class `.foot-archive` now inherits the footer
style (`prototype/template-a-v2.css`); it must not get its own size, weight, case or colour (Frank
2026-10-18: the smaller muted line looked shoehorned). Do not enlarge or promote it.

