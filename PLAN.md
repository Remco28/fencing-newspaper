# Fencing Newspaper — Plan v3.29
Date: 2026-10-07
Status: **Frank's hierarchy answers** (v3.28: no fixed lengths; Overheard only when good; Deadlines every issue next to the local board; "Go Cheer" renamed **"Nearby Tournaments"** (v3.29); "For the Parents" final; Dear Ref folded/dropped) + **CONTENT-HIERARCHY reviewed** (v3.27: renumbered, sources updated, standing elements + planned features split out, open questions listed) + **"For the Parents" recurring box** (v3.26: one practical item for non-fencing parents per issue; start issue open) + **"By the Book" recurring section** (v3.25: one USA Fencing rule/penalty per issue; awaiting Frank's material) + **FencingTracker recurring source** (v3.24: daily club-page look, Wed skim, Monday full sweep — SOURCES.md § FencingTracker) + **results tone LOCKED** (v3.23: strong finishes only, others "also fenced" — STYLE-GUIDE §0d) + **X as a lead source** (v3.22: read-only `x` tools, vetted list `sources/x-accounts.md`, rules in SOURCES.md § X) + **budget page v2** (v3.21: 1280×800 reading layout, questions for Frank, `answers` in submit) + **sample taste LOCKED** (v3.14) + **ops cadence LOCKED** (v3.15; wording v3.19) + **reality/provenance LOCKED** (v3.16) + **email trust allowlist LOCKED** (v3.17) + **Parent Q&A category LOCKED** (v3.18) + **flexible weekly publish LOCKED** (v3.19) + **first-real-run decisions LOCKED** (v3.20: epee-assumed labels, content-heavy cut order, proof round). **Issue No. 1 published** (`issues/2026-10-08/`, Thursday Edition, approved by Frank 2026-10-07 18:40 ET). Reference sheet `issues/2026-10-14/` (`paper-v3.14.pdf` / `paper.pdf`, `preview-p1.png`, `preview-p2.png`). Furniture: STYLE-GUIDE §2/§8/§12. Composition/voice: §1a–1b + STYLE-GUIDE §0/§0a. **Gather loop:** STAGING.md § Ops cadence + SOURCES.md cadence header (chat anytime; email daily + pre-budget; Wed skim + publish-morning full pass). **Dynamic layout PAUSED** (deferred future — Template A only). Next: Issue No. 2 (week of Oct 12; THE WEAPON at span 2). Prior: v3.20 first-real-run decisions; v3.19 drop Mon/Thu split / flexible weekly; v3.18 Parent Q&A; v3.17 email trust; v3.16 reality lock; v3.14 taste lock.
Project folder (runner): `/workspace/fencing-newspaper` on Musketeer's computer (Grok Bot box). Frank's earlier `~/Dev/fencing-newspaper` path is historical.
Durable store: private GitHub `Remco28/fencing-newspaper` (weekly sync; push sooner after a finished issue if you care).
Work item: office work #21

## 1. What we're building (v2 locked)

1 sheet, front + back, black & white, high-school reading level.
Audience: Elite Fencers Club members (Chatham, NJ), **epee only — no foil, no saber.** Because epee is assumed, club material never carries “Epee” / “(Epee)” labels (box titles, table headings, our fencers’ event names) — keep the word only for outside-world multi-weapon stories, proper names, and contrasts (STYLE-GUIDE §0c, v3.20). Frank will say if foil or sabre is ever added.

**One weekly newsletter** (locked 2026-10-06; clarified v3.19): results + club signup encouragement on the same sheet. No Monday/Thursday split; no second edition.
- **Target publish: Monday or Tuesday.** Later in the week is fine — not much changes; no rule broken.
- **Soft preference:** if Elite FC members are fencing Monday, holding for those results is nice when easy — not required.
- Dateline uses the **actual publish day** (`<Weekday> Edition` — not a forced Monday label). Historical note: a Thursday signup edition was tried and dropped 2026-10-06.

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


## 1c. Reality lock — invent nothing on real issues (locked 2026-10-07 — Frank)

Sample / layout-test fiction was OK while we were tuning the sheet. **Real issues are different.** This paper names real people (kids, parents, clubmates). Copy must be anchored to sourced reality.

- **No invention** of names, results, ratings, dates, entries, quotes, injuries, opinions attributed to real people, or “helpful” color that didn’t come from a source. Paraphrase OK; fabricating is not.
- **Every printed fact** needs provenance: staging item + issue `sources.json` (URL + retrieved date, or email/chat message-ID + date, or AskFRED/API call logged). No **model memory** as a source.
- **Sample / pretend / demo** content (layout tests, PRETEND photos, fake boards) must stay **clearly labeled** and **never** treated as real club or competition fact when building a real issue.
- Editorials, shorts, flanks, and furniture that mention real people follow the same rule — tone can vary (PLAN §1b); facts cannot.
- **Club roster** (`roster/people.json`): Frank-confirmed name variants + family links only, each with provenance. Clean normalizes print names from it. Minors — names/aliases/relations only; never print the roster as a list.

Canonical detail: this §1c + §2 Sourcing rules; STAGING.md (provenance on items); STYLE-GUIDE §0b for the compose checklist; `roster/README.md`.

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
- **Reality lock (v3.16 / §1c):** real issues invent nothing. Names, results, ratings, dates, entries, quotes, and any claim about a real person come from fetched/emailed/chat-staged sources — **never model memory**.
- Scores, names, signup lists come from fetched/emailed sources, never model memory.
- Every issue keeps `sources.json` (URL + retrieved date, or email/chat message-ID + date, or logged API/fetch). Every staging item carries enough provenance to rebuild that entry.
- **Sample / pretend / demo** material is labeled as such and is layout-only; do not promote it into a real issue as fact.
- Foil/saber items are dropped at fetch time, not rewritten.

## 3. Sections (v3.4 — single weekly issue; Frank sorts CONTENT-HIERARCHY.md)

Shared shell: masthead **En Garde Gazette** + descriptor "The Elite Fencers Club Weekly" (locked 2026-10-06; no "!" in the nameplate — the bang lives in headlines, not the masthead), **actual publish date**, issue #,
footer with issue # + for-fun disclaimer only (no "printed at the club"; no print timestamp — locked 2026-10-07). Bylines: none for Frank, credit guest writers.
Weighting rule: club newsletter news > national/regional tournaments > locals.
Canonical slot order + budgets: **CONTENT-HIERARCHY.md** (table order = cut priority). Summary:

**Weekly — results + signup (front / back), news-first**
1. Lead epee result of the weekend (FIE or national if big, else top NJ/club result).
2. Club results + ratings earned (always in).
3. 1–2 short national/regional articles + NJ HS roundup.
4. **Signup board (core):** upcoming tournaments + Elite FC names already entered — purpose is to nudge more clubmates into competition. Cap **4 tournaments**; if one event has many names (~20), show fewer tournaments so names stay readable (2–8 rows total).
5. Club events + deadlines box.

**Content-heavy weeks (v3.20):** standing/utility boxes give way to stories — drop the regular Weekly Classes table (changed/special class → one-line note), shrink tournament boards to the nearest/most important events + Elite FC entries, trim other utility boxes, then cut stories. Page 1 vs page 2 stays flexible. Canonical order: CONTENT-HIERARCHY “Cut (when long)”.
6. Comic (sparingly) + TV/streaming box as space allows (lowest cut priority among listed slots).

Killed: second (Thursday) edition; logistics box; Fencing 101; Milestones; About/corrections/archive placeholders.
Killed (v3.4): **Scoreboard strip** — hard to implement well as big headlines + one-line blurbs; can revive later as "headline wire" if wanted. Not in live hierarchy.

**For the Parents** (name final v3.28; v3.26, Frank call 2026-10-13 08:07 ET): standing box for parents who don't fence — one practical item per issue (a fencing term decoded, a tournament tip, or what to expect at an event). Unlike Parent Q&A (answers real questions parents ask), this is a proactive topic. Start issue not assigned; no content staged. CONTENT-HIERARCHY row 9b (position provisional; Frank sorts).

**Lengths (v3.28, chat: Frank 2026-10-13):** no fixed section lengths — length follows content quality; CONTENT-HIERARCHY sizes are rough guides only.

**By the Book** (v3.25, Frank call 2026-10-13): recurring short snippet from the USA Fencing rulebook and penalty guide, one rule or penalty per issue; random pick by default, or the relevant penalty when something specific happened that week. Built only from Frank's own source material (rulebook / penalty-guide apps) once he shares it; name kept despite possible future book content on the club site (Frank's call). CONTENT-HIERARCHY row 9a.

**Parent Q&A** locked v3.18 (CONTENT-HIERARCHY + STYLE-GUIDE §8a + STAGING `kind: qa`). "Dear Ref" (a Desk suggestion) folded into By the Book / dropped, pending Frank (v3.28). Low priority: recruiting notes (only if genuinely good).
Cut for v1: weather, food, travel, crossword, quiz/trivia, jokes/riddles, coaching tips, foil/saber anything, editorials, long interviews.
**Photo desk (v3.4–v3.5):** budget page shows actual image thumbnails; Frank multi-selects → `photoIncludes`. **Email media extract (v3.5):** on ingest, save MIME attachments **and** download remote/inline HTML images (skip tracking pixels, social icons, tiny logos <~80px). Store under `staging/weeks/<target>/media/` with provenance (`message_id`, url/attachment id, `from`, `vetted`). Budget desk reads that folder. First pass: 2 real JPEGs from Frank’s forwarded club newsletter; demo still keeps a few labeled PRETEND PNGs for multi-select. Feature was planned earlier; synthetic PNGs only until this pass.

## 4. Layout — Template A rails (V1); patterns TBD

**V1 ships Template A** (prototype `monday-v6` energy adapted for the weekly issue). One template only — no Template B / second-edition shell. Furniture locked by sample `issues/2026-10-14` (v3.14) — see STYLE-GUIDE §2/§8/§12.

Rules (rails, not a weekly redesign):
- Print geometry, type scales, word budgets, and furniture CSS are designed once, print-tested, then frozen. No generative redesign of the shell weekly.
- Content / layout split: Gazette Desk composes into `issue.json` + HTML within locked rails (PLAN §1a); Chromium/WeasyPrint renders `paper.pdf`. Schema + epee-only + word limits still bind. “Fill slots and ship” is a fail — compose for Elite FC.
- US Letter, 0.5in margins, B&W-safe: 100% black headlines, no gray text under 10pt, 1–2pt rules, SVG line art + approved B&W photo picks from photo desk.
- ~600–700 words max per issue.
- Per-issue folder: `issues/<YYYY-MM-DD>/` (publish date) with `issue.json`, `sources.json`, derived `inputs/`, `approvals.json`, `paper.pdf`. Pre-issue material lives under `staging/weeks/` — see **STAGING.md**. Raw email bodies stay in AgentMail (not in git); cite them by message-ID in `sources.json`.

**PAUSED / deferred — Layout patterns (Frank 2026-10-07):** constrained dynamic arrangement (select from a small pattern vocabulary so weeks feel alive) vs rotating 2–3 locked templates is **on pause for future consideration**. Another agent warned against unconstrained dynamism; freehand weekly invention stays banned. **Until revisited: ship Template A only.** STYLE-GUIDE §9 remains the hook for a future pattern menu. Do **not** invent layouts weekly; do **not** build the pattern vocabulary until Frank un-pauses this.

## 5. Inputs — AgentMail is the single channel (locked 2026-10-06 evening; tips/vetting v3.3; trust allowlist v3.17)

**Inbox (locked):** `efc.weekly@agentmail.to` (display name: The Elite Fencer's Club Weekly), via the AgentMail connector — **not Gmail**. Frank's Gmail stays for other work (rentals, etc.).

**Tips / mail (locked v3.3; allowlist v3.17):**
- Small public ask OK: tips & photos to `efc.weekly@agentmail.to` (editor decides).
- **Flexible ingest:** do not reject unknown apps/bots/newsletters — stage with provenance; content may come from Frank, other apps, other bots, club mail, etc.
- **Auto-vetted allowlist** (same as Frank — `vetted: true` on ingest): `frankcng@gmail.com`, `chunkymonkey@agentmail.to` (Frank’s other bot), `elitefencersclub@111617670.mailchimpapp.com` (club-owner Mailchimp). Detail: **STAGING.md § Tips / mail**.
- Other senders → staging as **unvetted**. Unvetted items MAY appear on the budget page labeled **UNVETTED**; Include stays disabled until Frank vets them. **Primary vet UX:** budget-page **Vet + notes** (`vet_notes` stored on the item). Chat promote / allowlist-sender mail still OK as alternates.

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

- Scheduler: once weekly. **Try Monday or Tuesday** (exact time TBD, US Eastern). Publishing later is OK. Soft preference only: hold for Monday club results when easy.
- **Ops cadence (locked v3.15; wording v3.19):** chat → staging anytime; email = daily morning light pass + second pass before HTML budget; self-gather = Wed mid-week skim + publish-morning full pass. Canonical: **STAGING.md § Ops cadence** + **SOURCES.md** cadence header.
- V1 gates: **Budget → Frank approve → Desk compose → Proof → Frank approve → print.** Proof round in practice (v3.20): proof v1 → Frank’s answers → v2 (…) → approval → **Frank prints the PDF himself**. Proof status lives in `issue.json`. Detail: STAGING.md § Proof. Chat is doorbell only for budget/proof readiness. Every fact → `sources.json` provenance. Unvetted tips stay off the sheet until Frank vets. No auto-print until approved.
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
- [x] **One weekly newsletter** (no Mon/Thu split; Thursday edition dropped 2026-10-06)
- [x] Target Mon/Tue publish; later OK (v3.19); soft preference to hold for Monday club results when easy
- [x] Dateline = actual publish day (`<Weekday> Edition`)
- [x] Signup board is core (max 4 tournaments; names first; encourage competition)
- [x] Logistics box / About-archive placeholders / Fencing 101 / Milestones killed for now
- [x] Email inputs (results app + forwarded club mail) via AgentMail
- [x] No coaching tips, coach not involved
- [x] Frank-only editorial (public tips OK but unvetted until Frank vets)
- [x] Template A only (no second-edition Template B). **PAUSED/deferred:** constrained dynamic / multi-template menu — see §4 (Template A only until Frank un-pauses)
- [x] Swappable model
- [x] Human-verified first, auto-print later
- [x] Reddit verdict: search-discovery only
- [x] Paper name — En Garde Gazette / The Elite Fencers Club Weekly (locked)
- [x] V1 section lineup in CONTENT-HIERARCHY.md (table order = priority)
- [x] Template A prototype through v6 + locked visual rules (STYLE-GUIDE.md)
- [x] Inbox — AgentMail `efc.weekly@agentmail.to` (not Gmail)
- [x] Storage — box working copy + GitHub sync; everything except raw emails
- [x] Pipeline names — Staging → Clean → Budget → Proof (STAGING.md)
- [x] Tips — public ask to inbox OK; auto-vet allowlist = Frank Gmail + chunkymonkey + club Mailchimp (v3.17); others stage unvetted (never reject unknown apps/bots)
- [x] Chat facts/ideas → next-week staging by default (named week override OK)
- [x] Budget page may show unvetted labeled; include blocked until vetted
- [x] Folder layout proposal — `staging/weeks/<YYYY-MM-DD|next>/` + `issues/<YYYY-MM-DD>/` (STAGING.md)
- [x] Article size-by-importance — slot word budgets + per-slot template type scale (STYLE-GUIDE §4/§11; CONTENT-HIERARCHY); stretch/cut hierarchies live (v3.7)
- [x] AgentMail processed-mail triage — label `processed` after successful ingest; never delete (STAGING.md; v3.7)
- [x] Masthead flanks + dateline swap (v3.8 origin) — **superseded by v3.12–v3.14 taste lock** (STYLE-GUIDE §12)
- [x] Photo fit — no silent crop; soft ~2.2in tall flag (STYLE-GUIDE §19; v3.9)
- [x] Production dateline — SAMPLE removed (v3.9); **final form (v3.12):** centered Playfair Display SC edition word (`<Weekday> Edition` from actual publish day / `Page Two`) + Caslon meta line; double top / solid bottom — **not** three-span Arial (STYLE-GUIDE §2/§12)
- [x] Voice — newsletter-aware, selective word choice, reporter default; tone matches the piece (PLAN §1b; STYLE-GUIDE §0a; v3.11)
- [x] §8 borders — **only** tabular `.box` boards; prose = `.rail-block` + `.rail-title` (no title underline); never wrap article-shaped copy in `.box` (v3.12–v3.14)
- [x] Flanks as newspaper ears — Caslon/Times, hairline top+bottom, clear air from masthead logo; left fixed publisher line; right rotating quip from `flank-quotes.json` (v3.13–v3.14)
- [x] No horizontal rules between page-2 article bands; no fake Gazette Staff bylines — guests only (v3.13–v3.14; PLAN §1b)
- [x] **Sample taste locked** — `issues/2026-10-14/` (`paper-v3.14.pdf`) is the authoritative visual reference (Frank 2026-10-07)
- [x] **Reality / provenance locked (v3.16)** — invent nothing on real issues; every printed fact → staging + `sources.json`; no model memory; sample/pretend labeled only (PLAN §1c)
- [x] **Parent Q&A category locked (v3.18)** — recurring slot; anonymous; no Frank byline; `kind: qa`; `.rail-block.qa` (CONTENT-HIERARCHY + STYLE-GUIDE §8a + STAGING)
- [x] **Email trust allowlist locked (v3.17)** — auto-vet `frankcng@gmail.com`, `chunkymonkey@agentmail.to`, club Mailchimp; flexible ingest for other senders (stage + provenance, unvetted) — STAGING.md § Tips / mail
- [x] **Ops cadence locked (v3.15; wording v3.19)** — chat anytime → next week; email daily + pre-budget; Wed skim + publish-morning full gather; Budget→approve→compose→Proof→approve→print; `sources.json`; chat doorbell only (STAGING.md + SOURCES.md)
- [x] **Flexible weekly publish (v3.19)** — try Mon/Tue; later fine; no two-edition cadence
- [x] **Results tone (v3.23)** — never print a weak finish/place; strong = podium/top 8, notable climb, PB, unbeaten pool; others on an "also fenced" line; when unsure, "also fenced" (STYLE-GUIDE §0d, CONTENT-HIERARCHY results row). Frank, chat 2026-10-12.
- [x] **First real run decisions (v3.20)** — epee assumed (no club “Epee” labels, STYLE-GUIDE §0c); content-heavy cut order (utility boxes give way to stories — CONTENT-HIERARCHY); budget slot note overrides `publishDate`; Desk fill with Frank-vetted items (veto at proof); late add past 2 pages → trim Desk fill before anything else (never shrink type); captions name only Frank-confirmed people; chat spelling beats scrape (scrape → roster alias); FencingTracker registrations unvetted until Frank confirms; proof status in `issue.json`; proof v1 → answers → v2 → approve → Frank prints; Desk inspects PNGs before calling a proof done; staging roll-forward after approval (STAGING.md). See CHANGELOG.md.

Still open:
1. Exact preferred publish window (proposal ~Mon/Tue morning US Eastern) — soft target only.
2. Optional: how to notice "members competing Monday" for the soft hold preference (results-app / AskFRED) — not a hard gate.
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
- [x] Build template A HTML/CSS, B&W test render
- [x] Lock inbox address (AgentMail `efc.weekly@agentmail.to`) + box/GitHub storage
- [x] Drop second edition; lock one weekly newsletter (flexible Mon/Tue target — v3.19)
- [x] Lock Staging→Clean→Budget→Proof + tips vetting + chat→staging (STAGING.md)
- [ ] Confirm preferred Mon/Tue publish window with Frank (soft target)
- [ ] Define results-app email schema (+ optional Monday-competitor fields for soft hold)
- [ ] Adapt Template A for weekly issue (signup board as core); Template A only
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
- [x] **First real weekly edition** — Issue No. 1, Thursday Edition Oct 8, 2026 (`issues/2026-10-08/`); proof v2 approved by Frank 2026-10-07 18:40 ET; Frank printed it
- [x] Docs v3.20: first-real-run decisions + epee-assumed labels + content-heavy cut order (CHANGELOG.md)
- [x] Docs v3.22: X (Twitter) tested as a source: vetted accounts `sources/x-accounts.md`, SOURCES.md § X rules + cadence, 5 unvetted X leads staged for No. 2 (CHANGELOG.md)
- [x] Docs v3.21: budget page v2 (practice.html redesign, lineup schema 2, `/thumb`, `answers`) — CHANGELOG.md
- [x] Docs v3.19: drop Mon/Thu split — weekly tries Mon/Tue, later OK; gather loop phrased publish-morning (not Monday-hard)
- [x] Docs v3.18: Parent Q&A category locked (hierarchy slot + STAGING kind `qa` + STYLE-GUIDE §8a + prototype)
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
- **Where the page runs (2026-10-07):** Gazette Desk serves it from its own computer (`budget-demo/server.py`,
  port 8766: `cd budget-demo && nohup python3 server.py &`) and opens it in Desk's desktop browser; Frank
  reviews / Vets / Submits through the Gazette Desk computer tab, or answers in chat and Desk applies them.
  Detail: STAGING.md Budget step.
- **Budget page v2 (v3.21):** redesigned for Frank's 1280×800 remote view — fixed summary bar with
  Submit, sections in reading order, one card per slot with questions for Frank answered in place
  (`answers` in the submit JSON), collapsed draft/provenance, small cached thumbnails, no
  animations. Monday routine rewrites `budget-demo/practice-lineup.json` (schema 2; STAGING.md).
- Chat is DOORBELL only: the bot pings "budget ready" / "proof ready" — no approval state
  lives in chat (chat fragments across messages and forces scroll-to-reference; rejected as
  a surface). Chat *facts* still go to staging (see STAGING.md).
- Google Form rejected: static templates can't show per-issue photos without regenerating
  the form each time, or force blind approvals.
- Two gates always: (1) approve the budget, (2) approve the rendered proof. Nothing prints
  otherwise. Missed message = skipped week, which is fine (low stakes, just for fun).
- Reversal = re-render from a previous `approvals.json`. Every render records which file it used.
- Pipeline detail: **STAGING.md**.
