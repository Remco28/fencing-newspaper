# Email ingest log — 2026-10-19 (weekday morning pass, Monday)

**Inbox:** `efc.weekly@agentmail.to` · **Operator:** Gazette Desk (routine "Gazette daily email check") · read-only, nothing sent.

Context: No. 3 was approved and published Oct 18 (16:08 ET) but staging had not rolled. Rolled at this pass: old `next/` → `staging/weeks/2026-10-19/` (history), `after-next/` → `next/` (**Issue No. 4, week of Oct 26**), fresh empty `after-next/`. Carried into No. 4 with `carried_from`: Morris Cup entries, Medeo YC #4 and #5 entries, Ultimate Cup registrations, NJ JO qualifier results watch, Deadlines box, Epee on Screen, standing schedule, Winter Camp (reference only). Prior log: `staging/weeks/2026-10-19/email-ingest-log-2026-10-18.md`.

| # | From | Subject | Vetting | Result | Labels after |
|---|------|---------|---------|--------|--------------|
| 1 | AgentMail `<chunkymonkey@agentmail.to>` | Club schedule · Monday, October 19 | auto-vetted (allowlist) | Morris Cup unchanged (30 entries; data as of Oct 18 6:01 PM, could not refresh). Medeo YC #5 unchanged (4). Wanglei October Cup (Oct 25) and a newly listed Wanglei November Cup I: Senior Epee (Nov 8): nobody signed up. | `processed` |

Updated items: `email-agentmail-morris-cup-entries-2026-10-07`, `email-agentmail-medeo-yc5-entries-2026-10-14` (provenance).
New items: none. Media: none.

## Self-gather (daily quick look)
- **FencingTracker club page** (one fetch, 7:59 AM ET): 161 tournaments / 1208 results, same as Oct 16. Newest still Artdu Open (Adela Sullivan 2nd). Nothing new; NJ JO qualifier (Oct 18) not on FT yet. Summary: `gather-2026-10-19-ft-club.json`.
- **fencing-api:** `club-results --since 2026-10-16` (cache): 0 rows. Live AskFRED results for the NJ JO qualifier (8:00 AM ET): 0 items, `final: false`. No API-vs-direct mismatch.

Frank ping: none needed (nothing new to vet; no entry changes).
