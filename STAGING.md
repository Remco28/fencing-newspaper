# Staging & editorial pipeline (canonical)

Canonical home for **how material moves** from tip/chat/email into a printed issue.
PLAN.md owns the narrative + decision list; this file owns the pipeline names, item
schema, vetting rules, folder layout, and **ops cadence / gather loop**. On conflict,
this file wins for pipeline topics.

Locked 2026-10-06 late evening (plan v3.3); photo desk + scoreboard cut noted in v3.4; **email media extract** first pass locked 2026-10-06 night (v3.5); **budget-page Vet + notes** pretend UX locked 2026-10-07 (v3.6); **AgentMail processed-mail labels** locked 2026-10-07 (v3.7); **ops cadence / gather loop** locked 2026-10-07 (plan v3.15; wording v3.19); **email trust allowlist** locked 2026-10-07 (plan v3.17); **Parent Q&A category** locked 2026-10-07 (plan v3.18).

## Pipeline (formal names)

1. **Staging** — centralized pile of cleaned-enough facts, photos, draft grafs,
   signup rows, tips. Every item carries provenance (source, message-ID if email,
   target week, `vetted` bool). Materials can accumulate for subsequent weeks in
   advance.
2. **Clean** — normalize names, apply epee filter, enforce word/row counts, attach
   provenance for `sources.json`. Unvetted items stay labeled; Clean does not
   promote them.
3. **Budget** — local HTML page on Musketeer's computer. Proposed lineup vs
   CONTENT-HIERARCHY.md. **Include only vetted** items in the proposed sheet;
   unvetted items may appear on the page labeled **UNVETTED** but are blocked from
   Include until Frank vets them. **Vetting UX (v3.6):** primary path is **Vet + notes
   on the budget page** (staging inbox, lineup cards, photo desk). Notes field =
   “Why this matters / what the bot should know”; stored on the staging item as
   `vet_notes` (alias `notes` accepted on POST `/vet`). Chat promote / forward-from-
   frank remain OK as alternates. **Photo desk:** visible image thumbnails with
   multi-select Include checkboxes (gated until vetted); selected IDs →
   `photoIncludes` in the submit JSON. Submit → timestamped budget JSON + overwrite
   `approvals.json`. Vet → update `staging/weeks/next/items.json` + append
   `vet-log.jsonl`. Chat is doorbell only for budget/proof readiness.
   **Practice budget (2026-10-07):** `budget-demo/practice.html` renders Desk's proposed lineup
   (`budget-demo/practice-lineup.json`) against live staging — real items only, seed/pretend in a
   collapsed excluded drawer, stale items flagged (not proposed), dupes merged, provenance links +
   CLICK-CHECK marks on cards, rough two-page fit estimate (~40 w/col-in; furniture measured on the
   2026-10-14 sample). Served at `/`; old pretend demo at `/demo`.
   Scoreboard strip is **cut** from the live hierarchy (v3.4); may return later as
   "headline wire" — do not treat it as a current Budget slot.
4. **Proof** — rendered PDF; second approve gate. Nothing prints without both
   budget + proof approval.

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
4. **Budget photo desk** reads from that media folder (thumbs visible). Demo server maps `/staging-media/*` → `staging/weeks/next/media/`.
5. Until this pass, the pretend budget demo used **synthetic PNGs** under `budget-demo/photos/` only. Those remain as clearly labeled **PRETEND** placeholders for multi-select UX; real photos from Frank’s test mail now lead the desk.

Auto-vet allowlist still applies (see § Tips / mail): Frank Gmail, chunkymonkey, club Mailchimp → `vetted: true`.

## Chat → staging

When Frank tells the bot a fact/idea in chat, **default target = next weekly issue**
staging unless he names another week. Materials can accumulate for later weeks.
Chat does **not** hold approval state — **doorbell only** for budget/proof readiness
(approvals live on the budget page / `approvals.json`).

## Ops cadence / gather loop (locked v3.15 — Frank 2026-10-07; wording v3.19)

Canonical home for **when** Gazette Desk checks chat, email, and self-gather.
SOURCES.md owns *what* to fetch; this section owns *how often*. Times = US Eastern.

### Chat → staging (anytime)
- Frank tells Desk a fact/idea → stage for **next weekly issue** unless he names another week.
- Same rule as § Chat → staging above; reaffirmed here so the gather loop is one place.

### Email (`efc.weekly@agentmail.to`) — two passes
1. **Daily light pass (morning):** ingest new mail → staging; apply `processed` (see § Email triage labels); run email media extract.
2. **Second pass immediately before building the HTML budget:** catch late tips, results-app slices, and club forwards so the lineup isn’t stale.

### Self-gather (SOURCES.md) — two passes
1. **Mid-week skim (Wednesday):** light pass — Google News RSS (`fencing+epee` + `+New Jersey` variant) as juice detector; skim Tier-1 headlines / AskFRED changes worth staging. Do **not** pretend this replaces the full checklist.
2. **Publish-morning full pass** (when Frank is aiming to ship — usually Mon/Tue morning; later OK): full SOURCES “Every run” checklist. Soft preference: if Elite FC members are fencing Monday, waiting for those results is nice when easy — not required.

### Publish gates (reminder)
**Budget HTML → Frank approve → Gazette Desk compose → Proof PDF → Frank approve → print.**
Every printed fact keeps provenance in `sources.json` (URL + retrieved date, or email/chat message-ID + date, or logged API/fetch). Chat is doorbell only for “budget ready” / “proof ready.”

### Reality / provenance (locked 2026-10-07 — plan v3.16)
- **Real issues invent nothing.** Sample/layout fiction stays labeled (`sample`, `pretend`, `demo`) and must not be promoted as fact.
- Every staging item that can become print copy carries provenance (`source`, `message_id` / URL / fetch log) so Clean and compose can fill `sources.json`.
- No model memory as a source for names, results, ratings, dates, entries, or claims about real people.
- Narrative home: PLAN §1c; compose checklist: STYLE-GUIDE §0b.

### Related
- Source checklists → **SOURCES.md**
- Labels / media extract / item schema → sections above
- Slip rule + schedule narrative → PLAN.md §1 / §6

## Item schema (sketch)

## Parent Q&A (locked v3.18 — Frank 2026-10-07)

Recurring **content category**, not a one-off layout trick.

- **Flow:** A parent asks Frank → Frank tells Gazette Desk in chat (or email) → we stage + print.
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

Educational illustrations / figures (Frank assets): stage as **`kind: other`** with `media_path` (SVG preferred) + tags `illustration` / `figure`; `suggested_slot` e.g. `back_page_feature`; default **`columns` / `span`: 2** (not 3 / not full-bleed) unless Frank widens it. Do not use `photo` (photo desk) or `comic` (gag panel) unless that is what they are.

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
      media/
    after-next/          # hold for the issue after `next` (e.g. THE WEAPON); same layout as next/

issues/
  YYYY-MM-DD/            # closed (or in-flight) week after budget/proof work starts
    issue.json
    sources.json
    approvals.json
    paper.pdf
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
- Raw emails never land in git (see `.gitignore`); only message-IDs + derived files (including downloaded newsletter photos under `media/`).

Exact filenames (`items.jsonl` vs `items/*.json`) may adjust when ingest ships;
the tree above is the layout lock.

## Related locks (pointers)

- Publish cadence (weekly, try Mon/Tue) + furniture → PLAN.md / STYLE-GUIDE.md
- Ops gather loop (email/self-gather timing) → this file § Ops cadence; fetch list → SOURCES.md
- Slot order + budgets + cut/stretch → CONTENT-HIERARCHY.md (visual scale → STYLE-GUIDE §4/§11)
- Fetch checklist → SOURCES.md
- Approvals UX (budget + proof, chat doorbell, photo desk) → PLAN.md § Approval design
- Slot order (scoreboard cut v3.4) → CONTENT-HIERARCHY.md
