from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from typing import Any

import yaml

from scripts.new_entity import (
    AllocationError,
    materialize_reserved_entity,
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


if __name__ == "__main__":
    unittest.main()
