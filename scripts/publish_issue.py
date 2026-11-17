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
  3b. Refresh scripts/section-history.json (scripts/build_section_history.py): which registry section ran in
     which published issue. The budget page shows it; "published" means "listed in site/issues.json".
  4. Sync site/ -> docs/ (GitHub Pages source), minus REPORT.md and tests/. Builds docs.new
     first and swaps it in, so docs/ is never left empty.

  5. Stamp a final PDF /Title (and the issues/<date>/issue.html <title>) on the
     way out, stripping any proof/version label left by the composer. Chrome
     printToPDF copies the HTML <title> into the PDF Info dictionary, so a proof
     rendered as "… (proof v3)" would otherwise ship that label. The published
     title follows No. 6's style: "En Garde Gazette — Vol. I No. N — Month D, YYYY".
     Page content is not re-rendered (pikepdf sets metadata only).

Then publish with git add/commit/push yourself.
"""
import argparse, glob, html, json, os, re, shutil, subprocess, sys, tempfile
from datetime import date as Date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE, DOCS = os.path.join(ROOT, 'site'), os.path.join(ROOT, 'docs')
EXCLUDE_FROM_DOCS = {'REPORT.md', 'tests'}


def die(msg):
    sys.exit('publish_issue: ' + msg)


# Proof labels that may ride in a composer's HTML <title> (and therefore the
# PDF Info /Title, which Chrome printToPDF copies from that tag). "Vol." is
# not a match for v\d.
PROOF_LABEL_RE = re.compile(r'(?i)\bproof\b|\bv\d+\b')


def published_pdf_title(number, date, volume='I'):
    """Canonical published title, matching No. 6: 'En Garde Gazette — Vol. I No. 6 — November 11, 2026'."""
    if isinstance(date, str):
        date = Date.fromisoformat(date)
    return f'En Garde Gazette — Vol. {volume} No. {int(number)} — {date.strftime("%B")} {date.day}, {date.year}'


def title_has_proof_label(title):
    """True if a title still carries a proof or vN version label."""
    return bool(PROOF_LABEL_RE.search(title or ''))


def pdf_info_title(path):
    """The PDF Info /Title as pdfinfo prints it, or '' if none."""
    out = subprocess.run(['pdfinfo', path], capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        if line.startswith('Title:'):
            return line.split(':', 1)[1].strip()
    return ''


def set_pdf_title(path, title):
    """Set the PDF Info /Title with pikepdf. Returns True if the file changed.

    Page streams are left alone; only the document Info dictionary is updated.
    No-op (and no rewrite) when the title is already exactly `title`.
    """
    try:
        import pikepdf
    except ImportError as e:
        die('pikepdf is required to stamp a published PDF title (pip install pikepdf)')
        raise e
    with pikepdf.open(path) as pdf:
        current = str(pdf.docinfo.get('/Title') or '')
        if current == title:
            return False
        pdf.docinfo['/Title'] = title
        tmp = path + '.title-tmp'
        try:
            pdf.save(tmp)
        except Exception:
            if os.path.exists(tmp):
                os.remove(tmp)
            raise
    os.replace(tmp, path)
    return True


def issue_volume(d):
    ij = os.path.join(ROOT, 'issues', d, 'issue.json')
    if os.path.exists(ij):
        with open(ij, encoding='utf-8') as f:
            j = json.load(f)
        return j.get('volume') or j.get('vol') or 'I'
    return 'I'


def finalize_issue_html_title(d, title):
    """Set issues/<date>/issue.html <title> to the published title. Returns True if changed."""
    path = os.path.join(ROOT, 'issues', d, 'issue.html')
    if not os.path.exists(path):
        return False
    with open(path, encoding='utf-8') as f:
        text = f.read()
    new, n = re.subn(
        r'(<title>)(.*?)(</title>)',
        lambda m: m.group(1) + html.escape(title) + m.group(3),
        text,
        count=1,
        flags=re.I | re.S,
    )
    if n != 1 or new == text:
        return False
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new)
    return True


def finalize_published_title(d, n, dt, pdf):
    """Stamp the canonical title on the issue PDF and issue.html. Returns (title, pdf_changed)."""
    title = published_pdf_title(n, dt, issue_volume(d))
    pdf_changed = set_pdf_title(pdf, title)
    html_changed = finalize_issue_html_title(d, title)
    if pdf_changed:
        print(f'  stamped PDF title: {title}')
    else:
        print(f'  PDF title already final: {title}')
    if html_changed:
        print('  stripped proof/version label from issue.html <title>')
    return title, pdf_changed


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


def render_images(pdf, outdir, force, assume_up_to_date=False):
    from PIL import Image
    pages = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True, check=True).stdout).group(1))
    targets = [os.path.join(outdir, f'page-{p}{s}.webp') for p in range(1, pages + 1) for s in ('', '-1200')]
    if not force and assume_up_to_date and all(os.path.exists(t) for t in targets):
        print(f'  images left as-is ({pages} pages; PDF title/metadata only)')
        return pages
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


def update_section_history():
    """Refresh section-history.json now that this issue is listed in site/issues.json (= published).
    Never blocks a publish: a failure here is a warning, and the budget page derives its own copy anyway."""
    try:
        from pathlib import Path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import build_section_history as bsh
        changed, hist = bsh.update_record(Path(ROOT))
        print('  scripts/section-history.json ' + ('updated' if changed else 'unchanged') + f" ({len(hist['issues'])} published issues)")
    except Exception as exc:  # noqa: BLE001
        print(f'  warning: scripts/section-history.json not refreshed ({exc}); run scripts/build_section_history.py')


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
    _title, pdf_changed = finalize_published_title(d, n, dt, pdf)

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
    pages = render_images(pdf, outdir, a.force_images, assume_up_to_date=pdf_changed)

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
    update_section_history()
    sync_docs()
    print('Done. Next: git add site docs scripts/section-history.json && git commit && git push')


if __name__ == '__main__':
    main()
