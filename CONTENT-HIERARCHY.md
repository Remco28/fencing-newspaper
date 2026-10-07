# Content Hierarchy — print priority for the weekly issue (FRANK SORTS THIS FILE)
How to use: **table order top-to-bottom = print priority** (not the old # column).
The bot fills from the TOP and cuts from the BOTTOM when space runs out.
Re-arrange freely; keep the budgets honest.
Budgets in words (articles) or rows (tables). Calibration: ~40 words/column-inch @8.5pt.
**Visual scale follows the slot (template CSS); words follow the Budget column** — see STYLE-GUIDE §4/§11. Writers do not invent size-by-importance weekly.

One weekly issue only (Thursday edition cancelled 2026-10-06). Default publish Monday;
may slip to Tuesday — see PLAN.md. Dateline uses the **actual publish day**.
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
| 9 | Deadlines box | 3–5 rows | AskFRED / newsletter | Entry closes + renewals |
| 10 | Comic | 1 panel | Frank via email | Sparingly |
| 11 | TV / streaming box | 3–5 rows | FIE calendar / FencingTV / YT | Major events + where to watch |

Killed (2026-10-06): Thursday signup edition entire; logistics box; Fencing 101; Milestones; About / corrections / archive placeholders.
Killed (2026-10-06 late — plan v3.4): **Scoreboard strip** — was meant for big headlines + one-line blurbs from various sources; hard to implement well. Can revive later as a "headline wire" if wanted; not in the live hierarchy now.

Photo desk (budget page, not a print slot): visible thumbnails + multi-select Include checkboxes → `photoIncludes` in approvals JSON. Not a hierarchy row.

## Rules for the sorter (Frank)
- Masthead, dateline, footer are template furniture: never cut, never grow. No separate About/archive slot.
- Tables shrink/grow by ROWS (width variant follows: few rows = rail, many = full).
- Articles shrink/grow by WORDS within their budget range, never below minimum.
  Lead = biggest type + 2-col; Secondary A = medium; Secondary B / NJ HS = smaller presence
  (locked in template — not a weekly dial).
- **Stretch (when short):** grow lead → grow Secondary A → add TV/streaming or club-events
  rows; if still short, FLAG TO FRANK (inches/words). Never stretch type/leading.
- **Cut (when long):** drop Secondary B first, then trim NJ HS / TV / comic, then trim
  Secondary A / lead toward minima. Never cut furniture; never shrink type or cheat margins.
- If everything above the line still doesn't fit, the bot flags the overage in inches —
  it never shrinks type or cheats margins to force it.
- OVERSUPPLY RULE: write to ~115% of page capacity, then cut bottom-up. Sections are
  size-flexible by design, so any hierarchy-compliant selection fits once oversupply exists.
