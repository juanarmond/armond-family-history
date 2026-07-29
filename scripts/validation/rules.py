"""Cross-entity genealogy, evidence, chronology and privacy rules."""

from __future__ import annotations

import calendar
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping

from .model import Issue, LoadedEntity, display_path, json_path, sha256_file
from .references import iter_references


PRIMARY_INFORMATION_QUALITIES = {"primary", "mixed"}
ASSERTIVE_EVIDENCE_TYPES = {"direct", "indirect"}
LEAD_ONLY_CATEGORIES = {"collaborative_tree"}
WEAK_STANDALONE_CATEGORIES = {"collaborative_tree", "family_recollection"}
# An original record, or a certified copy that faithfully reproduces an
# official record, may support a confirmed conclusion. Authored narratives
# (family recollection, published genealogies) never can.
CONFIRMING_SOURCE_FORMS = {"original", "derivative"}
POSTHUMOUS_BIRTH_ALLOWANCE = timedelta(days=310)
MINIMUM_PARENT_AGE = timedelta(days=8 * 365)


@dataclass(frozen=True)
class DateInterval:
    earliest: date
    latest: date


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
            source.get("record_category") in LEAD_ONLY_CATEGORIES
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
                    # An original record or a certified copy of an official
                    # record may confirm; the primary-information and direct
                    # evidence gates, plus the weak-category exclusion, keep
                    # family recollection and collaborative trees from ever
                    # confirming a conclusion.
                    direct_primary = any(
                        source.get("usage") == "evidence"
                        and source.get("source_form") in CONFIRMING_SOURCE_FORMS
                        and source.get("record_category")
                        not in WEAK_STANDALONE_CATEGORIES
                        and source.get("information_quality")
                        in PRIMARY_INFORMATION_QUALITIES
                        and source.get("evidence_type") == "direct"
                        for source in cited
                    )
                    indirect_primaries = {
                        source_id
                        for source_id in source_ids
                        if source_id in source_data
                        and source_data[source_id].get("usage") == "evidence"
                        and source_data[source_id].get("source_form")
                        in CONFIRMING_SOURCE_FORMS
                        and source_data[source_id].get("record_category")
                        not in WEAK_STANDALONE_CATEGORIES
                        and source_data[source_id].get("information_quality")
                        in PRIMARY_INFORMATION_QUALITIES
                        and source_data[source_id].get("evidence_type") == "indirect"
                    }
                    if not direct_primary and len(indirect_primaries) < 2:
                        issues.append(
                            Issue(
                                "error",
                                f"{location}:{json_path(path)}",
                                "confirmed conclusion requires direct primary "
                                "information from an original or certified "
                                "official record, or at least two such records "
                                "providing indirect primary information",
                            )
                        )
                elif status == "strong-evidence":
                    qualifies = any(
                        source.get("usage") == "evidence"
                        and source.get("record_category")
                        not in WEAK_STANDALONE_CATEGORIES
                        and source.get("evidence_type")
                        in ASSERTIVE_EVIDENCE_TYPES
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
            parent_relationships = child.get("parent_relationships", [])
            child_location = f"{location}:$.children[{index}]"
            parent_ids = (
                [
                    relationship.get("parent_id")
                    for relationship in parent_relationships
                    if isinstance(relationship, dict)
                    and isinstance(relationship.get("parent_id"), str)
                ]
                if isinstance(parent_relationships, list)
                else []
            )
            if len(parent_ids) != len(set(parent_ids)):
                issues.append(
                    Issue(
                        "error",
                        f"{child_location}.parent_relationships",
                        "parent IDs must be distinct for each child",
                    )
                )
            missing_partners = [
                identifier
                for identifier in parent_ids
                if identifier not in partner_set
            ]
            if missing_partners:
                issues.append(
                    Issue(
                        "error",
                        f"{child_location}.parent_relationships",
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
            if not isinstance(child_id, str):
                continue
            child_birth = births.get(child_id)
            if child_birth is None:
                continue
            for relationship in (
                parent_relationships
                if isinstance(parent_relationships, list)
                else []
            ):
                if (
                    not isinstance(relationship, dict)
                    or relationship.get("status") == "rejected"
                    or relationship.get("relationship_type") != "biological"
                ):
                    continue
                parent_id = relationship.get("parent_id")
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
            is_child = child.get("person_id") == person_id
            for relationship in child.get("parent_relationships", []):
                if not isinstance(relationship, dict):
                    continue
                if is_child or relationship.get("parent_id") == person_id:
                    source_ids.update(
                        identifier
                        for identifier in relationship.get("source_ids", [])
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
    checked = list(entities["sources"].values()) + list(entities["fan"].values())
    for source in checked:
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
