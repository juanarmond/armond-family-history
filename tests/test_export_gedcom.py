"""Tests for the GEDCOM exporter and GEDZIP bundle.

The fixture is a small self-contained temp repository (not the live data) so the
tests stay deterministic and can exercise paths the real data may not currently
contain (e.g. a hypothesis- or rejected-level edge, and an on-disk scan).
"""

from __future__ import annotations

import re
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml

from scripts.export_gedcom import SUPPORTED_VERSIONS, build_gedcom, write_gedzip


TRANSCRIPTION = "sob No 132 encontra-se o assento"
SCAN_PATH = "evidence/civil/CIV-0002-scan.jpg"


def _write(root: Path, directory: str, entity: dict) -> None:
    target = root / "data" / directory
    target.mkdir(parents=True, exist_ok=True)
    (target / f"{entity['id']}.yaml").write_text(
        yaml.safe_dump(entity, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


class GedcomFixture:
    """A minimal repository exercising every export branch."""

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

        # A real (dummy) scan on disk so the GEDZIP bundle has something to pack.
        scan = self.root / SCAN_PATH
        scan.parent.mkdir(parents=True, exist_ok=True)
        scan.write_bytes(b"\xff\xd8\xff\xe0 fake jpeg bytes")

        _write(self.root, "places", {
            "id": "PL-0001",
            "preferred_name": "Carangola, Minas Gerais, Brazil",
            "coordinates": {"latitude": -20.73, "longitude": -42.03},
        })
        _write(self.root, "sources/civil", {
            "id": "CIV-0001",
            "title": "Civil birth registration of the child",
            "abstract": "Curated summary.",
            "record_category": "civil_registration",
            "source_form": "original",
            "information_quality": "primary",
            "evidence_type": "direct",
            "repository": {"name": "Cartorio de Carangola", "book": "2", "page": "142"},
            "private": False,
        })
        _write(self.root, "sources/civil", {
            "id": "CIV-0002",
            "title": "Record with a scan",
            "abstract": "Curated summary.",
            "record_category": "civil_registration",
            "source_form": "derivative",
            "information_quality": "mixed",
            "evidence_type": "direct",
            "repository": {"name": "Cartorio de Carangola", "repository_path": SCAN_PATH},
            "transcription": TRANSCRIPTION,
            "digital_file": {"path": SCAN_PATH, "sha256": "a" * 64},
            "private": True,
        })

        _write(self.root, "people", {
            "id": "P-0001", "preferred_name": "Juan Carlos Muniz Armond",
            "privacy": "living", "sex": "male",
            "event_ids": ["E-0004"], "family_ids": ["F-0001"], "notes": [],
        })
        _write(self.root, "people", {
            "id": "P-0002", "preferred_name": "Aristao Ferreira Armond",
            "privacy": "deceased", "sex": "male",
            "event_ids": ["E-0003"], "family_ids": ["F-0001"], "notes": [],
        })
        _write(self.root, "people", {
            "id": "P-0003", "preferred_name": "Liliosa Paz Armond",
            "privacy": "deceased", "sex": "female",
            "event_ids": ["E-0003", "E-0005"], "family_ids": ["F-0001"], "notes": [],
        })
        _write(self.root, "people", {
            "id": "P-0004", "preferred_name": "Geraldo Paz Armond",
            "privacy": "deceased", "sex": "male",
            "occupations": [{"value": "farmer", "source_ids": ["CIV-0001"]}],
            "event_ids": ["E-0001", "E-0002"], "family_ids": ["F-0001"],
            "notes": [{"text": "A modelled child.", "source_ids": ["CIV-0001"]}],
        })

        _write(self.root, "families", {
            "id": "F-0001",
            "partners": [
                {"person_id": "P-0002", "role": "spouse"},
                {"person_id": "P-0003", "role": "spouse"},
            ],
            "partner_relationship": {"status": "confirmed", "source_ids": ["CIV-0001"]},
            "children": [
                {"person_id": "P-0001", "parent_relationships": [
                    {"parent_id": "P-0002", "status": "confirmed",
                     "source_ids": ["CIV-0002"]}]},
                {"person_id": "P-0004", "parent_relationships": [
                    {"parent_id": "P-0002", "status": "confirmed",
                     "source_ids": ["CIV-0001"]}]},
            ],
            "documented_children": [
                {"name": "Marfiza Ferreira Armond", "lifespan": "1873-1962",
                 "source_ids": ["CIV-0001"]},
            ],
            "event_ids": ["E-0003"], "notes": [],
        })

        _write(self.root, "events", {
            "id": "E-0001", "event_type": "birth",
            "date": {"kind": "exact", "value": "1915-01-30"},
            "place_id": "PL-0001",
            "participants": [{"person_id": "P-0004", "role": "principal"},
                             {"person_id": "P-0002", "role": "parent"}],
            "status": "confirmed", "source_ids": ["CIV-0001"], "notes": [],
        })
        _write(self.root, "events", {
            "id": "E-0002", "event_type": "death",
            "date": {"kind": "approximate", "text": "about 1980", "earliest": 1980},
            "place_text": "Unknown",
            "participants": [{"person_id": "P-0004", "role": "principal"}],
            "status": "hypothesis", "source_ids": ["CIV-0001"], "notes": [],
        })
        _write(self.root, "events", {
            "id": "E-0003", "event_type": "marriage",
            "date": {"kind": "year", "year": 1910},
            "place_id": "PL-0001",
            "participants": [{"person_id": "P-0002", "role": "principal"},
                             {"person_id": "P-0003", "role": "principal"}],
            "status": "confirmed", "source_ids": ["CIV-0001"], "notes": [],
        })
        _write(self.root, "events", {
            "id": "E-0004", "event_type": "birth",
            "date": {"kind": "exact", "value": "1982-05-10"},
            "place_id": "PL-0001",
            "participants": [{"person_id": "P-0001", "role": "principal"}],
            "status": "confirmed", "source_ids": ["CIV-0002"], "notes": [],
        })
        _write(self.root, "events", {
            "id": "E-0005", "event_type": "death",
            "date": {"kind": "year", "year": 1970},
            "place_text": "Somewhere",
            "participants": [{"person_id": "P-0003", "role": "principal"}],
            "status": "rejected", "source_ids": ["CIV-0001"], "notes": [],
        })

    def cleanup(self) -> None:
        self._tmp.cleanup()


def _assert_well_formed(text: str) -> None:
    lines = text.splitlines()
    assert lines[0] == "0 HEAD"
    assert lines[-1] == "0 TRLR"
    previous = -1
    for number, line in enumerate(lines, 1):
        match = re.match(r"^(\d+) ", line)
        assert match, f"line {number} lacks a level: {line!r}"
        level = int(match.group(1))
        assert level <= previous + 1, f"level jump at line {number}: {line!r}"
        previous = level
    defined = set(re.findall(r"^0 @([^@]+)@ ", text, re.M)) | {"SUBM0001"}
    used = set(re.findall(r"@([^@]+)@", text))
    assert not (used - defined), f"dangling pointers: {sorted(used - defined)}"


class ExportGedcomTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = GedcomFixture()
        self.addCleanup(self.fixture.cleanup)
        self.root = self.fixture.root / "data"

    def test_both_versions_are_well_formed(self) -> None:
        for version in SUPPORTED_VERSIONS:
            text = build_gedcom(self.root, version=version)
            _assert_well_formed(text)
            # 4 modelled people + 1 synthetic documented child
            self.assertEqual(len(re.findall(r"^0 @\S+@ INDI$", text, re.M)), 5, version)
            self.assertEqual(len(re.findall(r"^0 @\S+@ FAM$", text, re.M)), 1, version)

    def test_version_70_header_markers(self) -> None:
        text = build_gedcom(self.root, version="7.0")
        self.assertIn("2 VERS 7.0", text)
        self.assertNotIn("1 CHAR", text)          # removed in 7.0
        self.assertIn("1 LANG pt-BR", text)        # BCP-47 tag
        self.assertIn("1 RESN PRIVACY", text)      # uppercase enum, truthful marker
        self.assertNotIn("\n2 CONC ", text)        # CONC removed in 7.0
        self.assertNotIn("\n3 CONC ", text)

    def test_version_551_header_markers(self) -> None:
        text = build_gedcom(self.root, version="5.5.1")
        self.assertIn("2 VERS 5.5.1", text)
        self.assertIn("1 CHAR UTF-8", text)
        self.assertIn("1 LANG Portuguese", text)
        self.assertIn("1 RESN privacy", text)

    def test_full_backup_includes_everything(self) -> None:
        # No redaction: living people in full, transcriptions, scans and hashes.
        for version in SUPPORTED_VERSIONS:
            text = build_gedcom(self.root, version=version)
            self.assertIn("1 NAME Juan Carlos Muniz /Armond/", text, version)  # living
            self.assertIn("10 MAY 1982", text, version)                        # living DOB
            self.assertIn(f"Transcription: {TRANSCRIPTION}", text, version)
            self.assertIn(f"FILE {SCAN_PATH}", text, version)
            self.assertIn("sha256: " + "a" * 64, text, version)

    def test_sex_drives_husband_and_wife(self) -> None:
        text = build_gedcom(self.root)
        fam = text.split("0 @F0001@ FAM", 1)[1]
        self.assertIn("1 HUSB @P0002@", fam)  # male
        self.assertIn("1 WIFE @P0003@", fam)  # female
        self.assertIn("1 SEX M", text)
        self.assertIn("1 SEX F", text)

    def test_documented_child_becomes_a_synthetic_individual(self) -> None:
        text = build_gedcom(self.root)
        self.assertIn("\n0 @DOCF0001_1@ INDI\n", text)
        self.assertIn("1 NAME Marfiza Ferreira /Armond/", text)
        self.assertIn("1 FAMC @F0001@", text)
        self.assertIn("\n1 CHIL @DOCF0001_1@", text)
        self.assertIn("Documented child, not individually modelled", text)
        self.assertNotIn("1 NOTE None", text)  # missing optional fields stay absent

    def test_rejected_edges_are_flagged_not_asserted(self) -> None:
        text = build_gedcom(self.root)
        self.assertIn("REJECTED", text)
        self.assertIn("3 QUAY 0", text)  # rejected → quality 0
        self.assertIn("1970", text)      # the rejected death date is present

    def test_hypotheses_are_flagged_by_default(self) -> None:
        text = build_gedcom(self.root, include_hypotheses=True)
        self.assertIn("Unproven hypothesis", text)
        self.assertIn("3 QUAY 1", text)

    def test_hypotheses_can_be_excluded(self) -> None:
        text = build_gedcom(self.root, include_hypotheses=False)
        self.assertNotIn("Unproven hypothesis", text)
        self.assertNotIn("3 QUAY 1", text)

    def test_gedzip_bundles_gedcom_and_scans(self) -> None:
        out = self.fixture.root / "backup.gdz"
        count, missing = write_gedzip(self.root, out, repo_root=self.fixture.root)
        self.assertEqual(missing, [])
        self.assertGreaterEqual(count, 1)
        with zipfile.ZipFile(out) as archive:
            names = archive.namelist()
            self.assertIn("gedcom.ged", names)       # GEDZIP requires this name
            self.assertIn(SCAN_PATH, names)          # the actual scan is packed in
            ged = archive.read("gedcom.ged").decode("utf-8")
            self.assertIn("2 VERS 7.0", ged)         # GEDZIP is 7.0
            self.assertIn(f"FILE {SCAN_PATH}", ged)

    def test_gedzip_reports_missing_scans(self) -> None:
        # Remove the on-disk scan; the bundle still writes and reports it missing.
        (self.fixture.root / SCAN_PATH).unlink()
        out = self.fixture.root / "backup.gdz"
        count, missing = write_gedzip(self.root, out, repo_root=self.fixture.root)
        self.assertEqual(count, 0)
        self.assertIn(SCAN_PATH, missing)


if __name__ == "__main__":
    unittest.main()
