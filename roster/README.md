# Club roster (name variants + family links)

Durable store of **Frank-confirmed** facts about Elite FC people so Clean and
future reports spell names consistently.

## Files

| Path | Role |
|------|------|
| `people.json` | Machine-readable roster (scripts load this) |

## Rules

- **Frank-confirmed only.** Chat / email answers from Frank go here; do not invent
  aliases, ages, ratings, birthdays, or family links.
- **Provenance required** on every person (`who`, `when`, `via`).
- **Minors / privacy:** keep names, aliases, and relations only. Do **not** print
  this file as a list in the paper. Use it to normalize names inside stories and
  boards that already belong in the issue.
- **Chat beats scrape (v3.20):** a spelling Frank gives in chat overrides scraped
  registration forms (FencingTracker, AskFRED). Keep the scraped form in `aliases`
  as a scrape variant so Clean maps it to Frank’s spelling.
- **Names rule (v3.35, voice: Frank 2026-10-18):** official club/tournament pages (AskFRED, USA Fencing entrant lists, club pages/emails) are the source of truth. Add new fencers with the spelling the official page shows (e.g. Samuel SarroWaite, Nora Li, Owen Li, Christina Jiang), provenance "Frank (standing rule)", and **don't ask Frank**. A Frank chat spelling or an existing house form still wins. A shared surname is **not** a family link: record a relation only when it's confirmed (Nora/Owen Li: relation unknown).
- **Unresolved spelling:** set `spelling_unresolved: true` and print each person
  as registered until Frank picks a house form.
- **New confusion:** ask Frank once in chat, then record the answer here (and
  point Clean at the update). Do not re-ask every week.

## Schema (per person)

| Field | Type | Meaning |
|-------|------|---------|
| `id` | string | Stable slug (`first-last`, lowercase) |
| `canonical` | string | Print form: First Last |
| `aliases` | string[] | Registration / tracker forms (`Last, First`, ALL CAPS, etc.) |
| `relations` | object[] | `{ "type": "sibling", "id": "<other-id>" }` (extend types only with Frank) |
| `notes` | string | Short human context |
| `spelling_unresolved` | bool | If true, do not force a single house spelling yet |
| `provenance` | object | `{ "who", "when" (YYYY-MM-DD), "via" }` |

Top-level: `version`, `updated`, optional `note`.

## Clean usage

During Clean, normalize Elite FC names against `roster/people.json` (match
`canonical` or any `alias` → print `canonical`, unless `spelling_unresolved`).
See STAGING.md § Pipeline → Clean; PLAN.md §1c.
