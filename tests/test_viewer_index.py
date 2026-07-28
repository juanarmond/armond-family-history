from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from build_viewer_index import build_index  # noqa: E402

INDEX_PATH = PROJECT_ROOT / "family-tree-viewer" / "entity-index.json"


class ViewerIndexTests(unittest.TestCase):
    """The static viewer trusts entity-index.json to enumerate every entity.

    If it drifts from the YAML files in data/, the viewer fails to load, so
    keep the committed index in lockstep with the canonical directories.
    """

    def test_committed_index_matches_data_directory(self) -> None:
        expected = build_index(PROJECT_ROOT / "data")
        committed = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            expected,
            committed,
            "family-tree-viewer/entity-index.json is stale; "
            "regenerate it with `python3 scripts/build_viewer_index.py`.",
        )


if __name__ == "__main__":
    unittest.main()
