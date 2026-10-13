# Gather log — 2026-10-12 (Monday full pass, Issue No. 2)

Operator: Gazette Desk (scheduled routine, 9:11 AM ET). Read-only; nothing sent.

| Source | Result |
|---|---|
| Email second pass (`efc.weekly@agentmail.to`) | No new mail since the 8:05 AM pass. All messages already `processed`. Oct 12 digest re-read: Morris Cup 19 fencers / 29 entries (matches staging). |
| AskFRED API (1 call) | Nearby epee: NJFA Div 3 & Y8–Y14 (Oct 13, 29; Nov 10; Dec 1, 8, 29), Medeo YC #5 (Nov 8), Artdu Attack (Nov 14), Medeo clinic (Nov 7–8), Medeo winter camp (Dec 27–31). Nothing staged (no Elite FC names). |
| X full pass (8 calls) | FIE timeline: Vet Worlds team epee medallists (USA bronze x2) → merged into `web-fie-vet-worlds-epee-2026-10-11`. NAC searches: only foil/sabre college posts. College/NJSIAA timelines: nothing epee. Casablanca WC confirmed by aggregator (lead only). |
| FencingTracker | October NAC results for all four Frank-confirmed fencers (Penny Y14 pending today) → `ft-nac-results-efc-2026-10-12`. Ultimate Cup RJCC registrations → `ft-ultimate-cup-efc-registrations-2026-10-12`. Possible missed NJFA Sep 29 results → `ft-njfa-sep29-possible-efc-results`. |
| AskFRED public results | Medeo YC #3 not uploaded. |
| USA Fencing | Elite/Challenger explainer (Sep 19/28) → `web-usaf-elite-challenger-explainer`; ReCord body-cord project → `web-gear-recycling-blades-cords`. Epee feed stale; no NAC recap yet. |
| FIE news + events | Vet Worlds results; epee TV calendar → `web-fie-epee-tv-calendar-2026-10-12`; Takamatsu blade recycling. |
| NJ.com / NJSIAA | NJ.com quiet; NJSIAA 2026–27 dates → `web-njsiaa-fencing-2026-27-dates`. |
| Google News RSS | Orlando Sentinel NAC gallery (link only), re-dated UNC story (stale), para Euros, a legal story (skipped). |
| FencingTimeLive | Login wall; not used. |

Detail with URLs + timestamps: `gather-2026-10-12-web.json` / `.md`.

## Clean
- Names via roster: Young, Penelope → Penny Young; Anayaà → Anayaa Sheth; WU, Caden → Caden Wu; Ash Shah-Mirani spelling still flagged (question to Frank). New names (unvetted, ask Frank): Dieko Johnson, Lillian Liu, Bradley Tsai, Brendan Mendez.
- Watch out: "Elite Fencing Academy" (Div I Elite winner's club) is not Elite FC.
- Stale/merged (marked `clean` on items, not deleted): `ft-nac-efc-registrations-2026-10-07`, `x-lead-nac-oct-results-watch`, `x-lead-veteran-worlds-tbilisi`, `gather-morris-cup-ryc-oct25`, `gather-college-path-shamel-epee`, `x-lead-passivity-p-black-explainer`.
- All new self-gather items staged `vetted: false` (scraped/official web) pending Frank's Vet.

## Budget
`budget-demo/practice-lineup.json` rewritten for Issue No. 2 (`mode: real`), served at http://127.0.0.1:8766/. Fit ≈ 39% included now, ≈ 74% if Frank vets the proposed items. Screens: `budget-demo/screens/budget-no2-2026-10-12-*.png`.
