# Standing source checklist
For the bot: check every run. For Frank: forward-by-email also accepted.
Epee only. Record every fact in `sources.json` (URL + date, or email message-ID + date).

## Every run (Mon + Thu)
- [ ] FIE news: https://fie.org/news (+ epee event/result pages as needed)
- [ ] USA Fencing epee feed: https://www.usafencing.org/news/epee
- [ ] NJ.com HS fencing (boys + girls): https://highschoolsports.nj.com/boysfencing (+ girls equivalent, NJSIAA posts)
- [ ] AskFRED upcoming near NJ (epee filter, note check-in close + staleness warning): https://www.askfred.net/tournaments
- [ ] Inbox **`efc.weekly@agentmail.to`** (AgentMail — SINGLE input channel; not Gmail). Frank emails everything, incl. his own comics: results-app slice (tournaments, entrants, results) + forwarded club newsletter + tips/thread links + comics/guest pieces. Cite by message-ID in `sources.json`; do not commit raw MIME.

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
- [ ] FIE events calendar (https://fie.org/events) — upcoming epee World Cups/satellites with dates, for Thursday previews.
- [ ] YouTube channel RSS feeds (no login; verify channel IDs at build time — FIE, USA Fencing) — "watch this bout" links.
- [ ] Newsletters by email: subscribe `efc.weekly@agentmail.to` to USA Fencing + FIE updates — arrives as input, zero scraping.

## Social verdict (tested 2026-10-06)
- X: firecrawl fails outright (login wall since 2023; free API killed, paid tiers ~$100/mo). Snippets via searxng only + forwarded links.
- Instagram: profile fetch returns app-deep-link stubs, zero post content. Same wall. Exception: our OWN @elitefencersclub posts could come via Meta Graph API with the club's own token (our data, no scraping issue) — optional later.
- Rule for all social: never a fact source; angles only, verified against Tier 1–3 before print.

## Thursday extras (signup push)
- [ ] Re-check AskFRED close times for locals with late/at-door entry
- [ ] Re-check emailed start-list slice for new Elite FC entrants since Monday
- [ ] Venue/check-in times only if on event page or in email — never guessed
