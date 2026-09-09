#!/usr/bin/env python3
"""Generate the viewer's "What's new / Novidades" feed (family-tree-viewer/updates.json).

Comprehensive by construction so nothing is missed: every NON-private source becomes a dated
"document" entry (dated by the git commit that first added it), with its subject person linked
so a reader can jump straight to that ancestor. Curated editorial entries — milestones,
corrections and profile/"portrait" highlights that git cannot classify — are read from
family-tree-viewer/updates.yaml and merged in. Living people and private sources are never
surfaced. The merged feed is written newest-first to updates.json, which the viewer loads.

Run: ``uv run --frozen python scripts/build_updates.py`` (or ``make updates``). Commit the
regenerated updates.json alongside the data, the same way entity-index.json is committed.
"""
from __future__ import annotations

import datetime as _dt
import glob
import json
import os
import re
import subprocess

import yaml

_DATE_LINE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEWER = os.path.join(ROOT, "family-tree-viewer")
CURATED = os.path.join(VIEWER, "updates.yaml")
OUTPUT = os.path.join(VIEWER, "updates.json")

SOURCE_ID_PREFIXES = ("CIV", "GOV", "PAR", "PRB", "NWS", "PUB", "REC")


def git_add_dates(pathspec: str) -> dict[str, str]:
    """Map each added file (repo-relative) to the date of the commit that first added it."""
    out = subprocess.run(
        ["git", "-C", ROOT, "log", "--diff-filter=A", "--name-only",
         "--date=short", "--format=%ad", "--", pathspec],
        capture_output=True, text=True, check=True,
    ).stdout
    dates: dict[str, str] = {}
    current = None
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if _DATE_LINE.match(line):
            current = line
        elif current:  # a file path added in the `current` commit
            if line not in dates or current < dates[line]:
                dates[line] = current  # keep the earliest (original) add date
    return dates


def load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def main() -> int:
    people = {}
    for path in glob.glob(os.path.join(ROOT, "data", "people", "*.yaml")):
        data = load_yaml(path)
        pid = data.get("id")
        if pid:
            people[pid] = data

    def is_living(pid: str) -> bool:
        return (people.get(pid) or {}).get("privacy") == "living"

    def subject_person(source: dict) -> str | None:
        for pid in source.get("linked_people") or []:
            if pid in people and not is_living(pid):
                return pid
        return None

    add_dates = git_add_dates("data/sources")

    auto: list[dict] = []
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "sources", "*", "*.yaml"))):
        source = load_yaml(path)
        sid = source.get("id")
        if not sid or source.get("private"):
            continue  # never surface a private (living-adjacent) record
        rel = os.path.relpath(path, ROOT)
        entry = {
            "date": add_dates.get(rel, ""),
            "kind": "document",
            "title": source.get("title", sid),
            "title_pt": source.get("title_pt", source.get("title", sid)),
            "primary": sid,
        }
        subject = subject_person(source)
        if subject:
            entry["links"] = [subject]
        auto.append(entry)

    # Curated editorial entries (milestones / corrections / portrait highlights). These take
    # precedence: if one references a source, drop the auto entry for that source (no dupes).
    curated_doc = load_yaml(CURATED)
    curated = list(curated_doc.get("updates") or [])
    curated_source_ids = set()
    for entry in curated:
        for token in [entry.get("primary")] + list(entry.get("links") or []):
            if isinstance(token, str) and token.split("-")[0] in SOURCE_ID_PREFIXES:
                curated_source_ids.add(token)
        # Guard: never let a curated entry surface a living person.
        living = [pid for pid in (entry.get("links") or []) if is_living(pid)]
        if living:
            raise SystemExit(f"updates.yaml references living people {living} in: {entry.get('title')}")

    auto = [e for e in auto if e["primary"] not in curated_source_ids]

    merged = curated + auto
    # Newest first; stable so curated entries lead within a shared date.
    merged.sort(key=lambda e: str(e.get("date", "")), reverse=True)

    payload = {
        "generated": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updates": merged,
    }
    with open(OUTPUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"Wrote {os.path.relpath(OUTPUT, ROOT)} with {len(merged)} entries "
          f"({len(auto)} auto documents + {len(curated)} curated).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
