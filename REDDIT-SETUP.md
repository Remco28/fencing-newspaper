# Reddit authenticated access — setup
Goal: let the bot read r/Fencing threads/comments via OAuth. Tips only — facts still verified elsewhere.

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

## Rules for the paper
- OAuth limit ~60 req/min; cache threads per issue; 5–10 threads max per run.
- Snippet-first: title + top comments only; full pull only if the angle survives the editor filter.
- Never print usernames verbatim without need; paraphrase ("fencers online are debating X").
- Every Reddit-derived angle still needs a primary source (FIE/USA/NJ.com/email) before it prints.
- If auth breaks or limits bite: fall back to searxng snippets + Frank forwards links by email.
- Do NOT store these credentials in office memory, git, or the PDF. Env file on the runner only.
