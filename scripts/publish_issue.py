#!/usr/bin/env python3
"""Add (or refresh) one approved issue on the website. Does NOT commit or push.

Usage:
    python3 scripts/publish_issue.py 2026-10-19 [--headline "..."] [--force-images]

Steps (safe to re-run; same input -> same result):
  1. Copy issues/<date>/en-garde-gazette-no-<N>-<date>.pdf -> site/issues/<date>/
  2. Render page images from that PDF with pdftoppm at 220 dpi:
       page-<p>.webp (1870 px wide) and page-<p>-1200.webp (1200 px)
     Skipped when the images are already newer than the PDF (unless --force-images).
  3. Upsert the entry in site/issues.json (keyed by date), sorted newest first,
     so the newest issue lands on top of the desk.
  4. Sync site/ -> docs/ (GitHub Pages source), minus REPORT.md and tests/. Builds docs.new
     first and swaps it in, so docs/ is never left empty.

Then publish with git add/commit/push yourself.
"""
import argparse, glob, html, json, os, re, shutil, subprocess, sys, tempfile
from datetime import date as Date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE, DOCS = os.path.join(ROOT, 'site'), os.path.join(ROOT, 'docs')
EXCLUDE_FROM_DOCS = {'REPORT.md', 'tests'}


def die(msg):
    sys.exit('publish_issue: ' + msg)


def find_pdf(d):
    hits = sorted(glob.glob(os.path.join(ROOT, 'issues', d, f'en-garde-gazette-no-*-{d}.pdf')))
    if len(hits) != 1:
        die(f'expected exactly one issues/{d}/en-garde-gazette-no-<N>-{d}.pdf, found {len(hits)}')
    m = re.search(r'en-garde-gazette-no-(\d+)-', os.path.basename(hits[0]))
    return hits[0], int(m.group(1))


def issue_meta(d):
    """edition + headline from issues/<date>/issue.json and issue.html."""
    edition, headline = None, None
    ij = os.path.join(ROOT, 'issues', d, 'issue.json')
    if os.path.exists(ij):
        j = json.load(open(ij))
        edition = j.get('edition')
        if not edition and isinstance(j.get('dateline'), str):
            m = re.match(r'\s*([A-Za-z]+ Edition)', j['dateline'])
            edition = m and m.group(1)
    ih = os.path.join(ROOT, 'issues', d, 'issue.html')
    if os.path.exists(ih):
        m = re.search(r'<h1[^>]*class="[^"]*\bhead\b[^"]*"[^>]*>(.*?)</h1>', open(ih, encoding='utf-8').read(), re.S)
        if m:
            headline = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', m.group(1)))).strip()
    return edition, headline


def render_images(pdf, outdir, force):
    from PIL import Image
    pages = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True, check=True).stdout).group(1))
    targets = [os.path.join(outdir, f'page-{p}{s}.webp') for p in range(1, pages + 1) for s in ('', '-1200')]
    if not force and all(os.path.exists(t) and os.path.getmtime(t) >= os.path.getmtime(pdf) for t in targets):
        print(f'  images up to date ({pages} pages)')
        return pages
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['pdftoppm', '-r', '220', '-png', pdf, os.path.join(tmp, 'p')], check=True, stderr=subprocess.DEVNULL)
        for p in range(1, pages + 1):
            src = sorted(glob.glob(os.path.join(tmp, f'p-*{p}.png')), key=len)[0]
            im = Image.open(src).convert('RGB')
            if im.width != 1870:
                im = im.resize((1870, round(1870 * im.height / im.width)), Image.LANCZOS)
            im.save(os.path.join(outdir, f'page-{p}.webp'), quality=90)
            im.resize((1200, round(1200 * im.height / im.width)), Image.LANCZOS).save(os.path.join(outdir, f'page-{p}-1200.webp'), quality=88)
    print(f'  rendered {pages} pages -> page-N.webp (1870) + page-N-1200.webp')
    return pages


def write_issues_json(entries):
    entries.sort(key=lambda e: e['date'], reverse=True)
    body = ',\n'.join(' ' + json.dumps(e, ensure_ascii=False) for e in entries)
    new = '[\n' + body + '\n]\n'
    path = os.path.join(SITE, 'issues.json')
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    if old != new:
        open(path, 'w', encoding='utf-8').write(new)
        print('  issues.json updated')
    else:
        print('  issues.json unchanged')


def sync_docs():
    tmp = DOCS + '.new'
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.copytree(SITE, tmp, ignore=lambda d, names: [n for n in names if d == SITE and n in EXCLUDE_FROM_DOCS])
    for must in ('index.html', 'issues.json', 'CNAME', '.nojekyll'):
        if not os.path.exists(os.path.join(tmp, must)):
            shutil.rmtree(tmp); die(f'site/{must} missing; refusing to sync docs/')
    old = DOCS + '.old'
    shutil.rmtree(old, ignore_errors=True)
    if os.path.exists(DOCS):
        os.rename(DOCS, old)
    os.rename(tmp, DOCS)
    shutil.rmtree(old, ignore_errors=True)
    print('  docs/ synced from site/')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('date', help='issue folder date, YYYY-MM-DD')
    ap.add_argument('--headline', help='override the headline (default: first h1.head in issue.html)')
    ap.add_argument('--force-images', action='store_true')
    a = ap.parse_args()
    d = a.date
    try:
        dt = Date.fromisoformat(d)
    except ValueError:
        die('date must be YYYY-MM-DD')
    pdf, n = find_pdf(d)
    edition, headline = issue_meta(d)
    headline = a.headline or headline
    if not headline:
        die('no headline found; pass --headline')
    print(f'No. {n} ({d}): {headline}')

    outdir = os.path.join(SITE, 'issues', d)
    os.makedirs(outdir, exist_ok=True)
    dest = os.path.join(outdir, os.path.basename(pdf))
    if not os.path.exists(dest) or open(dest, 'rb').read() != open(pdf, 'rb').read():
        shutil.copy2(pdf, dest); print('  copied PDF')
    else:
        print('  PDF already current')
    for stale in glob.glob(os.path.join(outdir, '*.pdf')):
        if stale != dest:
            os.remove(stale); print('  removed stale', os.path.basename(stale))
    pages = render_images(pdf, outdir, a.force_images)

    path = os.path.join(SITE, 'issues.json')
    entries = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else []
    old = next((e for e in entries if e.get('date') == d), {})
    entry = {
        'number': n, 'date': d,
        'edition': edition or old.get('edition') or dt.strftime('%A') + ' Edition',
        'title': old.get('title') or f'En Garde Gazette No. {n}, {dt.strftime("%b")} {dt.day}, {dt.year}',
        'headline': headline,
        'pdf': f'issues/{d}/{os.path.basename(pdf)}',
        'pages': [f'issues/{d}/page-{p}.webp' for p in range(1, pages + 1)],
        'thumbs': [f'issues/{d}/page-{p}-1200.webp' for p in range(1, pages + 1)],
    }
    entries = [e for e in entries if e.get('date') != d] + [entry]
    write_issues_json(entries)
    sync_docs()
    print('Done. Next: git add site docs && git commit && git push')


if __name__ == '__main__':
    main()
