#!/usr/bin/env python3
"""Fit the budget page's capacity model to the composed issues and report estimated vs actual.

Input : calibration/measured.json (measure_issues.py, Chrome), archived lineups/submissions (read-only).
Output: scripts/budget_page/calibration.json  (coefficients the builder inlines over lineup.capacity)
        calibration/fit.json (every number in the report), and with --report the tables for calibration.md.
No Chrome needed here.  python3 calibration/calibrate_fill.py [--report] [--no-write]
"""
import argparse
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]  # repo root
sys.path.insert(0, str(REPO / "scripts"))
from budget_model import cost_of, merged_capacity, photo_cost  # noqa: E402  (the same model the page runs, in Python)

PAGE_W, GUT = 7.5, 0.125
r2 = lambda x: round(float(x), 2)  # noqa: E731


def span_of(w: float) -> float:
    """Width in columns, each column carrying its share of gutter (1 col = 1.0, 2 = 2.0, full = 3.0)."""
    return 3 * (w + GUT) / (PAGE_W + GUT)


def load_blocks(measured: dict) -> list[dict]:
    """One row per printed block; a page-1 lead that the HTML splits (h1 / photo / paragraphs) is re-joined."""
    out = []
    for iss in measured["issues"]:
        for pg in iss["pages"]:
            rows = []
            for b in pg["blocks"]:
                r = b["rect"]
                s = span_of(r["w"])
                rows.append({
                    "issue": iss["number"], "page": pg["page"], "label": b["label"], "cls": b["cls"], "x": r["x"], "y": r["y"], "w": r["w"], "h": r["h"],
                    "span": s, "colin": r["h"] * s, "words": b["bodyWords"] + b["capWords"], "bodyWords": b["bodyWords"], "capWords": b["capWords"],
                    "h1": any(h["tag"] == "h1" for h in b["heads"]), "heads": len(b["heads"]),
                    "rows": sum(t["rows"] - t["headRows"] for t in b["tables"]), "tables": len(b["tables"]),
                    "img_h": sum(i["h"] for i in b["imgs"]), "img_w": max([i["w"] for i in b["imgs"]] or [0]),
                    "nat": [(i["nw"], i["nh"]) for i in b["imgs"]],
                })
            # re-join "h1" + "p + p" runs of the same lead (No. 1, No. 4 put the photo between them)
            lead = next((x for x in rows if x["cls"].startswith("h1")), None)
            if lead:
                for x in list(rows):
                    if x is not lead and x["cls"].startswith("p") and abs(x["x"] - lead["x"]) < 0.1:
                        lead["colin"] += x["colin"]; lead["h"] += x["h"]; lead["words"] += x["words"]; lead["bodyWords"] += x["bodyWords"]
                        rows.remove(x)
            for x in rows:
                x["kind"] = "figure" if x["img_h"] else "table" if x["tables"] else "lead" if x["h1"] else "prose"
            out += rows
    return out


def lsq(rows, feats, target):
    A = np.array([[f(r) for f in feats] for r in rows], float)
    y = np.array([target(r) for r in rows], float)
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return [float(c) for c in coef]


SLICES = 30  # vertical slices across the page; each stands for 3/SLICES of a column


def columns(pg: dict):
    """Per page: body top/bottom and, for thin vertical slices across the page, the covered depth and block
    count. A slice in a gutter takes the blocks on either side (so a half-and-half row is not read as a hole)."""
    blocks = [b["rect"] for b in pg["blocks"]]
    top, bottom = min(b["y"] for b in blocks), pg["furn"]["footer"]["y"]
    cols = []
    for i in range(SLICES):
        cx = PAGE_W * (i + 0.5) / SLICES
        hit = [b for b in blocks if b["x"] <= cx <= b["x"] + b["w"]] or [b for b in blocks if b["x"] - 0.15 <= cx <= b["x"] + b["w"] + 0.15]
        spans, n = [], 0
        for b in sorted(hit, key=lambda b: b["y"]):
            if spans and b["y"] < spans[-1][1] - 0.01:
                spans[-1][1] = max(spans[-1][1], b["y"] + b["h"])
            else:
                spans.append([b["y"], b["y"] + b["h"]]); n += 1
        cols.append({"covered": sum(e - s0 for s0, e in spans), "n": n, "trail": bottom - max([e for _, e in spans] or [top]), "wt": 3 / SLICES})
    return top, bottom, cols


def fit(measured: dict, base_cap: dict) -> dict:
    B = load_blocks(measured)
    prose = [b for b in B if b["kind"] == "prose"]
    lead = [b for b in B if b["kind"] == "lead"]
    table = [b for b in B if b["kind"] == "table"]
    fig = [b for b in B if b["kind"] == "figure"]
    # prose: col-in = words / wpi + head_short * span
    a, head_short = lsq(prose, [lambda r: r["words"], lambda r: r["span"]], lambda r: r["colin"])
    wpi = 1 / a
    # lead: same idea with its own words-per-inch and headline depth (7 leads: fit the head, take wpi from the area)
    af, head_feature = lsq(lead, [lambda r: r["words"], lambda r: r["span"]], lambda r: r["colin"])
    if not (20 < 1 / af < 60) or not (0.2 < head_feature < 1.5):  # too few points for a 2-parameter fit: 1-parameter fallback
        af = 1 / wpi * 1.1
        head_feature = st.median((r["colin"] - r["words"] * af) / r["span"] for r in lead)
    # tables: col-in = span * (table_head + rows * row) + note words / wpi ; row by width class (rail <= 1.2 col, else wide)
    rail = lambda r: r["span"] <= 1.25  # noqa: E731
    th, row_rail, row_full = lsq(table, [lambda r: r["span"], lambda r: r["rows"] * r["span"] * rail(r), lambda r: r["rows"] * r["span"] * (not rail(r))],
                                 lambda r: r["colin"] - r["words"] / wpi)
    # figures: what the block adds around the picture (caption, credit, margins), per column of width
    pure = [r for r in fig if not r["heads"] and r["bodyWords"] == 0]
    cap1 = [r["h"] - r["img_h"] for r in pure if r["span"] <= 1.25 and r["capWords"]]
    cap2 = [r["h"] - r["img_h"] for r in pure if r["span"] > 1.25 and r["capWords"]]
    caption_in = st.median(cap1 + cap2) if cap1 + cap2 else base_cap.get("caption_in", 0.15)
    # white space between blocks: open depth per block in each column (median = the normal gap)
    per_col, caps = [], {1: [], 2: []}
    for iss in measured["issues"]:
        for pg in iss["pages"]:
            top, bottom, cols = columns(pg)
            caps[pg["page"]].append(3 * (bottom - top))
            per_col += [((bottom - top) - c["covered"]) / c["n"] for c in cols if c["n"]]
    gap = st.median(per_col)
    cal = {"page1_col_in": r2(st.median(caps[1])), "page2_col_in": r2(st.median(caps[2])), "wpi": r2(wpi), "wpi_feature": r2(1 / af),
           "head_short": r2(head_short), "head_feature": r2(head_feature), "gap": r2(gap), "table_head": r2(th), "row_rail": r2(row_rail),
           "row_full": r2(row_full), "caption_in": r2(caption_in), "full_width_in": PAGE_W}
    return {"capacity": cal, "n": {"prose": len(prose), "lead": len(lead), "table": len(table), "figure": len(fig), "columns": len(per_col)},
            "caption_1col": [r2(x) for x in cap1], "caption_wide": [r2(x) for x in cap2]}


def block_costs(b: dict, cap: dict) -> list[dict]:
    """The printed block expressed as lineup `cost` objects (what a perfectly informed budget would have said).
    A story with a picture inside it (a float, a Photo from History) is a picture plus prose."""
    span = max(1, min(3, round(b["span"])))
    if b["kind"] == "figure":
        nw, nh = b["nat"][0]
        img_span = max(1, min(3, round(span_of(b["img_w"]))))
        if b["heads"] or b["bodyWords"] or b["capWords"] > 40:
            return [{"type": "figure", "span": img_span, "w": nw, "h": nh, "head": False, "_nogap": True},
                    {"type": "prose", "span": span, "words": b["words"]}]
        return [{"type": "photo", "span": img_span, "w": nw, "h": nh}]
    if b["kind"] == "table":
        return [{"type": "table", "span": span, "rows": b["rows"], "words": b["words"]}]
    return [{"type": "prose", "span": span, "feature": b["kind"] == "lead", "words": b["words"]}]


def est_block(b: dict, cap: dict, gaps: bool) -> float:
    total = 0.0
    for c in block_costs(b, cap):
        v = photo_cost(c["w"], c["h"], c["span"], cap) if c["type"] == "photo" else cost_of(c, cap)
        total += v - (cap["gap"] * c["span"] if (not gaps or c.get("_nogap")) else 0)
    return total


def evaluate(measured: dict, cap: dict) -> dict:
    """Estimated vs actual, per block and per page, for one set of coefficients."""
    B = load_blocks(measured)
    out = {"blocks": [], "pages": []}
    for b in B:
        est = est_block(b, cap, gaps=False)  # the block itself; gaps are scored at page level
        out["blocks"].append({"issue": b["issue"], "page": b["page"], "label": b["label"], "kind": b["kind"], "span": r2(b["span"]),
                              "words": int(b["words"]), "rows": b["rows"], "actual": r2(b["colin"]), "est": r2(est), "err": r2(est - b["colin"])})
    for iss in measured["issues"]:
        for pg in iss["pages"]:
            top, bottom, cols = columns(pg)
            mine = [x for x in B if x["issue"] == iss["number"] and x["page"] == pg["page"]]
            depth = 3 * (bottom - top)
            est_used = sum(est_block(b, cap, gaps=True) for b in mine)
            used = sum(b["colin"] for b in mine)
            normal = sum(cap["gap"] * c["n"] * c["wt"] for c in cols)
            hole = sum(((bottom - top) - c["covered"]) * c["wt"] for c in cols) - normal  # open space beyond the normal gaps
            model_depth = cap["page1_col_in"] if pg["page"] == 1 else cap["page2_col_in"]
            ins = iss.get("instruments") or {}
            out["pages"].append({"issue": iss["number"], "page": pg["page"], "depth_est": r2(model_depth), "depth": r2(depth),
                                 "used_est": r2(est_used), "used": r2(used + normal), "hole_est": r2(model_depth - est_used), "hole": r2(hole),
                                 "err": r2((model_depth - est_used) - hole), "trail": [r2(st.mean(c["trail"] for c in cols[k * SLICES // 3:(k + 1) * SLICES // 3])) for k in range(3)],
                                 "instrument_gap_in": ins.get(f"p{pg['page']}_gap_in"), "blocks": len(mine)})
    return out


def summarise(ev: dict) -> dict:
    be = [b["err"] for b in ev["blocks"]]
    pe = [p["err"] for p in ev["pages"]]
    rel = [abs(b["err"]) / b["actual"] for b in ev["blocks"] if b["actual"] > 0.5]
    return {"block_mae": r2(st.mean(map(abs, be))), "block_bias": r2(st.mean(be)), "block_median_abs_pct": round(100 * st.median(rel)),
            "page_mae": r2(st.mean(map(abs, pe))), "page_bias": r2(st.mean(pe)), "page_max": r2(max(map(abs, pe))),
            "issue_mae": r2(st.mean(abs(sum(p["err"] for p in ev["pages"] if p["issue"] == n)) for n in sorted({p["issue"] for p in ev["pages"]})))}


def budget_time(measured: dict, base_cap: dict, cal_cap: dict) -> list[dict]:
    """What the budget page would have shown when Frank filed (archived lineup + his included slots) vs what printed."""
    rows = []
    for iss in measured["issues"]:
        n, date = iss["number"], iss["date"]
        lp = REPO / "budget-demo" / "archive" / f"practice-lineup-issue{n}-{date}.json"
        sp = REPO / "issues" / date / "budget-submission.json"
        if not lp.is_file() or not sp.is_file():
            continue
        lineup, sub = json.loads(lp.read_text(encoding="utf-8")), json.loads(sp.read_text(encoding="utf-8"))
        items = {}
        ip = REPO / "staging" / "weeks" / date / "items.json"
        if ip.is_file():
            items = {i.get("id"): i for i in json.loads(ip.read_text(encoding="utf-8")).get("items", []) if isinstance(i, dict)}
        slots = {s.get("key"): s for s in (lineup.get("slots") or lineup.get("lineup") or []) if isinstance(s, dict)}
        inc = [e.get("slot") for e in sub.get("includedSlots") or []]
        known = [slots[k] for k in inc if k in slots and slots[k].get("cost")]

        def words(s):
            it = items.get(s.get("item")) or {}
            return it.get("word_count") or len(str(it.get("body") or "").split())
        old_cap = {**base_cap, **(lineup.get("capacity") or {})}
        new_cap = merged_capacity(lineup.get("capacity") or {}, {"capacity": cal_cap})
        est_old = sum(cost_of(s["cost"], old_cap, words(s)) for s in known)
        est_new = sum(cost_of(s["cost"], new_cap, words(s)) for s in known)
        ev_pages = [p for p in measured_eval["pages"] if p["issue"] == n]
        printed_blocks = sum(p["blocks"] for p in ev_pages)
        total_new = new_cap["page1_col_in"] + new_cap["page2_col_in"]
        total_old = old_cap["page1_col_in"] + old_cap["page2_col_in"]
        rows.append({"issue": n, "included": len(inc), "costed": len(known), "printed_blocks": printed_blocks,
                     "old_est": r2(est_old), "old_pct": round(100 * est_old / total_old), "new_est": r2(est_new), "new_pct": round(100 * est_new / total_new),
                     "hole_at_budget": r2(total_new - est_new), "printed_used": r2(sum(p["used"] for p in ev_pages)),
                     "printed_hole": r2(sum(p["hole"] for p in ev_pages)),
                     "budget_words": int(sum((s["cost"].get("words") or words(s) or 0) for s in known if s["cost"].get("type") in ("prose", "figure"))),
                     "printed_words": int(sum(b["words"] for b in measured_eval["blocks"] if b["issue"] == n))})
    return rows


measured_eval: dict = {}


def main() -> None:
    global measured_eval
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--report", action="store_true", help="print the markdown tables used in calibration.md")
    args = ap.parse_args()
    measured = json.loads((HERE / "measured.json").read_text(encoding="utf-8"))
    base = json.loads((REPO / "budget-demo" / "practice-lineup.json").read_text(encoding="utf-8"))["capacity"]
    f = fit(measured, base)
    cal = merged_capacity(base, {"capacity": f["capacity"]})
    before, after = evaluate(measured, merged_capacity(base, None)), evaluate(measured, cal)
    measured_eval = after
    bt = budget_time(measured, base, f["capacity"])
    doc = {"_about": "Fill calibration for the Budget page. GENERATED by reviews/fable-budget-paper-2026-11-16/calibration/calibrate_fill.py "
                     "from Chrome measurements of the composed issues Nos. 1-7. build_budget_html.py lays 'capacity' over lineup.capacity. "
                     "Delete this file to fall back to the lineup's own numbers.",
           "fitted_on": [f"No. {i['number']} ({i['date']})" for i in measured["issues"]],
           "capacity": f["capacity"], "replaces": {k: base.get(k) for k in f["capacity"]},
           "residual": {"before": summarise(before), "after": summarise(after), "unit": "column-inches"}}
    (HERE / "fit.json").write_text(json.dumps({"fit": f, "before": before, "after": after, "budget_time": bt, "summary": doc["residual"]}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if not args.no_write:
        (REPO / "scripts" / "budget_page" / "calibration.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("fitted:", json.dumps(f["capacity"]))
    print("was   :", json.dumps(doc["replaces"]))
    print("n     :", f["n"], "caption 1col", f["caption_1col"], "wide", f["caption_wide"])
    print("before:", summarise(before))
    print("after :", summarise(after))
    if args.report:
        print("\n| No. | page | depth est / actual | used est / actual | hole est / actual | error | desk instrument gap |\n|---|---|---|---|---|---|---|")
        for p, q in zip(after["pages"], before["pages"]):
            print(f"| {p['issue']} | {p['page']} | {p['depth_est']} / {p['depth']} | {p['used_est']} / {p['used']} | {p['hole_est']} / {p['hole']} | {p['err']:+.2f} (was {q['err']:+.2f}) | {p['instrument_gap_in'] if p['instrument_gap_in'] is not None else '—'} |")
        print("\n| No. | p | block | kind | cols | words/rows | actual | est | error | old est |\n|---|---|---|---|---|---|---|---|---|---|")
        for b, o in zip(after["blocks"], before["blocks"]):
            print(f"| {b['issue']} | {b['page']} | {b['label'][:38]} | {b['kind']} | {b['span']} | {b['words']}w{' / ' + str(b['rows']) + 'r' if b['rows'] else ''} | {b['actual']} | {b['est']} | {b['err']:+.2f} | {o['est']} |")
        print("\n| No. | slots in / costed | printed blocks | budget-time est (old model) | budget-time est (calibrated) | hole shown at budget | printed used | printed hole | words budgeted → printed |\n|---|---|---|---|---|---|---|---|---|")
        for r in bt:
            print(f"| {r['issue']} | {r['included']} / {r['costed']} | {r['printed_blocks']} | {r['old_est']} ({r['old_pct']}%) | {r['new_est']} ({r['new_pct']}%) | {r['hole_at_budget']} | {r['printed_used']} | {r['printed_hole']} | {r['budget_words']} → {r['printed_words']} |")


if __name__ == "__main__":
    main()
