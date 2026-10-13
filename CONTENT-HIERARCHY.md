# Content Hierarchy — print priority for the weekly issue (FRANK SORTS THIS FILE)
Reviewed and cleaned 2026-10-13 (plan v3.27); Frank's answers applied v3.28 (chat: Frank 2026-10-13 11:27 ET) against PLAN, STYLE-GUIDE, STAGING, SOURCES and Issues No. 1–2 as built.

How to use: **table order top-to-bottom = print priority**. The `#` column is just a label (renumbered
v3.27; no more 9a/9b). The bot fills from the TOP and cuts from the BOTTOM when space runs out, except
where the **Cut (when long)** order below says otherwise for boxes.
Re-arrange freely. Rows marked **(provisional)** have a position/size Frank
hasn't set yet — see "Open questions for Frank" at the bottom.

- **No fixed lengths (v3.28, chat: Frank 2026-10-13):** a section runs as long as its content is good. The "Rough guide" column is a starting estimate for budgeting only, never a target or a minimum. Calibration: ~40 words/column-inch @8.5pt.
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
| # | Slot | Rough guide | Source | Notes |
|---|------|--------|--------|-------|
| 1 | Lead story | ~150–180w | FT / Web / Email | Weekend's biggest epee result (club result if strong, else national/NJ). |
| 2 | Club results box | ~3–5 rows + "also fenced" line | FT / Email / Chat | Elite FC finishes, always in. **Strong results only** (podium/top 8, notable climb, PB, unbeaten pool); everyone else on one **"Also fenced"** line (or "also attended") with no places — STYLE-GUIDE §0d. |
| 3 | Ratings earned | ~2–5 rows | FT / Email | Celebration; always in **when any were earned** (none posted for No. 2). |
| 4 | Secondary article A | ~80–100w | Web (USA Fencing / national) | Beefier news or explainer, not just scores. |
| 5 | Secondary article B | ~80–100w | Web (FIE / national / regional) | Drop first if tight. |
| 6 | NJ high-school roundup | ~60–90w or 3–5 one-liners | Web (NJ.com / NJSIAA) | Whole-state epee; in season. |
| 7 | **Overheard on Reddit** (provisional rank) | ~130–170w | Reddit | Recurring since No. 1 (etiquette ran No. 2). Forum takes as attributed opinion, no usernames; checked facts as fact; optional one-line *Fact check:* line. **Best at one per issue, but don't force it:** most of Reddit is junk, so skip it when nothing good turned up (v3.28, chat: Frank 2026-10-13). |
| 8 | Local tournaments board (**renaming** — formerly "Go Cheer"; Frank to pick: "Close to Home" / "Nearby Tournaments" / "Local Strip") | ~2–8 rows, max 4 tournaments | Email digest / FT registrations / AskFRED | **Core.** Elite FC entries only; prefer all names on fewer tournaments (if ~20 fencers enter one event, show fewer tournaments). Events coming up very soon in our area. No "(All Epee)". Sits next to the Deadlines box. |
| 9 | **Deadlines box** | ~3–5 rows | AskFRED / Email / Web | **Runs every issue** (v3.28, chat: Frank 2026-10-13). Entry deadlines and renewals, which can be months ahead. Separate from the local tournaments board (events very soon); place the two **adjacent**. |
| 10 | Club events | ~3–5 items or one-line notes | Email (newsletter) / Chat | Camps (e.g. Winter Camp), special classes, class changes as **one-line notes** (e.g. footwork class) — see Weekly Classes rule in Cut order. |
| 11 | **Parent Q&A** | ~40–70w (1 Q&A) | Chat (parent ask → Frank → Desk) | Answers a **real question a parent asked**. Anonymous; no Frank byline. `.rail-block.qa`. Default 1 per issue; second only if space after cuts. |
| 12 | **By the Book** (provisional rank) | 1 snippet | Frank's USA Fencing rulebook + penalty-guide material | v3.25. One rule or penalty per issue; random by default, the relevant penalty when something happened that week. **Nothing until Frank shares his material.** |
| 13 | **For the Parents** (provisional rank) | 1 item | Web / Chat (sourced per item) | v3.26. Standing box for non-fencing parents: one practical, **proactive** topic (term decoded, tournament tip, what to expect). Unlike Parent Q&A, nobody asked. Start issue not set. |
| 14 | Comic | 1 panel | Email (Frank; Ling may draw from No. 3 or later) | Sparingly. A guest artist gets a credit (guest-byline rule). |
| 15 | TV / streaming box | ~3–5 rows | Web (FIE calendar / FencingTV) | "Epee on Screen": major events + where to watch; no start times/prices unless listed. |

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
- Articles shrink/grow by WORDS; the rough guide is not a minimum or a target (v3.28) — length follows content quality.
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
  2. **Upcoming-tournament boards** (local tournaments board, formerly "Go Cheer") — shrink to the **nearest and most
     important** events and to **Elite FC entries only** (no open-call or “spots still open”
     rows). Fewer tournaments before fewer names; the board shrinks, it is not dropped (core).
  3. **Other standing utility boxes** — TV/streaming, glance/explainer boxes, comic: trim rows,
     then drop. The **Deadlines box** trims rows but is not dropped (runs every issue, v3.28).
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

## Open questions for Frank
1. **Ranking:** where do Overheard on Reddit, By the Book and For the Parents belong in the table? Placed provisionally.
2. **Local tournaments board name:** "Close to Home", "Nearby Tournaments" or "Local Strip"? ("Go Cheer" is retired; kept only in history.)
3. **Corrections:** SECTIONS-MENU marked a corrections box ✅, but corrections placeholders were killed 2026-10-06. Run a one-line correction only when needed, or never?
4. **Comic by Ling:** credit line, and does Ling send via efc.weekly like Frank?

Answered 2026-10-13 11:27 ET (chat: Frank 2026-10-13): no fixed lengths; Overheard one per issue when good, skip otherwise; Deadlines box every issue, next to the local board; "For the Parents" is final; "Dear Ref" folded into By the Book / dropped pending Frank (it was a Desk suggestion, not Frank's idea); "Go Cheer" being renamed.
