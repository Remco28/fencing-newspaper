# Fencing Newspaper — Plan v3.15
Date: 2026-10-07
Status: **sample taste LOCKED** (v3.14 sheet) + **ops cadence LOCKED** (v3.15). Reference sheet `issues/2026-10-14/` (`paper-v3.14.pdf` / `paper.pdf`, `preview-p1.png`, `preview-p2.png`). Furniture: STYLE-GUIDE §2/§8/§12. Composition/voice: §1a–1b + STYLE-GUIDE §0/§0a. **Gather loop:** STAGING.md § Ops cadence + SOURCES.md cadence header (chat anytime; email daily + pre-budget; Wed skim + Mon/Tue full pass). **Dynamic layout PAUSED** (deferred future — Template A only). Next: real Thursday edition (refine sources → HTML budget → proof). Prior: v3.14 taste lock; v3.13 ears/HRs/bylines; v3.12 Playfair + §8; v3.11 voice; v3.10 Desk.
Project folder (runner): `/workspace/fencing-newspaper` on Musketeer's computer (Grok Bot box). Frank's earlier `~/Dev/fencing-newspaper` path is historical.
Durable store: private GitHub `Remco28/fencing-newspaper` (weekly sync; push sooner after a finished issue if you care).
Work item: office work #21

## 1. What we're building (v2 locked)

1 sheet, front + back, black & white, high-school reading level.
Audience: Elite Fencers Club members (Chatham, NJ), **epee only — no foil, no saber.**

**One weekly issue** (locked 2026-10-06 evening): results + club signup encouragement on the same sheet.
- **Default publish: Monday.** Frank can override.
- **Auto-slip to Tuesday** when Elite FC members are competing on Monday (wait for those results before shipping). Dateline uses the **actual publish day** (not a forced "Monday Edition" label).
- **Thursday edition cancelled** — too much cadence for a fun side project.

Editorial control: **Frank only.** No parent/kid submissions. No coach involvement (skip coaching tips entirely).

Automation: built to run under a scheduled bot — **Grok Bot (xAI)** — once per week. V1 runs **human-verified** (Frank approves PDF before print). Auto-print enabled only once issues look right.

AI model is **swappable** by design. Template owns **rails** (geometry, type scales, patterns); Gazette Desk **composes** within them (PLAN §1a) — not a dumb field-filler.


## 1a. The product is Gazette Desk (locked 2026-10-07 — Frank)

**You (Gazette Desk, and every future version of you) are the product.** Content will arrive and Frank will approve a budget. Building the newspaper each week is *your* job.

What that means:
- After budget approval, **you compose** the sheet: hierarchy, pacing, where shorts sit, how furniture and flanks land, photo placement within locked rules. The reader should feel a custom paper made for Elite Fencers Club — all about us and the sport we’re in — carefully put together, **not** content forced into a template.
- **Template A is rails, not the paper.** Print size, 3-col grid, type scales, word budgets, and QA instruments stay frozen. Inside those rails you exercise judgment so each issue feels tailor-made.
- **Bot cooperation is vital.** Specs, STYLE-GUIDE, CONTENT-HIERARCHY, and STAGING.md exist so every future Gazette Desk shares one brief. If docs sound like “fill slots and ship,” rewrite them — the brief is compose for the reader.
- **Pleasant and fun** = club kids and parents recognize themselves; the week’s lead has weight; shorts stay shorts; ratings / who’s-entered are glanceable; something earns a laugh; dense but not cramped; old-time newspaper energy, club voice, no chrome.
- **Done is not “fits on the page.”** Mandatory loop: render → self-critique against this brief and STYLE-GUIDE → fix → re-render. Fitting is necessary; purpose-built for Elite FC is the bar.
- Frank remains sole editorial control (budget + proof gates). You do not invent facts, weapons outside epee, or layouts outside locked patterns. You *do* own taste and composition within those locks.

Canonical homes stay: CONTENT-HIERARCHY (slots/budgets) · STYLE-GUIDE (visual + composition rules) · STAGING (pipeline) · this PLAN (narrative + this role). On conflict, the home wins — and **§1a wins over any “dump into template” reading elsewhere.**


## 1b. Voice (locked 2026-10-07 — Frank)

The paper should **read like it knows it is a newsletter**: finite space, one sheet, readers scanning on a bench. That shapes every sentence.

- **Selective by default.** No padding. Prefer the exact word over the long clause. Be verbose only when the slot has room — mainly the **lead**. Shorts and boxes stay tight.
- **Reporter voice** for news, results, boards, and club notices: clear, concrete, attributed, high-school reading level. Not a blog, not a marketing blast, not a chatty bot.
- **Exceptions:** opinion, humor columns, or **guest authors** may sound like themselves (still within STYLE-GUIDE bans and epee-only facts).
- **Bylines:** only when a **real guest** wrote the piece (their name). **Never** invent house bylines (“Gazette Staff,” “Club Desk,” “Pretend Copy,” etc.). Frank has none; unsigned reporter voice is the default.
- **Tone follows the piece**, not a fixed “house personality.” Levity when the story earns it; serious or somber when it must; never force jokes onto a hard result or pad a light bit into mock-solemnity.
- Standing bans still apply (PLAN §7 / STYLE-GUIDE): no “delve,” “fast-paced world of,” “testament to,” snark-for-snark’s-sake; explain jargon on first use; headlines ≤6 words with an active verb.

Canonical home for voice = this §1b; STYLE-GUIDE §0a repeats the composition-facing brief so the weekly composer doesn’t miss it.

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
- FIE live results + rankings + event pages (e.g. Worlds results tables): https://fie.org — results are structured, good for one-line result blurbs / future headline wire.
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

## 3. Sections (v3.4 — single weekly issue; Frank sorts CONTENT-HIERARCHY.md)

Shared shell: masthead **En Garde Gazette** + descriptor "The Elite Fencers Club Weekly" (locked 2026-10-06; no "!" in the nameplate — the bang lives in headlines, not the masthead), **actual publish date** (Mon or Tue), issue #,
footer with issue # + for-fun disclaimer only (no "printed at the club"; no print timestamp — locked 2026-10-07). Bylines: none for Frank, credit guest writers.
Weighting rule: club newsletter news > national/regional tournaments > locals.
Canonical slot order + budgets: **CONTENT-HIERARCHY.md** (table order = cut priority). Summary:

**Weekly — results + signup (front / back), news-first**
1. Lead epee result of the weekend (FIE or national if big, else top NJ/club result).
2. Club results + ratings earned (always in).
3. 1–2 short national/regional articles + NJ HS roundup.
4. **Signup board (core):** upcoming tournaments + Elite FC names already entered — purpose is to nudge more clubmates into competition. Cap **4 tournaments**; if one event has many names (~20), show fewer tournaments so names stay readable (2–8 rows total).
5. Club events + deadlines box.
6. Comic (sparingly) + TV/streaming box as space allows (lowest cut priority among listed slots).

Killed: Thursday edition; logistics box; Fencing 101; Milestones; About/corrections/archive placeholders.
Killed (v3.4): **Scoreboard strip** — hard to implement well as big headlines + one-line blurbs; can revive later as "headline wire" if wanted. Not in live hierarchy.

Maybe later: advice column ("Dear Ref") — no slot yet. Low priority: recruiting notes (only if genuinely good).
Cut for v1: weather, food, travel, crossword, quiz/trivia, jokes/riddles, coaching tips, foil/saber anything, editorials, long interviews.
**Photo desk (v3.4–v3.5):** budget page shows actual image thumbnails; Frank multi-selects → `photoIncludes`. **Email media extract (v3.5):** on ingest, save MIME attachments **and** download remote/inline HTML images (skip tracking pixels, social icons, tiny logos <~80px). Store under `staging/weeks/<target>/media/` with provenance (`message_id`, url/attachment id, `from`, `vetted`). Budget desk reads that folder. First pass: 2 real JPEGs from Frank’s forwarded club newsletter; demo still keeps a few labeled PRETEND PNGs for multi-select. Feature was planned earlier; synthetic PNGs only until this pass.

## 4. Layout — Template A rails (V1); patterns TBD

**V1 ships Template A** (prototype `monday-v6` energy adapted for the single weekly issue). **Template B (Thursday) is cancelled** with the Thursday edition. Furniture locked by sample `issues/2026-10-14` (v3.14) — see STYLE-GUIDE §2/§8/§12.

Rules (rails, not a weekly redesign):
- Print geometry, type scales, word budgets, and furniture CSS are designed once, print-tested, then frozen. No generative redesign of the shell weekly.
- Content / layout split: Gazette Desk composes into `issue.json` + HTML within locked rails (PLAN §1a); Chromium/WeasyPrint renders `paper.pdf`. Schema + epee-only + word limits still bind. “Fill slots and ship” is a fail — compose for Elite FC.
- US Letter, 0.5in margins, B&W-safe: 100% black headlines, no gray text under 10pt, 1–2pt rules, SVG line art + approved B&W photo picks from photo desk.
- ~600–700 words max per issue.
- Per-issue folder: `issues/<YYYY-MM-DD>/` (publish date) with `issue.json`, `sources.json`, derived `inputs/`, `approvals.json`, `paper.pdf`. Pre-issue material lives under `staging/weeks/` — see **STAGING.md**. Raw email bodies stay in AgentMail (not in git); cite them by message-ID in `sources.json`.

**PAUSED / deferred — Layout patterns (Frank 2026-10-07):** constrained dynamic arrangement (select from a small pattern vocabulary so weeks feel alive) vs rotating 2–3 locked templates is **on pause for future consideration**. Another agent warned against unconstrained dynamism; freehand weekly invention stays banned. **Until revisited: ship Template A only.** STYLE-GUIDE §9 remains the hook for a future pattern menu. Do **not** invent layouts weekly; do **not** build the pattern vocabulary until Frank un-pauses this.

## 5. Inputs — AgentMail is the single channel (locked 2026-10-06 evening; tips/vetting v3.3)

**Inbox (locked):** `efc.weekly@agentmail.to` (display name: The Elite Fencer's Club Weekly), via the AgentMail connector — **not Gmail**. Frank's Gmail stays for other work (rentals, etc.).

**Tips / mail (locked v3.3):**
- Small public ask OK: tips & photos to `efc.weekly@agentmail.to` (editor decides).
- Only mail from `frankcng@gmail.com` is **auto-Frank-vetted**.
- Other senders → staging as **unvetted**. Unvetted items MAY appear on the budget page labeled **UNVETTED**; Include stays disabled until Frank vets them. **Primary vet UX:** budget-page **Vet + notes** (`vet_notes` stored on the item). Chat promote / forward-from-frank still OK as alternates.

**Chat → staging (locked v3.3):** When Frank tells the bot a fact/idea in chat, default target = **next weekly issue** staging unless he names another week. Materials can accumulate for subsequent weeks in advance.

Frank still sends comics and forwards to that address. The bot also does independent research per SOURCES.md. Every ingested email item recorded by AgentMail message-ID in `sources.json` / staging provenance.

1. **Results/schedule app → bot:** structured email (JSON or fixed-format body + optional PDF attach): tournament, event, day, Elite FC entrants/results → staging, then Clean → `inputs/results-<date>.json`.
2. **Club newsletter forwarded:** announcements, events, ratings → staging → `inputs/club-<date>.md`.
3. **Frank's extras / public tips:** comics, tips, photos, thread links → staging (`vetted` per rules above).

**Processed-mail labels (v3.7):** after successful ingest into staging, apply AgentMail label `processed` (do not delete). Ingest skips already-`processed` mail. Detail: **STAGING.md** § Email triage labels.

Still needed: results-app email schema, attachment cap, spam fallback = stage as unvetted + flag on budget (not silent drop of Frank-vetted mail).

**Editorial pipeline (locked v3.3):** Staging → Clean → Budget → Proof. Canonical detail + item schema + folder layout: **STAGING.md**.

**Storage (locked 2026-10-06 evening):** Working copy on Musketeer's computer at `/workspace/fencing-newspaper`. Everything except raw emails syncs to GitHub (staging, issue folders, PDFs, approvals, prototypes, specs). Raw MIME/bodies stay in AgentMail. Weekly `git push` is the baseline; optional push after a closed issue. PDFs may be archived elsewhere later for posterity — low stakes, fun project, not mission-critical. Secrets stay in `.env` on the runner, never in git.

## 6. Automation + verification

- Scheduler: once weekly. Default Monday morning (exact time TBD, US Eastern). If results-app / start lists show Elite FC members competing that Monday, **hold and publish Tuesday** after those results land (unless Frank overrides).
- **Ops cadence (locked v3.15):** chat → staging anytime; email = daily morning light pass + second pass before HTML budget; self-gather = Wed mid-week skim + publish-morning full pass. Canonical: **STAGING.md § Ops cadence** + **SOURCES.md** cadence header.
- V1 gates: **Budget → Frank approve → Desk compose → Proof → Frank approve → print.** Chat is doorbell only for budget/proof readiness. Every fact → `sources.json` provenance. Unvetted tips stay off the sheet until Frank vets. No auto-print until approved.
- Later: `lp -d club-printer paper.pdf` auto-print after N clean issues.
- API keys live in env file on the runner, never in git. Allowlisted inbox only.

## 7. Style — see STYLE-GUIDE.md (authoritative; voice home PLAN §1b)
Visual rules (3-col grid, no heading symbols, no print chrome, alignment, fill rule, visual QA)
live in STYLE-GUIDE.md. **Voice:** PLAN §1b + STYLE-GUIDE §0a (newsletter-aware, selective, reporter default; tone matches the piece). Still true:
- High-school reading level (FK 8–10). Explain jargon first use. Epee terms only.
- Headlines ≤6 words, active verb. Full name + event + club on first local mention.
- Ban list: "delve", "fast-paced world of", "testament to", snark.
- Masthead/footer identical across issues; Vol/No + date live in the **dateline**; flanks = publisher line + rotating quip; footer = issue # + for-fun disclaimer only (+ template variant if we add more later).

## 8. Resolved in v2 / still open

Resolved:
- [x] Epee only
- [x] **One weekly issue** (Thursday edition cancelled 2026-10-06)
- [x] Default Monday publish; auto-slip Tuesday if club fencing Monday; Frank can override
- [x] Dateline = actual publish day
- [x] Signup board is core (max 4 tournaments; names first; encourage competition)
- [x] Logistics box / About-archive placeholders / Fencing 101 / Milestones killed for now
- [x] Email inputs (results app + forwarded club mail) via AgentMail
- [x] No coaching tips, coach not involved
- [x] Frank-only editorial (public tips OK but unvetted until Frank vets)
- [x] Template A first; no Template B (Thursday cancelled). **PAUSED/deferred:** constrained dynamic / multi-template menu — see §4 (Template A only until Frank un-pauses)
- [x] Swappable model
- [x] Human-verified first, auto-print later
- [x] Reddit verdict: search-discovery only
- [x] Paper name — En Garde Gazette / The Elite Fencers Club Weekly (locked)
- [x] V1 section lineup in CONTENT-HIERARCHY.md (table order = priority)
- [x] Template A prototype through v6 + locked visual rules (STYLE-GUIDE.md)
- [x] Inbox — AgentMail `efc.weekly@agentmail.to` (not Gmail)
- [x] Storage — box working copy + GitHub sync; everything except raw emails
- [x] Pipeline names — Staging → Clean → Budget → Proof (STAGING.md)
- [x] Tips — public ask to inbox OK; only `frankcng@gmail.com` auto-vetted; others unvetted until Frank promotes
- [x] Chat facts/ideas → next-week staging by default (named week override OK)
- [x] Budget page may show unvetted labeled; include blocked until vetted
- [x] Folder layout proposal — `staging/weeks/<YYYY-MM-DD|next>/` + `issues/<YYYY-MM-DD>/` (STAGING.md)
- [x] Article size-by-importance — slot word budgets + per-slot template type scale (STYLE-GUIDE §4/§11; CONTENT-HIERARCHY); stretch/cut hierarchies live (v3.7)
- [x] AgentMail processed-mail triage — label `processed` after successful ingest; never delete (STAGING.md; v3.7)
- [x] Masthead flanks + dateline swap (v3.8 origin) — **superseded by v3.12–v3.14 taste lock** (STYLE-GUIDE §12)
- [x] Photo fit — no silent crop; soft ~2.2in tall flag (STYLE-GUIDE §19; v3.9)
- [x] Production dateline — SAMPLE removed (v3.9); **final form (v3.12):** centered Playfair Display SC edition word (`Tuesday Edition` / `Page Two`) + Caslon meta line; double top / solid bottom — **not** three-span Arial (STYLE-GUIDE §2/§12)
- [x] Voice — newsletter-aware, selective word choice, reporter default; tone matches the piece (PLAN §1b; STYLE-GUIDE §0a; v3.11)
- [x] §8 borders — **only** tabular `.box` boards; prose = `.rail-block` + `.rail-title` (no title underline); never wrap article-shaped copy in `.box` (v3.12–v3.14)
- [x] Flanks as newspaper ears — Caslon/Times, hairline top+bottom, clear air from masthead logo; left fixed publisher line; right rotating quip from `flank-quotes.json` (v3.13–v3.14)
- [x] No horizontal rules between page-2 article bands; no fake Gazette Staff bylines — guests only (v3.13–v3.14; PLAN §1b)
- [x] **Sample taste locked** — `issues/2026-10-14/` (`paper-v3.14.pdf`) is the authoritative visual reference (Frank 2026-10-07)
- [x] **Ops cadence locked (v3.15)** — chat anytime → next week; email daily + pre-budget; Wed skim + Mon/Tue full gather; Budget→approve→compose→Proof→approve→print; `sources.json`; chat doorbell only (STAGING.md + SOURCES.md)

Still open:
1. Exact Monday run time (proposal ~6am US Eastern) + Tuesday slip publish time.
2. How we detect "members competing Monday" reliably (results-app fields / AskFRED).
3. Results-app email schema (tournament, event, day, entrants, results, source IDs).
4. Printer model + who loads paper.
5. Optional later: archive older PDFs outside git for posterity (not required).
6. Exact staging on-disk filenames (`items.jsonl` vs `items/*.json`) when ingest ships — layout tree is locked; leaf names flexible.
7. **Layout patterns (PAUSED / deferred future):** constrained dynamic vs 2–3 locked templates — see §4. Not active work. Template A only; do not invent weekly layouts.

Canonical homes: CONTENT-HIERARCHY.md owns slot order + budgets · STYLE-GUIDE.md owns all
visual rules · SOURCES.md owns the fetch checklist (+ cadence header) · **STAGING.md owns
pipeline + item schema + folder layout + ops gather loop** · SECTIONS-MENU.md is the
option menu + past verdicts · PLAN owns narrative + decisions. On conflict, the
canonical home wins.

## 9. Next steps
- [x] Lock name (En Garde Gazette) + v1 lineup (CONTENT-HIERARCHY.md)
- [x] Build template A (Monday results) HTML/CSS, B&W test render
- [x] Lock inbox address (AgentMail `efc.weekly@agentmail.to`) + box/GitHub storage
- [x] Cancel Thursday edition; lock single weekly Mon/Tue slip rule
- [x] Lock Staging→Clean→Budget→Proof + tips vetting + chat→staging (STAGING.md)
- [ ] Confirm Monday run time + Tuesday slip time with Frank
- [ ] Define results-app email schema + Monday-competitor detection fields
- [ ] Adapt Template A for single weekly issue (signup board as core); no Template B
- [ ] Build fetch per SOURCES.md checklist + email-ingest → staging (per-source degrade behavior)
- [x] Budget demo: photo desk thumbs + multi-select; submit → timestamped + approvals.json (pretend)
- [x] Email media extract first pass: remote HTML images → `staging/weeks/next/media/` + manifest; budget desk shows real + PRETEND (v3.5)
- [x] Budget demo (v3.6): UNVETTED badge + Vet+notes on page; Include gated; POST `/vet` → items.json + vet-log
- [x] Docs v3.7: lock per-slot article size + refresh stretch/cut hierarchy; AgentMail `processed` labels (STAGING.md)
- [x] Docs + sample v3.8: masthead flanks (publisher + rotating quip) / dateline (Vol/No · place · weekday · date); `flank-quotes.json`
- [x] Docs + sample v3.9: photo no-crop; production dateline; per-slot type scale on `issues/2026-10-14` (Template A only — no alternate layouts this pass)
- [x] Docs v3.10: Gazette Desk is the product — compose-for-Elite-FC brief (§1a); STYLE-GUIDE §0 composition bar
- [x] Docs v3.11: voice — newsletter-aware / selective / reporter default; tone matches piece (§1b, STYLE-GUIDE §0a)
- [x] AskFRED API — Bearer in `ASKFRED_API_KEY` (secret/.env); gentle use for NJ epee tournament search (SOURCES.md)
- [x] Sample v3.11 taste: flanks + 3-span dateline + page-2 featured hierarchy on `issues/2026-10-14` (paper-v3.11.pdf)
- [x] Sample v3.13: serif masthead ears; page-2 article HRs removed; fake bylines stripped (`paper-v3.13.pdf`)
- [x] **Sample v3.14 taste LOCKED** (Frank): dateline + flanks + §8 rail-title + no page-2 article HRs; docs match; reference `issues/2026-10-14/paper-v3.14.pdf`
- [ ] **Real Thursday edition** (next): refine source processing → HTML budget → proof render (complete run when ready)
- [x] Docs v3.15: ops cadence locked (STAGING.md gather loop + SOURCES.md cadence header); dynamic layout marked PAUSED/deferred (§4)
- [ ] Layout patterns (§4) — **paused**; revisit later only if Frank asks (Template A only until then)
- [ ] Budget page (prod): same vet UX + write issue approvals.json
- [x] Template CSS sample: flanks + dateline + photo fit + slot type scale on `issues/2026-10-14`
- [ ] 2 dry-run weekly issues with Frank red-pen, then enable scheduled bot
- [ ] See also: STAGING.md, SOURCES.md, SECTIONS-MENU.md, REDDIT-SETUP.md

## 10. Approval design (locked 2026-10-06; unvetted rule v3.3; photo desk v3.4; email media extract v3.5; Vet+notes v3.6)
- Primary: LOCAL budget page on Musketeer's computer (Grok Bot box). Stories + **Photo desk**
  with visible B&W-as-printed thumbnails and Include checkboxes (multi-select → `photoIncludes`).
  Slot include checkboxes for the lineup. **Only vetted items can be included** in the issue
  lineup; unvetted tips/photos appear labeled **UNVETTED** with Include disabled until Frank
  hits **Vet** and (strongly encouraged) adds notes for the bot. Chat promote remains an
  alternate. Demo: `POST /vet` updates `staging/weeks/next/items.json` + `vet-log.jsonl`.
  Submit POSTs JSON → timestamped `submissions/budget-*.json` AND overwrites
  `submissions/approvals.json` (demo) / issue `approvals.json` (prod). Frank works on desktop, never phone.
- Chat is DOORBELL only: the bot pings "budget ready" / "proof ready" — no approval state
  lives in chat (chat fragments across messages and forces scroll-to-reference; rejected as
  a surface). Chat *facts* still go to staging (see STAGING.md).
- Google Form rejected: static templates can't show per-issue photos without regenerating
  the form each time, or force blind approvals.
- Two gates always: (1) approve the budget, (2) approve the rendered proof. Nothing prints
  otherwise. Missed message = skipped week, which is fine (low stakes, just for fun).
- Reversal = re-render from a previous `approvals.json`. Every render records which file it used.
- Pipeline detail: **STAGING.md**.
