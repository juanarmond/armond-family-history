"""The public triage index and the content-identity audits (plan §11.1; §16 T1, T2, C7).

Synthetic fixtures only: no real records, names or producer files.
"""

from __future__ import annotations

import copy
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from producer_scans import HashCache, scan_files  # noqa: E402
from triage_audit import find_untriaged  # noqa: E402

from tests.test_validate_data import RepositoryFixture  # noqa: E402

SHA_A = hashlib.sha256(b"synthetic page a").hexdigest()


def entry(**overrides) -> dict:
    base = {
        "sha256": SHA_A,
        "size": 16,
        "media_type": "image/jpeg",
        "producer_path": "evidence/images/synthetic-a.jpg",
        "disposition": "reviewed-lead",
        "target_ids": [],
        "decided": "2026-10-11",
        "source": "synthetic-test",
    }
    base.update(overrides)
    return base


class TriageIndexValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def write_index(self, entries: list[dict]) -> None:
        path = self.fixture.root / "data" / "triage-index.yaml"
        path.write_text(yaml.safe_dump({"version": 1, "generated": "2026-10-11", "entries": entries}), encoding="utf-8")

    def messages(self) -> list[str]:
        return [issue.message for issue in self.fixture.validate().issues if issue.severity == "error"]

    def test_valid_index_passes(self) -> None:
        self.write_index([entry()])
        self.assertEqual([m for m in self.messages() if "triage" in m.lower() or "sha256" in m], [])

    def test_duplicate_sha256_is_an_error(self) -> None:
        self.write_index([entry(), entry()])
        self.assertTrue(any("duplicate sha256" in m for m in self.messages()))

    def test_promoted_requires_held_bytes_and_targets(self) -> None:
        self.write_index([entry(disposition="promoted", target_ids=["CIV-0001"])])
        self.assertTrue(any("no source, FAN or inventory file holds" in m for m in self.messages()))

    def test_held_file_must_not_be_marked_rejected(self) -> None:
        evidence = self.fixture.root / "evidence" / "civil" / "synthetic.jpg"
        evidence.parent.mkdir(parents=True)
        evidence.write_bytes(b"synthetic page a")
        source = self.fixture.documents["sources"]["CIV-0001"]
        source["digital_file"] = {"path": "evidence/civil/synthetic.jpg", "sha256": SHA_A}
        self.fixture.rewrite()
        self.write_index([entry(disposition="rejected")])
        self.assertTrue(any("held as evidence by CIV-0001" in m for m in self.messages()))

    def test_unknown_target_is_an_error(self) -> None:
        self.write_index([entry(disposition="fan", target_ids=["FAN-0999"])])
        self.assertTrue(any("target FAN-0999 does not exist" in m for m in self.messages()))

    def test_schema_rejects_free_text_dispositions(self) -> None:
        self.write_index([entry(disposition="catalogued as the 1900 deed")])
        self.assertTrue(any("is not one of" in m for m in self.messages()))


class ContentIdentityAuditTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.producer = Path(self.tmp.name) / "producer"
        (self.producer / "research" / "evidence" / "images").mkdir(parents=True)
        (self.producer / "research" / "resources").mkdir(parents=True)
        self.cache = HashCache(Path(self.tmp.name) / "cache.json")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_a_renamed_file_keeps_its_disposition(self) -> None:
        images = self.producer / "research" / "evidence" / "images"
        (images / "old-name.jpg").write_bytes(b"synthetic page a")
        triaged = {SHA_A}
        self.assertEqual(find_untriaged(scan_files(self.producer), triaged, set(), self.cache), [])
        (images / "old-name.jpg").rename(images / "new-name-after-rename.jpg")
        self.assertEqual(find_untriaged(scan_files(self.producer), triaged, set(), self.cache), [])

    def test_a_new_file_is_untriaged_until_recorded(self) -> None:
        images = self.producer / "research" / "evidence" / "images"
        (images / "new.jpg").write_bytes(b"synthetic page b")
        self.assertEqual([p.name for p in find_untriaged(scan_files(self.producer), {SHA_A}, set(), self.cache)], ["new.jpg"])

    def test_strict_audits_fail_when_the_producer_is_unreadable(self) -> None:
        env = dict(os.environ, ARMOND_PRODUCER_ROOT=str(Path(self.tmp.name) / "absent"))
        for script in ("triage_audit.py", "drop_page_audit.py"):
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / script), "--strict"],
                cwd=ROOT, env=env, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2, (script, result.stdout, result.stderr))
            self.assertIn("BLOCKED", result.stdout)
            self.assertNotIn("Nothing to check", result.stdout)


if __name__ == "__main__":
    unittest.main()
