#!/usr/bin/env python3
"""Art-fitting policy for Template A (Frank t212u, design 2026-11-11).

Pure Python: manifest, eligibility, candidate lists, choose(), shortfall hints.
No Chrome. render.py evaluates candidates in one Chrome session and calls choose().
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Estimate-only grid constants (STYLE-GUIDE / historical). Fitting uses measured widths.
PHOTO_CEILING_IN = 2.2
COL1_IN, COL2_IN = 2.42, 4.96
PHOTO_MIN_DPI = 150
PHOTO_SOFT_DPI = 200
LINE_ART_MIN_DPI = 200
LINE_ART_SOFT_DPI = 300
MIN_PRINT_DPI = PHOTO_MIN_DPI  # alias so older imports keep working

# Text measure beside a float: the narrowest column the page already prints.
# (7.5in − 18pt) / 3 − 10pt. Confirmed against Chrome in the fixture run, not baked blindly.
MIN_MEASURE_IN = (7.5 - 18 / 72) / 3 - 10 / 72   # ≈ 2.236in; design draft was 2.28in
FLOAT_GUTTER_IN = 9 / 72                           # 9pt between float and text
LATTICE_IN = 0.125
GUTTER_MAX_IN = 0.25                               # Frank t211u Q2: last-resort side gutter cap
GAP_FLAG_IN = 0.75
SPREAD_FLAG_IN = 0.5
ASPECT_TOL = 0.01
SOFT_HOLE_IN = 0.35
LINE_IN = 0.149                                    # word-hint only, not a cut policy
LETTERED_CAP_PT = 5.0
FIT_VERIFY_TOL_IN = 0.05

KINDS = ("photo", "comic", "diagram", "illustration")
REGIONS = ("rail", "span2", "lower", "full")
ACCEPTABLE = ("ceiling", "dpi", "min_size")
FORBIDDEN_FIELDS = ("crop", "object-fit", "object_fit", "max-height", "max_height", "objectFit", "maxHeight")
REQUIRED = ("id", "src", "kind", "alt", "region")

# Hard floor, soft floor (WARN). Wordless/lightly lettered comics use the illustration floor
# (Frank t211u Q4 / Clark's default). Lettered comics (lettering_px or lettered=true) use 3.0 / 4.5.
FLOORS = {
    "photo":         (1.6, None),
    "illustration":  (1.6, None),
    "comic":         (3.0, 4.5),
    "diagram":       (3.0, 3.5),
}
WORDLESS_FLOOR = 1.6  # sane floor for wordless / lightly lettered comics and illustrations

NOMINAL_W = {"rail": COL1_IN, "span2": COL2_IN, "full": 7.5, "lower": None}


class ArtError(SystemExit):
    """Compose-time refusal (invalid manifest, missing file, crop-style field)."""


# ----------------------------------------------------------------- image size

def image_px(path):
    """Return (width, height) as displayed (EXIF-corrected). SVG: viewBox or width/height, no dpi."""
    path = Path(path)
    if path.suffix.lower() == ".svg":
        return _svg_px(path)
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(path))
    return im.size


def _svg_px(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    vb = re.search(r'viewBox\s*=\s*"([\d.\s-]+)"', text, re.I)
    if vb:
        a = [float(x) for x in vb.group(1).split()]
        if len(a) == 4 and a[2] > 0 and a[3] > 0:
            return int(round(a[2])), int(round(a[3]))
    def dim(name):
        m = re.search(rf'\b{name}\s*=\s*"([\d.]+)(?:px)?"', text, re.I)
        return float(m.group(1)) if m else None
    w, h = dim("width"), dim("height")
    if w and h:
        return int(round(w)), int(round(h))
    return 100, 100


def is_vector(path):
    return Path(path).suffix.lower() == ".svg"


# ----------------------------------------------------------------- floors and caps

def is_lettered(asset):
    """Essential lettering is confirmed when lettering_px is set or lettered=True."""
    if asset.get("lettering_px"):
        return True
    if asset.get("lettered") is True:
        return True
    return False


def floors(asset):
    """(hard_w_in, soft_w_in_or_None, lettering_confirmed).

    Wordless or lightly lettered comics inherit the 1.6in illustration floor (Frank t211u Q4).
    An explicit min_w_in or a lettering_px-derived width replaces both and clears the soft WARN.
    """
    kind = asset["kind"]
    confirmed = is_lettered(asset)
    if asset.get("min_w_in") is not None:
        w = float(asset["min_w_in"])
        return w, None, True
    if asset.get("lettering_px"):
        # printed cap height >= ~5pt: min_w = lettering_px * (5/72) / cap_px * native_w, done in
        # lettering_min_w once pixel size is known. Here we only flag "will be replaced".
        return None, None, True  # sentinel: caller uses lettering_min_w
    if kind == "comic" and not confirmed:
        return WORDLESS_FLOOR, None, False
    hard, soft = FLOORS[kind]
    return hard, soft, confirmed


def lettering_min_w(lettering_px, px_w, cap_pt=LETTERED_CAP_PT):
    """Width at which essential lettering prints at cap_pt (default 5pt)."""
    if not lettering_px or not px_w:
        return None
    # lettering_px / px_w * width_in * 72 = cap_pt  =>  width_in = cap_pt / 72 * px_w / lettering_px
    return (cap_pt / 72.0) * px_w / float(lettering_px)


def dpi_floors(kind, path):
    if is_vector(path) or kind == "illustration" and str(path).lower().endswith(".svg"):
        return None, None
    if kind == "photo":
        return PHOTO_MIN_DPI, PHOTO_SOFT_DPI
    # comic, diagram, raster illustration
    return LINE_ART_MIN_DPI, LINE_ART_SOFT_DPI


def max_w_dpi(px_w, kind, path, accept=()):
    hard, _ = dpi_floors(kind, path)
    if hard is None or not px_w:
        return None
    if "dpi" in (accept or ()):
        return None
    return px_w / hard


def ceiling_w(aspect_wh, kind, accept=()):
    """Max width (in) so a photo's printed height stays at the §19 2.2in ceiling. Photos only."""
    if kind != "photo" or "ceiling" in (accept or ()):
        return None
    if aspect_wh <= 0:
        return None
    # aspect_wh = width/height; height = width / aspect_wh; width = ceiling * aspect_wh
    return PHOTO_CEILING_IN * aspect_wh


def W_hi(region_w, px_w, aspect_wh, kind, path, accept=(), max_w_in=None):
    caps = [region_w]
    m = max_w_dpi(px_w, kind, path, accept)
    if m is not None:
        caps.append(m)
    c = ceiling_w(aspect_wh, kind, accept)
    if c is not None:
        caps.append(c)
    if max_w_in is not None:
        caps.append(float(max_w_in))
    return min(caps)


def float_cap(region_w, min_measure=MIN_MEASURE_IN, gutter=FLOAT_GUTTER_IN):
    return region_w - gutter - min_measure


# ----------------------------------------------------------------- manifest

def _normalize_asset(item, key=None):
    if not isinstance(item, dict):
        raise ArtError("compose REFUSED: art manifest entry is not an object")
    a = dict(item)
    if key and not a.get("id"):
        a["id"] = key
    return a


def load_art_manifest(path):
    """Load recipe/art.json. Accepts {"assets": [...]} or {id: {..}}."""
    path = Path(path)
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        assets = [_normalize_asset(x) for x in data]
    elif isinstance(data, dict) and "assets" in data:
        assets = [_normalize_asset(x) for x in data["assets"]]
    elif isinstance(data, dict):
        assets = [_normalize_asset(v, k) for k, v in data.items() if isinstance(v, dict)]
    else:
        raise ArtError("compose REFUSED: art manifest must be a list or an object")
    for a in assets:
        validate_asset(a)
    return assets


def validate_asset(a, file_path=None):
    for k in FORBIDDEN_FIELDS:
        if k in a and a[k] is not None:
            raise ArtError(f"compose REFUSED: art {a.get('id')!r} has a crop-style field {k!r}; layout never crops")
    missing = [k for k in REQUIRED if not a.get(k)]
    if missing:
        raise ArtError(f"compose REFUSED: art {a.get('id')!r} missing required field(s): {', '.join(missing)}")
    if a["kind"] not in KINDS:
        raise ArtError(f"compose REFUSED: art {a['id']!r} has unknown kind {a['kind']!r}")
    if a["region"] not in REGIONS:
        raise ArtError(f"compose REFUSED: art {a['id']!r} has unknown region {a['region']!r}")
    if a["kind"] == "photo" and not (a.get("caption") or "").strip():
        raise ArtError(f"compose REFUSED: art {a['id']!r} is a photo and needs a caption")
    if a["kind"] == "diagram" and a["region"] == "full" and not a.get("allow_full"):
        raise ArtError(f"compose REFUSED: art {a['id']!r} is a diagram in a full-width region; set allow_full")
    acc = a.get("accept") or {}
    if isinstance(acc, list):
        flags = acc
    elif isinstance(acc, dict):
        flags = acc.get("flags") or [k for k in ACCEPTABLE if acc.get(k)]
        if acc.get("exceptions"):
            flags = list(acc["exceptions"])
    else:
        flags = []
    for f in flags:
        if f not in ACCEPTABLE:
            raise ArtError(f"compose REFUSED: art {a['id']!r} accept flag {f!r} is not one of {ACCEPTABLE}")
    a["_accept"] = tuple(flags)
    if file_path and not Path(file_path).is_file():
        raise ArtError(f"compose REFUSED: art {a['id']!r} file is missing: {file_path}")
    return a


def accept_flags(asset):
    if "_accept" in asset:
        return tuple(asset["_accept"])
    acc = asset.get("accept") or {}
    if isinstance(acc, list):
        return tuple(acc)
    if isinstance(acc, dict):
        if "flags" in acc:
            return tuple(acc["flags"])
        return tuple(k for k in ACCEPTABLE if acc.get(k))
    return ()


def default_flex(asset):
    if asset.get("flex") is not None:
        return bool(asset["flex"])
    return asset.get("region") != "rail"


def default_modes(asset):
    if asset.get("modes"):
        modes = asset["modes"]
        if isinstance(modes, str):
            modes = [m.strip() for m in modes.split(",")]
        return list(modes)
    if asset.get("region") in ("rail", "full") or asset.get("kind") == "diagram":
        return ["stack"]
    return ["stack", "float"]


def effective_min_w(asset, px_w=None):
    hard, soft, confirmed = floors(asset)
    if hard is None and asset.get("lettering_px") and px_w:
        hard = lettering_min_w(asset["lettering_px"], px_w)
        soft = None
        confirmed = True
    if hard is None:
        hard = WORDLESS_FLOOR
    if "min_size" in accept_flags(asset):
        # recorded exception: still keep a sane absolute floor so a typo can't go to zero
        hard = min(hard, 0.75)
    return hard, soft, confirmed


# ----------------------------------------------------------------- candidates

def lattice(lo, hi, step=LATTICE_IN):
    """Descending widths from hi to lo, inclusive of both ends, on `step` plus the exact ends."""
    if hi < lo - 1e-9:
        return []
    out = [round(hi, 4)]
    # step down, snapping to multiples of `step` below hi
    x = math.floor(hi / step + 1e-9) * step
    if abs(x - hi) < 1e-9:
        x -= step
    while x > lo + 1e-9:
        out.append(round(x, 4))
        x -= step
    if not out or abs(out[-1] - lo) > 1e-9:
        out.append(round(lo, 4))
    # unique, descending
    seen, uniq = set(), []
    for w in out:
        k = round(w, 4)
        if k not in seen:
            seen.add(k); uniq.append(k)
    return uniq


def candidates(asset, region_w, wrap_ok=False, px_w=None, px_h=None, path=None, include_gutter=True):
    """Finite, static candidate list in evaluation order: stack, floats (wide→narrow), gutters last.

    region_w is the measured content width of the region, in inches.
    wrap_ok: there is wrap-eligible prose after the slot in the same container.
    Gutter stacks (width = region_w − g, g ≤ 0.25in, flush left) are last-resort rungs for
    the C1 reachability band (Frank t211u Q2). Smaller gutters come first (flush preferred).
    """
    kind = asset["kind"]
    path = path or asset.get("_path") or asset.get("src")
    if px_w and px_h:
        aspect_wh = px_w / px_h
    else:
        aspect_wh = 1.0
    accept = accept_flags(asset)
    w_lo, soft, confirmed = effective_min_w(asset, px_w)
    w_hi = W_hi(region_w, px_w, aspect_wh, kind, path, accept, asset.get("max_w_in"))
    modes = default_modes(asset)
    out = []

    def elig(w, mode, gutter=0.0, reason=""):
        why = []
        if w + 1e-9 < w_lo and "min_size" not in accept:
            why.append(f"below hard floor {w_lo:.2f}in")
        if w - 1e-9 > w_hi:
            why.append(f"above cap {w_hi:.2f}in")
        # dpi at this width
        hard_dpi, soft_dpi = dpi_floors(kind, path)
        dpi = (px_w / w) if (px_w and w) else None
        if hard_dpi and dpi is not None and dpi < hard_dpi - 0.5 and "dpi" not in accept:
            why.append(f"{dpi:.0f} dpi below hard floor {hard_dpi}")
        # photo ceiling at this width
        if kind == "photo" and "ceiling" not in accept and aspect_wh:
            tall = w / aspect_wh
            if tall > PHOTO_CEILING_IN + 1e-9:
                why.append(f"{tall:.2f}in tall, over the {PHOTO_CEILING_IN}in ceiling")
        rec = {
            "mode": mode, "width": round(w, 4), "gutter": round(gutter, 4),
            "eligible": not why, "why": why,
            "soft_floor": soft, "lettering_confirmed": confirmed,
            "dpi": None if dpi is None else round(dpi, 1),
            "height": round(w / aspect_wh, 4) if aspect_wh else None,
        }
        if reason:
            rec["note"] = reason
        return rec

    # 1. stack at region width
    if "stack" in modes:
        c = elig(region_w, "stack")
        c["role"] = "stack"
        out.append(c)

    # 2. floats, wide to narrow, only when wrap_ok and float is an allowed mode
    cap = float_cap(region_w)
    if "float" in modes and wrap_ok and cap >= w_lo - 1e-9:
        top = min(w_hi, cap)
        for w in lattice(w_lo, top):
            c = elig(w, "float")
            c["role"] = "float"
            out.append(c)
    elif "float" in modes and not wrap_ok:
        out.append({
            "mode": "float", "width": None, "gutter": 0, "eligible": False,
            "why": ["no wrap-eligible prose after the slot; place the art before the prose it should wrap"],
            "role": "float-skipped",
        })

    # 3. last-resort gutter stacks (C1 band). Prefer smaller gutters (flush-to-grid first).
    if include_gutter and "stack" in modes and region_w > 0:
        gutters = lattice(LATTICE_IN, GUTTER_MAX_IN)
        gutters = sorted(set(gutters + [GUTTER_MAX_IN, LATTICE_IN]))
        for g in gutters:
            if g < 1e-9 or g - 1e-9 > GUTTER_MAX_IN:
                continue
            w = region_w - g
            c = elig(w, "gutter", gutter=g)
            c["role"] = "gutter"
            out.append(c)

    return out


# ----------------------------------------------------------------- choose()

def hard_gates(rec):
    """Return (pass?, residual_inches, reasons). rec is a measurement dict in inches."""
    reasons = []
    residual = 0.0
    overflow = rec.get("overflow_in") or 0.0
    if overflow > 0.02:
        reasons.append(f"overflow {overflow:.2f}in")
        residual += overflow * 10
    min_gap = rec.get("min_gap_in")
    if min_gap is not None and min_gap < -0.02:
        reasons.append(f"footer overlap {min_gap:.2f}in")
        residual += abs(min_gap) * 10
    worst = rec.get("worst_gap_in")
    if worst is not None and worst > GAP_FLAG_IN:
        reasons.append(f"footer gap {worst:.2f}in > {GAP_FLAG_IN}in")
        residual += worst - GAP_FLAG_IN
    spread = rec.get("max_spread_in") or 0.0
    if spread > SPREAD_FLAG_IN:
        reasons.append(f"column spread {spread:.2f}in > {SPREAD_FLAG_IN}in")
        residual += spread - SPREAD_FLAG_IN
    err = rec.get("aspect_err") or 0.0
    if err > ASPECT_TOL:
        reasons.append(f"aspect error {err:.1%} (possible crop or distortion)")
        residual += (err - ASPECT_TOL) * 10
    return (not reasons), residual, reasons


def soft_warns(rec, cand, asset, region_w=None):
    warns = []
    if cand.get("mode") == "float" and (rec.get("float_hole_in") or 0) > SOFT_HOLE_IN:
        warns.append(f"float hole {rec['float_hole_in']:.2f}in > {SOFT_HOLE_IN}in")
    if (rec.get("interior_gap_in") or 0) > SOFT_HOLE_IN:
        warns.append(f"interior gap above art {rec['interior_gap_in']:.2f}in")
    soft = cand.get("soft_floor")
    if soft and cand.get("width") and cand["width"] + 1e-9 < soft and not cand.get("lettering_confirmed"):
        warns.append(f"width {cand['width']:.2f}in is below the unconfirmed soft floor {soft:.2f}in")
    dpi, kind = cand.get("dpi"), asset.get("kind")
    path = asset.get("_path") or asset.get("src") or ""
    _, soft_dpi = dpi_floors(kind, path)
    if dpi and soft_dpi and dpi < soft_dpi - 0.5:
        warns.append(f"{dpi:.0f} dpi is below the soft target {soft_dpi}")
    nominal = NOMINAL_W.get(asset.get("region"))
    w = region_w if region_w is not None else rec.get("region_w_in")
    if nominal and w and abs(w - nominal) / nominal > 0.10:
        warns.append(f"region width {w:.2f}in differs more than 10% from nominal {nominal:.2f}in (not on grid)")
    return warns


def choose(cands, records, asset, region_w=None):
    """Pick a candidate from (cands, records) measured 1:1.

    Order: a legal stack always wins (dominance). Then floats, wide to narrow, Tier A
    (hard gates, no soft WARNs) before Tier B (hard gates with WARNs). Then gutter
    stacks, small gutter first, same tiering. If nothing passes, the lowest residual
    (overflow ×10) wins and the caller FLAGs with a shortfall report.
    """
    pairs = []
    for c, r in zip(cands, records):
        if c.get("role") == "float-skipped" or not c.get("eligible", True) or c.get("width") is None:
            continue
        ok, resid, reasons = hard_gates(r)
        warns = soft_warns(r, c, asset, region_w)
        pairs.append({
            "cand": c, "rec": r, "ok": ok, "residual": resid,
            "reasons": reasons, "warns": warns,
        })

    def first(pred):
        for p in pairs:
            if pred(p):
                return p
        return None

    stack = first(lambda p: p["cand"].get("mode") == "stack" and p["cand"].get("role") == "stack")
    # A legal stack always wins; soft checks never demote it.
    if stack and stack["ok"]:
        return _decision(stack, "stack-passes", pairs, asset, region_w)

    # Floats, already in wide-to-narrow order in `pairs`
    float_a = first(lambda p: p["cand"].get("mode") == "float" and p["ok"] and not p["warns"])
    if float_a:
        return _decision(float_a, "float-tier-a", pairs, asset, region_w)
    float_b = first(lambda p: p["cand"].get("mode") == "float" and p["ok"])
    if float_b:
        return _decision(float_b, "float-tier-b", pairs, asset, region_w)

    gut_a = first(lambda p: p["cand"].get("mode") == "gutter" and p["ok"] and not p["warns"])
    if gut_a:
        return _decision(gut_a, "gutter-tier-a", pairs, asset, region_w)
    gut_b = first(lambda p: p["cand"].get("mode") == "gutter" and p["ok"])
    if gut_b:
        return _decision(gut_b, "gutter-tier-b", pairs, asset, region_w)

    # Nothing passed. Lowest residual; ties keep the earlier candidate.
    if not pairs:
        return {
            "ok": False, "flag": True, "cand": None, "rec": None,
            "reason": "no eligible candidates",
            "report": shortfall_report(None, None, asset, region_w, pairs),
            "pairs": pairs,
        }
    best = min(range(len(pairs)), key=lambda i: (pairs[i]["residual"], i))
    return _decision(pairs[best], "residual", pairs, asset, region_w, flag=True)


def _decision(pick, why, pairs, asset, region_w, flag=False):
    report = shortfall_report(pick["cand"], pick["rec"], asset, region_w, pairs)
    return {
        "ok": pick["ok"] and not flag,
        "flag": flag or not pick["ok"],
        "cand": pick["cand"],
        "rec": pick["rec"],
        "warns": pick.get("warns") or [],
        "reasons": pick.get("reasons") or [],
        "residual": pick["residual"],
        "why": why,
        "report": report,
        "pairs": pairs,
    }


def shortfall_report(cand, rec, asset, region_w, pairs):
    """Operator hint (not a cut policy). Describes the three cases and the C1 band when it applies."""
    lines = []
    stack_p = next((p for p in pairs if p["cand"].get("role") == "stack"), None)
    float_ps = [p for p in pairs if p["cand"].get("mode") == "float" and p["cand"].get("eligible", True)]
    largest_float = float_ps[0] if float_ps else None  # list is wide→narrow

    def gap(p):
        if not p or not p.get("rec"):
            return None
        return p["rec"].get("worst_gap_in")

    def over(p):
        if not p or not p.get("rec"):
            return False
        r = p["rec"]
        return (r.get("overflow_in") or 0) > 0.02 or (r.get("min_gap_in") is not None and r["min_gap_in"] < -0.02)

    aspect = None
    if cand and cand.get("height") and cand.get("width"):
        aspect = cand["width"] / cand["height"]
    # next-wider region hint
    if region_w and aspect:
        wider = None
        if region_w < 6.5:
            wider = ("full width", 7.5 / aspect)
        if wider:
            lines.append(f"a {wider[0]} stack would be {wider[1]:.2f}in tall")

    if stack_p and stack_p["ok"]:
        g = gap(stack_p)
        if g is not None:
            words = word_hint(g, region_w)
            extra = f"; or about {words} words" if words else ""
            lines.insert(0, f"stack leaves a {g:.2f}in footer gap{extra}")
        return lines

    if stack_p and not over(stack_p) and (gap(stack_p) or 0) > GAP_FLAG_IN:
        g = gap(stack_p)
        words = word_hint(g, region_w)
        extra = f"; or about {words} words" if words else ""
        lines.insert(0, f"width-constrained: stack is legal but leaves a {g:.2f}in gap (>{GAP_FLAG_IN}in). A float cannot close this hole{extra}")
        return lines

    if stack_p and over(stack_p) and largest_float and not over(largest_float) and (gap(largest_float) or 0) > GAP_FLAG_IN:
        sg = gap(stack_p)
        fg = gap(largest_float)
        words_cut = word_hint(abs(stack_p["rec"].get("overflow_in") or 0) or max(-(stack_p["rec"].get("min_gap_in") or 0), 0), region_w)
        words_fill = word_hint(fg, region_w) if fg else None
        lines.insert(0, (
            f"C1 reachability band: stack overshoots"
            + (f" (overflow/overlap)" if sg is None or sg < 0 else f" (gap {sg:.2f}in)")
            + f"; the largest float leaves a {fg:.2f}in gap. No legal width hits the {GAP_FLAG_IN}in window."
        ))
        if words_cut:
            lines.append(f"hint (not a cut policy): about {words_cut} words less might let the stack pass")
        if words_fill:
            lines.append(f"hint: about {words_fill} words more might fill the float")
        lines.append(f"a last-resort gutter of at most {GUTTER_MAX_IN}in was tried if eligible")
        return lines

    if rec and cand:
        g = rec.get("worst_gap_in")
        if g is not None:
            lines.insert(0, f"chosen {cand.get('mode')} at {cand.get('width'):.2f}in leaves a {g:.2f}in footer gap")
    return lines


def word_hint(gap_in, measure_in=None):
    """Rough word count to fill (or cut) a gap. A hint for the report, not STYLE-GUIDE §16 policy."""
    if gap_in is None or gap_in <= 0:
        return None
    measure = measure_in or COL1_IN
    # ~5.5 characters/word at 8.5pt; ~0.44 em/char → words per line
    em = 8.5 / 72
    words_per_line = max(4, int(measure / (5.5 * 0.44 * em)))
    lines = gap_in / LINE_IN
    n = int(round(lines * words_per_line))
    return n if n > 0 else None


# ----------------------------------------------------------------- photo_span (wrapper, parity with the old rule)

def photo_span(path, is_results_photo=True, root=None):
    """Placement rule for the week's photo. Returns (columns, reason).

    A results photo runs two columns wide under the lead only when, at COL2_IN and uncropped,
    it (1) stays within the §19 height ceiling and (2) still has 150 dpi. Otherwise it runs
    one column in the rail. Cropping is the photo desk's call, never CSS.
    """
    if not is_results_photo:
        return 1, "not a results photo; one column"
    root = root or ROOT
    p = Path(path)
    if not p.is_file():
        p = root / path
    try:
        w, h = image_px(p)
    except Exception as e:
        return 1, f"could not measure ({e}); one column"
    tall2, dpi2 = COL2_IN * h / w, w / COL2_IN
    if tall2 > PHOTO_CEILING_IN:
        return 1, (f"{w}x{h}: {tall2:.1f}in tall at two columns, over the {PHOTO_CEILING_IN}in ceiling; "
                   f"one column ({COL1_IN * h / w:.1f}in)")
    if dpi2 < PHOTO_MIN_DPI:
        return 1, f"{w}x{h}: only {dpi2:.0f} dpi at two columns; one column"
    return 2, f"{w}x{h}: {tall2:.1f}in tall, {dpi2:.0f} dpi at two columns"


# ----------------------------------------------------------------- markup

def art_markup(asset, src=None, credit_html=None):
    """Emit a <figure class="art"> with data-art* attributes for the fitter. No crop CSS."""
    import html as _html
    src = src or asset["src"]
    kind = asset["kind"]
    region = asset["region"]
    flex = "true" if default_flex(asset) else "false"
    modes = ",".join(default_modes(asset))
    alt = _html.escape(asset["alt"], quote=True)
    cap = asset.get("caption")
    credit = credit_html or ""
    cap_html = f'<p class="caption">{cap}</p>' if cap else ""
    cls = "art"
    attrs = [
        f'class="{cls}"',
        f'data-art="{_html.escape(asset["id"], quote=True)}"',
        f'data-kind="{kind}"',
        f'data-region="{region}"',
        f'data-flex="{flex}"',
        f'data-modes="{modes}"',
        f'data-src="{_html.escape(src, quote=True)}"',
    ]
    if asset.get("anchor") is not None:
        attrs.append(f'data-anchor="{_html.escape(str(asset["anchor"]), quote=True)}"')
    w_lo, soft, confirmed = effective_min_w(asset)
    if w_lo:
        attrs.append(f'data-min-w="{w_lo:.4f}"')
    if soft:
        attrs.append(f'data-soft-w="{soft:.4f}"')
    attrs.append(f'data-lettered="{"true" if confirmed else "false"}"')
    inner = f'<img src="{_html.escape(src, quote=True)}" alt="{alt}">' + cap_html + credit
    return f'<figure {" ".join(attrs)}>{inner}</figure>'


# ----------------------------------------------------------------- output-path guard (P0)

def frozen_output_path(out, root=None, force=False):
    """If `out` sits under an APPROVED issues/<date>/ folder, return a refusal message, else None."""
    if force:
        return None
    root = Path(root or ROOT).resolve()
    out = Path(out).resolve()
    issues = (root / "issues").resolve()
    try:
        rel = out.relative_to(issues)
    except ValueError:
        return None
    if not rel.parts:
        return None
    date = rel.parts[0]
    meta = issues / date / "issue.json"
    if not meta.is_file():
        return None
    try:
        status = str(json.loads(meta.read_text(encoding="utf-8")).get("status", ""))
    except Exception:
        return None
    if status.upper().startswith("APPROVED"):
        return (f"render REFUSED: issues/{date} is approved/published. "
                "Write the PDF somewhere else (for a trial), or pass --force to overwrite.")
    return None
