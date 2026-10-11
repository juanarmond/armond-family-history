#!/usr/bin/env python3
"""Consumer-side intake verifier for the retrieval handoff (Channel A).

The producer (armond-genealogy-retrieval) mirrors a text-only handoff into the
gitignored drop `research/from-retrieval/` with `rsync -av --delete`, so the
drop can change under a reader at any moment. This tool makes intake safe:

1. snapshot the whole drop into the local intake state (symlinks copied as links);
2. verify the snapshot — never the live drop — against its SYNC-MANIFEST.json
   (contract v1, or the legacy v0 shape during the migration window): shape,
   path confinement, no symlinks, the exact file set, sizes and SHA-256, the
   content digest and counts, and the EVIDENCE-INDEX.json schema;
3. pin the verified snapshot by content digest at `<state>/snapshots/<digest>/`
   and keep only the most recent pins;
4. record the generation in the tracked, public
   `research/integration/intake-log.yaml` — identity and counts only, never file
   contents or file lists;
5. compare the producer's INTAKE-FOR-GENEALOGY-REPO.md with the owner-accepted
   SHA-256 in `research/integration/accepted-intake.json` (owner decision O4).

Sync is not promotion. This tool never writes to the drop, never promotes
anything into data/ or evidence/, never runs Git and never uses the network.
Agents read the pinned snapshot it reports, never the live drop. The producer's
intake text governs intake procedure only; it has no authority over evidence,
conclusions or this repository's rules.

A torn snapshot (the manifest changed during the copy, a listed file is missing,
an unexpected file appears, or a v1 size/hash mismatch) is retried; an invalid
one (corrupt JSON, schema or shape failure, unsafe path, symlink, unsupported
version, digest or count mismatch) fails at once.

Exit codes:
    0  ok: accepted, already ingested, or (without --strict) no handoff / warnings
    2  blocked: no retrieval handoff (--strict only)
    3  invalid or torn handoff, or unreadable local intake state
    4  stale: an older generation than the last accepted (--strict only)
    5  the producer's intake instructions drifted from the pin (--strict only)

Usage:
    uv run --frozen python scripts/intake.py [--drop research/from-retrieval]
        [--state research/.intake] [--strict] [--retries N] [--wait S] [--accept-intake]
"""
from __future__ import annotations

import argparse
import difflib
import functools
import hashlib
import json
import os
import re
import shutil
import sys
import time
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "research" / "integration" / "schemas"
MANIFEST_SCHEMA = "sync-manifest.v1.schema.json"
EVIDENCE_INDEX_SCHEMA = "evidence-index.v1.schema.json"

DEFAULT_DROP = Path("research/from-retrieval")
DEFAULT_STATE = Path("research/.intake")
INTAKE_LOG = Path("research/integration/intake-log.yaml")
INTAKE_PIN = Path("research/integration/accepted-intake.json")

MANIFEST_NAME = "SYNC-MANIFEST.json"
EVIDENCE_INDEX_NAME = "EVIDENCE-INDEX.json"
INTAKE_TEXT_NAME = "INTAKE-FOR-GENEALOGY-REPO.md"
ACCEPTED_INTAKE_COPY = "accepted-intake.md"
KEEP_SNAPSHOTS = 3

EXIT_OK = 0
EXIT_BLOCKED = 2
EXIT_INVALID = 3
EXIT_STALE = 4
EXIT_DRIFT = 5

TORN_MESSAGE = "TORN: the handoff kept changing during intake; retry later"
STALE_MESSAGE = "STALE: older generation than the last accepted"
LEGACY_KEYS: dict[str, type] = {
    "generated_at": str,
    "generator": str,
    "design": str,
    "total_files": int,
    "class_counts": dict,
    "files": list,
}
SHA256_RE = re.compile(r"[0-9a-f]{64}")
LOG_HEADER = """\
# Retrieval-handoff intake log, written by scripts/intake.py (do not hand-edit).
#
# One entry per verified handoff generation: its content digest, contract
# version, producer commit, timestamps, counts and the SHA-256 of the producer's
# intake instructions. This file is tracked and public, so it never holds file
# contents or file lists. The pinned snapshots live in the local intake state
# (default research/.intake/snapshots/<digest>/). Sync is not promotion: an
# accepted generation is verified raw material, not evidence.
"""
STDERR_PREFIXES = ("WARNING", "BLOCKED", "INVALID", "TORN", "STALE", "DRIFT", "ERROR")


class IntakeError(Exception):
    """Base class for intake failures."""


class InvalidHandoff(IntakeError):
    """The handoff is malformed or unsafe; retrying cannot help."""


class TornHandoff(IntakeError):
    """The snapshot caught the drop mid-sync; a retry may succeed."""


class LocalStateError(IntakeError):
    """The consumer's own intake log, pin or state is unreadable or misplaced."""


@dataclass
class Verified:
    """The identity of a verified snapshot."""

    contract_version: int
    digest: str
    generated_at: str
    source_commit: str | None
    source_dirty: bool | None
    total_files: int
    class_counts: dict[str, int]


@dataclass
class IntakeResult:
    """Outcome of one intake run; `messages` are the lines the CLI prints."""

    exit_code: int
    status: str  # absent | blocked | invalid | torn | drift | stale | replay | accepted
    messages: list[str] = field(default_factory=list)
    digest: str | None = None
    contract_version: int | None = None
    snapshot: Path | None = None


# --- hashing and paths -------------------------------------------------------


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file's bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def content_digest(entries: Iterable[tuple[str, str]]) -> str:
    """SHA-256 of one `<path>\\t<sha256>\\n` line per file, sorted by path."""
    text = "".join(f"{path}\t{sha}\n" for path, sha in sorted(entries, key=lambda e: e[0]))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_confined(path: object, root: Path) -> str:
    """Return `path` if it is a safe relative POSIX path that stays inside `root`."""
    if not isinstance(path, str) or not path:
        raise InvalidHandoff(f"unsafe path {path!r}: not a non-empty string")
    parts = path.split("/")
    reasons = []
    if "\x00" in path:
        reasons.append("NUL byte")
    if path.startswith("/"):
        reasons.append("absolute path")
    if "\\" in path:
        reasons.append("backslash")
    if ".." in parts:
        reasons.append("'..' segment")
    if any(part.startswith(".") and part != ".." for part in parts):
        reasons.append("hidden segment")
    if "" in parts and not path.startswith("/"):
        reasons.append("empty segment")
    if reasons:
        raise InvalidHandoff(f"unsafe path {path!r}: {', '.join(reasons)}")
    if not (root / path).resolve().is_relative_to(root.resolve()):
        raise InvalidHandoff(f"unsafe path {path!r}: resolves outside the handoff")
    return path


# Operating-system metadata a local file browser may leave in the drop; never part
# of a handoff, so it is neither counted as unexpected nor read.
IGNORED_NAMES = frozenset({".DS_Store"})


def scan_tree(root: Path) -> set[str]:
    """Return every regular file under `root` as a relative POSIX path.

    Raises InvalidHandoff on any symlink (file or directory) or special file, so
    nothing downstream ever follows a link out of the snapshot. Files named in
    IGNORED_NAMES are skipped.
    """
    files: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(dirpath)
        for name in dirnames + filenames:
            entry = base / name
            if entry.is_symlink():
                raise InvalidHandoff(f"symlink in the handoff: {entry.relative_to(root).as_posix()}")
        for name in filenames:
            if name in IGNORED_NAMES:
                continue
            entry = base / name
            rel = entry.relative_to(root).as_posix()
            if not entry.is_file():
                raise InvalidHandoff(f"not a regular file in the handoff: {rel}")
            files.add(rel)
    return files


def _tree_hashes(root: Path) -> dict[str, str]:
    """Map each entry under `root` to its SHA-256 (links marked, never followed)."""
    hashes: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(dirpath)
        for name in dirnames + filenames:
            entry = base / name
            rel = entry.relative_to(root).as_posix()
            if entry.is_symlink():
                hashes[rel] = "symlink"
            elif entry.is_file():
                hashes[rel] = sha256_file(entry)
    return hashes


def _under(root: Path, path: Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else root / path


def _show(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _remove(path: Path | None) -> None:
    if path is None or not (path.exists() or path.is_symlink()):
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def _parse_time(value: object) -> datetime:
    """Parse an ISO-8601 timestamp (naive values are taken as UTC)."""
    moment = value if isinstance(value, datetime) else datetime.fromisoformat(str(value))
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def _write_atomic(path: Path, data: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)
    os.replace(temporary, path)


# --- manifest verification -----------------------------------------------------


@functools.cache
def _validator(schema_name: str) -> Draft202012Validator:
    schema = json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _schema_errors(schema_name: str, document: object) -> str | None:
    errors = sorted(_validator(schema_name).iter_errors(document), key=lambda e: e.json_path)
    if not errors:
        return None
    shown = "; ".join(f"{error.json_path}: {error.message}" for error in errors[:5])
    return shown + (f" (+{len(errors) - 5} more)" if len(errors) > 5 else "")


def _check_legacy_shape(manifest: dict[str, Any]) -> None:
    missing = [key for key in LEGACY_KEYS if key not in manifest]
    extra = sorted(set(manifest) - set(LEGACY_KEYS))
    if missing or extra:
        raise InvalidHandoff(f"legacy manifest shape: missing {missing}, unexpected {extra}")
    for key, kind in LEGACY_KEYS.items():
        value = manifest[key]
        if not isinstance(value, kind) or isinstance(value, bool):
            raise InvalidHandoff(f"legacy manifest shape: {key} must be {kind.__name__}")
    if manifest["total_files"] < 0:
        raise InvalidHandoff("legacy manifest shape: total_files must be >= 0")
    for name, count in manifest["class_counts"].items():
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise InvalidHandoff(f"legacy manifest shape: class_counts[{name!r}] must be an integer >= 0")
    if not all(isinstance(path, str) for path in manifest["files"]):
        raise InvalidHandoff("legacy manifest shape: files must be a list of path strings")


def load_manifest(data: bytes) -> tuple[int, dict[str, Any]]:
    """Parse and shape-check manifest bytes; return (contract version, manifest)."""
    try:
        manifest = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidHandoff(f"corrupt {MANIFEST_NAME}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise InvalidHandoff(f"corrupt {MANIFEST_NAME}: the top level is not an object")
    if "contract_version" not in manifest:
        _check_legacy_shape(manifest)
        return 0, manifest
    version = manifest["contract_version"]
    if type(version) is not int or version != 1:
        raise InvalidHandoff(f"unsupported contract_version: {version!r}")
    errors = _schema_errors(MANIFEST_SCHEMA, manifest)
    if errors:
        raise InvalidHandoff(f"{MANIFEST_NAME} fails the v1 schema: {errors}")
    return 1, manifest


def verify_snapshot(snapshot: Path) -> Verified:
    """Verify a snapshot against its own manifest; raise InvalidHandoff or TornHandoff."""
    present = scan_tree(snapshot)
    if MANIFEST_NAME not in present:
        raise TornHandoff(f"{MANIFEST_NAME} vanished during the copy")
    version, manifest = load_manifest((snapshot / MANIFEST_NAME).read_bytes())
    entries = manifest["files"] if version == 1 else [{"path": path} for path in manifest["files"]]
    paths = [entry["path"] for entry in entries]

    duplicates = sorted(path for path, count in Counter(paths).items() if count > 1)
    if duplicates:
        raise InvalidHandoff(f"duplicate paths in {MANIFEST_NAME}: {duplicates[:5]}")
    for path in paths:
        check_confined(path, snapshot)
    if MANIFEST_NAME in paths:
        raise InvalidHandoff(f"{MANIFEST_NAME} lists itself")
    # Channel A carries research text only: Markdown, plus the metadata-only evidence
    # index. A scan or any other binary in the handoff is a contract breach.
    for path in paths:
        if not (path.endswith(".md") or path == EVIDENCE_INDEX_NAME):
            raise InvalidHandoff(f"Channel A carries text only: {path} is not Markdown")
    if manifest["total_files"] != len(paths):
        raise InvalidHandoff(f"total_files is {manifest['total_files']} but {len(paths)} files are listed")
    try:
        _parse_time(manifest["generated_at"])
    except ValueError as exc:
        raise InvalidHandoff(f"generated_at is not an ISO-8601 timestamp: {manifest['generated_at']!r}") from exc
    if version == 1:
        counted = Counter(entry["class"] for entry in entries)
        declared = manifest["class_counts"]
        if any(declared.get(name, 0) != counted.get(name, 0) for name in set(declared) | set(counted)):
            raise InvalidHandoff(f"class_counts {dict(declared)} do not match the listed files {dict(counted)}")
        if content_digest((entry["path"], entry["sha256"]) for entry in entries) != manifest["content_digest"]:
            raise InvalidHandoff("content_digest does not recompute from the listed files")

    listed = set(paths)
    files = present - {MANIFEST_NAME}
    missing, unexpected = sorted(listed - files), sorted(files - listed)
    if missing:
        raise TornHandoff(f"listed file missing from the handoff: {', '.join(missing[:5])}")
    if unexpected:
        raise TornHandoff(f"unexpected file in the handoff: {', '.join(unexpected[:5])}")

    hashes: dict[str, str] = {}
    for entry in entries:
        target = snapshot / entry["path"]
        if version == 1 and target.stat().st_size != entry["size"]:
            raise TornHandoff(
                f"size mismatch for {entry['path']} (manifest {entry['size']}, file {target.stat().st_size})"
            )
        hashes[entry["path"]] = sha256_file(target)
        if entry["path"].endswith(".md"):
            try:
                target.read_bytes().decode("utf-8")
            except UnicodeDecodeError as exc:
                raise InvalidHandoff(f"{entry['path']} is not valid UTF-8") from exc
        if version == 1 and hashes[entry["path"]] != entry["sha256"]:
            raise TornHandoff(f"sha256 mismatch for {entry['path']}")

    indexes = {entry["path"] for entry in entries if entry.get("class") == "evidence_index"}
    indexes |= listed & {EVIDENCE_INDEX_NAME}
    for path in sorted(indexes):
        try:
            index = json.loads((snapshot / path).read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InvalidHandoff(f"corrupt {path}: {exc}") from exc
        errors = _schema_errors(EVIDENCE_INDEX_SCHEMA, index)
        if errors:
            raise InvalidHandoff(f"{path} fails the evidence-index schema: {errors}")

    return Verified(
        contract_version=version,
        digest=manifest["content_digest"] if version == 1 else content_digest(hashes.items()),
        generated_at=manifest["generated_at"],
        source_commit=manifest["source_commit"] if version == 1 else None,
        source_dirty=manifest["source_dirty"] if version == 1 else None,
        total_files=len(paths),
        class_counts=dict(sorted(manifest["class_counts"].items())),
    )


# --- snapshot, pin and prune ---------------------------------------------------


def _copy_drop(drop: Path, target: Path) -> None:
    """Copy the whole drop to `target`, keeping symlinks as links so they are detectable."""
    shutil.copytree(drop, target, symlinks=True)


def _live_state(drop: Path) -> dict[str, tuple[int, int]]:
    """(size, mtime_ns) of every file in the live drop, without following links."""
    state: dict[str, tuple[int, int]] = {}
    for dirpath, _dirnames, filenames in os.walk(drop, followlinks=False):
        for name in filenames:
            if name in IGNORED_NAMES:
                continue
            path = Path(dirpath) / name
            info = path.lstat()
            state[path.relative_to(drop).as_posix()] = (info.st_size, info.st_mtime_ns)
    return state


def _take_snapshot(drop: Path, target: Path) -> None:
    """Copy the drop to `target`; raise TornHandoff if anything in it changed meanwhile.

    Two signals, because the legacy manifest carries no hashes: the manifest's bytes,
    and the size and mtime of every live file before and after the copy. rsync replaces
    each file it updates, so a sync during the copy changes at least one of them.
    """
    _remove(target)
    manifest = drop / MANIFEST_NAME
    try:
        state_before = _live_state(drop)
        before = manifest.read_bytes()
        _copy_drop(drop, target)
        after = manifest.read_bytes()
        state_after = _live_state(drop)
        copied = target / MANIFEST_NAME
        copy_differs = not copied.is_symlink() and copied.read_bytes() != before
    except OSError as exc:  # includes shutil.Error: files vanished or appeared mid-copy
        raise TornHandoff(f"the drop changed while it was copied ({exc})") from exc
    if before != after or copy_differs:
        raise TornHandoff(f"{MANIFEST_NAME} changed during the copy")
    if state_before != state_after:
        changed = sorted(set(state_before) ^ set(state_after) | {k for k in state_before if state_after.get(k) != state_before[k]})
        raise TornHandoff(f"files changed during the copy: {', '.join(changed[:5])}")


def _pinned(snapshots: Path) -> list[Path]:
    if not snapshots.is_dir():
        return []
    return [p for p in snapshots.iterdir() if p.is_dir() and not p.is_symlink() and SHA256_RE.fullmatch(p.name)]


def _pin_snapshot(temporary: Path, final: Path) -> str | None:
    """Move the verified copy to `final` (or discard it if identical); return a warning."""
    warning = None
    if final.exists() or final.is_symlink():
        if final.is_dir() and not final.is_symlink() and _tree_hashes(final) == _tree_hashes(temporary):
            _remove(temporary)
        else:
            warning = f"WARNING: the pinned snapshot {final.name} differed from the verified copy; replaced it"
            _remove(final)
            temporary.rename(final)
    else:
        temporary.rename(final)
    newest = max((p.stat().st_mtime_ns for p in _pinned(final.parent) if p != final), default=0)
    stamp = max(time.time_ns(), newest + 1)
    os.utime(final, ns=(stamp, stamp))  # recency order for pruning
    return warning


def _prune(snapshots: Path, protect: set[str]) -> None:
    """Keep the KEEP_SNAPSHOTS most recent pins plus `protect`; delete the rest."""
    pinned = sorted(_pinned(snapshots), key=lambda p: p.stat().st_mtime_ns, reverse=True)
    keep = {p.name for p in pinned[:KEEP_SNAPSHOTS]} | protect
    for path in pinned:
        if path.name not in keep:
            _remove(path)


# --- intake log and instruction pin ------------------------------------------


def read_log(path: Path) -> tuple[str, dict[str, Any]]:
    """Return (header comment, data) of the intake log; a missing log is empty."""
    if not path.exists():
        return LOG_HEADER, {"generations": []}
    text = path.read_text(encoding="utf-8")
    header = []
    for line in text.splitlines(keepends=True):
        if not (line.startswith("#") or not line.strip()):
            break
        header.append(line)
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise LocalStateError(f"unreadable intake log {path}: {exc}") from exc
    data = {"generations": []} if data is None else data
    if not isinstance(data, dict) or not isinstance(data.get("generations"), list):
        raise LocalStateError(f"malformed intake log {path}: expected a 'generations' list")
    return "".join(header) or LOG_HEADER, data


def write_log(path: Path, header: str, data: dict[str, Any]) -> None:
    """Write the intake log deterministically, keeping its header comment."""
    header = header if header.endswith("\n") else header + "\n"
    _write_atomic(path, header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def read_pin(path: Path) -> dict[str, Any] | None:
    """Return the accepted intake-instruction pin, or None if there is none yet."""
    if not path.exists():
        return None
    try:
        pin = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LocalStateError(f"unreadable intake pin {path}: {exc}") from exc
    if not isinstance(pin, dict) or not SHA256_RE.fullmatch(str(pin.get("sha256", ""))):
        raise LocalStateError(f"malformed intake pin {path}: expected a 64-hex sha256")
    return pin


def _intake_diff(previous: Path, text: str) -> str | None:
    if not previous.is_file():
        return None
    old = previous.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    lines = difflib.unified_diff(
        old,
        text.splitlines(keepends=True),
        fromfile=f"{ACCEPTED_INTAKE_COPY} (last accepted)",
        tofile=f"{INTAKE_TEXT_NAME} (snapshot)",
    )
    return "".join(lines).rstrip("\n") or None


# --- the intake run ----------------------------------------------------------


def _has_handoff(drop: Path) -> bool:
    return drop.is_dir() and any(drop.iterdir()) and os.path.lexists(drop / MANIFEST_NAME)


def run(
    drop: Path,
    state: Path,
    *,
    repo_root: Path,
    strict: bool,
    retries: int = 3,
    wait: float = 5.0,
    accept_intake: bool = False,
    now: datetime | None = None,
    log_path: Path | None = None,
    pin_path: Path | None = None,
) -> IntakeResult:
    """Snapshot, verify, pin and log one handoff generation. Never promotes anything.

    Relative paths resolve against `repo_root`; the log and pin default to
    `research/integration/` under it. `retries` is the number of re-attempts
    after the first torn snapshot.
    """
    repo_root = Path(repo_root)
    drop, state = _under(repo_root, drop), _under(repo_root, state)
    log_path = _under(repo_root, log_path or INTAKE_LOG)
    pin_path = _under(repo_root, pin_path or INTAKE_PIN)
    moment = now or datetime.now(timezone.utc)
    moment = moment.replace(tzinfo=timezone.utc) if moment.tzinfo is None else moment.astimezone(timezone.utc)
    messages: list[str] = []

    if not _has_handoff(drop):
        notice = f"no retrieval handoff at {_show(drop, repo_root)}"
        if strict:
            return IntakeResult(EXIT_BLOCKED, "blocked", [f"BLOCKED: {notice}"])
        return IntakeResult(EXIT_OK, "absent", [f"INFO: {notice}; no intake was performed"])

    try:
        for target in (state, log_path, pin_path):
            if target.resolve().is_relative_to(drop.resolve()):
                raise LocalStateError(f"{_show(target, repo_root)} lies inside the drop; the drop is never written")
        header, log = read_log(log_path)
        pin = read_pin(pin_path)
        generations = log["generations"]
        if not all(isinstance(entry, dict) for entry in generations):
            raise LocalStateError(f"malformed intake log {log_path}: every generation must be a mapping")
        accepted = [entry for entry in generations if entry.get("status") == "accepted"]
        last = accepted[-1] if accepted else None
        last_time = _parse_time(last["generated_at"]) if last else None
    except (LocalStateError, KeyError, ValueError) as exc:
        return IntakeResult(EXIT_INVALID, "invalid", [f"ERROR: local intake state: {exc}"])

    snapshots = state / "snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)
    attempts = max(retries, 0) + 1
    verified: Verified | None = None
    reason = ""
    for attempt in range(1, attempts + 1):
        temporary = snapshots / f".tmp-{os.getpid()}-{attempt}"
        try:
            _take_snapshot(drop, temporary)
            verified = verify_snapshot(temporary)
            break
        except TornHandoff as exc:
            _remove(temporary)
            reason = str(exc)
            messages.append(f"WARNING: attempt {attempt}/{attempts} caught a torn snapshot: {reason}")
            if attempt < attempts:
                time.sleep(wait)
        except InvalidHandoff as exc:
            _remove(temporary)
            messages.append(f"INVALID: {exc}")
            return IntakeResult(EXIT_INVALID, "invalid", messages)
    if verified is None:
        messages.append(f"{TORN_MESSAGE} (last failure: {reason})")
        return IntakeResult(EXIT_INVALID, "torn", messages)

    digest, version = verified.digest, verified.contract_version
    result = IntakeResult(EXIT_OK, "accepted", messages, digest=digest, contract_version=version)

    # O4: the producer's intake instructions against the owner-accepted pin.
    intake_file = temporary / INTAKE_TEXT_NAME
    intake_sha = sha256_file(intake_file) if intake_file.is_file() else None
    intake_bytes = intake_file.read_bytes() if intake_sha else b""
    pinned_sha = pin["sha256"] if pin else None
    review_copy = state / ACCEPTED_INTAKE_COPY
    drift = intake_sha is not None and intake_sha != pinned_sha
    if intake_sha is None:
        messages.append(f"WARNING: the handoff carries no {INTAKE_TEXT_NAME}; the accepted pin is unchanged")
    if drift:
        old = f"{pinned_sha[:12]}…" if pinned_sha else "none"
        messages.append(
            f"DRIFT: the producer's intake instructions changed ({old} → {intake_sha[:12]}…). "
            "Review the change, then re-run with --accept-intake."
        )
        diff = _intake_diff(review_copy, intake_bytes.decode("utf-8", errors="replace"))
        if diff:
            messages.append(diff)
        if not accept_intake:
            if strict:
                _remove(temporary)
                return IntakeResult(EXIT_DRIFT, "drift", messages, digest=digest, contract_version=version)
            messages.append("WARNING: continuing without --strict; the accepted pin is unchanged")

    replay = last is not None and last.get("content_digest") == digest
    stale = not replay and last_time is not None and _parse_time(verified.generated_at) < last_time
    # A repeated non-strict run of the same stale generation is recorded once, not per run.
    recorded_stale = stale and any(
        entry.get("content_digest") == digest and entry.get("status") == "stale" for entry in generations
    )
    if stale and strict:
        _remove(temporary)
        messages.append(STALE_MESSAGE)
        return IntakeResult(EXIT_STALE, "stale", messages, digest=digest, contract_version=version)

    if drift and accept_intake:
        new_pin = {
            "path": INTAKE_TEXT_NAME,
            "sha256": intake_sha,
            "accepted_at": moment.date().isoformat(),
            "accepted_from_digest": digest,
        }
        _write_atomic(pin_path, json.dumps(new_pin, indent=2, ensure_ascii=False) + "\n")
        _write_atomic(review_copy, intake_bytes)
        messages.append(f"INFO: accepted the new intake instructions ({intake_sha[:12]}…) and updated the pin")
    elif intake_sha is not None and not drift:
        if not review_copy.is_file() or sha256_file(review_copy) != intake_sha:
            _write_atomic(review_copy, intake_bytes)  # the accepted text, kept for future drift diffs

    final = snapshots / digest
    warning = _pin_snapshot(temporary, final)
    if warning:
        messages.append(warning)
    result.snapshot = final
    shown = _show(final, repo_root)
    ok_line = f"OK: pinned {digest} (contract v{version}, {verified.total_files} files) — read the handoff from {shown}"

    if replay:
        result.status = "replay"
        messages.append(f"ALREADY INGESTED: {digest}; no-op — read the handoff from {shown}")
    elif recorded_stale:
        result.status = "stale"
        messages += [f"WARNING: {STALE_MESSAGE}; already recorded as stale, no new entry", ok_line]
    else:
        generations.append(
            {
                "content_digest": digest,
                "contract_version": version,
                "source_commit": verified.source_commit,
                "source_dirty": verified.source_dirty,
                "generated_at": verified.generated_at,
                "accepted_at": moment.replace(microsecond=0).isoformat(),
                "total_files": verified.total_files,
                "class_counts": verified.class_counts,
                "intake_text_sha256": intake_sha,
                "status": "stale" if stale else "accepted",
            }
        )
        write_log(log_path, header, log)
        if stale:
            result.status = "stale"
            messages.append(f"WARNING: {STALE_MESSAGE}; recorded with status stale")
        messages.append(ok_line)

    latest_accepted = digest if result.status == "accepted" else (last or {}).get("content_digest")
    _prune(snapshots, {digest} | ({str(latest_accepted)} if latest_accepted else set()))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Snapshot, verify and pin the retrieval handoff. Sync is not promotion.",
        epilog="Exit codes: 0 ok, 2 blocked (no handoff, --strict), 3 invalid or torn, "
        "4 stale (--strict), 5 intake-text drift (--strict). Relative paths resolve "
        "against the repository root.",
    )
    parser.add_argument("--drop", type=Path, default=DEFAULT_DROP, help="the retrieval drop (read-only)")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE, help="local intake state (snapshots)")
    parser.add_argument("--strict", action="store_true", help="fail on a missing handoff, staleness or drift")
    parser.add_argument("--retries", type=int, default=3, help="re-attempts after a torn snapshot")
    parser.add_argument("--wait", type=float, default=5.0, help="seconds between attempts")
    parser.add_argument(
        "--accept-intake", action="store_true", help="accept the producer's changed intake instructions"
    )
    args = parser.parse_args(argv)
    if args.retries < 0 or args.wait < 0:
        parser.error("--retries and --wait must be non-negative")

    result = run(
        args.drop,
        args.state,
        repo_root=ROOT,
        strict=args.strict,
        retries=args.retries,
        wait=args.wait,
        accept_intake=args.accept_intake,
    )
    for line in result.messages:
        print(line, file=sys.stderr if line.startswith(STDERR_PREFIXES) else sys.stdout)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
