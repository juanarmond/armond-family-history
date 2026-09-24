#!/usr/bin/env python3
"""Generate the viewer's "What's new / Novidades" feed (family-tree-viewer/updates.json).

Comprehensive by construction so nothing is missed: every NON-private source becomes a dated
"document" entry (dated by when it became readable — the commit that added it, or the later
commit that cleared its `private` flag), with its subject person linked
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
import subprocess

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEWER = os.path.join(ROOT, "family-tree-viewer")
CURATED = os.path.join(VIEWER, "updates.yaml")
OUTPUT = os.path.join(VIEWER, "updates.json")

SOURCE_ID_PREFIXES = ("CIV", "GOV", "PAR", "PRB", "NWS", "PUB", "REC")


def git_add_dates(pathspec: str) -> dict[str, str]:
    """Map each file (by its CURRENT repo-relative path) to the date it was first added.

    Renames are followed: reclassifying a source moves its file between category
    directories, and `--diff-filter=A` alone reports nothing for the new path, leaving
    the record undated and stranded at the foot of the feed.
    """
    out = subprocess.run(
        ["git", "-C", ROOT, "log", "--diff-filter=AR", "--name-status", "--find-renames",
         "--reverse", "--date=short", "--format=%x01%ad", "--", pathspec],
        capture_output=True, text=True, check=True,
    ).stdout
    dates: dict[str, str] = {}
    date = None
    for line in out.splitlines():
        if line.startswith("\x01"):
            date = line[1:].strip()
            continue
        parts = line.split("\t")
        if not date or len(parts) < 2:
            continue
        if parts[0].startswith("R") and len(parts) >= 3:
            dates[parts[2]] = dates.pop(parts[1], date)  # carry the original add date over
        elif parts[0] == "A":
            dates.setdefault(parts[1], date)  # oldest-first, so the first A is the original
    return dates


def git_public_dates(pathspec: str, add_dates: dict[str, str]) -> dict[str, str]:
    """Map each source file to the date it became visible to a reader.

    A record catalogued while `private: true` is not new to the public on the day the
    file was added — it is new on the day the flag was cleared. Dating it by the add
    date files it under a month when nobody could open it, stranding it far from the
    milestone that announces it.
    """
    out = subprocess.run(
        ["git", "-C", ROOT, "log", "-G", r"^private:", "-p", "--date=short",
         "--format=%x01%ad", "--", pathspec],
        capture_output=True, text=True, check=True,
    ).stdout

    # Newest-first; keep the first (most recent) true -> false flip seen per file.
    flips: dict[str, str] = {}
    date = None
    path = None
    removed_private_true = False
    for line in out.splitlines():
        if line.startswith("\x01"):
            date = line[1:].strip()
            path = None
            removed_private_true = False
        elif line.startswith("+++ b/"):
            path = line[6:].strip()
            removed_private_true = False
        elif line.startswith("-private:"):
            removed_private_true = "true" in line
        elif line.startswith("+private:"):
            if path and date and removed_private_true and "false" in line:
                flips.setdefault(path, date)
            removed_private_true = False

    dates = dict(add_dates)
    for path, flipped in flips.items():
        # A flip can only postpone visibility, never predate the file itself.
        dates[path] = max(flipped, add_dates.get(path, ""))
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

    public_dates = git_public_dates("data/sources", git_add_dates("data/sources"))

    auto: list[dict] = []
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "sources", "*", "*.yaml"))):
        source = load_yaml(path)
        sid = source.get("id")
        if not sid or source.get("private"):
            continue  # never surface a private (living-adjacent) record
        rel = os.path.relpath(path, ROOT)
        entry = {
            "date": public_dates.get(rel, ""),
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
