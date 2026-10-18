# Changelog — En Garde Gazette docs

Newest first. Earlier versions (v3.3–v3.19) are summarized in PLAN.md (status line, §8, §9).

## v3.37 — 2026-10-18
- **New recurring optional section: Photo from History** (Frank 2026-10-18, relayed by Grok Bot): one epee photo per issue, caption + credit mandatory, about 100–150 words including the caption (SECTIONS-MENU). New cross-issue pile `staging/history-photos/`: 12 entries distilled from Frank's research library (one compact .md each, plus a resized ≤1600 px JPEG), INDEX.md and a 3-line rights note. All 11 Commons licenses were spot-checked and match; 04 (LA84) is public domain by its 1928 publication date (US). Not yet in a budget; Frank picks.

## v3.36 — 2026-10-18
- **Claude Code is an optional second reviewer** (Frank 2026-10-18, relayed by Grok Bot): (a) copy check after vetting, before budget/compose; (b) proof check of rendered PNGs alongside Desk's own visual QA; (c) site and code work. Desk stays the writer and source-of-truth keeper; Claude Code never adds facts. Skip it if it's unavailable. PLAN §6, STAGING § Claude Code. First run: No. 3 copy check (Opus); taken/rejected fixes are logged in each item's `vet_notes`.
- **No. 3 budget feedback applied** (`issues/2026-10-19/budget-submission.json`, Frank 09:13 ET): Vet Worlds is now the lead (165w); the Controversial Call is rewritten for flow (v2, no new facts; v1 kept) and becomes the page-1 feature; Club Results runs only if a club fencer qualified at the NJ JO qualifier, otherwise the box is dropped (no "also fenced"); Overheard runs; gear and the weekly class table are out; Winter Camp stays "contact the club". Fill is about 84%; compose waits for Frank's additions.

## v3.35 — 2026-10-18
- **No. 3 budget built Sunday** (voice: Frank 2026-10-18 ~8:26 ET) instead of the Monday 8:50 routine. The No. 2 lineup is archived at `budget-demo/archive/practice-lineup-issue2-2026-10-13.json`, and the new `budget-demo/practice-lineup.json` is No. 3 (fill about 69% vetted, 74% with For the Parents).
- **By the Book is now Desk-written from the rulebook** (`reference/usa-fencing/`), so Frank's material isn't needed first (CONTENT-HIERARCHY row 12). First item: unjustified appeals (t.172 / t.174 / t.165).
- **Names rule:** official club/tournament pages are the source of truth, so the Desk stops asking Frank about names (STAGING § Names + pending entries, roster/README, STYLE-GUIDE §0b). Roster adds Samuel SarroWaite, Nora Li, Owen Li and Christina Jiang (AskFRED spellings). Nora/Owen relation is recorded as unknown.
- **Pending entries print** on the Nearby Tournaments board (CONTENT-HIERARCHY row 8, STAGING).
- Vets applied per Frank's voice instructions: Vet Worlds women (conditional on the fie.org check; met: US team gold confirmed), Elsayed (conditional on an authoritative source; met: FIE ranking + FIE article), Medeo #4/#5 combined line, gear one-liner, NJ HS one-liners, By the Book.

## v3.34 — 2026-10-13
- **fencing-api is supplemental** (chat: Frank 2026-10-13 22:57 ET): it does not replace direct AskFRED / FencingTracker / USA Fencing / email checks. Removed the "use it instead of scraping" wording. Cadence locked as an extra cross-check in each pass (daily quick look, Wednesday skim, Monday full pass, pre-budget) in SOURCES.md § fencing-api and STAGING ops cadence (0b). API-vs-direct disagreements are flagged for Frank.

## v3.33 — 2026-10-13
- **New source: fencing-api** (Frank's API over AskFRED / USA Fencing / FencingTracker; chat: Frank 2026-10-13 22:54 ET). SOURCES.md § fencing-api (coverage, limits, gentle use, staging as `source: "fencingapi"`, unvetted). Helper `scripts/fencingapi.py` reads `FENCING_API_KEY` from gitignored `.env`. Cadence **proposed** (daily quick look + Wed skim + Monday full pass + pre-budget); Frank to confirm before it goes into STAGING ops cadence. Test calls matched staged data (Morris Cup Cadet Men entrants; Medeo Y12 Mixed 5th for Christina Jiang; Milinkovic FencingTracker id).

## v3.32 — 2026-10-13
- **No. 2 reopened as PROOF v2** (chat: Frank 2026-10-13 12:01 ET; not yet printed): right flank now "It is better to deserve a rating than to have one." (default applies **from No. 2 onward**; `flank-quotes.json`, STYLE-GUIDE §12); board renamed "Go Cheer" → "Nearby Tournaments"; new **Deadlines** box (page 2, directly under the board): Ultimate Cup regular entry Oct 19 (extended), Morris Cup late entry Oct 22, Ultimate Cup late entry Oct 29, all from USA Fencing tournament pages. Awaiting re-approval.

## v3.31 — 2026-10-13
- **Masthead right flank default from No. 3:** "It is better to deserve a rating than to have one." (Frank, 2026-10-13 11:58 ET), replacing "Know yourself, know your enemy, know where you left your glove." Approved Nos. 1–2 unchanged. `flank-quotes.json` gains `right_flank_default`; STYLE-GUIDE §12 updated. Template A reference sheet (`issues/2026-10-14`) already carried this quip. Fit check: `staging/weeks/next/checks/masthead-check-no3.png` (wraps to two lines, hairlines clear of the logo).

## v3.30 — 2026-10-13
- **New occasional section "Controversial Calls"** (chat: Frank 2026-10-13 11:34 ET): article only when a real disputed call comes up. Structure: the call (verified facts) / the rule (rulebook + penalty guide, brief quotes) / both sides (labeled opinion) / the verdict (what the rules support, or "judgment call"). No naming referees critically; fencers named only with the family's OK; reality lock applies. CONTENT-HIERARCHY new § Occasional / triggered sections; SECTIONS-MENU 19c; PLAN §3.
- **Dear Ref back to MAYBE** (Frank: "isn't the worst thing"), separate from Controversial Calls; reverses the v3.28 "folded/dropped" mark.

## v3.29 — 2026-10-13
- **Board named "Nearby Tournaments"** (chat: Frank 2026-10-13 11:29 ET), replacing "Go Cheer" (kept only in history: No. 2 print, CHANGELOG, roll-forward archives). Applied to CONTENT-HIERARCHY (row 8, cut order; open question removed), SECTIONS-MENU, PLAN, STYLE-GUIDE, Template A reference heading (`issues/2026-10-14/issue.html` box title), budget page labels (`budget-demo/index.html`, `practice-lineup.json`), and staging next/ board items (`board: "Nearby Tournaments"`).

## v3.28 — 2026-10-13
- **Frank's answers to the hierarchy questions** (chat: Frank 2026-10-13 11:27 ET): no fixed section lengths (sizes are rough guides only; "Budget" column → "Rough guide"); Overheard on Reddit best at one per issue but skipped when nothing good; Deadlines box runs every issue (entry deadlines + renewals, months ahead), separate from and adjacent to the local tournaments board; "Go Cheer" being renamed (options: Close to Home / Nearby Tournaments / Local Strip; Frank to pick); "For the Parents" is final; "Dear Ref" (a Desk suggestion) folded into By the Book / dropped, pending Frank. Remaining open: ranking, board name, corrections, Ling credit. CONTENT-HIERARCHY, SECTIONS-MENU, PLAN.

## v3.27 — 2026-10-13
- **CONTENT-HIERARCHY review/cleanup** (Frank, call 2026-10-13 08:09 ET): renumbered 1–15 (no 9a/9b); source key added (efc.weekly email, FencingTracker, AskFRED, chat, web, X, Reddit) replacing stale "Results-app email"; house-rules line (invent nothing, no club Epee labels, results tone, bylines); added Overheard on Reddit row (provisional) and Go Cheer naming; Ratings earned "always in when earned"; Club events covers camps + one-line class notes; comic notes Ling; TV box = "Epee on Screen"; new sections "Standing elements" (THE WEAPON figure, Weekly Classes rule, photo desk, page placement) and "Planned one-off features" (referee piece → No. 4); killed list tidied; second Overheard counts as Desk fill in cut order; open questions for Frank listed at bottom.
- SECTIONS-MENU reconciled: header says CONTENT-HIERARCHY is canonical; cut items (weather, crossword, quiz, jokes) marked ❌; lead budget aligned to 150–180w; Dear Ref and Corrections flagged as open questions; new sections noted.

## v3.26 — 2026-10-13
- **New recurring section "For the Parents"** (working name; Frank, call 2026-10-13 08:07 ET): standing box for non-fencing parents, one practical item per issue (fencing term decoded, tournament tip, or what to expect at an event). Differs from Parent Q&A: Q&A answers real parent questions; this is a proactive topic. Start issue open; no content staged. CONTENT-HIERARCHY row 9b (position provisional, Frank sorts); PLAN §3.
- Renamed from "For the Grown-Ups" to **"For the Parents"** (Frank, call 2026-10-13 08:08 ET): "Grown-Ups" suggests parents of little kids; "For the Parents" is warmer and clearer. Nothing else changed.

## v3.25 — 2026-10-13
- **New recurring section "By the Book"** (Frank, call 2026-10-13 08:01 ET): short snippets from the USA Fencing rulebook and penalty guide, one rule or penalty per issue; random by default, or the relevant penalty when something specific happened that week. No content yet — awaiting Frank's material (rulebook / penalty-guide apps). Name clash with future club-site book content considered; Frank says fine. CONTENT-HIERARCHY row 9a; PLAN §3. Placeholder staged in `staging/weeks/next/` (No. 3): `chat-by-the-book-placeholder-2026-10-13`.

## v3.24 — 2026-10-13
- **FencingTracker added to recurring sources** (Frank, call 2026-10-13 07:58 ET): it catches results the NAC feed misses (Adela Sullivan's Artdu Open 2nd showed up only there) and Frank uses it. Club page https://fencingtracker.com/club/100261977/Elite%20FC/results. Cadence: daily quick look (weekday morning pass), Wednesday skim, Monday full sweep. Gentle use like AskFRED. SOURCES.md § FencingTracker + cadence table; STAGING.md § Ops cadence.
- Issue No. 2 approved (Frank 2026-10-13 07:57 ET); staging rolled forward (No. 3 = week of Oct 19).

## v3.23 — 2026-10-12
- **Results tone locked (Frank, chat 2026-10-12):** never print a weak finish/place; strong = podium/top 8, notable climb, personal best, unbeaten pool; others go on an "also fenced"/"also attended" line; when unsure, "also fenced". STYLE-GUIDE §0d, CONTENT-HIERARCHY results row. No. 2 results box no longer provisional.
- Medeo: Christina Jiang 5th printed as **Y12 Mixed** (Medeo combines men's+women's when one is small; AskFRED "Y12 Women's" is registration only).
- Roster: Rahi prints as **Shah-Mirani** (resolved, matches Ash).
- Staged Overheard on Reddit #2 candidate (r/Fencing Princess Bride duel thread), unvetted, with claim-check; draft `staging/weeks/next/drafts/overheard-princess-bride.md`.

## 2026-10-12 — Issue No. 2 budget (Monday full pass)
- Full SOURCES pass + second email pass; 8 new staging items (NAC results, Elite/Challenger explainer, Vet Worlds, NJSIAA dates, epee TV calendar, Ultimate Cup board, gear fill, NJFA lead); Clean marked 6 stale/merged items. Log: `staging/weeks/next/gather-log-2026-10-12.md`.
- Budget page: lineup `mode: "real"` swaps the PRACTICE tag for "Real budget · Submit goes to the Desk" and submits `practice: false` / `pageVersion: budget-v2`. Rehearsals keep `mode: practice` (default).

## 2026-10-12 — Issue No. 2 budget: Frank's chat answers (09:45 ET)

Recorded as "chat: Frank 2026-10-12". Not composed (Frank hasn't submitted).
- Vetted: NAC lead + results (FencingTracker kept as source), Ultimate Cup board, Medeo (Christina Jiang 5th),
  NJFA Sept. 29 late lines (Bradley Tsai confirmed; Brendan Mendez on FencingTracker club listing + Frank's belief, school never printed).
- Medeo: Bryce Cheng removed (did not fence; no reason printed). AskFRED lists Y12 Women's Epee, Frank said "Y12 mixed": row prints neutral "Y12" pending Frank.
- Roster: + Dieko Johnson, Lillian Liu, Bradley Tsai, Brendan Mendez; Ash resolved as Shah-Mirani (Rahi still unresolved).
- Winter Camp moved to staging/weeks/after-next (held for No. 3).
- Lineup: one club results box; weaker NAC finishes as "also fenced" (provisional, tone policy pending). Publish note "Tue or Wed, Frank deciding" (date stays Tue 10/13).
- practice.html: sidebar horizontal scrollbar fixed (jump-nav links' negative margin overflowed by 10px; nav now pads + overflow-x hidden); publish-day line shows the lineup's note.

## v3.22 — 2026-10-08 (X as a source)

Frank: test X (Twitter) as a source using the built-in read-only `x` tools, gently (about 25 calls used of a
40–60 budget; limits are 30/min and 1,000/day).

- **Works:** user lookup, user timelines, full-archive post search, post re-reads, mentions. **Doesn't:**
  `search_users` (403, app-only access); `search_news` is Grok trend summaries, noisy for "fencing".
- **`sources/x-accounts.md`** (new): vetted list with handle, display name, X user id, tier (A official /
  B media / C community), why, last active, vetted 2026-10-08. Plus rejected accounts (dormant, empty,
  fence companies, spam, can't-verify) and handles that don't exist. No minors' accounts, no private adults.
- **SOURCES.md § X (Twitter):** an X post is a lead, not a fact, unless it's a tier-A account on its own news
  (provenance still required). Opinions can run Overheard-style without usernames (except official orgs /
  public figures). Gentle-use budget: Wed skim ≈5–10 calls, Monday full pass ≈15–25. Old "Social verdict"
  X line marked superseded. Cadence table + Every-run checklist + STAGING.md self-gather updated.
- **Staged for Issue No. 2 (all unvetted, `source: "x"`, tag `x-lead`, provenance `x_post`):**
  `x-lead-nac-oct-results-watch`, `x-lead-veteran-worlds-tbilisi`, `x-lead-elsayed-world-no1-epee-feature`,
  `x-lead-passivity-p-black-explainer`, `x-lead-usafencing-nfl-radio-ad`. A corroborating @USAFencing post was
  added to `gather-college-path-shamel-epee` provenance (vetted status unchanged).

## v3.21 — 2026-10-07 (budget page v2)

Frank: the practice budget page was hasty and hard to read, even on desktop. Redesigned for how he
uses it — the box desktop browser through the computer tab, 1280×800, with some remote lag.

- **`budget-demo/practice.html` v2:** fixed left bar (issue, publish-day field, rough fit meter,
  Included / Need Vet / Questions counts that jump to the first match, section nav, Submit);
  sections in reading order (Lead & features · Club · Shorts & fill · Photos · Held, merged & next
  week); one card per slot with headline, one-line summary, words/rows + budget, status badges,
  **Questions for Frank** answer boxes, big Include toggle, note box, Vet, ↑/↓ reorder (replaces
  drag). Draft text (readable serif block, `[NEED]` highlighted) and provenance are collapsed and
  built only when opened. 16px body, ~68ch lines. No animations, transitions, shadows, blur, or
  smooth scroll; updates touch only the changed card and the counters.
- **Lineup schema 2** (`practice-lineup.json`): `issue`, `desk_summary`, `sections`, `slots` with
  `summary` / `questions`; staging items not in the file are auto-placed (not proposed). Issue No. 1's
  lineup and the v1 page moved to `budget-demo/archive/`. Lineup rewritten for Issue No. 2.
- **Server:** `GET /thumb/<file>?w=&bw=` (small cached JPEGs in gitignored `budget-demo/.thumbs/`),
  `/api/media` adds pixel sizes, `/api/lineup` alias, env overrides for testing on a throwaway copy
  (`GAZETTE_STAGING_WEEK`, `GAZETTE_SUBMISSIONS`, `GAZETTE_LINEUP`, `GAZETTE_PORT`). `/vet` and
  `/submit` unchanged; submit JSON keeps v1 keys and adds `answers`, `issue`, `pageVersion`.
- **`screenshot.py`:** viewport mode (`… <out> 1280 800`) shoots what Frank sees, per section.
- Docs: STAGING.md Budget step (Monday routine + schema), PLAN §10, README.

## v3.20 — 2026-10-07 (after Issue No. 1)

Issue No. 1 (Thursday Edition, Oct 8, 2026) approved by Frank in chat at 18:40 ET after proof v2;
Frank printed the PDF himself. Decisions from that first real run, locked:

- **Epee is assumed** (STYLE-GUIDE §0c; PLAN §1): no “Epee” / “(Epee)” labels in club context —
  box titles, table headings, our fencers’ event names, captions. Keep the word only for
  outside-world multi-weapon stories, proper names, and contrasts (rule explainers, HS primer).
  Frank will say if foil/sabre is ever added. Cleaned labels: `prototype/monday-v6.html`
  (“Events (Epee)” → “Events”), `issues/2026-10-14/issue.html` sample labels (HTML only; the
  locked `paper-v3.14.pdf` reference is unchanged), `budget-demo/index.html` (demo club results +
  Medeo row), `budget-demo/practice-lineup.json` (Medeo events, Morris Cup title).
- **Content-heavy cut order** (CONTENT-HIERARCHY; STYLE-GUIDE §11; SECTIONS-MENU; PLAN §3):
  standing/utility boxes give way to stories — drop the regular Weekly Classes table (changed or
  special class → one-line note), shrink tournament boards to nearest/most important events and
  Elite FC entries, trim other utility boxes, then cut stories. Page 1/2 placement stays flexible.
- **Budget slot note overrides `publishDate`** (STAGING Budget).
- **Desk fill** with Frank-vetted items when stories run short; Frank can veto at proof
  (CONTENT-HIERARCHY stretch; STYLE-GUIDE §11).
- **Late add past 2 pages → trim Desk-fill stories first**, never shrink type
  (CONTENT-HIERARCHY; STYLE-GUIDE §6).
- **Caption naming**: only Frank-confirmed people; no left/right order unless verifiable;
  others are “other medalists” or similar (STYLE-GUIDE §19, §7).
- **Chat spelling beats scrape**; scraped form → roster alias (STAGING Clean; roster/README).
- **FencingTracker / scraped registrations stage unvetted** until Frank confirms (STAGING Tips/mail).
- **Proof round**: v1 → Frank’s answers → v2 → approval → print; Frank prints the PDF himself;
  proof status lives in `issue.json` (+ `proofApproval` in `approvals.json`); approved PDFs frozen
  (STAGING Proof; PLAN §6).
- **PNG inspection before a proof is called done** — already in STYLE-GUIDE §7 (“Render… rasterize
  to PNG, and LOOK”); reaffirmed with an explicit “no proof-ready doorbell before PNGs are inspected”.
- **Staging roll-forward** after approval: `next/` → `staging/weeks/2026-10-08/`, `after-next/`
  → `next/` (THE WEAPON now in `next` for Issue No. 2, week of Oct 12), fresh `after-next/`.
