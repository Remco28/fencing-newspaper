# Changelog — En Garde Gazette docs

Newest first. Earlier versions (v3.3–v3.19) are summarized in PLAN.md (status line, §8, §9).

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
