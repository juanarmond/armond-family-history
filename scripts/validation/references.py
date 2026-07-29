"""Cross-entity reference discovery and resolution."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator, Mapping

from .identifiers import SOURCE_KINDS
from .model import Issue, LoadedEntity, display_path, json_path


REFERENCE_KEYS = {
    "person_id": "people",
    "parent_id": "people",
    "linked_people": "people",
    "family_ids": "families",
    "linked_families": "families",
    "event_ids": "events",
    "linked_events": "events",
    "place_id": "places",
    "parent_place_id": "places",
    "linked_places": "places",
    "source_ids": "sources",
    "fan_id": "fan",
}


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
                if target_kind == "sources":
                    resolved = any(
                        identifier in entities[kind] for kind in SOURCE_KINDS
                    )
                else:
                    resolved = identifier in entities[target_kind]
                if not resolved:
                    issues.append(
                        Issue(
                            "error",
                            f"{location}:{json_path(path)}",
                            f"reference {identifier!r} does not resolve",
                        )
                    )
