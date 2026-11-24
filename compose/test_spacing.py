#!/usr/bin/env python3
"""Spacing tokens, the fit.js unwrap fix, and the eye check's offline parts (Frank t229u).

Run: python3 compose/test_spacing.py   (Chrome; writes only under /tmp)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eyecheck as E  # noqa: E402
import gazette as g  # noqa: E402
import render as R  # noqa: E402
from gazette import (  # noqa: E402
    art, box, box_pair, box_table, cols3, copy_length, dateline, document, footer, masthead,
    page, paras, photo_pair, piece, render_piece, split, stack, table,
)

TMP = Path(tempfile.mkdtemp(prefix="gz-spacing-"))
failures = []


def check(name, cond, detail=""):
    print(("  ok: " if cond else "  FAIL: ") + name + ("" if cond else f" {detail}"))
    if not cond:
        failures.append(name)


# ----- tokens exist and the CSS has one page-level rhythm rule -----------------
css = g.base_css()
print("=== spacing tokens ===")
check("--gap-block token is defined at 7pt", "--gap-block: 7pt" in css)
check("one page-level rhythm rule includes the first block after the dateline",
      ".page > .dateline + :not(.footer)" in css
      and css.count(".page > :not(.masthead, .dateline) + :not(.footer)") == 1)
check("one column rhythm rule", css.count(".c > * + :not(p), .c > :not(p) + p") == 1)
check("render.py's token matches the CSS", abs(R.BLOCK_GAP_PT - 7.0) < 1e-9)
check("photo pairs have no column rule", ".split.pair > * + * { border-left: none" in css)

# ----- copy lengths -------------------------------------------------------------
print("=== copy lengths ===")
v = {"short": "a b", "standard": "a b c", "long": "a b c d"}
check("default is standard", copy_length("x", v, {}) == "a b c")
check("pick long", copy_length("x", v, {"x": "long"}) == "a b c d")
check("missing size falls back toward standard", copy_length("y", {"standard": "s"}, {"y": "long"}) == "s")
check("lengths_for reads --len flags", g.lengths_for("issues/does-not-exist", ["--len=lead:long"]) == {"lead": "long"})

# ----- Chrome: every inter-block gap equals the token ---------------------------
print("=== Chrome: inter-block gaps ===")
from PIL import Image
Image.new("RGB", (300, 200), (90, 90, 90)).save(TMP / "a.png")
Image.new("RGB", (300, 200), (60, 60, 60)).save(TMP / "b.png")
fig = lambda src, aid: (f'<figure class="art" data-art="{aid}" data-kind="illustration" data-region="span2" '
                        f'data-flex="false"><img src="{src}" alt=""></figure>')
t = table(["A", "B"], [["one", "two"], ["three", "four"]], ["1in", None])
lorem = "Fixture copy for the spacing test, not published. " * 6
p1 = page(
    masthead() + "\n" + dateline("Fixture", "Spacing fixture")
    + "\n" + cols3(
        stack(piece("Lead", paras(lorem), level=1, cls="lead"), box("Box in a column", t)),
        stack(piece("Rail A", paras(lorem), kicker="K"), piece("Rail B", paras(lorem), kicker="L")),
    )
    + "\n" + render_piece(piece("Full-width short", paras(lorem), kicker="Short"))
    + "\n" + box("Wide box", t, cls="w3")
    + "\n" + box_pair(box("Left", t), box("Right", t))
    + "\n" + split(render_piece(piece("Split L", paras(lorem))), render_piece(piece("Split R", paras(lorem))))
    + "\n" + footer(0)
)
p2 = page(dateline("Page Two", "Spacing fixture", first=False) + "\n"
          + photo_pair(fig("a.png", "pa"), fig("b.png", "pb")) + "\n" + paras(lorem) + "\n" + footer(0), cls="fit")
html_path = TMP / "issue.html"
html_path.write_text(document("Spacing fixture", [p1, p2]), encoding="utf-8")
rep = TMP / "rep.json"
r = subprocess.run([sys.executable, str(g.ROOT / "compose" / "render.py"), str(html_path), str(TMP / "out.pdf"),
                    f"--report={rep}", "--no-fit", "--allow-flag"], capture_output=True, text=True, cwd=str(g.ROOT))
check("fixture rendered", rep.is_file(), (r.stdout + r.stderr)[-500:])
if rep.is_file():
    data = json.loads(rep.read_text())
    gaps = [(bg["where"], bg["above"], bg["below"], round(bg["gap"] * 0.75, 1))
            for pg in data["pages"] for bg in pg.get("block_gaps") or []]
    print("  measured:", gaps)
    check("the page-level stack was measured (>= 5 gaps)", len([x for x in gaps if x[0] == "page"]) >= 5, gaps)
    bad = [x for x in gaps if not (R.BLOCK_GAP_MIN_PT <= x[3] <= R.BLOCK_GAP_MAX_PT)]
    check("every inter-block gap is inside the token band", not bad, bad)
    box_gaps = [x[3] for x in gaps if x[1].startswith("box") and x[2].startswith("box")]
    check("box to box-pair is exactly the token (no touching borders)",
          box_gaps and all(abs(x - 7.0) <= 0.6 for x in box_gaps), box_gaps)
    check("instrument reports picture rectangles", any(pg.get("img_rects") for pg in data["pages"]))
    # Regression (Frank, No. 8 proof v1): content must not sit against a page header rule.
    header = [(pg["page"], (hg.get("gap") or 0) * 0.75)
              for pg in data["pages"] for hg in pg.get("header_gaps") or []]
    print("  header gaps (pt):", header)
    check("each page reports a dateline-to-content header gap",
          {p for p, _ in header} >= {1, 2}, header)
    bad_h = [x for x in header if x[1] < R.BLOCK_GAP_MIN_PT]
    check("header-rule gap is at least the token minimum on every page",
          not bad_h, bad_h)

# ----- Chrome: unwrapLonelySplits never hoists a bare flex cell ---------------
print("=== Chrome: fit.js unwrap fix ===")
fit_js = (g.ROOT / "compose" / "fit.js").read_text()
probe = TMP / "unwrap.html"
probe.write_text(f"""<!doctype html><html><body><div class="page" id="pg" style="display:flex;flex-direction:column;height:400px">
<div class="split" data-balance="split"><div style="flex:1"><div class="slot-a">A</div><div class="slot-a">B</div></div><div style="flex:1"></div></div>
<div class="footer">f</div></div>
<script>{fit_js}</script>
<script>window.__gzFit.unwrapLonelySplits();
document.body.setAttribute('data-kids', [...document.getElementById('pg').children].map(e => (e.className||'BARE') + ':' + (e.style.flex||'')).join('|'));</script>
</body></html>""")
dom = subprocess.run([R.os.environ.get("GAZETTE_CHROME", "google-chrome"), "--headless=new", "--no-sandbox", "--disable-gpu",
                      "--dump-dom", "file://" + str(probe)], capture_output=True, text=True, timeout=60).stdout
import re as _re
m = _re.search(r'data-kids="([^"]*)"', dom)
kids = m.group(1) if m else ""
check("split cell's children are hoisted, not the bare flex cell", kids.startswith("slot-a:|slot-a:|footer"), kids)

# ----- eye check: blank map, rule, length targets, send gate -------------------
print("=== eye check (offline) ===")
W, H = int(8.5 * 100), int(11 * 100)
im = Image.new("L", (W, H), 0)          # all ink
from PIL import ImageDraw
d = ImageDraw.Draw(im)
d.rectangle([int(1.0 * 100), int(3.0 * 100), int(4.0 * 100), int(5.0 * 100)], fill=255)   # 3x2in hole
d.rectangle([int(5.0 * 100), int(6.0 * 100), int(7.0 * 100), int(7.5 * 100)], fill=255)   # a photo's white backdrop
png = TMP / "page.png"
im.save(png)
holes = E.blank_map(png, img_rects=[(4.5, 5.5, 2.0, 1.5)])
check("blank map finds the 3x2in hole", any(abs(h["w_in"] - 3.0) < 0.1 and abs(h["h_in"] - 2.0) < 0.1 for h in holes), holes)
check("a masked photo backdrop is not a hole", not any(h["x_in"] >= 4.9 and h["y_in"] >= 5.9 for h in holes), holes)
check("the 6 sq in hole breaks the rule", any(E.hole_breaks_rule(h) for h in holes))
check("a 4x0.5in ragged band does not break the rule",
      not E.hole_breaks_rule({"w_in": 4.0, "h_in": 0.5, "sq_in": 2.0, "bottom_band": False}))
check("a 0.6in bottom band breaks the rule",
      E.hole_breaks_rule({"w_in": 7.5, "h_in": 0.6, "sq_in": 4.5, "bottom_band": True}))
tg = E.length_targets({1: holes}, {"pages": [{"page": 1, "words_per_sq_in": 20, "overflow": 0, "gaps": [5]}]})
check("length target asks for ~120 words for a 6 sq in hole", tg and tg[0]["action"] == "add" and 100 <= tg[0]["words"] <= 140, tg)
tg = E.length_targets({1: []}, {"pages": [{"page": 1, "words_per_sq_in": 20, "overflow": 48, "gaps": [-48]}]})
check("an overset page asks for a cut", tg and tg[0]["action"] == "cut" and tg[0]["words"] > 0, tg)

pdf = TMP / "proof.pdf"
pdf.write_bytes(b"%PDF-1.4 fixture")
jp, _ = E.result_paths(pdf)
ok, why = E.verify(pdf)
check("no eye-check.json -> not sendable", not ok, why)
jp.write_text(json.dumps({"verdict": "PASS", "pdf_sha256": E.sha256(pdf)}))
check("PASS for this PDF -> sendable", E.verify(pdf)[0])
pdf.write_bytes(b"%PDF-1.4 changed")
check("PASS for another PDF -> not sendable", not E.verify(pdf)[0])
jp.write_text(json.dumps({"verdict": "FAIL", "pdf_sha256": E.sha256(pdf), "reasons": ["hole"]}))
check("FAIL -> not sendable", not E.verify(pdf)[0])
jp.write_text(json.dumps({"verdict": "FAIL", "pdf_sha256": E.sha256(pdf), "waived_by": "frank", "waiver_note": "t999u"}))
check("FAIL waived by Frank -> sendable", E.verify(pdf)[0])

print()
if failures:
    print(f"{len(failures)} check(s) failed")
    sys.exit(1)
print("spacing: all checks passed")
