# Pass log — Issue No. 7 (staging/weeks/next)

## 2026-11-16 Monday full pass + pre-budget email pass (8:51–9:35 AM ET)

**FencingTracker** (2 fetches, 8:51 AM ET): club results page unchanged since the 8:22 AM daily look (newest: Freehold Nov. Open — Nico Ng 5th; Manchen Friday Night — Brendan Mendez 5th). No Pizza RYC / Kiefer Meinhardt rows yet. Registrations page (Monday-only check): November NAC now 5 entries / 3 fencers (new: Athreya Aravind, DV1ME, Mon. Nov. 23); Cobra 26/16 unchanged; Dec. SJCC 5/3, Z1 11/7, Fairfax 7/4, Austin, Boston, Neil Lazar, JO + Jan. NAC, Capitol Clash, MCW Cup, Feb. NAC, Cherry Blossom, American Challenge listed for later issues. No Connecticut event other than Pizza RYC (New Haven) that weekend.

**fencing-api** (~14 calls, live where needed):
- Freehold Nov. Open D1AXE results (final): Nico Ng 5th of 30, no rating earned.
- Pizza RYC/RJCC (usfa 12111) results (final): Penny Young 3rd/52 Y12W, 13th/67 Y14W, 41st Cadet W (below bar); Amina Gore 13th/54 Cadet W, 16th/54 Junior W. No ratings earned for Elite FC.
- Kiefer Meinhardt (12117) Y14WE/Y12WE results: 0 rows, final=false (not posted).
- November NAC (12316) entries: job 710 → refreshed; matches FT registrations.
- Z1 (12141), Fairfax (12154), JO (12330) fee periods → Deadlines box.
- AskFRED NJFA Dec. 1 entries: Owen Li (D & Under Mixed, confirmed). Artdu Dec. 6: 0 entries.
- Cobra (12119) catalog (cached Oct. 26) details_text → For the Parents draft.
- No API-vs-direct mismatch found. Note: `scripts/fencingapi.py get /v1/guide` crashes (guide is markdown, client expects JSON) — client issue, not data.

**AskFRED** (2 calls): upcoming near Chatham: Artdu Epee Dec. 6, NJFA Div. 3/Y8–Y14 Dec. 1, Dec. 8, Dec. 29 (new to staging), Bernards HS Dec. 19 (staged), Cobra.

**Email (AgentMail efc.weekly)** second pass: nothing new since the 7:50 AM daily pass (all 5 messages since Nov. 13 already `processed`). Removed leftover `unread` from 5 older processed messages (Nov. 2–5).

**X** (3 calls, leads): FIE tier A — Bern men's / Wuxi women's epee World Cups (individual + team) → staged unvetted secondary. November NAC search: 0 posts.

**Web**: Google News RSS (epee; NJ): college Penn Elite Invitational (Nov. 14–15) headlines → note on college item; nothing NJ-fencing. USA Fencing epee news page: no new items. FIE calendar search endpoint returned non-JSON (Epee on Screen not refreshed). NJ HS out of season.

**Clean**: names via roster (Penelope → Penny Young; Anayaà → Anayaa Sheth; WU → Caden Wu); Owen Li already in roster. Dropped as stale (moved to `dropped-2026-11-16.json`): Pizza entries, Freehold entries, Nov. 14–15 calendar, Dakar YOG graf. Deadlines and Epee on Screen rows rebuilt.

**Budget**: No. 7 v1 built (target Tue. Nov. 17, alt Wed. Nov. 18). Fill ~28% now, ~61% if Frank vets the proposals, ~88% with held filler (Photo from History, Epee on Screen, college short).
