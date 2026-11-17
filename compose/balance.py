#!/usr/bin/env python3
"""Row-balance pass for Template A (STYLE-GUIDE §13, §19).

After art-fit, this pass evens out short columns in every row band so the
fill instrument's per-column bottom-gap check can pass. It is general
composer/fit behavior, not a one-issue layout.

REINED IN 2026-11-16 (Frank t229u, after the No. 7 v2 review): the pass is
report-only by default. The numbered moves below are history; only photo
pairing (2) survives, and only behind ``--balance=pair``. ``safe_cover_crop``
stays as an editorial helper but the balancer never calls it.

What it used to do:

1. Move a short box (``.box`` that is not ``.w3``) or a short rail piece
   (``.rail-block``, ``.slot-a``, ``.slot-b``, never the lead, masthead,
   dateline or footer) from a tall column — or out of an uneven nested
   split — into the shorter column or rail of the same page. Unwrap a
   split that is left with one child.

2. Pair two photos that sit in the same tall column into an equal
   ``.split``, so they share a row instead of stacking.

3. Scale a photo toward its floors / under the 2.2in ceiling, or apply a
   prepared face-safe backdrop cover-crop (the keep-band is preserved;
   the printed credit gains ``(cropped)``). Lettered comics are never
   cover-cropped; they may already have shrunk within art-fit floors.

Leftover gaps are reported (size and location). This pass never invents
or pads copy to close a hole. The crop is a real image file written
beside the original, not CSS ``object-fit: cover``.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import unquote, urlparse

from art import (
    COL_GAP_FLAG_IN,
    GAP_FLAG_IN,
    PHOTO_CEILING_IN,
    PHOTO_CROP_MIN_H_IN,
    FOOTER_PIN_FLAG_IN,
    frozen_output_path,
)

# Vertical band, as a fraction of the *original* image height, that a
# backdrop cover-crop must keep in full. Tournament portraits typically
# put faces and torsos in roughly this window; the crop prefers to take
# from the banner above it and the floor below it. A tighter target that
# cannot contain the band is refused — we never cut through it.
DEFAULT_KEEP_BAND = (0.10, 0.55)

CREDIT_CROPPED = "(cropped)"
MAX_PASSES = 8


def safe_cover_crop(src, dest, target_aspect, keep_band=DEFAULT_KEEP_BAND):
    """Crop ``src`` to ``target_aspect`` (width/height) without touching keep_band.

    Vertical crops (a tall portrait made shorter) take from the top
    (backdrop) first, then the bottom (floor), and refuse if the keep-band
    would not fit in the output window. Horizontal crops (a wide image
    made narrower) take equal amounts from both sides.

    Returns a dict: ``cropped`` (bool), ``reason``, ``box`` (left, top,
    right, bottom) in source pixels, sizes. The original file is never
    overwritten; ``dest`` is a sibling ``*-fillcrop.*`` path.
    """
    from PIL import Image

    src = Path(src)
    dest = Path(dest)
    im = Image.open(src)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    w, h = im.size
    if w < 1 or h < 1:
        return {"cropped": False, "reason": "empty image", "src_size": (w, h)}
    if target_aspect is None or target_aspect <= 0:
        return {"cropped": False, "reason": "invalid target aspect", "src_size": (w, h)}
    src_aspect = w / h
    lo, hi = keep_band
    if not (0 <= lo < hi <= 1):
        return {"cropped": False, "reason": "invalid keep-band", "src_size": (w, h)}

    if abs(src_aspect - target_aspect) < 0.02:
        return {"cropped": False, "reason": "already at target aspect", "src_size": (w, h)}

    if src_aspect < target_aspect:
        # Too tall: crop height to w / target_aspect.
        new_h = max(1, int(round(w / target_aspect)))
        if new_h >= h:
            return {"cropped": False, "reason": "target taller than source", "src_size": (w, h)}
        keep_top = int(round(lo * h))
        keep_bot = int(round(hi * h))
        keep_h = keep_bot - keep_top
        if keep_h > new_h:
            return {
                "cropped": False,
                "reason": "keep-band %dpx does not fit in %dpx window" % (keep_h, new_h),
                "src_size": (w, h),
                "keep_band": keep_band,
            }
        min_start = max(0, keep_bot - new_h)
        max_start = min(h - new_h, keep_top)
        if min_start > max_start:
            return {"cropped": False, "reason": "no window contains the keep-band",
                    "src_size": (w, h)}
        # Prefer cropping the backdrop (higher start = more taken from the top).
        start = max_start
        box = (0, start, w, start + new_h)
        out = im.crop(box)
    else:
        # Too wide: crop width, centered. The keep-band is vertical, so
        # a side crop does not cut it.
        new_w = max(1, int(round(h * target_aspect)))
        if new_w >= w:
            return {"cropped": False, "reason": "target wider than source", "src_size": (w, h)}
        left = (w - new_w) // 2
        box = (left, 0, left + new_w, h)
        out = im.crop(box)

    dest.parent.mkdir(parents=True, exist_ok=True)
    suffix = dest.suffix.lower()
    save_kw = {}
    if suffix in (".jpg", ".jpeg"):
        if out.mode != "RGB":
            out = out.convert("RGB")
        save_kw = {"quality": 92, "optimize": True}
    out.save(dest, **save_kw)
    return {
        "cropped": True,
        "reason": "ok",
        "box": box,
        "keep_band": keep_band,
        "src_size": (w, h),
        "out_size": out.size,
        "dest": str(dest),
    }


def original_and_dest(src_path):
    """Always crop from the uncropped original; write a *-fillcrop sibling."""
    src_path = Path(src_path)
    stem = src_path.stem
    if stem.endswith("-fillcrop"):
        stem = stem[: -len("-fillcrop")]
    original = src_path.with_name(stem + src_path.suffix)
    dest = src_path.with_name(stem + "-fillcrop" + src_path.suffix)
    return original, dest


def resolve_src(src, issue_dir):
    if not src:
        return None
    src = str(src).split("?", 1)[0]
    if src.startswith("file://"):
        path = Path(unquote(urlparse(src).path))
        return path if path.is_file() else None
    p = Path(src)
    if p.is_file():
        return p
    cand = Path(issue_dir) / src
    return cand if cand.is_file() else None


def summarize_gaps(inst):
    """Compact per-page / per-column gap list for reports and tests."""
    pages = []
    for pg in inst.get("pages") or []:
        rows = []
        for i, row in enumerate(pg.get("rows") or [], 1):
            rows.append({
                "row": i,
                "kind": row.get("kind"),
                "col_gaps_in": [round((g or 0) / 96.0, 2) for g in (row.get("col_gaps") or [])],
                "depths_in": [round((d or 0) / 96.0, 2) for d in (row.get("depths") or [])],
                "spread_in": round((row.get("spread") or 0) / 96.0, 2),
            })
        holes = []
        for h in pg.get("holes") or []:
            holes.append({
                "id": h.get("id"),
                "gap_in": round((h.get("gap") or 0) / 96.0, 2),
                "where": h.get("where"),
            })
        pages.append({
            "page": pg.get("page"),
            "footer_gaps_in": [round((g or 0) / 96.0, 2) for g in (pg.get("gaps") or [])],
            "footer_drop_in": round((pg.get("footer_drop") or 0) / 96.0, 2),
            "rows": rows,
            "holes": holes,
        })
    return pages


def leftover_flags(inst):
    """Human-readable leftover holes still over the threshold."""
    flags = []
    for pg in inst.get("pages") or []:
        pn = pg.get("page")
        for i, row in enumerate(pg.get("rows") or [], 1):
            for ci, g in enumerate(row.get("col_gaps") or [], 1):
                gap_in = (g or 0) / 96.0
                if round(gap_in, 2) > COL_GAP_FLAG_IN:
                    flags.append(
                        "page %s row %s (%s) column %s bottom gap %.2fin" % (
                            pn, i, row.get("kind") or "row", ci, gap_in)
                    )
        for h in pg.get("holes") or []:
            gap_in = (h.get("gap") or 0) / 96.0
            if round(gap_in, 2) > COL_GAP_FLAG_IN:
                flags.append(
                    "page %s float hole %.2fin %s (%s)" % (
                        pn, gap_in, h.get("where") or "", h.get("id") or "")
                )
    return flags


def _page_metrics(inst):
    """Per-page footer-drop, overflow, and footer-gap extremes, in inches / px."""
    out = []
    for pg in inst.get("pages") or []:
        gaps = [(g / 96.0) for g in (pg.get("gaps") or [])]
        out.append({
            "page": pg.get("page"),
            "drop": (pg.get("footer_drop") or 0) / 96.0,
            "overflow": (pg.get("overflow") or 0),
            "min_gap": min(gaps) if gaps else 0.0,
            "max_gap": max(gaps) if gaps else 0.0,
        })
    return out


def _page_ok(inst, before=None):
    """True if a layout is still printable.

    When ``before`` is given, only *regressions* fail: a page that was
    already short (a large footer gap) may still accept a move that
    closes an in-row hole without making the footer gap, pin, or
    overflow worse. A new footer overlap, a newly unpinned footer, or
    a newly overflowing page is always refused.
    """
    now = _page_metrics(inst)
    prev = {m["page"]: m for m in (_page_metrics(before) if before else [])}
    for m in now:
        was = prev.get(m["page"])
        if m["min_gap"] < -0.02:
            return False
        if m["overflow"] > 2 and (not was or m["overflow"] > was["overflow"] + 1):
            return False
        if abs(m["drop"]) > FOOTER_PIN_FLAG_IN:
            if not was or abs(m["drop"]) > abs(was["drop"]) + 0.03:
                return False
        # Footer-gap growth is allowed: shrinking a tall column to close an
        # in-row hole can move daylight down to the footer, and the fill
        # instrument will FLAG a footer gap over 0.75in. Reverting that
        # move would just put the hole back in the column. Still refuse a
        # new overlap, a newly hanging footer, or a newly overflowing page.
    return True


def _worst(inst):
    """The single worst in-row or float hole, or None if all are in budget."""
    worst = None
    for pg in inst.get("pages") or []:
        pn = pg.get("page")
        for ri, row in enumerate(pg.get("rows") or []):
            for ci, g in enumerate(row.get("col_gaps") or []):
                rec = {
                    "page": pn, "row": ri, "col": ci, "gap_in": g / 96.0,
                    "kind": row.get("kind") or "",
                    "where": "page %s row %s (%s) column %s" % (
                        pn, ri + 1, row.get("kind") or "row", ci + 1),
                }
                if worst is None or rec["gap_in"] > worst["gap_in"]:
                    worst = rec
        for hole in pg.get("holes") or []:
            rec = {
                "page": pn, "row": None, "col": None,
                "gap_in": (hole.get("gap") or 0) / 96.0,
                "kind": "float",
                "where": "page %s float hole %s (%s)" % (
                    pn, hole.get("where") or "", hole.get("id") or ""),
                "art_id": hole.get("id"),
            }
            if worst is None or rec["gap_in"] > worst["gap_in"]:
                worst = rec
    if worst and round(worst["gap_in"], 2) > COL_GAP_FLAG_IN:
        return worst
    return None


def _layout_page(layout, page_n):
    for p in (layout or {}).get("pages") or []:
        if p.get("page") == page_n:
            return p
    return None


def _snapshot(eval_js, call):
    return eval_js(call, "document.body.innerHTML")


def _restore(eval_js, call, html):
    eval_js(call, "document.body.innerHTML = " + json.dumps(html))


def _await_images(eval_js, call):
    """Wait for <img> decode so a just-written crop is in the layout."""
    eval_js(call, """
      Promise.all([...document.images].map(i =>
        (i.decode ? i.decode() : Promise.resolve()).catch(() => {})
      ))
    """, await_promise=True)


def _measure(eval_js, call, instrument_js):
    _await_images(eval_js, call)
    return json.loads(eval_js(call, instrument_js))


def _photos_in_column(layout_page, worst):
    """Photo items (not lettered comics) sitting in the tall side of the hole."""
    found = []
    if not layout_page:
        return found
    rows = layout_page.get("rows") or []
    if worst.get("row") is not None and worst["row"] < len(rows):
        cols = rows[worst["row"]].get("cols") or []
        if cols:
            tall = min(cols, key=lambda c: c.get("gap_in") or 0)
            for it in tall.get("items") or []:
                if it.get("photo") and not it.get("lettered") and it.get("art_id"):
                    found.append(it)
    if worst.get("art_id"):
        for row in rows:
            for col in row.get("cols") or []:
                for it in col.get("items") or []:
                    if it.get("art_id") == worst["art_id"]:
                        found.append(it)
    seen, out = set(), []
    for it in found:
        aid = it.get("art_id")
        if aid and aid not in seen:
            seen.add(aid)
            out.append(it)
    return out


def _all_photos_on_page(layout_page):
    out, seen = [], set()
    for row in (layout_page or {}).get("rows") or []:
        for col in row.get("cols") or []:
            for it in col.get("items") or []:
                if it.get("photo") and not it.get("lettered") and it.get("art_id"):
                    if it["art_id"] not in seen:
                        seen.add(it["art_id"])
                        out.append(it)
    return out


def _suggestions(inst):
    """Plain-words hints for each leftover hole. Report-only: nothing is moved."""
    out = []
    for pg in inst.get("pages") or []:
        pn = pg.get("page")
        for i, row in enumerate(pg.get("rows") or [], 1):
            for ci, g in enumerate(row.get("col_gaps") or [], 1):
                gap_in = (g or 0) / 96.0
                if round(gap_in, 2) > COL_GAP_FLAG_IN:
                    out.append(
                        "page %s row %s (%s) column %s is %.2fin short: grow the copy in that "
                        "column, scale its art, or try another arrangement (compose/arrange.py)"
                        % (pn, i, row.get("kind") or "row", ci, gap_in))
        for h in pg.get("holes") or []:
            gap_in = (h.get("gap") or 0) / 96.0
            if round(gap_in, 2) > COL_GAP_FLAG_IN:
                out.append("page %s %s hole %.2fin %s (%s): rescale the art or adjust the copy beside it"
                           % (pn, h.get("kind") or "float", gap_in, h.get("where") or "", h.get("id") or ""))
    return out


BALANCE_MODES = ("report", "pair")


def run_balance(call, flags, issue_dir, eval_js, instrument_js, fit_js, mode="report"):
    """Row-balance pass (Frank 2026-11-16 t229u: rein it in).

    ``mode="report"`` (default): measure and report holes with suggestions; the
    DOM is never touched. ``mode="pair"`` (opt-in, ``--balance=pair``): the only
    automatic change allowed is putting two stacked photos side by side in one
    row, kept only if total blank does not grow and the footer gap does not grow.

    Never: dissolve a row, move a box out of its row (stripping a neighbour),
    or crop/shrink a photo to push blank space somewhere else. Those were the
    v2 No. 7 failures (Opus review 2026-11-16).
    """
    if mode not in BALANCE_MODES:
        raise ValueError("balance mode must be one of %s" % (BALANCE_MODES,))
    issue_dir = Path(issue_dir)
    eval_js(call, fit_js)
    before = _measure(eval_js, call, instrument_js)
    actions = []

    if mode == "pair" and _worst(before):
        layout = eval_js(call, "window.__gzFit.listMovable()") or {"pages": []}
        worst = _worst(before)
        layout_page = _layout_page(layout, worst["page"])
        photos = _photos_in_column(layout_page, worst) or _all_photos_on_page(layout_page)
        if len(photos) >= 2:
            a, b = photos[0], photos[1]
            snap = _snapshot(eval_js, call)
            res = eval_js(call, "window.__gzFit.wrapInSplit(%s, [1, 1])" % json.dumps([a["id"], b["id"]]))
            inst2 = _measure(eval_js, call, instrument_js)
            new_worst = _worst(inst2)
            m0 = {m["page"]: m for m in _page_metrics(before)}
            footer_grew = any(m["max_gap"] > m0.get(m["page"], m)["max_gap"] + 0.05
                              for m in _page_metrics(inst2))
            improved = (new_worst is None) or (new_worst["gap_in"] < worst["gap_in"] - 0.04)
            if res and res.get("ok") and _page_ok(inst2, before=before) and improved and not footer_grew:
                rec = {"op": "pair", "items": [a["id"], b["id"]],
                       "why": "pair %s and %s in one row" % (a.get("art_id") or a["id"], b.get("art_id") or b["id"]),
                       "before_gap_in": round(worst["gap_in"], 2),
                       "after_gap_in": None if new_worst is None else round(new_worst["gap_in"], 2)}
                actions.append(rec)
                print("row-balance: %s" % rec["why"])
            else:
                _restore(eval_js, call, snap)

    after = _measure(eval_js, call, instrument_js) if actions else before
    leftovers = leftover_flags(after)
    suggestions = _suggestions(after)
    for line in suggestions:
        print("row-balance (report): %s" % line)
    if not leftovers:
        print("row-balance (report): no in-row holes over %.2fin" % COL_GAP_FLAG_IN)

    return {
        "mode": mode,
        "actions": actions,
        "before": summarize_gaps(before),
        "after": summarize_gaps(after),
        "leftovers": leftovers,
        "suggestions": suggestions,
        "threshold_in": COL_GAP_FLAG_IN,
    }


if __name__ == "__main__":
    raise SystemExit("balance.py is imported by render.py; it is not a CLI.")
