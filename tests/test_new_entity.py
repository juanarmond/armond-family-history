from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

import yaml

from scripts.new_entity import (
    AllocationError,
    materialize_reserved_entity,
    promote_entities,
    recover_promotion,
    reserve_entity,
)
from scripts.validate_data import validate_repository


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = PROJECT_ROOT / "schemas"


class AllocationFixture:
    def __init__(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.ledger: dict[str, Any] = {
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
        self.write_yaml(
            "templates/entities/person.yaml",
            {
                "schema_version": 1,
                "id": "P-NNNN",
                "preferred_name": "",
                "privacy": "unknown",
            },
        )

    def cleanup(self) -> None:
        self.temporary_directory.cleanup()

    def write_yaml(self, relative_path: str, value: Any) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(value, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    def read_ledger(self) -> dict[str, Any]:
        return yaml.safe_load(
            (self.root / "data/id-ledger.yaml").read_text(encoding="utf-8")
        )

    def write_linked_person_and_source_drafts(
        self, *, valid_person: bool = True
    ) -> None:
        self.ledger["reserved_ids"]["people"] = ["P-0001"]
        self.ledger["reserved_ids"]["sources"] = ["SRC-0001"]
        self.write_yaml("data/id-ledger.yaml", self.ledger)
        self.write_yaml(
            "research/entity-drafts/P-0001.yaml",
            {
                "schema_version": 1,
                "id": "P-0001",
                "preferred_name": "Example Person" if valid_person else "",
                "privacy": "deceased",
                "name_variants": [
                    {
                        "value": "Example Person",
                        "type": "source",
                        "source_ids": ["SRC-0001"],
                    }
                ],
                "event_ids": [],
                "family_ids": [],
                "notes": [],
            },
        )
        self.write_yaml(
            "research/entity-drafts/SRC-0001.yaml",
            {
                "schema_version": 1,
                "id": "SRC-0001",
                "title": "Synthetic linked source",
                "record_type": "synthetic civil record",
                "record_category": "civil_registration",
                "source_form": "original",
                "information_quality": "primary",
                "evidence_type": "direct",
                "usage": "evidence",
                "repository": {"name": "Synthetic test registry"},
                "access_date": "2026-07-28",
                "language": "English",
                "abstract": "Synthetic source used only for transaction tests.",
                "reliability": {"assessment": "Synthetic direct information."},
                "linked_people": ["P-0001"],
                "linked_families": [],
                "linked_events": [],
                "linked_places": [],
                "private": True,
                "notes": [],
            },
        )


class NewEntityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = AllocationFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_reserve_creates_draft_and_records_identifier(self) -> None:
        result = reserve_entity(
            self.fixture.root,
            "person",
            schema_dir=SCHEMA_DIR,
        )
        self.assertEqual("P-0001", result.identifier)
        self.assertFalse(result.dry_run)
        self.assertTrue(result.draft_path.is_file())
        draft = yaml.safe_load(result.draft_path.read_text(encoding="utf-8"))
        self.assertEqual("P-0001", draft["id"])
        self.assertEqual(
            ["P-0001"], self.fixture.read_ledger()["reserved_ids"]["people"]
        )
        validation = validate_repository(self.fixture.root, schema_dir=SCHEMA_DIR)
        self.assertEqual((), validation.errors)

    def test_dry_run_performs_no_writes(self) -> None:
        original = copy.deepcopy(self.fixture.read_ledger())
        result = reserve_entity(
            self.fixture.root,
            "person",
            dry_run=True,
            schema_dir=SCHEMA_DIR,
        )
        self.assertEqual("P-0001", result.identifier)
        self.assertFalse(result.draft_path.exists())
        self.assertEqual(original, self.fixture.read_ledger())

    def test_materialize_refuses_to_overwrite_existing_draft(self) -> None:
        result = reserve_entity(
            self.fixture.root,
            "person",
            schema_dir=SCHEMA_DIR,
        )
        with self.assertRaisesRegex(AllocationError, "refusing to overwrite"):
            materialize_reserved_entity(
                self.fixture.root,
                result.identifier,
                schema_dir=SCHEMA_DIR,
            )

    def test_materialize_recovers_reserved_id_without_draft(self) -> None:
        self.fixture.ledger["reserved_ids"]["people"] = ["P-0001"]
        self.fixture.write_yaml("data/id-ledger.yaml", self.fixture.ledger)
        result = materialize_reserved_entity(
            self.fixture.root,
            "P-0001",
            schema_dir=SCHEMA_DIR,
        )
        self.assertTrue(result.recovered)
        self.assertTrue(result.draft_path.is_file())

    def test_invalid_ledger_causes_no_writes(self) -> None:
        self.fixture.ledger["version"] = 1
        self.fixture.write_yaml("data/id-ledger.yaml", self.fixture.ledger)
        with self.assertRaisesRegex(
            AllocationError, "repository validation failed"
        ):
            reserve_entity(
                self.fixture.root,
                "person",
                schema_dir=SCHEMA_DIR,
            )
        self.assertFalse(
            (self.fixture.root / "research/entity-drafts").exists()
        )

    def test_promote_validates_mutually_dependent_entities_as_batch(self) -> None:
        self.fixture.write_linked_person_and_source_drafts()
        result = promote_entities(
            self.fixture.root,
            ["P-0001", "SRC-0001"],
            schema_dir=SCHEMA_DIR,
        )
        self.assertFalse(result.dry_run)
        self.assertTrue((self.fixture.root / "data/people/P-0001.yaml").is_file())
        self.assertTrue(
            (self.fixture.root / "data/sources/SRC-0001.yaml").is_file()
        )
        self.assertFalse(
            (self.fixture.root / "research/entity-drafts/P-0001.yaml").exists()
        )
        ledger = self.fixture.read_ledger()
        self.assertEqual([], ledger["reserved_ids"]["people"])
        self.assertEqual([], ledger["reserved_ids"]["sources"])
        validation = validate_repository(self.fixture.root, schema_dir=SCHEMA_DIR)
        self.assertEqual((), validation.errors)

    def test_promotion_dry_run_performs_no_writes(self) -> None:
        self.fixture.write_linked_person_and_source_drafts()
        original_ledger = copy.deepcopy(self.fixture.read_ledger())
        result = promote_entities(
            self.fixture.root,
            ["P-0001", "SRC-0001"],
            dry_run=True,
            schema_dir=SCHEMA_DIR,
        )
        self.assertTrue(result.dry_run)
        self.assertEqual(original_ledger, self.fixture.read_ledger())
        self.assertTrue(
            (self.fixture.root / "research/entity-drafts/P-0001.yaml").is_file()
        )
        self.assertFalse((self.fixture.root / "data/people/P-0001.yaml").exists())

    def test_promotion_uses_repository_schemas_by_default(self) -> None:
        shutil.copytree(SCHEMA_DIR, self.fixture.root / "schemas")
        self.fixture.write_linked_person_and_source_drafts()
        result = promote_entities(
            self.fixture.root,
            ["P-0001", "SRC-0001"],
            dry_run=True,
        )
        self.assertTrue(result.dry_run)

    def test_invalid_promotion_leaves_live_repository_unchanged(self) -> None:
        self.fixture.write_linked_person_and_source_drafts(valid_person=False)
        original_ledger = copy.deepcopy(self.fixture.read_ledger())
        with self.assertRaisesRegex(
            AllocationError, "prospective promotion is invalid"
        ):
            promote_entities(
                self.fixture.root,
                ["P-0001", "SRC-0001"],
                schema_dir=SCHEMA_DIR,
            )
        self.assertEqual(original_ledger, self.fixture.read_ledger())
        self.assertTrue(
            (self.fixture.root / "research/entity-drafts/P-0001.yaml").is_file()
        )
        self.assertFalse((self.fixture.root / "data/people/P-0001.yaml").exists())

    def test_promotion_rolls_back_after_live_commit_failure(self) -> None:
        self.fixture.write_linked_person_and_source_drafts()
        original_ledger = copy.deepcopy(self.fixture.read_ledger())
        with patch(
            "scripts.new_entity._remove_promoted_drafts",
            side_effect=OSError("synthetic commit failure"),
        ):
            with self.assertRaisesRegex(OSError, "synthetic commit failure"):
                promote_entities(
                    self.fixture.root,
                    ["P-0001", "SRC-0001"],
                    schema_dir=SCHEMA_DIR,
                )
        self.assertEqual(original_ledger, self.fixture.read_ledger())
        self.assertTrue(
            (self.fixture.root / "research/entity-drafts/P-0001.yaml").is_file()
        )
        self.assertFalse((self.fixture.root / "data/people/P-0001.yaml").exists())
        self.assertFalse(
            (self.fixture.root / ".entity-promotion-transaction").exists()
        )

    def test_recover_finalizes_already_committed_transaction(self) -> None:
        transaction = self.fixture.root / ".entity-promotion-transaction"
        self.fixture.write_yaml(
            ".entity-promotion-transaction/manifest.yaml",
            {"version": 1, "identifiers": ["P-0001"]},
        )
        (transaction / "committed").write_text("", encoding="utf-8")
        restored = recover_promotion(self.fixture.root)
        self.assertEqual(("P-0001",), restored)
        self.assertFalse(transaction.exists())


if __name__ == "__main__":
    unittest.main()
