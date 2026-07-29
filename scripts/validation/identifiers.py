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
    "civil": EntityConfig(
        "sources/civil", "civil", "CIV",
        re.compile(r"^CIV-(?!0000$)[0-9]{4}$"), "source.schema.json",
    ),
    "government": EntityConfig(
        "sources/government", "government", "GOV",
        re.compile(r"^GOV-(?!0000$)[0-9]{4}$"), "source.schema.json",
    ),
    "parish": EntityConfig(
        "sources/parish", "parish", "PAR",
        re.compile(r"^PAR-(?!0000$)[0-9]{4}$"), "source.schema.json",
    ),
    "probate": EntityConfig(
        "sources/probate", "probate", "PRB",
        re.compile(r"^PRB-(?!0000$)[0-9]{4}$"), "source.schema.json",
    ),
    "newspapers": EntityConfig(
        "sources/newspapers", "newspaper", "NWS",
        re.compile(r"^NWS-(?!0000$)[0-9]{4}$"), "source.schema.json",
    ),
    "publications": EntityConfig(
        "sources/publications", "publication", "PUB",
        re.compile(r"^PUB-(?!0000$)[0-9]{4}$"), "source.schema.json",
    ),
    "family-recollection": EntityConfig(
        "sources/family-recollection", "recollection", "REC",
        re.compile(r"^REC-(?!0000$)[0-9]{4}$"), "source.schema.json",
    ),
    "fan": EntityConfig(
        "fan",
        "fan",
        "FAN",
        re.compile(r"^FAN-(?!0000$)[0-9]{4}$"),
        "fan.schema.json",
    ),
}

# Source categories are distinct entity kinds that share source.schema.json.
# A `source_ids` reference resolves against the union of these kinds. Adding a
# new source category = add one EntityConfig above (its own PREFIX and
# data/sources/<category>/ directory), a ledger section, a template, and its
# name here.
SOURCE_KINDS = (
    "civil",
    "government",
    "parish",
    "probate",
    "newspapers",
    "publications",
    "family-recollection",
)

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
