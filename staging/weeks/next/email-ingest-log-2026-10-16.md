# Email ingest log — 2026-10-16 (daily morning pass)

**Inbox:** `efc.weekly@agentmail.to` · **Operator:** Gazette Desk (scheduled routine, ~8:00 AM ET) · read-only, nothing sent.

Context: `next` is **Issue No. 3 (week of Oct 19)**. Prior same-week log: `email-ingest-log-2026-10-15.md`.

| # | From | Subject | Vetting | Result | Labels after |
|---|------|---------|---------|--------|--------------|
| 1 | AgentMail `<chunkymonkey@agentmail.to>` | Club schedule · Friday, October 16 | auto-vetted (allowlist) | **Morris Cup CHANGED:** ADD Sheth, Anayaà → Sat JNRWE 8:00 AM (print **Anayaa Sheth**). Now 20 fencers / 30 entries (was 19/29). Data stamped Oct 15, 12:05 PM (could not refresh). Medeo #5 identical (4/4; data Oct 16 6:00 AM). Wanglei Oct 25 / Nov 8 still empty — not staged. | `processed` |

Updated items: `email-agentmail-morris-cup-entries-2026-10-07` (body + `entries_count` + `entries_change_log` + provenance; entry list change), `email-agentmail-medeo-yc5-entries-2026-10-14` (provenance + `entries_last_confirmed` only).

New items: none.

Roster check: Anayaa Sheth on-roster (`anayaa-sheth`; print Anayaa Sheth). Medeo #5 off-roster names unchanged (Samuel SarroWaite, Nora Li, Owen Li, Christina Jiang).

Media: none (digest is HTML text; no photo attachments).

Also this pass (non-email): FencingTracker club results once — no new Elite FC rows vs Oct 15 / Issue No. 2 (Artdu + October NAC still most recent). fencing-api `club-results --since 2026-10-15` empty; `--since 2026-10-01` (cache) still only Christina Jiang Medeo #3 — already printed. No API↔FT mismatch beyond known Medeo #3 absence from FT club page.

Frank ping: **yes** — Morris Cup entry list changed (Anayaa Sheth added to Sat JNRWE).
