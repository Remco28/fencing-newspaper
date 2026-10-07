# Staging & editorial pipeline (canonical)

Canonical home for **how material moves** from tip/chat/email into a printed issue.
PLAN.md owns the narrative + decision list; this file owns the pipeline names, item
schema, vetting rules, and folder layout. On conflict, this file wins for pipeline
topics.

Locked 2026-10-06 late evening (plan v3.3); photo desk + scoreboard cut noted in v3.4; **email media extract** first pass locked 2026-10-06 night (v3.5).

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
   unvetted items may appear on the page labeled **unvetted** but are blocked from
   include until Frank vets them (promote / forward-from-frank / checkbox that
   requires vet first). **Photo desk:** visible image thumbnails with multi-select
   Include checkboxes; selected IDs → `photoIncludes` in the submit JSON (not bare
   per-slot photo flags without images). Submit → timestamped budget JSON +
   overwrite `approvals.json`. Chat is doorbell only.
   Scoreboard strip is **cut** from the live hierarchy (v3.4); may return later as
   "headline wire" — do not treat it as a current Budget slot.
4. **Proof** — rendered PDF; second approve gate. Nothing prints without both
   budget + proof approval.

## Tips / mail

- **Public ask (small, OK):** tips & photos to `efc.weekly@agentmail.to`. Editor
  (Frank) decides what ships.
- **Auto-Frank-vetted:** only mail from `frankcng@gmail.com`.
- **Everyone else** → staging as **`vetted: false` (unvetted)**. Unvetted items MAY
  appear on the budget page but only labeled unvetted; they **cannot** be included
  in the issue until Frank vets them.
- No Gmail for this project (inbox stays AgentMail). Raw MIME/bodies stay in
  AgentMail; cite by message-ID.

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

Auto-vet rule still applies: `from` = `frankcng@gmail.com` → `vetted: true`.

## Chat → staging

When Frank tells the bot a fact/idea in chat, **default target = next weekly issue**
staging unless he names another week. Chat does not hold approval state (doorbell
only for budget/proof readiness).

## Item schema (sketch)

Each staging item is one record (JSON object or equivalent). Fields:

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | Stable id within the week (or UUID) |
| `kind` | enum | `fact` \| `photo` \| `graf` \| `signup_row` \| `tip` \| `comic` \| `other` |
| `body` | string | Text, or path/caption for media |
| `media_path` | string? | Relative path under the week folder if photo/comic |
| `source` | string | e.g. `email`, `chat`, `fie`, `results-app`, `frank-forward` |
| `message_id` | string? | AgentMail message-ID when from email |
| `from` | string? | Sender address when from email |
| `target_week` | string | Publish-date folder key `YYYY-MM-DD` (or `next` until dated) |
| `vetted` | bool | `true` only after Frank vet (or auto from `frankcng@gmail.com`) |
| `vetted_at` | string? | ISO timestamp when promoted |
| `vetted_by` | string? | `frank` / `auto-frank-gmail` |
| `slot_hint` | string? | Optional CONTENT-HIERARCHY slot name |
| `word_count` / `row_count` | number? | Filled/checked in Clean |
| `created_at` | string | ISO timestamp |

Promotion / vet paths (any one is enough):
- Frank marks vetted on the budget page (checkbox that requires vet first before include).
- Frank forwards the tip from `frankcng@gmail.com` (auto-vetted on ingest).
- Explicit promote action in chat/tools that sets `vetted: true` (Frank-initiated).

## Folder layout (proposed)

```
staging/
  weeks/
    YYYY-MM-DD/          # upcoming target week (publish date once known)
      items.jsonl        # one staging item per line (or items/*.json)
      media/             # photos, comics (derived copies; originals may live elsewhere)
    next/                # default dump when publish date not yet chosen
      items.jsonl
      media/

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
  date or the scheduler assigns the next Mon/Tue slip date.
- Raw emails never land in git (see `.gitignore`); only message-IDs + derived files (including downloaded newsletter photos under `media/`).

Exact filenames (`items.jsonl` vs `items/*.json`) may adjust when ingest ships;
the tree above is the layout lock.

## Related locks (pointers)

- Cadence, masthead flanks, footer disclaimer → PLAN.md / STYLE-GUIDE.md
- Slot order + budgets → CONTENT-HIERARCHY.md
- Fetch checklist → SOURCES.md
- Approvals UX (budget + proof, chat doorbell, photo desk) → PLAN.md § Approval design
- Slot order (scoreboard cut v3.4) → CONTENT-HIERARCHY.md
