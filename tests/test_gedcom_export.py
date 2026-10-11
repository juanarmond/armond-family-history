"""The full-backup GEDCOM is a local, private artefact (owner decision, 2026-10-11).

`export/armond-family-history.ged` carries living people and privately held records
in full, so it is never committed (`tests/test_public_surface.py` guards the index).
What remains checkable everywhere is that the export builds from `data/` and is
deterministic apart from the two header lines that carry the export date, so a
backup regenerated on the owner's machine is reproducible.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from export_gedcom import build_gedcom  # noqa: E402

# Header-only volatile lines: `1 DATE <today>` and `2 VERS <YYYY.MM.DD>`.
_VOLATILE = re.compile(r"^(1 DATE |2 VERS \d{4}\.)")


def _stable_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if not _VOLATILE.match(line)]


class GedcomExportTests(unittest.TestCase):
    def test_export_builds_deterministically_from_data(self) -> None:
        # Defaults mirror `make export` (7.0, hypotheses flagged, notes included).
        first = build_gedcom(PROJECT_ROOT / "data")
        second = build_gedcom(PROJECT_ROOT / "data")
        self.assertTrue(first.startswith("0 HEAD"))
        self.assertEqual(_stable_lines(first), _stable_lines(second))


if __name__ == "__main__":
    unittest.main()
