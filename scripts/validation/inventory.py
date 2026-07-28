"""Validation for the privacy-aware incoming-document inventory."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator

from .model import (
    Issue,
    LoadedEntity,
    display_path,
    json_path,
    load_yaml,
    sha256_file,
)


DOCUMENT_INVENTORY_SCHEMA = "document-inventory.schema.json"


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
        inventory_file_keys: set[tuple[str, str]] = set()
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
            if isinstance(relative_path, str) and isinstance(expected_hash, str):
                inventory_file_keys.add((relative_path, expected_hash))

        if (
            document.get("status") == "catalogued"
            and isinstance(proposed_source_id, str)
            and proposed_source_id in entities["sources"]
        ):
            source = entities["sources"][proposed_source_id].data
            digital_file = source.get("digital_file")
            if not isinstance(digital_file, dict):
                issues.append(
                    Issue(
                        "error",
                        f"{document_location}.proposed_source_id",
                        f"catalogued source {proposed_source_id} must retain a "
                        "digital_file matching the inventory",
                    )
                )
            else:
                source_file_key = (
                    digital_file.get("path"),
                    digital_file.get("sha256"),
                )
                if source_file_key not in inventory_file_keys:
                    issues.append(
                        Issue(
                            "error",
                            f"{document_location}.files",
                            f"no inventoried path and checksum match "
                            f"{proposed_source_id}.digital_file",
                        )
                    )

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
