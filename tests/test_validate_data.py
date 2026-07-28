from __future__ import annotations

import copy
import base64
import hashlib
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
            "version": 2,
            "reserved_ids": {
                "people": [],
                "families": [],
                "events": [],
                "places": [],
                "sources": [],
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
            "schema_version": 1,
            "id": "SRC-0001",
            "title": "Example civil registration",
            "record_type": "civil birth registration",
            "record_category": "civil_registration",
            "source_form": "original",
            "information_quality": "primary",
            "evidence_type": "direct",
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
                "schema_version": 1,
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
                "schema_version": 1,
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
                "schema_version": 1,
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
                "schema_version": 1,
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
            "schema_version": 1,
            "id": "F-0001",
            "partners": [{"person_id": "P-0001", "role": "parent"}],
            "children": [
                {
                    "person_id": "P-0002",
                    "parent_relationships": [
                        {
                            "parent_id": "P-0001",
                            "relationship_type": "biological",
                            "status": "confirmed",
                            "source_ids": ["SRC-0001"],
                            "notes": [],
                        }
                    ],
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
        self.write_yaml(
            "research/document-inventory.yaml", {"version": 1, "documents": []}
        )
        self.write_yaml(
            "research/record-coverage.yaml",
            {
                "version": 1,
                "scope": "deceased-direct-ancestors",
                "people": [],
            },
        )

    def rewrite(self) -> None:
        for kind, documents in self.documents.items():
            for identifier, document in documents.items():
                self.write_yaml(f"data/{kind}/{identifier}.yaml", document)
        self.write_yaml("data/id-ledger.yaml", self.ledger)
        inventory_path = self.root / "research/document-inventory.yaml"
        if not inventory_path.exists():
            self.write_yaml(
                "research/document-inventory.yaml", {"version": 1, "documents": []}
            )
        coverage_path = self.root / "research/record-coverage.yaml"
        if not coverage_path.exists():
            self.write_yaml(
                "research/record-coverage.yaml",
                {
                    "version": 1,
                    "scope": "deceased-direct-ancestors",
                    "people": [],
                },
            )

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

    def test_valid_document_inventory_entry_passes(self) -> None:
        content = b"privacy-reviewed synthetic document"
        evidence_path = self.fixture.root / "evidence/civil/test-record.bin"
        evidence_path.parent.mkdir(parents=True)
        evidence_path.write_bytes(content)
        self.fixture.write_yaml(
            "research/document-inventory.yaml",
            {
                "version": 1,
                "documents": [
                    {
                        "inventory_id": "DOC-0001",
                        "status": "reviewed",
                        "added_date": "2026-07-28",
                        "apparent_record_type": "synthetic civil record",
                        "apparent_people": ["Example Person"],
                        "apparent_event": "other",
                        "image_quality": "adequate",
                        "provenance": "Synthetic validator fixture.",
                        "rights_status": "private-research",
                        "files": [
                            {
                                "path": "evidence/civil/test-record.bin",
                                "sha256": hashlib.sha256(content).hexdigest(),
                                "media_type": "application/octet-stream",
                                "role": "primary",
                                "preservation": {
                                    "acquisition_method": "owner-supplied",
                                    "resolution_status": "original-file",
                                },
                                "privacy_review": "cleared",
                                "sensitive_content": [],
                            }
                        ],
                        "duplicate_of": None,
                        "proposed_source_id": None,
                        "notes": [],
                    }
                ],
            },
        )
        result = self.fixture.validate()
        self.assertEqual((), result.errors)

    def test_inventory_checksum_mismatch_is_an_error(self) -> None:
        evidence_path = self.fixture.root / "evidence/civil/test-record.bin"
        evidence_path.parent.mkdir(parents=True)
        evidence_path.write_bytes(b"synthetic document")
        self.fixture.write_yaml(
            "research/document-inventory.yaml",
            {
                "version": 1,
                "documents": [
                    {
                        "inventory_id": "DOC-0001",
                        "status": "intake",
                        "added_date": "2026-07-28",
                        "apparent_record_type": "synthetic record",
                        "apparent_people": [],
                        "apparent_event": "unknown",
                        "image_quality": "unreviewed",
                        "provenance": "Synthetic validator fixture.",
                        "rights_status": "unknown",
                        "files": [
                            {
                                "path": "evidence/civil/test-record.bin",
                                "sha256": "0" * 64,
                                "role": "primary",
                                "privacy_review": "pending",
                                "sensitive_content": [],
                            }
                        ],
                        "duplicate_of": None,
                        "proposed_source_id": None,
                        "notes": [],
                    }
                ],
            },
        )
        result = self.fixture.validate()
        self.assert_issue(result, "error", "checksum does not match")

    def test_inventory_image_dimensions_must_match_encoded_file(self) -> None:
        content = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4"
            "nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
        )
        evidence_path = self.fixture.root / "evidence/civil/test-record.png"
        evidence_path.parent.mkdir(parents=True)
        evidence_path.write_bytes(content)
        self.fixture.write_yaml(
            "research/document-inventory.yaml",
            {
                "version": 1,
                "documents": [
                    {
                        "inventory_id": "DOC-0001",
                        "status": "reviewed",
                        "added_date": "2026-07-28",
                        "apparent_record_type": "synthetic image",
                        "apparent_people": [],
                        "apparent_event": "other",
                        "image_quality": "adequate",
                        "provenance": "Synthetic validator fixture.",
                        "rights_status": "private-research",
                        "files": [
                            {
                                "path": "evidence/civil/test-record.png",
                                "sha256": hashlib.sha256(content).hexdigest(),
                                "media_type": "image/png",
                                "role": "primary",
                                "preservation": {
                                    "acquisition_method": "owner-supplied",
                                    "resolution_status": "original-file",
                                    "pixel_width": 2,
                                    "pixel_height": 1,
                                },
                                "privacy_review": "cleared",
                                "sensitive_content": [],
                            }
                        ],
                        "duplicate_of": None,
                        "proposed_source_id": None,
                        "notes": [],
                    }
                ],
            },
        )
        result = self.fixture.validate()
        self.assert_issue(result, "error", "do not match encoded image dimensions")

    def test_reviewed_inventory_requires_privacy_clearance(self) -> None:
        content = b"synthetic document"
        evidence_path = self.fixture.root / "evidence/civil/test-record.bin"
        evidence_path.parent.mkdir(parents=True)
        evidence_path.write_bytes(content)
        self.fixture.write_yaml(
            "research/document-inventory.yaml",
            {
                "version": 1,
                "documents": [
                    {
                        "inventory_id": "DOC-0001",
                        "status": "reviewed",
                        "added_date": "2026-07-28",
                        "apparent_record_type": "synthetic record",
                        "apparent_people": [],
                        "apparent_event": "unknown",
                        "image_quality": "adequate",
                        "provenance": "Synthetic validator fixture.",
                        "rights_status": "private-research",
                        "files": [
                            {
                                "path": "evidence/civil/test-record.bin",
                                "sha256": hashlib.sha256(content).hexdigest(),
                                "role": "primary",
                                "privacy_review": "pending",
                                "sensitive_content": [],
                            }
                        ],
                        "duplicate_of": None,
                        "proposed_source_id": None,
                        "notes": [],
                    }
                ],
            },
        )
        result = self.fixture.validate()
        self.assert_issue(
            result,
            "error",
            "reviewed or catalogued documents require every retained file",
        )

    def test_catalogued_inventory_must_match_source_file(self) -> None:
        inventory_content = b"catalogued inventory file"
        source_content = b"different source file"
        inventory_path = self.fixture.root / "evidence/civil/inventory.bin"
        source_path = self.fixture.root / "evidence/civil/source.bin"
        inventory_path.parent.mkdir(parents=True)
        inventory_path.write_bytes(inventory_content)
        source_path.write_bytes(source_content)
        self.fixture.documents["sources"]["SRC-0001"]["digital_file"] = {
            "path": "evidence/civil/source.bin",
            "sha256": hashlib.sha256(source_content).hexdigest(),
        }
        self.fixture.rewrite()
        self.fixture.write_yaml(
            "research/document-inventory.yaml",
            {
                "version": 1,
                "documents": [
                    {
                        "inventory_id": "DOC-0001",
                        "status": "catalogued",
                        "added_date": "2026-07-28",
                        "apparent_record_type": "synthetic record",
                        "apparent_people": ["Example Person"],
                        "apparent_event": "other",
                        "image_quality": "adequate",
                        "provenance": "Synthetic validator fixture.",
                        "rights_status": "private-research",
                        "files": [
                            {
                                "path": "evidence/civil/inventory.bin",
                                "sha256": hashlib.sha256(
                                    inventory_content
                                ).hexdigest(),
                                "media_type": "application/octet-stream",
                                "role": "primary",
                                "privacy_review": "cleared",
                                "sensitive_content": [],
                            }
                        ],
                        "duplicate_of": None,
                        "proposed_source_id": "SRC-0001",
                        "notes": [],
                    }
                ],
            },
        )
        result = self.fixture.validate()
        self.assert_issue(
            result,
            "error",
            "no inventoried path and checksum match SRC-0001.digital_file",
        )

    def test_record_coverage_rejects_living_person(self) -> None:
        self.fixture.documents["people"]["P-0001"]["privacy"] = "living"
        self.fixture.rewrite()
        self.fixture.write_yaml(
            "research/record-coverage.yaml",
            {
                "version": 1,
                "scope": "deceased-direct-ancestors",
                "people": [
                    {
                        "person_id": "P-0001",
                        "external_profiles": [],
                        "records": [
                            {
                                "record_type": "birth",
                                "status": "catalogued",
                                "source_ids": ["SRC-0001"],
                                "last_reviewed": "2026-07-28",
                                "notes": [],
                            }
                        ],
                        "notes": [],
                    }
                ],
            },
        )
        result = self.fixture.validate()
        self.assert_issue(
            result, "error", "living person P-0001 must not appear in this ledger"
        )

    def test_record_coverage_source_must_link_to_person(self) -> None:
        self.fixture.documents["sources"]["SRC-0001"]["linked_people"] = ["P-0002"]
        self.fixture.rewrite()
        self.fixture.write_yaml(
            "research/record-coverage.yaml",
            {
                "version": 1,
                "scope": "deceased-direct-ancestors",
                "people": [
                    {
                        "person_id": "P-0001",
                        "external_profiles": [],
                        "records": [
                            {
                                "record_type": "birth",
                                "status": "catalogued",
                                "source_ids": ["SRC-0001"],
                                "last_reviewed": "2026-07-28",
                                "notes": [],
                            }
                        ],
                        "notes": [],
                    }
                ],
            },
        )
        result = self.fixture.validate()
        self.assert_issue(
            result, "error", "SRC-0001 is not linked to coverage person P-0001"
        )

    def test_inventory_sequence_gap_is_an_error(self) -> None:
        self.fixture.write_yaml(
            "research/document-inventory.yaml",
            {
                "version": 1,
                "documents": [
                    {
                        "inventory_id": "DOC-0002",
                        "status": "intake",
                        "added_date": "2026-07-28",
                        "apparent_record_type": "synthetic record",
                        "apparent_people": [],
                        "apparent_event": "unknown",
                        "image_quality": "unreviewed",
                        "provenance": "Synthetic validator fixture.",
                        "rights_status": "unknown",
                        "files": [
                            {
                                "path": "evidence/missing.bin",
                                "sha256": "0" * 64,
                                "role": "primary",
                                "privacy_review": "pending",
                                "sensitive_content": [],
                            }
                        ],
                        "duplicate_of": None,
                        "proposed_source_id": None,
                        "notes": [],
                    }
                ],
            },
        )
        result = self.fixture.validate()
        self.assert_issue(
            result, "error", "inventory sequence has unaccounted identifiers"
        )

    def test_collaborative_tree_cannot_confirm_conclusion(self) -> None:
        source = self.fixture.documents["sources"]["SRC-0001"]
        source["record_category"] = "collaborative_tree"
        source["source_form"] = "authored_narrative"
        source["information_quality"] = "secondary"
        source["evidence_type"] = "undetermined"
        source["usage"] = "lead_only"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result,
            "error",
            "confirmed conclusion requires direct primary information",
        )

    def test_collaborative_tree_must_be_a_lead(self) -> None:
        source = self.fixture.documents["sources"]["SRC-0001"]
        source["record_category"] = "collaborative_tree"
        source["source_form"] = "authored_narrative"
        source["information_quality"] = "secondary"
        source["evidence_type"] = "undetermined"
        source["usage"] = "evidence"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result, "error", "collaborative trees must use usage 'lead_only'"
        )

    def test_collaborative_tree_alone_is_not_strong_evidence(self) -> None:
        source = self.fixture.documents["sources"]["SRC-0001"]
        source["record_category"] = "collaborative_tree"
        source["source_form"] = "authored_narrative"
        source["information_quality"] = "secondary"
        source["evidence_type"] = "undetermined"
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

    def test_certified_official_derivative_can_confirm_conclusion(self) -> None:
        # A certified copy of an official record (derivative form, direct
        # primary information) may support a confirmed conclusion.
        source = self.fixture.documents["sources"]["SRC-0001"]
        source["source_form"] = "derivative"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assertEqual((), result.errors)

    def test_recollection_derivative_cannot_confirm_conclusion(self) -> None:
        # A weak-category source cannot confirm even in derivative form.
        source = self.fixture.documents["sources"]["SRC-0001"]
        source["source_form"] = "derivative"
        source["record_category"] = "family_recollection"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result,
            "error",
            "confirmed conclusion requires direct primary information",
        )

    def test_two_original_indirect_sources_can_confirm_conclusion(self) -> None:
        first_source = self.fixture.documents["sources"]["SRC-0001"]
        first_source["evidence_type"] = "indirect"
        second_source = copy.deepcopy(first_source)
        second_source["id"] = "SRC-0002"
        second_source["title"] = "Second independent civil registration"
        self.fixture.documents["sources"]["SRC-0002"] = second_source
        for event in self.fixture.documents["events"].values():
            event["source_ids"].append("SRC-0002")
        self.fixture.documents["families"]["F-0001"]["children"][0][
            "parent_relationships"
        ][0]["source_ids"].append("SRC-0002")
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assertEqual((), result.errors)

    def test_entity_without_schema_version_is_an_error(self) -> None:
        del self.fixture.documents["people"]["P-0001"]["schema_version"]
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(result, "error", "'schema_version' is a required property")

    def test_uncontrolled_parent_relationship_type_is_an_error(self) -> None:
        relationship = self.fixture.documents["families"]["F-0001"]["children"][0][
            "parent_relationships"
        ][0]
        relationship["relationship_type"] = "probably-parent"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(result, "error", "is not one of")

    def test_other_parent_relationship_requires_detail(self) -> None:
        relationship = self.fixture.documents["families"]["F-0001"]["children"][0][
            "parent_relationships"
        ][0]
        relationship["relationship_type"] = "other"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result, "error", "'relationship_detail' is a required property"
        )

    def test_parent_relationships_for_child_require_distinct_parents(self) -> None:
        relationships = self.fixture.documents["families"]["F-0001"]["children"][0][
            "parent_relationships"
        ]
        relationships.append(copy.deepcopy(relationships[0]))
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result, "error", "parent IDs must be distinct for each child"
        )

    def test_two_reported_parents_do_not_require_partner_relationship(self) -> None:
        second_parent = copy.deepcopy(self.fixture.documents["people"]["P-0001"])
        second_parent["id"] = "P-0003"
        second_parent["preferred_name"] = "Second Example Parent"
        second_parent["name_variants"][0]["value"] = "Second Example Parent"
        second_parent["event_ids"] = []
        self.fixture.documents["people"]["P-0003"] = second_parent
        self.fixture.documents["sources"]["SRC-0001"]["linked_people"].append(
            "P-0003"
        )
        family = self.fixture.documents["families"]["F-0001"]
        family["partners"].append({"person_id": "P-0003", "role": "parent"})
        family["children"][0]["parent_relationships"].append(
            {
                "parent_id": "P-0003",
                "relationship_type": "unknown",
                "status": "confirmed",
                "source_ids": ["SRC-0001"],
                "notes": [],
            }
        )
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assertEqual((), result.errors)

    def test_partner_role_requires_sourced_partner_relationship(self) -> None:
        self.fixture.documents["families"]["F-0001"]["partners"][0][
            "role"
        ] = "partner"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result, "error", "'partner_relationship' is a required property"
        )

    def test_uncontrolled_event_participant_role_is_an_error(self) -> None:
        participant = self.fixture.documents["events"]["E-0001"]["participants"][0]
        participant["role"] = "mysterious-relative"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(result, "error", "is not one of")

    def test_other_event_role_requires_detail(self) -> None:
        participant = self.fixture.documents["events"]["E-0001"]["participants"][0]
        participant["role"] = "other"
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(result, "error", "'role_detail' is a required property")

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
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assertEqual((), result.errors)
        self.assert_issue(result, "warning", "possible duplicate identity")

    def test_unaccounted_identifier_gap_is_an_error(self) -> None:
        self.fixture.ledger["reserved_ids"]["people"] = ["P-0004"]
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result, "error", "allocated sequence has unaccounted identifiers"
        )

    def test_current_and_reserved_identifiers_cannot_overlap(self) -> None:
        self.fixture.ledger["reserved_ids"]["people"] = ["P-0001"]
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result, "error", "current and reserved identifiers overlap"
        )

    def test_unreserved_entity_draft_is_an_error(self) -> None:
        self.fixture.write_yaml(
            "research/entity-drafts/P-0003.yaml",
            {"schema_version": 1, "id": "P-0003"},
        )
        result = self.fixture.validate()
        self.assert_issue(result, "error", "draft identifier P-0003 is not reserved")

    def test_entity_draft_id_must_match_filename(self) -> None:
        self.fixture.ledger["reserved_ids"]["people"] = ["P-0003"]
        self.fixture.write_yaml(
            "research/entity-drafts/P-0003.yaml",
            {"schema_version": 1, "id": "P-9999"},
        )
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(result, "error", "draft ID must match filename P-0003")

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

    def test_parent_relationship_source_for_living_person_must_be_private(
        self,
    ) -> None:
        self.fixture.documents["people"]["P-0001"]["privacy"] = "living"
        source = copy.deepcopy(self.fixture.documents["sources"]["SRC-0001"])
        source["id"] = "SRC-0002"
        source["title"] = "Non-private relationship fixture"
        source["linked_people"] = []
        source["linked_events"] = []
        source["private"] = False
        self.fixture.documents["sources"]["SRC-0002"] = source
        relationship = self.fixture.documents["families"]["F-0001"]["children"][0][
            "parent_relationships"
        ][0]
        relationship["source_ids"].append("SRC-0002")
        self.fixture.rewrite()
        result = self.fixture.validate()
        self.assert_issue(
            result, "error", "source concerning living person P-0001 must be private"
        )

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
