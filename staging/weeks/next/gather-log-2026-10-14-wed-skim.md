# Gather log — 2026-10-14 (Wednesday skim, Issue No. 3)

Operator: Gazette Desk (scheduled routine, 9:55 AM ET). Read-only; nothing sent.

| Source | Result |
|---|---|
| FencingTracker club page (1 fetch, 9:56 AM ET) | Top of page unchanged since 7:54 AM look: Artdu (Sullivan 2nd), October NAC. No new Elite FC results. |
| Google News RSS (`fencing epee`, `+New Jersey`) | Para Euros (Coutya), India U-23 selections, college NAC recaps (UNC, Air Force), Casablanca WC preview. Nothing local. NJ variant: nothing recent. |
| AskFRED API (1 call) | Nearby epee: Medeo YC #4 (Oct 25, close Oct 24) new to staging; NJFA Div 3/Y8–Y14 (Oct 29; Nov 10; Dec 1, 8, 29); Medeo YC #5 (Nov 8); Medeo Ari Simmons clinic (Nov 7–8); Artdu Attack (Nov 14); Medeo winter camp (Dec 27–31). |
| fencing-api (cross-check, 5 calls + polling) | Morris Cup (usfa 12095, cached 6:01 AM ET): 29 EFC entries, agrees with digest. Medeo #5 (live): agrees with digest (4 EFC). Medeo #4 (live): Nora Li in Y10 Mixed → `fencingapi-medeo-yc4-entries-2026-10-14`. Catalog: Ultimate Cup prereg_close Oct 13. Ultimate Cup live entrants not fetched (client call cap). |
| USA Fencing news | Oct 5: "Never Too Late" (Vic Bianchini, sabre veteran) — not epee, skipped. Foundation leadership news (Oct 5), Volunteer Hub (Sep 29) — not staged. Epee feed (JS) stale. |
| NJ.com / NJSIAA | Quiet (still last season); NJSIAA dates unchanged (already staged). |
| X skim (3 calls) | FIE: Vet Worlds women's epee medals incl. Leslie Marx (USA) gold Vet-50 → `x-fie-vet-worlds-women-epee-2026-10-13`. NJIT: only RollTech donation RTs. Epee search: Casablanca WC starts Oct 15 (already on No. 2 TV list); a Div I Challenger bronze story (not ours). |

## Data issues for Frank (fencing-api)
- `GET /v1/tournaments?state=NJ,NY&from=…&to=…` returned 439 tournaments nationwide (CA, MT, MN, FL…): the `state` filter seemed to be ignored. Many RYC/RJCC rows (Morris Cup, Ultimate Cup) have `state: null`, so a state filter would drop them anyway.
- Cached catalog call returned `404 not_cached` (needed `--live`), as documented.
- Client note: polling a 202 job counts against `scripts/fencingapi.py`'s 8-call cap, so one slow USFA entrants job can exhaust it.
