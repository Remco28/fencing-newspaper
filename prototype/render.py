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

HTML2PDF_JS = None  # (placeholder, unused)


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
                flag = "OK" if inches <= 0.75 else "FLAG"
                print(f"page {i + 1}: gap above footer {inches:.2f}in [{flag}]")
        except Exception as e:
            print(f"measure skipped: {e}")
        try:
            info = subprocess.run(["pdfinfo", out], capture_output=True, text=True)
            for line in info.stdout.splitlines():
                if line.startswith("Pages:"):
                    print("pdf", line.strip())
        except Exception:
            pass
    finally:
        chrome.terminate()


if __name__ == "__main__":
    main()
