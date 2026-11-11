#!/usr/bin/env python3
"""Render the Gazette HTML to PDF via Chrome DevTools Protocol (stdlib only).

Why CDP and not `chrome --print-to-pdf`: newer Chrome ignores
--print-to-pdf-no-header, stamping date/URL/title chrome on every page.
Page.printToPDF with displayHeaderFooter=false never does. (Style guide section 1.)

Usage: render.py input.html [output.pdf] [--allow-flag] [--author=NAME] [--report=FILE.json]
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



DEFAULT_AUTHOR = "Nico's Dad"  # STYLE-GUIDE: PDF Author field = Frank's joke byline


def set_pdf_author(path, author):
    """Set /Author in the PDF Info dict via a stdlib incremental update (classic xref only).
    Chrome's printToPDF has no metadata parameters. Returns True on success."""
    import re as _re
    data = open(path, "rb").read()
    tail = data[-2048:]
    m_sx = _re.search(rb"startxref\s+(\d+)\s+%%EOF\s*$", tail)
    m_tr = list(_re.finditer(rb"trailer\s*<<(.*?)>>", data[-8192:], _re.S))
    if not m_sx or not m_tr:
        return False  # xref streams etc.: leave untouched
    trailer = m_tr[-1].group(1)
    m_info = _re.search(rb"/Info\s+(\d+)\s+(\d+)\s+R", trailer)
    m_root = _re.search(rb"/Root\s+(\d+)\s+(\d+)\s+R", trailer)
    m_size = _re.search(rb"/Size\s+(\d+)", trailer)
    if not (m_info and m_root and m_size):
        return False
    num, gen = int(m_info.group(1)), int(m_info.group(2))
    m_obj = _re.search(rb"(?<![0-9])%d %d obj\s*<<(.*?)>>\s*endobj" % (num, gen), data, _re.S)
    body = m_obj.group(1) if m_obj else b""
    body = _re.sub(rb"/Author\s*\((?:\\.|[^\\)])*\)", b"", body)
    esc = author.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("latin-1")
    new_obj = b"%d %d obj\n<<" % (num, gen) + body + b"/Author (" + esc + b")>>\nendobj\n"
    out = bytearray(data)
    if not out.endswith(b"\n"):
        out += b"\n"
    off = len(out)
    out += new_obj
    xref_off = len(out)
    out += b"xref\n%d 1\n%010d %05d n \n" % (num, off, gen)
    out += (b"trailer\n<</Size " + m_size.group(1) + b" /Root " + m_root.group(1) + b" " + m_root.group(2)
            + b" R /Info %d %d R /Prev " % (num, gen) + m_sx.group(1) + b">>\nstartxref\n%d\n%%%%EOF\n" % xref_off)
    open(path, "wb").write(bytes(out))
    return True

# ---------------------------------------------------------------------------
# Fill instrument (STYLE-GUIDE §6, §13, §18). Screen px at 96/in = print inches.
#
# What counts as a column: the children of any element tagged data-balance (the
# shared composer tags every multi-column row), plus the legacy classes .cols3,
# .page2-lower, .split, .board-split and .box-pair so old issues are measured too.
# Depth is CONTENT depth: the lowest ink in the column (text line boxes, images,
# table cells), never the box height, because flex stretch makes sibling boxes
# equal by construction.
#
# 1. Footer gap PER COLUMN: for each page, find the last block above the footer.
#    If it is a multi-column row, every column gets its own gap; the WORST column
#    is the page's number (old instrument: only the tallest sibling). FLAG > 0.75in.
#    A negative gap means content overlaps the footer: FLAG.
# 2. Balance: for every multi-column row, the spread between its deepest and
#    shallowest column. FLAG > 0.5in.
# 3. Type floor: every element that directly holds text, including ears, captions,
#    credits, kickers and board heads. FLAG < 7pt.
# 4. Hyphenation: how many justified lines actually end at a soft hyphen. Zero on
#    a page with justified text is reported as a WARN (regression check).
INSTRUMENT_JS = r"""
(() => {
  const SEL = '[data-balance], .cols3, .page2-lower, .split, .board-split, .box-pair';
  const inkBottom = (el) => {
    let b = -Infinity;
    const take = (r) => { if (r.width > 0 && r.height > 0 && r.bottom > b) b = r.bottom; };
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      if (!n.nodeValue.trim()) continue;
      range.selectNodeContents(n);
      for (const r of range.getClientRects()) take(r);
    }
    el.querySelectorAll('img, svg, hr, td, th').forEach(e => take(e.getBoundingClientRect()));
    if (el.matches && el.matches('img, svg')) take(el.getBoundingClientRect());
    return b;
  };
  const label = (el) => el.getAttribute('data-balance') || (el.className || '').split(' ')[0];
  // CSS multi-column text has no child boxes: read its columns from the line rects.
  const textCols = (el) => {
    const cs = getComputedStyle(el), n = parseInt(cs.columnCount, 10) || 1;
    const box = el.getBoundingClientRect(), gap = parseFloat(cs.columnGap) || 0;
    const colW = (box.width - gap * (n - 1)) / n;
    const cols = new Array(n).fill(-Infinity);
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    for (let t = w.nextNode(); t; t = w.nextNode()) {
      if (!t.nodeValue.trim()) continue;
      range.selectNodeContents(t);
      for (const r of range.getClientRects()) {
        if (!(r.width > 0 && r.height > 0)) continue;
        const k = Math.max(0, Math.min(n - 1, Math.floor((r.left - box.left + gap / 2) / (colW + gap))));
        if (r.bottom > cols[k]) cols[k] = r.bottom;
      }
    }
    return cols.filter(v => v > -Infinity);
  };
  const colBottoms = (row) => {
    if (getComputedStyle(row).columnCount !== 'auto') return textCols(row);
    return [...row.children].map(inkBottom).filter(v => v > -Infinity);
  };
  // The lowest multi-column structure inside a block decides the per-column picture.
  const columnsAtFoot = (block) => {
    if (block.matches(SEL)) {
      const kids = getComputedStyle(block).columnCount !== 'auto' ? null : [...block.children];
      if (!kids) return textCols(block);
      return kids.map(inkBottom).filter(v => v > -Infinity);
    }
    return [inkBottom(block)];
  };
  const pages = [...document.querySelectorAll('.page')].map((p, i) => {
    const f = p.querySelector(':scope > .footer');
    const ft = f.getBoundingClientRect().top;
    const last = f.previousElementSibling;
    const cols = columnsAtFoot(last).map(b => +(ft - b).toFixed(1));
    const rows = [...p.querySelectorAll(SEL)].map(r => {
      const bs = colBottoms(r);
      const top = r.getBoundingClientRect().top;
      return { kind: label(r), depths: bs.map(b => +(b - top).toFixed(1)),
               spread: bs.length > 1 ? +(Math.max(...bs) - Math.min(...bs)).toFixed(1) : 0 };
    });
    return { page: i + 1, last: label(last), gaps: cols, rows,
             overflow: +Math.max(p.scrollHeight - p.clientHeight, p.getBoundingClientRect().height - 10.1 * 96).toFixed(1) };
  });
  // type floor
  let minPx = Infinity, minWho = '';
  document.querySelectorAll('body *').forEach(e => {
    if (['STYLE', 'SCRIPT'].includes(e.tagName)) return;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim());
    if (!own) return;
    const px = parseFloat(getComputedStyle(e).fontSize);
    if (px < minPx) { minPx = px; minWho = e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).split(' ').join('.') : ''); }
  });
  // hyphenation: soft hyphens that became real line breaks
  let shy = 0, used = 0, justified = 0;
  const range = document.createRange();
  document.querySelectorAll('p').forEach(p => {
    if (getComputedStyle(p).textAlign === 'justify') justified++;
    const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      const t = n.nodeValue;
      for (let i = t.indexOf('­'); i > 0 && i < t.length - 1; i = t.indexOf('­', i + 1)) {
        shy++;
        range.setStart(n, i - 1); range.setEnd(n, i);
        const a = range.getClientRects()[0];
        range.setStart(n, i + 1); range.setEnd(n, i + 2);
        const br = range.getClientRects();        // at a break the first rect is the printed hyphen
        const b = br[br.length - 1];
        if (a && b && b.top > a.top + 2) used++;
      }
    }
  });
  return JSON.stringify({ pages, minPt: minPx * 0.75, minWho, shy, used, justified });
})()
"""

GAP_FLAG_IN = 0.75
SPREAD_FLAG_IN = 0.5


def report(m):
    """Print the instrument readings; return the list of FLAG messages."""
    flags = []
    inch = lambda px: px / 96.0
    for pg in m["pages"]:
        gaps = [inch(g) for g in pg["gaps"]]
        worst = max(gaps)
        detail = ""
        if len(gaps) > 1:
            detail = " per column [" + ", ".join(f"{g:.2f}in" for g in gaps) + f"] in .{pg['last']}"
        tag = "OK"
        if worst > GAP_FLAG_IN or min(gaps) < -0.02 or pg.get("overflow", 0) > 2:
            tag = "FLAG"
        msg = f"page {pg['page']}: worst gap above footer {worst:.2f}in [{tag}]{detail}"
        if min(gaps) < -0.02 or pg.get("overflow", 0) > 2:
            msg += f" (page is {inch(max(pg.get('overflow', 0), 0)):.2f}in too deep or content overlaps the footer)"
        print(msg)
        if tag == "FLAG":
            flags.append(msg)
        for k, row in enumerate(pg["rows"]):
            if len(row["depths"]) < 2:
                continue
            sp = inch(row["spread"])
            tag = "OK" if sp <= SPREAD_FLAG_IN else "FLAG"
            msg = (f"page {pg['page']} row {k + 1} ({row['kind']}): column spread {sp:.2f}in [{tag}] ["
                   + ", ".join(f"{inch(d):.2f}in" for d in row["depths"]) + "]")
            print(msg)
            if tag == "FLAG":
                flags.append(msg)
    if m.get("minPt") is None or m["minPt"] > 1e6:
        print("type floor n/a (no measurable text) [OK]")
    elif m["minPt"] < 7 - 0.005:
        msg = f"type floor violated: {m['minPt']:.2f}pt < 7pt at {m['minWho']} [FLAG]"
        print(msg); flags.append(msg)
    else:
        print(f"type floor {m['minPt']:.2f}pt ({m['minWho']}) [OK]")
    if m["justified"] and not m["used"]:
        print(f"hyphenation: 0 hyphenated line breaks ({m['shy']} soft hyphens available) [WARN]"
              " - justified text will show rivers; is gazette.ty() hyphenation on?")
    else:
        print(f"hyphenation: {m['used']} hyphenated line breaks ({m['shy']} soft hyphens available) [OK]")
    return flags


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
            os.environ.get("GAZETTE_CHROME", "google-chrome"), "--headless=new", "--no-sandbox", "--disable-gpu",
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
        # PDF Author (STYLE-GUIDE § PDF filename): --author=NAME, else <meta name="author">, else default
        author = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--author=")), None)
        if author is None:
            try:
                import re as _re
                m = _re.search(r'<meta\s+name="author"\s+content="([^"]*)"', open(src, encoding="utf-8").read())
                author = m.group(1) if m else DEFAULT_AUTHOR
            except Exception:
                author = DEFAULT_AUTHOR
        print("pdf Author set: " + author if set_pdf_author(out, author) else "pdf Author NOT set (unsupported xref)")
        flags = []  # any FLAG fails the build unless --allow-flag is passed (V7)
        try:
            res = call("Runtime.evaluate", {"expression": INSTRUMENT_JS, "returnByValue": True})
            m = json.loads(res["result"]["value"])
            flags += report(m)
            rep = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--report=")), None)
            if rep:
                with open(rep, "w") as f:
                    json.dump(m, f, indent=1)
        except Exception:
            import traceback as _tb
            _tb.print_exc()
            flags.append("instrument failed to run")
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
        try:
            chrome.wait(timeout=5)
        except Exception:
            pass
        import shutil
        shutil.rmtree(profile, ignore_errors=True)   # throwaway profile: never leave it in the temp dir


if __name__ == "__main__":
    main()
