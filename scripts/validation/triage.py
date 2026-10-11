"""Validation of the public triage index (data/triage-index.yaml, plan §11.1)."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from .identifiers import SOURCE_KINDS
from .model import Issue, LoadedEntity, display_path, json_path, load_yaml

TRIAGE_INDEX_SCHEMA = "triage-index.schema.json"
HELD_DISPOSITIONS = {"promoted", "fan", "duplicate"}


def held_hashes(
    root: Path, entities: Mapping[str, Mapping[str, LoadedEntity]]
) -> dict[str, set[str]]:
    """SHA-256 → the IDs whose evidence (or inventory entry) holds that file."""
    held: dict[str, set[str]] = defaultdict(set)
    kinds = [*SOURCE_KINDS, "fan"]
    for kind in kinds:
        for entity_id, entity in entities.get(kind, {}).items():
            data = entity.data
            for ref in [data.get("digital_file"), *(data.get("additional_pages") or [])]:
                if isinstance(ref, dict) and isinstance(ref.get("sha256"), str):
                    held[ref["sha256"]].add(entity_id)
    inventory_path = root / "data" / "document-inventory.yaml"
    if inventory_path.is_file():
        inventory = load_yaml(inventory_path) or {}
        for document in inventory.get("documents") or []:
            if not isinstance(document, dict):
                continue
            owner = document.get("proposed_source_id") or document.get("inventory_id")
            for record_file in document.get("files") or []:
                if isinstance(record_file, dict) and isinstance(record_file.get("sha256"), str):
                    held[record_file["sha256"]].add(str(owner))
    return held


def validate_triage_index(
    root: Path,
    validator: Draft202012Validator | None,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    path = root / "data" / "triage-index.yaml"
    if not path.is_file():
        return
    location = display_path(path, root)
    try:
        document = load_yaml(path)
    except Exception as exc:  # noqa: BLE001 — reported as a validation error
        issues.append(Issue("error", location, f"invalid YAML: {exc}"))
        return
    if validator is not None:
        for error in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path)):
            issues.append(Issue("error", f"{location}:{json_path(error.absolute_path)}", error.message))
        if not validator.is_valid(document):
            return

    known_ids = {entity_id for kind in [*SOURCE_KINDS, "fan"] for entity_id in entities.get(kind, {})}
    inventory_path = root / "data" / "document-inventory.yaml"
    if inventory_path.is_file():
        inventory = load_yaml(inventory_path) or {}
        known_ids |= {d.get("inventory_id") for d in inventory.get("documents") or [] if isinstance(d, dict)}
    held = held_hashes(root, entities)

    seen: dict[str, int] = {}
    for index, entry in enumerate(document.get("entries") or []):
        entry_location = f"{location}:$.entries[{index}]"
        digest = entry["sha256"]
        if digest in seen:
            issues.append(Issue("error", entry_location, f"duplicate sha256 (also entry {seen[digest]})"))
            continue
        seen[digest] = index
        for target in entry["target_ids"]:
            if target not in known_ids:
                issues.append(Issue("error", f"{entry_location}.target_ids", f"target {target} does not exist"))
        disposition = entry["disposition"]
        if disposition == "promoted":
            if digest not in held:
                issues.append(
                    Issue("error", entry_location, "promoted, but no source, FAN or inventory file holds this SHA-256")
                )
            if not entry["target_ids"]:
                issues.append(Issue("error", f"{entry_location}.target_ids", "a promoted file must name its targets"))
        elif digest in held and disposition not in HELD_DISPOSITIONS:
            holders = ", ".join(sorted(held[digest]))
            issues.append(
                Issue(
                    "error",
                    f"{entry_location}.disposition",
                    f"{disposition}, but the file is held as evidence by {holders}",
                )
            )
