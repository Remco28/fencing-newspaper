#!/usr/bin/env python3
"""fencing-api client for En Garde Gazette gather (gentle use).

Frank's API (https://fencingapi.teamremco.org, guide: /v1/guide) fronts AskFRED,
USA Fencing and FencingTracker. Reads FENCING_API_KEY from the environment or the
gitignored repo .env. Never prints the key. Soft call cap; honors 429 Retry-After;
polls 202 jobs. Staged data from here uses source "fencingapi" and is unvetted.

Examples (repo root):
  python3 scripts/fencingapi.py health
  python3 scripts/fencingapi.py club-results --since 2026-09-01
  python3 scripts/fencingapi.py search "Maksim Milinkovic"
  python3 scripts/fencingapi.py get /v1/usfa/tournaments/12095
  python3 scripts/fencingapi.py get "/v1/tournaments?state=NJ,NY" --live
Default is cached reads; pass --live only when fresh data is needed (limited: 20 scrapes/min/key).
"""
from __future__ import annotations
import argparse, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

BASE = "https://fencingapi.teamremco.org"
CLUB = "Elite Fencers Club"
DEFAULT_CALL_CAP = 8
POLL_SEC = 4
POLL_MAX_SEC = 250

_calls = 0
_cap = DEFAULT_CALL_CAP


def _key() -> str | None:
    if os.environ.get("FENCING_API_KEY"):
        return os.environ["FENCING_API_KEY"]
    here = Path(__file__).resolve()
    for p in (Path.cwd() / ".env", here.parent.parent / ".env"):
        if p.is_file():
            for line in p.read_text().splitlines():
                if line.startswith("FENCING_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"\'')
    return None


def _req(path: str, params: dict | None = None) -> tuple[int, dict]:
    global _calls
    url = BASE + path
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    for attempt in range(4):
        if _calls >= _cap:
            raise SystemExit(f"fencingapi: call cap {_cap} reached")
        _calls += 1
        r = urllib.request.Request(url, headers={"User-Agent": "en-garde-gazette/1"})
        k = _key()
        if k:
            r.add_header("X-API-Key", k)
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                return resp.status, json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            body = json.loads(e.read() or b"{}") if e.headers.get_content_type() == "application/json" else {}
            if e.code == 429:
                wait = float(e.headers.get("Retry-After") or body.get("retry_after") or 10)
                print(f"fencingapi: 429, waiting {wait:.0f}s", file=sys.stderr)
                time.sleep(wait)
                continue
            return e.code, body
    return 429, {"error": "rate_limited"}


def get(path: str, live: bool = False, **params) -> tuple[int, dict]:
    if live:
        params["live"] = "true"
    code, body = _req(path, params)
    t0 = time.time()
    while code == 202 and body.get("job_id") and time.time() - t0 < POLL_MAX_SEC:
        time.sleep(POLL_SEC)
        code, job = _req(f"/v1/jobs/{body['job_id']}")
        if job.get("status") == "done":
            return 200, job.get("result", job)
        if job.get("status") == "failed":
            return 502, job
        code = 202
    return code, body


def main() -> None:
    global _cap
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--call-cap", type=int, default=DEFAULT_CALL_CAP)
    ap.add_argument("--live", action="store_true", help="allow a fresh scrape (use sparingly)")
    ap.add_argument("--summary", action="store_true", help="one-line summary on stderr")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("health")
    c = sub.add_parser("club-results"); c.add_argument("--since"); c.add_argument("--club", default=CLUB)
    s = sub.add_parser("search"); s.add_argument("name")
    f = sub.add_parser("fencers"); f.add_argument("name")
    g = sub.add_parser("get"); g.add_argument("path")
    a = ap.parse_args()
    _cap = a.call_cap
    if a.cmd == "health":
        code, body = get("/v1/health")
    elif a.cmd == "club-results":
        code, body = get("/v1/results", club=a.club, since=a.since)
    elif a.cmd == "search":
        code, body = get("/v1/tracker/search", live=a.live, q=a.name)
    elif a.cmd == "fencers":
        code, body = get("/v1/fencers", q=a.name)
    else:
        code, body = get(a.path, live=a.live)
    json.dump({"http": code, **body}, sys.stdout, indent=2, ensure_ascii=False); print()
    if a.summary:
        print(f"fencingapi: http {code} source={body.get('source')} fetched_at={body.get('fetched_at')} "
              f"items={len(body.get('items') or [])} calls={_calls}", file=sys.stderr)


if __name__ == "__main__":
    main()
