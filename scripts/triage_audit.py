#!/usr/bin/env python3
"""Audit: list the producer's scans that have no value-gate disposition yet.

Record scans stay in the producer repository (``armond-genealogy-retrieval``); the
handoff carries text only. This audit reads the producer's scans by path, read-only
(``research/evidence/images`` and ``research/resources``), and identifies each by
**SHA-256**. A scan is resolved when its hash is in the public triage index
(``data/triage-index.yaml``) or is already held as evidence by a source, FAN entity or
inventory entry. Identity is content, not filename or mtime, so a file the producer
renames keeps its disposition.

The point is the owner rule (see the ``feedback-attach-every-doc-naming-a-modelled-person``
memory): a record image that names a modelled person must be catalogued; only a
byte-identical duplicate or an image naming no modelled person may be skipped, and
either way the decision is recorded in the triage index.

Local-only (CI has neither the producer nor the drop); never mutates repository data.
Exit codes: 0 ok (or findings without --strict), 1 untriaged scans under --strict,
2 blocked — the producer's scans or the triage index cannot be read.

Usage:
    uv run --frozen python scripts/triage_audit.py [--strict]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from producer_scans import HashCache, ProducerUnavailable, producer_root, scan_files  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "triage-index.yaml"


def held_hashes() -> set[str]:
    held: set[str] = set()
    for path in sorted((ROOT / "data" / "sources").glob("*/*.yaml")) + sorted((ROOT / "data" / "fan").glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for ref in [data.get("digital_file"), *(data.get("additional_pages") or [])]:
            if isinstance(ref, dict) and ref.get("sha256"):
                held.add(ref["sha256"])
    inventory = yaml.safe_load((ROOT / "data" / "document-inventory.yaml").read_text(encoding="utf-8")) or {}
    for document in inventory.get("documents") or []:
        for record_file in document.get("files") or []:
            held.add(record_file["sha256"])
    return held


def find_untriaged(scans: list[Path], triaged: set[str], held: set[str], cache: HashCache) -> list[Path]:
    """Scans whose SHA-256 is neither in the triage index nor held as evidence."""
    return [path for path in scans if (digest := cache.sha256(path)) not in triaged and digest not in held]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--strict", action="store_true", help="exit non-zero if any scan is untriaged or inputs are missing")
    args = parser.parse_args()

    if not INDEX.is_file():
        print(f"BLOCKED: the triage index {INDEX.relative_to(ROOT)} is missing.")
        return 2 if args.strict else 0
    try:
        scans = scan_files()
    except ProducerUnavailable as exc:
        print(f"BLOCKED: {exc} — an environment problem, not 'nothing delivered'.")
        return 2 if args.strict else 0

    index = yaml.safe_load(INDEX.read_text(encoding="utf-8")) or {}
    triaged = {entry["sha256"] for entry in index.get("entries") or []}
    held = held_hashes()
    cache = HashCache()
    untriaged = find_untriaged(scans, triaged, held, cache)
    cache.save()

    producer = producer_root()
    print(f"Triage audit: {len(scans)} producer scans; {len(scans) - len(untriaged)} triaged or held; "
          f"{len(untriaged)} untriaged.")
    if untriaged:
        print("UNTRIAGED — read each by path, then record its disposition in data/triage-index.yaml:")
        for path in untriaged:
            print(f"  {path.relative_to(producer / 'research')}")
    return 1 if (args.strict and untriaged) else 0


if __name__ == "__main__":
    raise SystemExit(main())
