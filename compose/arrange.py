#!/usr/bin/env python3
"""Try an issue's candidate arrangements and rank them (Frank t229u, 2026-11-16).

    python3 compose/arrange.py issues/<date> [--len=item:size ...] [--eye=2] [--only=a,b]

The recipe (issues/<date>/recipe/compose.py) declares ARRANGEMENTS (name -> layout choices:
tall/wide box shapes, photo pair vs float, rail vs full width ...) and a
build(arrangement, picks) function that returns the issue HTML. This driver renders every
arrangement with the current copy lengths, measures each with the eye check's pixel blank
map and the fill instrument (no vision; cheap), and ranks them. With --eye=N the top N also
get the vision critique, so the composer can pick the best or show Frank the top two.

Writes issues/<date>/arrangements.json. Never touches issue.html or the proof PDF; pick a
winner with `recipe/arrangement.json` or `--arrangement=` on the recipe, then build the
proof the normal way and run compose/eyecheck.py on it.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

COMPOSE = Path(__file__).resolve().parent
ROOT = COMPOSE.parent
sys.path.insert(0, str(COMPOSE))
import eyecheck as E  # noqa: E402


def load_recipe(issue_dir):
    path = ROOT / issue_dir / "recipe" / "compose.py"
    spec = importlib.util.spec_from_file_location("recipe_" + Path(issue_dir).name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "ARRANGEMENTS") or not hasattr(mod, "build"):
        raise SystemExit(f"{path} has no ARRANGEMENTS/build(); nothing to try")
    return mod


def score(ec):
    """Lower is better. Rule-breaking holes and instrument FLAGs dominate; then total blank."""
    s = 0.0
    breaks = 0
    for hs in ec["pixel_blank_map"].values():
        for h in hs:
            if E.hole_breaks_rule(h):
                breaks += 1
            s += (h["h_in"] * 7.5 * 0.3) if h["bottom_band"] else h["sq_in"]
    s += 6 * breaks + 3 * len(ec["instrument_flags"])
    return round(s, 2), breaks


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    issue_dir = argv[0].rstrip("/")
    only = next((a.split("=", 1)[1].split(",") for a in argv if a.startswith("--only=")), None)
    eye_n = int(next((a.split("=", 1)[1] for a in argv if a.startswith("--eye=")), "0"))
    mod = load_recipe(issue_dir)
    picks = mod.lengths_for(issue_dir, argv)
    work = Path(tempfile.mkdtemp(prefix="gz-arrange-"))
    results = []
    for name in mod.ARRANGEMENTS:
        if only and name not in only:
            continue
        html = ROOT / issue_dir / f".trial-{name}.html"
        html.write_text(mod.build(name, picks), encoding="utf-8")
        pdf = work / f"{name}.pdf"
        rep = work / f"{name}.json"
        try:
            r = subprocess.run([sys.executable, str(COMPOSE / "render.py"), str(html), str(pdf),
                                f"--report={rep}", "--allow-flag"], cwd=str(ROOT),
                               capture_output=True, text=True, timeout=600)
        finally:
            html.unlink(missing_ok=True)
        if not pdf.is_file():
            results.append({"arrangement": name, "error": (r.stderr or r.stdout)[-600:]})
            continue
        pdir = work / name
        pdir.mkdir(exist_ok=True)
        ec = E.run(pdf, report=rep, vision=False, previews_dir=pdir, write=False)
        sc, breaks = score(ec)
        results.append({"arrangement": name, "choices": mod.ARRANGEMENTS[name], "score": sc,
                        "rule_breaking_holes": breaks, "instrument_flags": ec["instrument_flags"],
                        "length_targets": ec["length_targets"], "pixel_blank_map": ec["pixel_blank_map"],
                        "previews": ec["previews"], "pdf": str(pdf)})
        print(f"{name:28s} score {sc:6.2f}  holes over rule {breaks}  flags {len(ec['instrument_flags'])}")
    ranked = sorted([r for r in results if "score" in r], key=lambda r: r["score"])
    for r in ranked[:eye_n]:
        ec = E.run(r["pdf"], report=str(Path(r["pdf"]).with_suffix(".json")), vision=True,
                   previews_dir=Path(r["previews"][0]).parent, write=False)
        r["vision"] = ec["vision"]
        r["eye_verdict"] = ec["verdict"]
        print(f"  eye check {r['arrangement']}: {ec['verdict']}")
    out = {"issue": issue_dir, "lengths": picks, "ranked": ranked,
           "errors": [r for r in results if "error" in r], "work_dir": str(work)}
    (ROOT / issue_dir / "arrangements.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    if ranked:
        print(f"best: {ranked[0]['arrangement']} (previews in {Path(ranked[0]['previews'][0]).parent})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
