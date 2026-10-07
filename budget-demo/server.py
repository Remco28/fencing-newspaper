#!/usr/bin/env python3
"""En Garde Gazette — pretend editorial budget server (stdlib only).

Serves index.html at / and accepts POST /submit, writing:
  submissions/budget-YYYYMMDD-HHMMSS.json
  submissions/approvals.json  (latest overwrite)
Bind: 127.0.0.1:8766
"""
from __future__ import annotations

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8766
ROOT = Path(__file__).resolve().parent
SUBMISSIONS = ROOT / "submissions"
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


class BudgetHandler(BaseHTTPRequestHandler):
    server_version = "EnGardeBudget/1.0"

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

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            target = ROOT / "index.html"
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

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/submit":
            self._json(404, {"ok": False, "error": "not found"})
            return

        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0 or length > 2_000_000:
            self._json(400, {"ok": False, "error": "bad Content-Length"})
            return

        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._json(400, {"ok": False, "error": f"invalid JSON: {exc}"})
            return

        if not isinstance(payload, dict):
            self._json(400, {"ok": False, "error": "payload must be a JSON object"})
            return

        SUBMISSIONS.mkdir(parents=True, exist_ok=True)
        now = datetime.now().astimezone()
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


def main() -> None:
    SUBMISSIONS.mkdir(parents=True, exist_ok=True)
    # keep empty dir in git-friendly shape without committing submissions
    keep = SUBMISSIONS / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")

    httpd = ThreadingHTTPServer((HOST, PORT), BudgetHandler)
    print(f"En Garde Gazette budget demo → http://{HOST}:{PORT}/")
    print(f"Serving {ROOT}")
    print("POST /submit → submissions/budget-*.json + approvals.json")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        httpd.server_close()


if __name__ == "__main__":
    main()
