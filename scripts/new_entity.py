#!/usr/bin/env python3
"""Reserve stable entity IDs, create non-live YAML drafts and apply validated
change sets (draft promotions, live-file replacements and owner-authorised
evidence transfers) as one recoverable transaction."""

from __future__ import annotations

import argparse
import copy
import hashlib
import os
import re
import shutil
import stat
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import yaml

if __package__:
    from .validate_data import REPOSITORY_ROOT, validate_repository
    from .validation.identifiers import (
        ENTITY_CONFIGS,
        KINDS_BY_SINGULAR,
        SOURCE_KINDS,
        EntityConfig,
        format_identifier,
        parse_identifier,
    )
    from .validation.model import ValidationResult, load_yaml, sha256_file
else:
    from validate_data import REPOSITORY_ROOT, validate_repository
    from validation.identifiers import (
        ENTITY_CONFIGS,
        KINDS_BY_SINGULAR,
        SOURCE_KINDS,
        EntityConfig,
        format_identifier,
        parse_identifier,
    )
    from validation.model import ValidationResult, load_yaml, sha256_file


TRANSACTION_DIRECTORY = ".entity-promotion-transaction"
LOCK_FILENAME = ".entity-transaction.lock"
SHA256_PATTERN = re.compile(r"[a-f0-9]{64}")
CHANGE_SET_KEYS = {"id", "promote", "replace", "evidence"}
REPLACE_KEYS = {"path", "base_sha256", "content_from"}
EVIDENCE_KEYS = {"from", "sha256", "to", "authorisation"}
LEDGER_RELATIVE_PATH = "data/id-ledger.yaml"


class AllocationError(RuntimeError):
    """Raised when an entity reservation cannot be completed safely."""


@dataclass(frozen=True)
class ReservationResult:
    identifier: str
    draft_path: Path
    dry_run: bool
    recovered: bool = False


@dataclass(frozen=True)
class PromotionResult:
    identifiers: tuple[str, ...]
    dry_run: bool
    warnings: tuple[str, ...] = ()
    label: str | None = None
    replaced: tuple[str, ...] = ()
    transferred: tuple[str, ...] = ()
    already_applied: bool = False


@dataclass(frozen=True)
class RecoveryResult:
    identifiers: tuple[str, ...]
    committed: bool
    label: str | None = None
    stale_lock_pid: int | None = None
    left_in_place: tuple[str, ...] = ()


@dataclass(frozen=True)
class Replacement:
    path: str
    base_sha256: str
    content: bytes


@dataclass(frozen=True)
class EvidenceTransfer:
    source: Path
    sha256: str
    destination: str
    authorisation: str


@dataclass(frozen=True)
class ChangeSet:
    label: str | None
    promote: tuple[str, ...]
    replace: tuple[Replacement, ...] = ()
    evidence: tuple[EvidenceTransfer, ...] = ()


@dataclass(frozen=True)
class _ResolvedPlan:
    batch: list[tuple[str, str, EntityConfig, Path, Path]]
    draft_hashes: dict[Path, str]
    updated_ledger: dict[str, Any]
    replacements: tuple[tuple[Replacement, Path], ...]
    evidence: tuple[tuple[EvidenceTransfer, Path], ...]


@dataclass(frozen=True)
class _Step:
    action: str
    target: Path
    source: Path | None = None
    content: bytes | None = None
    sha256: str | None = None


def _stage_error(stage: str, problems: list[str]) -> AllocationError:
    if len(problems) == 1:
        return AllocationError(f"{stage}: {problems[0]}")
    details = "\n".join(f"  - {problem}" for problem in problems)
    return AllocationError(f"{stage}: {len(problems)} problems:\n{details}")


def _pid_is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _read_lock_pid(lock_path: Path) -> int | None:
    document = yaml.safe_load(lock_path.read_text(encoding="utf-8"))
    pid = document.get("pid") if isinstance(document, dict) else None
    if isinstance(pid, int) and not isinstance(pid, bool) and pid > 0:
        return pid
    return None


@contextmanager
def _transaction_lock(
    root: Path, *, allow_stale: bool = False
) -> Iterator[int | None]:
    """Hold the exclusive repository lock; yield a dead holder's pid if allowed.

    Only ``recover`` passes ``allow_stale``: it may run under a lock left by a dead
    process, but it never removes or overwrites that lock (no automatic stealing).
    """
    lock_path = root / LOCK_FILENAME
    content = yaml.safe_dump(
        {
            "pid": os.getpid(),
            "acquired_at": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
            "token": uuid.uuid4().hex,
        },
        sort_keys=False,
    )
    acquired = False
    stale_pid: int | None = None
    for _ in range(3):
        try:
            _link_new_file(lock_path, content.encode("utf-8"))
            acquired = True
            break
        except FileExistsError:
            pass
        try:
            pid = _read_lock_pid(lock_path)
        except FileNotFoundError:
            continue
        except (OSError, yaml.YAMLError):
            pid = None
        if pid is None:
            raise AllocationError(
                f"lock: {lock_path} exists but names no readable pid; if no "
                "entity transaction is running, run the recover command and "
                "then remove the lock by hand"
            )
        if _pid_is_running(pid):
            raise AllocationError(
                f"lock: another entity transaction is running (pid {pid})"
            )
        try:
            if _read_lock_pid(lock_path) != pid:
                continue
        except (OSError, yaml.YAMLError):
            # Released (or replaced) between the read and the liveness check.
            continue
        if not allow_stale:
            raise AllocationError(
                f"lock: {lock_path} is held by pid {pid}, which is no longer "
                "running; run the recover command, then remove the lock by hand"
            )
        stale_pid = pid
        break
    if not acquired and stale_pid is None:
        raise AllocationError(f"lock: cannot acquire {lock_path}")
    try:
        yield stale_pid
    finally:
        if acquired:
            try:
                if lock_path.read_text(encoding="utf-8") == content:
                    lock_path.unlink()
            except FileNotFoundError:
                pass


def _transaction_guard(root: Path) -> None:
    if (root / TRANSACTION_DIRECTORY).exists():
        raise AllocationError(
            "lock: an unfinished promotion transaction exists; run the recover "
            "command"
        )


def _live_precheck(
    root: Path, schema_dir: Path | None, consequence: str
) -> tuple[dict[str, Any], frozenset[str]]:
    result = validate_repository(root, schema_dir=schema_dir)
    if result.errors:
        details = "\n".join(issue.render() for issue in result.errors[:10])
        raise AllocationError(
            f"live pre-check: repository validation failed; {consequence}"
            + (f":\n{details}" if details else "")
        )
    ledger_path = root / "data" / "id-ledger.yaml"
    ledger = load_yaml(ledger_path)
    if not isinstance(ledger, dict) or ledger.get("version") != 2:
        raise AllocationError("live pre-check: ID ledger version 2 is required")
    return ledger, frozenset(issue.render() for issue in result.warnings)


def _validated_ledger(
    root: Path, schema_dir: Path | None
) -> dict[str, Any]:
    ledger, _ = _live_precheck(root, schema_dir, "no allocation was attempted")
    return ledger


def _config_for_identifier(identifier: str) -> tuple[str, EntityConfig] | None:
    for kind, config in ENTITY_CONFIGS.items():
        if parse_identifier(identifier, config) is not None:
            return kind, config
    return None


def _render_draft(
    root: Path,
    config: EntityConfig,
    identifier: str,
    template_dir: Path | None,
) -> str:
    directory = template_dir or root / "templates" / "entities"
    template_path = directory / f"{config.singular}.yaml"
    try:
        document = load_yaml(template_path)
    except (OSError, yaml.YAMLError) as exc:
        raise AllocationError(f"cannot load template {template_path}: {exc}") from exc
    if not isinstance(document, dict):
        raise AllocationError(f"template {template_path} must be a YAML mapping")
    expected_placeholder = f"{config.prefix}-NNNN"
    if document.get("id") != expected_placeholder:
        raise AllocationError(
            f"template {template_path} must use ID placeholder "
            f"{expected_placeholder}"
        )
    document["id"] = identifier
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True)


def _as_bytes(content: str | bytes) -> bytes:
    return content.encode("utf-8") if isinstance(content, str) else content


def _atomic_replace(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(_as_bytes(content))
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            os.chmod(temporary_path, path.stat().st_mode & 0o777)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _link_new_file(path: Path, content: bytes) -> None:
    """Create ``path`` with ``content`` atomically; FileExistsError if present."""
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _atomic_create(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        _link_new_file(path, _as_bytes(content))
    except FileExistsError as exc:
        raise AllocationError(f"refusing to overwrite {path}") from exc


def _allocated_numbers(
    root: Path,
    kind: str,
    config: EntityConfig,
    ledger: dict[str, Any],
) -> set[int]:
    numbers: set[int] = set()
    entity_dir = root / "data" / config.directory
    if entity_dir.is_dir():
        for path in entity_dir.glob("*.yaml"):
            number = parse_identifier(path.stem, config)
            if number is not None:
                numbers.add(number)
    for section_name in ("reserved_ids", "retired_ids"):
        section = ledger.get(section_name, {})
        for identifier in section.get(kind, []):
            if isinstance(identifier, str):
                number = parse_identifier(identifier, config)
                if number is not None:
                    numbers.add(number)
    return numbers


def reserve_entity(
    root: Path,
    singular_kind: str,
    *,
    dry_run: bool = False,
    schema_dir: Path | None = None,
    template_dir: Path | None = None,
) -> ReservationResult:
    root = root.resolve()
    kind = KINDS_BY_SINGULAR.get(singular_kind)
    if kind is None:
        raise AllocationError(f"unknown entity kind {singular_kind!r}")
    config = ENTITY_CONFIGS[kind]
    with _transaction_lock(root):
        _transaction_guard(root)
        ledger = _validated_ledger(root, schema_dir)
        allocated = _allocated_numbers(root, kind, config, ledger)
        next_number = max(allocated, default=0) + 1
        if next_number > 9999:
            raise AllocationError(
                f"{config.prefix} identifier space is exhausted at four digits"
            )
        identifier = format_identifier(next_number, config.prefix)
        draft_path = root / "research" / "entity-drafts" / f"{identifier}.yaml"
        if draft_path.exists():
            raise AllocationError(f"refusing to overwrite {draft_path}")
        content = _render_draft(root, config, identifier, template_dir)

        if dry_run:
            return ReservationResult(identifier, draft_path, True)

        updated_ledger = copy.deepcopy(ledger)
        reservations = updated_ledger["reserved_ids"][kind]
        reservations.append(identifier)
        ledger_content = yaml.safe_dump(
            updated_ledger, sort_keys=False, allow_unicode=True
        )
        _atomic_replace(root / "data" / "id-ledger.yaml", ledger_content)
        try:
            _atomic_create(draft_path, content)
        except Exception as exc:
            raise AllocationError(
                f"{identifier} remains safely reserved, but its draft could not "
                "be created; rerun with the materialize command"
            ) from exc
        return ReservationResult(identifier, draft_path, False)


def materialize_reserved_entity(
    root: Path,
    identifier: str,
    *,
    dry_run: bool = False,
    schema_dir: Path | None = None,
    template_dir: Path | None = None,
) -> ReservationResult:
    root = root.resolve()
    resolved = _config_for_identifier(identifier)
    if resolved is None:
        raise AllocationError(f"invalid entity identifier {identifier!r}")
    kind, config = resolved
    with _transaction_lock(root):
        _transaction_guard(root)
        ledger = _validated_ledger(root, schema_dir)
        if identifier not in ledger["reserved_ids"][kind]:
            raise AllocationError(f"{identifier} is not reserved")
        draft_path = root / "research" / "entity-drafts" / f"{identifier}.yaml"
        if draft_path.exists():
            raise AllocationError(f"refusing to overwrite {draft_path}")
        content = _render_draft(root, config, identifier, template_dir)
        if not dry_run:
            _atomic_create(draft_path, content)
        return ReservationResult(identifier, draft_path, dry_run, recovered=True)


def _confined_relative_path(value: Any, prefix: str) -> tuple[str | None, str]:
    """Return a normalised repository-relative path under ``prefix``, or a problem."""
    if not isinstance(value, str) or not value:
        return None, "must be a non-empty repository-relative path"
    segments = value.split("/")
    if value.startswith("/") or "\\" in value:
        return None, "must be a repository-relative POSIX path"
    if any(segment in {"", ".", ".."} for segment in segments):
        return None, "must not contain empty, '.' or '..' segments"
    if segments[0] != prefix or len(segments) < 2:
        return None, f"must be under {prefix}/"
    return value, ""


def load_change_set(path: Path) -> ChangeSet:
    """Read and shape-check a change set; every problem is reported together."""
    try:
        document = load_yaml(path)
    except FileNotFoundError:
        raise AllocationError(f"change set: {path} does not exist") from None
    except (OSError, yaml.YAMLError) as exc:
        raise AllocationError(f"change set: cannot read {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise AllocationError(f"change set: {path} must be a YAML mapping")

    problems: list[str] = []
    unknown = sorted(str(key) for key in set(document) - CHANGE_SET_KEYS)
    if unknown:
        problems.append(f"$: unknown keys: {', '.join(unknown)}")
    label = document.get("id")
    if not isinstance(label, str) or not label.strip():
        problems.append("$.id: a non-empty free-text label is required")
        label = None

    def entries(key: str) -> list[Any]:
        value = document.get(key, [])
        if value is None:
            return []
        if not isinstance(value, list):
            problems.append(f"$.{key}: must be a list")
            return []
        return value

    def check_keys(
        item: Any, location: str, allowed: set[str], required: set[str]
    ) -> bool:
        if not isinstance(item, dict):
            problems.append(f"{location}: must be a mapping")
            return False
        missing = sorted(required - set(item))
        extra = sorted(str(key) for key in set(item) - allowed)
        if missing:
            problems.append(f"{location}: missing keys: {', '.join(missing)}")
        if extra:
            problems.append(f"{location}: unknown keys: {', '.join(extra)}")
        return True

    def check_sha256(value: Any, location: str) -> str | None:
        if isinstance(value, str) and SHA256_PATTERN.fullmatch(value):
            return value
        problems.append(f"{location}: must be a 64-character lowercase hex sha256")
        return None

    promote: list[str] = []
    for index, identifier in enumerate(entries("promote")):
        if isinstance(identifier, str) and identifier:
            promote.append(identifier)
        else:
            problems.append(f"$.promote[{index}]: must be an entity identifier")

    replacements: list[Replacement] = []
    for index, item in enumerate(entries("replace")):
        location = f"$.replace[{index}]"
        if not check_keys(item, location, REPLACE_KEYS, REPLACE_KEYS):
            continue
        relative, problem = _confined_relative_path(item.get("path"), "data")
        if relative is None:
            problems.append(f"{location}.path: {problem}")
        elif relative == LEDGER_RELATIVE_PATH:
            problems.append(
                f"{location}.path: {LEDGER_RELATIVE_PATH} is maintained by this "
                "tool and cannot be replaced"
            )
            relative = None
        base_sha256 = check_sha256(item.get("base_sha256"), f"{location}.base_sha256")
        content: bytes | None = None
        content_from = item.get("content_from")
        if not isinstance(content_from, str) or not content_from:
            problems.append(f"{location}.content_from: must be a file path")
        else:
            content_path = Path(content_from)
            if not content_path.is_absolute():
                content_path = path.parent / content_path
            try:
                content = content_path.read_bytes()
            except OSError as exc:
                problems.append(f"{location}.content_from: cannot be read: {exc}")
        if relative and base_sha256 and content is not None:
            replacements.append(Replacement(relative, base_sha256, content))

    transfers: list[EvidenceTransfer] = []
    for index, item in enumerate(entries("evidence")):
        location = f"$.evidence[{index}]"
        # A missing authorisation is reported with its own message below.
        if not check_keys(
            item, location, EVIDENCE_KEYS, EVIDENCE_KEYS - {"authorisation"}
        ):
            continue
        source = item.get("from")
        if not isinstance(source, str) or not Path(source).is_absolute():
            problems.append(f"{location}.from: must be an absolute file path")
            source = None
        expected = check_sha256(item.get("sha256"), f"{location}.sha256")
        destination, problem = _confined_relative_path(item.get("to"), "evidence")
        if destination is None:
            problems.append(f"{location}.to: {problem}")
        authorisation = item.get("authorisation")
        if not isinstance(authorisation, str) or not authorisation.strip():
            problems.append(
                f"{location}.authorisation: evidence transfer requires an owner "
                "authorisation reference"
            )
            authorisation = None
        if source and expected and destination and authorisation:
            transfers.append(
                EvidenceTransfer(
                    Path(source), expected, destination, authorisation.strip()
                )
            )

    if not (document.get("promote") or document.get("replace") or document.get("evidence")):
        problems.append("$: the change set has no promote, replace or evidence entries")
    if problems:
        details = "\n".join(f"  - {problem}" for problem in problems)
        raise AllocationError(f"change set: {path} is invalid:\n{details}")
    return ChangeSet(label, tuple(promote), tuple(replacements), tuple(transfers))


def _resolve_promotion_batch(
    root: Path,
    identifiers: list[str],
    ledger: dict[str, Any],
) -> list[tuple[str, str, EntityConfig, Path, Path]]:
    if not identifiers:
        raise AllocationError("at least one draft identifier is required")
    if len(identifiers) != len(set(identifiers)):
        raise AllocationError("promotion identifiers must be distinct")
    resolved_batch: list[tuple[str, str, EntityConfig, Path, Path]] = []
    for identifier in identifiers:
        resolved = _config_for_identifier(identifier)
        if resolved is None:
            raise AllocationError(f"invalid entity identifier {identifier!r}")
        kind, config = resolved
        if identifier not in ledger["reserved_ids"][kind]:
            raise AllocationError(f"{identifier} is not reserved")
        draft_path = root / "research" / "entity-drafts" / f"{identifier}.yaml"
        if not draft_path.is_file():
            raise AllocationError(f"reserved draft is missing: {draft_path}")
        target_path = root / "data" / config.directory / f"{identifier}.yaml"
        if target_path.exists():
            raise AllocationError(f"refusing to overwrite {target_path}")
        resolved_batch.append(
            (identifier, kind, config, draft_path, target_path)
        )
    return resolved_batch


def _ledger_without_reservations(
    ledger: dict[str, Any],
    batch: list[tuple[str, str, EntityConfig, Path, Path]],
) -> dict[str, Any]:
    updated = copy.deepcopy(ledger)
    for identifier, kind, _, _, _ in batch:
        updated["reserved_ids"][kind].remove(identifier)
    return updated


def _held_evidence_hashes(root: Path) -> dict[str, str]:
    """Map every evidence sha256 already held to the record that holds it."""
    held: dict[str, str] = {}
    inventory = load_yaml(root / "data" / "document-inventory.yaml")
    documents = inventory.get("documents") if isinstance(inventory, dict) else None
    for document in documents if isinstance(documents, list) else []:
        if not isinstance(document, dict):
            continue
        for file_record in document.get("files") or []:
            if isinstance(file_record, dict) and isinstance(
                file_record.get("sha256"), str
            ):
                held.setdefault(
                    file_record["sha256"],
                    f"{document.get('inventory_id')} in data/document-inventory.yaml",
                )
    for kind in (*SOURCE_KINDS, "fan"):
        directory = root / "data" / ENTITY_CONFIGS[kind].directory
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.yaml")):
            entity = load_yaml(path)
            if not isinstance(entity, dict):
                continue
            digital_file = entity.get("digital_file")
            files = [digital_file] if isinstance(digital_file, dict) else []
            pages = entity.get("additional_pages")
            files += [page for page in pages if isinstance(page, dict)] if isinstance(
                pages, list
            ) else []
            for file_record in files:
                if isinstance(file_record.get("sha256"), str):
                    held.setdefault(
                        file_record["sha256"], f"{entity.get('id')} ({path.name})"
                    )
    return held


def _resolve_change_set(
    root: Path, change_set: ChangeSet, ledger: dict[str, Any]
) -> _ResolvedPlan:
    problems: list[str] = []
    batch: list[tuple[str, str, EntityConfig, Path, Path]] = []
    if change_set.promote:
        try:
            batch = _resolve_promotion_batch(root, list(change_set.promote), ledger)
        except AllocationError as exc:
            problems.append(str(exc))
    draft_hashes = {draft_path: sha256_file(draft_path) for *_, draft_path, _ in batch}

    data_root = (root / "data").resolve()
    replacements: list[tuple[Replacement, Path]] = []
    seen_paths: set[str] = set()
    for replacement in change_set.replace:
        if replacement.path in seen_paths:
            problems.append(f"replacement path appears twice: {replacement.path}")
            continue
        seen_paths.add(replacement.path)
        live_path = root / replacement.path
        try:
            live_path.resolve().relative_to(data_root)
        except ValueError:
            problems.append(f"replacement path escapes data/: {replacement.path}")
            continue
        if live_path.is_symlink() or not live_path.is_file():
            problems.append(
                f"replacement target is not an existing regular file: "
                f"{replacement.path}; create new entities through promote"
            )
            continue
        if sha256_file(live_path) != replacement.base_sha256:
            problems.append(
                f"stale replacement: {replacement.path} changed since the patch "
                "was written"
            )
            continue
        replacements.append((replacement, live_path))

    evidence_root = (root / "evidence").resolve()
    held = _held_evidence_hashes(root)
    transfers: list[tuple[EvidenceTransfer, Path]] = []
    seen_hashes: set[str] = set()
    for transfer in change_set.evidence:
        destination = root / transfer.destination
        if not transfer.authorisation.strip():
            problems.append(
                f"{transfer.destination}: evidence transfer requires an owner "
                "authorisation reference"
            )
            continue
        try:
            destination.resolve().relative_to(evidence_root)
        except ValueError:
            problems.append(
                f"evidence destination escapes evidence/: {transfer.destination}"
            )
            continue
        if transfer.destination in seen_paths or os.path.lexists(destination):
            problems.append(
                f"evidence destination already exists: {transfer.destination}"
            )
            continue
        seen_paths.add(transfer.destination)
        if not transfer.source.is_file():
            problems.append(f"evidence source does not exist: {transfer.source}")
            continue
        actual = sha256_file(transfer.source)
        if actual != transfer.sha256:
            problems.append(
                f"evidence sha256 mismatch: {transfer.source} is {actual}, "
                f"expected {transfer.sha256}"
            )
            continue
        if transfer.sha256 in held:
            problems.append(
                f"duplicate evidence: {transfer.sha256} is already held by "
                f"{held[transfer.sha256]}"
            )
            continue
        if transfer.sha256 in seen_hashes:
            problems.append(
                f"duplicate evidence: {transfer.sha256} appears twice in the "
                "change set"
            )
            continue
        seen_hashes.add(transfer.sha256)
        transfers.append((transfer, destination))

    if problems:
        raise _stage_error("resolve", problems)
    return _ResolvedPlan(
        batch,
        draft_hashes,
        _ledger_without_reservations(ledger, batch),
        tuple(replacements),
        tuple(transfers),
    )


def _copy_tree(source: Path, destination: Path, *, hardlink: bool = False) -> None:
    if not source.is_dir():
        return
    copy_function = os.link if hardlink else shutil.copy2
    shutil.copytree(source, destination, copy_function=copy_function)


def _copy_new_file(source: Path, destination: Path) -> None:
    """Copy into a path that must not exist ('x' never writes through a link)."""
    with source.open("rb") as reader, destination.open("xb") as writer:
        shutil.copyfileobj(reader, writer, 1024 * 1024)
        writer.flush()
        os.fsync(writer.fileno())


def _new_warnings(
    validation: ValidationResult, live_warnings: frozenset[str]
) -> list[str]:
    return [
        issue.render()
        for issue in validation.warnings
        if issue.render() not in live_warnings
    ]


def _validate_prospective_promotion(
    root: Path,
    schema_dir: Path | None,
    batch: list[tuple[str, str, EntityConfig, Path, Path]],
    updated_ledger: dict[str, Any],
    replacements: tuple[tuple[Replacement, Path], ...] = (),
    evidence: tuple[tuple[EvidenceTransfer, Path], ...] = (),
    live_warnings: frozenset[str] = frozenset(),
) -> tuple[str, ...]:
    resolved_schema_dir = schema_dir or root / "schemas"
    with tempfile.TemporaryDirectory(
        dir=root, prefix=".promotion-preview-"
    ) as temporary_name:
        staging_root = Path(temporary_name)
        try:
            _copy_tree(root / "data", staging_root / "data")
            _copy_tree(root / "research", staging_root / "research")
            _copy_tree(root / "evidence", staging_root / "evidence", hardlink=True)
            for identifier, _, config, _, _ in batch:
                staging_draft = (
                    staging_root
                    / "research"
                    / "entity-drafts"
                    / f"{identifier}.yaml"
                )
                staging_target = (
                    staging_root
                    / "data"
                    / config.directory
                    / f"{identifier}.yaml"
                )
                staging_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(staging_draft, staging_target)
                staging_draft.unlink()
            for replacement, _ in replacements:
                # data/ is a full copy, never hard links, so this cannot reach live.
                (staging_root / replacement.path).write_bytes(replacement.content)
            for transfer, _ in evidence:
                staging_destination = staging_root / transfer.destination
                staging_destination.parent.mkdir(parents=True, exist_ok=True)
                _copy_new_file(transfer.source, staging_destination)
                if sha256_file(staging_destination) != transfer.sha256:
                    raise AllocationError(
                        f"stage: evidence source {transfer.source} changed since "
                        "it was resolved"
                    )
            (staging_root / "data" / "id-ledger.yaml").write_text(
                yaml.safe_dump(updated_ledger, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
        except OSError as exc:
            raise AllocationError(
                f"stage: cannot build the staging copy: {exc}"
            ) from exc
        validation = validate_repository(
            staging_root, schema_dir=resolved_schema_dir
        )
        if validation.errors:
            details = "\n".join(issue.render() for issue in validation.errors[:20])
            raise AllocationError(
                "validate staged: prospective promotion is invalid; live data was "
                "not changed"
                + (f":\n{details}" if details else "")
            )
        introduced = _new_warnings(validation, live_warnings)
        if introduced:
            raise AllocationError(
                "validate staged: "
                + "; ".join(f"new warning introduced: {issue}" for issue in introduced)
                + "; live data was not changed"
            )
        return tuple(issue.render() for issue in validation.warnings)


def _write_durable(path: Path, content: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def _prepare_transaction(
    root: Path,
    identifiers: list[str],
    ledger_content: str | bytes,
    *,
    label: str | None = None,
    replaced: tuple[tuple[Path, str], ...] = (),
    removed: tuple[tuple[Path, str], ...] = (),
    planned_creates: tuple[Path, ...] = (),
) -> Path:
    """Journal the original bytes of every replaced or removed file.

    ``replaced`` and ``removed`` pair each live path with the sha256 it must still
    have; a mismatch means the file changed after it was validated.
    """
    transaction_path = root / TRANSACTION_DIRECTORY
    if transaction_path.exists():
        raise AllocationError(
            "journal: an unfinished promotion transaction exists; run the recover "
            "command"
        )
    preparing_path = Path(
        tempfile.mkdtemp(dir=root, prefix=".promotion-prepare-")
    )
    try:
        (preparing_path / "originals").mkdir()
        entries: dict[str, list[dict[str, Any]]] = {"replaced": [], "removed": []}
        number = 0
        for section, files in (("replaced", replaced), ("removed", removed)):
            for path, expected in files:
                number += 1
                original = f"originals/{number:04d}"
                content = path.read_bytes()
                relative = path.relative_to(root).as_posix()
                if hashlib.sha256(content).hexdigest() != expected:
                    subject = (
                        "stale replacement: " if section == "replaced" else "draft "
                    )
                    raise AllocationError(
                        f"journal: {subject}{relative} changed since it was "
                        "validated"
                    )
                _write_durable(preparing_path / original, content)
                entries[section].append(
                    {
                        "path": relative,
                        "original": original,
                        "sha256": expected,
                        "mode": stat.S_IMODE(path.stat().st_mode),
                    }
                )
        _write_durable(
            preparing_path / "manifest.yaml",
            yaml.safe_dump(
                {
                    "version": 2,
                    "label": label,
                    "identifiers": identifiers,
                    "replaced": entries["replaced"],
                    "removed": entries["removed"],
                    "planned_creates": [
                        path.relative_to(root).as_posix() for path in planned_creates
                    ],
                },
                sort_keys=False,
                allow_unicode=True,
            ).encode("utf-8"),
        )
        _write_durable(preparing_path / "id-ledger.yaml", _as_bytes(ledger_content))
        _write_durable(preparing_path / "created", b"")
        os.replace(preparing_path, transaction_path)
    finally:
        if preparing_path.exists():
            shutil.rmtree(preparing_path)
    return transaction_path


def _record_created(root: Path, transaction_path: Path, path: Path) -> None:
    """Append one created path to the journal, durably, as soon as it exists."""
    line = f"{path.relative_to(root).as_posix()}\n".encode("utf-8")
    descriptor = os.open(transaction_path / "created", os.O_WRONLY | os.O_APPEND)
    try:
        os.write(descriptor, line)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _make_parents(root: Path, transaction_path: Path, directory: Path) -> None:
    missing: list[Path] = []
    current = directory
    while not current.exists():
        missing.append(current)
        current = current.parent
    for path in reversed(missing):
        try:
            path.mkdir()
        except FileExistsError:
            continue
        _record_created(root, transaction_path, path)


def _apply_step(root: Path, transaction_path: Path, step: _Step) -> None:
    """Perform one live write. Every apply-stage write goes through here."""
    target = step.target
    if step.action == "replace":
        _atomic_replace(target, step.content or b"")
        return
    if step.action == "remove":
        target.unlink()
        return
    _make_parents(root, transaction_path, target.parent)
    if step.action == "link-draft":
        try:
            os.link(step.source, target)
        except FileExistsError as exc:
            raise AllocationError(f"apply: refusing to overwrite {target}") from exc
        _record_created(root, transaction_path, target)
        return
    if step.action != "copy-evidence":
        raise AllocationError(f"apply: unknown step {step.action!r}")
    descriptor, temporary_name = tempfile.mkstemp(
        dir=target.parent, prefix=f".{target.name}.", suffix=".tmp"
    )
    temporary_path = Path(temporary_name)
    try:
        with step.source.open("rb") as reader, os.fdopen(descriptor, "wb") as writer:
            shutil.copyfileobj(reader, writer, 1024 * 1024)
            writer.flush()
            os.fsync(writer.fileno())
        if sha256_file(temporary_path) != step.sha256:
            raise AllocationError(
                f"apply: copied evidence from {step.source} does not match "
                f"sha256 {step.sha256}"
            )
        try:
            # A hard link is a rename that never replaces an existing path.
            os.link(temporary_path, target)
        except FileExistsError as exc:
            raise AllocationError(f"apply: refusing to overwrite {target}") from exc
        _record_created(root, transaction_path, target)
    finally:
        temporary_path.unlink(missing_ok=True)
    if sha256_file(target) != step.sha256:
        raise AllocationError(f"apply: {target} does not match sha256 {step.sha256}")


def _remove_promoted_drafts(
    root: Path,
    transaction_path: Path,
    batch: list[tuple[str, str, EntityConfig, Path, Path]],
) -> None:
    for _, _, _, draft_path, _ in batch:
        _apply_step(root, transaction_path, _Step("remove", draft_path))


def _read_manifest(transaction_path: Path) -> dict[str, Any]:
    try:
        manifest = load_yaml(transaction_path / "manifest.yaml")
    except (OSError, yaml.YAMLError) as exc:
        raise AllocationError(
            f"recover: cannot read promotion recovery state: {exc}"
        ) from exc
    identifiers = manifest.get("identifiers") if isinstance(manifest, dict) else None
    if not isinstance(identifiers, list) or not all(
        isinstance(identifier, str) for identifier in identifiers
    ):
        raise AllocationError("recover: promotion recovery manifest is invalid")
    return manifest


def _restore_file(root: Path, transaction_path: Path, entry: dict[str, Any]) -> None:
    path = root / entry["path"]
    original = (transaction_path / entry["original"]).read_bytes()
    if path.is_file() and not path.is_symlink() and path.read_bytes() == original:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path) and not path.is_file():
        raise AllocationError(f"recover: cannot restore {entry['path']}: not a file")
    _atomic_replace(path, original)
    os.chmod(path, int(entry.get("mode", 0o644)))


def _rollback_legacy(
    root: Path, transaction_path: Path, identifiers: list[str]
) -> tuple[str, ...]:
    """Roll back a version-1 journal, deleting only targets proven to be ours."""
    for identifier in identifiers:
        resolved = _config_for_identifier(identifier)
        if resolved is None:
            raise AllocationError(
                f"recover: promotion recovery contains invalid identifier "
                f"{identifier!r}"
            )
        _, config = resolved
        draft_path = root / "research" / "entity-drafts" / f"{identifier}.yaml"
        target_path = root / "data" / config.directory / f"{identifier}.yaml"
        if not draft_path.exists() and not target_path.exists():
            raise AllocationError(
                f"recover: cannot recover {identifier}: both draft and live target "
                "are missing"
            )
        if not draft_path.exists():
            draft_path.parent.mkdir(parents=True, exist_ok=True)
            os.link(target_path, draft_path)
        if target_path.exists() and os.path.samefile(draft_path, target_path):
            target_path.unlink()
    return tuple(identifiers)


def _rollback(
    root: Path, transaction_path: Path
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    manifest = _read_manifest(transaction_path)
    identifiers = list(manifest["identifiers"])
    try:
        ledger_content = (transaction_path / "id-ledger.yaml").read_bytes()
        created_log = (
            b""
            if manifest.get("version") == 1
            else (transaction_path / "created").read_bytes()
        )
    except OSError as exc:
        raise AllocationError(
            f"recover: cannot read promotion recovery state: {exc}"
        ) from exc
    left_in_place: list[str] = []
    if manifest.get("version") == 1:
        restored = _rollback_legacy(root, transaction_path, identifiers)
    else:
        planned = set(manifest.get("planned_creates") or [])
        planned_parents = {
            parent.as_posix()
            for relative in planned
            for parent in Path(relative).parents
            if parent.as_posix() != "."
        }
        # Only newline-terminated records count: a torn final write is ignored.
        created = [
            line.decode("utf-8") for line in created_log.split(b"\n")[:-1] if line
        ]
        created_set = set(created)
        removed = [
            entry for entry in manifest.get("removed") or [] if isinstance(entry, dict)
        ]
        removed_drafts = {entry["path"] for entry in removed}
        # A planned target missing from the log (crash between link and log) is
        # ours only if it is still a hard link of its draft.
        for relative in sorted(planned - created_set):
            path = root / relative
            if not os.path.lexists(path):
                continue
            draft = next(
                (
                    root / draft_relative
                    for draft_relative in removed_drafts
                    if Path(draft_relative).name == path.name
                ),
                None,
            )
            if draft is not None and draft.exists() and os.path.samefile(draft, path):
                created.append(relative)
            else:
                left_in_place.append(relative)
        for relative in reversed(created):
            if relative not in planned and relative not in planned_parents:
                continue
            path = root / relative
            if path.is_dir() and not path.is_symlink():
                try:
                    path.rmdir()
                except OSError:
                    left_in_place.append(relative + "/")
            elif os.path.lexists(path):
                path.unlink()
        for entry in removed + [
            entry
            for entry in manifest.get("replaced") or []
            if isinstance(entry, dict)
        ]:
            _restore_file(root, transaction_path, entry)
        restored = tuple(identifiers)
        for entry in removed + list(manifest.get("replaced") or []):
            if sha256_file(root / entry["path"]) != entry["sha256"]:
                raise AllocationError(
                    f"recover: {entry['path']} could not be restored; the journal "
                    f"is kept at {transaction_path}"
                )

    ledger_path = root / "data" / "id-ledger.yaml"
    if not ledger_path.is_file() or ledger_path.read_bytes() != ledger_content:
        _atomic_replace(ledger_path, ledger_content)
    shutil.rmtree(transaction_path)
    return restored, tuple(left_in_place)


def _rollback_transaction(root: Path, transaction_path: Path) -> tuple[str, ...]:
    restored, _ = _rollback(root, transaction_path)
    return restored


def recover_transaction(root: Path) -> RecoveryResult:
    """Finalise a committed transaction, or roll back an unfinished one."""
    root = root.resolve()
    with _transaction_lock(root, allow_stale=True) as stale_pid:
        transaction_path = root / TRANSACTION_DIRECTORY
        if not transaction_path.is_dir():
            message = "recover: no unfinished promotion transaction exists"
            if stale_pid is not None:
                message += (
                    f"; nothing needs rolling back, so remove the stale lock "
                    f"{root / LOCK_FILENAME} (pid {stale_pid}) by hand"
                )
            raise AllocationError(message)
        manifest = _read_manifest(transaction_path)
        label = manifest.get("label")
        if (transaction_path / "committed").is_file():
            shutil.rmtree(transaction_path)
            return RecoveryResult(
                tuple(manifest["identifiers"]),
                True,
                label if isinstance(label, str) else None,
                stale_pid,
            )
        restored, left_in_place = _rollback(root, transaction_path)
        return RecoveryResult(
            restored,
            False,
            label if isinstance(label, str) else None,
            stale_pid,
            left_in_place,
        )


def recover_promotion(root: Path) -> tuple[str, ...]:
    return recover_transaction(root).identifiers


def _change_set_already_applied(root: Path, change_set: ChangeSet) -> bool:
    try:
        ledger = load_yaml(root / "data" / "id-ledger.yaml")
    except (OSError, yaml.YAMLError):
        return False
    reserved = ledger.get("reserved_ids") if isinstance(ledger, dict) else None
    if not isinstance(reserved, dict):
        return False
    for identifier in change_set.promote:
        resolved = _config_for_identifier(identifier)
        if resolved is None:
            return False
        kind, config = resolved
        target = root / "data" / config.directory / f"{identifier}.yaml"
        if not target.is_file() or identifier in (reserved.get(kind) or []):
            return False
    for replacement in change_set.replace:
        live_path = root / replacement.path
        if not live_path.is_file() or live_path.read_bytes() != replacement.content:
            return False
    for transfer in change_set.evidence:
        destination = root / transfer.destination
        if not destination.is_file() or sha256_file(destination) != transfer.sha256:
            return False
    return True


def _run_transaction(
    root: Path,
    change_set: ChangeSet,
    *,
    consequence: str,
    dry_run: bool,
    schema_dir: Path | None,
    idempotent: bool,
) -> PromotionResult:
    root = root.resolve()
    with _transaction_lock(root):
        _transaction_guard(root)
        if idempotent and _change_set_already_applied(root, change_set):
            return PromotionResult(
                change_set.promote, dry_run, (), change_set.label,
                already_applied=True,
            )
        ledger, live_warnings = _live_precheck(root, schema_dir, consequence)
        plan = _resolve_change_set(root, change_set, ledger)
        warnings = _validate_prospective_promotion(
            root,
            schema_dir,
            plan.batch,
            plan.updated_ledger,
            plan.replacements,
            plan.evidence,
            live_warnings,
        )
        result = PromotionResult(
            change_set.promote,
            dry_run,
            warnings,
            change_set.label,
            tuple(replacement.path for replacement, _ in plan.replacements),
            tuple(transfer.destination for transfer, _ in plan.evidence),
        )
        if dry_run:
            return result

        ledger_path = root / "data" / "id-ledger.yaml"
        transaction_path = _prepare_transaction(
            root,
            list(change_set.promote),
            ledger_path.read_bytes(),
            label=change_set.label,
            replaced=tuple(
                (path, replacement.base_sha256)
                for replacement, path in plan.replacements
            ),
            removed=tuple(
                (draft_path, plan.draft_hashes[draft_path])
                for *_, draft_path, _ in plan.batch
            ),
            planned_creates=tuple(destination for _, destination in plan.evidence)
            + tuple(target for *_, target in plan.batch),
        )
        try:
            for transfer, destination in plan.evidence:
                _apply_step(
                    root,
                    transaction_path,
                    _Step(
                        "copy-evidence",
                        destination,
                        source=transfer.source,
                        sha256=transfer.sha256,
                    ),
                )
            for _, _, _, draft_path, target_path in plan.batch:
                _apply_step(
                    root,
                    transaction_path,
                    _Step("link-draft", target_path, source=draft_path),
                )
            for replacement, live_path in plan.replacements:
                _apply_step(
                    root,
                    transaction_path,
                    _Step("replace", live_path, content=replacement.content),
                )
            if plan.batch:
                _apply_step(
                    root,
                    transaction_path,
                    _Step(
                        "replace",
                        ledger_path,
                        content=yaml.safe_dump(
                            plan.updated_ledger, sort_keys=False, allow_unicode=True
                        ).encode("utf-8"),
                    ),
                )
                _remove_promoted_drafts(root, transaction_path, plan.batch)
            final_validation = validate_repository(root, schema_dir=schema_dir)
            if final_validation.errors:
                details = "\n".join(
                    issue.render() for issue in final_validation.errors[:20]
                )
                raise AllocationError(
                    "post-commit validation: repository validation failed; "
                    "rolling back" + (f":\n{details}" if details else "")
                )
            introduced = _new_warnings(final_validation, live_warnings)
            if introduced:
                raise AllocationError(
                    "post-commit validation: "
                    + "; ".join(
                        f"new warning introduced: {issue}" for issue in introduced
                    )
                    + "; rolling back"
                )
        except BaseException:
            _rollback_transaction(root, transaction_path)
            raise
        _atomic_create(transaction_path / "committed", "")
        try:
            shutil.rmtree(transaction_path)
        except OSError as exc:
            raise AllocationError(
                "commit: the transaction committed successfully, but its journal "
                "cleanup failed; run the recover command to finalize cleanup"
            ) from exc
        return result


def promote_entities(
    root: Path,
    identifiers: list[str],
    *,
    dry_run: bool = False,
    schema_dir: Path | None = None,
) -> PromotionResult:
    return _run_transaction(
        root,
        ChangeSet(None, tuple(identifiers)),
        consequence="nothing was promoted",
        dry_run=dry_run,
        schema_dir=schema_dir,
        idempotent=False,
    )


def apply_change_set(
    root: Path,
    change_set_path: Path,
    *,
    dry_run: bool = False,
    schema_dir: Path | None = None,
) -> PromotionResult:
    """Validate and atomically apply a change set (see data/README.md)."""
    return _run_transaction(
        root,
        load_change_set(Path(change_set_path)),
        consequence="the change set was not applied",
        dry_run=dry_run,
        schema_dir=schema_dir,
        idempotent=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Reserve, materialize and promote stable entity drafts, and apply "
            "change sets."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="repository root (defaults to the script's parent repository)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    reserve = subparsers.add_parser("reserve", help="reserve the next ID")
    reserve.add_argument("kind", choices=sorted(KINDS_BY_SINGULAR))
    reserve.add_argument("--dry-run", action="store_true")
    materialize = subparsers.add_parser(
        "materialize", help="recreate a missing draft for a reserved ID"
    )
    materialize.add_argument("identifier")
    materialize.add_argument("--dry-run", action="store_true")
    promote = subparsers.add_parser(
        "promote", help="validate and promote one or more completed drafts"
    )
    promote.add_argument("identifiers", nargs="+")
    promote.add_argument("--dry-run", action="store_true")
    apply = subparsers.add_parser(
        "apply",
        help="validate and atomically apply a change set of promotions, "
        "replacements and authorised evidence transfers",
    )
    apply.add_argument("change_set", type=Path)
    apply.add_argument("--dry-run", action="store_true")
    subparsers.add_parser(
        "recover",
        help="finalise a committed or roll back an unfinished transaction",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "reserve":
            result = reserve_entity(args.root, args.kind, dry_run=args.dry_run)
            action = "Would create" if result.dry_run else "Created"
            print(
                f"{action} reserved draft {result.identifier} at "
                f"{result.draft_path}"
            )
        elif args.command == "materialize":
            result = materialize_reserved_entity(
                args.root, args.identifier, dry_run=args.dry_run
            )
            action = "Would create" if result.dry_run else "Created"
            print(
                f"{action} reserved draft {result.identifier} at "
                f"{result.draft_path}"
            )
        elif args.command == "promote":
            promotion = promote_entities(
                args.root,
                args.identifiers,
                dry_run=args.dry_run,
            )
            action = "Would promote" if promotion.dry_run else "Promoted"
            print(f"{action} {', '.join(promotion.identifiers)}")
            for warning in promotion.warnings:
                print(warning)
        elif args.command == "apply":
            applied = apply_change_set(
                args.root, args.change_set, dry_run=args.dry_run
            )
            if applied.already_applied:
                print(f"Change set {applied.label!r} already applied; nothing to do")
            else:
                action = "Would apply" if applied.dry_run else "Applied"
                print(
                    f"{action} change set {applied.label!r}: promoted "
                    f"{', '.join(applied.identifiers) or 'none'}; replaced "
                    f"{', '.join(applied.replaced) or 'none'}; transferred "
                    f"{', '.join(applied.transferred) or 'none'}"
                )
                for warning in applied.warnings:
                    print(warning)
        else:
            recovery = recover_transaction(args.root)
            outcome = (
                "finalised the committed transaction"
                if recovery.committed
                else "rolled back the unfinished transaction"
            )
            subject = ", ".join(recovery.identifiers) or recovery.label or "transaction"
            print(f"Recovered {subject}: {outcome}")
            for relative in recovery.left_in_place:
                print(
                    f"NOTE: {relative} is not in the creation log and was left in "
                    "place; check whether this transaction created it"
                )
            if recovery.stale_lock_pid is not None:
                print(
                    f"NOTE: remove the stale lock {args.root.resolve() / LOCK_FILENAME} "
                    f"(pid {recovery.stale_lock_pid}) by hand"
                )
    except AllocationError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
