# Email ingest log — 2026-10-23 (weekday morning pass, Friday)

**Inbox:** `efc.weekly@agentmail.to` · **Operator:** Gazette Desk (routine "Gazette daily email check") · read-only, nothing sent. Prior log: `email-ingest-log-2026-10-22.md`.

| # | From | Subject | Vetting | Result | Labels after |
|---|------|---------|---------|--------|--------------|
| 1 | Elite Fencers Club `<elitefencersclub@111617670.mailchimpapp.com>` (Thu Oct 22, 12:19 PM ET) | Winter Camp Schedule!❄️ | auto-vetted (allowlist) | Day-by-day camp schedule (Dec 27 swag, 28 S&C, 29 yoga + lunch, 30 S&C, 31 crepes) + yoga/breathing session, K2 Fitness, headcount ask. Staged `email-mailchimp-winter-camp-schedule-2026-10-22`; fact appended to `chat-winter-camp-reminder` (body untouched). Graphic saved to `media/winter-camp-schedule-2026-10-22.png`. | `processed` |
| 2 | AgentMail `<chunkymonkey@agentmail.to>` (Fri Oct 23, 7:00 AM ET) | Club schedule · Friday, October 23 | auto-vetted (allowlist) | **ENTRY CHANGE:** Morris Cup Y14WE (Sat Oct 24, 3:00 PM) no longer lists Penelope Young (still in CDTWE Sun). Now 20 fencers / 30 entries. Data as of Oct 22 6:00 AM. NYFA YC #1 and Medeo YC #5 unchanged; Wanglei Oct 25 / Nov Cup I still empty. | `processed` |

New items: 1. Updated items: Morris Cup (entry change), Winter Camp reminder (facts), Medeo YC #5 + NYFA YC #1 (provenance refresh). Media: 1 graphic.

## Self-gather (daily quick look)
- **FencingTracker club page** (one fetch, 7:51 AM ET): 161 tournaments, newest still Artdu Open. No change. Summary: `gather-2026-10-23-ft-club.json`.
- **fencing-api:** `club-results --since 2026-10-22` (cache): 0 rows. No Elite FC tournament today; no live calls. No mismatch.

Frank ping: yes (Morris Cup entry change; Winter Camp schedule out).
