#!/usr/bin/env python3
"""En Garde Gazette — editorial budget server (stdlib only).

Pages:
  GET /            → practice.html (PRACTICE budget from REAL staging/weeks/next)
  GET /practice    → practice.html (alias)
  GET /demo        → index.html (old PRETEND demo, kept for reference)
  GET /practice-lineup.json → Desk's proposed lineup config (judgment file)
  GET /api/media   → staging/weeks/next/media/manifest.json
  GET /api/lineup  → practice-lineup.json (alias)
  GET /thumb/<file>?w=320[&bw=1] → small cached JPEG of a staging media file (Pillow;
                     cache in budget-demo/.thumbs/, gitignored). Keeps the remote desktop light.
Accepts:
  POST /submit  → submissions/budget-*.json + approvals.json
  POST /vet     → update staging/weeks/next/items.json + append vet-log
  GET  /api/items → staging items JSON
Bind: 127.0.0.1:8766

Env overrides (testing against a throwaway copy; defaults = the real paths):
  GAZETTE_STAGING_WEEK  (default <repo>/staging/weeks/next)
  GAZETTE_SUBMISSIONS   (default budget-demo/submissions)
  GAZETTE_LINEUP        (default budget-demo/practice-lineup.json)
  GAZETTE_PORT          (default 8766)
"""
from __future__ import annotations

import io
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = "127.0.0.1"
PORT = int(os.environ.get("GAZETTE_PORT", "8766"))
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
STAGING_WEEK = Path(os.environ.get("GAZETTE_STAGING_WEEK") or (REPO / "staging" / "weeks" / "next")).resolve()
LINEUP = Path(os.environ.get("GAZETTE_LINEUP") or (ROOT / "practice-lineup.json")).resolve()
THUMBS = ROOT / ".thumbs"
STAGING_MEDIA = STAGING_WEEK / "media"
STAGING_ITEMS = STAGING_WEEK / "items.json"
STAGING_VET_LOG = STAGING_WEEK / "vet-log.jsonl"
SUBMISSIONS = Path(os.environ.get("GAZETTE_SUBMISSIONS") or (ROOT / "submissions")).resolve()
SUBMISSIONS_VET_LOG = SUBMISSIONS / "vet-log.jsonl"
MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}


def _now() -> datetime:
    return datetime.now().astimezone()


def _load_items() -> dict:
    if not STAGING_ITEMS.is_file():
        return {"target_week": "next", "items": []}
    return json.loads(STAGING_ITEMS.read_text(encoding="utf-8"))


def _save_items(data: dict) -> None:
    STAGING_WEEK.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now().isoformat(timespec="seconds")
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    STAGING_ITEMS.write_text(text, encoding="utf-8")


def _thumb(src: Path, width: int, bw: bool) -> bytes:
    """Small JPEG thumbnail, cached on disk keyed by source mtime/size."""
    from PIL import Image  # Pillow is already on the box (screenshot slices use it)

    st = src.stat()
    THUMBS.mkdir(parents=True, exist_ok=True)
    key = f"{src.stem}-{int(st.st_mtime)}-{st.st_size}-w{width}{'-bw' if bw else ''}.jpg"
    cached = THUMBS / key
    if cached.is_file():
        return cached.read_bytes()
    with Image.open(src) as im:
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            bg.alpha_composite(im)
            im = bg
        im = im.convert("L" if bw else "RGB")
        if im.width > width:
            im = im.resize((width, max(1, round(im.height * width / im.width))), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=78, optimize=True)
    data = buf.getvalue()
    cached.write_bytes(data)
    return data


def _add_media_sizes(data: dict) -> None:
    """Add pixel w/h to manifest entries (read-only; lets the page reserve thumb space)."""
    try:
        from PIL import Image
    except ImportError:
        return
    for m in data.get("items", []) if isinstance(data, dict) else []:
        if not isinstance(m, dict) or m.get("w"):
            continue
        name = m.get("filename") or str(m.get("media_path", "")).rsplit("/", 1)[-1]
        src = STAGING_MEDIA / name
        if not name or not src.is_file() or src.suffix.lower() == ".svg":
            continue
        try:
            with Image.open(src) as im:
                m["w"], m["h"] = im.size
        except Exception:  # noqa: BLE001
            pass


def _append_vet_log(entry: dict) -> None:
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    STAGING_WEEK.mkdir(parents=True, exist_ok=True)
    SUBMISSIONS.mkdir(parents=True, exist_ok=True)
    with STAGING_VET_LOG.open("a", encoding="utf-8") as fh:
        fh.write(line)
    with SUBMISSIONS_VET_LOG.open("a", encoding="utf-8") as fh:
        fh.write(line)


class BudgetHandler(BaseHTTPRequestHandler):
    server_version = "EnGardeBudget/2.0"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {self.address_string()} {fmt % args}")

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload, indent=2).encode("utf-8")
        self._send(code, raw, "application/json; charset=utf-8")

    def _read_json_body(self) -> tuple[dict | None, dict | None]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0 or length > 2_000_000:
            return None, {"ok": False, "error": "bad Content-Length"}
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, {"ok": False, "error": f"invalid JSON: {exc}"}
        if not isinstance(payload, dict):
            return None, {"ok": False, "error": "payload must be a JSON object"}
        return payload, None

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/", "/practice", "/practice.html"):
            target = ROOT / "practice.html"
        elif path in ("/demo", "/index.html"):
            target = ROOT / "index.html"
        elif path in ("/practice-lineup.json", "/api/lineup"):
            target = LINEUP
        elif path.startswith("/thumb/"):
            self._handle_thumb(path[len("/thumb/") :])
            return
        elif path == "/api/media":
            manifest = STAGING_MEDIA / "manifest.json"
            data = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {}
            _add_media_sizes(data)
            self._json(200, data)
            return
        elif path in ("/api/items", "/staging/items.json"):
            data = _load_items()
            self._json(200, data)
            return
        elif path.startswith("/staging-media/"):
            # Real email-extracted photos live under staging/weeks/<target>/media/
            rel = path[len("/staging-media/") :]
            if ".." in rel or rel.startswith("/") or not rel:
                self._send(403, b"Forbidden", "text/plain; charset=utf-8")
                return
            target = (STAGING_MEDIA / rel).resolve()
            if not str(target).startswith(str(STAGING_MEDIA.resolve())):
                self._send(403, b"Forbidden", "text/plain; charset=utf-8")
                return
        else:
            # serve only files under ROOT (no traversal)
            rel = path.lstrip("/")
            if ".." in rel or rel.startswith("/"):
                self._send(403, b"Forbidden", "text/plain; charset=utf-8")
                return
            target = (ROOT / rel).resolve()
            if not str(target).startswith(str(ROOT)):
                self._send(403, b"Forbidden", "text/plain; charset=utf-8")
                return

        if not target.is_file():
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return

        data = target.read_bytes()
        ctype = MIME.get(target.suffix.lower(), "application/octet-stream")
        self._send(200, data, ctype)

    def _handle_thumb(self, rel: str) -> None:
        from urllib.parse import parse_qs, unquote

        rel = unquote(rel)
        if not rel or "/" in rel or ".." in rel:
            self._send(403, b"Forbidden", "text/plain; charset=utf-8")
            return
        src = (STAGING_MEDIA / rel).resolve()
        if not str(src).startswith(str(STAGING_MEDIA.resolve())) or not src.is_file():
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        if src.suffix.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
            self._send(415, b"No thumbnail for this type", "text/plain; charset=utf-8")
            return
        qs = parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
        try:
            width = max(64, min(640, int(qs.get("w", ["320"])[0])))
        except ValueError:
            width = 320
        bw = qs.get("bw", ["0"])[0] in ("1", "true", "yes")
        try:
            data = _thumb(src, width, bw)
        except Exception as exc:  # noqa: BLE001 — report, don't crash the server
            self._send(500, f"thumb failed: {exc}".encode(), "text/plain; charset=utf-8")
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "max-age=3600")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/submit":
            self._handle_submit()
        elif path == "/vet":
            self._handle_vet()
        else:
            self._json(404, {"ok": False, "error": "not found"})

    def _handle_submit(self) -> None:
        payload, err = self._read_json_body()
        if err:
            self._json(400, err)
            return
        assert payload is not None

        SUBMISSIONS.mkdir(parents=True, exist_ok=True)
        now = _now()
        stamp = now.strftime("%Y%m%d-%H%M%S")
        payload.setdefault("pretend", True)
        payload["submittedAt"] = now.isoformat(timespec="seconds")

        stamped_name = f"budget-{stamp}.json"
        stamped_path = SUBMISSIONS / stamped_name
        approvals_path = SUBMISSIONS / "approvals.json"

        text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        stamped_path.write_text(text, encoding="utf-8")
        approvals_path.write_text(text, encoding="utf-8")

        self._json(
            200,
            {
                "ok": True,
                "file": stamped_name,
                "path": f"submissions/{stamped_name}",
                "approvals": "submissions/approvals.json",
                "submittedAt": payload["submittedAt"],
            },
        )

    def _handle_vet(self) -> None:
        payload, err = self._read_json_body()
        if err:
            self._json(400, err)
            return
        assert payload is not None

        item_id = payload.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            self._json(400, {"ok": False, "error": "id required"})
            return
        item_id = item_id.strip()

        notes_raw = payload.get("vet_notes", payload.get("notes", ""))
        if notes_raw is None:
            notes_raw = ""
        if not isinstance(notes_raw, str):
            self._json(400, {"ok": False, "error": "vet_notes must be a string"})
            return
        vet_notes = notes_raw.strip()

        data = _load_items()
        items = data.get("items")
        if not isinstance(items, list):
            self._json(500, {"ok": False, "error": "items.json malformed"})
            return

        found = None
        for item in items:
            if isinstance(item, dict) and item.get("id") == item_id:
                found = item
                break
        if found is None:
            self._json(404, {"ok": False, "error": f"item not found: {item_id}"})
            return

        now = _now()
        already = bool(found.get("vetted"))
        found["vetted"] = True
        found["vetted_at"] = now.isoformat(timespec="seconds")
        found["vetted_by"] = "frank"
        if vet_notes:
            found["vet_notes"] = vet_notes
        elif "vet_notes" not in found:
            found["vet_notes"] = None

        _save_items(data)

        log_entry = {
            "id": item_id,
            "vetted": True,
            "vetted_at": found["vetted_at"],
            "vetted_by": "frank",
            "vet_notes": found.get("vet_notes"),
            "already_vetted": already,
            "kind": found.get("kind"),
            "body": found.get("body"),
            "source": "budget-page",
        }
        _append_vet_log(log_entry)

        self._json(
            200,
            {
                "ok": True,
                "item": found,
                "items_path": "staging/weeks/next/items.json",
                "vet_log": "staging/weeks/next/vet-log.jsonl",
                "vet_log_demo": "budget-demo/submissions/vet-log.jsonl",
            },
        )


def main() -> None:
    SUBMISSIONS.mkdir(parents=True, exist_ok=True)
    STAGING_WEEK.mkdir(parents=True, exist_ok=True)
    keep = SUBMISSIONS / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")
    if not STAGING_VET_LOG.exists():
        STAGING_VET_LOG.write_text("", encoding="utf-8")

    httpd = ThreadingHTTPServer((HOST, PORT), BudgetHandler)
    print(f"En Garde Gazette PRACTICE budget → http://{HOST}:{PORT}/  (pretend demo: /demo)")
    print(f"Serving {ROOT}")
    print(f"Staging week: {STAGING_WEEK}")
    print(f"Lineup: {LINEUP}")
    print(f"Submissions: {SUBMISSIONS}")
    print("POST /submit → submissions/budget-*.json + approvals.json")
    print("POST /vet    → staging/weeks/next/items.json + vet-log.jsonl")
    print("GET  /api/items → staging items")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        httpd.server_close()


if __name__ == "__main__":
    main()
