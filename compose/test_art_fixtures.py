#!/usr/bin/env python3
"""Chrome fixtures for art-fit. Writes only under /tmp/gz-fixtures/. Never into issues/.

    python3 compose/test_art_fixtures.py
"""
import json, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "compose"))
from gazette import *
import art as A

OUT = Path("/tmp/gz-fixtures")
if OUT.exists():
    shutil.rmtree(OUT)
ROOT_FX = OUT / "root"
(ROOT_FX / "issues" / "fixture").mkdir(parents=True)
(ROOT_FX / "issues" / "no6").mkdir()
(ROOT_FX / "issues" / "float").mkdir()
# relative media/masthead like a real issue
for sub in ("fixture", "no6", "float"):
    (ROOT_FX / "issues" / sub / "media").symlink_to(REPO / "issues" / "2026-11-11" / "media")
# Flessel lives in No. 5
(ROOT_FX / "issues" / "float" / "media5").symlink_to(REPO / "issues" / "2026-11-03" / "media")
(ROOT_FX / "masthead001.png").symlink_to(REPO / "masthead001.png")

# Also a tree used to render published HTML unchanged
for date in ("2026-11-11", "2026-11-03", "2026-10-26", "2026-10-19", "2026-10-13", "2026-10-08"):
    src = REPO / "issues" / date
    if not (src / "issue.html").is_file():
        continue
    dest = ROOT_FX / "issues" / date
    dest.mkdir(exist_ok=True)
    (dest / "issue.html").symlink_to(src / "issue.html")
    if (src / "media").is_dir() and not (dest / "media").exists():
        (dest / "media").symlink_to(src / "media")


def render(html_path, pdf_path, report_path, allow=False):
    cmd = [sys.executable, str(REPO / "compose" / "render.py"),
           str(html_path), str(pdf_path),
           f"--report={report_path}", f"--fit-report={report_path.with_name(report_path.stem + '-fit.json')}"]
    if allow:
        cmd.append("--allow-flag")
    r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    Path(str(pdf_path) + ".log").write_text(r.stdout + "\n" + r.stderr)
    return r


def write_html(folder, title, pages, extra_css=""):
    path = ROOT_FX / "issues" / folder / "issue.html"
    path.write_text(document(title, pages, extra_css=extra_css), encoding="utf-8")
    return path


EXTRA_P2 = """
  .p2-left { flex: 0 0 35%; }
  .p2-right { flex: 1; display: flex; flex-direction: column; }
"""

# ---- No. 6 page 2 cartoon: published HTML with the cartoon swapped to art()
# (issue-specific CSS kept; .art does not get margin-top:auto. Shared .art rules injected.)
ART_CSS = """
  :root { --colw: 2.42in; --art-w: 100%; }
  .art { margin: 6pt 0; max-width: 100%; }
  .art img { display: block; width: 100%; height: auto; filter: grayscale(100%); }
  .art--float { float: left; width: var(--art-w); margin: 2pt 9pt 3pt 0; }
  .art--gutter { width: var(--art-w); margin: 6pt auto 6pt 0; }
"""
pub = (REPO / "issues" / "2026-11-11" / "issue.html").read_text(encoding="utf-8")
if "</style>" not in pub:
    raise SystemExit("published No. 6 HTML has no </style>")
pub_fitted = pub.replace("</style>", ART_CSS + "\n</style>", 1)
old_comic = (
    '      <div class="comic-wide">\n'
    '        <div class="comicfig"><img src="media/tournament-day-cartoon.jpg" '
    'alt="A black-and-white comic titled Tournaments, showing a parent and young '
    'fencer’s tournament day in a clockwise loop."></div>\n'
    '      </div>'
)
cartoon = {
    "id": "cartoon", "src": "media/tournament-day-cartoon.jpg",
    "kind": "comic",
    "alt": "A black-and-white comic titled Tournaments, showing a parent and young fencer’s tournament day in a clockwise loop.",
    "region": "lower",
}
if old_comic not in pub_fitted:
    raise SystemExit("published comic-wide block not found; recipe changed?")
no6_src = pub_fitted.replace(old_comic, "      " + art(cartoon), 1)
no6_html = ROOT_FX / "issues" / "no6" / "issue.html"
no6_html.write_text(no6_src, encoding="utf-8")

# ---- Too-tall case: a 2-column-wide region (no rail, so H3 cannot poison the choice).
# Enough lead copy that a stack of the 3:2 cartoon (~3.3in at 4.96in wide) overshoots;
# wrap-eligible prose follows the art so a 1-column float can share the depth.
lead_paras = paras(
    "This is a fixture paragraph used only to take up depth so the stacked cartoon cannot fit. "
    "It is not published copy. The fencer names below are already in the public issue and are repeated "
    "here only so the page has real words to wrap beside a float: Maksim Milinkovic, Nico Ng, "
    "Stella Kuo, Mila Siu, Penny Young, Christina Jiang, Remy Ng, Amina Gore.\n\n"
    + ("The club travels this month to Glen Allen, Columbus, New Haven and Secaucus. "
       "Parents should check the deadlines box and the entry lists. " * 22)
)
wrap_paras = paras(
    "These sentences sit after the art in source order so they can wrap beside a narrower float. "
    "A beginner asked whether tennis shoes work as well as fencing shoes, at about half the price. "
    "Commenters said the usual recommendation is indoor court shoes — squash or volleyball. "
    "Some epee fencers prefer tennis shoes on aluminum strips. That is the commenters’ opinion, not advice.\n\n"
    "Ratings and bigger events come later. Sunday was the beginning, and the cartoon has to share the column. "
    "A float at about one column should leave the following sentences beside the art instead of below a stack.\n\n"
    "One more short paragraph of fixture copy, used only so the floated column can close the last of the leftover."
)
fp1 = page(
    masthead() + "\n" + dateline("Wednesday Edition", "Vol. I — Fixture · Chatham, N.J. · November 11, 2026")
    + "\n" + "<div class=\"art-region\" style=\"width:4.96in\">"
    + "<h1 class=\"head\">A Tall Cartoon Has to Share the Column</h1>"
    + "<p class=\"dek\">The stack at the region width is too deep for the leftover; the fitter should float.</p>"
    + lead_paras
    + art(cartoon)
    + wrap_paras
    + "</div>"
    + footer(0)
)
fp2 = page(
    dateline("Page Two", "Fixture · Vol. I — No. 0", first=False)
    + "\n" + paras("Page two of the float fixture. The fitter must not push a third page.")
    + footer(0)
)
float_html = write_html("float", "En Garde Gazette — art-fit float fixture", [fp1, fp2])

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"  OK  {name}")
    else:
        print(f"  FAIL {name} {detail}")
        failures.append(name + " " + (detail if isinstance(detail, str) else repr(detail)))


# 1) Frozen published HTML → /tmp, 0 art slots, HTML checksums later compared at repo files
print("=== published HTML through --fit to /tmp (0 slots) ===")
for date, n in (("2026-11-11", "no6"), ("2026-11-03", "no5")):
    html = ROOT_FX / "issues" / date / "issue.html"
    if not html.is_file():
        continue
    pdf = OUT / f"{n}-published-refit.pdf"
    rep = OUT / f"{n}-published-refit.json"
    r = render(html, pdf, rep, allow=True)
    log = r.stdout + r.stderr
    check(f"{n} published ran", pdf.is_file(), log[-400:])
    check(f"{n} 0 art slots", "0 art slots" in log, log[-400:])
    if pdf.is_file():
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        pages = next((ln.split()[1] for ln in info.splitlines() if ln.startswith("Pages:")), "?")
        check(f"{n} published is 2 pages", pages == "2", pages)

# 2) No. 6-like cartoon: expect stack, 2 pages, flush (side gutter tiny)
print("=== No. 6 cartoon fixture ===")
pdf = OUT / "no6-cartoon.pdf"
rep = OUT / "no6-cartoon.json"
r = render(no6_html, pdf, rep, allow=True)
log = r.stdout + r.stderr
(OUT / "no6-cartoon.log").write_text(log)
check("no6 fixture ran", pdf.is_file(), log[-500:])
fit = json.loads((OUT / "no6-cartoon-fit.json").read_text()) if (OUT / "no6-cartoon-fit.json").is_file() else {}
decs = fit.get("decisions") or []
check("no6 has a decision", bool(decs), str(fit)[:400])
if decs:
    d = decs[0]
    check("no6 chose stack", (d.get("cand") or {}).get("mode") == "stack", d.get("cand"))
    gutter = (d.get("rec") or {}).get("side_gutter_in") or 0
    check("no6 stack is flush (gutter < 0.1in)", gutter < 0.1, f"gutter={gutter}")
    check("no6 wrap_ok is false (art last)", d.get("wrap_ok") is False, d)
info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
pages = next((ln.split()[1] for ln in info.splitlines() if ln.startswith("Pages:")), "?")
check("no6 fixture is 2 pages", pages == "2", pages)
subprocess.run(["pdftoppm", "-r", "200", "-png", str(pdf), str(OUT / "no6-cartoon")], check=False)

# 3) Too-tall → float
print("=== too-tall float fixture ===")
pdf = OUT / "float-tall.pdf"
rep = OUT / "float-tall.json"
r = render(float_html, pdf, rep, allow=True)
log = r.stdout + r.stderr
(OUT / "float-tall.log").write_text(log)
check("float fixture ran", pdf.is_file(), log[-500:])
fit = json.loads((OUT / "float-tall-fit.json").read_text()) if (OUT / "float-tall-fit.json").is_file() else {}
decs = fit.get("decisions") or []
check("float has a decision", bool(decs))
if decs:
    d = decs[0]
    mode = (d.get("cand") or {}).get("mode")
    check("too-tall chose a passing float",
          mode == "float" and not d.get("flag") and str(d.get("why","")).startswith("float"),
          f"mode={mode} why={d.get('why')} flag={d.get('flag')} report={d.get('report')} rec={d.get('rec')}")
    check("float wrap_ok", d.get("wrap_ok") is True, d)
info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
pages = next((ln.split()[1] for ln in info.splitlines() if ln.startswith("Pages:")), "?")
check("float fixture is 2 pages", pages == "2", f"pages={pages} log={log[-300:]}")
subprocess.run(["pdftoppm", "-r", "200", "-png", str(pdf), str(OUT / "float-tall")], check=False)

print()
if failures:
    print(f"{len(failures)} fixture check(s) failed:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("art fixtures: all checks passed")
