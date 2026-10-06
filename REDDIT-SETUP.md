# Reddit authenticated access — setup
Goal: let the bot read r/Fencing threads/comments via OAuth. Tips only — facts still verified elsewhere.

## ⚠️ Reality check 2026-10-06: approval is required, self-serve is closed
Since Nov 2025 Reddit's **Responsible Builder Policy** ended self-service API access.
New apps/OAuth tokens need **manual approval**: submit "I'm a Developer → register to use the Reddit API"
via Reddit's request form, then wait — no published timeline (reports of multi-week waits, template
denials, no appeal). The CAPTCHA-loop / silent-fail on `prefs/apps` is a widely reported symptom of this.
Do NOT block the paper on Reddit approval; run the fallbacks below in the meantime.

Before retrying the form, all of these matter: every field filled (name, script, description,
about url, redirect `http://localhost:8080`), account email verified, extensions/VPN off
(or incognito / another browser), and trying `old.reddit.com/prefs/apps` as alternate.
New/low-karma accounts fail more often.

## One-time setup (Frank, ~10 min)
1. Log into reddit.com (use a dedicated account for the bot if you have one).
2. Go to https://www.reddit.com/prefs/apps/ → "create app" (bottom).
3. Fill: name `efc-paper-reader`, type **script**, description anything, about url `http://localhost`, redirect uri `http://localhost:8080`.
4. Note the **client_id** (shown under the app name, ~14 chars) and **secret**.
5. On the runner machine, install: `pip install praw`, then create env (never git, never chat):
   ```
   REDDIT_CLIENT_ID=...
   REDDIT_CLIENT_SECRET=...
   REDDIT_USERNAME=...
   REDDIT_PASSWORD=...
   REDDIT_USER_AGENT=efc-paper/1.0 by <your-reddit-username>
   ```
6. Test read-only:
   ```python
   import praw, os
   r = praw.Reddit(client_id=os.environ["REDDIT_CLIENT_ID"],
                   client_secret=os.environ["REDDIT_CLIENT_SECRET"],
                   username=os.environ["REDDIT_USERNAME"],
                   password=os.environ["REDDIT_PASSWORD"],
                   user_agent=os.environ["REDDIT_USER_AGENT"])
   for s in r.subreddit("Fencing").new(limit=5):
       print(s.title, s.url)
   ```

## ⚠️ Verdict 2026-10-06: do NOT take the Devvit/CLI path for this paper
The "create an app + download CLI" flow is Reddit's **Developer Platform (Devvit)** — a different
product from legacy script apps. Verified against Devvit docs:
- Devvit apps run **on Reddit's servers**, not on our machine; auth is platform-managed, no keys.
- Reddit API access is **limited to installation scope**: the app can only read the subreddit it is
  installed in. Reading r/Fencing requires **r/Fencing's moderators to install our app** — we don't
  moderate it, and playtests only work on auto-made test subs or subs under 200 members.
- Shipping anything real needs App Review (directory listing, external `fetch`, scheduler→email all
  gated). It's built for in-subreddit games/mod tools, not external readers.
Conclusion: Devvit is the wrong tool for "external bot reads r/Fencing for tips." The right tool is a
legacy script app (PRAW), which is approval-gated — see above. Recommendation: file the Data API
request, run fallbacks meanwhile, skip the CLI entirely.

## Rules for the paper (when OAuth works)
- OAuth limit ~60 req/min; cache threads per issue; 5–10 threads max per run.
- Snippet-first: title + top comments only; full pull only if the angle survives the editor filter.
- Never print usernames verbatim without need; paraphrase ("fencers online are debating X").
- Every Reddit-derived angle still needs a primary source (FIE/USA/NJ.com/email) before it prints.
- If auth breaks or limits bite: fall back to searxng snippets + Frank forwards links by email.
- Do NOT store these credentials in office memory, git, or the PDF. Env file on the runner only.
