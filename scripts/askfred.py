#!/usr/bin/env python3
"""AskFRED API client for En Garde Gazette gather (gentle use).

Reads ASKFRED_API_KEY from the environment or a gitignored .env next to the
repo root / cwd. Never prints the key. Caps requests; backs off on HTTP 429.

Docs: https://help.askfred.net/en/articles/14068759-getting-started-w-askfred-s-api
Endpoints: https://help.askfred.net/en/articles/10328385-api-endpoints-data

Examples (from repo root):
  set -a && source .env && set +a
  python3 scripts/askfred.py me
  python3 scripts/askfred.py tournaments --summary
  python3 scripts/askfred.py tournaments --radius 100 --per-page 10
  python3 scripts/askfred.py tournament <uuid>
  python3 scripts/askfred.py events <uuid>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

BASE = "https://www.askfred.net/api/v1"
# Elite Fencers Club / Chatham NJ area
DEFAULT_LAT = 40.7409
DEFAULT_LON = -74.3838
DEFAULT_RADIUS_MILES = 75
DEFAULT_WEAPON = "epee"
DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 50
# Soft cap per process — Gazette gather should stay well under this
DEFAULT_CALL_CAP = 8
MAX_RETRIES_429 = 4
BACKOFF_BASE_SEC = 5.0


def _load_dotenv() -> None:
    """Load ASKFRED_API_KEY from .env if not already in the environment."""
    if os.environ.get("ASKFRED_API_KEY"):
        return
    here = Path(__file__).resolve()
    candidates = [
        Path.cwd() / ".env",
        here.parent.parent / ".env",  # repo root when script is scripts/askfred.py
        here.parent / ".env",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip("'").strip('"')
                if key == "ASKFRED_API_KEY" and val and "ASKFRED_API_KEY" not in os.environ:
                    os.environ["ASKFRED_API_KEY"] = val
                    return
        except OSError:
            continue


def _api_key() -> str:
    _load_dotenv()
    key = os.environ.get("ASKFRED_API_KEY", "").strip()
    if not key:
        print(
            "error: ASKFRED_API_KEY not set. Put it in a gitignored .env or export it.",
            file=sys.stderr,
        )
        sys.exit(2)
    return key


class AskFredClient:
    def __init__(self, call_cap: int = DEFAULT_CALL_CAP) -> None:
        self.key = _api_key()
        self.call_cap = max(1, call_cap)
        self.calls = 0

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        if self.calls >= self.call_cap:
            raise RuntimeError(
                f"call cap reached ({self.call_cap}). Raise --call-cap only if you must."
            )
        q = {k: v for k, v in (params or {}).items() if v is not None and v != ""}
        url = f"{BASE}{path}"
        if q:
            url = f"{url}?{urllib.parse.urlencode(q)}"

        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self.key}",
                "Accept": "application/vnd.api+json, application/json",
                "User-Agent": "EnGardeGazette/1.0 (Elite FC weekly; gentle gather)",
            },
            method="GET",
        )

        attempt = 0
        while True:
            self.calls += 1
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    body = resp.read().decode("utf-8")
                    if not body:
                        return None
                    return json.loads(body)
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < MAX_RETRIES_429:
                    wait = BACKOFF_BASE_SEC * (2**attempt)
                    print(
                        f"askfred: 429 rate limited; sleeping {wait:.0f}s "
                        f"(attempt {attempt + 1}/{MAX_RETRIES_429})",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                    attempt += 1
                    # count the retry toward the cap too
                    if self.calls >= self.call_cap:
                        raise RuntimeError(
                            f"call cap reached ({self.call_cap}) while backing off on 429"
                        ) from e
                    continue
                err_body = e.read().decode("utf-8", errors="replace")[:500]
                raise RuntimeError(f"HTTP {e.code} for {path}: {err_body}") from e
            except urllib.error.URLError as e:
                raise RuntimeError(f"network error for {path}: {e}") from e


def _data_list(payload: Any) -> list[dict[str, Any]]:
    if payload is None:
        return []
    data = payload.get("data") if isinstance(payload, dict) else payload
    if data is None:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _attrs(item: dict[str, Any]) -> dict[str, Any]:
    a = item.get("attributes")
    return a if isinstance(a, dict) else {}


def summarize_me(payload: Any) -> str:
    items = _data_list(payload)
    if not items:
        return "me: (empty response)"
    a = _attrs(items[0])
    bits = [f"id={items[0].get('id', '?')}"]
    for k in ("email", "name", "full_name", "display_name"):
        if a.get(k):
            bits.append(f"{k}={a[k]}")
            break
    return "me: " + " ".join(bits)


def summarize_tournaments(payload: Any) -> str:
    items = _data_list(payload)
    lines = [f"tournaments: {len(items)} result(s)"]
    for item in items:
        a = _attrs(item)
        tid = item.get("id", "?")
        name = a.get("name") or a.get("title") or "(unnamed)"
        start = a.get("start_date") or a.get("start") or "?"
        end = a.get("end_date") or ""
        city = a.get("city") or ""
        state = a.get("state") or a.get("region") or ""
        loc = ", ".join(x for x in (city, state) if x)
        close = a.get("prereg_close") or a.get("close_of_reg") or ""
        extra = f"  close={close}" if close else ""
        when = start if not end or end == start else f"{start}→{end}"
        lines.append(f"  - {when}  {name}  ({loc})  id={tid}{extra}")
        lines.append(f"    https://www.askfred.net/tournaments/{tid}")
    return "\n".join(lines)


def summarize_events(payload: Any) -> str:
    items = _data_list(payload)
    lines = [f"events: {len(items)} result(s)"]
    for item in items:
        a = _attrs(item)
        eid = item.get("id", "?")
        name = a.get("name") or a.get("title") or "(unnamed)"
        weapon = a.get("weapon") or ""
        gender = a.get("gender") or ""
        age = a.get("age_limit") or a.get("age") or ""
        close = a.get("close_of_reg") or ""
        bits = " / ".join(x for x in (weapon, gender, age) if x)
        extra = f"  close={close}" if close else ""
        lines.append(f"  - {name}  [{bits}]  id={eid}{extra}")
    return "\n".join(lines)


def cmd_me(client: AskFredClient, _args: argparse.Namespace) -> Any:
    return client.get("/me")


def cmd_tournaments(client: AskFredClient, args: argparse.Namespace) -> Any:
    start = args.start_date_gteq or date.today().isoformat()
    per_page = min(max(1, args.per_page), MAX_PER_PAGE)
    params = {
        "latitude": args.lat,
        "longitude": args.lon,
        "radius_miles": args.radius,
        "weapon": args.weapon,
        "start_date_gteq": start,
        "per_page": per_page,
        "page": args.page,
    }
    return client.get("/tournaments", params)


def cmd_tournament(client: AskFredClient, args: argparse.Namespace) -> Any:
    return client.get(f"/tournaments/{args.id}")


def cmd_events(client: AskFredClient, args: argparse.Namespace) -> Any:
    return client.get(f"/tournaments/{args.id}/events", {"per_page": min(args.per_page, MAX_PER_PAGE)})


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Gentle AskFRED client for Clark Kent's gather (epee / Chatham defaults)."
    )
    p.add_argument(
        "--call-cap",
        type=int,
        default=DEFAULT_CALL_CAP,
        help=f"max HTTP calls this run (default {DEFAULT_CALL_CAP})",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="print a human summary to stderr; JSON still goes to stdout",
    )
    p.add_argument(
        "--quiet-json",
        action="store_true",
        help="with --summary, suppress JSON on stdout (summary only on stderr)",
    )

    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("me", help="GET /me — verify auth")

    t = sub.add_parser("tournaments", help="nearby tournaments (default: Chatham epee)")
    t.add_argument("--lat", type=float, default=DEFAULT_LAT)
    t.add_argument("--lon", type=float, default=DEFAULT_LON)
    t.add_argument("--radius", type=float, default=DEFAULT_RADIUS_MILES, help="miles (default 75)")
    t.add_argument("--weapon", default=DEFAULT_WEAPON)
    t.add_argument(
        "--start-date-gteq",
        dest="start_date_gteq",
        default=None,
        help="YYYY-MM-DD (default: today)",
    )
    t.add_argument("--per-page", type=int, default=DEFAULT_PER_PAGE)
    t.add_argument("--page", type=int, default=1)

    one = sub.add_parser("tournament", help="GET /tournaments/:id")
    one.add_argument("id", help="tournament uuid")

    ev = sub.add_parser("events", help="GET /tournaments/:id/events")
    ev.add_argument("id", help="tournament uuid")
    ev.add_argument("--per-page", type=int, default=DEFAULT_PER_PAGE)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    client = AskFredClient(call_cap=args.call_cap)

    handlers = {
        "me": cmd_me,
        "tournaments": cmd_tournaments,
        "tournament": cmd_tournament,
        "events": cmd_events,
    }
    try:
        payload = handlers[args.command](client, args)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.summary:
        if args.command == "me":
            print(summarize_me(payload), file=sys.stderr)
        elif args.command == "tournaments":
            print(summarize_tournaments(payload), file=sys.stderr)
        elif args.command == "events":
            print(summarize_events(payload), file=sys.stderr)
        else:
            items = _data_list(payload)
            a = _attrs(items[0]) if items else {}
            print(
                f"tournament: {a.get('name', '?')} id={items[0].get('id') if items else '?'}",
                file=sys.stderr,
            )

    if not args.quiet_json:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")

    print(f"askfred: {client.calls} call(s) used (cap {client.call_cap})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
