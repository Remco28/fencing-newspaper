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

---

## Feature gather — NJ high school season primer (2026-10-07, ~3:50 PM ET)

**Trigger:** Frank chat request (wants an NJ HS fencing season explainer; has never done HS fencing).  
**Staged:** `gather-nj-hs-season-primer` (`kind: graf`, `suggested_slot: lead_or_feature`, **vetted: false**) · draft `drafts/nj-hs-season-primer.md` · 447w body + 6-row "Season at a glance" sidebar · 23 provenance URLs.

| Source | Status | Notes |
|--------|--------|-------|
| NJSIAA fencing page | OK | 2026–27 dates published (tryouts Nov 23–25, practice Nov 30, competition Dec 7, team rounds Feb 9–23, finals Feb 25 Morris Hills, individuals Feb 27 Hunterdon Central). |
| NJSIAA PDFs (2025–26 regs, regular-season rules, quick chart, minutes, restructure memo) | OK | **2026–27 tournament regs not posted yet** — site still links 2025–26. Districts dropped 2025–26 (2-yr pilot); top 36/weapon via Touch By Touch; 50% rule + TbT qualifying flagged for revision in Mar 31, 2026 minutes. |
| NJ.com HS fencing | **Partial** | WebFetch + curl blocked (JS wall). Facts taken from search-index snippets of NJ.com articles (Santelli/Cetrulo 2026, state finals 14-13, individuals Mar 7, 2026). Frank may want to click-verify. |
| NJIFA (coaches assoc.) Google Site | OK / possibly stale | Confirms NJIFA organizes Cetrulo (boys) + Santelli (girls); officer list dated 2022–25. |
| USA Fencing | OK | Parent explainers (pools 5-touch; DE 15-touch, 3×3 min) + rulebook; LinkedIn post "95th Cetrulo / 45th Santelli … largest and oldest". |
| Dual-meet format | OK (secondary) | No NJSIAA doc spells out 3×3×27; sourced via NJSIAA "NCAA rules govern" + "all 27 bouts must be contested" (2024 minutes) + Montgomery HS guide (docest mirror) + Community News 2007. |
| newjerseyhills.com | OK | Chatham boys 7th / girls 5th straight Morris County titles (2026). |

**Kept out of print (unverified/conflicting):** NJ HS fleche/crossover ban (old sources say banned; a 2026 Reddit thread says dropped — not in NJSIAA docs) · whether HS bouts affect USA Fencing ratings (no source found) · 2027 Santelli/Cetrulo and Morris County dates (not published) · Cetrulo/Santelli edition numbers (Drew 2019 "40th" vs USA Fencing/NJ.com "95th Cetrulo / 45th Santelli" in 2026). Also: 2025–26 regs listed finals Feb 26, 2026 but NJ.com reports they were fenced Fri Feb 27, 2026 (NJSIAA "play-by" dates can move by mutual agreement).

## Staging moves (2026-10-07 evening)
- **THE WEAPON** (`chat-asset-weapon-epee`) moved `next/` → `after-next/` — Frank: hold for the week after next issue (still span 2).
- **NJ HS primer photo** (`chat-photo-nj-hs-dual-meet-morris-hills`) staged under `next/media/nj-hs-dual-meet-morris-hills.png` (+ bw JPEG) for `gather-nj-hs-season-primer`.

---

## Sidebar gather — NJ HS flèche rule (2026-10-07, ~4:22 PM ET)

**Trigger:** Frank chat (t28u) — wants a side story on the flèche rule for the HS primer; pasted a Gemini answer. **Gemini = lead list only, not a source.**
**Staged:** `gather-nj-hs-fleche-rule` (`kind: graf`, `suggested_slot: sidebar_to_feature`, `for_item: gather-nj-hs-season-primer`, **vetted: false**) · draft `drafts/nj-hs-fleche-rule.md` · 190w body · 13 source URLs + 3 corroboration-only.

| Source | Status | Notes |
|--------|--------|-------|
| NJSIAA current fencing page + 2025–26 regs/rules | OK | "NCAA Rules shall govern"; tournament regs add "any NJSIAA modifications" — none posted. No flèche text. 2026–27 regs not up yet. |
| NJSIAA archived docs (Wayback) | **Partial** | 2014–15 "Fencing Guidelines" (Dec 2014): "NO fleching is permitted" — **primary proof of ban** (also spells out 27-bout dual meet → useful for primer). Archived fencing pages show "Fencing Modifications" PDFs for 2015-16, 2016-17, 2017-18, 2019-20 — **none of those PDFs were captured**. Wayback was flaky (timeouts; retries needed). |
| NJSIAA 2021–22 Constitutional Rules / 2022–25 rules | OK | Keep old mods (3-min bouts, coin-toss priority, S2000, weights) but **no flèche clause** → limit gone by 2021–22. |
| NJIFA coaches' minutes (Google Docs off njifa2 site) | OK | Mar 8, 2017: crossover rule debated (safety, cramped gyms, coach beside strip hit by a flèche at State Squads; "get the rule renewed"). Fall 2017: "no two crossover steps before the touch … running attacks disallowed / garden variety fleche is perfectly fine." No flèche items 2018–2023. |
| NCAA 2025–26 pre-champs manual | OK | USFA rules in effect Oct 1 govern; Appendix C has no flèche change. |
| USA Fencing Rules (Oct 2025) | OK | t.26.2 running flèche not forbidden; t.26.1/t.121.2 jostling flèche penalized; t.101.5 sabre forbids flèche/forward cross. |
| Reddit r/Fencing | Search snippets only (box blocked) | 2016 thread quotes NJSIAA 2016-17 pilot text incl. "first group offense … touch annulled" — **only source for the penalty → kept out**. 2022 thread: "since the 1980s" (one commenter) → kept out. |
| NJ.com / news | None found | No coverage of the change surfaced. |

**Verdicts on Gemini:** no-longer-banned ✔ (caveat: 2026–27 unposted) · sabre ✔ · ban 1980s–mid-2010s: ban ✔ as of 2014, start date ✘ unverifiable · rationale: safety debate ✔ in 2017, liability/gym-floor/broken-blade specifics ✘ Gemini-only · c.2016 one-crossover ✔ (2016–17 pilot) · Group 1/annul ⚠ Reddit-quote only · "fully phased out" ✔ as current state, **year unknown (2018–2021 window)** · corps-à-corps rules apply ✔.
