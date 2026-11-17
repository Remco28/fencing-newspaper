#!/usr/bin/env python3
"""Tests for the fill instrument's per-column holes and the row-balance pass.

Run: python3 compose/test_balance.py
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art as A
import balance as B
import gazette as g
import render as R

TMP = Path(tempfile.mkdtemp(prefix="gz-balance-"))
failures = []


def check(name, cond, detail=""):
    if cond:
        print("  ok:", name)
        return
    failures.append(name if not detail else f"{name}: {detail}")
    print("  FAIL:", name, detail)


# ----- safe_cover_crop -------------------------------------------------------

def _band_image(w=100, h=200, lo=0.10, hi=0.55):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (w, h), (0, 0, 200))  # blue = croppable backdrop/floor
    d = ImageDraw.Draw(im)
    top = int(round(lo * h))
    bot = int(round(hi * h))
    d.rectangle([0, top, w - 1, bot - 1], fill=(220, 30, 30))  # red keep-band
    # unique marker rows at the keep edges so we can prove they survived
    d.line([(0, top), (w, top)], fill=(0, 255, 0))
    d.line([(0, bot - 1), (w, bot - 1)], fill=(255, 255, 0))
    p = TMP / "keep-src.png"
    im.save(p)
    return p, top, bot


print("=== safe_cover_crop ===")
src, keep_top, keep_bot = _band_image()
# Target aspect 1.0 → 100×100 window; keep-band is 90px and fits.
dest = TMP / "keep-src-fillcrop.png"
info = B.safe_cover_crop(src, dest, target_aspect=1.0, keep_band=(0.10, 0.55))
check("gentle crop is applied", info.get("cropped") is True, info)
check("original is not overwritten", src.stat().st_size > 0 and dest.is_file())
if info.get("cropped"):
    from PIL import Image as _Im
    out = _Im.open(dest)
    box = info["box"]  # left, top, right, bottom in source px
    check("output is 100x100", out.size == (100, 100), out.size)
    check("keep-band top is inside the window", box[1] <= keep_top, f"box={box} keep_top={keep_top}")
    check("keep-band bottom is inside the window", box[3] >= keep_bot, f"box={box} keep_bot={keep_bot}")
    # Every keep-band pixel in the source should be unchanged in the crop.
    src_im = _Im.open(src)
    ok = True
    for y in range(keep_top, keep_bot):
        if src_im.getpixel((50, y)) != out.getpixel((50, y - box[1])):
            ok = False
            break
    check("keep-band pixels are unchanged", ok)
    check("crop prefers the backdrop (start at keep top)", box[1] == keep_top, box)

# Too tight to contain the keep-band: 100x200 → aspect 4.0 is 100x25, band is 90px.
info2 = B.safe_cover_crop(src, TMP / "too-tight.png", target_aspect=4.0, keep_band=(0.10, 0.55))
check("refuses a crop that would cut the keep-band", info2.get("cropped") is False, info2)
check("tight-crop reason mentions keep-band", "keep-band" in (info2.get("reason") or ""), info2)

orig, dest2 = B.original_and_dest(TMP / "photo-fillcrop.jpg")
check("original_and_dest strips -fillcrop for the source", orig.name == "photo.jpg", orig.name)
check("original_and_dest writes a -fillcrop sibling", dest2.name == "photo-fillcrop.jpg", dest2.name)

# ----- report() flags --------------------------------------------------------

print("=== fill instrument report ===")
check("COL_GAP_FLAG_IN is 0.35in in art, gazette, render",
      abs(A.COL_GAP_FLAG_IN - 0.35) < 1e-9
      and abs(g.COL_GAP_FLAG_IN - 0.35) < 1e-9
      and abs(R.COL_GAP_FLAG_IN - 0.35) < 1e-9,
      (A.COL_GAP_FLAG_IN, g.COL_GAP_FLAG_IN, R.COL_GAP_FLAG_IN))


def _inst(col_gaps_px, holes=None, spread_px=None, footer_gaps_px=None):
    if spread_px is None:
        spread_px = max(col_gaps_px) - min(col_gaps_px) if col_gaps_px else 0
    depths = [200 - g for g in col_gaps_px]
    return {
        "pages": [{
            "page": 1,
            "gaps": footer_gaps_px if footer_gaps_px is not None else [40],
            "footer_drop": 0,
            "overflow": 0,
            "last": "split",
            "rows": [{
                "kind": "columns",
                "depths": depths,
                "spread": spread_px,
                "col_gaps": col_gaps_px,
            }],
            "holes": holes or [],
        }],
        "minPt": 8, "minWho": "p", "shy": 4, "used": 2, "justified": 1,
    }


def flags_for(inst):
    buf = io.StringIO()
    with redirect_stdout(buf):
        flags = R.report(inst)
    return flags, buf.getvalue()


# 33/96 = 0.34375in ≤ 0.35 → OK
flags, out = flags_for(_inst([0, 33], spread_px=33))
check("0.34in column gap does not FLAG",
      not any("bottom gap" in f for f in flags), flags)

# 36/96 = 0.375in → 0.38in rounded, FLAGs; 33/96 still OK above.
flags, out = flags_for(_inst([0, 36], spread_px=36))
check("0.38in column gap FLAGs the build",
      any("bottom gap" in f and "[FLAG]" in f for f in flags), flags)
check("FLAG names the page, row, and column",
      any("page 1 row 1 (columns): column 2 bottom gap" in f for f in flags), flags)
# 36/96 < 0.5, so spread should still be OK
check("0.38in gap does not by itself FLAG the 0.5in spread check",
      not any("column spread" in f and "[FLAG]" in f for f in flags), flags)

# Footer gap can be fine (0.50in) while an in-row hole FLAGs — Frank's diagnosis.
flags, out = flags_for(_inst([0, 211], spread_px=211, footer_gaps_px=[48]))  # 211/96=2.20
check("in-row 2.2in hole FLAGs even when the footer gap is 0.50in OK",
      any("bottom gap 2.20in" in f for f in flags)
      and "worst gap above footer 0.50in [OK]" in out, (flags, out))

# Float hole
flags, out = flags_for(_inst([0, 10], holes=[{
    "kind": "float", "id": "penny-young-pizza-ryc", "gap": 63,  # 0.656in
    "where": "under wrapping text beside art",
}]))
check("0.65in float hole FLAGs",
      any("float hole 0.66in" in f or "float hole 0.65in" in f for f in flags), flags)

flags, out = flags_for(_inst([0, 10], holes=[{
    "kind": "float", "id": "x", "gap": 30,  # 0.3125
    "where": "under wrapping text beside art",
}]))
check("0.31in float hole does not FLAG",
      not any("float hole" in f for f in flags), flags)

# leftover_flags helper
leftovers = B.leftover_flags(_inst([0, 211], footer_gaps_px=[48]))
check("leftover_flags names the 2.20in hole",
      any("2.20in" in x for x in leftovers), leftovers)

# ----- reined-in balancer (Frank t229u) -------------------------------------

print("=== balancer is report-only ===")
check("move picker is gone (no box moves, no neighbour stripping)", not hasattr(B, "_pick_move"))
check("balance modes are report and pair only", B.BALANCE_MODES == ("report", "pair"), B.BALANCE_MODES)
sugg = B._suggestions(_inst([0, 211], footer_gaps_px=[48]))
check("report mode turns a hole into a plain-words suggestion",
      any("2.20in short" in x and "grow the copy" in x for x in sugg), sugg)
import inspect as _inspect
_src = _inspect.getsource(B.run_balance)
check("run_balance never crops, moves, floats, or unwraps",
      not any(k in _src for k in ("safe_cover_crop", "moveItem", "floatIntoLead", "setArtSrc", "unwrapLonelySplits")))

# ----- block-gap rhythm in report() ------------------------------------------
inst = _inst([0, 10])
inst["pages"][0]["block_gaps"] = [
    {"where": "page", "above": "rail-block", "below": "box", "gap": 9.3},      # 7pt OK
    {"where": "page", "above": "box", "below": "box-pair", "gap": 0.0},        # touching
    {"where": "page", "above": "rail-block", "below": "box", "gap": 46.7},     # 35pt stretch
]
flags, out = flags_for(inst)
check("a touching pair of blocks FLAGs", any("gap 0.0pt" in f for f in flags), flags)
check("a 35pt stretched gap FLAGs", any("gap 35.0pt" in f for f in flags), flags)
check("a 7pt gap does not FLAG", not any("gap 7.0pt" in f for f in flags), flags)

# ----- Chrome fixture: FLAG without balance; report-only balance; send gate ----

print("=== Chrome instrument + balancer fixture ===")
sys.path.insert(0, str(g.ROOT / "compose"))
from gazette import (  # noqa: E402
    box, cols3, dateline, document, footer, masthead, page, paras, piece,
    render_piece, split, stack, write_issue,
)

fx = TMP / "fx-issue"
(fx / "recipe").mkdir(parents=True)
# write_issue wants issues/<date> under ROOT, so write the HTML ourselves.
tall_copy = (
    "This is fixture copy used only to take up depth in the tall half of a split. "
    "It is not published. " * 2
)
from PIL import Image as _Im
# A tall raster so the instrument counts ink (an empty spacer would be a
# phantom hole). ~3.2in at ~1.65in wide, 96 dpi CSS.
_Im.new("RGB", (160, 310), (200, 200, 200)).save(fx / "tall.png")
tall_img = '<img src="tall.png" alt="" style="width:100%;height:auto;display:block">'
short_rail = "A short rail item, only a couple of lines, so the rail stays shallow."
parents_copy = "A balanced bottom-row item so the footer gap can pass while the cols3 still has a hole."
camp_copy = "The other half of the balanced bottom row, about the same length as its pair."

p1 = page(
    masthead()
    + "\n"
    + dateline("Fixture Edition", "Vol. I — Balance fixture · November 16, 2026")
    + "\n"
    + cols3(
        stack(
            piece("A Tall Lead", paras("Lead fixture paragraph. " * 4), level=1, cls="lead"),
            split(
                ('<figure class="art" data-art="tall-placeholder" data-kind="illustration" '
                 'data-region="span2" data-flex="false"><img src="tall.png" alt=""></figure>'),
                box("Ratings Earned", paras("Mila Siu  C26  Fixture event.")),
                widths=[1, 2],
            ),
        ),
        render_piece(piece("Short Rail", paras(short_rail), kicker="Rail")),
    )
    + "\n"
    + split(
        render_piece(piece("Parents item", paras(parents_copy), kicker="For the Parents")),
        render_piece(piece("Camp item", paras(camp_copy), kicker="Club Events")),
        widths=[1, 1],
    )
    + "\n"
    + footer(0)
)
p2 = page(
    dateline("Page Two", "Balance fixture · Vol. I", first=False)
    + "\n"
    + paras("Page two of the balance fixture. It exists so the renderer keeps a two-page sheet.")
    + "\n"
    + footer(0),
    cls="fit",
)
html_path = fx / "issue.html"
html_path.write_text(document("Balance fixture", [p1, p2]), encoding="utf-8")

repo = g.ROOT


def run_render(out_pdf, report_path, extra):
    import subprocess
    cmd = [sys.executable, str(repo / "compose" / "render.py"),
           str(html_path), str(out_pdf),
           f"--report={report_path}", "--no-fit", *extra]
    r = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True)
    (Path(str(out_pdf) + ".log")).write_text(r.stdout + "\n" + r.stderr)
    return r


# 1) Instrument only: the cols3 rail hole must FLAG at 0.35in.
pdf_a = TMP / "unbalanced.pdf"
rep_a = TMP / "unbalanced.json"
r = run_render(pdf_a, rep_a, ["--no-balance", "--allow-flag"])
check("unbalanced fixture rendered", pdf_a.is_file() and rep_a.is_file(),
      (r.returncode, (r.stderr or r.stdout)[-400:]))
if rep_a.is_file():
    data = json.loads(rep_a.read_text())
    # Page 1 row 1 is the cols3; the rail (column 2) should have a big bottom gap.
    rows = (data.get("pages") or [{}])[0].get("rows") or []
    cols3_row = next((row for row in rows if row.get("kind") in ("columns", "cols3")),
                     rows[0] if rows else {})
    gaps = [px / 96.0 for px in (cols3_row.get("col_gaps") or [])]
    check("unbalanced fixture measures per-column col_gaps",
          len(gaps) >= 2, cols3_row)
    if gaps:
        check("unbalanced rail hole is above 0.35in (the new FLAG)",
              max(gaps) > 0.35, gaps)
        check("unbalanced fixture still has a last-row footer measurement",
              "gaps" in (data.get("pages") or [{}])[0], data.get("pages"))

# 2) Default balancer (report-only): nothing moves; the hole is reported with a suggestion.
pdf_b = TMP / "balanced.pdf"
rep_b = TMP / "balanced.json"
r = run_render(pdf_b, rep_b, ["--allow-flag"])
check("report-only fixture rendered", pdf_b.is_file() and rep_b.is_file(),
      (r.returncode, (r.stderr or r.stdout)[-400:]))
if rep_b.is_file():
    data = json.loads(rep_b.read_text())
    bal = (data.get("art_fit") or {}).get("balance") or {}
    check("report mode takes no actions", bal.get("mode") == "report" and not bal.get("actions"), bal.get("actions"))
    check("report mode leaves a suggestion for the hole", bool(bal.get("suggestions")), bal)
    check("Ratings Earned stays where the recipe put it",
          "Ratings Earned" in html_path.read_text() and bal.get("before") == bal.get("after"))

# 3) A failed build is not a proof: <out> is untouched and the PDF is kept as .FAILED.pdf.
pdf_c = TMP / "gate.pdf"
r = run_render(pdf_c, TMP / "gate.json", [])
check("failed build exits non-zero", r.returncode != 0, r.returncode)
check("failed build does not write the proof path", not pdf_c.exists())
check("failed build keeps a .FAILED.pdf", (TMP / "gate.FAILED.pdf").is_file())
check("no draft left behind", not (TMP / "gate.draft.pdf").exists())

print()
if failures:
    print(f"{len(failures)} check(s) failed:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("balance: all checks passed")
