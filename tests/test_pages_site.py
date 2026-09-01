"""Regression guard for the deployed (privacy-filtered) Pages site.

The GitHub Pages deploy does not publish the raw repo — it runs
``scripts/build_pages_site.py`` to copy a privacy-filtered subset into ``_site``.
A multi-page document is only fully viewable if EVERY referenced evidence page
(``digital_file`` + ``additional_pages``) is copied; a build that ships only the
primary scan leaves pages 2+ as broken images in the reader. This test builds the
site into a temp dir and asserts no publishable record is missing a page.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

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


class PagesSiteEvidenceTest(unittest.TestCase):
    def test_publishable_multipage_documents_ship_every_page(self) -> None:
        people = _load_dir(ROOT / "data" / "people")
        living = {p["id"] for p in people if p.get("privacy") == "living"}

        with tempfile.TemporaryDirectory() as tmp:
            original = build_pages_site.OUTPUT
            build_pages_site.OUTPUT = Path(tmp) / "_site"
            try:
                build_pages_site.main()
                site = build_pages_site.OUTPUT

                missing: list[str] = []
                checked_pages = 0
                # Sources (keyed by linked_people) and FANs (keyed by participants);
                # a record is published with its scans only when no living person is named.
                specs = [
                    (ROOT / "data" / "sources", lambda r: r.get("linked_people") or []),
                    (
                        ROOT / "data" / "fan",
                        lambda r: [
                            p.get("person_id")
                            for p in (r.get("participants") or [])
                            if isinstance(p, dict)
                        ],
                    ),
                ]
                for directory, linked_of in specs:
                    for rec in _load_dir(directory):
                        if any(pid in living for pid in linked_of(rec)):
                            continue  # living-linked: intentionally no scan deployed
                        refs = [rec.get("digital_file"), *(rec.get("additional_pages") or [])]
                        for ref in refs:
                            path = ref.get("path") if isinstance(ref, dict) else None
                            if isinstance(path, str) and path.startswith("evidence/"):
                                checked_pages += 1
                                if not (site / path).exists():
                                    missing.append(f"{rec.get('id')}: {path}")

                self.assertGreater(checked_pages, 0, "no evidence pages were checked")
                self.assertEqual(
                    missing,
                    [],
                    "deployed Pages site is missing evidence pages (multi-page docs "
                    f"would show only page 1): {missing}",
                )
            finally:
                build_pages_site.OUTPUT = original


if __name__ == "__main__":
    unittest.main()
