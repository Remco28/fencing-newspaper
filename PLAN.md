# Fencing Newspaper — Plan v3
Date: 2026-10-06
Status: locked direction from Frank, details in progress (v3: signup board both days, Thursday = local last-minute, sources expanded, Reddit auth answered)
Project folder: `~/Dev/fencing-newspaper` (moved from `~/Projects/fencing-newspaper` on 2026-10-06 — wrong-computer oops)
Work item: office work #21

## 1. What we're building (v2 locked)

1 sheet, front + back, black & white, high-school reading level.
Audience: Elite Fencers Club members (Chatham, NJ), **epee only — no foil, no saber.**

Two editions per week:
- **Monday morning: results edition.** What happened over the weekend.
- **Thursday: signup edition.** Final reminder to enter upcoming tournaments + who from our club is already signed up.

Editorial control: **Frank only.** No parent/kid submissions. No coach involvement (skip coaching tips entirely).

Automation: built to run under a scheduled bot — **Grok Bot (xAI) or OpenAI Dots** — at a chosen time. V1 runs **human-verified** (Frank approves PDF before print). Auto-print enabled only once issues look right.

AI model is **swappable** by design. Template owns layout; model only fills fields.

## 2. Content rules (v2)

Epee filter applies to everything: FIE, national, high-school, club. If a source mixes weapons, we extract epee events only.

### Sources

**Tier 1 — World + National (epee only)**
- FIE news + results + rankings, filtered to epee: https://fie.org/news
- USA Fencing news + national results (NACs, Summer Nationals, JOs): https://www.usafencing.org/news
- Escrime XXI / American Fencer for background features.

**Tier 2 — NJ high school (whole state, epee)**
- NJ.com high-school fencing: https://highschoolsports.nj.com/boysfencing (and girls equivalent), NJSIAA rule/change posts.
- Scope is all-NJ epee, not just Chatham. Chatham HS gets a callout when relevant, not a dedicated beat.

**Tier 3 — Tournaments + club (the reason to pick it up)**
- Tournament results: reused from Frank's other app (fencer-schedules: USFA + AskFRED start-list data proven). That app **emails** this project the relevant slice — no shared DB, no scraping twice.
- Club emails: forwarded directly to the newspaper bot as input (announcements, closures, camp dates).
- Member results + signups: from the emailed data + FencingTracker club page cross-check.
- No crowd submissions. If it's not in an emailed source or a fetched page, it doesn't print.

**Reddit (r/Fencing) — tip sheet only, auth possible**
- Tested 2026-10-06: anonymous fetch of reddit.com / old.reddit.com / RSS is **login-walled / blocked** (network policy + account gate). Firecrawl returns a login page; RSS returns "blocked due to network policy."
- What works today: local searxng discovers r/Fencing threads via search snippets (Google CSE engine).
- With a login: yes, it can work — but not with username+password alone in a fetcher. Need a Reddit **script-type app** (client_id + client_secret) plus the account credentials for OAuth (PRAW script flow), stored in env, never in git/chat. Post-2023 API limits apply (rate caps, mod compliance). This upgrades Reddit from "snippets" to "authenticated read of threads/comments."
- Rule either way: Reddit never auto-ingests as fact. It suggests angles ("people are arguing about X"); every printed fact still comes from FIE / USA Fencing / NJ.com / emailed data, editor-verified. Cheapest v1 alternative: Frank forwards interesting thread links by email like any other tip.

### Additional sources found 2026-10-06 (all filtered to epee)
- USA Fencing epee-only news feed: https://www.usafencing.org/news/epee — use instead of the general news page.
- FIE live results + rankings + event pages (e.g. Worlds results tables): https://fie.org — results are structured, good for scoreboard facts.
- FencingTV: https://www.fencingtv.com — for "watch the bout" links (print as short URL), not facts.
- European Fencing Confederation results, weapon-filterable to epee: https://fencing-efc.eu/results — useful when FIE coverage is thin.
- AskFRED tournament catalog + preregistration pages: https://www.askfred.net/tournaments — entry lists, check-in close times, ratings mix (proven in fencer-schedules). Note pages warn lists may be stale — always timestamp.
- FencingTracker: registrations, podium finishes, ratings, NJ event pages (e.g. NJ Division qualifiers, Durkan showcase): https://fencingtracker.com — cross-check for club/NJ results.
- NJ.com boys/girls fencing + NJSIAA posts (already Tier 2) — the only consistent NJ high-school source found; NJ Division USFA news otherwise flows through AskFRED + club blogs.
-Nearby club feeds (example): Freehold Fencing Academy upcoming-tournaments category — template for "what locals announced this week"; add 2–3 more NJ clubs the same way.
- USA Fencing official podcast "First to 15" + CEO newsletter "5 Minutes With Phil" + FIE "minds of champions" podcast spot: https://www.usafencing.org/firstto15 — background quotes only, 1 per issue max.
- NCAA: NJIT / Columbia / Duke / UNC / Notre Dame fencing pages + https://www.ncaa.com/sports/fencing — college-path stories for youth (epee names only).
- FencingTimeLive (FTL): deferred to later, for live strips/results once results-app covers it.

### Sourcing rules
- Scores, names, signup lists come from fetched/emailed sources, never model memory.
- Every issue keeps `sources.json` (URL + retrieved date, or email message-ID + date).
- Foil/saber items are dropped at fetch time, not rewritten.

## 3. Sections (v3 — locked by Frank 2026-10-06)

Shared shell: masthead **En Garde Gazette** + descriptor "The Elite Fencers Club Weekly" (locked 2026-10-06; no "!" in the nameplate — the bang lives in headlines, not the masthead), date, edition tag (Monday Results / Thursday Signups), issue #,
footer with print timestamp + archive pointer. Bylines: none for Frank, credit guest writers.
Weighting rule: club newsletter news > national/regional tournaments > locals.

**Monday — Results edition (front / back), news-first**
1. Lead epee result of the weekend (FIE or national if big, else top NJ/club result). 120–150 words.
2. 1–2 more short epee articles (national/regional weight over locals). News beefier than scores.
3. Club results box: Elite FC epeeists, event, place — from emailed results data.
4. Ratings earned box: members' new ratings — always in, celebration.
5. Scoreboard strip: 4–6 world/national epee one-liners.
6. **Signup board (compact): available tournaments + Elite FC entrants.** Full version Thursday.
7. Back: TV/streaming box (major events + where to watch) + 1 upcoming-deadline box + club events (from newsletter email).

**Thursday — Signup edition (front / back), no rehash**
1. Lead: "Entries close soon" — biased to local late/at-door events. 100–120 words.
2. **Signup board (full): available tournaments + who from Elite FC is already entered**, grouped by event/day, short print-friendly entry URLs.
3. Weekend logistics box: venue, check-in close, what to bring (sourced only).
4. Back: 1-line pointer to Monday's results + TV/streaming box + club events.
5. Comic (sparingly, Frank-supplied via email) as space allows.

Maybe later: advice column ("Dear Ref") — no slot yet. Low priority: recruiting notes (only if genuinely good).
Cut for v1: weather, food, travel, crossword, quiz/trivia, jokes/riddles, photos.

**Thursday — Signup edition (front / back), no rehash**
1. Lead: "Entries close soon" — tournament name, close date, why it fits our fencers. 100–120 words. Bias to **local events with late / at-door registration** (Thursday signups are last-minute locals, not NACs planned months out).
2. **Signup board (core, full): available tournaments + who from Elite FC is already entered**, grouped by event/day, with entry links as short print-friendly URLs. Seeing clubmates entered is the point — keep names prominent.
3. Weekend logistics box: venue, check-in close times, what to bring — only if sourced from AskFRED/USFA event pages or emailed data.
4. Back: pointer to last Monday's results (1 line, no rehash) + trivia.

Dropped: coaching tips, foil/saber anything, editorials, long interviews.

## 4. Layout — fixed set, rotated

Frank's call: fixed templates, but **rotate among 2–3 locked templates** so it doesn't feel identical weekly.

Rules:
- Templates A/B/C are designed once, print-tested, then frozen. Rotation is round-robin or Monday=A-results / Thursday=B-signups; no generative redesign.
- Content/ layout split stands: AI fills `issue.json` (strict schema + word limits + epee-only), template renders `paper.pdf` deterministically (HTML + print CSS → Chromium headless or WeasyPrint).
- US Letter, 0.5in margins, B&W-safe: 100% black headlines, no gray text under 10pt, 1–2pt rules, SVG line art only (no photos v1).
- ~600–700 words max per issue.
- Per-issue folder: `issues/<date>-<edition>/issue.json + sources.json + emails/ + paper.pdf`.

Why rotate fixed templates instead of free design: same readability + reliable print, but visual variety. New template = design task with test print, never a weekly AI decision.

## 5. Inputs — email is the single channel (locked 2026-10-06)

Frank sends EVERYTHING via email, including comics he draws himself. The bot also does independent
research per SOURCES.md. Allowlisted inbox; every item stored per-issue with message-ID.
1. **Results/schedule app → bot:** structured email (JSON or fixed-format body + optional PDF attach): tournament, event, day, Elite FC entrants/results → `inputs/results-<date>.json`.
2. **Club newsletter forwarded:** announcements, events, ratings → `inputs/club-<date>.md`.
3. **Frank's extras:** comics (image attach), tips/thread links, guest pieces → `inputs/frank-<date>/`.

Needs: dedicated inbox address, allowlist (only Frank's app + Frank's forwards accepted), attachment cap, spam fallback = ignore + flag in preview.

## 6. Automation + verification

- Scheduler: Grok Bot or OpenAI Dots runs `make-issue.sh --edition monday|thursday` at set times (Mon ~6am, Thu ~6am — adjustable).
- V1: bot builds PDF + **waits for Frank's approve** (preview link / email). No auto-print until approved.
- Later: `lp -d club-printer paper.pdf` auto-print after N clean issues.
- API keys live in env file on the runner, never in git. Allowlisted inbox only.

## 7. Style — see STYLE-GUIDE.md (authoritative, locked 2026-10-06)
Visual rules (3-col grid, no heading symbols, no print chrome, alignment, fill rule, visual QA)
live in STYLE-GUIDE.md. Voice rules stay here:
- High-school reading level (FK 8–10). Explain jargon first use. Epee terms only.
- Headlines ≤6 words, active verb. Full name + event + club on first local mention.
- Ban list: "delve", "fast-paced world of", "testament to", snark.
- Masthead/footer identical; only date/edition/issue # + template variant change.

## 8. Resolved in v2 / still open

Resolved:
- [x] Epee only
- [x] Mon results + Thu signups
- [x] Signup board with club entrants
- [x] Email inputs (results app + forwarded club mail)
- [x] No coaching tips, coach not involved
- [x] Frank-only editorial, no submissions
- [x] Fixed templates, rotate 2–3
- [x] Swappable model
- [x] Human-verified first, auto-print later
- [x] Reddit verdict: search-discovery only

Still open:
1. Paper name?
2. Exact run times (Mon/Thu 6am OK?).
3. Inbox address + email format from results app (define schema).
4. Thursday data cutoff (e.g. entries as of Wed 8pm?).
5. Archive PDFs in git or local-only?
6. Printer model + who loads paper.

## 9. Next steps
- [ ] Lock name + run times + inbox address
- [ ] Define results-app email schema (fields: tournament, event, day, entrants, results, source IDs)
- [ ] Do Reddit OAuth setup per REDDIT-SETUP.md (Frank one-time, ~10 min)
- [ ] Narrow SECTIONS-MENU.md to v1 lineup (proposal at bottom of that file)
- [ ] Build templates A (results) + B (signups) HTML/CSS, B&W test print
- [ ] Build fetch per SOURCES.md checklist (FIE/USA/NJ.com epee filter) + email-ingest scripts
- [ ] 2 dry-run issues per edition with Frank red-pen, then enable scheduled bot
- [ ] See also: SOURCES.md (standing checklist), SECTIONS-MENU.md (full options), REDDIT-SETUP.md
