#!/usr/bin/env python3
"""Reserve a stable entity ID and create a non-live YAML draft safely."""

from __future__ import annotations

import argparse
import copy
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

if __package__:
    from .validate_data import REPOSITORY_ROOT, validate_repository
    from .validation.identifiers import (
        ENTITY_CONFIGS,
        KINDS_BY_SINGULAR,
        EntityConfig,
        format_identifier,
        parse_identifier,
    )
    from .validation.model import load_yaml
else:
    from validate_data import REPOSITORY_ROOT, validate_repository
    from validation.identifiers import (
        ENTITY_CONFIGS,
        KINDS_BY_SINGULAR,
        EntityConfig,
        format_identifier,
        parse_identifier,
    )
    from validation.model import load_yaml


class AllocationError(RuntimeError):
    """Raised when an entity reservation cannot be completed safely."""


@dataclass(frozen=True)
class ReservationResult:
    identifier: str
    draft_path: Path
    dry_run: bool
    recovered: bool = False


def _validated_ledger(
    root: Path, schema_dir: Path | None
) -> dict[str, Any]:
    result = validate_repository(root, schema_dir=schema_dir)
    if result.errors:
        details = "\n".join(issue.render() for issue in result.errors[:10])
        raise AllocationError(
            "repository validation failed; no allocation was attempted"
            + (f":\n{details}" if details else "")
        )
    ledger_path = root / "data" / "id-ledger.yaml"
    ledger = load_yaml(ledger_path)
    if not isinstance(ledger, dict) or ledger.get("version") != 2:
        raise AllocationError("ID ledger version 2 is required")
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


def _atomic_replace(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            os.chmod(temporary_path, path.stat().st_mode & 0o777)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _atomic_create(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary_path, path)
        except FileExistsError as exc:
            raise AllocationError(f"refusing to overwrite {path}") from exc
    finally:
        temporary_path.unlink(missing_ok=True)


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
            f"{identifier} remains safely reserved, but its draft could not be "
            "created; rerun with the materialize command"
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reserve stable IDs and create editable entity drafts."
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "reserve":
            result = reserve_entity(args.root, args.kind, dry_run=args.dry_run)
        else:
            result = materialize_reserved_entity(
                args.root, args.identifier, dry_run=args.dry_run
            )
    except AllocationError as exc:
        print(f"ERROR: {exc}")
        return 1
    action = "Would create" if result.dry_run else "Created"
    print(f"{action} reserved draft {result.identifier} at {result.draft_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
