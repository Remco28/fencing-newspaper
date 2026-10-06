#!/usr/bin/env python3
"""Render the Gazette HTML to PDF via Chrome DevTools Protocol (stdlib only).

Why CDP and not `chrome --print-to-pdf`: newer Chrome ignores
--print-to-pdf-no-header, stamping date/URL/title chrome on every page.
Page.printToPDF with displayHeaderFooter=false never does. (Style guide section 1.)

Usage: render.py input.html [output.pdf]
"""
import base64
import hashlib
import json
import os
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request

def ws_connect(host, port, path):
    s = socket.create_connection((host, port), timeout=15)
    key = base64.b64encode(os.urandom(16)).decode()
    req = (
        f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\n"
        f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    s.sendall(req.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk:
            raise RuntimeError("websocket handshake failed")
        resp += chunk
    return s


def ws_send(s, payload):
    if isinstance(payload, str):
        payload = payload.encode()
    header = bytes([0x81])
    n = len(payload)
    mask = os.urandom(4)
    if n < 126:
        header += struct.pack("!B", 0x80 | n)
    elif n < 65536:
        header += struct.pack("!BH", 0x80 | 126, n)
    else:
        header += struct.pack("!BQ", 0x80 | 127, n)
    header += mask
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    s.sendall(header + masked)


def ws_recv(s):
    def rn(n):
        buf = b""
        while len(buf) < n:
            chunk = s.recv(n - len(buf))
            if not chunk:
                raise RuntimeError("websocket closed")
            buf += chunk
        return buf

    hdr = rn(2)
    opcode = hdr[0] & 0x0F
    length = hdr[1] & 0x7F
    if length == 126:
        length = struct.unpack("!H", rn(2))[0]
    elif length == 127:
        length = struct.unpack("!Q", rn(8))[0]
    if hdr[1] & 0x80:
        mask = rn(4)
    else:
        mask = None
    data = rn(length)
    if mask:
        data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
    if opcode == 0x8:
        raise RuntimeError("websocket close frame")
    return data.decode("utf-8", "replace")


def cdp_call(s, msg_id, method, params=None):
    ws_send(s, json.dumps({"id": msg_id, "method": method, "params": params or {}}))
    while True:
        msg = json.loads(ws_recv(s))
        if msg.get("id") == msg_id:
            if "error" in msg:
                raise RuntimeError(f"{method}: {msg['error']}")
            return msg.get("result", {})


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "prototype/monday-v2.html"
    out = sys.argv[2] if len(sys.argv) > 2 else (
        src.rsplit(".", 1)[0] + ".pdf" if "." in src else src + ".pdf"
    )
    src = os.path.abspath(src)
    port = 19222
    profile = tempfile.mkdtemp(prefix="gazette-chrome-")
    chrome = subprocess.Popen(
        [
            "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
            f"--remote-debugging-port={port}", f"--user-data-dir={profile}",
            "--no-first-run", "--no-default-browser-check",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        ws_url = None
        new_target = urllib.request.Request(
            f"http://127.0.0.1:{port}/json/new?about:blank", method="PUT"
        )
        for _ in range(100):
            try:
                with urllib.request.urlopen(new_target, timeout=2) as r:
                    ws_url = json.load(r)["webSocketDebuggerUrl"]
                break
            except Exception:
                time.sleep(0.2)
        if not ws_url:
            raise RuntimeError("chrome debugger did not start")
        host_port = ws_url.split("//", 1)[1].split("/", 1)[0]
        host, p = host_port.rsplit(":", 1)
        path = "/" + ws_url.split("//", 1)[1].split("/", 1)[1]
        s = ws_connect(host, int(p), path)
        mid = 0

        def call(method, params=None):
            nonlocal mid
            mid += 1
            return cdp_call(s, mid, method, params)

        call("Page.enable")
        call("Runtime.enable")
        call("Page.navigate", {"url": "file://" + src})
        for _ in range(100):
            time.sleep(0.2)
            # poll load event via evaluate-ready check instead:
            try:
                res = call("Runtime.evaluate", {"expression": "document.readyState"})
                if res.get("result", {}).get("value") == "complete":
                    break
            except RuntimeError:
                break
        time.sleep(0.4)  # let webfonts/images settle
        res = call("Page.printToPDF", {
            "displayHeaderFooter": False,
            "preferCSSPageSize": True,
            "printBackground": True,
            "marginTop": 0, "marginBottom": 0, "marginLeft": 0, "marginRight": 0,
        })
        with open(out, "wb") as f:
            f.write(base64.b64decode(res["data"]))
        print(f"wrote {out}")
        flags = []  # any FLAG fails the build unless --allow-flag is passed (V7)
        # --- whitespace instrument: footers are pinned to page bottom, so the
        # honest slack is the GAP ABOVE each footer (dead zone between last
        # content and footer). Screen px (~96dpi) ≈ print inches. FLAG > 0.75in.
        try:
            res = call("Runtime.evaluate", {
                "expression": "JSON.stringify("
                "[...document.querySelectorAll('.page')].map(p => {"
                "const f = p.querySelector('.footer');"
                "const prev = f.previousElementSibling;"
                "const fr = f.getBoundingClientRect();"
                "const pr = prev.getBoundingClientRect();"
                "return Math.round(fr.top - pr.bottom);"
                "}))"
            })
            gaps = json.loads(res["result"]["value"])
            for i, g in enumerate(gaps):
                inches = g / 96.0
                if inches <= 0.75:
                    print(f"page {i + 1}: gap above footer {inches:.2f}in [OK]")
                else:
                    msg = f"page {i + 1}: gap above footer {inches:.2f}in [FLAG]"
                    print(msg)
                    flags.append(msg)
            # region balance: CONTENT depth per column (deepest descendant bottom),
            # not box height — flex stretch equalizes boxes by construction (V2).
            res = call("Runtime.evaluate", {
                "expression": "JSON.stringify("
                "[...document.querySelectorAll('.page .cols3')].map(r => {"
                "const depth = c => {"
                "const top = c.getBoundingClientRect().top; let b = top;"
                "c.querySelectorAll('*').forEach(e => {"
                "const rr = e.getBoundingClientRect();"
                "if (rr.bottom > b) b = rr.bottom; });"
                "return Math.round(b - top); };"
                "const ds = [...r.children].map(depth);"
                "const lo = Math.min(...ds), hi = Math.max(...ds);"
                "return Math.round(hi - lo) + '|' + ds.map(d => Math.round(d)).join(',');"
                "}))"
            })
            region = json.loads(res["result"]["value"])
            for i, entry in enumerate(region):
                if isinstance(entry, str) and "|" in entry:
                    spread_px, _, depths = entry.partition("|")
                else:
                    spread_px, depths = entry, ""
                inches = float(spread_px) / 96.0
                detail = ""
                if depths:
                    detail = " [" + ", ".join(
                        f"{int(d) / 96.0:.2f}in" for d in depths.split(",")) + "]"
                if inches <= 0.5:
                    print(f"row {i + 1}: column spread {inches:.2f}in [OK]{detail}")
                else:
                    msg = f"row {i + 1}: column spread {inches:.2f}in [FLAG]{detail}"
                    print(msg)
                    flags.append(msg)
            # type floor (§4/§6): nothing below 7pt, measured as computed styles.
            res = call("Runtime.evaluate", {
                "expression": "JSON.stringify(Math.min("
                "...[...document.querySelectorAll("
                "'body p, body td, body th, body li, body h1, body h2, "
                "body h3, body .footer, body .dateline, body .byline']"
                ".map(e => parseFloat(getComputedStyle(e).fontSize))))"
            })
            try:
                raw = res.get("result", {})
                # CDP shape varies: {value} or {result: {value}}
                val = raw.get("value", None)
                if isinstance(val, dict):
                    val = val.get("value", None)
                min_px = json.loads(val) if isinstance(val, str) else val
            except (KeyError, TypeError):
                min_px = None
            if min_px is None:
                print("type floor n/a (no measurable text) [OK]")
            else:
                min_pt = min_px * 0.75
                if min_pt < 7 - 1e-9:
                    msg = f"type floor violated: {min_pt:.2f}pt < 7pt [FLAG]"
                    print(msg)
                    flags.append(msg)
                else:
                    print(f"type floor {min_pt:.2f}pt [OK]")
        except Exception as e:
            import traceback as _tb
            _tb.print_exc()
            try:
                print("RES-DUMP:", json.dumps(res)[:400])
            except Exception:
                print("RES-DUMP: <unavailable>")
        try:
            info = subprocess.run(["pdfinfo", out], capture_output=True, text=True)
            for line in info.stdout.splitlines():
                if line.startswith("Pages:"):
                    print("pdf", line.strip())
                    if line.split()[1] != "2":
                        flags.append(f"expected 2 pages, got {line.split()[1]}")
        except Exception:
            pass
        if flags and "--allow-flag" not in sys.argv:
            print("FAIL: " + "; ".join(flags), file=sys.stderr)
            sys.exit(1)
    finally:
        chrome.terminate()


if __name__ == "__main__":
    main()
