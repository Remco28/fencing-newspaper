# Content Hierarchy — print priority for the weekly issue (FRANK SORTS THIS FILE)
How to use: **table order top-to-bottom = print priority** (not the old # column).
The bot fills from the TOP and cuts from the BOTTOM when space runs out.
Re-arrange freely; keep the budgets honest.
Budgets in words (articles) or rows (tables). Calibration: ~40 words/column-inch @8.5pt.
**Visual scale follows the slot (template CSS); words follow the Budget column** — see STYLE-GUIDE §4/§11. Writers do not invent size-by-importance weekly.

One weekly newsletter (no Mon/Thu split). Target Mon or Tue; later OK — see PLAN.md.
Dateline uses the **actual publish day** (`<Weekday> Edition`).
Pipeline (Staging→Clean→Budget→Proof) and tip vetting live in **STAGING.md**; this file only owns slot order + budgets.

## WEEKLY — Results + signup (news-first)
| # | Slot | Budget | Source | Notes |
|---|------|--------|--------|-------|
| 1 | Lead story | 150–180w | FIE / USA Fencing / big NJ result | Weekend's biggest epee result |
| 2 | Club results box | 3–5 rows | Results-app email | Elite FC finishes, always in |
| 3 | Ratings earned | 2–5 rows | Results-app email | Celebration, always in |
| 4 | Secondary article A | 80–100w | National / regional | Beefier news, not just scores |
| 5 | Secondary article B | 80–100w | National / regional | Drop first if tight |
| 6 | NJ high-school roundup | 60–90w or 3–5 one-liners | NJ.com / NJSIAA | Whole-state epee |
| 7 | Signup board | 2–8 rows | Results-app email | **Core.** Encourage clubmates to enter. Max **4 tournaments**; prefer listing all Elite FC names on those events — if ~20 fencers enter one event, show fewer tournaments to make room. |
| 8 | Club events | 3–5 items | Newsletter email | From Frank's forwards |
| 9 | **Parent Q&A** | 40–70w (1 Q&A) | Frank chat (parent ask → desk) | Recurring category. Anonymous asker + no Frank byline unless they ask to be named. Layout: `.rail-block.qa`. **Default 1 per issue**; second only if space after cut hierarchy. |
| 10 | Deadlines box | 3–5 rows | AskFRED / newsletter | Entry closes + renewals |
| 11 | Comic | 1 panel | Frank via email | Sparingly |
| 12 | TV / streaming box | 3–5 rows | FIE calendar / FencingTV / YT | Major events + where to watch |

Killed (2026-10-06): Thursday signup edition entire; logistics box; Fencing 101; Milestones; About / corrections / archive placeholders.
Killed (2026-10-06 late — plan v3.4): **Scoreboard strip** — was meant for big headlines + one-line blurbs from various sources; hard to implement well. Can revive later as a "headline wire" if wanted; not in the live hierarchy now.

Photo desk (budget page, not a print slot): visible thumbnails + multi-select Include checkboxes → `photoIncludes` in approvals JSON. Not a hierarchy row.

Educational figures (e.g. exploded-weapon art): not a hierarchy row — optional **back-page / page-2 feature** when space and budget Include say so. Default **span 2 columns** (not 3, not full-bleed) unless Frank says otherwise. Prefer SVG; do not invent a standing Fencing-101 category.

**Page 1 vs page 2:** hierarchy order is **print priority** (fill top → cut bottom), **not** hard page assignment. Template A only requires two `.page` shells + furniture. Sample convention often puts news/boards on the front and club calendar/notes on the back; that is **compose judgment**, not a locked pin — Budget/Proof can move material either side so both pages fill.

## Rules for the sorter (Frank)
- **Parent Q&A** is a recurring content **category** (not a one-off): parent asks Frank → Frank briefs Gazette Desk → we print Q&A. Default anonymous; name only if they ask. No Frank byline. See STYLE-GUIDE §8a / `.qa`.
- Masthead, dateline, footer are template furniture: never cut, never grow. No separate About/archive slot.
- Tables shrink/grow by ROWS (width variant follows: few rows = rail, many = full).
- Articles shrink/grow by WORDS within their budget range, never below minimum.
  Lead = biggest type + 2-col; Secondary A = medium; Secondary B / NJ HS = smaller presence
  (locked in template — not a weekly dial).
- **Stretch (when short):** grow lead → grow Secondary A → add TV/streaming or club-events
  rows; if still short, FLAG TO FRANK (inches/words). Never stretch type/leading.
- **Cut (when long):** drop Secondary B first, then trim NJ HS / TV / comic (keep Parent Q&A if printed — drop second Q&A before first), then trim
  Secondary A / lead toward minima. Never cut furniture; never shrink type or cheat margins.
- If everything above the line still doesn't fit, the bot flags the overage in inches —
  it never shrinks type or cheats margins to force it.
- OVERSUPPLY RULE: write to ~115% of page capacity, then cut bottom-up. Sections are
  size-flexible by design, so any hierarchy-compliant selection fits once oversupply exists.
