#!/usr/bin/env python3
"""Export the canonical YAML data model to a GEDCOM file (7.0 or 5.5.1).

Text-only by design. The export carries people, families, events, and source
*citations* — never the scans behind them. It deliberately emits no ``OBJE``
multimedia records, no source ``transcription`` text, no ``digital_file`` /
``repository_path`` values, and no ``evidence/`` paths (all optional in GEDCOM,
so omitting them is standards-compliant). See ``docs/gedcom-export-design.md``.

Version (``--gedcom-version``): ``7.0`` (default, the current FamilySearch
standard) or ``5.5.1`` (for the widest commercial-site import support).

Living people (``privacy: living`` or ``unknown``) are controlled by ``--living``:
``full`` (default) exports everything; ``redact`` emits a minimal "Living" node
with family links only; ``omit`` drops them entirely. A ``redact``/``omit`` file is
the one safe to share; the ``full`` file is a private local backup.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__:
    from .validation.identifiers import ENTITY_CONFIGS, SOURCE_KINDS
    from .validation.model import load_yaml
else:  # pragma: no cover - exercised only when run as a script
    from validation.identifiers import ENTITY_CONFIGS, SOURCE_KINDS
    from validation.model import load_yaml

MONTHS = ["", "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

QUAY = {"confirmed": "3", "strong-evidence": "2", "hypothesis": "1"}
SEX_TAG = {"male": "M", "female": "F", "unknown": "U"}

# INDI-level event tag per event_type. `marriage` is emitted on the FAM instead.
INDI_EVENT_TAGS = {
    "birth": "BIRT",
    "baptism": "BAPM",
    "death": "DEAT",
    "burial": "BURI",
    "residence": "RESI",
    "immigration": "IMMI",
    "naturalisation": "NATU",
    "occupation": "OCCU",
    "probate": "PROB",
    "other": "EVEN",
}

SUPPORTED_VERSIONS = ("7.0", "5.5.1")
# 5.5.1 lines must stay within 255 octets; 7.0 removed CONC and the length cap.
LINE_WRAP = 200
_YEAR = re.compile(r"\b(\d{4})\b")


def xref(entity_id: str) -> str:
    """Turn a repository ID (``CIV-0022``) into a GEDCOM xref (``CIV0022``)."""
    return entity_id.replace("-", "")


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def _year_in(text: Any) -> str | None:
    match = _YEAR.search(str(text or ""))
    return match.group(1) if match else None


def format_date(date_obj: Any) -> tuple[str | None, str | None]:
    """Map a `common.date` object to (GEDCOM DATE value, phrase).

    The value is None when the date cannot be expressed as a machine date; the
    phrase carries the human wording for fuzzy kinds (approximate/before/after/
    inferred/range) so 7.0 can attach it via a DATE ``PHRASE`` substructure.
    """
    if not isinstance(date_obj, dict):
        return None, None
    kind = date_obj.get("kind")
    if kind == "exact":
        match = re.match(r"(\d{4})-(\d{2})-(\d{2})$", str(date_obj.get("value", "")))
        if not match:
            return None, None
        year, month, day = match.group(1), int(match.group(2)), int(match.group(3))
        return f"{day:02d} {MONTHS[month]} {year}", None
    if kind == "month":
        return f"{MONTHS[int(date_obj['month'])]} {int(date_obj['year'])}", None
    if kind == "year":
        return f"{int(date_obj['year'])}", None
    if kind == "range":
        return f"BET {date_obj['earliest']} AND {date_obj['latest']}", date_obj.get("text")
    if kind == "approximate":
        year = date_obj.get("earliest") or _year_in(date_obj.get("text"))
        return (f"ABT {year}" if year else None), date_obj.get("text")
    if kind == "before":
        year = date_obj.get("latest") or _year_in(date_obj.get("text"))
        return (f"BEF {year}" if year else None), date_obj.get("text")
    if kind == "after":
        year = date_obj.get("earliest") or _year_in(date_obj.get("text"))
        return (f"AFT {year}" if year else None), date_obj.get("text")
    if kind == "inferred":
        year = _year_in(date_obj.get("text"))
        return (f"EST {year}" if year else None), date_obj.get("text")
    # `conflicting` / `unknown`: no machine date.
    return None, date_obj.get("text")


def format_name(full_name: str) -> tuple[str, str, str]:
    """Return (GEDCOM NAME value, given, surname). Surname = last token."""
    cleaned = _clean(full_name)
    tokens = cleaned.split(" ")
    if len(tokens) == 1:
        return f"{cleaned} //", cleaned, ""
    given, surname = " ".join(tokens[:-1]), tokens[-1]
    return f"{given} /{surname}/", given, surname


def load_entities(data_root: Path) -> dict[str, dict[str, dict]]:
    entities: dict[str, dict[str, dict]] = {}
    for kind, config in ENTITY_CONFIGS.items():
        directory = data_root / config.directory
        store: dict[str, dict] = {}
        if directory.exists():
            for path in sorted(directory.glob("*.yaml")):
                data = load_yaml(path)
                if isinstance(data, dict) and isinstance(data.get("id"), str):
                    store[data["id"]] = data
        entities[kind] = store
    return entities


class GedcomBuilder:
    def __init__(
        self,
        data_root: Path,
        *,
        version: str = "7.0",
        living: str = "full",
        include_hypotheses: bool = True,
        include_notes: bool = True,
    ) -> None:
        if version not in SUPPORTED_VERSIONS:
            raise ValueError(f"unsupported GEDCOM version: {version!r}")
        entities = load_entities(data_root)
        self.people = entities["people"]
        self.families = entities["families"]
        self.events = entities["events"]
        self.places = entities["places"]
        self.sources: dict[str, dict] = {}
        for kind in SOURCE_KINDS:
            self.sources.update(entities[kind])
        self.version = version
        self.living = living
        self.include_hypotheses = include_hypotheses
        self.include_notes = include_notes
        self.used_sources: set[str] = set()
        self.lines: list[str] = []

    # -- low-level emission -------------------------------------------------
    def emit(self, level: int, tag: str, value: str | None = None) -> None:
        """Append a line. In 5.5.1 long free text wraps across CONC; 7.0 does not."""
        if value is None:
            self.lines.append(f"{level} {tag}")
            return
        text = ("@" + value) if value.startswith("@") else value  # escape leading @
        if self.version != "5.5.1":
            self.lines.append(f"{level} {tag} {text}".rstrip())
            return
        first, rest = text[:LINE_WRAP], text[LINE_WRAP:]
        self.lines.append(f"{level} {tag} {first}".rstrip())
        while rest:
            chunk, rest = rest[:LINE_WRAP], rest[LINE_WRAP:]
            self.lines.append(f"{level + 1} CONC {chunk}")

    def pointer(self, level: int, tag: str, entity_id: str) -> None:
        self.lines.append(f"{level} {tag} @{xref(entity_id)}@")

    def cite(self, level: int, source_ids: Any, status: str | None = None) -> None:
        for source_id in source_ids or []:
            if source_id not in self.sources:
                continue
            self.pointer(level, "SOUR", source_id)
            self.used_sources.add(source_id)
            if status and status in QUAY:
                self.emit(level + 1, "QUAY", QUAY[status])

    def note(self, level: int, text: Any, source_ids: Any = None) -> None:
        cleaned = _clean(text)
        if not cleaned:
            return
        self.emit(level, "NOTE", cleaned)
        self.cite(level + 1, source_ids)

    def emit_date(self, level: int, date_obj: Any) -> None:
        value, phrase = format_date(date_obj)
        phrase = _clean(phrase) if phrase else ""
        if self.version == "5.5.1":
            if value:
                self.emit(level, "DATE", value)
            elif phrase:
                self.emit(level, "DATE", f"({phrase})")
            return
        # 7.0: a machine date plus an optional PHRASE; a pure phrase → a NOTE.
        if value:
            self.emit(level, "DATE", value)
            if phrase:
                self.emit(level + 1, "PHRASE", phrase)
        elif phrase:
            self.emit(level, "NOTE", f"Date: {phrase}")

    # -- status gating ------------------------------------------------------
    def allowed(self, status: str | None) -> bool:
        if status == "rejected":
            return False
        if status == "hypothesis" and not self.include_hypotheses:
            return False
        return True

    def is_hidden(self, person_id: str) -> bool:
        """A living person hidden entirely (omit mode)."""
        person = self.people.get(person_id, {})
        return self.living == "omit" and person.get("privacy") in ("living", "unknown")

    def is_redacted(self, person: dict) -> bool:
        return self.living in ("redact", "omit") and person.get("privacy") in (
            "living",
            "unknown",
        )

    def resn_privacy(self, level: int) -> None:
        self.emit(level, "RESN", "PRIVACY" if self.version != "5.5.1" else "privacy")

    def name_type(self) -> str:
        return "AKA" if self.version != "5.5.1" else "aka"

    # -- place --------------------------------------------------------------
    def emit_place(self, level: int, place_id: Any, place_text: Any) -> None:
        name = None
        coords = None
        if place_id and place_id in self.places:
            place = self.places[place_id]
            name = place.get("preferred_name")
            coords = place.get("coordinates")
        elif place_text:
            name = place_text
        if not name:
            return
        self.emit(level, "PLAC", name)
        if isinstance(coords, dict) and "latitude" in coords and "longitude" in coords:
            lat, lon = coords["latitude"], coords["longitude"]
            self.emit(level + 1, "MAP")
            self.emit(level + 2, "LATI", f"{'N' if lat >= 0 else 'S'}{abs(lat):.6f}")
            self.emit(level + 2, "LONG", f"{'E' if lon >= 0 else 'W'}{abs(lon):.6f}")

    # -- header / trailer ---------------------------------------------------
    def emit_header(self) -> None:
        stamp = datetime.now(timezone.utc)
        version = stamp.strftime("%Y.%m.%d")
        date_line = f"{stamp.day:02d} {MONTHS[stamp.month]} {stamp.year}"
        self.emit(0, "HEAD")
        self.emit(1, "GEDC")
        self.emit(2, "VERS", self.version)
        if self.version == "5.5.1":
            self.emit(2, "FORM", "LINEAGE-LINKED")
        self.emit(1, "SOUR", "ARMOND-FAMILY-HISTORY")
        self.emit(2, "NAME", "Armond Family History")
        self.emit(2, "VERS", version)
        self.emit(1, "DATE", date_line)
        self.pointer(1, "SUBM", "SUBM-0001")
        if self.version == "5.5.1":
            self.emit(1, "CHAR", "UTF-8")
            self.emit(1, "LANG", "Portuguese")
        else:
            self.emit(1, "LANG", "pt-BR")
        self.lines.append("0 @SUBM0001@ SUBM")
        self.emit(1, "NAME", "Armond Family History")

    # -- individuals --------------------------------------------------------
    def emit_person(self, person_id: str) -> None:
        person = self.people[person_id]
        if self.is_hidden(person_id):
            return
        redacted = self.is_redacted(person)
        self.lines.append(f"0 @{xref(person_id)}@ INDI")

        if redacted:
            _, _, surname = format_name(person.get("preferred_name", ""))
            self.emit(1, "NAME", f"Living /{surname}/")
            self.emit(2, "SURN", surname)
        else:
            name_value, given, surname = format_name(person.get("preferred_name", ""))
            self.emit(1, "NAME", name_value)
            if given:
                self.emit(2, "GIVN", given)
            if surname:
                self.emit(2, "SURN", surname)
            for variant in person.get("name_variants", []):
                value = _clean(variant.get("value"))
                if not value or value == _clean(person.get("preferred_name", "")):
                    continue
                alt_value, _, _ = format_name(value)
                self.emit(1, "NAME", alt_value)
                self.emit(2, "TYPE", self.name_type())
                self.cite(2, variant.get("source_ids"))

        self.emit(1, "SEX", SEX_TAG.get(person.get("sex", "unknown"), "U"))
        if person.get("privacy") in ("living", "unknown"):
            self.resn_privacy(1)

        if not redacted:
            self.emit_person_events(person_id)
            for occupation in person.get("occupations", []):
                self.emit(1, "OCCU", occupation.get("value"))
                self.cite(2, occupation.get("source_ids"))

        self.emit_family_links(person_id)

        if not redacted and self.include_notes:
            for entry in person.get("notes", []):
                self.note(1, entry.get("text"), entry.get("source_ids"))

    def emit_person_events(self, person_id: str) -> None:
        for event_id in self.people[person_id].get("event_ids", []):
            event = self.events.get(event_id)
            if event is None:
                continue
            event_type = event.get("event_type")
            if event_type == "marriage":
                continue  # emitted on the FAM
            if not self.allowed(event.get("status")):
                continue
            role = next(
                (p.get("role") for p in event.get("participants", [])
                 if p.get("person_id") == person_id),
                None,
            )
            if role != "principal":
                continue
            tag = INDI_EVENT_TAGS.get(event_type, "EVEN")
            self.emit(1, tag)
            if tag == "EVEN":
                self.emit(2, "TYPE", event_type or "other")
            self.emit_date(2, event.get("date"))
            self.emit_place(2, event.get("place_id"), event.get("place_text"))
            self.cite(2, event.get("source_ids"), event.get("status"))
            if event.get("status") == "hypothesis":
                self.emit(2, "NOTE", "Unproven hypothesis (not yet confirmed by evidence).")

    def emit_family_links(self, person_id: str) -> None:
        for family_id in self.people[person_id].get("family_ids", []):
            family = self.families.get(family_id)
            if family is None:
                continue
            is_partner = any(
                partner.get("person_id") == person_id
                for partner in family.get("partners", [])
            )
            is_child = any(
                child.get("person_id") == person_id
                for child in family.get("children", [])
            )
            if is_partner:
                self.pointer(1, "FAMS", family_id)
            if is_child:
                self.pointer(1, "FAMC", family_id)

    def documented_child_xref(self, family_id: str, index: int) -> str:
        return f"DOC{xref(family_id)}_{index}"

    def emit_documented_children(self) -> None:
        """Synthetic minimal INDI records so attested collateral children reach
        the tree graph as real CHIL nodes (they have no repository person ID)."""
        for family_id in sorted(self.families):
            family = self.families[family_id]
            for index, documented in enumerate(family.get("documented_children", []), 1):
                child_xref = self.documented_child_xref(family_id, index)
                self.lines.append(f"0 @{child_xref}@ INDI")
                name_value, given, surname = format_name(documented.get("name", ""))
                self.emit(1, "NAME", name_value)
                if given:
                    self.emit(2, "GIVN", given)
                if surname:
                    self.emit(2, "SURN", surname)
                self.emit(1, "SEX", "U")
                self.pointer(1, "FAMC", family_id)
                marker = "Documented child, not individually modelled."
                lifespan = _clean(documented.get("lifespan"))
                if lifespan:
                    marker = f"{marker} Reported lifespan: {lifespan}."
                self.note(1, marker, documented.get("source_ids"))
                extra = _clean(documented.get("note"))
                if self.include_notes and extra:
                    self.note(1, extra)

    # -- families -----------------------------------------------------------
    def emit_family(self, family_id: str) -> None:
        family = self.families[family_id]
        self.lines.append(f"0 @{xref(family_id)}@ FAM")

        partners = [
            p for p in family.get("partners", [])
            if not self.is_hidden(p.get("person_id", ""))
        ]
        males = [p for p in partners
                 if self.people.get(p.get("person_id"), {}).get("sex") == "male"]
        females = [p for p in partners
                   if self.people.get(p.get("person_id"), {}).get("sex") == "female"]
        husband = males[0] if males else (partners[0] if partners else None)
        wife = females[0] if females else (
            next((p for p in partners if p is not husband), None)
        )
        if husband:
            self.pointer(1, "HUSB", husband["person_id"])
        if wife and wife is not husband:
            self.pointer(1, "WIFE", wife["person_id"])

        for child in family.get("children", []):
            child_id = child.get("person_id")
            if child_id and not self.is_hidden(child_id):
                self.pointer(1, "CHIL", child_id)
        for index, _documented in enumerate(family.get("documented_children", []), 1):
            self.lines.append(
                f"1 CHIL @{self.documented_child_xref(family_id, index)}@"
            )

        self.emit_marriage(family)

        for source_id in self.collect_parentage_sources(family):
            self.pointer(1, "SOUR", source_id)
            self.used_sources.add(source_id)

        if self.include_notes:
            for entry in family.get("notes", []):
                self.note(1, entry.get("text"), entry.get("source_ids"))

    def emit_marriage(self, family: dict) -> None:
        marriage_event = None
        for event_id in family.get("event_ids", []):
            event = self.events.get(event_id)
            if event and event.get("event_type") == "marriage" and self.allowed(
                event.get("status")
            ):
                marriage_event = event
                break

        relationship = family.get("partner_relationship")
        if marriage_event is not None:
            self.emit(1, "MARR")
            self.emit_date(2, marriage_event.get("date"))
            self.emit_place(
                2, marriage_event.get("place_id"), marriage_event.get("place_text")
            )
            self.cite(2, marriage_event.get("source_ids"), marriage_event.get("status"))
            if marriage_event.get("status") == "hypothesis":
                self.emit(2, "NOTE", "Unproven hypothesis (not yet confirmed by evidence).")
        elif isinstance(relationship, dict) and self.allowed(relationship.get("status")):
            self.emit(1, "MARR")
            self.cite(2, relationship.get("source_ids"), relationship.get("status"))
            if relationship.get("status") == "hypothesis":
                self.emit(2, "NOTE", "Unproven hypothesis (not yet confirmed by evidence).")

    def collect_parentage_sources(self, family: dict) -> list[str]:
        collected: list[str] = []
        seen: set[str] = set()
        for child in family.get("children", []):
            for relationship in child.get("parent_relationships", []):
                if not self.allowed(relationship.get("status")):
                    continue
                for source_id in relationship.get("source_ids", []):
                    if source_id in self.sources and source_id not in seen:
                        seen.add(source_id)
                        collected.append(source_id)
        return collected

    # -- sources ------------------------------------------------------------
    def emit_sources(self) -> None:
        repositories: dict[str, str] = {}
        for source_id in sorted(self.used_sources):
            source = self.sources[source_id]
            name = _clean((source.get("repository") or {}).get("name"))
            if name and name not in repositories:
                repositories[name] = f"REPO-{len(repositories) + 1:04d}"

        for name, repo_id in repositories.items():
            self.lines.append(f"0 @{xref(repo_id)}@ REPO")
            self.emit(1, "NAME", name)

        for source_id in sorted(self.used_sources):
            source = self.sources[source_id]
            self.lines.append(f"0 @{xref(source_id)}@ SOUR")
            self.emit(1, "TITL", source.get("title"))
            abstract = _clean(source.get("abstract"))
            if abstract:
                self.emit(1, "TEXT", abstract)
            repository = source.get("repository") or {}
            name = _clean(repository.get("name"))
            if name:
                self.pointer(1, "REPO", repositories[name])
                call_number = self.archival_reference(repository)
                if call_number:
                    self.emit(2, "CALN", call_number)
            classification = "; ".join(
                part for part in (
                    source.get("record_category"),
                    source.get("source_form"),
                    f"information {source.get('information_quality')}"
                    if source.get("information_quality") else None,
                    f"{source.get('evidence_type')} evidence"
                    if source.get("evidence_type") else None,
                ) if part
            )
            if classification:
                self.emit(1, "NOTE", f"Evidence classification: {classification}.")

    @staticmethod
    def archival_reference(repository: dict) -> str:
        parts: list[str] = []
        if repository.get("collection"):
            parts.append(_clean(repository["collection"]))
        if repository.get("series"):
            parts.append(_clean(repository["series"]))
        if repository.get("book"):
            parts.append(f"livro {_clean(repository['book'])}")
        if repository.get("volume"):
            parts.append(f"vol. {_clean(repository['volume'])}")
        if repository.get("page"):
            parts.append(f"fl. {_clean(repository['page'])}")
        if repository.get("record_number"):
            parts.append(f"nº {_clean(repository['record_number'])}")
        return ", ".join(parts)

    # -- driver -------------------------------------------------------------
    def build(self) -> str:
        self.emit_header()
        for person_id in sorted(self.people):
            self.emit_person(person_id)
        self.emit_documented_children()
        for family_id in sorted(self.families):
            self.emit_family(family_id)
        self.emit_sources()
        self.emit(0, "TRLR")
        return "\n".join(self.lines) + "\n"


def build_gedcom(
    data_root: Path,
    *,
    version: str = "7.0",
    living: str = "full",
    include_hypotheses: bool = True,
    include_notes: bool = True,
) -> str:
    return GedcomBuilder(
        data_root,
        version=version,
        living=living,
        include_hypotheses=include_hypotheses,
        include_notes=include_notes,
    ).build()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument(
        "--output", type=Path, default=Path("export/armond-family-history.ged")
    )
    parser.add_argument(
        "--gedcom-version", choices=SUPPORTED_VERSIONS, default="7.0",
        help="GEDCOM version to emit (default: 7.0)",
    )
    parser.add_argument(
        "--living", choices=("full", "redact", "omit"), default="full",
        help="how to treat living people (default: full — a private local backup)",
    )
    parser.add_argument(
        "--exclude-hypotheses", action="store_true",
        help="omit hypothesis-level edges instead of flagging them",
    )
    parser.add_argument("--no-notes", action="store_true", help="omit NOTE text")
    args = parser.parse_args(argv)

    text = build_gedcom(
        args.data_root,
        version=args.gedcom_version,
        living=args.living,
        include_hypotheses=not args.exclude_hypotheses,
        include_notes=not args.no_notes,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(f"Wrote {args.output} (GEDCOM {args.gedcom_version}, "
          f"{len(text.splitlines())} lines).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
