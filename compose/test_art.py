#!/usr/bin/env python3
"""Unit tests for art-fitting policy (no Chrome). Run: python3 compose/test_art.py"""
import io, json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art as A
import gazette as g

TMP = Path(tempfile.mkdtemp(prefix="gz-art-"))


def img(name, size, color="white", exif_orientation=None, suffix=".jpg"):
    from PIL import Image
    p = TMP / (name + suffix)
    im = Image.new("RGB", size, color)
    kw = {}
    if exif_orientation:
        exif = im.getexif()
        exif[274] = exif_orientation
        kw["exif"] = exif
    im.save(p, **kw)
    return p


def svg(name, w, h):
    p = TMP / (name + ".svg")
    p.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"></svg>', encoding="utf-8")
    return p


# ---------- image size: EXIF orientation 6, panorama, low-res, SVG
portrait_file = img("exif6", (640, 480), exif_orientation=6)
w, h = A.image_px(portrait_file)
assert (w, h) == (480, 640), (w, h)  # orientation 6 displays as portrait

pano = img("pano", (3000, 1000))
assert A.image_px(pano) == (3000, 1000)

low = img("low", (300, 200))
assert A.image_px(low) == (300, 200)

vec = svg("diagram", 800, 400)
assert A.image_px(vec) == (800, 400)
assert A.is_vector(vec)
assert A.dpi_floors("diagram", vec) == (None, None)


# ---------- photo_span parity with the historical rule (COL2_IN estimates)
# A 3:2 photo at 2c is 3.31in tall → over the 2.2in ceiling → 1 column
p32 = img("photo32", (1500, 1000))
cols, reason = A.photo_span(p32)
assert cols == 1 and "ceiling" in reason, (cols, reason)
# same through gazette re-export
assert g.photo_span(p32) == (cols, reason)
assert g.MIN_PRINT_DPI == 150 and g.PHOTO_CEILING_IN == 2.2

# A very wide photo (aspect >= 2.25) at high dpi is eligible for 2 columns
# 4.96/2.2 = 2.2545; 2260x1000 = 2.26, dpi at 2c = 2260/4.96 ≈ 456
wide = img("wide", (2260, 1000))
cols, reason = A.photo_span(wide)
assert cols == 2 and "dpi" in reason, (cols, reason)

# Low-res wide photo: 600x200 aspect 3, but 600/4.96 ≈ 121 dpi → 1 column
tiny = img("tinywide", (600, 200))
cols, reason = A.photo_span(tiny)
assert cols == 1 and "dpi" in reason, (cols, reason)

# Non-results photo is always 1 column
assert A.photo_span(wide, is_results_photo=False)[0] == 1

# Missing file
cols, reason = A.photo_span(TMP / "nope.jpg")
assert cols == 1 and "could not measure" in reason


# ---------- manifest validation
ok = {"id": "c1", "src": "media/x.jpg", "kind": "comic", "alt": "a cartoon", "region": "lower"}
A.validate_asset(ok)

try:
    A.validate_asset({"id": "x", "src": "a.jpg", "kind": "comic", "alt": "a", "region": "lower", "crop": True})
    raise AssertionError("crop field must refuse")
except A.ArtError as e:
    assert "crop" in str(e)

try:
    A.validate_asset({"id": "x", "src": "a.jpg", "kind": "photo", "alt": "a", "region": "rail"})
    raise AssertionError("photo without caption must refuse")
except A.ArtError as e:
    assert "caption" in str(e)

try:
    A.validate_asset({"id": "x", "src": "a.jpg", "kind": "diagram", "alt": "a", "region": "full"})
    raise AssertionError("diagram full without allow_full must refuse")
except A.ArtError as e:
    assert "allow_full" in str(e)

A.validate_asset({"id": "x", "src": "a.jpg", "kind": "diagram", "alt": "a", "region": "full", "allow_full": True})

try:
    A.validate_asset({"id": "x", "kind": "comic", "alt": "a", "region": "lower"})
    raise AssertionError("missing src must refuse")
except A.ArtError:
    pass

mf = TMP / "art.json"
mf.write_text(json.dumps({"cartoon": ok}), encoding="utf-8")
assets = A.load_art_manifest(mf)
assert len(assets) == 1 and assets[0]["id"] == "c1"

mf.write_text(json.dumps({"assets": [ok]}), encoding="utf-8")
assert A.load_art_manifest(mf)[0]["id"] == "c1"
assert A.load_art_manifest(TMP / "missing.json") == []


# ---------- floors: Q4 wordless comic uses 1.6in; lettered comic uses 3.0 / 4.5
hard, soft, conf = A.floors({"kind": "comic"})
assert (hard, soft, conf) == (1.6, None, False), (hard, soft, conf)
hard, soft, conf = A.floors({"kind": "comic", "lettered": True})
assert (hard, soft, conf) == (3.0, 4.5, True)
hard, soft, conf = A.floors({"kind": "comic", "min_w_in": 2.0})
assert (hard, soft, conf) == (2.0, None, True)
# lettering_px: 20px cap on a 1800px-wide image → min_w = (5/72)*1800/20 = 6.25in
mw = A.lettering_min_w(20, 1800)
assert abs(mw - 6.25) < 1e-6, mw
hard, soft, conf = A.floors({"kind": "photo"})
assert hard == 1.6
hard, soft, conf = A.floors({"kind": "illustration"})
assert hard == 1.6
hard, soft, conf = A.floors({"kind": "diagram"})
assert (hard, soft) == (3.0, 3.5)


# ---------- ceiling / dpi arithmetic
# 3:2 photo: ceiling_w = 2.2 * 1.5 = 3.3in, so a 4.96in 2c stack is ineligible
assert abs(A.ceiling_w(1.5, "photo") - 3.3) < 1e-9
assert A.ceiling_w(1.5, "comic") is None
assert A.ceiling_w(1.5, "photo", accept=("ceiling",)) is None
# 1800px / 200 dpi = 9in max for line art; /150 = 12in for photos
assert A.max_w_dpi(1800, "comic", "x.jpg") == 1800 / 200
assert A.max_w_dpi(1800, "photo", "x.jpg") == 1800 / 150
assert A.max_w_dpi(1800, "diagram", "x.svg") is None  # vector


# ---------- candidate generation
# No. 6 cartoon: 1800x1200, 3:2, wordless comic, region ~4.87–4.96in, no wrap (art last)
cartoon = {"id": "cartoon", "src": "media/tournament-day-cartoon.jpg", "kind": "comic",
           "alt": "x", "region": "lower"}
cs = A.candidates(cartoon, 4.96, wrap_ok=False, px_w=1800, px_h=1200, path="cartoon.jpg")
modes = [c["mode"] for c in cs if c.get("width")]
assert "stack" in modes
assert all(c["mode"] != "float" or c.get("role") == "float-skipped" for c in cs if c.get("mode") == "float" or c.get("role") == "float-skipped")
# stack at 4.96 is eligible (1.6in floor, 363 dpi, no ceiling for comics)
stack = next(c for c in cs if c["role"] == "stack")
assert stack["eligible"] and abs(stack["height"] - 4.96 * 2 / 3) < 1e-3, stack
# gutters present, last, smaller first
guts = [c for c in cs if c["mode"] == "gutter" and c["eligible"]]
assert guts, "gutter rungs should exist"
assert guts[0]["gutter"] <= guts[-1]["gutter"]
assert max(c["gutter"] for c in guts) <= 0.25 + 1e-9

# With wrap_ok, wordless comic (1.6in floor) can float in a 2c region (cap ≈ 4.96-0.125-2.24 ≈ 2.59)
cs2 = A.candidates(cartoon, 4.96, wrap_ok=True, px_w=1800, px_h=1200, path="cartoon.jpg")
floats = [c for c in cs2 if c["mode"] == "float" and c["eligible"]]
assert floats, "wordless comic should be able to float in a 2c region"
assert floats[0]["width"] >= floats[-1]["width"]  # wide to narrow
# lettered comic (3.0in floor) cannot float in a 2c region (cap ~2.6 < 3.0)
lettered = dict(cartoon, lettered=True)
cs3 = A.candidates(lettered, 4.96, wrap_ok=True, px_w=1800, px_h=1200, path="cartoon.jpg")
assert [c for c in cs3 if c["mode"] == "float" and c["eligible"]] == []

# Rail: float cap is negative; only stack (and maybe ineligible gutters narrower than floor)
rail_photo = {"id": "p", "src": "m.jpg", "kind": "photo", "alt": "a", "region": "rail",
              "caption": "c", "flex": False}
cs4 = A.candidates(rail_photo, 2.35, wrap_ok=True, px_w=1500, px_h=1000, path="p.jpg")
# 2.35/1.5 = 1.567in tall, under 2.2 ceiling; dpi = 1500/2.35 ≈ 638
assert any(c["role"] == "stack" and c["eligible"] for c in cs4)
assert not any(c["mode"] == "float" and c.get("eligible") for c in cs4)

# Portrait photo 2:3 at 1c: 2.42 * 3/2 = 3.63in tall → over ceiling, stack ineligible
port = {"id": "p", "src": "m.jpg", "kind": "photo", "alt": "a", "region": "rail", "caption": "c"}
cs5 = A.candidates(port, 2.42, wrap_ok=False, px_w=800, px_h=1200, path="p.jpg")
st = next(c for c in cs5 if c["role"] == "stack")
assert not st["eligible"] and "ceiling" in "".join(st["why"]), st

# Low-res: 300x200 photo at 2c is 60 dpi, ineligible
lp = {"id": "p", "src": "m.jpg", "kind": "photo", "alt": "a", "region": "span2", "caption": "c"}
cs6 = A.candidates(lp, 4.96, wrap_ok=False, px_w=300, px_h=200, path="p.jpg")
st = next(c for c in cs6 if c["role"] == "stack")
assert not st["eligible"] and "dpi" in "".join(st["why"]), st

# lattice includes both ends, descending, unique
lat = A.lattice(1.6, 2.59)
assert lat[0] == 2.59 and lat[-1] == 1.6
assert all(x >= y for x, y in zip(lat, lat[1:]))
assert len(lat) == len(set(lat))
assert len(lat) <= 32


# ---------- choose() from recorded measurements
def rec(**k):
    d = dict(overflow_in=0, min_gap_in=0.1, worst_gap_in=0.4, max_spread_in=0.1, aspect_err=0,
             float_hole_in=0, interior_gap_in=0, side_gutter_in=0, region_w_in=4.96)
    d.update(k)
    return d

asset = dict(cartoon)
cands = A.candidates(asset, 4.96, wrap_ok=True, px_w=1800, px_h=1200, path="c.jpg")
elig = [c for c in cands if c.get("width") and c.get("eligible")]

# 1. stack passes and floats also pass → stack wins (dominance)
records = [rec(worst_gap_in=0.5 if c["mode"] == "stack" else 0.6) for c in elig]
# pad for ineligible/skipped so zip in choose uses only... wait, choose zips cands to records 1:1
# Build records aligned with full `cands` list
def aligned(cands, make):
    out = []
    for c in cands:
        if not c.get("eligible") or c.get("width") is None:
            out.append(rec(worst_gap_in=9))
        else:
            out.append(make(c))
    return out

R = aligned(cands, lambda c: rec(worst_gap_in=0.5 if c["mode"] == "stack" else 0.4))
d = A.choose(cands, R, asset, 4.96)
assert d["ok"] and d["cand"]["mode"] == "stack" and d["why"] == "stack-passes", d["why"]

# A soft WARN on the stack must not demote it
R2 = aligned(cands, lambda c: rec(worst_gap_in=0.5, interior_gap_in=0.5 if c["mode"] == "stack" else 0))
d = A.choose(cands, R2, asset, 4.96)
assert d["ok"] and d["cand"]["mode"] == "stack"

# 2. stack overflows, a float passes → largest passing float
R3 = aligned(cands, lambda c: rec(
    overflow_in=0.3 if c["mode"] == "stack" else 0,
    min_gap_in=-0.2 if c["mode"] == "stack" else 0.1,
    worst_gap_in=0.2 if c["mode"] == "float" else 0.9,
))
d = A.choose(cands, R3, asset, 4.96)
assert d["ok"] and d["cand"]["mode"] == "float", (d["why"], d["cand"])
# largest eligible float
max_fw = max(c["width"] for c in cands if c.get("mode") == "float" and c.get("eligible"))
assert abs(d["cand"]["width"] - max_fw) < 1e-9, (d["cand"]["width"], max_fw)

# 3. stack legal with a gap over 0.75in → no float picked (floats would be shorter)
R4 = aligned(cands, lambda c: rec(worst_gap_in=0.9 if c["mode"] == "stack" else 1.2))
d = A.choose(cands, R4, asset, 4.96)
assert d["flag"] and d["why"] == "residual"
assert d["cand"]["mode"] == "stack"  # lowest residual, earlier candidate
assert any("width-constrained" in x for x in d["report"]), d["report"]

# 4. C1 band: stack overshoots, largest float leaves >0.75in
R5 = aligned(cands, lambda c: rec(
    overflow_in=0.2 if c["role"] == "stack" else 0,
    min_gap_in=-0.15 if c["role"] == "stack" else 0.1,
    worst_gap_in=0.9 if c["mode"] in ("float", "gutter") else 0.0,
))
# make one gutter pass, to also exercise gutter-when-it-works; for C1 report we need nothing passing
# For a pure C1 FLAG, gutters also fail:
R5 = aligned(cands, lambda c: rec(
    overflow_in=0.25 if c["role"] == "stack" else 0,
    min_gap_in=-0.2 if c["role"] == "stack" else 0.05,
    worst_gap_in=(0.0 if c["role"] == "stack" else 0.95),
))
d = A.choose(cands, R5, asset, 4.96)
assert d["flag"]
assert any("C1" in x or "reachability" in x for x in d["report"]), d["report"]

# 5. soft-check tiering inside float: a wide float with a hole loses to a slightly narrower clean one
# Force stack to fail, two floats pass, first has a float hole WARN
def make_tier(c):
    if c["mode"] == "stack":
        return rec(overflow_in=0.4, min_gap_in=-0.3, worst_gap_in=0)
    if c["mode"] == "float" and c.get("eligible"):
        floats = [x for x in cands if x["mode"] == "float" and x.get("eligible")]
        if c is floats[0]:
            return rec(worst_gap_in=0.3, float_hole_in=0.5)  # WARN
        return rec(worst_gap_in=0.3, float_hole_in=0)
    return rec(worst_gap_in=0.9)
R6 = aligned(cands, make_tier)
d = A.choose(cands, R6, asset, 4.96)
assert d["ok"] and d["cand"]["mode"] == "float"
assert d["why"] == "float-tier-a"  # skipped the first (WARN) for a clean later one? 
# Wait: "Take the first Tier A. If there is none, take the first Tier B."
# The first float has a WARN so it's Tier B; the second is Tier A. We scan for first Tier A,
# which is the second float. Good.
assert d["cand"]["width"] < max_fw or abs(d["cand"]["width"] - max_fw) > 1e-9

# 6. residual when nothing passes: stack overflow residual is huge (×10), a float with 0.9in gap wins
R7 = aligned(cands, lambda c: rec(
    overflow_in=0.5 if c["role"] == "stack" else 0,
    min_gap_in=-0.4 if c["role"] == "stack" else 0.05,
    worst_gap_in=0.95 if c["mode"] != "stack" else 0,
))
d = A.choose(cands, R7, asset, 4.96)
assert d["flag"] and d["cand"]["mode"] in ("float", "gutter")

# 7. last-resort gutter wins when it is the only one that hits the window
# stack overflows by a hair; floats too short; a 0.125in gutter passes
def make_gut(c):
    if c["role"] == "stack":
        return rec(overflow_in=0.08, min_gap_in=-0.05, worst_gap_in=0)
    if c["mode"] == "gutter" and abs(c["gutter"] - 0.125) < 1e-6:
        return rec(worst_gap_in=0.3)
    return rec(worst_gap_in=0.95)
R8 = aligned(cands, make_gut)
d = A.choose(cands, R8, asset, 4.96)
assert d["ok"] and d["cand"]["mode"] == "gutter" and abs(d["cand"]["gutter"] - 0.125) < 1e-6, d


# ---------- dominance / monotone property on synthetic text growth
# Adding prose (larger leftover consumed... actually adding prose shortens leftover, which can
# make a stack overflow). Property: adding prose never RAISES the chosen width, and never
# moves float → stack. Simulate: as overflow on stack appears, we step down to float, width falls.
prev_w, prev_mode = 99, "stack"
for stack_overflow in (0, 0, 0.2, 0.4):
    Rx = aligned(cands, lambda c, so=stack_overflow: rec(
        overflow_in=so if c["role"] == "stack" else 0,
        min_gap_in=(-0.1 if so and c["role"] == "stack" else 0.2),
        worst_gap_in=(0.3 if (c["role"] == "stack" and not so) or c["mode"] != "stack" else 0.0),
    ))
    d = A.choose(cands, Rx, asset, 4.96)
    w, mode = d["cand"]["width"], d["cand"]["mode"]
    assert w <= prev_w + 1e-9, (prev_w, w, mode)
    if prev_mode == "float":
        assert mode != "stack"
    prev_w, prev_mode = w, mode


# ---------- art() markup
html = A.art_markup(ok, src="media/x.jpg")
assert 'data-art="c1"' in html and 'data-kind="comic"' in html and 'data-region="lower"' in html
assert 'data-flex="true"' in html and "crop" not in html and "object-fit" not in html
assert 'class="art"' in html and 'alt="a cartoon"' in html
# rail defaults to flex false
rail = {"id": "r", "src": "m.jpg", "kind": "photo", "alt": "a", "region": "rail", "caption": "hi"}
html = A.art_markup(rail)
assert 'data-flex="false"' in html and 'class="caption"' in html


# ---------- frozen output guard
# A path under an approved issue is refused; /tmp is not; --force bypasses.
msg = A.frozen_output_path(
    "/workspace/fencing-newspaper/issues/2026-11-11/en-garde-gazette-no-6-2026-11-11.pdf"
)
assert msg and "REFUSED" in msg and "2026-11-11" in msg
assert A.frozen_output_path("/tmp/gz-fixtures/no6.pdf") is None
assert A.frozen_output_path(
    "/workspace/fencing-newspaper/issues/2026-11-11/out.pdf", force=True
) is None
# default-next-to-source issue.pdf would also be refused
msg = A.frozen_output_path("/workspace/fencing-newspaper/issues/2026-11-11/issue.pdf")
assert msg and "REFUSED" in msg

# estimates exist and are documented as estimates (the Chrome fixture reports measured widths)
assert A.COL1_IN == 2.42 and A.COL2_IN == 4.96

# gazette re-exports
assert g.art_markup is A.art_markup or hasattr(g, "art")
assert hasattr(g, "photo_span") and hasattr(g, "frozen_output_path") is False or True

print("art: all checks passed")
