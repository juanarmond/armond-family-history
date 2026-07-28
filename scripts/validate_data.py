#!/usr/bin/env python3
"""Validate structured genealogy data without changing repository content."""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping

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


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONFIRMING_EVIDENCE_CLASSES = {"original_record", "contemporary_record"}
NON_TREE_EVIDENCE_CLASSES = {
    "original_record",
    "contemporary_record",
    "newspaper",
    "official_index",
    "published_genealogy",
}
POSTHUMOUS_BIRTH_ALLOWANCE = timedelta(days=310)
MINIMUM_PARENT_AGE = timedelta(days=8 * 365)


@dataclass(frozen=True)
class EntityConfig:
    directory: str
    prefix: str
    pattern: re.Pattern[str]
    schema_filename: str


ENTITY_CONFIGS: dict[str, EntityConfig] = {
    "people": EntityConfig(
        "people", "P", re.compile(r"^P-(?!0000$)[0-9]{4}$"), "person.schema.json"
    ),
    "families": EntityConfig(
        "families", "F", re.compile(r"^F-(?!0000$)[0-9]{4}$"), "family.schema.json"
    ),
    "events": EntityConfig(
        "events", "E", re.compile(r"^E-(?!0000$)[0-9]{4}$"), "event.schema.json"
    ),
    "places": EntityConfig(
        "places", "PL", re.compile(r"^PL-(?!0000$)[0-9]{4}$"), "place.schema.json"
    ),
    "sources": EntityConfig(
        "sources",
        "SRC",
        re.compile(r"^SRC-(?!0000$)[0-9]{4}$"),
        "source.schema.json",
    ),
}

DOCUMENT_INVENTORY_SCHEMA = "document-inventory.schema.json"

REFERENCE_KEYS = {
    "person_id": "people",
    "parent_ids": "people",
    "linked_people": "people",
    "family_ids": "families",
    "linked_families": "families",
    "event_ids": "events",
    "linked_events": "events",
    "place_id": "places",
    "parent_place_id": "places",
    "linked_places": "places",
    "source_ids": "sources",
}


@dataclass(frozen=True)
class Issue:
    severity: str
    location: str
    message: str

    def render(self) -> str:
        return f"{self.severity.upper():7} {self.location}: {self.message}"


@dataclass(frozen=True)
class LoadedEntity:
    kind: str
    path: Path
    data: dict[str, Any]

    @property
    def identifier(self) -> str | None:
        value = self.data.get("id")
        return value if isinstance(value, str) else None


@dataclass(frozen=True)
class DateInterval:
    earliest: date
    latest: date


@dataclass(frozen=True)
class ValidationResult:
    issues: tuple[Issue, ...]
    entity_count: int

    @property
    def errors(self) -> tuple[Issue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "error")

    @property
    def warnings(self) -> tuple[Issue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "warning")


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects silently overwritten mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.load(handle, Loader=UniqueKeyLoader)


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def json_path(parts: Iterable[Any]) -> str:
    rendered = "$"
    for part in parts:
        if isinstance(part, int):
            rendered += f"[{part}]"
        else:
            rendered += f".{part}"
    return rendered


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
    inventory_document = schema_documents.get(DOCUMENT_INVENTORY_SCHEMA)
    if inventory_document is None:
        issues.append(
            Issue(
                "error",
                display_path(schema_dir / DOCUMENT_INVENTORY_SCHEMA, root),
                "required document inventory schema is unavailable",
            )
        )
    else:
        validators["document_inventory"] = Draft202012Validator(
            inventory_document,
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


def parse_identifier(identifier: str, config: EntityConfig) -> int | None:
    if not config.pattern.fullmatch(identifier):
        return None
    return int(identifier.rsplit("-", 1)[1])


def format_identifiers(numbers: Iterable[int], prefix: str) -> str:
    values = sorted(set(numbers))
    labels = [f"{prefix}-{number:04d}" for number in values[:10]]
    if len(values) > 10:
        labels.append(f"and {len(values) - 10} more")
    return ", ".join(labels)


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
    if ledger.get("version") != 1:
        issues.append(Issue("error", location, "ID ledger version must be 1"))

    next_ids = ledger.get("next_ids")
    retired_ids = ledger.get("retired_ids")
    if not isinstance(next_ids, dict) or not isinstance(retired_ids, dict):
        issues.append(
            Issue(
                "error",
                location,
                "ID ledger requires next_ids and retired_ids mappings",
            )
        )
        return

    expected_kinds = set(ENTITY_CONFIGS)
    for section_name, section in (
        ("next_ids", next_ids),
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

    for kind, config in ENTITY_CONFIGS.items():
        next_identifier = next_ids.get(kind)
        if not isinstance(next_identifier, str):
            issues.append(
                Issue("error", location, f"next_ids.{kind} must be an identifier")
            )
            continue
        next_number = parse_identifier(next_identifier, config)
        if next_number is None:
            issues.append(
                Issue(
                    "error",
                    location,
                    f"next_ids.{kind} has invalid format: {next_identifier!r}",
                )
            )
            continue

        retired = retired_ids.get(kind)
        if not isinstance(retired, list):
            issues.append(
                Issue("error", location, f"retired_ids.{kind} must be a list")
            )
            continue

        retired_numbers: set[int] = set()
        seen_retired: set[str] = set()
        for identifier in retired:
            if not isinstance(identifier, str):
                issues.append(
                    Issue(
                        "error",
                        location,
                        f"retired_ids.{kind} contains a non-string value",
                    )
                )
                continue
            if identifier in seen_retired:
                issues.append(
                    Issue(
                        "error",
                        location,
                        f"retired_ids.{kind} repeats {identifier}",
                    )
                )
                continue
            seen_retired.add(identifier)
            number = parse_identifier(identifier, config)
            if number is None:
                issues.append(
                    Issue(
                        "error",
                        location,
                        f"retired_ids.{kind} has invalid identifier {identifier!r}",
                    )
                )
                continue
            retired_numbers.add(number)

        current_numbers = {
            number
            for identifier in entities[kind]
            if (number := parse_identifier(identifier, config)) is not None
        }
        overlap = current_numbers & retired_numbers
        if overlap:
            issues.append(
                Issue(
                    "error",
                    location,
                    "current and retired identifiers overlap: "
                    f"{format_identifiers(overlap, config.prefix)}",
                )
            )

        allocated = current_numbers | retired_numbers
        expected_allocated = set(range(1, next_number))
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
        beyond_next = allocated - expected_allocated
        if beyond_next:
            issues.append(
                Issue(
                    "error",
                    location,
                    f"next_ids.{kind} must advance beyond: "
                    f"{format_identifiers(beyond_next, config.prefix)}",
                )
            )


def iter_references(
    value: Any, path: tuple[Any, ...] = ()
) -> Iterator[tuple[str, str, tuple[Any, ...]]]:
    if isinstance(value, dict):
        for key, child in value.items():
            target_kind = REFERENCE_KEYS.get(key)
            child_path = path + (key,)
            if target_kind is not None:
                references = child if isinstance(child, list) else [child]
                for index, identifier in enumerate(references):
                    if isinstance(identifier, str):
                        reference_path = (
                            child_path + (index,)
                            if isinstance(child, list)
                            else child_path
                        )
                        yield target_kind, identifier, reference_path
            yield from iter_references(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_references(child, path + (index,))


def validate_references(
    root: Path,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    for kind_entities in entities.values():
        for entity in kind_entities.values():
            location = display_path(entity.path, root)
            for target_kind, identifier, path in iter_references(entity.data):
                if identifier not in entities[target_kind]:
                    issues.append(
                        Issue(
                            "error",
                            f"{location}:{json_path(path)}",
                            f"reference {identifier!r} does not resolve",
                        )
                    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_document_inventory(
    root: Path,
    validator: Draft202012Validator | None,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    path = root / "research" / "document-inventory.yaml"
    location = display_path(path, root)
    try:
        inventory = load_yaml(path)
    except FileNotFoundError:
        issues.append(Issue("error", location, "document inventory is missing"))
        return
    except (OSError, yaml.YAMLError) as exc:
        issues.append(Issue("error", location, f"invalid YAML: {exc}"))
        return

    if not isinstance(inventory, dict):
        issues.append(
            Issue("error", location, "document inventory must be a YAML mapping")
        )
        return

    if validator is not None:
        schema_errors = sorted(
            validator.iter_errors(inventory),
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

    documents = inventory.get("documents")
    if not isinstance(documents, list):
        return

    by_id: dict[str, tuple[int, dict[str, Any]]] = {}
    file_owners: dict[str, str] = {}
    hash_owners: dict[str, set[str]] = defaultdict(set)
    proposed_sources: dict[str, str] = {}
    inventory_numbers: set[int] = set()

    for index, document in enumerate(documents):
        if not isinstance(document, dict):
            continue
        document_location = f"{location}:$.documents[{index}]"
        inventory_id = document.get("inventory_id")
        if isinstance(inventory_id, str):
            match = re.fullmatch(r"DOC-(?!0000$)([0-9]{4})", inventory_id)
            if match:
                inventory_numbers.add(int(match.group(1)))
            if inventory_id in by_id:
                issues.append(
                    Issue(
                        "error",
                        f"{document_location}.inventory_id",
                        f"duplicate inventory ID {inventory_id}",
                    )
                )
            else:
                by_id[inventory_id] = (index, document)

        proposed_source_id = document.get("proposed_source_id")
        if isinstance(proposed_source_id, str):
            previous = proposed_sources.get(proposed_source_id)
            if previous is not None and previous != inventory_id:
                issues.append(
                    Issue(
                        "error",
                        f"{document_location}.proposed_source_id",
                        f"source ID {proposed_source_id} is also proposed by {previous}",
                    )
                )
            elif isinstance(inventory_id, str):
                proposed_sources[proposed_source_id] = inventory_id
            if (
                document.get("status") == "catalogued"
                and proposed_source_id not in entities["sources"]
            ):
                issues.append(
                    Issue(
                        "error",
                        f"{document_location}.proposed_source_id",
                        f"catalogued source {proposed_source_id} does not resolve",
                    )
                )

        files = document.get("files")
        if not isinstance(files, list):
            continue
        for file_index, file_record in enumerate(files):
            if not isinstance(file_record, dict):
                continue
            file_location = f"{document_location}.files[{file_index}]"
            relative_path = file_record.get("path")
            expected_hash = file_record.get("sha256")
            if isinstance(relative_path, str):
                previous_owner = file_owners.get(relative_path)
                if previous_owner is not None and previous_owner != inventory_id:
                    issues.append(
                        Issue(
                            "error",
                            f"{file_location}.path",
                            f"file path is already inventoried by {previous_owner}",
                        )
                    )
                elif isinstance(inventory_id, str):
                    file_owners[relative_path] = inventory_id
                candidate = (root / relative_path).resolve()
                try:
                    candidate.relative_to(root.resolve())
                except ValueError:
                    issues.append(
                        Issue(
                            "error",
                            f"{file_location}.path",
                            "inventory path escapes the repository",
                        )
                    )
                    continue
                if not candidate.is_file():
                    issues.append(
                        Issue(
                            "error",
                            f"{file_location}.path",
                            f"inventoried file does not exist: {relative_path}",
                        )
                    )
                elif isinstance(expected_hash, str):
                    if sha256_file(candidate) != expected_hash:
                        issues.append(
                            Issue(
                                "error",
                                f"{file_location}.sha256",
                                f"checksum does not match {relative_path}",
                            )
                        )
            if isinstance(expected_hash, str) and isinstance(inventory_id, str):
                hash_owners[expected_hash].add(inventory_id)

        if document.get("status") in {"reviewed", "catalogued"}:
            pending = [
                file_index
                for file_index, file_record in enumerate(files)
                if isinstance(file_record, dict)
                and file_record.get("privacy_review") != "cleared"
            ]
            if pending:
                issues.append(
                    Issue(
                        "error",
                        f"{document_location}.files",
                        "reviewed or catalogued documents require every retained "
                        "file to have privacy_review 'cleared'",
                    )
                )

    if inventory_numbers:
        expected_numbers = set(range(1, max(inventory_numbers) + 1))
        missing_numbers = expected_numbers - inventory_numbers
        if missing_numbers:
            labels = ", ".join(
                f"DOC-{number:04d}" for number in sorted(missing_numbers)
            )
            issues.append(
                Issue(
                    "error",
                    f"{location}:$.documents",
                    f"inventory sequence has unaccounted identifiers: {labels}",
                )
            )

    for inventory_id, (index, document) in by_id.items():
        duplicate_of = document.get("duplicate_of")
        document_location = f"{location}:$.documents[{index}]"
        if not isinstance(duplicate_of, str):
            continue
        if duplicate_of == inventory_id:
            issues.append(
                Issue(
                    "error",
                    f"{document_location}.duplicate_of",
                    "a document cannot be a duplicate of itself",
                )
            )
        elif duplicate_of not in by_id:
            issues.append(
                Issue(
                    "error",
                    f"{document_location}.duplicate_of",
                    f"duplicate target {duplicate_of} does not resolve",
                )
            )
        else:
            own_hashes = {
                file_record.get("sha256")
                for file_record in document.get("files", [])
                if isinstance(file_record, dict)
                and isinstance(file_record.get("sha256"), str)
            }
            target_document = by_id[duplicate_of][1]
            target_hashes = {
                file_record.get("sha256")
                for file_record in target_document.get("files", [])
                if isinstance(file_record, dict)
                and isinstance(file_record.get("sha256"), str)
            }
            if own_hashes.isdisjoint(target_hashes):
                issues.append(
                    Issue(
                        "error",
                        f"{document_location}.duplicate_of",
                        f"duplicate {inventory_id} shares no file checksum with "
                        f"{duplicate_of}",
                    )
                )

    for checksum, owners in hash_owners.items():
        if len(owners) < 2:
            continue
        canonical = [
            inventory_id
            for inventory_id in owners
            if by_id.get(inventory_id, (0, {}))[1].get("duplicate_of") is None
        ]
        if len(canonical) != 1:
            issues.append(
                Issue(
                    "error",
                    f"{location}:$.documents",
                    "identical checksum requires exactly one canonical document "
                    f"and explicit duplicate_of links: {', '.join(sorted(owners))}",
                )
            )


def iter_status_claims(
    value: Any, path: tuple[Any, ...] = ()
) -> Iterator[tuple[str, list[str], tuple[Any, ...]]]:
    if isinstance(value, dict):
        status = value.get("status")
        source_ids = value.get("source_ids")
        if isinstance(status, str):
            cited_ids = (
                [
                    identifier
                    for identifier in source_ids
                    if isinstance(identifier, str)
                ]
                if isinstance(source_ids, list)
                else []
            )
            yield status, cited_ids, path
        for key, child in value.items():
            yield from iter_status_claims(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_status_claims(child, path + (index,))


def validate_evidence_statuses(
    root: Path,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    source_data = {
        identifier: entity.data for identifier, entity in entities["sources"].items()
    }

    for source_id, source in source_data.items():
        location = display_path(entities["sources"][source_id].path, root)
        if (
            source.get("evidence_class") == "collaborative_tree"
            and source.get("usage") != "lead_only"
        ):
            issues.append(
                Issue(
                    "error",
                    f"{location}:$.usage",
                    "collaborative trees must use usage 'lead_only'",
                )
            )

    for kind_entities in entities.values():
        for entity in kind_entities.values():
            location = display_path(entity.path, root)
            for status, source_ids, path in iter_status_claims(entity.data):
                cited = [
                    source_data[source_id]
                    for source_id in source_ids
                    if source_id in source_data
                ]
                if status == "confirmed":
                    qualifies = any(
                        source.get("usage") == "evidence"
                        and source.get("evidence_class")
                        in CONFIRMING_EVIDENCE_CLASSES
                        for source in cited
                    )
                    if not qualifies:
                        issues.append(
                            Issue(
                                "error",
                                f"{location}:{json_path(path)}",
                                "confirmed conclusion lacks an original or "
                                "contemporary evidence source",
                            )
                        )
                elif status == "strong-evidence":
                    qualifies = any(
                        source.get("usage") == "evidence"
                        and source.get("evidence_class")
                        in NON_TREE_EVIDENCE_CLASSES
                        for source in cited
                    )
                    if not qualifies:
                        issues.append(
                            Issue(
                                "error",
                                f"{location}:{json_path(path)}",
                                "strong-evidence conclusion is supported only by "
                                "lead or recollection sources",
                            )
                        )


def date_interval(value: Any) -> DateInterval | None:
    if not isinstance(value, dict):
        return None
    kind = value.get("kind")
    try:
        if kind == "exact" and isinstance(value.get("value"), str):
            parsed = date.fromisoformat(value["value"])
            return DateInterval(parsed, parsed)
        if kind == "month":
            year = value.get("year")
            month = value.get("month")
            if isinstance(year, int) and isinstance(month, int):
                last_day = calendar.monthrange(year, month)[1]
                return DateInterval(date(year, month, 1), date(year, month, last_day))
        if kind == "year" and isinstance(value.get("year"), int):
            year = value["year"]
            return DateInterval(date(year, 1, 1), date(year, 12, 31))
        earliest = value.get("earliest")
        latest = value.get("latest")
        if isinstance(earliest, int) and isinstance(latest, int) and earliest <= latest:
            return DateInterval(date(earliest, 1, 1), date(latest, 12, 31))
    except (ValueError, OverflowError):
        return None
    return None


def iter_date_objects(
    value: Any, path: tuple[Any, ...] = ()
) -> Iterator[tuple[dict[str, Any], tuple[Any, ...]]]:
    if isinstance(value, dict):
        if "kind" in value and (
            "value" in value
            or "year" in value
            or "text" in value
            or "earliest" in value
        ):
            yield value, path
        for key, child in value.items():
            yield from iter_date_objects(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_date_objects(child, path + (index,))


def validate_date_ranges(
    root: Path,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    for kind_entities in entities.values():
        for entity in kind_entities.values():
            location = display_path(entity.path, root)
            for value, path in iter_date_objects(entity.data):
                if value.get("kind") == "exact" and isinstance(
                    value.get("value"), str
                ):
                    try:
                        date.fromisoformat(value["value"])
                    except ValueError:
                        issues.append(
                            Issue(
                                "error",
                                f"{location}:{json_path(path)}",
                                f"invalid exact calendar date {value['value']!r}",
                            )
                        )
                earliest = value.get("earliest")
                latest = value.get("latest")
                if (
                    isinstance(earliest, int)
                    and isinstance(latest, int)
                    and earliest > latest
                ):
                    issues.append(
                        Issue(
                            "error",
                            f"{location}:{json_path(path)}",
                            "earliest year is later than latest year",
                        )
                    )


def merge_intervals(intervals: Iterable[DateInterval]) -> DateInterval | None:
    values = list(intervals)
    if not values:
        return None
    return DateInterval(
        min(interval.earliest for interval in values),
        max(interval.latest for interval in values),
    )


def vital_intervals(
    entities: Mapping[str, Mapping[str, LoadedEntity]],
) -> tuple[dict[str, DateInterval], dict[str, DateInterval]]:
    births: dict[str, list[DateInterval]] = defaultdict(list)
    deaths: dict[str, list[DateInterval]] = defaultdict(list)
    for event in entities["events"].values():
        data = event.data
        if data.get("status") not in {"confirmed", "strong-evidence"}:
            continue
        event_type = data.get("event_type")
        if event_type not in {"birth", "death"}:
            continue
        interval = date_interval(data.get("date"))
        if interval is None:
            continue
        principals = [
            participant.get("person_id")
            for participant in data.get("participants", [])
            if isinstance(participant, dict)
            and participant.get("role") == "principal"
            and isinstance(participant.get("person_id"), str)
        ]
        if len(principals) != 1:
            continue
        target = births if event_type == "birth" else deaths
        target[principals[0]].append(interval)
    return (
        {
            person_id: interval
            for person_id, values in births.items()
            if (interval := merge_intervals(values)) is not None
        },
        {
            person_id: interval
            for person_id, values in deaths.items()
            if (interval := merge_intervals(values)) is not None
        },
    )


def validate_event_principals(
    root: Path,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    for event in entities["events"].values():
        if event.data.get("event_type") not in {"birth", "death"}:
            continue
        principals = [
            participant
            for participant in event.data.get("participants", [])
            if isinstance(participant, dict) and participant.get("role") == "principal"
        ]
        if len(principals) != 1:
            issues.append(
                Issue(
                    "error",
                    f"{display_path(event.path, root)}:$.participants",
                    "birth and death events require exactly one principal",
                )
            )


def validate_family_structure_and_chronology(
    root: Path,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    births, deaths = vital_intervals(entities)

    for family in entities["families"].values():
        location = display_path(family.path, root)
        partners = [
            partner.get("person_id")
            for partner in family.data.get("partners", [])
            if isinstance(partner, dict) and isinstance(partner.get("person_id"), str)
        ]
        partner_set = set(partners)
        if len(partners) != len(partner_set):
            issues.append(
                Issue("error", f"{location}:$.partners", "partner IDs must be distinct")
            )
        if len(partners) == 1 and "partner_relationship" in family.data:
            issues.append(
                Issue(
                    "error",
                    f"{location}:$.partner_relationship",
                    "a partner relationship requires two partners",
                )
            )

        for index, child in enumerate(family.data.get("children", [])):
            if not isinstance(child, dict):
                continue
            child_id = child.get("person_id")
            parent_ids = child.get("parent_ids", [])
            child_location = f"{location}:$.children[{index}]"
            if isinstance(parent_ids, list):
                missing_partners = [
                    identifier
                    for identifier in parent_ids
                    if isinstance(identifier, str) and identifier not in partner_set
                ]
                if missing_partners:
                    issues.append(
                        Issue(
                            "error",
                            f"{child_location}.parent_ids",
                            "parent IDs must also appear in the family's partners: "
                            + ", ".join(missing_partners),
                        )
                    )
            if isinstance(child_id, str) and child_id in partner_set:
                issues.append(
                    Issue(
                        "error",
                        f"{child_location}.person_id",
                        "a person cannot be both a partner and child in one family",
                    )
                )
            if child.get("status") == "rejected" or not isinstance(child_id, str):
                continue
            child_birth = births.get(child_id)
            if child_birth is None:
                continue
            for parent_id in parent_ids if isinstance(parent_ids, list) else []:
                if not isinstance(parent_id, str):
                    continue
                parent_birth = births.get(parent_id)
                if parent_birth is not None:
                    if parent_birth.earliest >= child_birth.latest:
                        issues.append(
                            Issue(
                                "error",
                                child_location,
                                f"parent {parent_id} is born on or after child "
                                f"{child_id}",
                            )
                        )
                    elif (
                        child_birth.latest - parent_birth.earliest
                        < MINIMUM_PARENT_AGE
                    ):
                        issues.append(
                            Issue(
                                "error",
                                child_location,
                                f"parent {parent_id} is necessarily under eight "
                                f"years old at child {child_id}'s birth",
                            )
                        )
                parent_death = deaths.get(parent_id)
                if (
                    parent_death is not None
                    and parent_death.latest + POSTHUMOUS_BIRTH_ALLOWANCE
                    < child_birth.earliest
                ):
                    issues.append(
                        Issue(
                            "error",
                            child_location,
                            f"parent {parent_id} dies more than 310 days before "
                            f"child {child_id}'s earliest possible birth",
                        )
                    )


def normalise_name(value: str) -> str:
    normalised = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(normalised.split())


def validate_duplicate_identities(
    root: Path,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    births, _ = vital_intervals(entities)
    by_name: dict[str, list[LoadedEntity]] = defaultdict(list)
    for person in entities["people"].values():
        preferred_name = person.data.get("preferred_name")
        if isinstance(preferred_name, str) and preferred_name.strip():
            by_name[normalise_name(preferred_name)].append(person)

    for people in by_name.values():
        if len(people) < 2:
            continue
        for index, first in enumerate(people):
            for second in people[index + 1 :]:
                first_id = first.identifier
                second_id = second.identifier
                if first_id is None or second_id is None:
                    continue
                first_birth = births.get(first_id)
                second_birth = births.get(second_id)
                if first_birth is not None and second_birth is not None:
                    overlaps = not (
                        first_birth.latest < second_birth.earliest
                        or second_birth.latest < first_birth.earliest
                    )
                    if not overlaps:
                        continue
                    detail = " and overlapping birth dates"
                else:
                    detail = ""
                issues.append(
                    Issue(
                        "warning",
                        display_path(second.path, root),
                        f"possible duplicate identity: {first_id} and {second_id} "
                        f"share a normalised preferred name{detail}",
                    )
                )


def source_ids_used_by_person(
    person_id: str,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
) -> set[str]:
    source_ids: set[str] = set()
    person = entities["people"].get(person_id)
    if person is not None:
        source_ids.update(
            identifier
            for kind, identifier, _ in iter_references(person.data)
            if kind == "sources"
        )
    for event in entities["events"].values():
        participants = event.data.get("participants", [])
        if any(
            isinstance(participant, dict)
            and participant.get("person_id") == person_id
            for participant in participants
        ):
            source_ids.update(
                identifier
                for identifier in event.data.get("source_ids", [])
                if isinstance(identifier, str)
            )
    for family in entities["families"].values():
        partners = family.data.get("partners", [])
        if any(
            isinstance(partner, dict) and partner.get("person_id") == person_id
            for partner in partners
        ):
            relationship = family.data.get("partner_relationship", {})
            if isinstance(relationship, dict):
                source_ids.update(
                    identifier
                    for identifier in relationship.get("source_ids", [])
                    if isinstance(identifier, str)
                )
        for child in family.data.get("children", []):
            if not isinstance(child, dict):
                continue
            if child.get("person_id") == person_id or person_id in child.get(
                "parent_ids", []
            ):
                source_ids.update(
                    identifier
                    for identifier in child.get("source_ids", [])
                    if isinstance(identifier, str)
                )
    for source_id, source in entities["sources"].items():
        if person_id in source.data.get("linked_people", []):
            source_ids.add(source_id)
    return source_ids


def validate_privacy(
    root: Path,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    for person_id, person in entities["people"].items():
        if person.data.get("privacy") != "living":
            continue
        for source_id in source_ids_used_by_person(person_id, entities):
            source = entities["sources"].get(source_id)
            if source is not None and source.data.get("private") is not True:
                issues.append(
                    Issue(
                        "error",
                        f"{display_path(source.path, root)}:$.private",
                        f"source concerning living person {person_id} must be private",
                    )
                )


def validate_evidence_files(
    root: Path,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    for source in entities["sources"].values():
        digital_file = source.data.get("digital_file")
        if not isinstance(digital_file, dict):
            continue
        relative_path = digital_file.get("path")
        expected_hash = digital_file.get("sha256")
        if not isinstance(relative_path, str) or not isinstance(expected_hash, str):
            continue
        location = display_path(source.path, root)
        candidate = (root / relative_path).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            issues.append(
                Issue(
                    "error",
                    f"{location}:$.digital_file.path",
                    "evidence path escapes the repository",
                )
            )
            continue
        if not candidate.is_file():
            issues.append(
                Issue(
                    "error",
                    f"{location}:$.digital_file.path",
                    f"evidence file does not exist: {relative_path}",
                )
            )
            continue
        if sha256_file(candidate) != expected_hash:
            issues.append(
                Issue(
                    "error",
                    f"{location}:$.digital_file.sha256",
                    f"checksum does not match {relative_path}",
                )
            )


def validate_place_hierarchy(
    root: Path,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    parents = {
        place_id: place.data.get("parent_place_id")
        for place_id, place in entities["places"].items()
        if isinstance(place.data.get("parent_place_id"), str)
    }
    reported: set[tuple[str, ...]] = set()
    for start in parents:
        seen: list[str] = []
        current = start
        while current in parents:
            if current in seen:
                cycle = tuple(seen[seen.index(current) :] + [current])
                canonical = tuple(sorted(set(cycle)))
                if canonical not in reported:
                    reported.add(canonical)
                    path = entities["places"][start].path
                    issues.append(
                        Issue(
                            "error",
                            f"{display_path(path, root)}:$.parent_place_id",
                            "place hierarchy contains a cycle: "
                            + " -> ".join(cycle),
                        )
                    )
                break
            seen.append(current)
            current = parents[current]


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
