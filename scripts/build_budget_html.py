#!/usr/bin/env python3
"""Build the standalone Gazette budget page: ONE self-contained .html, no server, no network.

Inlines the lineup (practice-lineup.json, schema 2), the staging week's items.json and
media/manifest.json as JSON, small B&W JPEG thumbnails as data-URIs, and all CSS/JS
(scripts/budget_page/). A CSP meta tag (default-src 'none') blocks every network request.
Frank opens the file on his laptop or phone, vets/includes/answers locally, and Submit downloads +
copies a JSON file; scripts/ingest_budget_submission.py applies it on the box.
See budget-demo/STANDALONE-README.md.

Usage:
  python3 scripts/build_budget_html.py [--lineup FILE] [--staging-week DIR] [--out FILE|DIR]
                                       [--thumb-width 360] [--quality 70]
Defaults: budget-demo/practice-lineup.json, staging/weeks/next,
  budget-demo/out/budget-no-<N>-<publish-date>.html
Output holds unvetted content and minors' names: it must land somewhere gitignored
(budget-demo/out/ is) or outside the repo.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ASSETS = Path(__file__).resolve().parent / "budget_page"
DEFAULT_LINEUP = REPO / "budget-demo" / "practice-lineup.json"
DEFAULT_WEEK = REPO / "staging" / "weeks" / "next"
DEFAULT_OUT_DIR = REPO / "budget-demo" / "out"
RASTER = (".png", ".jpg", ".jpeg", ".gif", ".webp")
CAPACITY_KEYS = ("page1_col_in", "page2_col_in", "wpi", "wpi_feature", "head_short", "head_feature", "gap",
                 "table_head", "row_rail", "row_full", "col_width_in", "span2_width_in", "caption_in")
SIZE_TARGET = 2 * 1024 * 1024


def die(msg: str, code: int = 1) -> None:
    print(f"build_budget_html: error: {msg}", file=sys.stderr)
    sys.exit(code)


def rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(REPO))
    except ValueError:
        return str(p)


def load_json(path: Path, what: str):
    if not path.is_file():
        die(f"{what} not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        die(f"{what} is not valid JSON ({path}): {exc}")


def check_lineup(cfg) -> list[str]:
    if not isinstance(cfg, dict):
        return ["lineup must be a JSON object"]
    errs = []
    if cfg.get("schema") not in (1, 2):
        errs.append(f"lineup schema must be 2 (got {cfg.get('schema')!r})")
    slots = cfg.get("slots", cfg.get("lineup"))
    if not isinstance(slots, list):
        errs.append("lineup needs a 'slots' list")
    issue = cfg.get("issue")
    if not isinstance(issue, dict) or issue.get("number") is None:
        errs.append("lineup needs issue.number")
    pub = cfg.get("publish")
    if not isinstance(pub, dict) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(pub.get("date", ""))):
        errs.append("lineup needs publish.date (YYYY-MM-DD)")
    cap = cfg.get("capacity")
    if not isinstance(cap, dict):
        errs.append("lineup needs a 'capacity' object")
    else:
        bad = [k for k in CAPACITY_KEYS if not isinstance(cap.get(k), (int, float))]
        if bad:
            errs.append("capacity missing numeric keys: " + ", ".join(bad))
    if "sections" in cfg and not isinstance(cfg["sections"], list):
        errs.append("'sections' must be a list")
    return errs


def media_file(media_dir: Path, ref: str | None) -> Path | None:
    """Resolve a media reference (filename or staging/weeks/<x>/media/<file>) to this week's media dir."""
    name = str(ref or "").rsplit("/", 1)[-1]
    if not name or name in (".", ".."):
        return None
    return media_dir / name


def make_thumb(src: Path, width: int, quality: int) -> dict:
    """B&W JPEG data-URI ("as printed", like practice.html's /thumb?bw=1)."""
    from PIL import Image

    with Image.open(src) as im:
        im.seek(0)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            bg.alpha_composite(im)
            im = bg
        im = im.convert("L")
        if im.width > width:
            im = im.resize((width, max(1, round(im.height * width / im.width))), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        w, h = im.size
    return {"src": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii"), "w": w, "h": h}


def add_media_sizes(manifest: dict, media_dir: Path) -> None:
    """Pixel w/h on manifest entries (same as server.py _add_media_sizes) for the photo cost model."""
    from PIL import Image

    for m in manifest.get("items", []):
        if not isinstance(m, dict) or m.get("w"):
            continue
        src = media_file(media_dir, m.get("filename") or m.get("media_path"))
        if not src or not src.is_file() or src.suffix.lower() == ".svg":
            continue
        try:
            with Image.open(src) as im:
                m["w"], m["h"] = im.size
        except Exception:  # noqa: BLE001 — unreadable image: no size, page falls back to 1:1
            pass


def script_json(obj) -> str:
    """JSON safe inside <script type="application/json">: no </script>, <!--, or raw U+2028/9."""
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return (text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def ensure_ignored(out: Path) -> None:
    """Refuse to write the page anywhere git would track it."""
    try:
        out.resolve().relative_to(REPO)
    except ValueError:
        return  # outside the repo (e.g. /tmp): fine
    try:
        r = subprocess.run(["git", "-C", str(REPO), "check-ignore", "-q", str(out.resolve())],
                           capture_output=True, timeout=10)
        ignored = r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        ignored = DEFAULT_OUT_DIR.resolve() in out.resolve().parents
    if not ignored:
        die(f"refusing to write {rel(out)}: it is inside the repo and not gitignored "
            f"(the page holds unvetted content and minors' names). Use {rel(DEFAULT_OUT_DIR)}/ or a path outside the repo.")


def self_check(html: str, data: dict) -> list[str]:
    """Static sanity checks on the generated page."""
    problems = []
    m = re.search(r'<script type="application/json" id="budget-data">(.*?)</script>', html, re.S)
    if not m:
        problems.append("inlined data block not found")
    else:
        try:
            back = json.loads(m.group(1))
            if back.get("build", {}).get("dataVersion") != data["build"]["dataVersion"]:
                problems.append("inlined data did not round-trip")
        except json.JSONDecodeError as exc:
            problems.append(f"inlined data does not parse: {exc}")
    code = html[:m.start(1)] + html[m.end(1):] if m else html  # markup/CSS/JS only (data is just strings)
    if m and re.search(r"</script|<!--", m.group(1), re.I):
        problems.append("inlined data contains </script or <!--")
    loads = re.findall(r'(?:src|href)\s*=\s*["\']?\s*(?:https?:)?//|url\(\s*["\']?\s*(?:https?:)?//|@import|<link\b|<iframe\b|<object\b|<embed\b', code, re.I)
    if loads:
        problems.append(f"possible network resource loads: {loads[:5]}")
    for pat in (r"\bfetch\(", r"XMLHttpRequest", r"new WebSocket", r"EventSource", r"sendBeacon", r"importScripts"):
        if re.search(pat, code):
            problems.append(f"network API in page: {pat}")
    if "default-src 'none'" not in html:
        problems.append("CSP meta missing")
    return problems


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the standalone (offline) Gazette budget page.")
    ap.add_argument("--lineup", type=Path, default=DEFAULT_LINEUP, help="lineup JSON (default budget-demo/practice-lineup.json)")
    ap.add_argument("--staging-week", type=Path, default=DEFAULT_WEEK, help="dir with items.json + media/ (default staging/weeks/next)")
    ap.add_argument("--out", type=Path, help="output .html file or directory (default budget-demo/out/)")
    ap.add_argument("--thumb-width", type=int, default=360, help="thumbnail width px (default 360)")
    ap.add_argument("--quality", type=int, default=70, help="thumbnail JPEG quality (default 70)")
    args = ap.parse_args()
    if not 64 <= args.thumb_width <= 1200:
        die("--thumb-width must be 64..1200")
    if not 20 <= args.quality <= 95:
        die("--quality must be 20..95")
    try:
        import PIL  # noqa: F401
    except ImportError:
        die("Pillow is required (python3 -m pip install Pillow)")

    lineup_path, week = args.lineup.resolve(), args.staging_week.resolve()
    cfg = load_json(lineup_path, "lineup")
    errs = check_lineup(cfg)
    if errs:
        die("bad lineup " + rel(lineup_path) + ":\n  - " + "\n  - ".join(errs))
    if not week.is_dir():
        die(f"staging week dir not found: {week}")
    items_doc = load_json(week / "items.json", "items.json")
    if not isinstance(items_doc, dict) or not isinstance(items_doc.get("items"), list):
        die(f"{rel(week / 'items.json')} must be an object with an 'items' list")
    media_dir = week / "media"
    manifest_path = media_dir / "manifest.json"
    warnings = []
    if manifest_path.is_file():
        manifest = load_json(manifest_path, "media manifest")
        if not isinstance(manifest, dict) or not isinstance(manifest.get("items", []), list):
            die(f"{rel(manifest_path)} must be an object with an 'items' list")
        manifest.setdefault("items", [])
    else:
        manifest = {"items": []}
        warnings.append(f"no media manifest at {rel(manifest_path)} (no photos)")
    add_media_sizes(manifest, media_dir)

    items = [i for i in items_doc["items"] if isinstance(i, dict) and i.get("id")]
    by_id = {i["id"]: i for i in items}
    slots = [s for s in (cfg.get("slots") or cfg.get("lineup") or []) if isinstance(s, dict)]
    missing_items = [s["item"] for s in slots if s.get("item") and s["item"] not in by_id]
    missing_merged = [m for s in slots for m in (s.get("merged") or []) if m not in by_id]
    media_ids = {m.get("id") for m in manifest["items"] if isinstance(m, dict)}
    missing_photos = [p.get("id") for p in cfg.get("photos") or [] if isinstance(p, dict) and p.get("id") not in media_ids and p.get("id") not in by_id]

    # thumbnails for everything the page can show: slot thumbs, item media, manifest photos
    refs = [s.get("thumb") for s in slots]
    refs += [i.get("media_path") for i in items]
    refs += [m.get("filename") or m.get("media_path") for m in manifest["items"] if isinstance(m, dict)]
    thumbs, missing_media = {}, []
    for ref in refs:
        src = media_file(media_dir, ref)
        if not src or src.name in thumbs or src.suffix.lower() not in RASTER:
            continue
        if not src.is_file():
            if src.name not in missing_media:
                missing_media.append(src.name)
            continue
        try:
            thumbs[src.name] = make_thumb(src, args.thumb_width, args.quality)
        except Exception as exc:  # noqa: BLE001 — bad image: no thumbnail, keep going
            warnings.append(f"thumbnail failed for {src.name}: {exc}")

    version = hashlib.sha256(json.dumps([cfg, items_doc, manifest], sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
    number, date = cfg["issue"]["number"], cfg["publish"]["date"]
    data = {
        "build": {
            "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
            "generator": "scripts/build_budget_html.py",
            "lineupPath": rel(lineup_path), "stagingWeek": rel(week), "dataVersion": version,
            "thumbWidth": args.thumb_width,
            "missing": {"items": missing_items, "merged": missing_merged, "photos": missing_photos, "media": missing_media},
        },
        "lineup": cfg, "items": items_doc, "media": manifest, "thumbs": thumbs,
    }

    page = (ASSETS / "page.html").read_text(encoding="utf-8")
    parts = {name: (ASSETS / name).read_text(encoding="utf-8") for name in ("page.css", "core.js", "ui.js")}
    for name, text in parts.items():
        if re.search(r"</(script|style)", text, re.I):
            die(f"{name} contains a closing </script> or </style> tag")
    title = f"Budget — {cfg['issue'].get('label') or 'Issue No. ' + str(number)}" + ("" if cfg.get("mode") == "real" else " (practice)")
    html = (page.replace("@@TITLE@@", title.replace("&", "&amp;").replace("<", "&lt;"))
            .replace("@@CSS@@", parts["page.css"]).replace("@@CORE_JS@@", parts["core.js"])
            .replace("@@UI_JS@@", parts["ui.js"]).replace("@@DATA@@", script_json(data)))

    problems = self_check(html, data)
    if problems:
        die("generated page failed self-check:\n  - " + "\n  - ".join(problems))

    out = args.out.resolve() if args.out else DEFAULT_OUT_DIR
    if out.suffix.lower() != ".html":
        out = out / f"budget-no-{number}-{date}.html"
    ensure_ignored(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(html.encode("utf-8"))

    size = out.stat().st_size
    auto = sum(1 for i in items if i["id"] not in {s.get("item") for s in slots})
    print(f"wrote {rel(out)}  ({size / 1024:.0f} KB)")
    print(f"  issue No. {number} · publish {date} · lineup {rel(lineup_path)} · staging {rel(week)} · data {version}")
    print(f"  slots {len(slots)} ({sum(1 for s in slots if s.get('empty'))} empty) · items {len(items)} "
          f"(≤{auto} not in a lineup slot) · media {len(manifest['items'])} · thumbnails {len(thumbs)} "
          f"({sum(len(t['src']) for t in thumbs.values()) / 1024:.0f} KB)")
    if missing_items:
        print(f"  lineup items not in staging ({len(missing_items)}): " + ", ".join(missing_items))
    if missing_merged:
        print(f"  merged items not in staging ({len(missing_merged)}): " + ", ".join(missing_merged))
    if missing_photos:
        print(f"  lineup photos not in staging: " + ", ".join(missing_photos))
    if missing_media:
        print(f"  media files missing (no thumbnail): " + ", ".join(missing_media))
    for w in warnings:
        print(f"  warning: {w}")
    if size > SIZE_TARGET:
        print(f"  warning: page is {size / 1048576:.1f} MB (target < 2 MB); try --thumb-width 320 --quality 60")
    print("  self-check: ok (inlined JSON parses; no network loads; CSP default-src 'none')")


if __name__ == "__main__":
    main()
