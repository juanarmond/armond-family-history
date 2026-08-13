#!/usr/bin/env python3
"""Advisory audit: flag modelled-person profiles that lag the retrieval drop.

The external FamilySearch retrieval agent maintains rich per-person profiles under
`research/from-retrieval/FINDINGS/profiles/<surname>/<person>.md` (see AGENTS.md).
Those are the enrichment *source*; each modelled person's YAML `profile`/`profile_pt`
should track them. Over time the YAML profiles drift behind the research profiles.

This script is a LOCAL, ADVISORY heuristic (the drop is gitignored, so this cannot
run in CI). For every deceased modelled person it best-matches a research profile by
name and reports where the research profile is materially larger than the YAML
`profile`, or where `profile`/`profile_pt` are missing or out of balance. It never
mutates data and always exits 0 unless run with --strict (then non-zero if anything
is flagged), so it can gate a pre-commit step if desired.

The name match is a heuristic (common names like "Maria de Jesus" collide) — always
confirm the identity before enriching from the suggested file.

Usage:
    uv run --frozen python scripts/profile_sync_audit.py [--strict] [--ratio 1.8]
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
import unicodedata

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PEOPLE_DIR = os.path.join(ROOT, "data", "people")
FINDINGS_DIR = os.path.join(
    ROOT, "research", "from-retrieval", "FINDINGS", "profiles"
)


def norm_tokens(text: str) -> set[str]:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if t}


def load_findings() -> dict[str, set[str]]:
    files: dict[str, set[str]] = {}
    for path in glob.glob(os.path.join(FINDINGS_DIR, "**", "*.md"), recursive=True):
        base = os.path.basename(path)[:-3]
        if base.lower() in ("readme", "analytical-depth"):
            continue
        files[path] = norm_tokens(base.replace("-", " "))
    return files


def best_match(name_tokens: set[str], findings: dict[str, set[str]]):
    best, best_overlap = None, 0
    for path, tokens in findings.items():
        overlap = len(name_tokens & tokens)
        if overlap > best_overlap:
            best, best_overlap = path, overlap
    return (best, best_overlap) if best_overlap >= 2 else (None, best_overlap)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="exit non-zero if any profile is flagged")
    ap.add_argument("--ratio", type=float, default=1.8, help="flag when findings/YAML char ratio exceeds this")
    args = ap.parse_args()

    if not os.path.isdir(FINDINGS_DIR):
        print("profile-sync-audit: no retrieval drop present "
              f"({os.path.relpath(FINDINGS_DIR, ROOT)} absent) — nothing to compare.")
        return 0

    findings = load_findings()
    flagged: list[tuple[str, str, str, str]] = []  # (pid, name, reason, hint)

    for pf in sorted(glob.glob(os.path.join(PEOPLE_DIR, "*.yaml"))):
        person = yaml.safe_load(open(pf, encoding="utf-8"))
        if not isinstance(person, dict) or person.get("privacy") == "living":
            continue
        pid, name = person.get("id", "?"), person.get("preferred_name", "")
        en = person.get("profile") or ""
        pt = person.get("profile_pt") or ""
        if not en:
            flagged.append((pid, name, "no EN profile", ""))
            continue
        if not pt:
            flagged.append((pid, name, "no PT profile (bilingual gap)", ""))
        match, _ = best_match(norm_tokens(name), findings)
        if match:
            fc = len(open(match, encoding="utf-8").read())
            ratio = fc / max(len(en), 1)
            if ratio >= args.ratio:
                rel = os.path.relpath(match, os.path.join(ROOT, "research", "from-retrieval"))
                flagged.append((pid, name, f"research profile {ratio:.1f}x the YAML profile", rel))

    if not flagged:
        print("profile-sync-audit: all modelled profiles are in step with the retrieval drop.")
        return 0

    print(f"profile-sync-audit: {len(flagged)} profile(s) may lag the retrieval drop "
          "(heuristic name-match — verify identity before enriching):\n")
    for pid, name, reason, hint in sorted(flagged, key=lambda r: r[2], reverse=True):
        line = f"  {pid}  {name[:34]:34}  {reason}"
        if hint:
            line += f"   → {hint}"
        print(line)
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
