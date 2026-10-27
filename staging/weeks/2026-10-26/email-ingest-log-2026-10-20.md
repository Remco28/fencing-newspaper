# Email ingest log — 2026-10-20 (weekday morning pass, Tuesday)

**Inbox:** `efc.weekly@agentmail.to` · **Operator:** Gazette Desk (routine "Gazette daily email check") · read-only, nothing sent. Prior log: `email-ingest-log-2026-10-19.md`.

| # | From | Subject | Vetting | Result | Labels after |
|---|------|---------|---------|--------|--------------|
| 1 | Elite Fencers Club `<elitefencersclub@111617670.mailchimpapp.com>` (Mon Oct 19, 12:45 PM ET) | Group Class! | auto-vetted (allowlist) | Routine reminder: all lessons Mon + Tue; Musketeers Group Class Mon 4:30 PM; Advanced Group Class Tue 6:00 PM. Matches the standing schedule; added as provenance only. | `processed` |
| 2 | AgentMail `<chunkymonkey@agentmail.to>` (Tue Oct 20, 7:00 AM ET) | Club schedule · Tuesday, October 20 | auto-vetted (allowlist) | **Morris Cup CHANGED:** Penelope Young (prints Penny Young) added to Sat Y14WE 3:00 PM; now 20 fencers / 31 entries. Medeo YC #5 unchanged (4). Wanglei Oct 25 and Wanglei Nov Cup I (Nov 8): nobody signed up. Newly listed: NYFA Youth Cup #1 (NYFA Brooklyn, Nov 8), nobody signed up (not staged, same as the empty Wanglei cups). | `processed` |

Updated items: `email-agentmail-morris-cup-entries-2026-10-07` (body, change log, count, provenance), `email-agentmail-medeo-yc5-entries-2026-10-14` (provenance), `web-efc-standing-schedule` (provenance).
New items: none. Media: none.

## Self-gather (daily quick look)
- **FencingTracker club page** (one fetch, 7:51 AM ET): 161 tournaments / 1208 results, same as Oct 19. Newest still Artdu Open. Nothing new; NJ JO qualifier (Oct 18) still not on FT. Summary: `gather-2026-10-20-ft-club.json`.
- **fencing-api:** `club-results --since 2026-10-19` (cache): 0 rows. Live AskFRED results for the NJ JO qualifier (7:51 AM ET): 0 items, `final: false`. USA Fencing Morris Cup entries (cache, 6:02 AM ET): 31 Elite FC entries / 20 fencers, all approved, Penelope Young in Y14WE. No API-vs-direct mismatch.

Frank ping: yes, entry change (Penny Young added to Morris Cup Y14WE).
