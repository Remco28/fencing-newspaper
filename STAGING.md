# Staging & editorial pipeline (canonical)

Canonical home for **how material moves** from tip/chat/email into a printed issue.
PLAN.md owns the narrative + decision list; this file owns the pipeline names, item
schema, vetting rules, folder layout, and **ops cadence / gather loop**. On conflict,
this file wins for pipeline topics.

Locked 2026-10-06 late evening (plan v3.3); scoreboard cut noted in v3.4; **email media extract** first pass locked 2026-10-06 night (v3.5); **budget-page Vet + notes** locked 2026-10-07 (v3.6); **AgentMail processed-mail labels** locked 2026-10-07 (v3.7); **ops cadence / gather loop** locked 2026-10-07 (plan v3.15; wording v3.19); **email trust allowlist** locked 2026-10-07 (plan v3.17); **Parent Q&A category** locked 2026-10-07 (plan v3.18); **first-real-run decisions** (slot-note override, scraped registrations unvetted, chat spellings, proof round, week roll-forward) locked 2026-10-07 (plan v3.20); **Budget spread** adopted 2026-11-16 (`budget-paper-v1`, then `budget-paper-v2` Auto/Manual on 2026-11-17); **weekly Budget rhythm** locked 2026-11-17 (Frank).

## Pipeline (formal names)

1. **Staging** — centralized pile of cleaned-enough facts, photos, draft grafs,
   signup rows, tips. Every item carries provenance (source, message-ID if email,
   target week, `vetted` bool). Materials can accumulate for subsequent weeks in
   advance.
2. **Clean** — normalize names against `roster/people.json` (canonical print form;
   honor `spelling_unresolved`), apply epee filter, enforce word/row counts, attach
   provenance for `sources.json`. New name confusions → ask Frank once, record the
   answer in the roster. Unvetted items stay labeled; Clean does not promote them.
   **Spelling precedence (v3.20):** a name spelling Frank gives in chat beats any scraped
   form (FencingTracker / AskFRED / registration). Print Frank’s spelling; add the scraped
   form to that person’s `aliases` in `roster/people.json` as a scrape variant (e.g.
   “Anayaà Sheth” → “Anayaa Sheth”).
3. **Budget** — one self-contained HTML file Frank opens on his laptop or phone
   (offline, no server). Built by `python3 scripts/build_budget_html.py` into
   `budget-demo/out/budget-no-<N>-<date>-v<K>.html` (gitignored; send the file, don't
   commit it). Proposed lineup vs CONTENT-HIERARCHY.md, shown as the two pages of the
   issue: included items are blocks sized by the capacity model, a **bank** holds what
   isn't running, hatched holes mark unfilled space, and overflow hangs past a red trim
   line (visual overset, with a spill well). `pageVersion` is `budget-paper-v2`.
   User-facing copy says **Clark** / **Clark Kent**, never “desk”. Always called
   **Budget**, never Dummy. Detail: **budget-demo/STANDALONE-README.md**.
   **Include only vetted** items and photos. Unvetted work stays in the bank (drag and
   the Page 1 / Page 2 buttons are disabled) until Frank vets it on the slip. A vet in
   the same submission is enough. Ingest refuses (exit 4) a submission that includes an
   unvetted staging item or photo. Photo vets are written to `media/manifest.json` and
   persist into next week; an unvetted photo is never auto-queued.
   **Vetting UX (v3.6, still the primary path):** **Vet + notes on the Budget page**.
   Notes field = “Why this matters / what the bot should know”; stored on the staging
   item as `vet_notes`. Chat promote / forward-from-frank remain OK as alternates.
   **Placement:** Auto is the default (the packer places and sizes blocks). A Manual
   switch freezes the current layout: drag blocks on the grid (dashed landing outline;
   drop on the bank or left of page 1 to remove), resize only that block, Wide/Tall
   variants (`layouts.json`), Expand/Shrink/Clear, framed photos that scale to fit and
   are never cropped. Overlaps warn; nothing is auto-fixed. Undo is stacked; Back to
   Auto asks first.
   **Weekly rhythm (Frank, 2026-11-17):** curate through the week; Clark preps sections
   ahead; when ready, generate the Budget, then Frank modifies and adds. Nothing about
   that changes until Frank wants final layout tweaks, or wants to push one layout
   harder — that is what Manual is for. Then Clark composes the proof (v3 process, eye
   check) from the approved budget. A Manual layout is saved as `mode` + `manualLayout`;
   compose does not yet pack from it, so Clark matches it by hand and flags anything
   that will not fit.
   Submit → download/copy JSON → ingest (`scripts/ingest_budget_submission.py`) writes a
   timestamped budget JSON, `approvals.json`, vets (items + photo manifest), and a
   decision in `budget-versions.json`. Chat is doorbell only for budget/proof readiness.
   **Lineup:** rewrite `budget-demo/practice-lineup.json` (schema 2) for the coming
   issue, then build the standalone page. Last issue's lineup is kept under
   `budget-demo/archive/`. Apply Frank's answers like chat answers (provenance
   “budget: Frank YYYY-MM-DD”).
   **Fallback:** `practice.html` + `server.py` (`http://127.0.0.1:8766/`) still work if
   the standalone file cannot be used. The old pretend demo is at `/demo`. Test a server
   run against a throwaway copy (`GAZETTE_STAGING_WEEK`, `GAZETTE_SUBMISSIONS`,
   `GAZETTE_PORT`), never the real pile.
   **Slot note beats the date field (v3.20):** if Frank’s budget submission carries a slot
   note or general note that names a publish day (e.g. “We are publishing this Thursday
   (tomorrow)”), that note **overrides** the `publishDate` field; the issue folder and dateline
   follow the note. Record the override in `issue.json`.
   Scoreboard strip is **cut** from the live hierarchy (v3.4); may return later as
   "headline wire" — do not treat it as a current Budget slot.
4. **Proof** — rendered PDF; second approve gate. Every proof goes through the eye check
   (`compose/eyecheck.py`; `--verify` is the send gate) and Clark opens every preview
   himself before it goes to Frank (STYLE-GUIDE §7; the proof v3 process used on No. 7).
   (Optional Claude Code copy check after vetting and PNG proof check: see § Claude Code, v3.36.) Nothing prints without both
   budget + proof approval.
   **Proof round (v3.20 — as run for Issue No. 1):**
   proof **v1** → “proof ready” doorbell with previews + open flags (Clark fill list Frank can
   veto, names to confirm) → **Frank’s answers** (chat) applied → proof **v2** (v3… if needed)
   → **Frank approves** → print. **Frank prints the PDF himself** (no auto-print yet).
   - **Proof status lives in `issue.json`** (`status`, `proof_version`, `proof_history`,
     `proof_approval`) and the HTML `<title>` only — never a PROOF stamp on the sheet.
     On approval also add `proofApproval` to the issue `approvals.json`. Approved PDFs are
     frozen: do not re-render or edit an approved issue.
   - Before any proof is called done, Clark opens and inspects every page PNG (STYLE-GUIDE §7).
   - Frank’s chat answers count as verified facts; provenance `chat: Frank YYYY-MM-DD`.

## Tips / mail

- **Public ask (small, OK):** tips & photos to `efc.weekly@agentmail.to`. Editor
  (Frank) decides what ships.
- **Flexible ingest:** accept mail from Frank, apps, bots, newsletters, unknown
  senders — **never reject** an unknown app/bot on address alone. Stage with full
  provenance (`from`, `message_id`, `source`). Content shape may vary (plain tip,
  structured digest, forward, newsletter HTML).
- **Auto-vetted allowlist** (same rule as Frank — `vetted: true` on ingest):
  - `frankcng@gmail.com` → `vetted_by: auto-frank-gmail`
  - `chunkymonkey@agentmail.to` (Frank’s other bot) → `vetted_by: auto-chunkymonkey`
  - `elitefencersclub@111617670.mailchimpapp.com` (club-owner Mailchimp) → `vetted_by: auto-club-mailchimp`
- **Everyone else** → staging as **`vetted: false` (unvetted)**. Unvetted items MAY
  appear on the budget page but only labeled unvetted; they **cannot** be included
  in the issue until Frank vets them.
- No Gmail for this project (inbox stays AgentMail). Raw MIME/bodies stay in
  AgentMail; cite by message-ID.
- **Scraped registrations (v3.20):** Elite FC names found on **FencingTracker** (or other
  scraped registration lists) are staged **`vetted: false`** until Frank confirms them — they
  don’t print, even when the page looks clear. After Frank confirms, vet the item (source
  `chat: Frank <date>`, append `vet-log.jsonl`) and normalize names via the roster.

## Email triage labels (locked v3.7)

AgentMail has **labels**, not Gmail-style folders. Labels mark workflow state; raw
bodies stay in AgentMail for cite-by-message-ID. **Never delete** ingested mail.

1. After a message is **fully** ingested into staging (facts/media extracted,
   `message_id` recorded, staging write succeeded), apply label **`processed`** and
   remove **`unread`** if present.
2. The ingest loop only considers messages that are **not** labeled `processed`
   (equivalently: unread / missing `processed`).
3. **Failed or partial ingest:** leave unlabeled, or apply **`ingest-error`**, so the
   next pass retries / Frank can see it. Never mark `processed` until the staging
   write succeeded.
4. Optional later (not required for v1): `week:YYYY-MM-DD` for filtering — skip if it
   complicates the first automation pass.

## Email media extract (locked v3.5)

On ingest from AgentMail (planned automation; first manual pass done 2026-10-06):

1. **MIME attachments** — save image/PDF attachments into the target week’s media folder.
2. **Remote / inline HTML images** — parse the HTML body and **download** embedded image URLs (club newsletters often use Mailchimp CDN embeds with **no** MIME attachments). Filter out:
   - tracking pixels (1×1 / `list-manage` / known trackers)
   - social icons (Instagram, website, Mailchimp monkey, etc. — known icon hosts)
   - tiny logos / brand marks under ~80px (or obvious logo assets)
3. **Store** under `staging/weeks/<target>/media/` with a `manifest.json` (or per-item records) carrying provenance: `message_id`, `url` or attachment id, `from`, `vetted`, `kind: photo`, caption.
4. **The Budget page** reads photos from that media folder (thumbnails on the spread and in the bank). The fallback demo server maps `/staging-media/*` → `staging/weeks/next/media/`.
5. Until this pass, the pretend budget demo used **synthetic PNGs** under `budget-demo/photos/` only. Those remain as clearly labeled **PRETEND** placeholders; real photos from Frank’s test mail now lead the photo bank.

Auto-vet allowlist still applies (see § Tips / mail): Frank Gmail, chunkymonkey, club Mailchimp → `vetted: true`.

## Chat → staging

When Frank tells the bot a fact/idea in chat, **default target = next weekly issue**
staging unless he names another week. Materials can accumulate for later weeks.
Chat does **not** hold approval state — **doorbell only** for budget/proof readiness
(approvals live on the budget page / `approvals.json`).

## Ops cadence / gather loop (locked v3.15 — Frank 2026-10-07; wording v3.19)

Canonical home for **when** Clark Kent checks chat, email, and self-gather.
SOURCES.md owns *what* to fetch; this section owns *how often*. Times = US Eastern.

### Chat → staging (anytime)
- Frank tells Clark a fact/idea → stage for **next weekly issue** unless he names another week.
- Same rule as § Chat → staging above; reaffirmed here so the gather loop is one place.

### Email (`efc.weekly@agentmail.to`) — two passes
1. **Daily light pass (morning):** ingest new mail → staging; apply `processed` (see § Email triage labels); run email media extract.
2. **Second pass immediately before building the HTML budget:** catch late tips, results-app slices, and club forwards so the lineup isn’t stale.

### Self-gather (SOURCES.md) — two passes + FencingTracker daily look
0. **Daily quick look (weekday morning pass, v3.24):** FencingTracker Elite FC club page (https://fencingtracker.com/club/100261977/Elite%20FC/results), one fetch; stage any new Elite FC result unvetted (`source: "web"`, from FencingTracker, URL + retrieved_at). Gentle use per SOURCES.md § FencingTracker.
0b. **fencing-api cross-check (v3.34, supplemental — every pass):** Frank's API (`scripts/fencingapi.py`, SOURCES.md § fencing-api) runs *alongside*, never instead of, the direct AskFRED / FencingTracker / USA Fencing / email checks. Daily quick look: cached club results + live results for that day's/weekend's Elite FC tournaments. Wednesday skim: upcoming board entrants. Monday full pass: prior week's results + upcoming board entrants. Pre-budget: board entrants + deadlines. Stage as `source: "fencingapi"` (unvetted); any API-vs-direct mismatch gets flagged for Frank.
1. **Mid-week skim (Wednesday):** light pass — Google News RSS (`fencing+epee` + `+New Jersey` variant) as juice detector; skim Tier-1 headlines / AskFRED changes worth staging; X skim (≈5–10 read-only calls, vetted accounts in `sources/x-accounts.md`); FencingTracker club-page check (v3.24). Do **not** pretend this replaces the full checklist.
2. **Publish-morning full pass** (when Frank is aiming to ship — usually Mon/Tue morning; later OK): full SOURCES “Every run” checklist (incl. FencingTracker full sweep — club page + event results pages, v3.24; X full pass, ≈15–25 calls; X items stage `source: "x"`, unvetted, provenance `type: "x_post"` with post URL + UTC/ET time). Soft preference: if Elite FC members are fencing Monday, waiting for those results is nice when easy — not required.

### Publish gates (reminder)
**Budget HTML → Frank approve → Clark Kent compose → Proof PDF → Frank approve → print.**
Weekly rhythm (Frank, 2026-11-17): curate through the week, Clark preps sections ahead, generate the Budget (Auto default), Frank modifies and adds; Manual only for final layout tweaks or to push one layout harder; then compose, eye-check, Frank approves, publish.
Every printed fact keeps provenance in `sources.json` (URL + retrieved date, or email/chat message-ID + date, or logged API/fetch). Chat is doorbell only for “budget ready” / “proof ready.”
Compose with the shared Template A helpers in `compose/` (copy `compose/recipe_template.py` to `issues/<date>/recipe/compose.py`; see `compose/README.md`). Render with `python3 compose/render.py`, run `python3 compose/eyecheck.py` (and `--verify` before sending), and write 200 dpi previews. Clark also opens every preview himself. An issue whose `issue.json` status starts with APPROVED is frozen — in-place compose needs `--force`. Published Nos. 1–7 stay frozen. If Frank submitted a Manual layout, match `manualLayout` by hand — compose does not yet pack from it.

### Reality / provenance (locked 2026-10-07 — plan v3.16)
- **Real issues invent nothing.** Sample/layout fiction stays labeled (`sample`, `pretend`, `demo`) and must not be promoted as fact.
- Every staging item that can become print copy carries provenance (`source`, `message_id` / URL / fetch log) so Clean and compose can fill `sources.json`.
- No model memory as a source for names, results, ratings, dates, entries, or claims about real people.
- Narrative home: PLAN §1c; compose checklist: STYLE-GUIDE §0b.

### Claude Code — optional second reviewer (v3.36 — Frank 2026-10-18)
Claude Code (`claude -p`, Opus or Sonnet, whichever is available on the runner) is an **optional second reviewer**. It never writes copy or adds facts. **Clark stays the writer and the keeper of sources.** If Claude Code isn't available, skip the step: nothing depends on it.
- **(a) Copy check:** after vetting, before budget or compose. Give it the texts plus the house rules (STYLE-GUIDE §0a–0d: reality lock, no Epee labels in club context, opinions labeled, no usernames, strong results only, no birth years) and each item's provenance. Ask it to flag unsupported claims, opinion/fact drift, typos, awkward lines and house-rule slips. Clark takes the fixes it agrees with and notes taken/rejected fixes in the item's `vet_notes`. A fact Claude Code proposes never goes in.
- **(b) Proof check:** run it on rendered page PNGs (overflow, orphans, gaps, alignment) alongside Clark's own STYLE-GUIDE §7 visual QA. It does not replace Clark's check.
- **(c) Site and code work:** reviews of budget page, site and scripts changes.
- Never pass `.env` contents, API keys, raw email or DOBs into a Claude Code prompt.

### Names + pending entries (v3.35 — voice: Frank 2026-10-18)
- **Official pages are the source of truth for names.** Print a fencer's name exactly as the official club or tournament page lists it (AskFRED, USA Fencing/member.usafencing.org entrant lists, the club's own pages and emails). Don't ask Frank about names. Order of precedence: a spelling Frank gives in chat, then an existing roster house form, then the official page. FencingTracker is a mirror, not an official page: if it disagrees with an official page, use the official spelling. New names go into `roster/people.json` with the official spelling and provenance "Frank (standing rule)".
- **Pending entries print.** An entry that AskFRED shows as pending (not yet paid or confirmed) counts as an entry for the Nearby Tournaments board.
- Never stage birth years / DOBs (some API and registration payloads carry them; drop on ingest).
- **Brendan Mendez (Frank budget submission 2026-11-16):** assume he is **not** a club member until Frank confirms otherwise. Do not stage or print his results, do not list him on club boards, and **never ask Frank about him again**. A FencingTracker club listing is not confirmation. Keep the roster entry so the name is recognized and skipped. See `roster/people.json` (`brendan-mendez`).

### Related
- Source checklists → **SOURCES.md**
- Labels / media extract / item schema → sections above
- Slip rule + schedule narrative → PLAN.md §1 / §6

## Item schema (sketch)

## Parent Q&A (locked v3.18 — Frank 2026-10-07)

Recurring **content category**, not a one-off layout trick.

- **Flow:** A parent asks Frank → Frank tells Clark Kent in chat (or email) → we stage + print.
- **Privacy default:** **no parent name**, **no Frank byline**. Name the asker only if they ask to be named; still no Frank byline unless he is explicitly guesting.
- **Staging:** `kind: qa`, tags include `qa`, `suggested_slot` / `slot_hint`: `parent_qa`, `vetted` per normal trust rules (Frank chat = vetted).
- **Print:** CONTENT-HIERARCHY slot **Parent Q&A** (40–70w); STYLE-GUIDE `.rail-block.qa`. Usually **one** per issue.
- **Facts:** same reality lock as everything else (PLAN §1c) — answers must be anchored; light source check OK; do not invent.

Each staging item is one record (JSON object or equivalent). Fields:

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | Stable id within the week (or UUID) |
| `kind` | enum | `fact` \| `photo` \| `graf` \| `signup_row` \| `tip` \| `comic` \| **`qa`** \| `other` |
| `body` | string | Text, or path/caption for media |
| `media_path` | string? | Relative path under the week folder if photo/comic |
| `source` | string | e.g. `email`, `chat`, `fie`, `results-app`, `frank-forward` |
| `message_id` | string? | AgentMail message-ID when from email |
| `from` | string? | Sender address when from email |
| `target_week` | string | Publish-date folder key `YYYY-MM-DD` (or `next` until dated) |
| `vetted` | bool | `true` after Frank vet or auto from allowlist (Frank Gmail / chunkymonkey / club Mailchimp) |
| `vetted_at` | string? | ISO timestamp when promoted |
| `vetted_by` | string? | `frank` / `auto-frank-gmail` / `auto-chunkymonkey` / `auto-club-mailchimp` |
| `vet_notes` | string? | Frank’s context for the bot when vetting on the budget page (or chat) |
| `slot_hint` | string? | Optional CONTENT-HIERARCHY slot name |
| `word_count` / `row_count` | number? | Filled/checked in Clean |
| `created_at` | string | ISO timestamp |

Educational illustrations / figures (Frank assets): stage as **`kind: other`** with `media_path` (SVG preferred) + tags `illustration` / `figure`; `suggested_slot` e.g. `back_page_feature`; default **`columns` / `span`: 2** (not 3 / not full-bleed) unless Frank widens it. Do not use `photo` (Budget photo) or `comic` (gag panel) unless that is what they are.

Promotion / vet paths (any one is enough):
- **Budget-page Vet + notes (preferred UX):** Frank hits **Vet** on an UNVETTED row/card/photo, adds `vet_notes`, Include unlocks. Demo: `POST /vet` → `staging/weeks/next/items.json` + `vet-log.jsonl`.
- Mail from the auto-vet allowlist (`frankcng@gmail.com`, `chunkymonkey@agentmail.to`, club Mailchimp) → auto-vetted on ingest.
- Explicit promote action in chat/tools that sets `vetted: true` (+ optional notes) — still OK as alternate.

## Folder layout (proposed)

```
staging/
  weeks/
    YYYY-MM-DD/          # upcoming target week (publish date once known)
      items.jsonl        # one staging item per line (or items/*.json)
      media/             # photos, comics (derived copies; originals may live elsewhere)
    next/                # default dump when publish date not yet chosen
      items.json           # (demo) staging items; items.jsonl OK when ingest ships
      vet-log.jsonl        # append-only Vet actions from budget page / tools
      budget-versions.json # per-week Budget version counter + Frank's decision log
      media/
    after-next/          # hold for the issue after `next`; same layout as next/

issues/
  YYYY-MM-DD/            # closed (or in-flight) week after budget/proof work starts
    issue.json
    sources.json
    approvals.json
    en-garde-gazette-no-<N>-<YYYY-MM-DD>.pdf   # unique; never bare paper.pdf for published issues
    inputs/              # Clean outputs derived for the template
```

Rules:
- **Staging** lives under `staging/weeks/` so material can pile up for future weeks
  without pretending the issue is already locked.
- When a week moves into Budget/Proof, copy or link Clean outputs into
  `issues/YYYY-MM-DD/`. Closed weeks stay under `issues/`; do not delete staging
  history for that week until Frank says so (fun project — keep provenance).
- `staging/weeks/next/` is the default chat/email dump target until Frank names a
  date or the scheduler assigns the next target publish date (usually Mon/Tue).
- **Roll forward after an issue is approved (v3.20):** `next/` → `YYYY-MM-DD/` (the
  published issue’s date — kept as history), `after-next/` → `next/`, fresh empty
  `after-next/`. Still-relevant unprinted items may be copied into the new `next/` with
  `carried_from`. First roll: 2026-10-07 (Issue No. 1 → `staging/weeks/2026-10-08/`).
- Raw emails never land in git (see `.gitignore`); only message-IDs + derived files (including downloaded newsletter photos under `media/`).

Exact filenames (`items.jsonl` vs `items/*.json`) may adjust when ingest ships;
the tree above is the layout lock.

## Related locks (pointers)

- Publish cadence (weekly, try Mon/Tue) + furniture → PLAN.md / STYLE-GUIDE.md
- Ops gather loop (email/self-gather timing) → this file § Ops cadence; fetch list → SOURCES.md
- Slot order + budgets + cut/stretch → CONTENT-HIERARCHY.md (visual scale → STYLE-GUIDE §4/§11)
- Fetch checklist → SOURCES.md
- Approvals UX (budget + proof, chat doorbell) → this file § Budget; **budget-demo/STANDALONE-README.md**; PLAN.md § Approval design
- Slot order (scoreboard cut v3.4) → CONTENT-HIERARCHY.md

## Printed-page archive whisper (2026-10-15)

Footer middle line on every page: `Past issues · newsletter.teamremco.org` (class `.foot-archive`). Carry into No. 3+ from the locked issue HTML pattern.
