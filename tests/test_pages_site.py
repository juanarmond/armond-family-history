"""Regression guard for the deployed (privacy-filtered) Pages site.

The GitHub Pages deploy does not publish the raw repo — it runs
``scripts/build_pages_site.py`` to copy a privacy-filtered subset into ``_site``.
A multi-page document is only fully viewable if EVERY referenced evidence page
(``digital_file`` + ``additional_pages``) is copied; a build that ships only the
primary scan leaves pages 2+ as broken images in the reader. These tests build the
site once into a temp dir and assert no publishable record is missing a page, that a
multi-page PDF ships its page images (iOS draws only a PDF's first page), and that
withheld records ship nothing.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pypdfium2 as pdfium
import yaml

from scripts import build_pages_site

ROOT = Path(__file__).resolve().parent.parent


def _load_dir(directory: Path) -> list[dict]:
    out = []
    for path in directory.rglob("*.yaml"):
        rec = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(rec, dict) and rec.get("id"):
            out.append(rec)
    return out


def _published(rec: dict, living: set[str]) -> bool:
    linked = rec.get("linked_people") or [
        p.get("person_id") for p in (rec.get("participants") or []) if isinstance(p, dict)
    ]
    return not any(pid in living for pid in linked) and rec.get("withhold_from_site") is not True


class PagesSiteEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls._original = build_pages_site.OUTPUT
        build_pages_site.OUTPUT = Path(cls._tmp.name) / "_site"
        build_pages_site.main()
        cls.site = build_pages_site.OUTPUT

    @classmethod
    def tearDownClass(cls) -> None:
        build_pages_site.OUTPUT = cls._original
        cls._tmp.cleanup()

    def test_publishable_multipage_documents_ship_every_page(self) -> None:
        living = {p["id"] for p in _load_dir(ROOT / "data" / "people") if p.get("privacy") == "living"}
        missing: list[str] = []
        checked_pages = 0
        # A record is published with its scans only when it names no living person and is
        # not withheld.
        for directory in (ROOT / "data" / "sources", ROOT / "data" / "fan"):
            for rec in _load_dir(directory):
                if not _published(rec, living):
                    continue
                for ref in [rec.get("digital_file"), *(rec.get("additional_pages") or [])]:
                    path = ref.get("path") if isinstance(ref, dict) else None
                    if isinstance(path, str) and path.startswith("evidence/"):
                        checked_pages += 1
                        if not (self.site / path).exists():
                            missing.append(f"{rec.get('id')}: {path}")

        self.assertGreater(checked_pages, 0, "no evidence pages were checked")
        self.assertEqual(
            missing,
            [],
            "deployed Pages site is missing evidence pages (multi-page docs "
            f"would show only page 1): {missing}",
        )

    def test_multipage_pdfs_ship_their_page_images(self) -> None:
        living = {p["id"] for p in _load_dir(ROOT / "data" / "people") if p.get("privacy") == "living"}
        problems: list[str] = []
        checked = 0
        for directory in (ROOT / "data" / "sources", ROOT / "data" / "fan"):
            for rec in _load_dir(directory):
                if not _published(rec, living):
                    continue
                published = next(self.site.rglob(f"data/**/{rec['id']}.yaml"))
                site_rec = yaml.safe_load(published.read_text(encoding="utf-8"))
                for ref in [site_rec.get("digital_file"), *(site_rec.get("additional_pages") or [])]:
                    path = ref.get("path") if isinstance(ref, dict) else None
                    if not isinstance(path, str) or not path.lower().endswith(".pdf"):
                        continue
                    pdf = pdfium.PdfDocument(ROOT / path)
                    total = len(pdf)
                    pdf.close()
                    listed = [spec["page"] for spec in ref.get("show_pages") or []]
                    expected = listed or (list(range(1, total + 1)) if total > 1 else [])
                    rendered = ref.get("rendered_pages") or []
                    if [page["page"] for page in rendered] != expected:
                        problems.append(f"{rec['id']}: {path} rendered {[p['page'] for p in rendered]}, expected {expected}")
                    problems += [
                        f"{rec['id']}: missing {page['path']}"
                        for page in rendered
                        if not (self.site / page["path"]).is_file()
                    ]
                    checked += bool(expected)
        self.assertGreater(checked, 0, "no multi-page PDF was checked")
        self.assertEqual(problems, [], f"multi-page PDFs would show only their first page on iOS: {problems}")

    def test_withheld_records_ship_no_scan_or_transcription(self) -> None:
        withheld = [
            rec
            for directory in (ROOT / "data" / "sources", ROOT / "data" / "fan")
            for rec in _load_dir(directory)
            if rec.get("withhold_from_site") is True
        ]
        leaked: list[str] = []
        for rec in withheld:
            for ref in [rec.get("digital_file"), *(rec.get("additional_pages") or [])]:
                path = ref.get("path") if isinstance(ref, dict) else None
                if isinstance(path, str) and (self.site / path).exists():
                    leaked.append(f"{rec['id']}: {path}")
            for published in self.site.rglob(f"{rec['id']}.yaml"):
                data = yaml.safe_load(published.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data.get("transcription"):
                    leaked.append(f"{rec['id']}: transcription")
        self.assertEqual(leaked, [], f"withheld records were published: {leaked}")


if __name__ == "__main__":
    unittest.main()
