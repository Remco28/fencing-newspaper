# Email ingest log — 2026-10-22 (weekday morning pass, Thursday)

**Inbox:** `efc.weekly@agentmail.to` · **Operator:** Gazette Desk (routine "Gazette daily email check") · read-only, nothing sent. Prior log: `email-ingest-log-2026-10-21.md`.

| # | From | Subject | Vetting | Result | Labels after |
|---|------|---------|---------|--------|--------------|
| 1 | Elite Fencers Club `<elitefencersclub@111617670.mailchimpapp.com>` (Wed Oct 21, 9:53 AM ET) | Group Class! | auto-vetted (allowlist) | Routine day sheet (Musketeers 5:00 / Footwork 6:30 Wed; Advanced Group Thu 6:00) + Medeo YC #4 registration link. Staged `email-mailchimp-group-class-2026-10-21`. Logo only, no photo extract. | `processed` |
| 2 | AgentMail `<chunkymonkey@agentmail.to>` (Thu Oct 22, 7:00 AM ET) | Club schedule · Thursday, October 22 | auto-vetted (allowlist) | **ENTRY CHANGE:** NYFA Youth Cup #1 (Nov 8, NYFA Brooklyn) now lists Bryce Cheng, Y10 Mixed Epee 9:00 AM (was nobody). Staged `email-agentmail-nyfa-youth-cup1-entries-2026-10-22`. Morris Cup unchanged (30 entries; data as of Oct 21 6:02 PM, could not refresh). Medeo YC #5 unchanged (4). Wanglei Oct 25 / Nov Cup I still empty. | `processed` |

New items: 2. Updated items: Morris Cup + Medeo YC #5 (provenance refresh only). Media: none.

## Self-gather (daily quick look)
- **FencingTracker club page** (one fetch, 7:56 AM ET): 161 tournaments / 1208 results, same as Oct 21. Newest still Artdu Open. Summary: `gather-2026-10-22-ft-club.json`.
- **fencing-api:** `club-results --since 2026-10-21` (cache): 0 rows. No Elite FC tournament today; no live calls. No mismatch.

Frank ping: yes (entry change: Bryce Cheng into NYFA Youth Cup #1).
