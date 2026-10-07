# Staging & editorial pipeline (canonical)

Canonical home for **how material moves** from tip/chat/email into a printed issue.
PLAN.md owns the narrative + decision list; this file owns the pipeline names, item
schema, vetting rules, and folder layout. On conflict, this file wins for pipeline
topics.

Locked 2026-10-06 late evening (plan v3.3).

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
   requires vet first). Submit → `approvals.json`. Chat is doorbell only.
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
- Raw emails never land in git (see `.gitignore`); only message-IDs + derived files.

Exact filenames (`items.jsonl` vs `items/*.json`) may adjust when ingest ships;
the tree above is the layout lock.

## Related locks (pointers)

- Cadence, masthead flanks, footer disclaimer → PLAN.md / STYLE-GUIDE.md
- Slot order + budgets → CONTENT-HIERARCHY.md
- Fetch checklist → SOURCES.md
- Approvals UX (budget + proof, chat doorbell) → PLAN.md § Approval design
