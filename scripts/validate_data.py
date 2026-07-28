#!/usr/bin/env python3
"""Validate structured genealogy data without changing repository content."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
    from referencing import Registry, Resource
except ImportError as exc:  # pragma: no cover - exercised only before setup
    dependency = getattr(exc, "name", "a required dependency")
    print(
        f"Missing {dependency}. Install project dependencies with 'uv sync'.",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc

if __package__:
    from .validation.coverage import (
        RECORD_COVERAGE_SCHEMA,
        validate_record_coverage,
    )
    from .validation.inventory import (
        DOCUMENT_INVENTORY_SCHEMA,
        validate_document_inventory,
    )
    from .validation.identifiers import (
        ENTITY_CONFIGS,
        format_identifiers,
        parse_identifier,
    )
    from .validation.model import (
        Issue,
        LoadedEntity,
        ValidationResult,
        display_path,
        json_path,
        load_yaml,
    )
    from .validation.references import validate_references
    from .validation.rules import (
        validate_date_ranges,
        validate_duplicate_identities,
        validate_evidence_files,
        validate_evidence_statuses,
        validate_event_principals,
        validate_family_structure_and_chronology,
        validate_place_hierarchy,
        validate_privacy,
    )
else:
    from validation.coverage import (
        RECORD_COVERAGE_SCHEMA,
        validate_record_coverage,
    )
    from validation.inventory import (
        DOCUMENT_INVENTORY_SCHEMA,
        validate_document_inventory,
    )
    from validation.identifiers import (
        ENTITY_CONFIGS,
        format_identifiers,
        parse_identifier,
    )
    from validation.model import (
        Issue,
        LoadedEntity,
        ValidationResult,
        display_path,
        json_path,
        load_yaml,
    )
    from validation.references import validate_references
    from validation.rules import (
        validate_date_ranges,
        validate_duplicate_identities,
        validate_evidence_files,
        validate_evidence_statuses,
        validate_event_principals,
        validate_family_structure_and_chronology,
        validate_place_hierarchy,
        validate_privacy,
    )


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_validators(
    schema_dir: Path, root: Path, issues: list[Issue]
) -> dict[str, Draft202012Validator]:
    schema_documents: dict[str, dict[str, Any]] = {}
    resources: list[tuple[str, Resource[Any]]] = []

    for path in sorted(schema_dir.glob("*.schema.json")):
        location = display_path(path, root)
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(document)
            resource = Resource.from_contents(document)
        except (OSError, json.JSONDecodeError, SchemaError) as exc:
            issues.append(Issue("error", location, f"invalid schema: {exc}"))
            continue
        schema_documents[path.name] = document
        resources.append((document["$id"], resource))

    registry = Registry().with_resources(resources)
    validators: dict[str, Draft202012Validator] = {}
    for kind, config in ENTITY_CONFIGS.items():
        document = schema_documents.get(config.schema_filename)
        if document is None:
            issues.append(
                Issue(
                    "error",
                    display_path(schema_dir / config.schema_filename, root),
                    "required entity schema is unavailable",
                )
            )
            continue
        validators[kind] = Draft202012Validator(
            document,
            registry=registry,
            format_checker=FormatChecker(),
        )
    auxiliary_schemas = (
        ("document_inventory", DOCUMENT_INVENTORY_SCHEMA),
        ("record_coverage", RECORD_COVERAGE_SCHEMA),
    )
    for validator_name, schema_filename in auxiliary_schemas:
        document = schema_documents.get(schema_filename)
        if document is None:
            issues.append(
                Issue(
                    "error",
                    display_path(schema_dir / schema_filename, root),
                    f"required {validator_name.replace('_', ' ')} schema is "
                    "unavailable",
                )
            )
            continue
        validators[validator_name] = Draft202012Validator(
            document,
            registry=registry,
            format_checker=FormatChecker(),
        )
    return validators


def load_entities(
    root: Path,
    validators: Mapping[str, Draft202012Validator],
    issues: list[Issue],
) -> tuple[dict[str, dict[str, LoadedEntity]], int]:
    entities: dict[str, dict[str, LoadedEntity]] = {
        kind: {} for kind in ENTITY_CONFIGS
    }
    entity_count = 0

    for kind, config in ENTITY_CONFIGS.items():
        directory = root / "data" / config.directory
        if not directory.is_dir():
            continue

        candidates = sorted(
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in {".yaml", ".yml"}
        )
        for path in candidates:
            entity_count += 1
            location = display_path(path, root)
            if path.suffix != ".yaml":
                issues.append(
                    Issue("error", location, "entity files must use the .yaml suffix")
                )
            try:
                raw = load_yaml(path)
            except (OSError, yaml.YAMLError) as exc:
                issues.append(Issue("error", location, f"invalid YAML: {exc}"))
                continue
            if not isinstance(raw, dict):
                issues.append(
                    Issue("error", location, "entity document must be a YAML mapping")
                )
                continue

            validator = validators.get(kind)
            if validator is not None:
                schema_errors = sorted(
                    validator.iter_errors(raw),
                    key=lambda error: tuple(str(part) for part in error.absolute_path),
                )
                for error in schema_errors:
                    issues.append(
                        Issue(
                            "error",
                            f"{location}:{json_path(error.absolute_path)}",
                            error.message,
                        )
                    )

            loaded = LoadedEntity(kind, path, raw)
            identifier = loaded.identifier
            if identifier is None:
                continue
            expected_filename = f"{identifier}.yaml"
            if path.name != expected_filename:
                issues.append(
                    Issue(
                        "error",
                        location,
                        f"filename must be {expected_filename!r} to match the entity ID",
                    )
                )
            previous = entities[kind].get(identifier)
            if previous is not None:
                issues.append(
                    Issue(
                        "error",
                        location,
                        "duplicate entity ID also used by "
                        f"{display_path(previous.path, root)}",
                    )
                )
                continue
            entities[kind][identifier] = loaded

    return entities, entity_count


def validate_id_ledger(
    root: Path,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    path = root / "data" / "id-ledger.yaml"
    location = display_path(path, root)
    try:
        ledger = load_yaml(path)
    except FileNotFoundError:
        issues.append(Issue("error", location, "ID ledger is missing"))
        return
    except (OSError, yaml.YAMLError) as exc:
        issues.append(Issue("error", location, f"invalid YAML: {exc}"))
        return

    if not isinstance(ledger, dict):
        issues.append(Issue("error", location, "ID ledger must be a YAML mapping"))
        return
    if ledger.get("version") != 2:
        issues.append(Issue("error", location, "ID ledger version must be 2"))

    reserved_ids = ledger.get("reserved_ids")
    retired_ids = ledger.get("retired_ids")
    if not isinstance(reserved_ids, dict) or not isinstance(retired_ids, dict):
        issues.append(
            Issue(
                "error",
                location,
                "ID ledger requires reserved_ids and retired_ids mappings",
            )
        )
        return

    expected_kinds = set(ENTITY_CONFIGS)
    for section_name, section in (
        ("reserved_ids", reserved_ids),
        ("retired_ids", retired_ids),
    ):
        missing = expected_kinds - set(section)
        extra = set(section) - expected_kinds
        if missing:
            issues.append(
                Issue(
                    "error",
                    location,
                    f"{section_name} is missing: {', '.join(sorted(missing))}",
                )
            )
        if extra:
            issues.append(
                Issue(
                    "error",
                    location,
                    f"{section_name} has unknown keys: {', '.join(sorted(extra))}",
                )
            )

    parsed_sections: dict[str, dict[str, set[int]]] = {
        "reserved_ids": {},
        "retired_ids": {},
    }
    for section_name, section in (
        ("reserved_ids", reserved_ids),
        ("retired_ids", retired_ids),
    ):
        for kind, config in ENTITY_CONFIGS.items():
            values = section.get(kind)
            if not isinstance(values, list):
                issues.append(
                    Issue("error", location, f"{section_name}.{kind} must be a list")
                )
                parsed_sections[section_name][kind] = set()
                continue
            numbers: set[int] = set()
            seen: set[str] = set()
            for identifier in values:
                if not isinstance(identifier, str):
                    issues.append(
                        Issue(
                            "error",
                            location,
                            f"{section_name}.{kind} contains a non-string value",
                        )
                    )
                    continue
                if identifier in seen:
                    issues.append(
                        Issue(
                            "error",
                            location,
                            f"{section_name}.{kind} repeats {identifier}",
                        )
                    )
                    continue
                seen.add(identifier)
                number = parse_identifier(identifier, config)
                if number is None:
                    issues.append(
                        Issue(
                            "error",
                            location,
                            f"{section_name}.{kind} has invalid identifier "
                            f"{identifier!r}",
                        )
                    )
                    continue
                numbers.add(number)
            parsed_sections[section_name][kind] = numbers

    for kind, config in ENTITY_CONFIGS.items():
        current_numbers = {
            number
            for identifier in entities[kind]
            if (number := parse_identifier(identifier, config)) is not None
        }
        reserved_numbers = parsed_sections["reserved_ids"].get(kind, set())
        retired_numbers = parsed_sections["retired_ids"].get(kind, set())
        overlaps = {
            "current and reserved": current_numbers & reserved_numbers,
            "current and retired": current_numbers & retired_numbers,
            "reserved and retired": reserved_numbers & retired_numbers,
        }
        for label, overlap in overlaps.items():
            if not overlap:
                continue
            issues.append(
                Issue(
                    "error",
                    location,
                    f"{label} identifiers overlap: "
                    f"{format_identifiers(overlap, config.prefix)}",
                )
            )

        allocated = current_numbers | reserved_numbers | retired_numbers
        expected_allocated = (
            set(range(1, max(allocated) + 1)) if allocated else set()
        )
        unaccounted = expected_allocated - allocated
        if unaccounted:
            issues.append(
                Issue(
                    "error",
                    location,
                    "allocated sequence has unaccounted identifiers: "
                    f"{format_identifiers(unaccounted, config.prefix)}",
                )
            )

    drafts_dir = root / "research" / "entity-drafts"
    if not drafts_dir.is_dir():
        return
    reserved = {
        identifier
        for kind in ENTITY_CONFIGS
        for identifier in reserved_ids.get(kind, [])
        if isinstance(identifier, str)
    }
    for draft_path in sorted(drafts_dir.glob("*.yaml")):
        identifier = draft_path.stem
        draft_location = display_path(draft_path, root)
        config = next(
            (
                candidate
                for candidate in ENTITY_CONFIGS.values()
                if candidate.pattern.fullmatch(identifier)
            ),
            None,
        )
        if config is None:
            issues.append(
                Issue(
                    "error",
                    draft_location,
                    "draft filename is not a valid entity identifier",
                )
            )
            continue
        if identifier not in reserved:
            issues.append(
                Issue(
                    "error",
                    draft_location,
                    f"draft identifier {identifier} is not reserved",
                )
            )
        try:
            draft = load_yaml(draft_path)
        except (OSError, yaml.YAMLError) as exc:
            issues.append(Issue("error", draft_location, f"invalid YAML: {exc}"))
            continue
        if not isinstance(draft, dict) or draft.get("id") != identifier:
            issues.append(
                Issue(
                    "error",
                    f"{draft_location}:$.id",
                    f"draft ID must match filename {identifier}",
                )
            )


def validate_repository(
    root: Path, schema_dir: Path | None = None
) -> ValidationResult:
    root = root.resolve()
    schema_dir = (schema_dir or root / "schemas").resolve()
    issues: list[Issue] = []
    validators = load_validators(schema_dir, root, issues)
    entities, entity_count = load_entities(root, validators, issues)

    validate_id_ledger(root, entities, issues)
    validate_document_inventory(
        root, validators.get("document_inventory"), entities, issues
    )
    validate_record_coverage(
        root, validators.get("record_coverage"), entities, issues
    )
    validate_references(root, entities, issues)
    validate_evidence_statuses(root, entities, issues)
    validate_date_ranges(root, entities, issues)
    validate_event_principals(root, entities, issues)
    validate_family_structure_and_chronology(root, entities, issues)
    validate_duplicate_identities(root, entities, issues)
    validate_privacy(root, entities, issues)
    validate_evidence_files(root, entities, issues)
    validate_place_hierarchy(root, entities, issues)

    severity_order = {"error": 0, "warning": 1}
    ordered = tuple(
        sorted(
            issues,
            key=lambda issue: (
                severity_order.get(issue.severity, 9),
                issue.location,
                issue.message,
            ),
        )
    )
    return ValidationResult(ordered, entity_count)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate YAML entities and cross-file genealogy rules."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="repository root (defaults to the script's parent repository)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_repository(args.root)
    for issue in result.issues:
        print(issue.render())
    print(
        f"Validated {result.entity_count} entities: "
        f"{len(result.errors)} error(s), {len(result.warnings)} warning(s)."
    )
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
