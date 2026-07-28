#!/usr/bin/env python3
"""Reserve a stable entity ID and create a non-live YAML draft safely."""

from __future__ import annotations

import argparse
import copy
import os
import shutil
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


@dataclass(frozen=True)
class PromotionResult:
    identifiers: tuple[str, ...]
    dry_run: bool
    warnings: tuple[str, ...] = ()


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


def _copy_tree(source: Path, destination: Path, *, hardlink: bool = False) -> None:
    if not source.is_dir():
        return
    copy_function = os.link if hardlink else shutil.copy2
    shutil.copytree(source, destination, copy_function=copy_function)


def _validate_prospective_promotion(
    root: Path,
    schema_dir: Path | None,
    batch: list[tuple[str, str, EntityConfig, Path, Path]],
    updated_ledger: dict[str, Any],
) -> tuple[str, ...]:
    resolved_schema_dir = schema_dir or root / "schemas"
    with tempfile.TemporaryDirectory(
        dir=root, prefix=".promotion-preview-"
    ) as temporary_name:
        staging_root = Path(temporary_name)
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
        (staging_root / "data" / "id-ledger.yaml").write_text(
            yaml.safe_dump(updated_ledger, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        validation = validate_repository(
            staging_root, schema_dir=resolved_schema_dir
        )
        if validation.errors:
            details = "\n".join(issue.render() for issue in validation.errors[:20])
            raise AllocationError(
                "prospective promotion is invalid; live data was not changed"
                + (f":\n{details}" if details else "")
            )
        return tuple(issue.render() for issue in validation.warnings)


def _prepare_transaction(
    root: Path,
    identifiers: list[str],
    ledger_content: str,
) -> Path:
    transaction_path = root / ".entity-promotion-transaction"
    if transaction_path.exists():
        raise AllocationError(
            "an unfinished promotion transaction exists; run the recover command"
        )
    preparing_path = Path(
        tempfile.mkdtemp(dir=root, prefix=".promotion-prepare-")
    )
    try:
        (preparing_path / "manifest.yaml").write_text(
            yaml.safe_dump(
                {"version": 1, "identifiers": identifiers},
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
        (preparing_path / "id-ledger.yaml").write_text(
            ledger_content, encoding="utf-8"
        )
        os.replace(preparing_path, transaction_path)
    finally:
        if preparing_path.exists():
            shutil.rmtree(preparing_path)
    return transaction_path


def _remove_promoted_drafts(
    batch: list[tuple[str, str, EntityConfig, Path, Path]],
) -> None:
    for _, _, _, draft_path, _ in batch:
        draft_path.unlink()


def _rollback_transaction(root: Path, transaction_path: Path) -> tuple[str, ...]:
    try:
        manifest = load_yaml(transaction_path / "manifest.yaml")
        ledger_content = (transaction_path / "id-ledger.yaml").read_text(
            encoding="utf-8"
        )
    except (OSError, yaml.YAMLError) as exc:
        raise AllocationError(
            f"cannot read promotion recovery state: {exc}"
        ) from exc
    identifiers = manifest.get("identifiers") if isinstance(manifest, dict) else None
    if not isinstance(identifiers, list) or not all(
        isinstance(identifier, str) for identifier in identifiers
    ):
        raise AllocationError("promotion recovery manifest is invalid")

    restored: list[str] = []
    for identifier in identifiers:
        resolved = _config_for_identifier(identifier)
        if resolved is None:
            raise AllocationError(
                f"promotion recovery contains invalid identifier {identifier!r}"
            )
        _, config = resolved
        draft_path = root / "research" / "entity-drafts" / f"{identifier}.yaml"
        target_path = root / "data" / config.directory / f"{identifier}.yaml"
        if not draft_path.exists() and not target_path.exists():
            raise AllocationError(
                f"cannot recover {identifier}: both draft and live target are missing"
            )
        if not draft_path.exists():
            draft_path.parent.mkdir(parents=True, exist_ok=True)
            os.link(target_path, draft_path)
        if target_path.exists():
            target_path.unlink()
        restored.append(identifier)

    _atomic_replace(root / "data" / "id-ledger.yaml", ledger_content)
    shutil.rmtree(transaction_path)
    return tuple(restored)


def recover_promotion(root: Path) -> tuple[str, ...]:
    root = root.resolve()
    transaction_path = root / ".entity-promotion-transaction"
    if not transaction_path.is_dir():
        raise AllocationError("no unfinished promotion transaction exists")
    committed_marker = transaction_path / "committed"
    if committed_marker.is_file():
        manifest = load_yaml(transaction_path / "manifest.yaml")
        identifiers = (
            manifest.get("identifiers") if isinstance(manifest, dict) else None
        )
        if not isinstance(identifiers, list) or not all(
            isinstance(identifier, str) for identifier in identifiers
        ):
            raise AllocationError("promotion recovery manifest is invalid")
        shutil.rmtree(transaction_path)
        return tuple(identifiers)
    return _rollback_transaction(root, transaction_path)


def promote_entities(
    root: Path,
    identifiers: list[str],
    *,
    dry_run: bool = False,
    schema_dir: Path | None = None,
) -> PromotionResult:
    root = root.resolve()
    transaction_path = root / ".entity-promotion-transaction"
    if transaction_path.exists():
        raise AllocationError(
            "an unfinished promotion transaction exists; run the recover command"
        )
    ledger = _validated_ledger(root, schema_dir)
    batch = _resolve_promotion_batch(root, identifiers, ledger)
    updated_ledger = _ledger_without_reservations(ledger, batch)
    warnings = _validate_prospective_promotion(
        root, schema_dir, batch, updated_ledger
    )
    if dry_run:
        return PromotionResult(tuple(identifiers), True, warnings)

    original_ledger_content = (
        root / "data" / "id-ledger.yaml"
    ).read_text(encoding="utf-8")
    transaction_path = _prepare_transaction(
        root, identifiers, original_ledger_content
    )
    try:
        for _, _, _, draft_path, target_path in batch:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.link(draft_path, target_path)
            except FileExistsError as exc:
                raise AllocationError(f"refusing to overwrite {target_path}") from exc
        _atomic_replace(
            root / "data" / "id-ledger.yaml",
            yaml.safe_dump(updated_ledger, sort_keys=False, allow_unicode=True),
        )
        _remove_promoted_drafts(batch)
        final_validation = validate_repository(root, schema_dir=schema_dir)
        if final_validation.errors:
            details = "\n".join(
                issue.render() for issue in final_validation.errors[:20]
            )
            raise AllocationError(
                "post-promotion validation failed; rolling back"
                + (f":\n{details}" if details else "")
            )
    except BaseException:
        _rollback_transaction(root, transaction_path)
        raise
    _atomic_create(transaction_path / "committed", "")
    try:
        shutil.rmtree(transaction_path)
    except OSError as exc:
        raise AllocationError(
            "promotion committed successfully, but transaction cleanup failed; "
            "run the recover command to finalize cleanup"
        ) from exc
    return PromotionResult(tuple(identifiers), False, warnings)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reserve, materialize and promote stable entity drafts."
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
    subparsers.add_parser(
        "recover", help="roll back an unfinished promotion transaction"
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
        else:
            restored = recover_promotion(args.root)
            print(f"Recovered {', '.join(restored)}")
    except AllocationError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
