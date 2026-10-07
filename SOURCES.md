# Standing source checklist
For the bot: check on the cadence below. For Frank: forward-by-email also accepted.
Epee only. Record every fact in `sources.json` (URL + date, or email message-ID + date).

## Cadence (locked v3.15 — Frank 2026-10-07; wording v3.19)

Times = US Eastern. Full ops loop (chat / email / gates): **STAGING.md § Ops cadence**.

| Pass | When | What |
|------|------|------|
| **Mid-week skim** | Wednesday | Light: Google News RSS (`fencing+epee` + `+New Jersey`) as juice detector; skim Tier-1 headlines / AskFRED changes worth staging. Not a full checklist run. |
| **Publish-morning full pass** | When aiming to ship (usually **Mon/Tue**; later OK) | Full **Every run** checklist below. Soft: see **Club-results hold preference** if members fence Monday. |
| **Email** | Daily morning light pass + second pass right before HTML budget | Ingest → staging, `processed` label, media extract (STAGING.md). |

Keep all checklists below; do not delete sources when editing cadence.


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
- [ ] Inbox **`efc.weekly@agentmail.to`** (AgentMail — SINGLE input channel; not Gmail). Flexible: Frank, apps, bots, newsletters, tips — stage all with provenance; never drop unknown senders. **Auto-vet allowlist:** `frankcng@gmail.com`, `chunkymonkey@agentmail.to` (Frank’s other bot / results-app digests), `elitefencersclub@111617670.mailchimpapp.com` (club Mailchimp). Others → unvetted until Frank vets. Cite by message-ID in `sources.json`; do not commit raw MIME. Detail: **STAGING.md § Tips / mail**.

## Weekly / as-needed
- [ ] FencingTracker club page + NJ event pages: https://fencingtracker.com
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
- X: firecrawl fails outright (login wall since 2023; free API killed, paid tiers ~$100/mo). Snippets via searxng only + forwarded links.
- Instagram: profile fetch returns app-deep-link stubs, zero post content. Same wall. Exception: our OWN @elitefencersclub posts could come via Meta Graph API with the club's own token (our data, no scraping issue) — optional later.
- Rule for all social: never a fact source; angles only, verified against Tier 1–3 before print.

## Club-results hold preference (soft — not a rule)
- [ ] Optional: from results-app / start lists, any Elite FC members competing **Monday**? Holding for those results is nice when easy — publishing later (or without them) is fine.
- [ ] Re-check AskFRED close times for locals with late/at-door entry (feeds deadlines + signup board)
- [ ] Re-check emailed start-list slice for Elite FC entrants (signup board names)
