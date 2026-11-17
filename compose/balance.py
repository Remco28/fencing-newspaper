#!/usr/bin/env python3
"""Row-balance pass for Template A (STYLE-GUIDE §13, §19).

After art-fit, this pass evens out short columns in every row band so the
fill instrument's per-column bottom-gap check can pass. It is general
composer/fit behavior, not a one-issue layout.

What it may do, looping until every column/float hole is at most
COL_GAP_FLAG_IN or no safe move remains:

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


def _pick_move(layout_page, worst):
    """Choose a short movable item and the shorter destination column.

    Prefers a short box inside an uneven nested split on the same page,
    then the smallest movable item in the tall column of the worst row.
    Destination is the short column of the worst row (typically the rail).
    """
    if not layout_page or worst.get("row") is None:
        return None
    rows = layout_page.get("rows") or []
    ri = worst["row"]
    if ri >= len(rows):
        return None
    row = rows[ri]
    cols = row.get("cols") or []
    if len(cols) < 2:
        return None
    dest = max(cols, key=lambda c: c.get("gap_in") or 0)
    tall = min(cols, key=lambda c: c.get("gap_in") or 0)
    if dest.get("id") == tall.get("id"):
        return None
    dest_gap = dest.get("gap_in") or 0
    dest_item_ids = {it["id"] for it in (dest.get("items") or [])}

    cands = []
    # Nested uneven splits: a short box in a short half is the first thing
    # to move into this row's short rail (Ratings Earned → the page rail).
    for rj, nrow in enumerate(rows):
        if rj == ri:
            continue
        ncols = nrow.get("cols") or []
        if len(ncols) < 2:
            continue
        short_n = max(ncols, key=lambda c: c.get("gap_in") or 0)
        for it in short_n.get("items") or []:
            if it.get("movable") and it.get("kind") in ("box", "short"):
                cands.append((it, short_n, True))
    for it in tall.get("items") or []:
        if it.get("movable"):
            cands.append((it, tall, False))

    filtered = []
    for it, col, nested in cands:
        if not it.get("id") or it["id"] in dest_item_ids:
            continue
        if col.get("id") == dest.get("id"):
            continue
        filtered.append((it, col, nested))
    if not filtered:
        return None

    def score(entry):
        it, col, nested = entry
        h = it.get("h_in") or 0
        kind_rank = 0 if it.get("kind") == "box" else (1 if it.get("kind") == "short" else 2)
        fits = 0 if h <= dest_gap + 0.20 else 1
        nest_rank = 0 if nested else 1
        return (nest_rank, kind_rank, fits, h)

    filtered.sort(key=score)
    it, col, nested = filtered[0]
    return {
        "item": it["id"],
        "label": it.get("label") or it["id"],
        "dest": dest["id"],
        "from": col.get("id"),
        "why": "move %r into the shorter column (hole %.2fin)" % (
            it.get("label") or it["id"], dest_gap),
    }


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


def run_balance(call, flags, issue_dir, eval_js, instrument_js, fit_js):
    """One Chrome-session balance pass. Returns a report dict."""
    issue_dir = Path(issue_dir)
    eval_js(call, fit_js)
    before = _measure(eval_js, call, instrument_js)
    actions = []

    def attempt(action_fn):
        """Run action_fn. Commit only if the page stays printable and the worst hole shrinks."""
        inst = _measure(eval_js, call, instrument_js)
        worst = _worst(inst)
        if not worst:
            return None
        snap = _snapshot(eval_js, call)
        result = action_fn()
        if not result or not result.get("ok"):
            _restore(eval_js, call, snap)
            return None
        inst2 = _measure(eval_js, call, instrument_js)
        ok = _page_ok(inst2, before=inst)
        new_worst = _worst(inst2)
        improved = (new_worst is None) or (new_worst["gap_in"] < worst["gap_in"] - 0.04)
        if not ok:
            _restore(eval_js, call, snap)
            return None
        if not improved:
            _restore(eval_js, call, snap)
            return None
        result["before_gap_in"] = round(worst["gap_in"], 2)
        result["after_gap_in"] = None if new_worst is None else round(new_worst["gap_in"], 2)
        result["where"] = worst["where"]
        return result

    for _pass in range(MAX_PASSES):
        inst = _measure(eval_js, call, instrument_js)
        worst = _worst(inst)
        if not worst:
            break
        layout = eval_js(call, "window.__gzFit.listMovable()") or {"pages": []}
        layout_page = _layout_page(layout, worst["page"])

        # 1. Move a short box / short into the shorter column.
        move = _pick_move(layout_page, worst)
        if move:
            def do_move(m=move):
                # Move only. Pairing photos is a later, separate attempt so a
                # useful move is not reverted when the pair would overflow.
                return eval_js(
                    call,
                    "window.__gzFit.moveItem(%s, %s)" % (
                        json.dumps(m["item"]), json.dumps(m["dest"])),
                )
            result = attempt(do_move)
            if result:
                rec = {
                    "op": "move",
                    "item": move["item"],
                    "label": move["label"],
                    "dest": move["dest"],
                    "why": move["why"],
                    "before_gap_in": result["before_gap_in"],
                    "after_gap_in": result["after_gap_in"],
                }
                actions.append(rec)
                print("row-balance: %s" % move["why"])
                continue

        # 2. Pair two photos in the tall column so they share a row.
        photos = _photos_in_column(layout_page, worst)
        if len(photos) < 2:
            # A float in the lead plus a stacked portrait in the same span
            # should still pair — look at every photo on the page's tall side
            # plus other photos on the same page in the same parent column.
            photos = _all_photos_on_page(layout_page)
        if len(photos) >= 2:
            a, b = photos[0], photos[1]
            def do_pair(ids=None):
                ids = ids or [a["id"], b["id"]]
                return eval_js(
                    call,
                    "window.__gzFit.wrapInSplit(%s, [1, 1])" % json.dumps(ids),
                )
            result = attempt(do_pair)
            if result:
                rec = {
                    "op": "pair",
                    "items": [a["id"], b["id"]],
                    "labels": [a.get("art_id") or a.get("label"),
                               b.get("art_id") or b.get("label")],
                    "why": "pair %s and %s in one row" % (
                        a.get("art_id") or a["id"], b.get("art_id") or b["id"]),
                    "before_gap_in": result["before_gap_in"],
                    "after_gap_in": result["after_gap_in"],
                }
                actions.append(rec)
                print("row-balance: %s" % rec["why"])
                continue

        # 3. Face-safe backdrop crop / scale of a photo in the tall column.
        crop_targets = _photos_in_column(layout_page, worst) or _all_photos_on_page(layout_page)
        cropped_any = False
        for it in crop_targets:
            aid = it.get("art_id")
            src = resolve_src(it.get("src"), issue_dir)
            if not aid or src is None:
                continue
            current_h = it.get("h_in") or 0
            # Figure height includes caption/credit; use a conservative trim.
            # We ask the image itself to lose enough to close the hole, but
            # never go under PHOTO_CROP_MIN_H_IN or over the ceiling already.
            needed = worst["gap_in"] - (COL_GAP_FLAG_IN - 0.05)
            if needed <= 0.05:
                break
            # Estimate printed image height as ~85% of the figure (caption/credit).
            img_h = max(current_h * 0.85, current_h - 0.45)
            img_w = None
            # We don't have printed width on the item; infer from height and
            # the file's aspect, then aim at a shorter printed height.
            try:
                from PIL import Image as _Im
                with _Im.open(src) as _im:
                    pw, ph = _im.size
                if ph:
                    img_w = img_h * (pw / ph)
            except Exception:
                img_w = None
            if not img_w or img_w <= 0:
                continue
            target_h = max(PHOTO_CROP_MIN_H_IN, min(PHOTO_CEILING_IN, img_h - needed))
            if target_h >= img_h - 0.05:
                # Not enough room to shrink this photo; try the next.
                continue
            target_aspect = img_w / target_h
            original, dest = original_and_dest(src)
            if not original.is_file():
                continue
            # Never write a crop into an APPROVED / published issue folder.
            if frozen_output_path(str(dest)):
                continue

            def do_crop(aid=aid, original=original, dest=dest, target_aspect=target_aspect):
                info = safe_cover_crop(original, dest, target_aspect)
                if not info.get("cropped"):
                    return {"ok": False, "reason": info.get("reason")}
                # New file is in the issue folder; use a path relative to the HTML.
                try:
                    rel = dest.resolve().relative_to(issue_dir.resolve())
                except ValueError:
                    rel = dest.name
                # Cache-bust in case a prior crop used the same name.
                src_rel = str(rel) + "?v=fillcrop"
                ret = eval_js(
                    call,
                    "window.__gzFit.setArtSrc(%s, %s, %s)" % (
                        json.dumps(aid), json.dumps(src_rel), json.dumps(CREDIT_CROPPED)),
                )
                if ret and ret.get("ok"):
                    ret["crop"] = {k: info[k] for k in info if k != "dest"}
                    ret["dest"] = str(dest)
                return ret or {"ok": False}

            result = attempt(do_crop)
            if result:
                rec = {
                    "op": "crop",
                    "id": aid,
                    "dest": str(dest),
                    "why": "face-safe backdrop crop of %s (%.2fin → ~%.2fin)" % (
                        aid, img_h, target_h),
                    "before_gap_in": result["before_gap_in"],
                    "after_gap_in": result["after_gap_in"],
                    "keep_band": list(DEFAULT_KEEP_BAND),
                }
                actions.append(rec)
                print("row-balance: %s" % rec["why"])
                cropped_any = True
                break
        if cropped_any:
            continue

        # 4. Float a leftover narrow photo up into the lead so it sits
        # beside wrapping text instead of leaving a side gutter under the
        # lead in a wide column.
        photos = _photos_in_column(layout_page, worst) or _all_photos_on_page(layout_page)
        floated = False
        for it in photos:
            aid = it.get("art_id")
            if not aid or it.get("lettered"):
                continue
            # Already a float inside the lead: skip.
            # We still try a stacked sibling photo that sits below the lead.
            def do_float(aid=aid, width=it.get("w_in") or None):
                w = width
                return eval_js(
                    call,
                    "window.__gzFit.floatIntoLead(%s, %s)" % (
                        json.dumps(aid), "null" if not w else json.dumps(round(w, 4))),
                )
            result = attempt(do_float)
            if result:
                rec = {
                    "op": "float",
                    "id": aid,
                    "why": "float %s into the lead to close a side gutter" % aid,
                    "before_gap_in": result["before_gap_in"],
                    "after_gap_in": result["after_gap_in"],
                }
                actions.append(rec)
                print("row-balance: %s" % rec["why"])
                floated = True
                break
        if floated:
            continue

        # Nothing safe left to do for this hole.
        break

    after = _measure(eval_js, call, instrument_js)
    leftovers = leftover_flags(after)
    if leftovers:
        for line in leftovers:
            print("row-balance leftover: %s" % line)
    elif actions:
        print("row-balance: all in-row column and float holes <= %.2fin" % COL_GAP_FLAG_IN)
    else:
        print("row-balance: no moves needed (or no safe move remained)")

    return {
        "actions": actions,
        "before": summarize_gaps(before),
        "after": summarize_gaps(after),
        "leftovers": leftovers,
        "threshold_in": COL_GAP_FLAG_IN,
    }


if __name__ == "__main__":
    raise SystemExit("balance.py is imported by render.py; it is not a CLI.")
