"""The repository is public: guard what Git tracks (owner decision, 2026-10-11).

Records naming living people are held in the gitignored private store, and every
GEDCOM export is a local, private backup. These tests fail if either ever reaches
the index, and if a source naming a living person still carries what belongs in
the private store. Fixtures elsewhere stay synthetic; these tests read the real
data only to check its shape, never to print it.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
HELD_PRIVATELY = ("transcription", "transcription_pt", "event_date", "event_place_text", "registration_date")


def tracked_paths() -> list[str] | None:
    try:
        output = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
        ).stdout.decode("utf-8")
    except (OSError, subprocess.CalledProcessError):
        return None
    return [path for path in output.split("\0") if path]


class PublicSurfaceTest(unittest.TestCase):
    def setUp(self) -> None:
        paths = tracked_paths()
        if paths is None:
            self.skipTest("not a Git checkout")
        self.tracked = paths

    def test_private_store_is_never_tracked(self) -> None:
        leaked = [path for path in self.tracked if path.startswith("private/")]
        self.assertEqual(leaked, [], f"private-store files are tracked: {leaked}")

    def test_gedcom_exports_are_never_tracked(self) -> None:
        exports = [
            path for path in self.tracked
            if path.startswith("export/") and path.endswith((".ged", ".gdz"))
        ]
        self.assertEqual(exports, [], f"GEDCOM backups are tracked: {exports}")

    def test_records_naming_living_people_are_held_privately(self) -> None:
        living = set()
        for path in (ROOT / "data" / "people").glob("*.yaml"):
            person = yaml.safe_load(path.read_text(encoding="utf-8"))
            if person.get("privacy") == "living":
                living.add(person["id"])
        tracked = set(self.tracked)
        problems: list[str] = []
        for path in sorted((ROOT / "data" / "sources").glob("*/*.yaml")):
            source = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not set(source.get("linked_people") or []) & living:
                continue
            problems += [f"{source['id']}: {field}" for field in HELD_PRIVATELY if field in source]
            for ref in [source.get("digital_file"), *(source.get("additional_pages") or [])]:
                scan = ref.get("path") if isinstance(ref, dict) else None
                if isinstance(scan, str) and (scan in tracked or not scan.startswith("private/")):
                    problems.append(f"{source['id']}: scan {scan}")
        self.assertEqual(problems, [], f"records naming living people are not held privately: {problems}")


if __name__ == "__main__":
    unittest.main()
