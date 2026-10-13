# Content Hierarchy — print priority for the weekly issue (FRANK SORTS THIS FILE)
Reviewed and cleaned 2026-10-13 (plan v3.27) against PLAN, STYLE-GUIDE, STAGING, SOURCES and Issues No. 1–2 as built.

How to use: **table order top-to-bottom = print priority**. The `#` column is just a label (renumbered
v3.27; no more 9a/9b). The bot fills from the TOP and cuts from the BOTTOM when space runs out, except
where the **Cut (when long)** order below says otherwise for boxes.
Re-arrange freely; keep the budgets honest. Rows marked **(provisional)** have a position/size Frank
hasn't set yet — see "Open questions for Frank" at the bottom.

- Budgets in words (articles) or rows (tables). Calibration: ~40 words/column-inch @8.5pt.
- **Visual scale follows the slot (template CSS); words follow the Budget column** — STYLE-GUIDE §4/§11.
- One weekly issue (no Mon/Thu split). Target Mon or Tue; later OK — PLAN §3. Dateline uses the actual
  publish day (`<Weekday> Edition`).
- Pipeline (Staging → Clean → Budget → Proof) and vetting: **STAGING.md**. Sources and cadence:
  **SOURCES.md**. This file owns slot order + budgets only.
- **House rules that apply to every row:** invent nothing (STYLE-GUIDE §0b); no club "Epee" labels
  (§0c); results tone — strong finishes only, everyone else on an "also fenced" line (§0d); no
  bylines except real guest authors (PLAN §1b); no Reddit/X usernames; no minors' personal accounts.

### Source key (used in the table)
| Key | Meaning |
|-----|---------|
| **Email** | `efc.weekly@agentmail.to`: Frank's forwards, club Mailchimp newsletter, allowlisted club-schedule digest (registrations) |
| **FT** | FencingTracker — Elite FC club page + event pages (results, ratings earned, registrations); recurring since v3.24 |
| **AskFRED** | AskFRED API/site (gentle use) — local tournaments, events, entry closes |
| **Chat/call** | Frank directly (facts he gives are verified) |
| **Web** | FIE, USA Fencing, NJ.com / NJSIAA, club website |
| **X** | X leads (read-only, vetted accounts; leads only — facts confirmed elsewhere) |
| **Reddit** | r/Fencing threads, usually as PDFs Frank shares; opinion only, facts claim-checked |

## WEEKLY — recurring slots (news-first)
| # | Slot | Budget | Source | Notes |
|---|------|--------|--------|-------|
| 1 | Lead story | 150–180w | FT / Web / Email | Weekend's biggest epee result (club result if strong, else national/NJ). |
| 2 | Club results box | 3–5 rows + "also fenced" line | FT / Email / Chat | Elite FC finishes, always in. **Strong results only** (podium/top 8, notable climb, PB, unbeaten pool); everyone else on one **"Also fenced"** line (or "also attended") with no places — STYLE-GUIDE §0d. |
| 3 | Ratings earned | 2–5 rows | FT / Email | Celebration; always in **when any were earned** (none posted for No. 2). |
| 4 | Secondary article A | 80–100w | Web (USA Fencing / national) | Beefier news or explainer, not just scores. |
| 5 | Secondary article B | 80–100w | Web (FIE / national / regional) | Drop first if tight. |
| 6 | NJ high-school roundup | 60–90w or 3–5 one-liners | Web (NJ.com / NJSIAA) | Whole-state epee; in season. |
| 7 | **Overheard on Reddit** (provisional) | 130–170w | Reddit | Recurring since No. 1 (etiquette ran No. 2). Forum takes as attributed opinion, no usernames; checked facts as fact; optional one-line *Fact check:* line. Default 1 per issue (No. 2 ran 2). |
| 8 | Signup board — **Go Cheer** | 2–8 rows, max 4 tournaments | Email digest / FT registrations / AskFRED | **Core.** Elite FC entries only; prefer all names on fewer tournaments (if ~20 fencers enter one event, show fewer tournaments). Title "Go Cheer — Elite FC Entries" (no "(All Epee)"). |
| 9 | Club events | 3–5 items or one-line notes | Email (newsletter) / Chat | Camps (e.g. Winter Camp), special classes, class changes as **one-line notes** (e.g. footwork class) — see Weekly Classes rule in Cut order. |
| 10 | **Parent Q&A** | 40–70w (1 Q&A) | Chat (parent ask → Frank → Desk) | Answers a **real question a parent asked**. Anonymous; no Frank byline. `.rail-block.qa`. Default 1 per issue; second only if space after cuts. |
| 11 | **By the Book** (provisional) | ≈40–80w, 1 snippet (provisional) | Frank's USA Fencing rulebook + penalty-guide material | v3.25. One rule or penalty per issue; random by default, the relevant penalty when something happened that week. **Nothing until Frank shares his material.** |
| 12 | **For the Parents** (working name; provisional) | ≈40–80w, 1 item (provisional) | Web / Chat (sourced per item) | v3.26. Standing box for non-fencing parents: one practical, **proactive** topic (term decoded, tournament tip, what to expect). Unlike Parent Q&A, nobody asked. Start issue not set. |
| 13 | Deadlines box | 3–5 rows | AskFRED / Email | Entry closes + renewals. |
| 14 | Comic | 1 panel | Email (Frank; Ling may draw from No. 3 or later) | Sparingly. A guest artist gets a credit (guest-byline rule). |
| 15 | TV / streaming box | 3–5 rows | Web (FIE calendar / FencingTV) | "Epee on Screen": major events + where to watch; no start times/prices unless listed. |

## Standing elements outside the priority table
- **Educational figure / THE WEAPON (back-page figure):** optional page-2 feature when the budget includes
  it. Default **span 2 columns** (not 3, not full-bleed) unless Frank says otherwise; SVG preferred; short
  caption OK. Not a standing Fencing-101 category. Can absorb slack, but grows only within its span.
- **Weekly Classes table:** not a weekly slot. Runs only when the schedule changed or something special
  needs it; otherwise a one-line note in Club events (Cut order step 1). Left out of No. 2.
- **Photo desk** (budget page, not a print slot): thumbnails + multi-select → `photoIncludes`.
- **Page 1 vs page 2:** priority order, **not** page assignment. Compose judgment places material so both
  pages fill (No. 2 ran an Overheard on page 1 and the TV box on page 2).

## Planned one-off features (not recurring)
| Piece | Target | Status | Where |
|-------|--------|--------|-------|
| How to become a referee | No. 4 | Placeholder, no content (Frank picked No. 4, 2026-10-13) | `staging/weeks/after-next/` `chat-become-a-referee-placeholder-2026-10-13` |

(Recurring-section placeholders such as By the Book live in staging, not here.)

## Killed
- 2026-10-06: Thursday signup edition; logistics box; Fencing 101; Milestones; About / corrections / archive placeholders.
- 2026-10-06 late (v3.4): **Scoreboard strip** (big headlines + one-line blurbs) — hard to do well; could return as a "headline wire".

## Rules for the sorter (Frank)
- **Parent Q&A** is a recurring content **category** (not a one-off): parent asks Frank → Frank briefs Gazette Desk → we print Q&A. Default anonymous; name only if they ask. No Frank byline. See STYLE-GUIDE §8a / `.qa`.
- Masthead, dateline, footer are template furniture: never cut, never grow. No separate About/archive slot.
- Tables shrink/grow by ROWS (width variant follows: few rows = rail, many = full).
- Articles shrink/grow by WORDS within their budget range, never below minimum.
  Lead = biggest type + 2-col; Secondary A = medium; Secondary B / NJ HS = smaller presence
  (locked in template — not a weekly dial).
- **Stretch (when short):** grow lead → grow Secondary A → add TV/streaming or club-events
  rows → **Desk fill** (v3.20): Gazette Desk may fill remaining space with **Frank-vetted**
  staging items it picks (budget candidates / self-gather Frank already vetted). Desk fill is
  listed in `issue.json` `desk_fill` and in the proof message; **Frank can veto any Desk-fill
  piece at proof.** Never print unvetted items as fill. If still short, FLAG TO FRANK
  (inches/words). Never stretch type/leading.
- **Cut (when long) — content-heavy weeks (v3.20, Frank 2026-10-07): standing / utility boxes
  give way to stories.** Work this order before cutting any story:
  1. **Weekly Classes table** (the regular class schedule) — drop it. It runs only when
     something changed or there is a special class, and even then a **one-line note** in Club
     events (e.g. “Mini Musketeers now starts at 4:15 on Fridays.”) is preferred over the table.
  2. **Upcoming-tournament boards** (signup / Go Cheer) — shrink to the **nearest and most
     important** events and to **Elite FC entries only** (no open-call or “spots still open”
     rows). Fewer tournaments before fewer names; the board shrinks, it is not dropped (core).
  3. **Other standing utility boxes** — deadlines, TV/streaming, glance/explainer boxes,
     comic: trim rows, then drop.
  4. **Then stories:** Desk-fill and Secondary B first (a second Overheard counts as Desk-fill), then trim NJ HS, then trim Secondary A /
     lead toward minima. Keep Parent Q&A if printed — drop a second Q&A before the first.
  Club results + Ratings earned stay (always in; Ratings only when earned). This order overrides strict bottom-up table
  order for boxes. **Page 1 vs page 2 stays flexible** — cut order is priority, never a page
  assignment. Never cut furniture; never shrink type or cheat margins.
- **Two-page overflow from a late add (v3.20):** if adding an item (e.g. a Frank-confirmed
  board group at proof) would push the issue past 2 pages, **trim Desk-fill stories first**
  (reflow columns, then cut words from Desk fill), then follow the cut order above — **before**
  any thought of shrinking type (which stays banned). Note every trim in `issue.json`.
- If everything above the line still doesn't fit, the bot flags the overage in inches —
  it never shrinks type or cheats margins to force it.
- OVERSUPPLY RULE: write to ~115% of page capacity, then cut bottom-up. Sections are
  size-flexible by design, so any hierarchy-compliant selection fits once oversupply exists.

## Open questions for Frank (v3.27 review)
1. **Ranks:** where do Overheard on Reddit (#7), By the Book (#11) and For the Parents (#12) belong? Placed provisionally.
2. **Sizes:** confirm Overheard 130–170w (budget-page figure, never locked) and ≈40–80w for By the Book / For the Parents.
3. **Overheard frequency:** 1 per issue by default, with a second only as Desk fill (as in No. 2)?
4. **Dear Ref** (SECTIONS-MENU 19b, "maybe"): fold into By the Book, or keep as a separate idea?
5. **Corrections box:** SECTIONS-MENU marks it ✅, but "corrections placeholders" were killed 2026-10-06. Run a one-line correction only when needed, or never?
6. **Comic by Ling:** confirm the credit line and whether Ling sends via efc.weekly like Frank.
7. **Deadlines box** hasn't run in No. 1 or No. 2. Keep it, or fold entry closes into Go Cheer notes?
8. **For the Parents:** final name (still a working name).
