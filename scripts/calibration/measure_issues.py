#!/usr/bin/env python3
"""Measure the composed issues in headless Chrome (read-only): every content block's rectangle, words,
table rows and art, per page. Writes calibration/measured.json. Does not touch compose/ or the issues.

  python3 calibration/measure_issues.py            # Nos. 1-7 from issues/<date>/issue.html
Needs: playwright (python) + /usr/bin/google-chrome. The fit step (calibrate_fill.py) needs neither.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]  # repo root
ISSUES = [(1, "2026-10-08"), (2, "2026-10-13"), (3, "2026-10-19"), (4, "2026-10-26"), (5, "2026-11-03"),
          (6, "2026-11-11"), (7, "2026-11-17")]

JS = r"""
() => {
  const IN = 96, BLOCK = '.box,.rail-block,.photo,.slot-a,.slot-b,.lead,figure,.comic-wide,.art';
  const words = t => { t = (t || '').replace(/­/g, '').trim(); return t ? t.split(/\s+/).length : 0; };
  return [...document.querySelectorAll('.page')].map((pg, pi) => {
    const pr = pg.getBoundingClientRect();
    const rel = r => ({ x: +((r.left - pr.left) / IN).toFixed(3), y: +((r.top - pr.top) / IN).toFixed(3), w: +(r.width / IN).toFixed(3), h: +(r.height / IN).toFixed(3) });
    const area = el => [...el.getClientRects()].reduce((a, r) => a + r.width * r.height, 0) / IN / IN;
    const furn = {};
    for (const c of ['masthead', 'dateline', 'footer']) { const e = pg.querySelector(':scope > .' + c); if (e) furn[c] = rel(e.getBoundingClientRect()); }
    const blocks = [];
    function describe(els) {
      let l = 1e9, t = 1e9, r = -1e9, b = -1e9;
      const all = [];
      els.forEach(e => { const q = e.getBoundingClientRect(); if (!q.width || !q.height) return; l = Math.min(l, q.left); t = Math.min(t, q.top); r = Math.max(r, q.right); b = Math.max(b, q.bottom); all.push(e, ...e.querySelectorAll('*')); });
      if (r < l) return;
      const pick = sel => all.filter(e => e.matches(sel));
      const heads = pick('h1,h2,h3,h4').map(e => ({ tag: e.tagName.toLowerCase(), words: words(e.innerText), h: +(e.getBoundingClientRect().height / IN).toFixed(3), w: +(e.getBoundingClientRect().width / IN).toFixed(3) }));
      const tables = pick('table').map(e => ({ rows: e.querySelectorAll('tr').length, headRows: [...e.querySelectorAll('tr')].filter(x => x.querySelector('th') && !x.querySelector('td')).length,
        words: words(e.innerText), w: +(e.getBoundingClientRect().width / IN).toFixed(3), h: +(e.getBoundingClientRect().height / IN).toFixed(3) }));
      const titles = pick('.boxtitle,.rail-title,.tourney-head,.kicker').map(e => ({ cls: e.className, words: words(e.innerText), h: +(e.getBoundingClientRect().height / IN).toFixed(3) }));
      const imgs = pick('img').map(e => ({ nw: e.naturalWidth, nh: e.naturalHeight, w: +(e.getBoundingClientRect().width / IN).toFixed(3), h: +(e.getBoundingClientRect().height / IN).toFixed(3) }));
      const inTable = e => !!e.closest('table');
      const ps = pick('p,li,.boxnote,.dek,.q,.a').filter(e => !inTable(e) && !e.querySelector('p,li'));
      const cap = ps.filter(e => e.matches('.caption,.credit'));
      const body = ps.filter(e => !e.matches('.caption,.credit'));
      const sum = (xs, f) => +xs.reduce((a, x) => a + f(x), 0).toFixed(3);
      const first = els[0], txt = (pick('h1,h2,h3,.boxtitle,.rail-title')[0] || first).innerText || '';
      blocks.push({ page: pi + 1, cls: els.map(e => e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).trim().replace(/\s+/g, '.') : '')).slice(0, 3).join(' + '),
        parent: (first.parentElement.className || first.parentElement.tagName) + (first.parentElement.getAttribute('style') ? '[' + first.parentElement.getAttribute('style') + ']' : ''),
        label: txt.replace(/\s+/g, ' ').trim().slice(0, 60), rect: rel({ left: l, top: t, width: r - l, height: b - t }),
        heads, tables, titles, imgs, bodyWords: sum(body, e => words(e.innerText)), bodyArea: sum(body, area), bodyWidth: body.length ? +(Math.max(...body.map(e => (e.getClientRects()[0] || { width: 0 }).width)) / IN).toFixed(3) : 0,
        capWords: sum(cap, e => words(e.innerText)), capArea: sum(cap, area), totalWords: sum(els, e => words(e.innerText)) });
    }
    function visit(el) {
      let run = [];
      const flush = () => { if (run.length) { describe(run); run = []; } };
      for (const ch of el.children) {
        if (ch.matches('.masthead,.dateline,.footer,style,script')) continue;
        if (ch.matches(BLOCK)) { flush(); describe([ch]); }
        else if (ch.querySelector(BLOCK)) { flush(); visit(ch); }
        else { if (ch.matches('h1,h2,h3,.head,.rail-title,.kicker') && run.some(e => e.matches('p,table,ul,.textcols'))) flush(); run.push(ch); }
      }
      flush();
    }
    visit(pg);
    return { page: pi + 1, pageRect: { w: +(pr.width / IN).toFixed(3), h: +(pr.height / IN).toFixed(3) }, furn, blocks };
  });
}
"""


APPLY_FIT = r"""
(decs) => decs.forEach(({ id, cand }) => {   // same steps as compose/fit.js apply()
  const el = document.querySelector('[data-art="' + CSS.escape(id) + '"]'); if (!el) return;
  const page = el.closest('.page'); if (page) page.classList.add('fit');
  if (el.parentElement && !el.parentElement.classList.contains('page')) el.parentElement.style.display = 'flow-root';
  el.classList.remove('art--float', 'art--gutter');
  if (cand.mode === 'stack') { el.style.width = '100%'; el.style.setProperty('--art-w', '100%'); el.style.marginLeft = '0'; el.style.marginRight = '0'; }
  else if (cand.mode === 'float') { el.classList.add('art--float'); el.style.width = cand.width + 'in'; el.style.setProperty('--art-w', cand.width + 'in'); el.style.cssFloat = 'left'; el.style.marginRight = '9pt'; }
  else if (cand.mode === 'gutter') { el.classList.add('art--gutter'); el.style.width = cand.width + 'in'; el.style.setProperty('--art-w', cand.width + 'in'); el.style.marginLeft = '0'; el.style.marginRight = 'auto'; }
})
"""


def main() -> None:
    from playwright.sync_api import sync_playwright
    out = {"issues": []}
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--disable-gpu"])
        for number, date in ISSUES:
            src = REPO / "issues" / date / "issue.html"
            pg = br.new_page(viewport={"width": 1100, "height": 1400})
            pg.emulate_media(media="print")
            pg.goto(src.as_uri())
            pg.wait_for_load_state("load")
            pg.evaluate("document.fonts.ready.then(() => 1)")
            fit = src.parent / "art-fit.json"
            if fit.is_file():  # replay the art-fit decisions render.py applied at PDF time (static issue.html is unfitted)
                decs = [{"id": d["id"], "cand": d["cand"]} for d in json.loads(fit.read_text(encoding="utf-8")).get("decisions", []) if d.get("cand")]
                pg.evaluate(APPLY_FIT, decs)
            pages = pg.evaluate(JS)
            meta = json.loads((src.parent / "issue.json").read_text(encoding="utf-8")) if (src.parent / "issue.json").is_file() else {}
            out["issues"].append({"number": number, "date": date, "pages": pages,
                                  "instruments": meta.get("instruments") or meta.get("fill"), "words": meta.get("words"),
                                  "status": meta.get("status")})
            pg.close()
            print(f"No. {number} {date}: " + ", ".join(f"p{p['page']} {len(p['blocks'])} blocks, page {p['pageRect']['h']}in" for p in pages))
        br.close()
    (HERE / "measured.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", HERE / "measured.json")


if __name__ == "__main__":
    sys.exit(main())
