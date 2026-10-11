"""The repository is public: guard what Git tracks (owner decision, 2026-10-11).

A living person's own document is held in the gitignored private store, and every
GEDCOM export is a local, private backup. These tests fail if either ever reaches
the index, if a record held privately still carries what belongs in the private
store, or if the scan of a record naming a living person is tracked. Fixtures
elsewhere stay synthetic; these tests read the real data only to check its shape,
never to print it.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STUB_FREE_FIELDS = ("transcription", "transcription_pt", "event_date", "event_place_text", "registration_date")


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
        # `private` alone would be the private repository's clone added as a gitlink.
        leaked = [path for path in self.tracked if path == "private" or path.startswith("private/")]
        self.assertEqual(leaked, [], f"private-store files are tracked: {leaked}")

    def test_gedcom_exports_are_never_tracked(self) -> None:
        exports = [
            path for path in self.tracked
            if path.startswith("export/") and path.endswith((".ged", ".gdz"))
        ]
        self.assertEqual(exports, [], f"GEDCOM backups are tracked: {exports}")

    def test_private_records_and_living_people_scans_stay_out_of_git(self) -> None:
        living = set()
        for path in (ROOT / "data" / "people").glob("*.yaml"):
            person = yaml.safe_load(path.read_text(encoding="utf-8"))
            if person.get("privacy") == "living":
                living.add(person["id"])
        tracked = set(self.tracked)
        problems: list[str] = []
        for path in sorted((ROOT / "data" / "sources").glob("*/*.yaml")):
            source = yaml.safe_load(path.read_text(encoding="utf-8"))
            held = source.get("held_privately") is True
            if held:
                problems += [f"{source['id']}: {field}" for field in STUB_FREE_FIELDS if field in source]
            if not held and not set(source.get("linked_people") or []) & living:
                continue
            for ref in [source.get("digital_file"), *(source.get("additional_pages") or [])]:
                scan = ref.get("path") if isinstance(ref, dict) else None
                if isinstance(scan, str) and (scan in tracked or not scan.startswith("private/")):
                    problems.append(f"{source['id']}: scan {scan}")
        self.assertEqual(problems, [], f"private material is tracked: {problems}")


if __name__ == "__main__":
    unittest.main()
