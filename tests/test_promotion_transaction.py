"""Change-set transactions: atomic apply, rollback, recovery, locking and evidence
transfer. Every fixture is synthetic and lives in a temporary directory."""

from __future__ import annotations

import copy
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

import yaml

from scripts import new_entity
from scripts.new_entity import (
    LOCK_FILENAME,
    TRANSACTION_DIRECTORY,
    AllocationError,
    apply_change_set,
    load_change_set,
    promote_entities,
    recover_transaction,
    reserve_entity,
)
from scripts.validate_data import validate_repository
from tests.test_new_entity import AllocationFixture
from tests.test_validate_data import RepositoryFixture


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = PROJECT_ROOT / "schemas"
SCAN_BYTES = b"synthetic producer scan, page 1"
SCAN_DESTINATION = "evidence/civil/CIV-0002-synthetic-scan.bin"
AUTHORISATION = "owner-authorisation-test-0001"


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def dead_pid() -> int:
    process = subprocess.Popen([sys.executable, "-c", "pass"])
    process.wait()
    return process.pid


class SimulatedCrash(BaseException):
    """Stands in for the process dying mid-transaction."""


class TransactionFixture(RepositoryFixture):
    """The validator's synthetic repository plus a separate producer workspace."""

    def __init__(self) -> None:
        super().__init__()
        self.producer_directory = tempfile.TemporaryDirectory()
        self.producer = Path(self.producer_directory.name)

    def cleanup(self) -> None:
        super().cleanup()
        self.producer_directory.cleanup()

    def reserve(self, kind: str, identifier: str) -> None:
        self.ledger["reserved_ids"][kind].append(identifier)
        self.write_yaml("data/id-ledger.yaml", self.ledger)

    def write_draft(self, document: dict[str, Any]) -> None:
        self.write_yaml(f"research/entity-drafts/{document['id']}.yaml", document)

    def live_sha256(self, relative_path: str) -> str:
        return sha256((self.root / relative_path).read_bytes())

    def write_producer_file(self, relative_path: str, content: bytes) -> Path:
        path = self.producer / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def write_patch(self, name: str, value: Any) -> Path:
        return self.write_producer_file(
            f"patches/{name}",
            yaml.safe_dump(value, sort_keys=False, allow_unicode=True).encode(
                "utf-8"
            ),
        )

    def replacement(self, relative_path: str, value: Any) -> dict[str, str]:
        return {
            "path": relative_path,
            "base_sha256": self.live_sha256(relative_path),
            "content_from": str(
                self.write_patch(relative_path.replace("/", "__"), value)
            ),
        }

    def write_change_set(self, value: dict[str, Any]) -> Path:
        path = self.producer / "change-set.yaml"
        path.write_text(
            yaml.safe_dump(value, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return path

    def snapshot(self) -> dict[str, str]:
        return {
            path.relative_to(self.root).as_posix(): (
                "<dir>" if path.is_dir() else sha256(path.read_bytes())
            )
            for path in sorted(self.root.rglob("*"))
        }


def inventory_document(
    path: str, checksum: str, *, producer_sha256: str | None = None
) -> dict[str, Any]:
    return {
        "inventory_id": "DOC-0001",
        "status": "catalogued",
        "added_date": "2026-07-28",
        "apparent_record_type": "synthetic parentage record",
        "apparent_people": ["Example Parent", "Example Grandparent"],
        "apparent_event": "other",
        "image_quality": "adequate",
        "provenance": "Synthetic producer workspace fixture.",
        "rights_status": "private-research",
        "files": [
            {
                "path": path,
                "sha256": checksum,
                "media_type": "application/octet-stream",
                "role": "primary",
                "preservation": {
                    "acquisition_method": "authorised-original-download",
                    "resolution_status": "original-file",
                },
                "privacy_review": "cleared",
                "sensitive_content": [],
            }
        ],
        "duplicate_of": None,
        "proposed_source_id": "CIV-0002",
        "notes": [],
        "transfer": {
            "producer_path": "research/evidence/images/synthetic-scan.bin",
            "producer_sha256": producer_sha256 or checksum,
            "handoff_digest": None,
            "resolution": "max-res",
            "authorisation": AUTHORISATION,
            "transferred_at": "2026-07-28",
        },
    }


def parent_family_change_set(
    fixture: TransactionFixture,
    *,
    person_replacement: bool = True,
    authorisation: str | None = AUTHORISATION,
    declared_sha256: str | None = None,
) -> Path:
    """A new parent family above P-0001, with its source, scan and inventory entry."""
    for kind, identifier in (
        ("people", "P-0003"),
        ("families", "F-0002"),
        ("civil", "CIV-0002"),
    ):
        fixture.reserve(kind, identifier)
    fixture.write_draft(
        {
            "schema_version": 1,
            "id": "P-0003",
            "preferred_name": "Example Grandparent",
            "privacy": "deceased",
            "name_variants": [
                {
                    "value": "Example Grandparent",
                    "type": "source",
                    "source_ids": ["CIV-0002"],
                }
            ],
            "event_ids": [],
            "family_ids": ["F-0002"],
            "notes": [],
        }
    )
    fixture.write_draft(
        {
            "schema_version": 1,
            "id": "F-0002",
            "partners": [{"person_id": "P-0003", "role": "parent"}],
            "children": [
                {
                    "person_id": "P-0001",
                    "parent_relationships": [
                        {
                            "parent_id": "P-0003",
                            "relationship_type": "biological",
                            "status": "confirmed",
                            "source_ids": ["CIV-0002"],
                            "notes": [],
                        }
                    ],
                    "notes": [],
                }
            ],
            "event_ids": [],
            "notes": [],
        }
    )
    source = copy.deepcopy(fixture.documents["sources"]["CIV-0001"])
    source.update(
        {
            "id": "CIV-0002",
            "title": "Synthetic parentage record",
            "linked_people": ["P-0001", "P-0003"],
            "linked_families": ["F-0002"],
            "linked_events": [],
            "digital_file": {"path": SCAN_DESTINATION, "sha256": sha256(SCAN_BYTES)},
        }
    )
    fixture.write_draft(source)
    scan = fixture.write_producer_file("images/synthetic-scan.bin", SCAN_BYTES)

    replacements = []
    if person_replacement:
        person = copy.deepcopy(fixture.documents["people"]["P-0001"])
        person["family_ids"] = ["F-0001", "F-0002"]
        replacements.append(fixture.replacement("data/people/P-0001.yaml", person))
    replacements.append(
        fixture.replacement(
            "data/document-inventory.yaml",
            {
                "version": 1,
                "documents": [
                    inventory_document(SCAN_DESTINATION, sha256(SCAN_BYTES))
                ],
            },
        )
    )
    evidence: dict[str, Any] = {
        "from": str(scan),
        "sha256": declared_sha256 or sha256(SCAN_BYTES),
        "to": SCAN_DESTINATION,
    }
    if authorisation is not None:
        evidence["authorisation"] = authorisation
    return fixture.write_change_set(
        {
            "id": "synthetic parent family",
            "promote": ["P-0003", "F-0002", "CIV-0002"],
            "replace": replacements,
            "evidence": [evidence],
        }
    )


class ChangeSetTransactionTests(unittest.TestCase):
    def new_fixture(self) -> TransactionFixture:
        fixture = TransactionFixture()
        self.addCleanup(fixture.cleanup)
        return fixture

    def setUp(self) -> None:
        self.fixture = self.new_fixture()

    def apply(self, fixture: TransactionFixture, change_set: Path, **kwargs: Any):
        return apply_change_set(
            fixture.root, change_set, schema_dir=SCHEMA_DIR, **kwargs
        )

    def assert_clean(self, fixture: TransactionFixture) -> None:
        validation = validate_repository(fixture.root, schema_dir=SCHEMA_DIR)
        self.assertEqual((), validation.errors)
        self.assertFalse((fixture.root / LOCK_FILENAME).exists())
        self.assertFalse((fixture.root / TRANSACTION_DIRECTORY).exists())

    # T3 -----------------------------------------------------------------------

    def test_change_set_promotes_replaces_and_transfers_atomically(self) -> None:
        change_set = parent_family_change_set(self.fixture)
        result = self.apply(self.fixture, change_set)
        root = self.fixture.root
        self.assertFalse(result.already_applied)
        self.assertEqual(("P-0003", "F-0002", "CIV-0002"), result.identifiers)
        self.assertEqual(
            ("data/people/P-0001.yaml", "data/document-inventory.yaml"),
            result.replaced,
        )
        self.assertEqual((SCAN_DESTINATION,), result.transferred)
        for relative in (
            "data/people/P-0003.yaml",
            "data/families/F-0002.yaml",
            "data/sources/civil/CIV-0002.yaml",
        ):
            self.assertTrue((root / relative).is_file(), relative)
        self.assertFalse((root / "research/entity-drafts/P-0003.yaml").exists())
        self.assertEqual(sha256(SCAN_BYTES), self.fixture.live_sha256(SCAN_DESTINATION))
        person = yaml.safe_load((root / "data/people/P-0001.yaml").read_text())
        self.assertEqual(["F-0001", "F-0002"], person["family_ids"])
        inventory = yaml.safe_load(
            (root / "data/document-inventory.yaml").read_text()
        )
        self.assertEqual(AUTHORISATION, inventory["documents"][0]["transfer"]["authorisation"])
        ledger = yaml.safe_load((root / "data/id-ledger.yaml").read_text())
        self.assertEqual([], ledger["reserved_ids"]["people"])
        self.assertEqual([], ledger["reserved_ids"]["civil"])
        self.assert_clean(self.fixture)

    def test_missing_back_reference_fails_staged_validation_unchanged(self) -> None:
        change_set = parent_family_change_set(self.fixture, person_replacement=False)
        before = self.fixture.snapshot()
        with self.assertRaisesRegex(
            AllocationError, r"^validate staged: prospective promotion is invalid"
        ) as raised:
            self.apply(self.fixture, change_set)
        self.assertIn("P-0001.family_ids omits F-0002", str(raised.exception))
        self.assertEqual(before, self.fixture.snapshot())

    def test_failure_after_any_write_restores_tree_byte_identically(self) -> None:
        real_apply_step = new_entity._apply_step
        writes = 0
        while True:
            writes += 1
            fixture = self.new_fixture()
            change_set = parent_family_change_set(fixture)
            before = fixture.snapshot()
            calls: list[str] = []

            def fail_after_k(*args: Any, limit: int = writes) -> None:
                if len(calls) == limit:
                    raise OSError(f"injected failure after {limit} writes")
                calls.append(args[2].action)
                real_apply_step(*args)

            with patch("scripts.new_entity._apply_step", side_effect=fail_after_k):
                try:
                    self.apply(fixture, change_set)
                except OSError:
                    failed = True
                else:
                    failed = False
            if not failed:
                break
            with self.subTest(after_writes=writes):
                self.assertEqual(before, fixture.snapshot())
        # 1 evidence copy + 3 draft links + 2 replacements + ledger + 3 draft removals.
        self.assertEqual(10, writes)

    def test_recover_rolls_back_an_interrupted_transaction(self) -> None:
        change_set = parent_family_change_set(self.fixture)
        before = self.fixture.snapshot()
        real_apply_step = new_entity._apply_step
        calls: list[str] = []

        def crash_after_four(*args: Any) -> None:
            if len(calls) == 4:
                raise SimulatedCrash()
            calls.append(args[2].action)
            real_apply_step(*args)

        with patch(
            "scripts.new_entity._apply_step", side_effect=crash_after_four
        ), patch("scripts.new_entity._rollback_transaction"):
            with self.assertRaises(SimulatedCrash):
                self.apply(self.fixture, change_set)
        root = self.fixture.root
        self.assertTrue((root / TRANSACTION_DIRECTORY).is_dir())
        self.assertFalse((root / TRANSACTION_DIRECTORY / "committed").exists())
        self.assertNotEqual(before, self.fixture.snapshot())

        # A killed process leaves its lock behind: nothing else may run.
        stale = dead_pid()
        lock = root / LOCK_FILENAME
        lock.write_text(f"pid: {stale}\nacquired_at: test\n", encoding="utf-8")
        with self.assertRaisesRegex(AllocationError, "unfinished|no longer running"):
            reserve_entity(root, "person", schema_dir=SCHEMA_DIR)
        self.assertEqual(f"pid: {stale}\nacquired_at: test\n", lock.read_text())

        recovery = recover_transaction(root)
        self.assertFalse(recovery.committed)
        self.assertEqual(stale, recovery.stale_lock_pid)
        self.assertEqual(("P-0003", "F-0002", "CIV-0002"), recovery.identifiers)
        self.assertTrue(lock.is_file(), "recover must not remove a stale lock")
        lock.unlink()
        self.assertEqual(before, self.fixture.snapshot())

    def test_recover_finalises_a_committed_transaction(self) -> None:
        change_set = parent_family_change_set(self.fixture)
        real_rmtree = shutil.rmtree

        def journal_cleanup_fails(path: Any, *args: Any, **kwargs: Any) -> None:
            if Path(path).name == TRANSACTION_DIRECTORY:
                raise OSError("injected cleanup failure")
            real_rmtree(path, *args, **kwargs)

        with patch("shutil.rmtree", side_effect=journal_cleanup_fails):
            with self.assertRaisesRegex(AllocationError, "^commit: .*recover"):
                self.apply(self.fixture, change_set)
        root = self.fixture.root
        self.assertTrue((root / TRANSACTION_DIRECTORY / "committed").is_file())
        applied = self.fixture.snapshot()

        recovery = recover_transaction(root)
        self.assertTrue(recovery.committed)
        self.assertEqual("synthetic parent family", recovery.label)
        self.assertEqual(("P-0003", "F-0002", "CIV-0002"), recovery.identifiers)
        applied = {
            path: digest
            for path, digest in applied.items()
            if not path.startswith(TRANSACTION_DIRECTORY)
        }
        self.assertEqual(applied, self.fixture.snapshot())
        self.assertTrue((root / "data/people/P-0003.yaml").is_file())
        self.assert_clean(self.fixture)

    def test_rollback_never_deletes_a_path_that_it_did_not_create(self) -> None:
        for racing_path in (SCAN_DESTINATION, "data/people/P-0003.yaml"):
            with self.subTest(racing_path=racing_path):
                fixture = self.new_fixture()
                (fixture.root / "evidence/civil").mkdir(parents=True)
                change_set = parent_family_change_set(fixture)
                before = fixture.snapshot()
                foreign = b"written by another process"
                real_apply_step = new_entity._apply_step

                def racing_writer(*args: Any, racing: str = racing_path) -> None:
                    step = args[2]
                    if step.target == fixture.root.resolve() / racing:
                        step.target.write_bytes(foreign)
                    real_apply_step(*args)

                with patch(
                    "scripts.new_entity._apply_step", side_effect=racing_writer
                ):
                    with self.assertRaisesRegex(
                        AllocationError, "^apply: refusing to overwrite"
                    ):
                        self.apply(fixture, change_set)
                self.assertEqual(
                    {**before, racing_path: sha256(foreign)}, fixture.snapshot()
                )

    def test_recover_leaves_an_unlogged_foreign_file_in_place(self) -> None:
        (self.fixture.root / "evidence/civil").mkdir(parents=True)
        change_set = parent_family_change_set(self.fixture)
        before = self.fixture.snapshot()
        foreign = b"written by another process"
        real_apply_step = new_entity._apply_step

        def race_then_crash(*args: Any) -> None:
            step = args[2]
            if step.action == "copy-evidence":
                step.target.write_bytes(foreign)
                raise SimulatedCrash()
            real_apply_step(*args)

        with patch(
            "scripts.new_entity._apply_step", side_effect=race_then_crash
        ), patch("scripts.new_entity._rollback_transaction"):
            with self.assertRaises(SimulatedCrash):
                self.apply(self.fixture, change_set)
        recovery = recover_transaction(self.fixture.root)
        self.assertEqual((SCAN_DESTINATION,), recovery.left_in_place)
        self.assertEqual(
            {**before, SCAN_DESTINATION: sha256(foreign)}, self.fixture.snapshot()
        )

    # T4 -----------------------------------------------------------------------

    def test_stale_replacement_is_rejected(self) -> None:
        change_set = parent_family_change_set(self.fixture)
        self.fixture.documents["people"]["P-0001"]["notes"] = [
            {"text": "Edited after the patch was written."}
        ]
        self.fixture.rewrite()
        before = self.fixture.snapshot()
        with self.assertRaisesRegex(
            AllocationError,
            "^resolve: stale replacement: data/people/P-0001.yaml changed since "
            "the patch was written",
        ):
            self.apply(self.fixture, change_set)
        self.assertEqual(before, self.fixture.snapshot())

    def test_concurrent_reserve_never_duplicates_an_identifier(self) -> None:
        fixture = AllocationFixture()
        self.addCleanup(fixture.cleanup)
        shutil.copytree(SCHEMA_DIR, fixture.root / "schemas")
        command = [
            sys.executable,
            str(PROJECT_ROOT / "scripts/new_entity.py"),
            "--root",
            str(fixture.root),
            "reserve",
            "person",
        ]
        processes = [
            subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            for _ in range(6)
        ]
        outputs = [(process.wait(), process.stdout.read()) for process in processes]
        for process in processes:
            process.stdout.close()
        reserved = []
        for returncode, output in outputs:
            if returncode == 0:
                reserved.append(output.split("reserved draft ", 1)[1].split()[0])
            else:
                self.assertIn("another entity transaction is running (pid", output)
        self.assertTrue(reserved)
        self.assertEqual(len(reserved), len(set(reserved)), outputs)
        self.assertEqual(sorted(reserved), fixture.read_ledger()["reserved_ids"]["people"])
        validation = validate_repository(fixture.root, schema_dir=SCHEMA_DIR)
        self.assertEqual((), validation.errors)
        self.assertFalse((fixture.root / LOCK_FILENAME).exists())

    def test_lock_held_by_a_running_or_dead_process_is_never_stolen(self) -> None:
        fixture = AllocationFixture()
        self.addCleanup(fixture.cleanup)
        lock = fixture.root / LOCK_FILENAME
        for pid, message in (
            (os.getpid(), "^lock: another entity transaction is running"),
            (dead_pid(), "no longer running; run the recover command, then remove"),
        ):
            with self.subTest(pid=pid):
                content = f"pid: {pid}\nacquired_at: test\n"
                lock.write_text(content, encoding="utf-8")
                with self.assertRaisesRegex(AllocationError, message):
                    reserve_entity(fixture.root, "person", schema_dir=SCHEMA_DIR)
                self.assertEqual(content, lock.read_text(encoding="utf-8"))
                self.assertEqual([], fixture.read_ledger()["reserved_ids"]["people"])

    # T5 -----------------------------------------------------------------------

    def test_evidence_without_authorisation_is_refused(self) -> None:
        for authorisation in (None, "", "   "):
            with self.subTest(authorisation=authorisation):
                fixture = self.new_fixture()
                change_set = parent_family_change_set(
                    fixture, authorisation=authorisation
                )
                before = fixture.snapshot()
                with self.assertRaisesRegex(
                    AllocationError,
                    "evidence transfer requires an owner authorisation reference",
                ):
                    self.apply(fixture, change_set)
                self.assertEqual(before, fixture.snapshot())

    def test_evidence_sha256_mismatch_is_refused(self) -> None:
        change_set = parent_family_change_set(
            self.fixture, declared_sha256=sha256(b"something else")
        )
        before = self.fixture.snapshot()
        with self.assertRaisesRegex(AllocationError, "^resolve: evidence sha256 mismatch"):
            self.apply(self.fixture, change_set)
        self.assertEqual(before, self.fixture.snapshot())

    def test_evidence_already_held_is_refused(self) -> None:
        for holder, held_path in (
            ("inventory", "evidence/civil/held.bin"),
            ("source", "evidence/civil/CIV-0001-held.bin"),
        ):
            with self.subTest(holder=holder):
                fixture = self.new_fixture()
                (fixture.root / held_path).parent.mkdir(parents=True)
                (fixture.root / held_path).write_bytes(SCAN_BYTES)
                if holder == "source":
                    fixture.documents["sources"]["CIV-0001"]["digital_file"] = {
                        "path": held_path,
                        "sha256": sha256(SCAN_BYTES),
                    }
                    fixture.rewrite()
                else:
                    document = inventory_document(held_path, sha256(SCAN_BYTES))
                    document.update(status="intake", proposed_source_id=None)
                    fixture.write_yaml(
                        "data/document-inventory.yaml",
                        {"version": 1, "documents": [document]},
                    )
                scan = fixture.write_producer_file("images/copy.bin", SCAN_BYTES)
                change_set = fixture.write_change_set(
                    {
                        "id": "re-file a held scan",
                        "evidence": [
                            {
                                "from": str(scan),
                                "sha256": sha256(SCAN_BYTES),
                                "to": "evidence/civil/CIV-0009-copy.bin",
                                "authorisation": AUTHORISATION,
                            }
                        ],
                    }
                )
                before = fixture.snapshot()
                expected_holder = "DOC-0001" if holder == "inventory" else "CIV-0001"
                with self.assertRaisesRegex(
                    AllocationError,
                    f"^resolve: duplicate evidence: .* already held by {expected_holder}",
                ):
                    self.apply(fixture, change_set)
                self.assertEqual(before, fixture.snapshot())

    def test_inventory_transfer_must_match_one_of_its_files(self) -> None:
        scan = self.fixture.root / "evidence/civil/transfer.bin"
        scan.parent.mkdir(parents=True)
        scan.write_bytes(SCAN_BYTES)
        for producer_sha256, expected_errors in (
            (sha256(SCAN_BYTES), 0),
            (sha256(b"a different producer file"), 1),
        ):
            with self.subTest(matches=expected_errors == 0):
                document = inventory_document(
                    "evidence/civil/transfer.bin",
                    sha256(SCAN_BYTES),
                    producer_sha256=producer_sha256,
                )
                document.update(status="reviewed", proposed_source_id=None)
                self.fixture.write_yaml(
                    "data/document-inventory.yaml",
                    {"version": 1, "documents": [document]},
                )
                validation = validate_repository(
                    self.fixture.root, schema_dir=SCHEMA_DIR
                )
                messages = [issue.message for issue in validation.errors]
                self.assertEqual(expected_errors, len(messages), messages)
                if expected_errors:
                    self.assertIn("transfer producer_sha256 matches none", messages[0])

    def test_inventory_transfer_schema_is_strict(self) -> None:
        scan = self.fixture.root / "evidence/civil/transfer.bin"
        scan.parent.mkdir(parents=True)
        scan.write_bytes(SCAN_BYTES)
        document = inventory_document("evidence/civil/transfer.bin", sha256(SCAN_BYTES))
        document.update(status="reviewed", proposed_source_id=None)
        document["transfer"].update(resolution="thumbnail", authorisation="x")
        self.fixture.write_yaml(
            "data/document-inventory.yaml", {"version": 1, "documents": [document]}
        )
        validation = validate_repository(self.fixture.root, schema_dir=SCHEMA_DIR)
        locations = sorted(issue.location.rsplit(".", 1)[1] for issue in validation.errors)
        self.assertEqual(["authorisation", "resolution"], locations)

    def test_change_set_introducing_a_new_warning_fails(self) -> None:
        self.fixture.reserve("people", "P-0003")
        duplicate = copy.deepcopy(self.fixture.documents["people"]["P-0001"])
        duplicate.update(id="P-0003", event_ids=[], family_ids=[])
        self.fixture.write_draft(duplicate)
        source = copy.deepcopy(self.fixture.documents["sources"]["CIV-0001"])
        source["linked_people"].append("P-0003")
        change_set = self.fixture.write_change_set(
            {
                "id": "duplicate name",
                "promote": ["P-0003"],
                "replace": [
                    self.fixture.replacement("data/sources/civil/CIV-0001.yaml", source)
                ],
            }
        )
        before = self.fixture.snapshot()
        with self.assertRaisesRegex(
            AllocationError,
            "^validate staged: new warning introduced: WARNING .*possible duplicate "
            "identity",
        ):
            self.apply(self.fixture, change_set)
        self.assertEqual(before, self.fixture.snapshot())

    def test_pre_existing_warning_does_not_fail_a_change_set(self) -> None:
        duplicate = copy.deepcopy(self.fixture.documents["people"]["P-0001"])
        duplicate.update(id="P-0003", event_ids=[], family_ids=[])
        self.fixture.documents["people"]["P-0003"] = duplicate
        self.fixture.documents["sources"]["CIV-0001"]["linked_people"].append("P-0003")
        self.fixture.rewrite()
        person = copy.deepcopy(self.fixture.documents["people"]["P-0002"])
        person["notes"] = [{"text": "Synthetic note added by a change set."}]
        change_set = self.fixture.write_change_set(
            {
                "id": "note only",
                "replace": [self.fixture.replacement("data/people/P-0002.yaml", person)],
            }
        )
        result = self.apply(self.fixture, change_set)
        self.assertEqual(1, len(result.warnings))
        self.assertIn("possible duplicate identity", result.warnings[0])
        self.assert_clean(self.fixture)

    # Idempotence, shape and pre-check -----------------------------------------

    def test_reapplying_an_applied_change_set_is_a_no_op(self) -> None:
        change_set = parent_family_change_set(self.fixture)
        self.apply(self.fixture, change_set)
        applied = self.fixture.snapshot()
        result = self.apply(self.fixture, change_set)
        self.assertTrue(result.already_applied)
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = new_entity.main(
                ["--root", str(self.fixture.root), "apply", str(change_set)]
            )
        self.assertEqual(0, exit_code)
        self.assertIn("already applied; nothing to do", output.getvalue())
        self.assertEqual(applied, self.fixture.snapshot())

    def test_change_set_shape_errors_are_reported_together(self) -> None:
        path = self.fixture.write_change_set(
            {
                "promote": "P-0003",
                "replace": [
                    {
                        "path": "data/../README.md",
                        "base_sha256": "not-a-hash",
                        "content_from": "missing.yaml",
                    },
                    {
                        "path": "data/id-ledger.yaml",
                        "base_sha256": "0" * 64,
                        "content_from": "missing.yaml",
                    },
                ],
                "evidence": [
                    {"from": "relative.bin", "sha256": "0" * 64, "to": "data/x.bin"}
                ],
                "extra": True,
            }
        )
        with self.assertRaises(AllocationError) as raised:
            load_change_set(path)
        message = str(raised.exception)
        for expected in (
            "$: unknown keys: extra",
            "$.id: a non-empty free-text label is required",
            "$.promote: must be a list",
            "$.replace[0].path: must not contain empty, '.' or '..' segments",
            "$.replace[0].base_sha256: must be a 64-character lowercase hex sha256",
            "$.replace[0].content_from: cannot be read",
            "$.replace[1].path: data/id-ledger.yaml is maintained by this tool",
            "$.evidence[0].from: must be an absolute file path",
            "$.evidence[0].to: must be under evidence/",
            "$.evidence[0].authorisation: evidence transfer requires an owner "
            "authorisation reference",
        ):
            self.assertIn(expected, message)

    def test_live_pre_check_names_the_operation(self) -> None:
        change_set = parent_family_change_set(self.fixture)
        self.fixture.ledger["version"] = 1
        self.fixture.write_yaml("data/id-ledger.yaml", self.fixture.ledger)
        with self.assertRaisesRegex(
            AllocationError,
            "^live pre-check: repository validation failed; the change set was not "
            "applied",
        ):
            self.apply(self.fixture, change_set)
        with self.assertRaisesRegex(
            AllocationError,
            "^live pre-check: repository validation failed; nothing was promoted",
        ):
            promote_entities(self.fixture.root, ["P-0003"], schema_dir=SCHEMA_DIR)


if __name__ == "__main__":
    unittest.main()
