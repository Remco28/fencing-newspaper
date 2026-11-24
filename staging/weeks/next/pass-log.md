# Pass log — Issue No. 8 (staging/weeks/next)

## 2026-11-24 daily email check + FencingTracker quick look (8:01 AM ET)

Follows the 2026-11-23 Monday full pass (commit 6fafbc6).

**Email (AgentMail efc.weekly):** one new message, ingested and labeled processed.

- Club Mailchimp "Group Class! + Thanksgiving" (Mon Nov 23, 9:56 AM ET; allowlisted, auto-vetted). Lessons Mon+Tue and class times (Musketeers 4:30 p.m., Advanced 6:00 p.m.) match the standing schedule. Closure dates unchanged (Wed 11/25–Fri 11/27). Reopen date is now **Saturday, Nov. 28** — the later email confirms the Nov. 20 "Saturday 12/28" typo; Thanksgiving item body updated and the typo flag for Frank is cleared. Congratulates Nico Ng on a top-16 at the November NAC and Christina Jiang on 1st in Y12 Freehold. Two content photos extracted (logo / social / 1×1 pixel skipped). No other new mail. No chunkymonkey club-schedule digest since Mon. Nov. 16 (already flagged yesterday).

**FencingTracker** (1 fetch, club results page, 7:53 AM ET): **new November NAC results** (absent yesterday). Official cross-check below. Freehold Youth and Freehold Junior unchanged. Manchen still only Brendan Mendez; skipped per standing rule.

**fencing-api** (5 calls: 1 cached club-results since Nov. 16, then live NAC catalog + 4 epee event results): cache still had only Freehold Youth. Live official results (final=true) agree with FencingTracker places:

- Nico Ng tied for **15th of 257** in Cadet Men's Epee (Sat. Nov. 21) — the club's "top 16." Also tied for 90th of 351 in Junior Men (Sun. Nov. 22).
- Athreya Aravind tied for 55th of 349 in Division I Men (Mon. Nov. 23) and tied for 83rd of 351 in Junior Men.
- Anayaa Sheth (official "Sheth, Anayaà") tied for 85th of 220 in Junior Women (Fri. Nov. 20).
- No ratings earned. Field sizes are official finishers-list counts (catalog official_competitors ran slightly higher for JNRME/JNRWE/DV1ME). No place-data mismatch with FencingTracker.

**Staged:** ft-november-nac-results-2026-11-24 (unvetted; proposed lead). Thanksgiving item updated (Sat. 11/28 confirmed, auto-vetted). Jiang podium photo + NAC strip photo in media/ (auto-club-mailchimp; ask Frank to confirm the NAC photo is Nico before a named caption). Freehold Youth item gets the club confirmation of Jiang's gold (Jeong still unvetted).

**For Frank:** Nico's cadet T15 of 257 is a strong new result and a natural No. 8 lead. The Monday Budget did not have these NAC results. Confirm the NAC photo, and whether he wants a revised Budget.

## 2026-11-23 Monday full pass + pre-budget email pass (9:00–9:15 AM ET)

Follows the 7:56 AM daily pass (commit ba176ae: Thanksgiving closure, Freehold Youth results, Xinxuewei Chen 7th).

**Email (AgentMail efc.weekly)** second pass (9:00 and 9:13 AM ET): nothing new; every message since Nov. 13 is already `processed`. No chunkymonkey club-schedule digest since Mon. Nov. 16 (flag for Frank: digest may have stopped).

**FencingTracker** (2 fetches):
- Registrations page (Monday-only check, 9:01 AM ET): November NAC 5/3 (over; results watch); Freehold Youth 2/2 (past); Cobra 26/16 unchanged; December SJCC 5/3 (Nico Ng, Amina Gore, Anayaa Sheth) → On the Road item, unvetted; Z1 11/7 unchanged; Fairfax now 14/6 (was 7/4; adds Connor Anderson Div II/Cadet/Y14, Noah Gore Div II/Cadet/Junior, Amina Gore D1A/Div II, Sarah Sun Y14W, Eric Anderson and Kang Sun veteran events); Austin 3/1, Boston 1/1, Neil Lazar 1/1, JO + January NAC 6/3, Capitol Clash 13/8 (adds Clara Liu Y10W), MCW Cup 2/1, February NAC 2/1 (Maksim Milinkovic), **new: Duel of the East Coast 2/1 (Caden Wu, Feb. 27–28)**, **new: March NAC 6/4 (Noah Gore Y14ME + DV2ME, Caden Wu DV2ME, Christina Jiang Y12WE, Mila Siu Y12WE + Y14WE)** → staged unvetted for the March NAC feature, Cherry Blossom 1/1, American Challenge 4/3. Not added to roster this pass (not printing): Sarah Sun, Kang Sun, Clara Liu.
- Club results page (9:02 AM ET): unchanged since 7:51 AM (Freehold Youth: Jiang 1st, Jeong 3rd; Freehold Junior: Chen 7th). No November NAC rows. Manchen (Brendan Mendez) skipped per standing rule.

**fencing-api** (~8 calls): November NAC (12316) catalog + JNRWE/CDTME/JNRME results — empty, final=false (served from the 7:53 AM cache). USA Fencing tournament page 12316 fetched directly: no results. Cobra (12119) live: days unchanged, all events capped; entrant counts recorded on the Cobra item. Z1 (12141), Fairfax (12154), JO (12330) fee periods → Deadlines. Artdu Dec. 6 AskFRED entries live: 0 in all four events. No API-vs-direct mismatch.

**AskFRED** (2 calls): upcoming near Chatham — Artdu Dec. 6 (0 entries), NJFA Dec. 1/8/29 (hold), Bernards HS Dec. 19, Columbia HS Cougar Clash Feb. 20, Morris Knolls Frosh/Soph Jan. 10, Medeo winter camp, Melcher Grand Prix (June). All known; nothing new staged.

**Web**: USA Fencing March NAC page re-fetched (unchanged facts; schedule still empty; withdrawal deadline still contradicts itself; GRACE fee-waiver deadline TBD). USA Fencing news: priority-window explainer (February NAC) — not staged. FIE news: 2026 FIE Awards Gala (Nov. 22) and Fair Play Trophy (Kruz Schembri + Gilles Martinage) → secondary draft; ComEx moved 2027 Junior & Cadet Worlds to Erzurum, Apr. 1–9 (noted on Epee on Screen item). Google News RSS: college headlines (Stevens at Vassar Invitational, FDU preview) noted on the college item; a Virginia lawsuit against USA Fencing/a fencing academy seen in headlines, not staged. Club website: schedule unchanged (Friday Mini Musketeers listed 4:00 vs 4:15 per Frank/club email); camps page unchanged. NJ HS: season not started.

**X** (3 calls): @FIE_fencing timeline + one epee search — gala/Congress posts (leads; facts taken from fie.org).

**Clean**: names via roster (Penelope → Penny Young; Anayaà → Anayaa Sheth; WU → Caden Wu). Dropped as stale to `dropped-2026-11-23.json`: Freehold Youth entries (past; results item supersedes), Kiefer Meinhardt podium photo item (No. 7 covered Kiefer; media file and manifest kept). Deadlines and Epee on Screen rebuilt.

**New drafts (unvetted)**: March NAC feature (~285w, proposed lead), "The Touch He Gave Back" (Fair Play, ~140w), By the Book "Two of Everything" (t.117, ~90w).

**Budget**: No. 8 v1 built (target Tue. Nov. 24, alt Wed. Nov. 25). Fill ~17% now, ~51% if Frank vets the proposals, ~72% with filler (holiday party, Epee on Screen, Photo from History, college short; not counting the classes table).
