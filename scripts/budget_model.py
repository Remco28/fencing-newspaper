#!/usr/bin/env python3
"""The Budget page's capacity model in Python: the same arithmetic as costOf() in scripts/budget_page/core.js.

Used by build_budget_html.py (merging the fill calibration over lineup.capacity), by the calibration
script, and by tests that check the JS and Python sides agree. Units are column-inches: one column
(~2.42in wide) one inch deep. A block's cost includes the white space that separates it from the next.
"""
from __future__ import annotations

import json
from pathlib import Path

CALIBRATION = Path(__file__).resolve().parent / "budget_page" / "calibration.json"
DEFAULTS = {"photo_ceiling_in": 2.2, "full_width_in": 7.5, "oversupply": 1.15}


def load_calibration(path: Path = CALIBRATION) -> dict | None:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return doc if isinstance(doc, dict) and isinstance(doc.get("capacity"), dict) else None


def merged_capacity(lineup_capacity: dict, calibration: dict | None) -> dict:
    """lineup.capacity with the calibrated coefficients laid over it (numbers only; notes are kept)."""
    cap = {**DEFAULTS, **(lineup_capacity or {})}
    for k, v in ((calibration or {}).get("capacity") or {}).items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            cap[k] = v
    return cap


def cost_of(c: dict | None, cap: dict, item_words: int = 0) -> float:
    """Column-inches for one lineup slot `cost` ({type, span, words, rows, w, h, feature, head})."""
    if not c:
        return 0.0
    span = c.get("span") or 1
    words = c["words"] if isinstance(c.get("words"), (int, float)) else (item_words or 0)
    t = c.get("type")
    if t in ("prose", "qa"):
        f = bool(c.get("feature"))
        return words / (cap["wpi_feature"] if f else cap["wpi"]) + ((cap["head_feature"] if f else cap["head_short"]) + cap["gap"]) * span
    if t in ("table", "table_rows"):
        row = cap["row_full"] if span > 1 else cap["row_rail"]
        return (cap["table_head"] + (c.get("rows") or 0) * row + cap["gap"]) * span + (c.get("words") or 0) / cap["wpi"]
    if t == "figure":
        return figure_depth(c.get("w"), c.get("h"), span, cap) * span + (cap["caption_in"] if c.get("head") else 0) * span + cap["gap"] * span \
            + (c.get("words") or 0) / cap["wpi"] + (cap["head_short"] * span if c.get("head") else 0)
    return 0.0


def figure_depth(w, h, span: int, cap: dict) -> float:
    """Depth of a picture at its natural shape: one column is capped at the photo ceiling, wider art is not."""
    width = cap["col_width_in"] if span <= 1 else cap["span2_width_in"] if span == 2 else cap.get("full_width_in", 7.5)
    nat = width * (h or 1) / (w or 1)
    return min(nat, cap.get("photo_ceiling_in", 2.2)) if span <= 1 else nat


def photo_cost(w, h, span: int, cap: dict) -> float:
    """A loose photo (no story of its own): picture + caption + gap."""
    return (figure_depth(w, h, span, cap) + cap["caption_in"] + cap["gap"]) * span
