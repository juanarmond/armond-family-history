"""Enforce that the committed GEDCOM backup stays in step with the data.

`export/armond-family-history.ged` is a committed derived artefact. If structured
data changes and `make export` is not re-run, the backup drifts silently — nothing
used to catch it. This regenerates the GEDCOM from `data/` and compares, ignoring
only the two header lines that carry the export date (they change every day).
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from export_gedcom import build_gedcom  # noqa: E402

GEDCOM_PATH = PROJECT_ROOT / "export" / "armond-family-history.ged"
# Header-only volatile lines: `1 DATE <today>` and `2 VERS <YYYY.MM.DD>`.
_VOLATILE = re.compile(r"^(1 DATE |2 VERS \d{4}\.)")


def _stable_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if not _VOLATILE.match(line)]


class GedcomExportTests(unittest.TestCase):
    def test_committed_gedcom_matches_data(self) -> None:
        # Defaults mirror `make export` (7.0, hypotheses flagged, notes included).
        expected = build_gedcom(PROJECT_ROOT / "data")
        committed = GEDCOM_PATH.read_text(encoding="utf-8")
        self.assertEqual(
            _stable_lines(expected),
            _stable_lines(committed),
            "export/armond-family-history.ged is stale; "
            "regenerate it with `make export`.",
        )


if __name__ == "__main__":
    unittest.main()
