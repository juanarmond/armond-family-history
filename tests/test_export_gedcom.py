"""Tests for the GEDCOM exporter, especially its privacy guarantees.

The fixture is a small self-contained temp repository (not the live data) so the
tests stay deterministic and can exercise paths the real data may not currently
contain (e.g. a hypothesis-level edge).
"""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.export_gedcom import SUPPORTED_VERSIONS, build_gedcom


# A transcription that must never reach the export, plus private file details.
SECRET_TRANSCRIPTION = "sob No 132 encontra-se o assento"
SECRET_PATH = "evidence/civil/CIV-0002-secret.jpg"


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

        _write(self.root, "places", {
            "id": "PL-0001",
            "preferred_name": "Carangola, Minas Gerais, Brazil",
            "coordinates": {"latitude": -20.73, "longitude": -42.03},
        })
        _write(self.root, "sources/civil", {
            "id": "CIV-0001",
            "title": "Civil birth registration of the child",
            "abstract": "Curated summary, safe to export.",
            "record_category": "civil_registration",
            "source_form": "original",
            "information_quality": "primary",
            "evidence_type": "direct",
            "repository": {"name": "Cartorio de Carangola", "book": "2", "page": "142"},
            "private": False,
        })
        _write(self.root, "sources/civil", {
            "id": "CIV-0002",
            "title": "Private record",
            "abstract": "Also curated and safe.",
            "record_category": "civil_registration",
            "source_form": "derivative",
            "information_quality": "mixed",
            "evidence_type": "direct",
            "repository": {
                "name": "Cartorio de Carangola",
                "repository_path": SECRET_PATH,
            },
            "transcription": SECRET_TRANSCRIPTION,
            "digital_file": {"path": SECRET_PATH, "sha256": "a" * 64},
            "private": True,
        })

        # Living subject, with a birth event that redaction must hide.
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
        self.assertIn("1 RESN PRIVACY", text)      # uppercase enum
        self.assertNotIn("\n2 CONC ", text)        # CONC removed in 7.0
        self.assertNotIn("\n3 CONC ", text)

    def test_version_551_header_markers(self) -> None:
        text = build_gedcom(self.root, version="5.5.1")
        self.assertIn("2 VERS 5.5.1", text)
        self.assertIn("1 CHAR UTF-8", text)
        self.assertIn("1 LANG Portuguese", text)
        self.assertIn("1 RESN privacy", text)

    def _assert_scrubbed(self, text: str, label: str) -> None:
        self.assertNotIn("evidence/", text, label)
        self.assertNotIn(SECRET_PATH, text, label)
        self.assertNotIn(SECRET_TRANSCRIPTION, text, label)
        self.assertNotIn("Transcription:", text, label)
        self.assertNotIn("sha256", text.lower(), label)
        self.assertNotIn("repository_path", text, label)
        self.assertNotIn("REJECTED", text, label)

    def test_shareable_modes_never_leak(self) -> None:
        # The safe-to-share outputs — redact/omit, and full with --no-private —
        # carry no scans, paths, hashes, transcriptions or rejected edges.
        for version in SUPPORTED_VERSIONS:
            for mode in ("redact", "omit"):
                self._assert_scrubbed(
                    build_gedcom(self.root, version=version, living=mode),
                    f"{version}/{mode}",
                )
            self._assert_scrubbed(
                build_gedcom(self.root, version=version, living="full",
                             include_private=False),
                f"{version}/no-private",
            )

    def test_archival_full_export_includes_private_detail(self) -> None:
        # The default full export is the owner's archival copy: it *does* carry
        # transcriptions and OBJE scan references.
        for version in SUPPORTED_VERSIONS:
            text = build_gedcom(self.root, version=version, living="full")
            self.assertIn(f"Transcription: {SECRET_TRANSCRIPTION}", text, version)
            self.assertIn(f"FILE {SECRET_PATH}", text, version)
            self.assertIn("sha256: " + "a" * 64, text, version)

    def test_rejected_edges_flagged_in_archival_but_absent_when_shareable(self) -> None:
        full = build_gedcom(self.root, living="full")
        self.assertIn("REJECTED", full)
        self.assertIn("3 QUAY 0", full)          # rejected → quality 0
        self.assertIn("1970", full)              # the rejected death date appears
        for text in (
            build_gedcom(self.root, living="redact"),
            build_gedcom(self.root, living="full", include_private=False),
        ):
            self.assertNotIn("REJECTED", text)
            self.assertNotIn("3 QUAY 0", text)

    def test_sex_drives_husband_and_wife(self) -> None:
        text = build_gedcom(self.root)
        fam = text.split("0 @F0001@ FAM", 1)[1]
        self.assertIn("1 HUSB @P0002@", fam)  # male
        self.assertIn("1 WIFE @P0003@", fam)  # female
        self.assertIn("1 SEX M", text)
        self.assertIn("1 SEX F", text)

    def test_documented_child_becomes_a_synthetic_individual(self) -> None:
        # Standard-compliant: a real INDI + CHIL link, not just a FAM note.
        text = build_gedcom(self.root)
        self.assertIn("\n0 @DOCF0001_1@ INDI\n", text)
        self.assertIn("1 NAME Marfiza Ferreira /Armond/", text)
        self.assertIn("1 FAMC @F0001@", text)
        self.assertIn("\n1 CHIL @DOCF0001_1@", text)
        self.assertIn("Documented child, not individually modelled", text)
        self.assertNotIn("1 NOTE None", text)  # missing optional fields stay absent

    def test_living_full_exports_the_real_record(self) -> None:
        text = build_gedcom(self.root, living="full")
        self.assertIn("1 NAME Juan Carlos Muniz /Armond/", text)
        self.assertIn("10 MAY 1982", text)  # living person's birth date present

    def test_living_redact_anonymises_the_own_record(self) -> None:
        text = build_gedcom(self.root, living="redact")
        _assert_well_formed(text)
        self.assertIn("@P0001@ INDI", text)            # node kept
        self.assertIn("1 NAME Living /Armond/", text)  # name anonymised
        self.assertNotIn("1 NAME Juan Carlos Muniz /Armond/", text)
        self.assertNotIn("10 MAY 1982", text)          # vitals hidden
        self.assertIn("1 RESN PRIVACY", text)          # 7.0 default

    def test_living_omit_drops_the_node_without_dangling_refs(self) -> None:
        text = build_gedcom(self.root, living="omit")
        _assert_well_formed(text)
        self.assertNotIn("@P0001@ INDI", text)
        self.assertNotIn("1 CHIL @P0001@", text)

    def test_hypotheses_are_flagged_by_default(self) -> None:
        text = build_gedcom(self.root, include_hypotheses=True)
        self.assertIn("Unproven hypothesis", text)
        self.assertIn("3 QUAY 1", text)  # hypothesis citation quality

    def test_hypotheses_can_be_excluded(self) -> None:
        text = build_gedcom(self.root, include_hypotheses=False)
        self.assertNotIn("Unproven hypothesis", text)
        # the hypothesis death (E-0002) is dropped entirely
        self.assertNotIn("3 QUAY 1", text)


if __name__ == "__main__":
    unittest.main()
