#!/usr/bin/env python3
"""Full-page screenshots of the running budget server via Chrome CDP (stdlib only).

Usage: python3 budget-demo/screenshot.py [url] [out_prefix] [width] [viewport_height]
  default url  = http://127.0.0.1:8766/
  default out  = budget-demo/screens/practice-<YYYY-MM-DD>
Writes <out>-full.png plus 2–3 readable slices <out>-1.png, -2.png, ... (<=3400px tall each).
Slices need Pillow; the full PNG does not.

Viewport mode (what Frank actually sees): pass a 4th arg, e.g. 800 →
  python3 budget-demo/screenshot.py http://127.0.0.1:8766/ budget-demo/screens/budget-v2 1280 800
writes <out>-vp-top.png and one <out>-vp-<section>.png per `section.sec` (scrolled so the
section heading is at the top; fixed sidebar included). No full-page stitch in this mode.
"""
import base64
import json
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "prototype"))
from render import ws_connect, cdp_call  # noqa: E402


def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8766/"
    out = sys.argv[2] if len(sys.argv) > 2 else str(HERE / "screens" / f"practice-{date.today().isoformat()}")
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    port = 19223
    profile = tempfile.mkdtemp(prefix="gazette-shot-")
    chrome = subprocess.Popen(
        ["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
         f"--remote-debugging-port={port}", f"--user-data-dir={profile}",
         "--no-first-run", "--no-default-browser-check", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        ws_url = None
        req = urllib.request.Request(f"http://127.0.0.1:{port}/json/new?about:blank", method="PUT")
        for _ in range(100):
            try:
                with urllib.request.urlopen(req, timeout=2) as r:
                    ws_url = json.load(r)["webSocketDebuggerUrl"]
                break
            except Exception:
                time.sleep(0.2)
        if not ws_url:
            raise RuntimeError("chrome debugger did not start")
        hp, path = ws_url.split("//", 1)[1].split("/", 1)
        host, p = hp.rsplit(":", 1)
        s = ws_connect(host, int(p), "/" + path)
        mid = 0

        def call(method, params=None):
            nonlocal mid
            mid += 1
            return cdp_call(s, mid, method, params)

        vp_h = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        call("Page.enable")
        call("Emulation.setDeviceMetricsOverride",
             {"width": width, "height": vp_h or 900, "deviceScaleFactor": 1, "mobile": False})
        call("Page.navigate", {"url": url})
        time.sleep(3.0)
        if vp_h:
            ids = call("Runtime.evaluate", {"expression": "JSON.stringify(Array.from(document.querySelectorAll('section.sec')).map(s=>s.id))",
                                            "returnByValue": True})["result"]["value"]
            for name, js in [("top", "window.scrollTo(0,0)")] + [
                    (sid.replace("sec-", ""), f"document.getElementById('{sid}').scrollIntoView({{block:'start'}})")
                    for sid in json.loads(ids)]:
                call("Runtime.evaluate", {"expression": js})
                time.sleep(0.6)
                shot = call("Page.captureScreenshot", {"format": "png"})
                pth = Path(f"{out}-vp-{name}.png")
                pth.write_bytes(base64.b64decode(shot["data"]))
                print(pth)
            return
        res = call("Runtime.evaluate", {"expression": "document.documentElement.scrollHeight", "returnByValue": True})
        height = int(res["result"]["value"])
        call("Emulation.setDeviceMetricsOverride",
             {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False})
        time.sleep(0.8)
        shot = call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
        full = Path(out + "-full.png")
        full.write_bytes(base64.b64decode(shot["data"]))
        print(f"{full} ({width}x{height})")
        try:
            from PIL import Image
        except ImportError:
            return
        img = Image.open(full)
        for old in Path(out).parent.glob(Path(out).name + "-[0-9]*.png"):
            old.unlink()
        n = max(1, -(-height // 3400))
        step = -(-height // n)
        for i in range(n):
            part = img.crop((0, i * step, width, min(height, (i + 1) * step)))
            pth = Path(f"{out}-{i + 1}.png")
            part.save(pth)
            print(pth)
    finally:
        chrome.terminate()


if __name__ == "__main__":
    main()
