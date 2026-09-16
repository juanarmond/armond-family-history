#!/usr/bin/env python3
"""Build the AI-assistant knowledge base from the canonical YAML data.

Emits three JSON artefacts under ``family-tree-viewer/kb/`` that the
``family-assistant`` Cloudflare Worker feeds to Gemini (see
``_local/ai-assistant-plan.md``):

* ``knowledge-base.json`` — Tier A, sent on every query: every public source
  transcription, the full family/event graph, and a short summary of every
  deceased person. This is the assistant's always-present context.
* ``P-XXXX.json`` — Tier B, one per deceased person, fetched on demand: the full
  bilingual profile plus every name variant, occupation, and the source IDs of
  every document that names the person.
* ``name-index.json`` — a normalized (lowercased, accent-stripped) map from every
  ``preferred_name`` and ``name_variant`` to the P-IDs that bear it, so the Worker
  can resolve a name in a question to a person even when no P-ID is typed.

Privacy model mirrors ``build_pages_site.py`` exactly — this only ever contains
what is already public on the deployed site:

* living people (``privacy: living`` → P-0001/2/3) are excluded entirely: no
  summary, no Tier B file, no name-index entry.
* a source that names any living person (the owner's own documents) is skipped
  entirely — no transcription reaches the knowledge base.
* an event with any living participant is skipped.
* families are kept structurally (they carry no evidence text); a living partner
  or child appears only as an opaque P-ID with no name or profile anywhere.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

import yaml


def load_entities(directory: Path) -> dict[str, dict]:
    entities: dict[str, dict] = {}
    if not directory.exists():
        return entities
    for path in sorted(directory.rglob("*.yaml")):
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(value, dict) and isinstance(value.get("id"), str):
            entities[value["id"]] = value
    return entities


def normalize_name(name: str) -> str:
    """Lowercase, strip accents, collapse whitespace — for the name index."""
    decomposed = unicodedata.normalize("NFKD", name)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", stripped).strip().lower()


def summarize(profile: str | None, max_words: int = 90) -> str:
    """First ``max_words`` words of a profile, markdown preserved.

    Tier A only needs an identity-level gloss of each person (who they are, their
    role and line) so the model always knows everyone exists; the full profile is
    fetched on demand in Tier B. Short by design to keep the always-sent context lean.
    """
    if not profile:
        return ""
    words = profile.split()
    if len(words) <= max_words:
        return profile.strip()
    return " ".join(words[:max_words]).strip() + " …"


def date_value(date_field: object) -> str | None:
    if isinstance(date_field, dict):
        value = date_field.get("value")
        return value if isinstance(value, str) else None
    return None


def build(data_root: Path, output_dir: Path) -> dict[str, int]:
    people = load_entities(data_root / "people")
    families = load_entities(data_root / "families")
    events = load_entities(data_root / "events")
    sources = load_entities(data_root / "sources")

    living_ids = {pid for pid, p in people.items() if p.get("privacy") == "living"}

    def has_living(person_ids: object) -> bool:
        return any(pid in living_ids for pid in (person_ids or []))

    def participant_ids(participants: object) -> list[str]:
        out: list[str] = []
        for item in participants or []:
            if isinstance(item, dict) and isinstance(item.get("person_id"), str):
                out.append(item["person_id"])
        return out

    # --- Public sources (exclude any that name a living person) ------------------
    # Tier A carries only a lightweight descriptor of each document (title, type,
    # date, who it names) so the model always knows every record exists and its gist.
    # The full transcription lives in a per-source Tier B file, fetched on demand.
    # Also invert linked_people → the set of source IDs that name each person.
    source_tier_a: dict[str, dict] = {}
    source_tier_b: dict[str, dict] = {}
    person_source_ids: dict[str, list[str]] = {pid: [] for pid in people}
    skipped_sources = 0
    for sid, src in sources.items():
        linked = src.get("linked_people") or []
        if has_living(linked):
            skipped_sources += 1
            continue
        public_linked = [pid for pid in linked if pid not in living_ids]
        source_tier_a[sid] = {
            "title": src.get("title"),
            "record_type": src.get("record_type"),
            "date": date_value(src.get("event_date")),
            "place": src.get("event_place_text"),
            "linked_people": public_linked,
        }
        source_tier_b[sid] = {
            "id": sid,
            "title": src.get("title"),
            "title_pt": src.get("title_pt"),
            "record_type": src.get("record_type"),
            "record_category": src.get("record_category"),
            "date": date_value(src.get("event_date")),
            "place": src.get("event_place_text"),
            "linked_people": public_linked,
            "abstract": src.get("abstract"),
            "abstract_pt": src.get("abstract_pt"),
            "transcription": src.get("transcription"),
            "transcription_pt": src.get("transcription_pt"),
        }
        for pid in linked:
            if pid in person_source_ids:
                person_source_ids[pid].append(sid)

    # --- Public events (drop any with a living participant) ----------------------
    public_events: dict[str, dict] = {}
    for eid, ev in events.items():
        parts = participant_ids(ev.get("participants"))
        if has_living(parts):
            continue
        public_events[eid] = {
            "type": ev.get("event_type"),
            "date": date_value(ev.get("date")),
            "place": ev.get("place_text"),
            "participants": [
                {"id": item["person_id"], "role": item.get("role")}
                for item in ev.get("participants") or []
                if isinstance(item, dict) and isinstance(item.get("person_id"), str)
            ],
            "source_ids": ev.get("source_ids") or [],
        }

    # --- Families (structural; kept verbatim, living appear only as bare IDs) ----
    public_families: dict[str, dict] = {}
    for fid, fam in families.items():
        public_families[fid] = {
            "partners": [
                p["person_id"]
                for p in fam.get("partners") or []
                if isinstance(p, dict) and isinstance(p.get("person_id"), str)
            ],
            "children": [
                c["person_id"]
                for c in fam.get("children") or []
                if isinstance(c, dict) and isinstance(c.get("person_id"), str)
            ],
            "documented_children": [
                {
                    "name": dc.get("name"),
                    "source_ids": dc.get("source_ids") or [],
                    "note": dc.get("note"),
                }
                for dc in fam.get("documented_children") or []
                if isinstance(dc, dict)
            ],
        }

    # --- People: Tier A summaries + Tier B full records (deceased only) -----------
    tier_a_people: dict[str, dict] = {}
    tier_b: dict[str, dict] = {}
    for pid, person in people.items():
        if pid in living_ids:
            continue
        src_ids = person_source_ids.get(pid, [])
        tier_a_people[pid] = {
            "name": person.get("preferred_name"),
            "sex": person.get("sex"),
            "nationality": person.get("nationality"),
            "summary": summarize(person.get("profile")),
            "source_ids": src_ids,
            "family_ids": person.get("family_ids") or [],
            "event_ids": person.get("event_ids") or [],
        }
        tier_b[pid] = {
            "id": pid,
            "name": person.get("preferred_name"),
            "sex": person.get("sex"),
            "nationality": person.get("nationality"),
            "name_variants": [
                {"value": nv.get("value"), "source_ids": nv.get("source_ids") or []}
                for nv in person.get("name_variants") or []
                if isinstance(nv, dict)
            ],
            "occupations": [
                {"value": oc.get("value"), "source_ids": oc.get("source_ids") or []}
                for oc in person.get("occupations") or []
                if isinstance(oc, dict)
            ],
            "family_ids": person.get("family_ids") or [],
            "event_ids": person.get("event_ids") or [],
            "source_ids": src_ids,
            "notes": [
                {"text": n.get("text"), "text_pt": n.get("text_pt")}
                for n in person.get("notes") or []
                if isinstance(n, dict)
            ],
            "profile": person.get("profile"),
            "profile_pt": person.get("profile_pt"),
        }

    # --- Name index (deceased only) ---------------------------------------------
    # Two maps: `names` = full preferred names + variants (high-confidence exact
    # match); `tokens` = individual given-name / surname words (so a bare "Iris" or
    # "Rutschmann" in a question still resolves). A token may map to several people
    # (e.g. "maria"); the Worker prefers a `names` hit, then disambiguates a `tokens`
    # hit by context.
    NAME_STOPWORDS = {"de", "da", "do", "dos", "das", "e", "du", "von", "van",
                      "la", "le", "del", "di", "y", "the", "of"}
    full_names: dict[str, set[str]] = {}
    tokens: dict[str, set[str]] = {}

    def add_full(name: object, pid: str) -> None:
        if not isinstance(name, str) or not name.strip():
            return
        key = normalize_name(name)
        if key:
            full_names.setdefault(key, set()).add(pid)
            for tok in key.split(" "):
                if len(tok) >= 3 and tok not in NAME_STOPWORDS:
                    tokens.setdefault(tok, set()).add(pid)

    for pid, person in people.items():
        if pid in living_ids:
            continue
        add_full(person.get("preferred_name"), pid)
        for nv in person.get("name_variants") or []:
            if isinstance(nv, dict):
                add_full(nv.get("value"), pid)

    names_sorted = {k: sorted(v) for k, v in sorted(full_names.items())}
    tokens_sorted = {k: sorted(v) for k, v in sorted(tokens.items())}

    # --- Write artefacts ---------------------------------------------------------
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = date.today().isoformat()

    knowledge_base = {
        "generated": generated,
        "counts": {
            "people": len(tier_a_people),
            "sources": len(source_tier_a),
            "families": len(public_families),
            "events": len(public_events),
        },
        "people": tier_a_people,
        "sources": source_tier_a,
        "families": public_families,
        "events": public_events,
    }

    # Compact separators: the Worker re-serializes these before sending to Gemini,
    # so the token count that matters is the compact form, not pretty-printed bytes.
    def write_json(path: Path, payload: object) -> int:
        compact = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        path.write_text(compact + "\n", encoding="utf-8")
        return len(compact)

    kb_chars = write_json(output_dir / "knowledge-base.json", knowledge_base)
    write_json(
        output_dir / "name-index.json",
        {"generated": generated, "names": names_sorted, "tokens": tokens_sorted},
    )

    # Clean stale Tier B files, then write current person + source sets.
    for stale in output_dir.glob("*.json"):
        if stale.name not in ("knowledge-base.json", "name-index.json"):
            stale.unlink()
    tier_b_chars = 0
    for pid, record in tier_b.items():
        tier_b_chars += write_json(output_dir / f"{pid}.json", record)
    source_b_chars = 0
    for sid, record in source_tier_b.items():
        source_b_chars += write_json(output_dir / f"{sid}.json", record)

    return {
        "people": len(tier_a_people),
        "living_excluded": len(living_ids),
        "sources": len(source_tier_a),
        "sources_skipped_living": skipped_sources,
        "families": len(public_families),
        "events": len(public_events),
        "names": len(names_sorted),
        "tokens": len(tokens_sorted),
        "tier_a_tokens_est": kb_chars // 4,
        "tier_b_person_tokens_avg": (tier_b_chars // max(len(tier_b), 1)) // 4,
        "tier_b_source_tokens_avg": (source_b_chars // max(len(source_tier_b), 1)) // 4,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("family-tree-viewer/kb"))
    args = parser.parse_args()

    stats = build(args.data_root, args.output)
    print(f"Wrote knowledge base to {args.output}/:")
    print(
        f"  {stats['people']} people ({stats['living_excluded']} living excluded), "
        f"{stats['sources']} sources ({stats['sources_skipped_living']} skipped: living-linked), "
        f"{stats['families']} families, {stats['events']} events, "
        f"{stats['names']} indexed names"
    )
    print(
        f"  Tier A ≈ {stats['tier_a_tokens_est']:,} tokens (always sent); "
        f"Tier B ≈ {stats['tier_b_person_tokens_avg']:,} tokens/person, "
        f"{stats['tier_b_source_tokens_avg']:,} tokens/source (fetched on demand)"
    )


if __name__ == "__main__":
    main()
