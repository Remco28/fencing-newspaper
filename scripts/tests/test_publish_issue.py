#!/usr/bin/env python3
"""Published PDFs must ship a clean title, with no proof or vN version label.

Chrome printToPDF copies the HTML <title> into the PDF Info /Title, so a proof
rendered as "… (proof v3)" would otherwise go out with that label. publish_issue.py
stamps the canonical title (No. 6's style) on publish.

Run: python3 scripts/tests/test_publish_issue.py
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import publish_issue as pub  # noqa: E402


def pdfinfo_title(path):
    return pub.pdf_info_title(str(path))


def page_pixel_hashes(path, dpi=50):
    """sha256 of each pdftoppm page, used to confirm a metadata stamp is not a re-render."""
    tmp = Path(tempfile.mkdtemp())
    try:
        subprocess.run(
            ["pdftoppm", "-r", str(dpi), "-png", str(path), str(tmp / "p")],
            check=True,
            stderr=subprocess.DEVNULL,
        )
        return tuple(
            hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(tmp.glob("p*.png"))
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class TitleFormat(unittest.TestCase):
    def test_matches_no_6_published_style(self):
        # No. 6 is the reference: already published with a clean title.
        want = "En Garde Gazette — Vol. I No. 6 — November 11, 2026"
        self.assertEqual(pub.published_pdf_title(6, "2026-11-11"), want)
        self.assertEqual(pdfinfo_title(REPO / "issues/2026-11-11/en-garde-gazette-no-6-2026-11-11.pdf"), want)

    def test_no_7_and_no_1_forms(self):
        self.assertEqual(
            pub.published_pdf_title(7, "2026-11-17"),
            "En Garde Gazette — Vol. I No. 7 — November 17, 2026",
        )
        self.assertEqual(
            pub.published_pdf_title(1, "2026-10-08"),
            "En Garde Gazette — Vol. I No. 1 — October 8, 2026",
        )

    def test_day_is_not_zero_padded(self):
        self.assertEqual(
            pub.published_pdf_title(5, "2026-11-03"),
            "En Garde Gazette — Vol. I No. 5 — November 3, 2026",
        )


class ProofLabel(unittest.TestCase):
    def test_flags_proof_and_version_labels(self):
        dirty = [
            "En Garde Gazette — Vol. I No. 7 — November 17, 2026 (proof v3)",
            "En Garde Gazette — Vol. I No. 1 — October 8, 2026 (PROOF v2)",
            "En Garde Gazette — Vol. I No. 7 — November 17, 2026 (Proof v3)",
            "something proof something",
            "Gazette v3",
        ]
        for t in dirty:
            self.assertTrue(pub.title_has_proof_label(t), t)

    def test_clean_title_and_volume_are_ok(self):
        clean = [
            "En Garde Gazette — Vol. I No. 7 — November 17, 2026",
            "En Garde Gazette — Vol. I No. 6 — November 11, 2026",
            "",
            None,
        ]
        for t in clean:
            self.assertFalse(pub.title_has_proof_label(t), t)


class StampTitle(unittest.TestCase):
    def test_set_pdf_title_rewrites_metadata_only(self):
        src = REPO / "issues/2026-10-13/en-garde-gazette-no-2-2026-10-13.pdf"
        tmp = Path(tempfile.mkdtemp()) / "sample.pdf"
        shutil.copy2(src, tmp)
        before_pages = page_pixel_hashes(tmp)
        before_title = pdfinfo_title(tmp)
        self.assertFalse(pub.title_has_proof_label(before_title))

        dirty = before_title + " (proof v3)"
        self.assertTrue(pub.set_pdf_title(str(tmp), dirty))
        self.assertEqual(pdfinfo_title(tmp), dirty)
        self.assertEqual(page_pixel_hashes(tmp), before_pages)

        clean = pub.published_pdf_title(2, "2026-10-13")
        self.assertTrue(pub.set_pdf_title(str(tmp), clean))
        self.assertEqual(pdfinfo_title(tmp), clean)
        self.assertFalse(pub.title_has_proof_label(pdfinfo_title(tmp)))
        self.assertEqual(page_pixel_hashes(tmp), before_pages)

        # Second stamp is a no-op: the file is not rewritten.
        digest = hashlib.sha256(tmp.read_bytes()).hexdigest()
        self.assertFalse(pub.set_pdf_title(str(tmp), clean))
        self.assertEqual(hashlib.sha256(tmp.read_bytes()).hexdigest(), digest)

    def test_finalize_issue_html_title(self):
        tmp = Path(tempfile.mkdtemp())
        issues = tmp / "issues" / "2026-11-17"
        issues.mkdir(parents=True)
        html = (
            "<html><head><title>En Garde Gazette — Vol. I No. 7 — "
            "November 17, 2026 (proof v3)</title></head><body>ok</body></html>\n"
        )
        (issues / "issue.html").write_text(html, encoding="utf-8")
        old_root = pub.ROOT
        try:
            pub.ROOT = str(tmp)
            want = pub.published_pdf_title(7, "2026-11-17")
            self.assertTrue(pub.finalize_issue_html_title("2026-11-17", want))
            got = (issues / "issue.html").read_text(encoding="utf-8")
            self.assertIn(f"<title>{want}</title>", got)
            self.assertNotIn("proof", got.lower())
            self.assertFalse(pub.finalize_issue_html_title("2026-11-17", want))
        finally:
            pub.ROOT = old_root
            shutil.rmtree(tmp, ignore_errors=True)


class PublishedPdfs(unittest.TestCase):
    """Every issue listed in site/issues.json, in issues/, site/, and docs/."""

    @classmethod
    def published_entries(cls):
        import json
        return json.loads((REPO / "site" / "issues.json").read_text(encoding="utf-8"))

    def _pdfs_for(self, entry):
        date, n = entry["date"], entry["number"]
        name = f"en-garde-gazette-no-{n}-{date}.pdf"
        return [
            ("issues", REPO / "issues" / date / name),
            ("site", REPO / "site" / "issues" / date / name),
            ("docs", REPO / "docs" / "issues" / date / name),
        ]

    def test_every_published_pdf_title_is_clean_and_canonical(self):
        failures = []
        for entry in self.published_entries():
            want = pub.published_pdf_title(entry["number"], entry["date"])
            for where, path in self._pdfs_for(entry):
                if not path.is_file():
                    failures.append(f"missing {where}: {path}")
                    continue
                title = pdfinfo_title(path)
                if pub.title_has_proof_label(title):
                    failures.append(f"{where} {path.name}: proof/version label in title {title!r}")
                if title != want:
                    failures.append(f"{where} {path.name}: title {title!r} != {want!r}")
        self.assertEqual(failures, [])

    def test_published_issue_html_titles_are_clean(self):
        import re
        failures = []
        for entry in self.published_entries():
            path = REPO / "issues" / entry["date"] / "issue.html"
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            m = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
            title = m.group(1) if m else ""
            want = pub.published_pdf_title(entry["number"], entry["date"])
            if pub.title_has_proof_label(title) or title != want:
                failures.append(f"{path}: <title> {title!r} != {want!r}")
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
