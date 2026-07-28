from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from typing import Any

import yaml

from scripts.validate_data import ValidationResult, validate_repository


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = PROJECT_ROOT / "schemas"


class RepositoryFixture:
    def __init__(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        for directory in ("people", "families", "events", "places", "sources"):
            (self.root / "data" / directory).mkdir(parents=True, exist_ok=True)
        self.documents = self._base_documents()
        self.ledger = {
            "version": 1,
            "next_ids": {
                "people": "P-0003",
                "families": "F-0002",
                "events": "E-0003",
                "places": "PL-0001",
                "sources": "SRC-0002",
            },
            "retired_ids": {
                "people": [],
                "families": [],
                "events": [],
                "places": [],
                "sources": [],
            },
        }
        self.write_all()

    def cleanup(self) -> None:
        self.temporary_directory.cleanup()

    @staticmethod
    def _base_documents() -> dict[str, dict[str, dict[str, Any]]]:
        source = {
            "id": "SRC-0001",
            "title": "Example civil registration",
            "record_type": "civil birth registration",
            "evidence_class": "original_record",
            "usage": "evidence",
            "repository": {"name": "Example civil registry"},
            "access_date": "2026-07-28",
            "language": "Portuguese",
            "abstract": "Synthetic fixture used only for validator tests.",
            "reliability": {
                "assessment": "Direct test evidence; not a genealogical claim."
            },
            "linked_people": ["P-0001", "P-0002"],
            "linked_families": ["F-0001"],
            "linked_events": ["E-0001", "E-0002"],
            "linked_places": [],
            "private": True,
        }
        people = {
            "P-0001": {
                "id": "P-0001",
                "preferred_name": "Example Parent",
                "privacy": "deceased",
                "name_variants": [
                    {
                        "value": "Example Parent",
                        "type": "source",
                        "source_ids": ["SRC-0001"],
                    }
                ],
                "event_ids": ["E-0001"],
                "family_ids": ["F-0001"],
                "notes": [],
            },
            "P-0002": {
                "id": "P-0002",
                "preferred_name": "Example Child",
                "privacy": "deceased",
                "name_variants": [
                    {
                        "value": "Example Child",
                        "type": "source",
                        "source_ids": ["SRC-0001"],
                    }
                ],
                "event_ids": ["E-0002"],
                "family_ids": ["F-0001"],
                "notes": [],
            },
        }
        events = {
            "E-0001": {
                "id": "E-0001",
                "event_type": "birth",
                "date": {"kind": "exact", "value": "1900-01-01"},
                "place_text": "Example place",
                "participants": [{"person_id": "P-0001", "role": "principal"}],
                "status": "confirmed",
                "source_ids": ["SRC-0001"],
                "notes": [],
            },
            "E-0002": {
                "id": "E-0002",
                "event_type": "birth",
                "date": {"kind": "exact", "value": "1930-01-01"},
                "place_text": "Example place",
                "participants": [{"person_id": "P-0002", "role": "principal"}],
                "status": "confirmed",
                "source_ids": ["SRC-0001"],
                "notes": [],
            },
        }
        family = {
            "id": "F-0001",
            "partners": [{"person_id": "P-0001", "role": "partner"}],
            "children": [
                {
                    "person_id": "P-0002",
                    "parent_ids": ["P-0001"],
                    "status": "confirmed",
                    "source_ids": ["SRC-0001"],
                    "notes": [],
                }
            ],
            "event_ids": [],
            "notes": [],
        }
        return {
            "people": people,
            "families": {"F-0001": family},
            "events": events,
            "places": {},
            "sources": {"SRC-0001": source},
        }

    def write_yaml(self, relative_path: str, value: Any) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(value, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    def write_all(self) -> None:
        for kind, documents in self.documents.items():
            for identifier, document in documents.items():
                self.write_yaml(f"data/{kind}/{identifier}.yaml", document)
        self.write_yaml("data/id-ledger.yaml", self.ledger)

    def rewrite(self) -> None:
        for kind, documents in self.documents.items():
            for identifier, document in documents.items():
                self.write_yaml(f"data/{kind}/{identifier}.yaml", document)
        self.write_yaml("data/id-ledger.yaml", self.ledger)

    def validate(self) -> ValidationResult:
        return validate_repository(self.root, schema_dir=SCHEMA_DIR)


class ValidateDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def assert_issue(
        self, result: ValidationResult, severity: str, text: str
    ) -> None:
        matching = [
            issue
            for issue in result.issues
            if issue.severity == severity and text in issue.message
        ]
        self.assertTrue(
            matching,
            f"Expected {severity!r} containing {text!r}; got "
            f"{[issue.render() for issue in result.issues]}",
        )

    def test_valid_repository_passes(self) -> None:
        result = self.fixture.validate()
        self.assertEqual((), result.errors)
        self.assertEqual((), result.warnings)
        self.assertEqual(6, result.entity_count)

    def test_missing_empty_entity_directory_is_allowed(self) -> None:
        (self.fixture.root / "data/places").rmdir()
        result = self.fixture.validate()
        self.assertEqual((), result.errors)

    def test_missing_cross_reference_is_an_error(self) -> None:
        self.fixture.documents["people"]["P-0001"]["event_ids"] = ["E-9999"]
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(result, "error", "reference 'E-9999' does not resolve")

    def test_collaborative_tree_cannot_confirm_conclusion(self) -> None:
        source = self.fixture.documents["sources"]["SRC-0001"]
        source["evidence_class"] = "collaborative_tree"
        source["usage"] = "lead_only"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result,
            "error",
            "confirmed conclusion lacks an original or contemporary evidence source",
        )

    def test_collaborative_tree_must_be_a_lead(self) -> None:
        source = self.fixture.documents["sources"]["SRC-0001"]
        source["evidence_class"] = "collaborative_tree"
        source["usage"] = "evidence"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result, "error", "collaborative trees must use usage 'lead_only'"
        )

    def test_collaborative_tree_alone_is_not_strong_evidence(self) -> None:
        source = self.fixture.documents["sources"]["SRC-0001"]
        source["evidence_class"] = "collaborative_tree"
        source["usage"] = "lead_only"
        self.fixture.documents["events"]["E-0001"]["status"] = "strong-evidence"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result,
            "error",
            "strong-evidence conclusion is supported only by lead or "
            "recollection sources",
        )

    def test_parent_born_after_child_is_an_error(self) -> None:
        parent_birth = self.fixture.documents["events"]["E-0001"]
        parent_birth["date"] = {"kind": "exact", "value": "1940-01-01"}
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(result, "error", "is born on or after child")

    def test_possible_duplicate_identity_is_a_warning(self) -> None:
        duplicate = copy.deepcopy(self.fixture.documents["people"]["P-0001"])
        duplicate["id"] = "P-0003"
        duplicate["event_ids"] = []
        duplicate["family_ids"] = []
        self.fixture.documents["people"]["P-0003"] = duplicate
        self.fixture.documents["sources"]["SRC-0001"]["linked_people"].append(
            "P-0003"
        )
        self.fixture.ledger["next_ids"]["people"] = "P-0004"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assertEqual((), result.errors)
        self.assert_issue(result, "warning", "possible duplicate identity")

    def test_unaccounted_identifier_gap_is_an_error(self) -> None:
        self.fixture.ledger["next_ids"]["people"] = "P-0004"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result, "error", "allocated sequence has unaccounted identifiers"
        )

    def test_invalid_calendar_date_is_an_error(self) -> None:
        event = self.fixture.documents["events"]["E-0001"]
        event["date"] = {"kind": "exact", "value": "1900-02-30"}
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(result, "error", "invalid exact calendar date")

    def test_missing_required_source_field_is_an_error(self) -> None:
        del self.fixture.documents["sources"]["SRC-0001"]["abstract"]
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(result, "error", "'abstract' is a required property")

    def test_zero_identifier_is_an_error(self) -> None:
        self.fixture.documents["people"]["P-0001"]["id"] = "P-0000"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(result, "error", "does not match")

    def test_duplicate_yaml_key_is_an_error(self) -> None:
        path = self.fixture.root / "data/people/P-0001.yaml"
        path.write_text(
            "id: P-0001\n"
            "id: P-0001\n"
            "preferred_name: Example Parent\n",
            encoding="utf-8",
        )
        result = self.fixture.validate()
        self.assert_issue(result, "error", "invalid YAML")

    def test_source_for_living_person_must_be_private(self) -> None:
        self.fixture.documents["people"]["P-0001"]["privacy"] = "living"
        self.fixture.documents["sources"]["SRC-0001"]["private"] = False
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(result, "error", "must be private")

    def test_evidence_checksum_mismatch_is_an_error(self) -> None:
        evidence_path = self.fixture.root / "evidence/civil/example.txt"
        evidence_path.parent.mkdir(parents=True)
        evidence_path.write_bytes(b"private test fixture")
        self.fixture.documents["sources"]["SRC-0001"]["digital_file"] = {
            "path": "evidence/civil/example.txt",
            "sha256": "0" * 64,
        }
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(result, "error", "checksum does not match")


if __name__ == "__main__":
    unittest.main()
