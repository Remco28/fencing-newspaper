# Standing source checklist
For the bot: check on the cadence below. For Frank: forward-by-email also accepted.
Epee only. Record every fact in `sources.json` (URL + date, or email message-ID + date).

## Cadence (locked v3.15 — Frank 2026-10-07; wording v3.19)

Times = US Eastern. Full ops loop (chat / email / gates): **STAGING.md § Ops cadence**.

| Pass | When | What |
|------|------|------|
| **Mid-week skim** | Wednesday | Light: Google News RSS (`fencing+epee` + `+New Jersey`) as juice detector; skim Tier-1 headlines / AskFRED changes worth staging; **X skim** (≈5–10 calls, see § X). Not a full checklist run. |
| **Publish-morning full pass** | When aiming to ship (usually **Mon/Tue**; later OK) | Full **Every run** checklist below, incl. **X full pass** (≈15–25 calls, see § X). Soft: see **Club-results hold preference** if members fence Monday. |
| **FencingTracker club page** (v3.24) | **Daily quick look** (weekday morning pass) · **Wednesday skim** · **Monday full pass** | Daily + Wed: one fetch of the Elite FC club results page for new results. Monday: full sweep (club page + event results pages for anything new). Gentle use — see § FencingTracker. |
| **Email** | Daily morning light pass + second pass right before HTML budget | Ingest → staging, `processed` label, media extract (STAGING.md). |

Keep all checklists below; do not delete sources when editing cadence.


## FencingTracker (recurring source — locked 2026-10-13, plan v3.24, Frank on a call 07:58 ET)
- **Club page (Elite FC results):** https://fencingtracker.com/club/100261977/Elite%20FC/results
- **Good for:** Elite FC results the NAC feed / AskFRED miss — local opens and regionals (e.g. Adela Sullivan's 2nd at the Artdu Open, Oct 11, 2026, appeared only here); placements by event; rating earned; links to event results pages (field size, pool/DE detail) and fencer history pages. Frank uses it himself.
- **Cadence:**
  - **Daily quick look (weekday morning pass):** fetch the club page once; diff against staging for new results.
  - **Wednesday skim:** same club-page check.
  - **Monday full pass:** full sweep — club page plus event results pages (`/event/<id>/results`) for any new Elite FC result (field size, pools, DE scores) and registration previews for upcoming boards.
- **Gentle use (like AskFRED):** a handful of page fetches per pass (daily/Wed: 1; Monday: ≲10), no crawling, no parallel bursts, plain browser User-Agent, back off on errors/429. Read-only.
- **Caveats:** scraped results are **unvetted until Frank vets** (scraped-source rule); some events (local opens) have no linked event page, so field size/venue may be missing; club attribution comes from registration and can be wrong — cross-check names against `roster/people.json`; names appear in registration form ("Young, Penelope", "Anayaà") → print via roster; don't confuse Elite Fencing Academy with Elite FC; results can post hours to a day after an event; FencingTimeLive is login-walled, so FencingTracker is our results mirror.
- Provenance: URL + retrieved_at (ET) in the staging item.

## fencing-api (Frank's API — added 2026-10-13, plan v3.33; SUPPLEMENTAL, cadence locked v3.34 — chat: Frank 2026-10-13 22:57 ET)
- **What:** Frank's own API over AskFRED (tournaments, preregistrations, results), USA Fencing (member.usafencing.org events, entrants, results with membership numbers) and FencingTracker (fencer search, profile, strength, win/loss). Base `https://fencingapi.teamremco.org`; guide `GET /v1/guide`; full schema `GET /docs` / `GET /openapi.json`. **Supplemental only:** it does not replace our direct checks of AskFRED, FencingTracker, USA Fencing and email; every pass still runs those. If the API and a direct source disagree (or API data is missing/wrong), flag it for Frank: he wants to hear about data problems.
- **Key:** `FENCING_API_KEY` in the gitignored repo `.env` only (header `X-API-Key`). Never commit, echo or paste it.
- **Client:** `scripts/fencingapi.py` (soft call cap 8/run, honors 429 `Retry-After`, polls 202 jobs). Examples: `health`, `club-results --since YYYY-MM-DD`, `search "<name>" --live`, `get <path> [--live]`.
- **Good for:** USA Fencing regional/national entrants and results by event (RYC/RJCC boards, NACs) with event days and close-of-registration times; AskFRED results and preregistrations; FencingTracker fencer lookups (ids, club). `GET /v1/results?club=Elite Fencers Club&since=…` joins every cached Elite FC result row; pass the full club name (`Elite` also matches Elite Fencing Academy).
- **Caveats:** cached-first: nothing exists until someone fetches it (`404 not_cached`); `club-results` only covers tournaments already fetched, so it is not a complete sweep by itself. `?live=true` scrapes and is limited (20 scrapes/min per key; 30/min per site across all keys; 600 req/min per key). FencingTracker `history` is season aggregates, not per-event placements. Always record `fetched_at` (UTC; convert to ET). `final: false` = results may still change. `birth_year` (keyed only) is youth data: never stage or print it.
- **Gentle use:** prefer cached reads; `--live` only for the specific tournament/event/fencer needed; ≤ ~10 calls per pass; spread live calls out.
- **Staging:** `source: "fencingapi"`, provenance = endpoint path + `fetched_at` (+ underlying site). Unvetted until Frank vets it (reality lock).
- **Cadence (v3.34; extra cross-check alongside the existing sources in each pass):**
  - Daily quick look (weekday morning pass): one cached `club-results` call since the last pass, plus `--live` results for any tournament Elite FC fenced that day/weekend; compare with the FencingTracker club-page look.
  - Wednesday skim: refresh upcoming Nearby Tournaments entrants; compare with FencingTracker/AskFRED registrations.
  - Monday full pass: live results for each event Elite FC entered the prior week + entrants for upcoming boards; compare with the direct FencingTracker/AskFRED/USA Fencing sweep.
  - Before the budget: refresh board entrants + deadlines (tournament timeline); compare with USA Fencing tournament pages.
  - Any disagreement → stage a note in the pass log and add a question for Frank (data problem).

## AskFRED API (locked 2026-10-07 — gentle use)
- Base: `https://www.askfred.net/api/v1/` — Bearer token in env `ASKFRED_API_KEY` (gitignored `.env` / process secret). **Never commit or paste the key into chat/docs.**
- **Client:** `scripts/askfred.py` — loads key from env/`.env`; backs off on 429; soft call cap (default 8). Defaults: Chatham NJ (40.7409, -74.3838), radius 75mi, weapon=epee, `per_page` 10.
- Gather usage (repo root):
  ```bash
  set -a && source .env && set +a   # or export ASKFRED_API_KEY=…
  python3 scripts/askfred.py me --summary --quiet-json
  python3 scripts/askfred.py tournaments --summary          # nearby upcoming epee
  python3 scripts/askfred.py tournament <uuid> --summary
  python3 scripts/askfred.py events <uuid> --summary
  ```
  JSON on stdout (omit `--quiet-json`); human lines on stderr with `--summary`. Prefer this over HTML for NJ epee discovery.
- Prefer API over HTML for upcoming epee near NJ: `/tournaments?latitude=&longitude=&radius_miles=&weapon=epee&start_date_gteq=…&per_page≤10` (API max 50; keep ≤10 for gather).
- Rate limits (respect 429): layered caps ~125 req/hour — for Gazette weekly use, **keep to a handful of calls per gather** (not bulk scrapes). This is a secondary account; do not abuse.
- Still timestamp closes; HTML fallback OK if API errors. Combine with FencingTracker / results-app for Elite FC names.
- Docs: https://help.askfred.net/en/articles/14068759-getting-started-w-askfred-s-api · endpoints: https://help.askfred.net/en/articles/10328385-api-endpoints-data

## Every run (publish-morning full pass)
- [ ] FIE news: https://fie.org/news (+ epee event/result pages as needed)
- [ ] USA Fencing epee feed: https://www.usafencing.org/news/epee
- [ ] NJ.com HS fencing (boys + girls): https://highschoolsports.nj.com/boysfencing (+ girls equivalent, NJSIAA posts)
- [ ] AskFRED upcoming near NJ (epee filter, note check-in close + staleness warning): https://www.askfred.net/tournaments
- [ ] X full pass (see **§ X (Twitter)**): tier-A timelines + 3–4 targeted searches; stage leads unvetted with post URL + time.
- [ ] Inbox **`efc.weekly@agentmail.to`** (AgentMail — SINGLE input channel; not Gmail). Flexible: Frank, apps, bots, newsletters, tips — stage all with provenance; never drop unknown senders. **Auto-vet allowlist:** `frankcng@gmail.com`, `chunkymonkey@agentmail.to` (Frank’s other bot / results-app digests), `elitefencersclub@111617670.mailchimpapp.com` (club Mailchimp). Others → unvetted until Frank vets. Cite by message-ID in `sources.json`; do not commit raw MIME. Detail: **STAGING.md § Tips / mail**.

## Weekly / as-needed
- [ ] FencingTracker club page (full sweep, § FencingTracker): https://fencingtracker.com/club/100261977/Elite%20FC/results + NJ event pages
- [ ] European Fencing Confederation results (epee): https://fencing-efc.eu/results
- [ ] FIE rankings pages (1 line each, top-3 moves only)
- [ ] Nearby NJ club blogs (Freehold template; add 2–3 more)
- [ ] r/Fencing via authenticated API (see REDDIT-SETUP.md) — tips only, snippet first, full thread only if relevant
- [ ] USA Fencing "First to 15" / "5 Minutes With Phil" / FIE podcast — 1 quote max
- [ ] NCAA pages (NJIT, Columbia, Duke, UNC, Notre Dame) — college-path items in season
- [ ] FencingTV — "watch the bout" short links only

## Juicy + open (no login needed — added 2026-10-06)
- [ ] Google News RSS: `news.google.com/rss/search?q=fencing+epee` (+ `+New+Jersey` variant) — best automated juice detector, anonymous.
- [ ] fencing.net: open news archive + guides (https://fencing.net) — epee 101, gear/armory explainers for Fencing 101 rotation; puns page for the jokes box. Forums are sunset but archives are curated.
- [ ] FIE events calendar (https://fie.org/events) — upcoming epee World Cups/satellites with dates (TV box + deadlines).
- [ ] YouTube channel RSS feeds (no login; verify channel IDs at build time — FIE, USA Fencing) — "watch this bout" links.
- [ ] Newsletters by email: subscribe `efc.weekly@agentmail.to` to USA Fencing + FIE updates — arrives as input, zero scraping.

## Social verdict (tested 2026-10-06)
- X: firecrawl fails outright (login wall since 2023). **Superseded 2026-10-08:** the built-in read-only `x` tools work. See **§ X (Twitter)** below.
- Instagram: profile fetch returns app-deep-link stubs, zero post content. Same wall. Exception: our OWN @elitefencersclub posts could come via Meta Graph API with the club's own token (our data, no scraping issue) — optional later.
- Rule for all social: never a fact source; angles only, verified against Tier 1–3 before print.

## X (Twitter) — added 2026-10-08 (v3.22)
Tested 2026-10-08 with the built-in **read-only** `x` tools (via GetDynamicTools / CallDynamicTool, namespace `x`).
**Vetted account list (tiers A/B/C + rejected + not-found): `sources/x-accounts.md`.** Only use handles from that
list. Verify any new handle with `get_users_by_usernames` before adding it, and never guess.

**Rules**
- **An X post is a lead, not a fact.** The one exception is a **tier-A** primary account talking about *its own* news
  (FIE on its own events, a college program on its own roster/results, a venue on its own dates). Even then,
  keep provenance on the staging item: post URL, post time (UTC + ET), and retrieved_at.
- Everything else (media, commentary, community) stages **unvetted** and gets checked against Tier 1–3 web sources
  or Frank before print. "Nothing gets printed as fact without verification."
- **Opinions** can run attributed, Overheard style ("one fan on X…"), with **no usernames** unless the account is an
  official org or a public figure. Same as Overheard on Reddit.
- **Never** list, quote, or name personal accounts of **minors or youth fencers**. Adult national-team athletes and
  coaches are OK only if public, verified by lookup, and fencing-focused.
- Don't mine the replies/mentions pile. `@USAFencing` mentions are mostly unrelated political noise.

**Use it gently**
- Limits: 30 reads/min, 1,000/day (each response reports what's left). Gazette budget: **Wednesday skim ≈5–10 calls;
  Monday/publish-morning full pass ≈15–25 calls.** Never bulk-pull.
- Cheapest useful calls: `get_users_posts` on tier-A ids (exclude replies, max 10–25), then `search_posts_all` with
  `lang:en` and fencing context words (plain "epee"/"épée" pulls in French "sword" noise; "NAC" alone pulls in
  soccer/supplements/Moldova). `get_posts_by_ids` to re-read a post exactly before quoting it.
- Weak spots: `search_users` → 403 (app-only access), so you can't search for accounts. `search_news` is
  Grok-written trend summaries ("may make mistakes"), mostly garbage-fence stories for "fencing", so skip it.
  `sort_order: relevancy` gave off-topic junk for rule-change queries; prefer `recency` + tight terms.
- Fold into the cadence: Wednesday skim = FIE + NJ college timelines + one NAC/epee search. Monday full pass =
  all tier-A timelines active in the last 30 days + searches for this week's events (NAC, World Cup, NJ HS/college).

## Club-results hold preference (soft — not a rule)
- [ ] Optional: from results-app / start lists, any Elite FC members competing **Monday**? Holding for those results is nice when easy — publishing later (or without them) is fine.
- [ ] Re-check AskFRED close times for locals with late/at-door entry (feeds deadlines + signup board)
- [ ] Re-check emailed start-list slice for Elite FC entrants (signup board names)
