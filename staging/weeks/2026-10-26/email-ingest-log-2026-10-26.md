# Email ingest log — 2026-10-26 (weekday morning pass, Monday)

**Inbox:** `efc.weekly@agentmail.to` · **Operator:** Gazette Desk (routine "Gazette daily email check") · read-only, nothing sent. Prior log: `email-ingest-log-2026-10-23.md`.

| # | From | Subject | Vetting | Result | Labels after |
|---|------|---------|---------|--------|--------------|
| 1 | Elite Fencers Club (Mailchimp) (Fri Oct 23, 10:55 AM ET) | Group Class! | auto-vetted (allowlist) | Fri/Sat Oct 23–24 day sheet (Mini Musketeers 4:15 PM, open bouting ~6:30 PM; Sat Musketeers 11 AM, Advanced 1 PM). Past dates, matches standing schedule; not staged. | `processed` |
| 2 | chunkymonkey (Sat Oct 24, 7:00 AM ET) | Club schedule · Saturday, October 24 | auto-vetted | Superseded by #4; no entry change. | `processed` |
| 3 | chunkymonkey (Sun Oct 25, 7:00 AM ET) | Club schedule · Sunday, October 25 | auto-vetted | Superseded by #4; no entry change. | `processed` |
| 4 | chunkymonkey (Mon Oct 26, 7:00 AM ET) | Club schedule · Monday, October 26 | auto-vetted | Morris Cup entries unchanged vs Oct 23 (data as of Oct 25 6 AM, could not refresh). NYFA YC #1 and Medeo YC #5 unchanged; Wanglei Oct 25 / Nov Cup I empty. Provenance refreshed. | `processed` |

New items: 0 from email.

## Self-gather (daily quick look)
- **FencingTracker club page** (one fetch, 7:51 AM ET): 164 tournaments (+3). New Elite FC results staged unvetted: Maksim Milinkovic 6th CDTME at FIE Cadet World Cup (Oct 22, venue not shown); Maksim 48th JNRME at FIE Junior WC San Jose (Oct 23); Brendan Mendez 3rd SNRME at Freehold Unrated (Oct 23). Morris Cup / Medeo #4 results not on FT yet. Summary: `gather-2026-10-26-ft-club.json`.
- **fencing-api:** `club-results --since 2026-10-22` (cache): 0 rows — mismatch vs FT, flagged. Weekend live results left for the Monday full pass.

Frank ping: yes (Maksim Cadet WC 6th to vet; API mismatch).

## Afternoon addendum (4:40 PM ET, Desk during No. 4 compose; Frank flagged the email)

| # | From | Subject | Vetting | Result | Labels after |
|---|------|---------|---------|--------|--------------|
| 5 | Elite Fencers Club (Mailchimp), to frankcng@gmail.com (Mon Oct 26, 11:38 AM ET) | Group Class + CONGRATS!🏆 | auto-vetted (allowlist) | Lessons Mon/Tue; Musketeers Group Class Mon 4:30 PM, Advanced Tue 6:00 PM (not staged for print). Congrats: Madeline Siu 1st Y8, "Josh" Jeong 2nd Y10 at Morris Cup — matches FencingTracker (prints "Joshua Jeong"). 3 photos saved to media/ (group + 2 podium). Staged `email-mailchimp-congrats-2026-10-26`. | `processed` |

Also staged: `fencingapi-cobra-details-2026-10-26` (USA Fencing page 12119, live 4:26 PM ET) for Frank's Cobra slot note. Re-checked: Medeo YC #4 (AskFRED) still only Y14 Mixed posted; NJ JO qualifier still 0 results. Nothing sent.
