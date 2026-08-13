#!/usr/bin/env python3
"""Advisory audit: flag people whose OWN vital record may name unmodelled parents.

Per AGENTS.md ("Entity connectivity and completeness"): when a held vital record
(baptism, birth, marriage, death) *about* a modelled person names that person's
parents (or grandparents), those ancestors must be modelled as person nodes with a
parentage family and full reciprocity — not left in prose or demoted to
`documented_children`. This heuristic catches the gap the moment such a record is
catalogued: it lists every modelled, deceased person who is the SUBJECT of their own
birth/baptism/death (as `principal`) or marriage (as `spouse`) event yet has NO
parentage family, so a reviewer can open the cited record and, if it names the
parents, model them.

It is ADVISORY, not a hard rule: a death act does not always name parents, and many
people are genuinely top-of-line (their parents appear only in a *descendant's*
record, or only as an un-promoted published-genealogy / collaborative-tree lead —
which must never be minted into a node). So it separates the candidates that a note
already flags as OPEN/unlocated (acknowledged) from those with no such note (review).
It never mutates data and exits 0 unless --strict is given (then non-zero if any
un-acknowledged candidate remains), so it can gate a pre-commit step if desired.

Usage:
    uv run --frozen python scripts/ancestor_gap_audit.py [--strict]
"""
from __future__ import annotations

import argparse
import glob
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PEOPLE_DIR = os.path.join(ROOT, "data", "people")
FAMILY_DIR = os.path.join(ROOT, "data", "families")
EVENT_DIR = os.path.join(ROOT, "data", "events")

# Events whose principal (or, for marriage, spouse) is the subject the record is
# *about*, and which therefore typically state that subject's own parents.
SUBJECT_PRINCIPAL_EVENTS = {"birth", "baptism", "death"}
SUBJECT_SPOUSE_EVENTS = {"marriage"}

# A note containing any of these already marks the parentage as a known, deliberate
# open gap (record not held, or parents only a lead) — demote such candidates.
ACKNOWLEDGED = (
    "not located",
    "not held",
    "not in hand",
    "unrecorded",
    "unlocated",
    "not reachable",
    "names no parents",
    "no parents",
    "parents not",
    "parents unknown",
    "parentage open",
    "[open",
    "open]",
    "off-tool",
    "only a lead",
    "lead only",
    "not promoted",
    "published genealogy",
    "published compilation",
    "collaborative tree",
    "fs-tree",
    "pre-1801",
    "pre-1706",
)


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero if any un-acknowledged candidate remains")
    args = parser.parse_args()

    people = {}
    for path in glob.glob(os.path.join(PEOPLE_DIR, "*.yaml")):
        data = load(path)
        if data and data.get("id"):
            people[data["id"]] = data

    # Person ids that already have a parentage family (appear as a child).
    have_parents: set[str] = set()
    for path in glob.glob(os.path.join(FAMILY_DIR, "*.yaml")):
        fam = load(path) or {}
        for child in fam.get("children") or []:
            pid = child.get("person_id")
            if pid:
                have_parents.add(pid)

    # Subject-of-own-vital-record: person id -> [(event id, type, source ids)]
    own_vitals: dict[str, list[tuple[str, str, list[str]]]] = {}
    for path in glob.glob(os.path.join(EVENT_DIR, "*.yaml")):
        ev = load(path) or {}
        etype = ev.get("event_type")
        for part in ev.get("participants") or []:
            pid = part.get("person_id")
            role = part.get("role")
            if not pid:
                continue
            is_subject = (
                (etype in SUBJECT_PRINCIPAL_EVENTS and role == "principal")
                or (etype in SUBJECT_SPOUSE_EVENTS and role == "spouse")
            )
            if is_subject:
                own_vitals.setdefault(pid, []).append(
                    (ev.get("id"), etype, ev.get("source_ids") or [])
                )

    review: list[tuple[str, str, list]] = []
    acknowledged: list[tuple[str, str, list]] = []
    for pid, events in own_vitals.items():
        if pid in have_parents:
            continue  # parents already modelled
        person = people.get(pid)
        if not person:
            continue  # documented-only participant, not a modelled node
        if person.get("privacy") == "living":
            continue  # never model living people's parents from this signal
        name = person.get("preferred_name") or person.get("name") or pid
        blob = yaml.safe_dump(person, allow_unicode=True).lower()
        bucket = acknowledged if any(k in blob for k in ACKNOWLEDGED) else review
        bucket.append((pid, name, sorted(events)))

    def show(items: list, header: str) -> None:
        if not items:
            return
        print(f"\n{header}")
        for pid, name, events in sorted(items):
            print(f"  {pid}  {name}")
            for eid, etype, srcs in events:
                srcs_str = ", ".join(srcs) if srcs else "no source"
                print(f"      {eid} ({etype}) — {srcs_str}")

    total = len(review) + len(acknowledged)
    print(
        f"Ancestor-gap audit: {total} deceased person(s) are the subject of their own "
        f"vital record but have no parentage family."
    )
    show(
        review,
        "REVIEW — no note yet marks the parentage as open; open each cited record and, "
        "if it names the parents/grandparents, model them (AGENTS.md, Entity connectivity):",
    )
    show(
        acknowledged,
        "Acknowledged (a note already flags the parents as unlocated / lead-only / not "
        "named in the record) — no action unless a new record changes that:",
    )
    if not total:
        print("  none — every subject of a held vital record has their named parents modelled.")

    return 1 if (args.strict and review) else 0


if __name__ == "__main__":
    raise SystemExit(main())
