#!/usr/bin/env python3
"""The eye check: every proof is looked at before it goes to Frank (Frank t229u, 2026-11-16).

    python3 compose/eyecheck.py <proof.pdf> --report=<fit-report.json>      # check
    python3 compose/eyecheck.py --verify <proof.pdf>                         # gate before sending

A proof is sendable only when `--verify` exits 0: eye-check.json beside the PDF has
verdict PASS (or a recorded waiver from Frank) for this exact PDF (sha256).

What it does
 1. Renders 200 dpi previews of the PDF (preview-p1.png, preview-p2.png beside it).
 2. Pixel blank map: the largest blank rectangles on each page, with pictures masked out
    (a photo's white backdrop is not a hole). Rule: no blank area over HOLE_MAX_SQ_IN
    anywhere, except the band right above the footer, which may be BOTTOM_BAND_MAX_IN tall.
 3. Reads the fill instrument (render.py --report): every FLAG, the inter-block gaps
    against the --gap-block token, and the page's body-copy density.
 4. Length targets: turns blank area into "page N needs ~W words" (and overset into
    "cut ~W words"), naming where the hole is, so the editor can grow or trim a story
    with vetted copy (gazette.copy_length). Never pad with unvetted facts.
 5. Vision critique by a DIFFERENT model from the composer (default: Claude Code
    `sonnet`; override with --model= or GAZETTE_EYE_MODEL). It sees the proof pages and
    No. 6's approved pages as the reference, and grades the rubric below.
 6. Writes eye-check.json and eye-check.md beside the PDF. The composer (Clark) still
    opens the previews himself; this does not replace that.

Verdict: PASS only if the vision critique passes AND no pixel hole breaks the rule AND the
instrument has no FLAG. Otherwise FAIL with the reasons and the suggested fixes.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

COMPOSE = Path(__file__).resolve().parent
ROOT = COMPOSE.parent
sys.path.insert(0, str(COMPOSE))

HOLE_MAX_SQ_IN = 1.5
HOLE_RULE_MIN_H_IN = 0.75   # shorter blanks are ragged lines / headline ends: reported, judged by eye
BOTTOM_BAND_MAX_IN = 0.5
HOLE_MIN_W_IN, HOLE_MIN_H_IN = 0.6, 0.4
CONTENT = (0.5, 0.5, 8.0, 10.6)        # x0, y0, x1, y1 in inches on the Letter page
FOOTER_BAND_IN = 0.2                   # the footer line itself, not counted
DEFAULT_DENSITY = 16.0                 # words per sq in of 8.5pt body (≈40 words per column-inch)
REFERENCE = ROOT / "issues" / "2026-11-11"   # No. 6, approved by Frank (proof v3, Nov. 10)
DEFAULT_MODEL = os.environ.get("GAZETTE_EYE_MODEL", "sonnet")
CLAUDE = os.environ.get("GAZETTE_CLAUDE", shutil.which("claude") or str(Path.home() / ".local/bin/claude"))

RUBRIC = """\
You are the picture editor and page designer checking a proof of a 2-page club newsletter
(US Letter, black and white) before it goes to the owner. Judge it like a human newspaper
editor with a good eye. Compare against the REFERENCE pages, which the owner approved.

Rubric (each item PASS or FAIL, with where and why):
 1. blank_space  - no blank area bigger than about 1.5 square inches anywhere on the page
                   (beside a photo, under a story, inside a box, mid-page); the band right
                   above the footer may be at most about 0.5in tall.
 2. even_gaps    - the vertical gaps between stacked blocks (stories, boxes, pictures) look
                   the same everywhere; nothing touches; nothing has a visibly bigger gap.
 3. no_widows    - no one-word or very short last line stranded at the top of a column or
                   box; no one-line paragraph left alone; no table cell wrapping into a
                   tall sliver (e.g. a 'Where' column wrapping into 4 lines).
 4. photo_sizing - photos and art are sized for their role (a lead photo reads as the lead;
                   nothing is so small it looks like an afterthought); lettered cartoons
                   stay readable.
 5. focal_point  - page 1 has one clear focal point (the lead and its art).
 6. alignment    - column bottoms and side-by-side blocks line up; rules and borders are
                   consistent; nothing looks accidental.
Calibration: the REFERENCE pages were approved by the owner, so anything they also do is
acceptable (for example a ~0.4in band above the footer, a box with a few short rows). The
measured sizes below (footer gaps, inter-block gaps) come from the layout engine and are
exact: use them instead of estimating sizes from the image, and judge how the page LOOKS.
The white space after a headline or a paragraph's last line is normal ragged-right type,
not a hole.
Grade every issue's severity:
  "major" - a reader would notice it as a mistake: a visible hole (rule 1), blocks touching
            or a clearly bigger gap, a widow stranded at the top of a column or box, a table
            cell wrapping into a sliver, a photo too small for its role or unreadable
            lettering, no focal point, overset or clipped text.
  "minor" - polish an editor might do with time (a short last line at a paragraph end,
            a one-row table, header alignment conventions, a slightly thin story).
Overall verdict: PASS if there are no "major" issues (minor ones are listed for the editor),
FAIL if there is at least one "major" issue. A rubric item fails only for a major issue.
For each FAIL, suggest the editor's fix, preferring CONTENT changes (grow or trim a named
story by ~N words, scale a picture up or down, choose another arrangement) over nudging.

Reply with ONLY one JSON object, no prose before or after, in this shape:
{"verdict": "PASS"|"FAIL",
 "rubric": {"blank_space": {"pass": true|false, "notes": "..."}, "even_gaps": {...},
            "no_widows": {...}, "photo_sizing": {...}, "focal_point": {...}, "alignment": {...}},
 "issues": [{"page": 1, "severity": "major"|"minor", "where": "...", "problem": "...", "fix": "..."}],
 "summary": "one or two sentences"}
"""


# ----------------------------------------------------------------- helpers

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def result_paths(pdf):
    pdf = Path(pdf)
    return pdf.parent / "eye-check.json", pdf.parent / "eye-check.md"


def render_previews(pdf, out_dir, dpi=200):
    """pdftoppm the PDF; return [page1.png, page2.png, ...] named preview-pN.png in out_dir."""
    out_dir = Path(out_dir)
    tmp = Path(tempfile.mkdtemp(prefix="gz-eye-"))
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(tmp / "p")], check=True)
    pages = sorted(tmp.glob("p-*.png"), key=lambda p: int(re.search(r"-(\d+)\.png$", p.name).group(1)))
    out = []
    for i, src in enumerate(pages, 1):
        dest = out_dir / f"preview-p{i}.png"
        shutil.move(str(src), dest)
        out.append(dest)
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def _max_rect(empty):
    import numpy as np
    h, w = empty.shape
    heights = np.zeros(w, dtype=int)
    best = (0, None)
    for y in range(h):
        heights = np.where(empty[y], heights + 1, 0)
        stack = []
        for x in range(w + 1):
            cur = heights[x] if x < w else 0
            start = x
            while stack and stack[-1][1] >= cur:
                sx, sh = stack.pop()
                area = sh * (x - sx)
                if area > best[0]:
                    best = (area, (sx, y - sh + 1, x, y + 1))
                start = sx
            stack.append((start, cur))
    return best


def blank_map(png, img_rects=(), n=6, s=50):
    """Largest blank rectangles (what the eye sees as holes) on one page PNG.

    img_rects are picture boxes in inches from the content-box top-left; they count as ink.
    Returns dicts with w_in, h_in, sq_in, x_in, y_in (page coordinates), bottom_band."""
    import numpy as np
    from PIL import Image
    im = Image.open(png).convert("L").resize((int(8.5 * s), int(11 * s)))
    a = np.asarray(im)
    x0, y0, x1, y1 = (int(v * s) for v in CONTENT)
    a = a[y0:y1, x0:x1]
    empty = a > 200
    for (rx, ry, rw, rh) in img_rects or ():
        empty[max(0, int(ry * s) - 1):int((ry + rh) * s) + 2, max(0, int(rx * s) - 1):int((rx + rw) * s) + 2] = False
    empty = empty[: -int(FOOTER_BAND_IN * s)]
    H = empty.shape[0]
    out = []
    for _ in range(n * 3):
        area, r = _max_rect(empty)
        if not r:
            break
        x, y, xe, ye = r
        wi, hi = (xe - x) / s, (ye - y) / s
        empty[y:ye, x:xe] = False
        if wi < HOLE_MIN_W_IN or hi < HOLE_MIN_H_IN:
            continue
        bottom = (H - ye) <= int(0.12 * s) and wi >= 5.0
        out.append({"w_in": round(wi, 2), "h_in": round(hi, 2), "sq_in": round(wi * hi, 2),
                    "x_in": round(x / s + CONTENT[0], 2), "y_in": round(y / s + CONTENT[1], 2),
                    "bottom_band": bool(bottom)})
        if len(out) >= n:
            break
    return out


def hole_breaks_rule(h):
    if h["bottom_band"]:
        return h["h_in"] > BOTTOM_BAND_MAX_IN + 0.02
    return h["sq_in"] > HOLE_MAX_SQ_IN and h["h_in"] >= HOLE_RULE_MIN_H_IN


def where_words(h):
    x_mid = h["x_in"] + h["w_in"] / 2
    side = "left" if x_mid < 3.2 else ("right" if x_mid > 5.6 else "middle")
    if h["bottom_band"]:
        return "above the footer, full width"
    return f"{side}, {h['y_in']:.1f}-{h['y_in'] + h['h_in']:.1f}in from the top"


def length_targets(pages_holes, instrument):
    """Words to add (or cut) per page, from blank area × the page's measured copy density."""
    out = []
    ipages = {p.get("page"): p for p in (instrument or {}).get("pages") or []}
    for pn, holes in pages_holes.items():
        ip = ipages.get(pn) or {}
        dens = ip.get("words_per_sq_in") or DEFAULT_DENSITY
        overflow_px = max(0.0, float(ip.get("overflow") or 0))
        gaps = ip.get("gaps") or [0]
        if overflow_px > 2 or min(gaps) < -2:
            over_in = max(overflow_px, -min(gaps)) / 96.0
            out.append({"page": pn, "action": "cut", "words": int(round(over_in * 7.5 * dens / 5.0) * 5),
                        "where": "page is overset", "density": dens})
            continue
        # Rule breakers, plus any blank at least half the rule's height and 1 sq in: shorter
        # blanks are a headline's or last line's ragged end, not missing copy.
        bad = [h for h in holes if hole_breaks_rule(h)
               or (h["sq_in"] >= 1.0 and h["h_in"] >= HOLE_RULE_MIN_H_IN / 1.5 and not h["bottom_band"])]
        if not bad:
            continue
        sq = sum(h["sq_in"] for h in bad)
        out.append({"page": pn, "action": "add", "words": int(round(sq * dens / 5.0) * 5),
                    "where": "; ".join(f"{h['w_in']}x{h['h_in']}in {where_words(h)}" for h in bad),
                    "density": dens})
    return out


def instrument_flags(instrument):
    import render as R
    buf = io.StringIO()
    with redirect_stdout(buf):
        flags = R.report(instrument)
    return flags, buf.getvalue()


def vision_critique(previews, ref_pngs, numbers, model=DEFAULT_MODEL, timeout=900):
    """Ask a different model to look at the pages. Returns (parsed_json_or_None, meta)."""
    work = Path(tempfile.mkdtemp(prefix="gz-eye-vision-"))
    names = []
    for i, p in enumerate(previews, 1):
        d = work / f"proof-page{i}.png"; shutil.copy(p, d); names.append(d.name)
    refs = []
    for i, p in enumerate(ref_pngs, 1):
        d = work / f"reference-approved-page{i}.png"; shutil.copy(p, d); refs.append(d.name)
    prompt = (RUBRIC + "\nFiles in the current directory (open each with the Read tool and look at it):\n"
              + "".join(f"  PROOF  {n}\n" for n in names)
              + "".join(f"  REFERENCE (approved) {n}\n" for n in refs)
              + "\nMeasured numbers from the layout instrument and pixel blank map (trust your eyes "
              "over these if they disagree, and say so):\n" + json.dumps(numbers, indent=1)[:6000])
    cmd = [CLAUDE, "-p", prompt, "--model", model, "--output-format", "json",
           "--allowedTools", "Read", "--disallowedTools", "Bash", "Write", "Edit", "WebFetch", "WebSearch",
           "--max-budget-usd", "3"]
    meta = {"model_alias": model, "cmd": "claude -p --model %s (Read only)" % model}
    try:
        r = subprocess.run(cmd, cwd=str(work), capture_output=True, text=True, timeout=timeout)
    except Exception as e:  # noqa: BLE001
        meta["error"] = str(e)
        return None, meta
    finally:
        pass
    meta["returncode"] = r.returncode
    try:
        env = json.loads(r.stdout)
    except Exception:
        meta["error"] = (r.stderr or r.stdout)[-800:]
        return None, meta
    meta["cost_usd"] = env.get("total_cost_usd")
    meta["num_turns"] = env.get("num_turns")
    mu = env.get("modelUsage") or {}
    if mu:
        meta["model"] = ",".join(mu.keys())
    text = env.get("result") or ""
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        meta["error"] = "no JSON in reply: " + text[-500:]
        return None, meta
    try:
        parsed = json.loads(m.group(0))
    except Exception as e:  # noqa: BLE001
        meta["error"] = f"bad JSON ({e}): " + text[-500:]
        return None, meta
    shutil.rmtree(work, ignore_errors=True)
    return parsed, meta


def run(pdf, report=None, model=DEFAULT_MODEL, vision=True, previews_dir=None, write=True, ref=REFERENCE):
    pdf = Path(pdf).resolve()
    previews_dir = Path(previews_dir) if previews_dir else pdf.parent
    previews = render_previews(pdf, previews_dir)
    instrument = None
    if report and Path(report).is_file():
        instrument = json.loads(Path(report).read_text())
        if Path(report).stat().st_mtime + 120 < pdf.stat().st_mtime:
            print(f"eye-check WARN: {report} is older than the PDF; re-render with --report")
    ipages = {p.get("page"): p for p in (instrument or {}).get("pages") or []}
    holes = {}
    for i, png in enumerate(previews, 1):
        holes[i] = blank_map(png, (ipages.get(i) or {}).get("img_rects") or ())
    flags, inst_text = instrument_flags(instrument) if instrument else (["no fill-instrument report given"], "")
    targets = length_targets(holes, instrument)
    hole_fails = [f"page {pn}: blank {h['w_in']}x{h['h_in']}in ({h['sq_in']} sq in) {where_words(h)}"
                  for pn, hs in holes.items() for h in hs if hole_breaks_rule(h)]
    gaps = {pn: [round((g.get("gap") or 0) * 0.75, 1) for g in (ipages.get(pn) or {}).get("block_gaps") or []]
            for pn in ipages}
    footer_gaps = {pn: [round((g or 0) / 96.0, 2) for g in (ipages.get(pn) or {}).get("gaps") or []]
                   for pn in ipages}
    numbers = {"pixel_blank_map": holes, "instrument_flags": flags, "inter_block_gaps_pt": gaps,
               "footer_gap_in_per_column": footer_gaps, "length_targets": targets}
    critique, meta = (None, {"skipped": True})
    if vision:
        ref_pngs = [p for p in (ref / "preview-p1.png", ref / "preview-p2.png") if p.is_file()]
        critique, meta = vision_critique(previews, ref_pngs, numbers, model=model)
    reasons = []
    if hole_fails:
        reasons += hole_fails
    if flags:
        reasons += ["instrument: " + f for f in flags]
    if not vision:
        reasons.append("vision critique skipped (--no-vision): not sendable")
    elif critique is None:
        reasons.append("vision critique failed to run: " + str(meta.get("error", ""))[:300])
    else:
        majors = [i for i in critique.get("issues") or [] if str(i.get("severity", "major")).lower() == "major"]
        if str(critique.get("verdict", "")).upper() != "PASS" or majors:
            reasons.append("vision critique: FAIL - " + str(critique.get("summary", ""))
                           + "".join(f" | major p{i.get('page')}: {i.get('problem')}" for i in majors))
    verdict = "PASS" if not reasons else "FAIL"
    out = {
        "verdict": verdict,
        "pdf": str(pdf.relative_to(ROOT)) if str(pdf).startswith(str(ROOT)) else str(pdf),
        "pdf_sha256": sha256(pdf),
        "checked_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "reasons": reasons,
        "length_targets": targets,
        "pixel_blank_map": holes,
        "inter_block_gaps_pt": gaps,
        "instrument_flags": flags,
        "vision": {"meta": meta, "critique": critique},
        "reference": str(ref.relative_to(ROOT)) if str(ref).startswith(str(ROOT)) else str(ref),
        "previews": [str(p) for p in previews],
        "rules": {"hole_max_sq_in": HOLE_MAX_SQ_IN, "bottom_band_max_in": BOTTOM_BAND_MAX_IN},
        "clark_looked": False,
    }
    if write:
        jp, mp = result_paths(pdf)
        jp.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        mp.write_text(to_markdown(out), encoding="utf-8")
    return out


def to_markdown(r):
    lines = [f"# Eye check: {r['verdict']}", "", f"PDF `{r['pdf']}` (sha256 {r['pdf_sha256'][:12]}), checked {r['checked_at']}.", ""]
    if r["reasons"]:
        lines += ["## Why not PASS", ""] + [f"- {x}" for x in r["reasons"]] + [""]
    if r["length_targets"]:
        lines += ["## Length targets (editor's call; vetted copy only)", ""]
        lines += [f"- Page {t['page']}: {t['action']} ~{t['words']} words ({t['where']})" for t in r["length_targets"]]
        lines += [""]
    c = (r.get("vision") or {}).get("critique") or {}
    meta = (r.get("vision") or {}).get("meta") or {}
    if c:
        lines += [f"## Vision critique ({meta.get('model') or meta.get('model_alias')}): {c.get('verdict')}", "", str(c.get("summary", "")), ""]
        for k, v in (c.get("rubric") or {}).items():
            if isinstance(v, dict):
                lines.append(f"- {k}: {'pass' if v.get('pass') else 'FAIL'} - {v.get('notes', '')}")
        for it in c.get("issues") or []:
            lines.append(f"- [{it.get('severity', '?')}] p{it.get('page')} {it.get('where')}: {it.get('problem')} -> {it.get('fix')}")
        lines.append("")
    lines += ["## Pixel blank map", ""]
    for pn, hs in r["pixel_blank_map"].items():
        lines.append(f"- Page {pn}: " + ("; ".join(f"{h['w_in']}x{h['h_in']}in @({h['x_in']},{h['y_in']})" + (" [bottom band]" if h['bottom_band'] else "") for h in hs) or "none"))
    lines += ["", "Send only after `python3 compose/eyecheck.py --verify <pdf>` passes and Clark has looked at the previews.", ""]
    return "\n".join(lines)


def verify(pdf):
    """Exit status 0 only if eye-check.json is PASS (or waived) for exactly this PDF."""
    pdf = Path(pdf).resolve()
    jp, _ = result_paths(pdf)
    if not jp.is_file():
        return False, "no eye-check.json beside the PDF: run compose/eyecheck.py first"
    r = json.loads(jp.read_text())
    if r.get("pdf_sha256") != sha256(pdf):
        return False, "eye-check.json is for a different PDF (re-run the eye check on this one)"
    if r.get("verdict") == "PASS":
        return True, "PASS"
    if r.get("waived_by"):
        return True, f"FAIL waived by {r['waived_by']} ({r.get('waiver_note', '')})"
    return False, "verdict FAIL: " + "; ".join(r.get("reasons") or [])[:800]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--verify":
        ok, why = verify(argv[1])
        print(("SENDABLE: " if ok else "NOT SENDABLE: ") + why)
        return 0 if ok else 1
    pdf = argv[0]
    opt = lambda p, d=None: next((a.split("=", 1)[1] for a in argv if a.startswith(p)), d)
    r = run(pdf, report=opt("--report="), model=opt("--model=", DEFAULT_MODEL),
            vision="--no-vision" not in argv, previews_dir=opt("--previews="),
            ref=Path(opt("--ref=", str(REFERENCE))).resolve())
    print(to_markdown(r))
    return 0 if r["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
