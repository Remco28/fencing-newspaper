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

## 2026-11-16 budget submission + proof v1 compose (from 3:18 PM ET)

Frank submitted the No. 7 budget (practice:false, publish Tue. Nov. 17) at 3:18 PM ET. Ingested (decision #1); budget rebuilt as v2. Standing rules recorded with provenance "Frank budget submission 2026-11-16":

- **NJFA hold:** do not recommend any NJFA tournaments for now (unreliable organizers; padded signups; turnout often 1–2; they push their class afterwards). NJFA Dec. 1 excluded; the Nov. 30 NJFA row was dropped from Deadlines. Written into SOURCES.md, sections.json (Nearby Tournaments + Deadlines), and the NJFA item.
- **Brendan Mendez:** assume he is not a club member until Frank confirms; drop his results; never ask about him again. Manchen Friday Night item marked dropped; roster entry updated.
- **Lead:** Penny Young as drafted.

**Kiefer Meinhardt recheck at compose (3:23 PM ET, fencing-api live, official / final):** Mila Siu 3rd of 62 in Y14 Women (earned C26) and 10th of 54 in Y12 Women; Stella Kuo 20th of 62 (Y14) and 17th of 54 (Y12), both below the regional top-16 bar. Staged as `fencingapi-kiefer-meinhardt-results-2026-11-16`, unvetted. Not added to proof v1 (Frank did not include Club Results; the approved lead was written before these posted). The Kiefer placeholder sentence was omitted from the printed lead so it would not become an "also fenced" line.

## 2026-11-16 3:38 PM ET — Frank adds Kiefer results (chat t223u)

Frank said YES, add the Kiefer Meinhardt official results and share the lead between Mila Siu and Penny Young (two-bronze weekend: Penny in New Haven, Mila in Glen Allen, Va.). Print Mila's Y14 bronze (3rd of 62, Sat. Nov. 14, earned C26) and Y12 10th of 54 (Sun. Nov. 15). The C26 is the new rating mentioned earlier; Ratings Earned may be a line in the lead or a small box. Stella Kuo's 20th (Y14) and 17th (Y12) stay out (below the regional top-16 bar; no "also fenced" line). Official results from the 3:23 PM ET fencing-api live recheck (final=true) stand. Item `fencingapi-kiefer-meinhardt-results-2026-11-16` is now vetted via this chat. Club Results as a section remains excluded; the results run in the shared lead.

## 2026-11-16 9:51 PM ET — Frank sends Clark to the club email (t226u)

Frank (chat, 9:51 PM ET): the remaining No. 7 content is in the Gazette inbox, from the club — holiday party announcement and photos of Mila and Stella plus Penny (Penelope, she goes by Penny).

**Email found** (inbox `efc.weekly@agentmail.to`, unread / not yet `processed`): Elite Fencers Club `<elitefencersclub@111617670.mailchimpapp.com>` → `frankcng@gmail.com` (copy in the Gazette inbox). Subject: Group Class + HOLIDAY PARTY! Sent 2026-11-16 10:18 AM ET (message-id `<d0ff43e598e6fe5cb242389b7.f656c71db1.20261116151823.8f59fffb3b.49d225ef@mail67.atl91.mcsv.net>`). DKIM/DMARC pass. Auto-vet allowlist plus Frank's chat.

**Holiday party, as written:** Friday, December 11th; food, drinks and snacks; everyone welcome; mark your calendars; hope you can join to celebrate everything we have accomplished. No time, venue, cost, or RSVP in the email (the 17 Watchung Ave line is the newsletter sign-off). Staged as `email-holiday-party-2026-12-11`. Same-email class reminders were not staged (classes stay excluded).

**Photos extracted** (Mailchimp CDN; logo, social icons, and a 1×1 tracker skipped) into `staging/weeks/next/media/` and `issues/2026-11-17/media/`, EXIF-normalized, not cropped:
- `mila-siu-stella-kuo-kiefer-meinhardt-2026-11-14.jpg` (480×640) — Mila, left, with the Y14 bronze, and Stella Kuo. Printed with the lead.
- `penny-young-pizza-ryc-2026-11-15.jpg` (480×640) — Penny Young with the Y12 bronze in New Haven. Printed with the lead.
- `kiefer-meinhardt-podium-group-2026-11-14.jpg` (640×480) — wider Y14 podium group; staged, not printed (Stella not clearly identifiable; other medalists not named in the email).
