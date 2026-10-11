"""Tests for the consumer-side retrieval-handoff intake verifier (synthetic drops only)."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import tempfile
import unittest
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import yaml

from scripts import intake

NOW = datetime(2026, 10, 11, 12, 0, tzinfo=timezone.utc)
EARLY = "2026-10-01T08:00:00.000000+00:00"
LATE = "2026-10-05T08:00:00.000000+00:00"
INTAKE_TEXT = "# Synthetic intake procedure\n\nStep one.\nStep two.\n"
NEW_INTAKE_TEXT = "# Synthetic intake procedure\n\nStep one.\nStep two, revised.\n"
CLASSES = {"STATUS.md": "status", intake.EVIDENCE_INDEX_NAME: "evidence_index", intake.INTAKE_TEXT_NAME: "methodology"}
VALID_SCAN = {
    "path": "scan-0001.jpg",
    "sha256": "b" * 64,
    "size": 10,
    "media_type": "image/jpeg",
    "aliases": [],
    "record": None,
    "page": None,
    "pages": None,
    "complete": None,
    "resolution": "max-res",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def as_bytes(content: str | bytes) -> bytes:
    return content.encode("utf-8") if isinstance(content, str) else content


def default_files(variant: str = "") -> dict[str, str]:
    return {
        "findings/alpha.md": f"Synthetic finding alpha{variant}.\n",
        "STATUS.md": f"Synthetic status{variant}.\n",
        intake.INTAKE_TEXT_NAME: INTAKE_TEXT,
    }


def expected_digest(files: dict[str, str | bytes]) -> str:
    text = "".join(f"{path}\t{sha(as_bytes(files[path]))}\n" for path in sorted(files))
    return sha(text.encode("utf-8"))


def build_manifest(files: dict[str, str | bytes], *, version: int, generated_at: str) -> dict:
    """A manifest for `files` in the v1 or legacy (v0) shape, consistent unless altered."""
    classes = {path: CLASSES.get(path, "findings") for path in files}
    counts = dict(sorted(Counter(classes.values()).items()))
    if version == 0:
        return {
            "generated_at": generated_at,
            "generator": "synthetic/generator.py",
            "design": "synthetic test drop",
            "total_files": len(files),
            "class_counts": counts,
            "files": sorted(files),
        }
    entries = [
        {"path": path, "class": classes[path], "size": len(as_bytes(files[path])), "sha256": sha(as_bytes(files[path]))}
        for path in sorted(files)
    ]
    return {
        "contract_version": version,
        "producer": "armond-genealogy-retrieval",
        "generator": "synthetic/generator.py",
        "source_commit": "a" * 40,
        "source_dirty": False,
        "generated_at": generated_at,
        "content_digest": expected_digest(files),
        "total_files": len(entries),
        "class_counts": counts,
        "files": entries,
    }


def write_manifest(drop: Path, manifest: dict) -> None:
    text = json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    (drop / intake.MANIFEST_NAME).write_text(text, encoding="utf-8")


def write_drop(
    drop: Path,
    contents: dict[str, str | bytes] | None = None,
    *,
    version: int = 1,
    generated_at: str = EARLY,
    **overrides: object,
) -> dict:
    """Write a synthetic drop (replacing its files) and return its manifest; `overrides` alter the manifest."""
    files = default_files() if contents is None else contents
    drop.mkdir(parents=True, exist_ok=True)
    for path in drop.rglob("*"):
        if path.is_file() or path.is_symlink():
            path.unlink()
    for rel, content in files.items():
        target = drop / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(as_bytes(content))
    manifest = build_manifest(files, version=version, generated_at=generated_at)
    manifest.update(overrides)
    write_manifest(drop, manifest)
    return manifest


def tree(root: Path) -> dict[str, tuple[str, int]]:
    """Map every file under `root` to (sha256, mtime_ns)."""
    return {
        path.relative_to(root).as_posix(): (sha(path.read_bytes()), path.stat().st_mtime_ns)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def add_nested_file(drop: Path) -> None:
    (drop / "notes").mkdir()
    (drop / "notes/extra.md").write_text("x\n", encoding="utf-8")


class IntakeCase(unittest.TestCase):
    """Fixture: a temporary repo_root with its own log and pin, and a synthetic drop."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._roots = 0
        self.fresh()
        patcher = mock.patch.object(intake.time, "sleep")
        self.sleep = patcher.start()
        self.addCleanup(patcher.stop)

    def fresh(self, pin_text: str | None = INTAKE_TEXT) -> None:
        """Point the fixture at a brand-new repo_root (for subTests)."""
        self._roots += 1
        self.root = Path(self._tmp.name) / f"repo-{self._roots}"
        self.drop = self.root / "drop"
        self.state = self.root / "state"
        self.log_path = self.root / intake.INTAKE_LOG
        self.pin_path = self.root / intake.INTAKE_PIN
        self.log_path.parent.mkdir(parents=True)
        self.log_path.write_text("# Synthetic header line.\ngenerations: []\n", encoding="utf-8")
        if pin_text is not None:
            pin = {"path": intake.INTAKE_TEXT_NAME, "sha256": sha(pin_text.encode()), "accepted_at": "2026-10-11",
                   "accepted_from_digest": None}
            self.pin_path.write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")

    def intake(self, *, strict: bool = True, retries: int = 2, **kwargs: object) -> intake.IntakeResult:
        return intake.run(
            self.drop, self.state, repo_root=self.root, strict=strict, retries=retries, wait=0.01, now=NOW, **kwargs
        )

    def log_entries(self) -> list[dict]:
        return yaml.safe_load(self.log_path.read_text(encoding="utf-8"))["generations"]

    def pinned(self) -> set[str]:
        snapshots = self.state / "snapshots"
        return {p.name for p in snapshots.iterdir()} if snapshots.is_dir() else set()

    def text(self, result: intake.IntakeResult) -> str:
        return "\n".join(result.messages)

    def assert_rejected(self, result: intake.IntakeResult, status: str, needle: str) -> None:
        self.assertEqual(intake.EXIT_INVALID, result.exit_code, self.text(result))
        self.assertEqual(status, result.status, self.text(result))
        self.assertIn(needle, self.text(result))
        self.assertEqual(set(), self.pinned())
        self.assertEqual([], self.log_entries())


class CorruptManifestTests(IntakeCase):  # C1
    def test_truncated_manifest_is_invalid_at_once(self) -> None:
        write_drop(self.drop)
        (self.drop / intake.MANIFEST_NAME).write_bytes(b'{"contract_version": 1, "files": [')
        result = self.intake()
        self.assert_rejected(result, "invalid", "INVALID: corrupt SYNC-MANIFEST.json")
        self.sleep.assert_not_called()

    def test_non_object_manifest_is_invalid(self) -> None:
        write_drop(self.drop)
        (self.drop / intake.MANIFEST_NAME).write_text("[1, 2, 3]\n", encoding="utf-8")
        self.assert_rejected(self.intake(), "invalid", "not an object")


class TornSnapshotTests(IntakeCase):  # C2
    def test_inconsistent_file_set_is_torn_after_retries(self) -> None:
        cases = [
            (1, "missing", lambda d: (d / "findings/alpha.md").unlink(), "listed file missing"),
            (1, "unexpected", lambda d: (d / "extra.md").write_text("x\n"), "unexpected file"),
            (1, "sha256", lambda d: (d / "STATUS.md").write_text("Synthetic statuX.\n"), "sha256 mismatch"),
            (1, "size", lambda d: (d / "STATUS.md").write_text("longer synthetic status\n"), "size mismatch"),
            (0, "legacy missing", lambda d: (d / "STATUS.md").unlink(), "listed file missing"),
            (0, "legacy unexpected", add_nested_file, "unexpected file"),
        ]
        for version, name, mutate, needle in cases:
            with self.subTest(name):
                self.fresh()
                self.sleep.reset_mock()
                write_drop(self.drop, version=version)
                mutate(self.drop)
                with mock.patch.object(intake, "_copy_drop", wraps=intake._copy_drop) as copy:
                    result = self.intake(retries=2)
                self.assert_rejected(result, "torn", intake.TORN_MESSAGE)
                self.assertIn(needle, self.text(result))
                self.assertEqual(3, copy.call_count)
                self.assertEqual(2, self.sleep.call_count)
                self.assertEqual([], [p for p in (self.state / "snapshots").iterdir()])


class ContractVersionTests(IntakeCase):  # C3
    def test_v1_and_legacy_are_accepted_with_the_same_digest(self) -> None:
        digest = expected_digest(default_files())
        for version in (1, 0):
            with self.subTest(version=version):
                self.fresh()
                write_drop(self.drop, version=version)
                result = self.intake()
                self.assertEqual(intake.EXIT_OK, result.exit_code, self.text(result))
                self.assertEqual("accepted", result.status)
                self.assertEqual(digest, result.digest)
                self.assertIn(f"OK: pinned {digest} (contract v{version}, 3 files)", self.text(result))
                self.assertIn("read the handoff from state/snapshots/" + digest, self.text(result))
                entry = self.log_entries()[0]
                self.assertEqual(version, entry["contract_version"])
                self.assertEqual("a" * 40 if version else None, entry["source_commit"])
                self.assertEqual(False if version else None, entry["source_dirty"])

    def test_unsupported_contract_version_is_rejected(self) -> None:
        write_drop(self.drop, contract_version=2)
        self.assert_rejected(self.intake(), "invalid", "unsupported contract_version")

    def test_wrong_content_digest_is_rejected(self) -> None:
        write_drop(self.drop, content_digest="0" * 64)
        self.assert_rejected(self.intake(), "invalid", "content_digest does not recompute")

    def test_count_mismatches_are_rejected(self) -> None:
        cases = [
            (1, {"total_files": 4}, "total_files"),
            (0, {"total_files": 2}, "total_files"),
            (1, {"class_counts": {"findings": 3}}, "class_counts"),
        ]
        for version, override, needle in cases:
            with self.subTest(version=version, override=override):
                self.fresh()
                write_drop(self.drop, version=version, **override)
                self.assert_rejected(self.intake(), "invalid", needle)

    def test_v1_schema_and_legacy_shape_failures_are_rejected(self) -> None:
        cases = [
            (1, {"producer": "someone-else"}, "fails the v1 schema"),
            (1, {"unexpected_key": True}, "fails the v1 schema"),
            (0, {"unexpected_key": True}, "legacy manifest shape"),
            (0, {"files": [1, 2, 3]}, "legacy manifest shape"),
            (0, {"total_files": "3"}, "legacy manifest shape"),
            (0, {"generated_at": "yesterday"}, "generated_at is not an ISO-8601 timestamp"),
        ]
        for version, override, needle in cases:
            with self.subTest(version=version, override=override):
                self.fresh()
                write_drop(self.drop, version=version, **override)
                self.assert_rejected(self.intake(), "invalid", needle)


class ConfinementTests(IntakeCase):  # C4
    UNSAFE = ["../x.md", "/abs/x.md", ".hidden/x.md", "sub/.git/x.md", "a\\b.md", "a//b.md"]

    def test_unsafe_listed_paths_are_rejected(self) -> None:
        for version in (0, 1):
            for path in self.UNSAFE:
                with self.subTest(version=version, path=path):
                    self.fresh()
                    manifest = write_drop(self.drop, version=version)
                    if version:
                        manifest["files"].append({"path": path, "class": "findings", "size": 1, "sha256": "c" * 64})
                    else:
                        manifest["files"].append(path)
                    manifest["total_files"] += 1
                    write_manifest(self.drop, manifest)
                    result = self.intake()
                    self.assert_rejected(result, "invalid", "INVALID:")
                    # v1 is caught by the schema pattern or, failing that, by the code-level check
                    self.assertRegex(self.text(result), "fails the v1 schema|unsafe path" if version else "unsafe path")

    def test_check_confined_rejects_each_unsafe_form(self) -> None:
        root = Path(self._tmp.name) / "confined"
        (root / "inside").mkdir(parents=True)
        outside = Path(self._tmp.name) / "outside"
        outside.mkdir()
        (root / "escape").symlink_to(outside, target_is_directory=True)
        self.assertEqual("inside/a.md", intake.check_confined("inside/a.md", root))
        for path in [*self.UNSAFE, "", "a/", ".", "x\x00.md", "escape/a.md", None]:
            with self.subTest(path=path), self.assertRaises(intake.InvalidHandoff):
                intake.check_confined(path, root)

    def test_symlinks_in_the_drop_are_rejected(self) -> None:
        outside = Path(self._tmp.name) / "outside.md"
        outside.write_text("Synthetic outside file.\n", encoding="utf-8")

        def listed_file_link(drop: Path) -> None:
            (drop / "STATUS.md").unlink()
            (drop / "STATUS.md").symlink_to(drop / "findings/alpha.md")

        def unlisted_outside_link(drop: Path) -> None:
            (drop / "elsewhere.md").symlink_to(outside)

        def directory_link(drop: Path) -> None:
            (drop / "linked-dir").symlink_to(drop / "findings", target_is_directory=True)

        for version in (0, 1):
            for make_link in (listed_file_link, unlisted_outside_link, directory_link):
                with self.subTest(version=version, case=make_link.__name__):
                    self.fresh()
                    write_drop(self.drop, version=version)
                    make_link(self.drop)
                    self.assert_rejected(self.intake(), "invalid", "symlink in the handoff")


class ChannelATextOnlyTests(IntakeCase):  # Channel A: no evidence binaries
    def test_a_scan_in_the_handoff_is_rejected(self) -> None:
        for version in (0, 1):
            with self.subTest(version=version):
                self.fresh()
                files = default_files()
                files["findings/scan.jpg"] = b"\xff\xd8\xff synthetic"
                write_drop(self.drop, files, version=version)
                result = self.intake()
                self.assert_rejected(result, "invalid", "INVALID:")
                self.assertIn("Channel A carries text only", self.text(result))

    def test_non_utf8_markdown_is_rejected(self) -> None:
        for version in (0, 1):
            with self.subTest(version=version):
                self.fresh()
                files = default_files()
                files["findings/latin1.md"] = "Jos\u00e9".encode("latin-1")
                write_drop(self.drop, files, version=version)
                result = self.intake()
                self.assert_rejected(result, "invalid", "INVALID:")
                self.assertIn("not valid UTF-8", self.text(result))

    def test_finder_metadata_is_ignored(self) -> None:
        write_drop(self.drop)
        (self.drop / ".DS_Store").write_bytes(b"synthetic finder metadata")
        result = self.intake()
        self.assertEqual(result.exit_code, 0, self.text(result))


class ConcurrentSyncTests(IntakeCase):  # C5
    def test_sync_during_the_copy_is_retried_then_accepted(self) -> None:
        write_drop(self.drop)
        updated = default_files(" v2")
        real_copy = intake._copy_drop
        calls: list[Path] = []

        def syncing_copy(src: Path, dst: Path) -> None:
            calls.append(dst)
            real_copy(src, dst)
            if len(calls) == 1:  # the producer re-syncs mid-copy
                write_drop(self.drop, updated, generated_at=LATE)

        with mock.patch.object(intake, "_copy_drop", side_effect=syncing_copy):
            result = self.intake()
        self.assertEqual(intake.EXIT_OK, result.exit_code, self.text(result))
        self.assertEqual(2, len(calls))
        self.assertEqual(1, self.sleep.call_count)
        self.assertIn("changed during the copy", self.text(result))
        self.assertEqual(expected_digest(updated), result.digest)
        self.assertEqual(LATE, self.log_entries()[0]["generated_at"])

    def test_a_drop_that_keeps_changing_is_torn(self) -> None:
        write_drop(self.drop)
        real_copy = intake._copy_drop
        calls: list[Path] = []

        def always_syncing(src: Path, dst: Path) -> None:
            calls.append(dst)
            real_copy(src, dst)
            write_drop(self.drop, default_files(f" v{len(calls)}"), generated_at=LATE)

        with mock.patch.object(intake, "_copy_drop", side_effect=always_syncing):
            result = self.intake(retries=3)
        self.assert_rejected(result, "torn", intake.TORN_MESSAGE)
        self.assertEqual(4, len(calls))
        self.assertEqual(3, self.sleep.call_count)

    def test_pinned_snapshot_is_immune_to_later_syncs(self) -> None:
        write_drop(self.drop)
        result = self.intake()
        self.assertEqual(intake.EXIT_OK, result.exit_code, self.text(result))
        assert result.snapshot is not None
        self.assertEqual(self.state / "snapshots" / result.digest, result.snapshot)
        before = {path: digest for path, (digest, _) in tree(result.snapshot).items()}
        write_drop(self.drop, {"findings/alpha.md": "Rewritten.\n"}, generated_at=LATE)
        after = {path: digest for path, (digest, _) in tree(result.snapshot).items()}
        self.assertEqual(before, after)
        self.assertEqual(sha(b"Synthetic status.\n"), after["STATUS.md"])

    def test_intake_never_writes_to_the_drop(self) -> None:
        write_drop(self.drop, version=0)
        before = tree(self.drop)
        for strict in (True, False):
            self.intake(strict=strict)
        self.assertEqual(before, tree(self.drop))


class LegacyTornDetectionTests(IntakeCase):  # C5, legacy manifests carry no hashes
    def test_a_file_rewritten_during_the_copy_is_detected_without_manifest_change(self) -> None:
        write_drop(self.drop, version=0)
        original = intake._copy_drop
        calls = {"n": 0}

        def copy_while_syncing(drop: Path, target: Path) -> None:
            original(drop, target)
            calls["n"] += 1
            if calls["n"] == 1:  # a sync rewrites one file during the first copy only
                victim = next(p for p in sorted(drop.rglob("*.md")) if p.name != intake.INTAKE_TEXT_NAME)
                victim.write_text("rewritten by a concurrent sync, longer than before\n", encoding="utf-8")

        with mock.patch.object(intake, "_copy_drop", copy_while_syncing):
            result = self.intake()
        self.assertEqual(result.exit_code, 0, self.text(result))
        self.assertGreaterEqual(calls["n"], 2, "the torn first copy was not retried")


class GenerationTests(IntakeCase):  # C6
    def test_a_second_run_is_already_ingested(self) -> None:
        write_drop(self.drop)
        first = self.intake()
        second = self.intake()
        self.assertEqual(intake.EXIT_OK, second.exit_code, self.text(second))
        self.assertEqual("replay", second.status)
        self.assertIn(f"ALREADY INGESTED: {first.digest}; no-op", self.text(second))
        self.assertEqual(1, len(self.log_entries()))

    def test_an_older_generation_is_stale(self) -> None:
        for strict in (True, False):
            with self.subTest(strict=strict):
                self.fresh()
                write_drop(self.drop, generated_at=LATE)
                newer = self.intake()
                write_drop(self.drop, default_files(" old"), generated_at=EARLY)
                result = self.intake(strict=strict)
                self.assertIn(intake.STALE_MESSAGE, self.text(result))
                if strict:
                    self.assertEqual(intake.EXIT_STALE, result.exit_code)
                    self.assertEqual([newer.digest], [e["content_digest"] for e in self.log_entries()])
                    self.assertEqual({newer.digest}, self.pinned())
                else:
                    self.assertEqual(intake.EXIT_OK, result.exit_code)
                    self.assertIn("WARNING: STALE", self.text(result))
                    self.assertEqual(["accepted", "stale"], [e["status"] for e in self.log_entries()])
                    self.assertIn(result.digest, self.pinned())
                    self.intake(strict=False)  # the same stale generation is not re-recorded
                    self.assertEqual(2, len(self.log_entries()))

    def test_the_log_records_identity_only_and_keeps_its_header(self) -> None:
        write_drop(self.drop)
        result = self.intake()
        text = self.log_path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# Synthetic header line.\n"))
        for leaked in ("findings/alpha.md", "STATUS.md", "Synthetic finding", "Step one"):
            self.assertNotIn(leaked, text)
        entry = self.log_entries()[0]
        self.assertEqual(
            [
                "content_digest", "contract_version", "source_commit", "source_dirty", "generated_at",
                "accepted_at", "total_files", "class_counts", "intake_text_sha256", "status",
            ],
            list(entry),
        )
        self.assertEqual(result.digest, entry["content_digest"])
        self.assertEqual("2026-10-11T12:00:00+00:00", entry["accepted_at"])
        self.assertEqual({"findings": 1, "methodology": 1, "status": 1}, entry["class_counts"])
        self.assertEqual(sha(INTAKE_TEXT.encode()), entry["intake_text_sha256"])
        self.assertEqual("accepted", entry["status"])

    def test_only_the_three_most_recent_snapshots_are_kept(self) -> None:
        digests = []
        for day in range(1, 6):
            write_drop(self.drop, default_files(f" day {day}"), generated_at=f"2026-10-0{day}T08:00:00+00:00")
            digests.append(self.intake().digest)
        self.assertEqual(set(digests[-3:]), self.pinned())
        self.assertEqual(5, len(self.log_entries()))


class AbsentHandoffTests(IntakeCase):  # C7
    def test_missing_handoff_blocks_only_under_strict(self) -> None:
        layouts = {
            "absent": lambda: None,
            "empty": lambda: self.drop.mkdir(),
            "no manifest": lambda: (self.drop.mkdir(), (self.drop / "STATUS.md").write_text("x\n")),
        }
        for name, make in layouts.items():
            with self.subTest(name):
                self.fresh()
                make()
                strict = self.intake(strict=True)
                self.assertEqual(intake.EXIT_BLOCKED, strict.exit_code)
                self.assertEqual(["BLOCKED: no retrieval handoff at drop"], strict.messages)
                relaxed = self.intake(strict=False)
                self.assertEqual(intake.EXIT_OK, relaxed.exit_code)
                self.assertTrue(relaxed.messages[0].startswith("INFO: no retrieval handoff at drop"))
                for result in (strict, relaxed):
                    self.assertNotIn("Nothing to check", self.text(result))
                self.assertFalse(self.state.exists())

    def test_cli_exit_codes_for_a_missing_handoff(self) -> None:
        missing = Path(self._tmp.name) / "missing-drop"
        state = Path(self._tmp.name) / "cli-state"
        for argv, code, stream in (([], 0, "out"), (["--strict"], 2, "err")):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(code, intake.main(["--drop", str(missing), "--state", str(state), *argv]))
            printed = (out if stream == "out" else err).getvalue()
            self.assertIn("no retrieval handoff at", printed)
            self.assertNotIn("Nothing to check", out.getvalue() + err.getvalue())
        self.assertFalse(state.exists())


class IntakeInstructionTests(IntakeCase):  # O4
    def drifted_drop(self) -> None:
        files = default_files()
        files[intake.INTAKE_TEXT_NAME] = NEW_INTAKE_TEXT
        write_drop(self.drop, files)
        self.state.mkdir(parents=True)
        (self.state / intake.ACCEPTED_INTAKE_COPY).write_text(INTAKE_TEXT, encoding="utf-8")

    def test_drift_exits_5_under_strict_before_pinning(self) -> None:
        self.drifted_drop()
        pin_before = self.pin_path.read_text(encoding="utf-8")
        result = self.intake()
        self.assertEqual(intake.EXIT_DRIFT, result.exit_code, self.text(result))
        old, new = sha(INTAKE_TEXT.encode())[:12], sha(NEW_INTAKE_TEXT.encode())[:12]
        self.assertIn(
            f"DRIFT: the producer's intake instructions changed ({old}… → {new}…). "
            "Review the change, then re-run with --accept-intake.",
            self.text(result),
        )
        self.assertIn("-Step two.\n+Step two, revised.", self.text(result))
        self.assertEqual(set(), self.pinned())
        self.assertEqual([], self.log_entries())
        self.assertEqual(pin_before, self.pin_path.read_text(encoding="utf-8"))

    def test_drift_is_a_warning_without_strict(self) -> None:
        self.drifted_drop()
        pin_before = self.pin_path.read_text(encoding="utf-8")
        result = self.intake(strict=False)
        self.assertEqual(intake.EXIT_OK, result.exit_code, self.text(result))
        self.assertIn("DRIFT:", self.text(result))
        self.assertEqual(pin_before, self.pin_path.read_text(encoding="utf-8"))
        self.assertEqual(sha(NEW_INTAKE_TEXT.encode()), self.log_entries()[0]["intake_text_sha256"])

    def test_accept_intake_updates_the_pin(self) -> None:
        self.drifted_drop()
        result = self.intake(accept_intake=True)
        self.assertEqual(intake.EXIT_OK, result.exit_code, self.text(result))
        self.assertEqual(
            {
                "path": intake.INTAKE_TEXT_NAME,
                "sha256": sha(NEW_INTAKE_TEXT.encode()),
                "accepted_at": "2026-10-11",
                "accepted_from_digest": result.digest,
            },
            json.loads(self.pin_path.read_text(encoding="utf-8")),
        )
        self.assertEqual(NEW_INTAKE_TEXT, (self.state / intake.ACCEPTED_INTAKE_COPY).read_text(encoding="utf-8"))
        again = self.intake()
        self.assertEqual("replay", again.status, self.text(again))
        self.assertNotIn("DRIFT", self.text(again))

    def test_a_missing_pin_counts_as_drift(self) -> None:
        self.fresh(pin_text=None)
        write_drop(self.drop)
        result = self.intake()
        self.assertEqual(intake.EXIT_DRIFT, result.exit_code)
        self.assertIn("(none → ", self.text(result))

    def test_matching_text_seeds_the_review_copy(self) -> None:
        write_drop(self.drop)
        result = self.intake()
        self.assertEqual(intake.EXIT_OK, result.exit_code, self.text(result))
        self.assertNotIn("DRIFT", self.text(result))
        self.assertEqual(INTAKE_TEXT, (self.state / intake.ACCEPTED_INTAKE_COPY).read_text(encoding="utf-8"))


class EvidenceIndexTests(IntakeCase):
    def index(self, scans: list[dict]) -> str:
        return json.dumps(
            {"contract_version": 1, "producer": "armond-genealogy-retrieval", "root": "research/evidence/images",
             "scans": scans}
        )

    def test_an_evidence_index_failing_its_schema_is_invalid(self) -> None:
        for version in (0, 1):
            with self.subTest(version=version):
                self.fresh()
                files = default_files()
                files[intake.EVIDENCE_INDEX_NAME] = self.index([{"path": "scan-0001.jpg"}])
                write_drop(self.drop, files, version=version)
                self.assert_rejected(self.intake(), "invalid", "EVIDENCE-INDEX.json fails the evidence-index schema")

    def test_a_valid_evidence_index_is_accepted(self) -> None:
        files = default_files()
        files[intake.EVIDENCE_INDEX_NAME] = self.index([VALID_SCAN])
        write_drop(self.drop, files)
        result = self.intake()
        self.assertEqual(intake.EXIT_OK, result.exit_code, self.text(result))
        self.assertEqual(1, self.log_entries()[0]["class_counts"]["evidence_index"])


class LocalStateTests(IntakeCase):
    def test_state_inside_the_drop_is_refused(self) -> None:
        write_drop(self.drop)
        before = tree(self.drop)
        result = intake.run(self.drop, self.drop / "state", repo_root=self.root, strict=True, now=NOW)
        self.assertEqual(intake.EXIT_INVALID, result.exit_code)
        self.assertIn("lies inside the drop", self.text(result))
        self.assertEqual(before, tree(self.drop))

    def test_a_malformed_log_is_an_error(self) -> None:
        write_drop(self.drop)
        self.log_path.write_text("generations: {not: a list}\n", encoding="utf-8")
        result = self.intake()
        self.assertEqual(intake.EXIT_INVALID, result.exit_code)
        self.assertIn("ERROR: local intake state", self.text(result))
        self.assertEqual(set(), self.pinned())

    def test_content_digest_formula(self) -> None:
        entries = [("b.md", "2" * 64), ("a.md", "1" * 64)]
        text = f"a.md\t{'1' * 64}\nb.md\t{'2' * 64}\n"
        self.assertEqual(sha(text.encode("utf-8")), intake.content_digest(entries))
        self.assertTrue(os.access(intake.SCHEMA_DIR / intake.MANIFEST_SCHEMA, os.R_OK))


if __name__ == "__main__":
    unittest.main()
