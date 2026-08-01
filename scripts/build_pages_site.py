"""Build the privacy-filtered static site for GitHub Pages.

Design goal: stay in step with the viewer automatically. Rather than hardcoding
which viewer files to copy or which person fields to publish (both of which drift
as the viewer grows), this script:

* copies the entire ``family-tree-viewer/`` directory (so every JS module, incl.
  ``i18n.js`` and any future file, plus ``vendor/``, ships automatically); and
* publishes deceased people *verbatim* (so new person fields such as
  ``nationality``/``sex``/``occupations`` appear without edits here), while
  reducing only the entity kinds that carry private evidence text.

Privacy model (the site is public; the repository is private):

* people    – deceased verbatim; living reduced to a private stub (structural
              family links only, name and all attributes withheld).
* events    – dropped when any participant is living; otherwise verbatim.
* families  – verbatim (structural; no evidence transcriptions).
* places    – verbatim.
* sources   – reduced: display metadata only. Transcriptions, abstracts,
              repository details and scan/file references are never published.
* fan       – reduced the same way as sources: who appears in what record and in
              what role, but never the transcription or scan.

Sources are written into their category subfolders to match the viewer's
per-category fetch paths.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

ROOT = Path.cwd()
VIEWER = ROOT / "family-tree-viewer"
DATA = ROOT / "data"
OUTPUT = ROOT / "_site"

# Non-private display metadata kept on public sources / fan references. The
# viewer degrades gracefully when the omitted (private) fields are absent.
PUBLIC_SOURCE_FIELDS = (
    "schema_version",
    "id",
    "title",
    "record_type",
    "record_category",
    "source_form",
    "information_quality",
    "event_date",
    "private",
)
PUBLIC_FAN_FIELDS = (
    "schema_version",
    "id",
    "title",
    "record_type",
    "record_category",
    "event_date",
    "event_place_text",
)


def load_entities(directory: Path) -> dict[str, dict]:
    """Load every ``*.yaml`` under ``directory`` (recursively) keyed by id."""
    entities: dict[str, dict] = {}
    if not directory.exists():
        return entities
    for path in sorted(directory.rglob("*.yaml")):
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(value, dict) and isinstance(value.get("id"), str):
            entities[value["id"]] = value
    return entities


def source_subpaths() -> dict[str, str]:
    """Map each source id to its category subfolder under ``data/sources``.

    Mirrors the on-disk layout, which the viewer fetches by category, so a new
    source category ships correctly without editing this script.
    """
    mapping: dict[str, str] = {}
    sources_root = DATA / "sources"
    if sources_root.exists():
        for path in sources_root.rglob("*.yaml"):
            value = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(value, dict) and isinstance(value.get("id"), str):
                mapping[value["id"]] = path.parent.relative_to(sources_root).as_posix()
    return mapping


def reduce_record(record: dict, fields: tuple[str, ...]) -> dict:
    out = {key: record[key] for key in fields if key in record}
    out.setdefault("schema_version", record.get("schema_version", 1))
    out.setdefault("id", record["id"])
    return out


def main() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)

    # Dynamic file copy: ship the whole viewer directory. The committed
    # entity-index.json is regenerated below; package.json/README.md are inert.
    shutil.copytree(VIEWER, OUTPUT)

    loader = OUTPUT / "data-loader.js"
    loader.write_text(
        loader.read_text(encoding="utf-8").replace(
            'const DATA_ROOT = "../data";',
            'const DATA_ROOT = "./data";',
        ),
        encoding="utf-8",
    )
    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")

    people = load_entities(DATA / "people")
    families = load_entities(DATA / "families")
    events = load_entities(DATA / "events")
    places = load_entities(DATA / "places")
    sources = load_entities(DATA / "sources")
    fan = load_entities(DATA / "fan")

    living_ids = {pid for pid, p in people.items() if p.get("privacy") == "living"}

    def involves_living(participants: object) -> bool:
        return any(
            isinstance(item, dict) and item.get("person_id") in living_ids
            for item in (participants or [])
        )

    # People: deceased verbatim; living reduced to a structural stub.
    public_people: dict[str, dict] = {}
    for pid, person in people.items():
        if pid in living_ids:
            public_people[pid] = {
                "schema_version": person.get("schema_version", 1),
                "id": pid,
                "preferred_name": "Private living person",
                "privacy": person.get("privacy", "living"),
                "family_ids": person.get("family_ids", []),
            }
        else:
            public_people[pid] = person

    # Events: drop any that involve a living participant.
    public_events = {
        eid: event
        for eid, event in events.items()
        if not involves_living(event.get("participants"))
    }

    # Sources: display metadata only; never publish transcriptions/scans.
    public_sources: dict[str, dict] = {}
    for sid, source in sources.items():
        reduced = reduce_record(source, PUBLIC_SOURCE_FIELDS)
        reduced["linked_people"] = [
            pid for pid in source.get("linked_people", []) if pid not in living_ids
        ]
        public_sources[sid] = reduced

    # FAN references: contextual metadata + who appears in what role; no evidence text.
    public_fan: dict[str, dict] = {}
    for fid, ref in fan.items():
        reduced = reduce_record(ref, PUBLIC_FAN_FIELDS)
        reduced["participants"] = [
            {k: v for k, v in item.items() if k in ("person_id", "role", "note")}
            for item in ref.get("participants", [])
            if isinstance(item, dict) and item.get("person_id") not in living_ids
        ]
        public_fan[fid] = reduced

    datasets = {
        "people": public_people,
        "families": families,
        "events": public_events,
        "places": places,
        "sources": public_sources,
        "fan": public_fan,
    }

    source_dirs = source_subpaths()
    entity_index: dict[str, list[str]] = {}
    for kind, entities in datasets.items():
        entity_index[kind] = sorted(entities)
        for entity_id, entity in entities.items():
            if kind == "sources":
                sub = source_dirs.get(entity_id)
                if not sub:
                    raise SystemExit(f"No category folder for source {entity_id}")
                target = OUTPUT / "data" / "sources" / sub
            else:
                target = OUTPUT / "data" / kind
            target.mkdir(parents=True, exist_ok=True)
            (target / f"{entity_id}.yaml").write_text(
                yaml.safe_dump(entity, allow_unicode=True, sort_keys=False, width=100),
                encoding="utf-8",
            )

    (OUTPUT / "entity-index.json").write_text(
        json.dumps(entity_index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        "Built privacy-filtered Pages site:",
        f"{len(public_people)} people,",
        f"{len(families)} families,",
        f"{len(public_events)} events,",
        f"{len(places)} places,",
        f"{len(public_sources)} sources,",
        f"{len(public_fan)} fan",
    )


if __name__ == "__main__":
    main()
