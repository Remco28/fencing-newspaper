# Email ingest log — 2026-10-07

**Inbox:** `efc.weekly@agentmail.to` (AgentMail MCP `user-Agentmail`)  
**Pass type:** workflow test (manual, on Frank request)  
**Operator:** Gazette Desk  
**Started / finished:** ~2026-10-07T13:15:19-04:00 ET (single session; wall clock ~10–15 min judgment + tool round-trips)

## Messages processed (4)

| # | From | Subject | Vetting | Staged item ids | Media | Labels after |
|---|------|---------|---------|-----------------|-------|--------------|
| 1 | AgentMail `<chunkymonkey@agentmail.to>` | Club schedule · Wednesday, October 7 | **unvetted** | `email-agentmail-medeo-entries-2026-10-07`, `email-agentmail-morris-cup-entries-2026-10-07` | none (HTML text digest, no photos) | `processed` (unread removed) |
| 2 | Elite Fencers Club Mailchimp | Group Class! + Footwork Class | **unvetted** | `email-mailchimp-group-footwork-2026-10-07` | skipped logo + icons + pixel | `processed` |
| 3 | Frank Ng `<frankcng@gmail.com>` | *(blank / missing)* | **auto-vetted** | `email-frank-medeo-entries-2026-10-07` (+ patched `signup-medeo` message_id) | none | `processed` |
| 4 | Frank Ng `<frankcng@gmail.com>` | Fwd: Group Class! + Congrats!🏅 | **auto-vetted** | `email-frank-congrats-forward-2026-10-07` (+ patched club-events / result-syc / tip-medeo / photo items) | already on disk (`club-newsletter-photo-1/2`) | `processed` |

Remise + gather-* items **kept**. Total staging items after pass: **29**.

## What worked

- `list_messages` with `labels: ["unread"]` returned exactly the 4 expected messages.
- `get_message` returned full `text` / `html` (and usually `extractedText`) — enough to stage without MIME spelunking.
- Auto-vet rule clear: `from` contains `frankcng@gmail.com` → `vetted: true`; Mailchimp + AgentMail digest → `vetted: false`.
- Media extract rules held: Mailchimp CDN embeds recognizable; logo (~100px width), social icons, 1×1 tracker correctly skipped.
- Prior Congrats photo extract (same `message_id` + URLs) meant **no re-download** — dedupe by URL/message_id works.
- AgentMail digest is high-value for **Who's Entered** (full Morris Cup EFC list) — better than gather-only event stub.
- `update_message` addLabels `processed` / removeLabels `unread` is the right triage loop (applied after staging write).

## Issues / friction

1. **Missing subject (Frank Medeo):** list + get returned **no `subject` field** for message 3. Preview/body still fine; staged with `subject: null` + note. Prefer Frank always setting a subject, or Desk synthesizing one from first line.
2. **Mailchimp `To:` is frankcng@gmail.com** but message lives in `efc.weekly` inbox — delivery path unclear (forward? list-add of AgentMail address? Gmail filter?). Workflow still works; provenance records the odd `to`.
3. **`extractedText` empty on direct Mailchimp** (msg 2) while `text`/`html` present — always prefer `text` then `html` fallback; don't trust extractedText alone.
4. **Content overlap / duplicate seeds:** Congrats + Medeo facts already existed as pretend/prior-seed items (`club-events-efc`, `result-syc`, `signup-medeo`, …) **without** `message_id`. This pass appended cite-ready email items **and** patched message_ids onto the seeds. Budget Clean will need a **dedupe step** (prefer email+message_id over seed).
5. **No MIME image attachments** on any of the 4 — club photos are always remote HTML. Confirm automation always parses HTML `img src`, not only attachments.
6. **AgentMail digest is unvetted by rule** even though it's club-ops gold. Daily pass will pile UNVETTED who's-entered until Frank vets on budget page (or we later whitelist `chunkymonkey@agentmail.to` / results-app — **not** done this pass).

## Time feel

- **Light / viable for daily morning pass.** Four messages ≈ **10–15 minutes** desk time with MCP round-trips; would be faster once a small ingest script exists (list unread → get → stage → label).
- Pre-budget second pass should be even lighter (usually 0–2 late messages).
- Heaviest part is **editorial judgment** (what to stage vs skip, dedupe), not API latency.

## Workflow verdict

**Viable** for locked STAGING cadence (daily light + pre-budget). Do **not** need to rethink the two-pass model. Next hardening (optional): ingest helper script, subject fallback, Clean-time dedupe, optional AgentMail-digest auto-vet discussion with Frank.

## Not done (per brief)

- No budget HTML / PDF build.
