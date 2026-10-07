# Self-gather test log — 2026-10-07 (publish-morning style)

**Pass type:** Timed test of SOURCES.md “Every run / publish-morning” checklist  
**AskFRED API:** not available — used AskFRED web browse + FencingTracker + search only  
**Budget/PDF:** not built (per brief)  
**Existing staging:** preserved (incl. `chat-remise-anderson-app` and pretend seeds)

## Timing (honest)

| Measure | Value |
|--------|--------|
| Box stopwatch (`gather-start` → staging write) | **~73 seconds** wall clock |
| Felt effort (reading, epee-filter, judgment) | **Light — ~15–25 min** desk job if done without racing |
| Vs locked estimate (30–60 min full pass) | **Under** — parallel RSS/HTML fetches + degrade-and-move-on worked |
| Token / context pain | **Moderate** — Google News RSS returns huge noisy dumps; USA Fencing `/news/epee` page is stale (2020–2024) |

**Cadence verdict:** Leave Wed skim + publish-morning full pass as locked. Full pass is manageable; pain is AskFRED filtering without API and RSS noise, not source count.

## Checklist results

| Source | Status | Notes |
|--------|--------|-------|
| FIE news (`fie.org/news`) | OK | Soft news (podcasts, Asian Games education stands, Youth Olympics). No hard epee result headline for *this* week. |
| FIE events calendar | OK (light) | Casablanca WC **Oct 15–18** confirmed; also Lima WC Oct 8–11, Oran/Takamatsu same weekend as Casablanca. |
| USA Fencing epee feed | **Degraded** | `/news/epee` still showing 2024 Olympics-era posts. Used `/2026-october-nac` event page instead for actionable national copy. |
| NJ.com HS fencing | OK / offseason | Boys hub live; content is Mar 2026 state individuals / All-State. **No fresh Oct duals** — staged ops note, not a print lead. |
| AskFRED upcoming near NJ (epee) | **Painful / partial** | Browse page works nationally (saw October NAC Oct 9–12). **Could not reliably filter NJ + epee + upcoming** from HTML. Old Medeo events (e.g. 2008 “October Sky”) still indexed by search. Staleness warning: treat AskFRED search-engine hits as suspect without API. |
| Google News RSS `fencing+epee` | OK (noisy) | Best juice detector. Recent: Casablanca preview (Oct 5), college duals, Asian Games epee (late Sep), Shamel NCAA title **republication** (event was Mar 22). |
| Google News RSS + NJ | OK / stale for Oct | Mostly Jan–Mar 2026 HS season. Useful Dec–Mar; skip for early-Oct print. |
| FencingTracker (light) | OK | Medeo registrations show October NAC + Morris Cup RYC Oct 25. Elite FC club URL 404’d this pass — skip inventing club results. |
| Inbox AgentMail | Skipped this test | Not part of self-gather timer; email is separate daily/pre-budget pass. |

## Staged (new) — 6 items

All `vetted: false`. Appended; nothing wiped.

| id | Role |
|----|------|
| `gather-october-nac-orlando` | National / TV / deadlines — **Oct 9–12 Orlando** |
| `gather-casablanca-epee-wc` | International / TV — **Oct 15–18** |
| `gather-asian-games-song-sera-epee` | International short (1–2 wks old) |
| `gather-morris-cup-ryc-oct25` | Nearby regional signup (Suffern NY) |
| `gather-college-path-shamel-epee` | Optional college-path color (Mar event; RSS noise) |
| `gather-njhs-offseason-note` | Ops note — not a print candidate |

**Already in pile (not from this gather):** `chat-remise-anderson-app` (Frank), Medeo signup, Ben Gutenberg SYC results, club events, photos, pretend demo seeds.

## Failures / blocks

1. **USA Fencing epee news feed stale** — do not trust as “what’s new this week.”
2. **AskFRED without API** — cannot cheaply answer “epee tournaments near NJ with check-in/close times.” Browse dump + search returned national noise and archaic pages.
3. **FencingTracker Elite FC club page** — 404 this run; no club result scrape.
4. **Google News article URLs** — opaque `news.google.com/rss/articles/...` redirects; prefer canonical Tier-1 URLs when staging print copy.
5. **Shamel “Oct 3” RSS date** — republication of March NCAA title; easy to mis-stage as fresh if not checking event date.

## Where AskFRED API would cut work

- Filter `state=NJ` (or radius from Chatham) + `weapon=Epee` + `status=upcoming` in one call.
- Pull **registration close / check-in** for deadlines + signup board without HTML archaeology.
- Resolve “Who’s Coming?” for Elite FC / Medeo neighbors without FencingTracker crosswalk.
- Avoid false positives from decade-old tournament pages still in the public index.

Until then: AskFRED browse for big nationals (NAC) + FencingTracker for regional entry lists + Frank/results-app for club names.

## Top Thursday candidate headlines (editorial pick, not budgeted)

1. **Club parent ships Remise fencing journal** (`chat-remise-anderson-app`) — local, Frank-vetted, unique to Elite FC.
2. **October NAC opens in Orlando this weekend** (`gather-october-nac-orlando`) — national pulse + watch/deadline furniture.
3. **Casablanca Senior Epee World Cup next week** (`gather-casablanca-epee-wc`) — international / TV box.

Honorable: Ben Gutenberg SYC club results + Medeo Youth Challenge signup (already staged from Frank) — those still beat Asian Games/Shamel for *our* readers unless Frank wants an international short.

## Bottom line for Frank

Self-gather is **viable at the locked cadence**. This test was easy when we parallelize and degrade. The bottleneck is **AskFRED local epee discovery** (API would help a lot) and **RSS noise**, not “too many sources.” Ready to refine sources and move toward a real Thursday lineup when you say go.
