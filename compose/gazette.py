#!/usr/bin/env python3
"""Shared composer for En Garde Gazette, Template A.

Every issue recipe (issues/<date>/recipe/compose.py) imports this module and supplies only
its data and block order. Design fixes made here reach every future issue.

    from gazette import *          # after putting <repo>/compose on sys.path

What lives here
  ROOT                  repo root, derived from this file (never a hardcoded absolute path)
  base_css()            compose/template-a.css (the one stylesheet)
  ty(), paras()         house typography; paras() adds soft hyphens (pyphen, proper names skipped)
  piece(), stack()      kicker + headline + body; a kicker shared by adjacent pieces prints once
  table()               plain board
  results_table()       Club Results: tournament/date sub-row once, then one-line rows
  tourney()             one block per tournament; thin days become a Day column
  board_split()         two halves of a full-width board; box notes go under the shorter half
  box(), box_pair()     tabular box; two small boxes side by side
  photo(), credit_line(), photo_span()   photo furniture and the placement rule
  art(), load_art_manifest()             flexible art slot (comics, diagrams, photos)
  textcols(), split()   prose in ruled columns
  masthead(), dateline(), footer(), page(), document(), write_issue()
  check_issue()         compose-time checks (credit form, weapon spelling)
"""
import html, json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_VENDOR = Path(__file__).resolve().parent / "vendor"      # pip install --target compose/vendor pyphen
if _VENDOR.is_dir() and str(_VENDOR) not in sys.path:
    sys.path.insert(0, str(_VENDOR))
try:
    import pyphen
    _DIC = pyphen.Pyphen(lang="en_US", left=3, right=3)
except Exception:                                          # composing still works, just unhyphenated
    _DIC = None
    print("gazette: pyphen not found - body text will not be hyphenated "
          "(pip install --target compose/vendor pyphen)", file=sys.stderr)

SHY = "­"
NBH = "‑"  # U+2011 non-breaking hyphen; preserves compounds like regular-fee
WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)
    print("compose WARN: " + msg, file=sys.stderr)


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def base_css():
    return (ROOT / "compose" / "template-a.css").read_text(encoding="utf-8")


# ----------------------------------------------------------------- typography
_WORD = re.compile(r"(?<![\w/@.’'\-–—‑&#$­])([a-zà-ÿ]{7,})(?![\w/@’'\-–—‑­]|\.\w)")


def hyphenate(text):
    """Insert soft hyphens into ordinary lowercase words of 7+ letters.

    Skipped on purpose: anything capitalised (names, places, sentence openers), words joined by a
    hyphen, non-breaking hyphen, or apostrophe, anything touching a digit, slash, @ or dot
    (r/Fencing, URLs), and the last word of the paragraph (a hyphenated last line is the ugliest
    break there is). Existing hard hyphens are never turned into soft hyphens.
    At least 3 letters stay on each side of a break."""
    if _DIC is None:
        return text
    last = None
    for last in _WORD.finditer(text):
        pass
    tail = text.rstrip()
    skip_start = last.start(1) if (last and last.end(1) >= len(tail.rstrip(".,;:!?”\"’')*")) ) else -1

    def sub(m):
        if m.start(1) == skip_start:
            return m.group(1)
        return _DIC.inserted(m.group(1), hyphen=SHY)
    return _WORD.sub(sub, text)


def ty(t, hyph=False):
    """House typography: curly quotes, *italic*, **run-in bold**, non-breaking date/time joins.
    hyph=True (body paragraphs only) also places soft hyphens."""
    if hyph:
        t = hyphenate(t)
    t = html.escape(t, quote=False)
    t = re.sub(r'(^|[\s(\[—–-])"', r'\1“', t); t = t.replace('"', '”')
    t = re.sub(r"(\w)'(\w)", r"\1’\2", t); t = re.sub(r"(^|[\s(“])'", r"\1‘", t); t = t.replace("'", "’")
    t = re.sub(r'\*\*(.+?)\*\*', r'<b class="run">\1</b>', t); t = re.sub(r'\*(.+?)\*', r'<i>\1</i>', t)
    t = re.sub(r'(Oct|Nov|Dec|Jan|Feb)\. (\d)', r'\1.&nbsp;\2', t)
    t = re.sub(r'(\d) (a\.m\.|p\.m\.)', '\\1&nbsp;\\2', t)
    t = re.sub(r'(\d) (milliseconds)', '\\1&nbsp;\\2', t)
    # Preserve existing hard hyphens in letter-letter compounds (regular-fee, triple-fee).
    # An ASCII hyphen is a line-break opportunity; when Chrome breaks there, pdftotext
    # treats it as a hyphenation hyphen and the compound comes out as "regularfee".
    # U+2011 stays visible and does not break.
    t = re.sub(r'(?<=[A-Za-z])-(?=[A-Za-z])', NBH, t)
    return t


def paras(t, cls=None):
    c = f' class="{cls}"' if cls else ""
    return "\n".join(f"<p{c}>{ty(p.strip(), hyph=True)}</p>" for p in t.strip().split("\n\n") if p.strip())


def nw(n):
    return f'<span class="nw">{n}</span>'


def protect_hyphens(s):
    """Turn letter-hyphen-letter ASCII hyphens into U+2011 in already-built HTML cells.
    Tags and attribute values are left alone."""
    parts = re.split(r'(<[^>]+>)', s)
    out = []
    for part in parts:
        if part.startswith("<"):
            out.append(part)
        else:
            out.append(re.sub(r'(?<=[A-Za-z])-(?=[A-Za-z])', NBH, part))
    return "".join(out)


def plain(s):
    """Visible text of an HTML fragment (for estimates and checks)."""
    return html.unescape(re.sub(r"<[^>]+>", "", s)).replace(SHY, "").replace(NBH, "-").replace(" ", " ")


# ----------------------------------------------------------------- text measure (estimates only)
try:
    from PIL import ImageFont
    _F = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", 100)
    def _w(text, pt): return _F.getlength(text) * pt / 100.0
except Exception:
    def _w(text, pt): return len(text) * pt * 0.44


def est_lines(text, width_pt, pt=8.5):
    """Greedy word wrap: how many lines `text` takes in a measure of width_pt."""
    n, cur = 1, 0.0
    space = _w(" ", pt)
    for word in plain(text).split():
        w = _w(word, pt)
        if cur and cur + space + w > width_pt:
            n += 1; cur = w
        else:
            cur = cur + (space if cur else 0) + w
    return n


LINE = 10.71      # 8.5pt x 1.26
ROW_PAD = 2.5     # cell padding + rule


def _in(s):
    """Column width string ('0.85in' or '61.5pt') to points."""
    if not s:
        return None
    return float(s[:-2]) * (72 if s.endswith("in") else 1)


def _table_height(cols, rows, width_pt, subrows=0):
    fixed = sum(_in(c) for c in cols if c)
    free = [c for c in cols if not c]
    flex = (width_pt - fixed) / max(1, len(free))
    h = 12.0 + subrows * 13.0                      # header row + sub-rows
    for r in rows:
        n = 1
        for c, cell in zip(cols, r):
            n = max(n, est_lines(cell, (_in(c) if c else flex) - 4))
        h += n * LINE + ROW_PAD
    return h


class Block(str):
    """An HTML string that also knows roughly how tall it is at a given width (points)."""
    est = None
    def height(self, width_pt):
        return self.est(width_pt) if self.est else 0.0


def _block(markup, est):
    b = Block(markup); b.est = est
    return b


# ----------------------------------------------------------------- boards
def _colgroup(cols):
    return "<colgroup>" + "".join(f'<col style="width:{c}">' if c else "<col>" for c in cols) + "</colgroup>"


def table(head, rows, cols, numcol=0):
    """Plain board. Cells are HTML already (pass them through ty() first)."""
    h = "<tr>" + "".join(f'<th{" class=\"r\"" if i == numcol else ""}>{ty(x)}</th>' for i, x in enumerate(head)) + "</tr>"
    rr = "".join("<tr>" + "".join(f'<td{" class=\"num\"" if i == numcol else ""}>{protect_hyphens(x)}</td>' for i, x in enumerate(r)) + "</tr>" for r in rows)
    return f'<table class="board">{_colgroup(cols)}{h}{rr}</table>'


_RES = re.compile(r"^(?P<t>.+), (?P<e>[^,]+?) \((?P<d>[^()]+)\)$")


def results_table(rows, cols=None, head=("Fencer", "Event", "Finish"), width_pt=157.0):
    """Club Results (A7). rows = [fencer, "Tournament, Event (Date)", finish] exactly as vetted.

    The tournament and its date print once, as a sub-row ("NYFA #1 · NOV. 8"), and each fencer
    gets a one-line row: Fencer / Event / Finish. A new sub-row starts whenever the tournament or
    the date changes, so a two-day tournament gets one sub-row per day. No fact is dropped; a row
    that does not parse as "Tournament, Event (Date)" is printed as it came.
    width_pt is the inside width of the box the table sits in (default: a one-column rail box)."""
    groups = []                                    # [(tournament, date), [(fencer, event, finish)]]
    for fencer, ev, finish in rows:
        m = _RES.match(plain(ev).strip())
        key, e = ((m.group("t"), m.group("d")), m.group("e")) if m else (None, ev)
        if groups and groups[-1][0] == key and key is not None:
            groups[-1][1].append((fencer, e, finish))
        else:
            groups.append([key, [(fencer, e, finish)]])
    if cols is None:
        # Widths follow content. Finish is capped (a long "5th of 83 · earned A26" wraps); Event
        # gets its longest entry on one line; Fencer takes the rest, down to the longest single
        # word of a name, so a long name wraps before an event does.
        ev_w = max(_w(plain(e), 8.5) for _, rs in groups for _, e, _ in rs) + 4.5      # + cell padding
        fin_w = min(max(_w(plain(r[2]), 8.5) for r in rows) + 4.5, 50)
        name_w = max(_w(plain(r[0]), 8.5) for r in rows) + 4.5
        word_w = max(_w(w, 8.5) for r in rows for w in plain(r[0]).split()) + 4.5
        name_w = max(word_w, min(name_w, width_pt - fin_w - ev_w))
        cols = (f"{name_w:.1f}pt", None, f"{fin_w:.1f}pt")
    n = len(head)
    out = "<tr>" + "".join(f"<th>{ty(x)}</th>" for x in head) + "</tr>"
    for key, rs in groups:
        if key is not None:
            t, d = key
            words = ty(t).rsplit(" ", 1)           # keep "last word · date" together on a wrap
            label = (words[0] + " " if len(words) > 1 else "") + nw(f"{words[-1]} · {ty(d)}")
            out += f'<tr class="day"><td colspan="{n}">{label}</td></tr>'
        for fencer, e, finish in rs:
            out += f"<tr><td>{ty(fencer)}</td><td>{ty(e)}</td><td>{ty(finish)}</td></tr>"
    return f'<table class="board">{_colgroup(cols)}{out}</table>'


def tourney(name, where, dates, head, cols, days, layout="auto", day_col="0.98in"):
    """One block per tournament: name · town · dates once (STYLE-GUIDE §10a).

    days = [(day label, [row, ...]), ...]; a row is a list of HTML cells matching `head`.
    layout="rows"    days are sub-rows inside the table (busy tournaments, e.g. Cobra).
    layout="column"  a leading Day column replaces the sub-rows (A8).
    layout="auto"    use the Day column when the sub-rows would outnumber half the data rows
                     (that is, when most days hold a single event); otherwise sub-rows."""
    nrows = sum(len(r) for _, r in days)
    labelled = [d for d, _ in days if d]
    if layout == "auto":
        layout = "column" if labelled and 2 * len(labelled) > nrows else "rows"
    timed = head[0] == "Time"
    def cells(r, off=0):
        return "".join(f'<td{" class=\"num\"" if (i == 0 and timed) else ""}>{protect_hyphens(x)}</td>' for i, x in enumerate(r))
    if layout == "column":
        hd = ["Day"] + list(head); cc = [day_col] + list(cols)
        h = "<tr><th>Day</th>" + "".join(f'<th{" class=\"r\"" if (i == 0 and timed) else ""}>{x}</th>' for i, x in enumerate(head)) + "</tr>"
        rr, flat = "", []
        for label, rows in days:
            for j, r in enumerate(rows):
                rr += f'<tr><td class="dayc">{label if j == 0 else ""}</td>{cells(r)}</tr>'
                flat.append([label] + list(r))
        est = lambda w, cc=cc, flat=flat: 12.5 + _table_height(cc, flat, w)
    else:
        n = len(head); cc = list(cols)
        h = "<tr>" + "".join(f'<th{" class=\"r\"" if (i == 0 and timed) else ""}>{x}</th>' for i, x in enumerate(head)) + "</tr>"
        rr, flat = "", []
        for label, rows in days:
            if label:
                rr += f'<tr class="day"><td colspan="{n}">{label}</td></tr>'
            rr += "".join(f"<tr>{cells(r)}</tr>" for r in rows)
            flat += [list(r) for r in rows]
        est = lambda w, cc=cc, flat=flat, k=len(labelled): 12.5 + _table_height(cc, flat, w, subrows=k)
    markup = (f'<div class="tourney"><div class="tourney-head">{name} <span>· {where} · {dates}</span></div>'
              f'<table class="board">{_colgroup(cc)}{h}{rr}</table></div>')
    return _block(markup, est)


BOARD_INNER_PT = 7.5 * 72 - 2 * (5 + 1.5)          # full-width .box, inside padding and border
SPLIT_GAP_PT = 12.0


def board_split(left, right, notes=(), ratio="auto", width_pt=BOARD_INNER_PT):
    """Two halves of a full-width board, plus the box notes (A2).

    left / right   lists of tourney() blocks, already in the reading order wanted.
    notes          HTML strings (use ty()); each is placed under the SHORTER half so it fills the
                   hole beside the taller table at half the line length, instead of running the
                   full width under both. A note only stays full width when that makes the box
                   shorter.
    ratio          "auto" tries 50/50, 45/55, 40/60 and 3:5 (and their mirrors) and keeps the split
                   that gives the shortest box, then the smallest hole (width follows content,
                   §10). No half goes under 3/8 of the box: narrower than that, every
                   Time/Event/name row wraps. Pass e.g. (40, 60) to pin it.
    Returns (markup_for_inside_the_box, info). Heights are estimates; render.py measures the
    result and flags a hole over 0.5in."""
    ratios = ([(50, 50), (45, 55), (55, 45), (40, 60), (60, 40), (3, 5), (5, 3)]
              if ratio == "auto" else [tuple(ratio)])
    best = None
    notes = list(notes)
    for ri, (a, b) in enumerate(ratios):
        wl = (width_pt - SPLIT_GAP_PT) * a / (a + b); wr = (width_pt - SPLIT_GAP_PT) - wl
        hl = sum(x.height(wl) for x in left) + 9 * (len(left) - 1)
        hr = sum(x.height(wr) for x in right) + 9 * (len(right) - 1)
        for code in range(3 ** len(notes)):
            where, c = [], code
            for _ in notes:
                where.append("LRF"[c % 3]); c //= 3
            L, R, F = hl, hr, 0.0
            for nt, wh in zip(notes, where):
                if wh == "L": L += est_lines(nt, wl) * LINE + 5
                elif wh == "R": R += est_lines(nt, wr) * LINE + 5
                else: F += est_lines(nt, width_pt) * LINE + 3
            total = max(L, R) + F
            key = (round(total / 6), round(abs(L - R) / 6), ri, where.count("F"))
            if best is None or key < best[0]:
                best = (key, (a, b), where, L, R, F)
    _, (a, b), where, L, R, F = best
    def half(blocks, side):
        inner = "\n".join(blocks) + "".join(f'\n<p class="boxnote">{nt}</p>' for nt, wh in zip(notes, where) if wh == side)
        return inner
    style = "" if a == b else f' style="flex:{a}"'
    style_r = "" if a == b else f' style="flex:{b}"'
    markup = (f'<div class="board-split" data-balance="board">\n<div{style}>\n{half(left, "L")}\n</div>\n'
              f'<div{style_r}>\n{half(right, "R")}\n</div>\n</div>'
              + "".join(f'\n<p class="boxnote">{nt}</p>' for nt, wh in zip(notes, where) if wh == "F"))
    info = {"ratio": (a, b), "notes": where, "est_left_in": round(L / 72, 2), "est_right_in": round(R / 72, 2)}
    return markup, info


def box(title, inner, note=None, cls=""):
    n = f'<p class="boxnote">{note}</p>' if note else ""
    return f'<div class="box{(" " + cls) if cls else ""}"><div class="boxtitle">{ty(title)}</div>{inner}{n}</div>'


def box_pair(a, b):
    """Two small boxes side by side as half-width boxes (A3). Use when each has too few rows to
    earn the full width of a span2 on its own."""
    return f'<div class="box-pair" data-balance="boxes">{a}{b}</div>'


# ----------------------------------------------------------------- prose pieces
def piece(head, body_html, kicker=None, cls="rail-block", level=2, extra=""):
    """Kicker (optional) + headline + body. Returned as a dict so stack() can manage kickers."""
    return {"kicker": kicker, "head": head, "body": body_html, "cls": cls, "level": level, "extra": extra}


def render_piece(p, show_kicker=True):
    k = f'<div class="rail-title">{ty(p["kicker"])}</div>' if (p["kicker"] and show_kicker) else ""
    h = f'<h{p["level"]} class="head">{ty(p["head"])}</h{p["level"]}>' if p["head"] else ""
    return f'<div class="{p["cls"]}">{k}{h}{p["body"]}{p["extra"]}</div>'


def stack(*items):
    """Join pieces and ready-made HTML in reading order. When two ADJACENT pieces carry the same
    kicker it prints once, over the first (A4)."""
    out, prev = [], None
    for it in items:
        if isinstance(it, dict):
            out.append(render_piece(it, show_kicker=(it["kicker"] != prev)))
            prev = it["kicker"]
        else:
            out.append(it); prev = None
    return "\n".join(out)


def textcols(inner, n=2):
    """Prose in n ruled newspaper columns under one headline (browser balances the columns)."""
    return f'<div class="textcols n{n}" data-balance="text">{inner}</div>'


def split(*cols, widths=None):
    """Side-by-side prose columns that are not thirds. Always ruled (A12)."""
    widths = widths or [1] * len(cols)
    return ('<div class="split" data-balance="split">'
            + "".join(f'<div style="flex:{w}">{c}</div>' for c, w in zip(cols, widths)) + "</div>")


# ----------------------------------------------------------------- photos and flexible art
# Placement numbers and photo_span() live in art.py so the fitter and the composer share them.
from art import (  # noqa: E402
    PHOTO_CEILING_IN, COL1_IN, COL2_IN, PHOTO_MIN_DPI, MIN_PRINT_DPI,
    photo_span, art_markup, load_art_manifest, validate_asset, ArtError,
)


def art(asset, src=None, credit=None):
    """Flexible art slot for the fitter. `asset` is one entry from recipe/art.json.

    The printed credit, if any, is the same one-line rule as photo(). Full attributions
    should go through credit_line() first. Layout never crops."""
    cred = ""
    if credit:
        cred = f'<p class="credit">{html.escape(check_credit(credit), quote=False)}</p>'
    return art_markup(asset, src=src, credit_html=cred)


_CREDIT_BAD = re.compile(r"\.(jpe?g|png|tiff?)\b|https?://|www\.|\w+\.(org|com|net)/|File:", re.I)


def credit_line(full):
    """One short credit line from a full attribution (A6; SECTIONS-MENU: author / source, license
    with version, "(cropped)" if changed; no file names, no URLs). The full attribution, with the
    title and URLs, stays in the issue's sources.json and on the web archive.

      'Photo: © A / Wikimedia Commons, “X.jpg”, CC BY 2.5 (creativecommons.org/…). Source: …. Cropped.'
        -> 'Photo: © A / Wikimedia Commons, CC BY 2.5 (cropped)'"""
    s = full.strip()
    cropped = bool(re.search(r"\bcropped\b", s, re.I))
    s = re.sub(r"\s*Source:.*?(?=(\bCropped\b|$))", " ", s, flags=re.I | re.S)
    s = re.sub(r"\(?\bcropped\b\)?\.?", "", s, flags=re.I)
    s = re.sub(r",?\s*[“\"][^”\"]*\.(jpe?g|png|tiff?)[”\"]", "", s, flags=re.I)        # quoted file name
    s = re.sub(r"\s*\((?:https?://)?[\w.-]+\.(?:org|com|net)[^)]*\)", "", s)           # (url)
    s = re.sub(r"\s+", " ", s).strip().rstrip(".,; ")
    if cropped:
        s += " (cropped)"
    return s


def check_credit(text):
    if _CREDIT_BAD.search(text) or "/wiki/" in text:
        raise SystemExit(f"compose FAIL: photo credit must be one short line with no file name or URL: {text!r}")
    if len(text) > 90:
        warn(f"photo credit is {len(text)} characters; the rule is one short line: {text!r}")
    return text


def photo(src, alt, caption, credit=None, cls="photo"):
    c = f'<p class="credit">{html.escape(check_credit(credit), quote=False)}</p>' if credit else ""
    return (f'<div class="{cls}"><img src="{src}" alt="{html.escape(alt)}">'
            f'<p class="caption">{ty(caption)}</p>{c}</div>')


# ----------------------------------------------------------------- page furniture
def masthead():
    fl = load("flank-quotes.json")
    return ('  <div class="masthead">\n'
            f'    <div class="flank left">{fl["left_flank_fixed"]}</div>\n'
            '    <img src="../../masthead001.png" alt="The En Garde Gazette — The Elite Fencers Club Weekly">\n'
            f'    <div class="flank right">{fl["right_flank_default"]}</div>\n'
            '  </div>')


def dateline(edition, meta, first=True):
    st = "" if first else ' style="margin-top:0;"'
    return (f'  <div class="dateline"{st}>\n    <div class="edition">{edition}</div>\n'
            f'    <div class="meta">{meta}</div>\n  </div>')


def footer(no):
    return ('  <div class="footer">\n'
            f'    <span>En Garde Gazette · Issue No. {no}</span>\n'
            '    <span class="foot-archive">Past issues · newsletter.teamremco.org</span>\n'
            '    <span>For fun only — facts aren’t guaranteed accurate.</span>\n'
            '  </div>')


def cols3(*cols, span2_first=True):
    """The Template A row: a 2-column span plus a rail (or three equal columns)."""
    out = []
    for i, c in enumerate(cols):
        cls = "c span2" if (span2_first and i == 0 and len(cols) == 2) else "c"
        out.append(f'<div class="{cls}">\n{c}\n</div>')
    return '<div class="cols3 ruled" data-balance="columns">\n' + "\n".join(out) + "\n</div>"


def page(inner, cls=""):
    return f'<div class="page{(" " + cls) if cls else ""}">\n{inner}\n</div>'


def document(title, pages, extra_css="", author="Nico's Dad"):
    return ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<title>{title}</title>\n<meta name="author" content="{html.escape(author)}">\n'
            f'<style>\n{base_css()}{extra_css}</style>\n</head>\n<body>\n\n'
            + "\n\n".join(pages) + "\n\n</body>\n</html>\n")


def check_issue(doc):
    """Compose-time checks that warn (they never rewrite approved copy)."""
    text = plain(re.sub(r"<style>.*?</style>", "", doc, flags=re.S))
    a = len(re.findall(r"\bépée\b", text)); b = len(re.findall(r"\bepee\b", text))     # lowercase = running text
    if a and b:
        warn(f"weapon spelled two ways in one issue: 'épée' x{a}, 'epee' x{b} (A9: lock one in VOCABULARY.md)")
    for m in re.finditer(r'<p class="credit">(.*?)</p>', doc, flags=re.S):
        text = plain(m.group(1))
        try:
            check_credit(text)
        except SystemExit as e:
            # Do not fail a compose that reprints a published long credit. New work
            # should use credit_line() / photo(), which still enforce the one-line rule.
            warn(str(e).replace("compose FAIL: ", ""))


def write_issue(issue_dir, doc, argv=None):
    """Write issues/<date>/issue.html. An issue whose issue.json says APPROVED is frozen:
    re-composing it needs --force (C1), so an old recipe cannot silently overwrite a published
    page. --out=PATH writes somewhere else instead."""
    argv = sys.argv if argv is None else argv
    check_issue(doc)
    out = next((a.split("=", 1)[1] for a in argv if a.startswith("--out=")), None)
    target = Path(out) if out else ROOT / issue_dir / "issue.html"
    meta = ROOT / issue_dir / "issue.json"
    if not out and meta.is_file() and "--force" not in argv:
        status = str(json.loads(meta.read_text(encoding="utf-8")).get("status", ""))
        if status.upper().startswith("APPROVED"):
            raise SystemExit(f"compose REFUSED: {issue_dir} is approved/published. "
                             "Use --out=PATH for a trial, or --force to overwrite issue.html.")
    target.write_text(doc, encoding="utf-8")
    print(f"ok: wrote {target}" + (f" ({len(WARNINGS)} warning(s))" if WARNINGS else ""))
