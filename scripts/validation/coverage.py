"""Validation for the direct-ancestor missing-record coverage ledger."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator

from .model import Issue, LoadedEntity, display_path, json_path, load_yaml


RECORD_COVERAGE_SCHEMA = "record-coverage.schema.json"


def validate_record_coverage(
    root: Path,
    validator: Draft202012Validator | None,
    entities: Mapping[str, Mapping[str, LoadedEntity]],
    issues: list[Issue],
) -> None:
    path = root / "research" / "record-coverage.yaml"
    location = display_path(path, root)
    try:
        coverage = load_yaml(path)
    except FileNotFoundError:
        issues.append(Issue("error", location, "record coverage ledger is missing"))
        return
    except (OSError, yaml.YAMLError) as exc:
        issues.append(Issue("error", location, f"invalid YAML: {exc}"))
        return

    if not isinstance(coverage, dict):
        issues.append(
            Issue("error", location, "record coverage must be a YAML mapping")
        )
        return

    if validator is not None:
        schema_errors = sorted(
            validator.iter_errors(coverage),
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

    people = coverage.get("people")
    if not isinstance(people, list):
        return

    seen_people: set[str] = set()
    for person_index, person_coverage in enumerate(people):
        if not isinstance(person_coverage, dict):
            continue
        person_location = f"{location}:$.people[{person_index}]"
        person_id = person_coverage.get("person_id")
        if not isinstance(person_id, str):
            continue
        if person_id in seen_people:
            issues.append(
                Issue(
                    "error",
                    f"{person_location}.person_id",
                    f"record coverage repeats person {person_id}",
                )
            )
        seen_people.add(person_id)

        person = entities["people"].get(person_id)
        if person is None:
            issues.append(
                Issue(
                    "error",
                    f"{person_location}.person_id",
                    f"record coverage person {person_id} does not resolve",
                )
            )
        elif person.data.get("privacy") == "living":
            issues.append(
                Issue(
                    "error",
                    f"{person_location}.person_id",
                    f"living person {person_id} must not appear in this ledger",
                )
            )

        seen_record_types: set[str] = set()
        records = person_coverage.get("records")
        if not isinstance(records, list):
            continue
        for record_index, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            record_location = f"{person_location}.records[{record_index}]"
            record_type = record.get("record_type")
            if isinstance(record_type, str):
                if record_type in seen_record_types:
                    issues.append(
                        Issue(
                            "error",
                            f"{record_location}.record_type",
                            f"{person_id} repeats coverage for {record_type}",
                        )
                    )
                seen_record_types.add(record_type)

            source_ids = record.get("source_ids")
            if not isinstance(source_ids, list):
                continue
            for source_index, source_id in enumerate(source_ids):
                if not isinstance(source_id, str):
                    continue
                source = entities["sources"].get(source_id)
                source_location = (
                    f"{record_location}.source_ids[{source_index}]"
                )
                if source is None:
                    issues.append(
                        Issue(
                            "error",
                            source_location,
                            f"record coverage source {source_id} does not resolve",
                        )
                    )
                elif person_id not in source.data.get("linked_people", []):
                    issues.append(
                        Issue(
                            "error",
                            source_location,
                            f"{source_id} is not linked to coverage person {person_id}",
                        )
                    )
