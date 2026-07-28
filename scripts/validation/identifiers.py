"""Canonical entity kinds and stable identifier operations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class EntityConfig:
    directory: str
    singular: str
    prefix: str
    pattern: re.Pattern[str]
    schema_filename: str


ENTITY_CONFIGS: dict[str, EntityConfig] = {
    "people": EntityConfig(
        "people",
        "person",
        "P",
        re.compile(r"^P-(?!0000$)[0-9]{4}$"),
        "person.schema.json",
    ),
    "families": EntityConfig(
        "families",
        "family",
        "F",
        re.compile(r"^F-(?!0000$)[0-9]{4}$"),
        "family.schema.json",
    ),
    "events": EntityConfig(
        "events",
        "event",
        "E",
        re.compile(r"^E-(?!0000$)[0-9]{4}$"),
        "event.schema.json",
    ),
    "places": EntityConfig(
        "places",
        "place",
        "PL",
        re.compile(r"^PL-(?!0000$)[0-9]{4}$"),
        "place.schema.json",
    ),
    "sources": EntityConfig(
        "sources",
        "source",
        "SRC",
        re.compile(r"^SRC-(?!0000$)[0-9]{4}$"),
        "source.schema.json",
    ),
}

KINDS_BY_SINGULAR = {
    config.singular: kind for kind, config in ENTITY_CONFIGS.items()
}


def parse_identifier(identifier: str, config: EntityConfig) -> int | None:
    if not config.pattern.fullmatch(identifier):
        return None
    return int(identifier.rsplit("-", 1)[1])


def format_identifier(number: int, prefix: str) -> str:
    return f"{prefix}-{number:04d}"


def format_identifiers(numbers: Iterable[int], prefix: str) -> str:
    values = sorted(set(numbers))
    labels = [format_identifier(number, prefix) for number in values[:10]]
    if len(values) > 10:
        labels.append(f"and {len(values) - 10} more")
    return ", ".join(labels)
