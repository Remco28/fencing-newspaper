# Pass log — Issue No. 8 (staging/weeks/next)

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
