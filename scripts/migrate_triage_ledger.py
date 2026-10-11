"""Migrate the narrative value-gate ledger into the public, hash-keyed triage index.

One-off migration of 2026-10-11 (plan §11.1), kept for provenance and so it can be
re-run on a fresh checkout to reproduce the index. It reads, read-only:

* the private narrative ledger (``private/triage/from-retrieval-triage-ledger.md``);
* the producer's scans, by path (``…/armond-genealogy-retrieval/research/evidence/images``
  and ``…/research/resources``), never running Git there;
* the producer's records manifest (``research/output/ledgers/records-manifest.json``),
  for FamilySearch ARK keys, page lists and rename aliases.

It writes ``data/triage-index.yaml`` (public: SHA-256, size, media type, disposition,
target IDs and the producer filename when the filename names no living person — never
record content) and a private migration report beside the ledger listing every row,
how it mapped and every row that could not be mapped. No row is dropped silently.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import mimetypes
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PRODUCER = Path.home() / "Documents" / "meu" / "armond-genealogy-retrieval"
LEDGER = ROOT / "private" / "triage" / "from-retrieval-triage-ledger.md"
REPORT = ROOT / "private" / "triage" / "migration-report-2026-10-11.md"
INDEX = ROOT / "data" / "triage-index.yaml"
SCAN_DIRS = ("research/evidence/images", "research/resources")
SCAN_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".pdf"}
ENTITY_ID = re.compile(r"\b(?:CIV|GOV|PAR|PRB|NWS|PUB|REC|FAN|DOC)-\d{4}\b")
DATE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")

# Free-text disposition → controlled vocabulary, first match wins (order matters).
DISPOSITION_RULES: tuple[tuple[str, str], ...] = (
    (r"privacy-excluded|privacy excluded", "privacy-excluded"),
    (r"\bduplicate\b|byte-identical|same bytes|re-?sync of", "duplicate"),
    (r"supersed", "superseded"),
    (r"catalogued|completed\s*→|\bpromoted\b|already catalogued|already held|already in", "promoted"),
    (r"\bfan\b", "fan"),
    (r"namesake|distinct[- ]family|different (?:man|woman|person|family)", "namesake"),
    (r"bounded|negative[- ]proof|no hit|not found", "bounded-negative"),
    (r"\bnoise\b|not a record|unrelated|photo of|portrait", "noise"),
    (r"deferred|awaiting|reduced-res|native-res|incomplete", "held"),
    (r"mismatch|rejected|not promoted|no value|discard", "rejected"),
    (r"candidate", "candidate-for-promotion"),
    (r"\blead\b|collateral|context|assessed|read\b|passed", "reviewed-lead"),
)
PRECEDENCE = (
    "promoted", "duplicate", "superseded", "fan", "held", "candidate-for-promotion",
    "reviewed-lead", "reviewed", "bounded-negative", "namesake", "noise", "rejected",
    "privacy-excluded", "unclassified",
)


def classify(text: str) -> str:
    low = text.lower()
    for pattern, disposition in DISPOSITION_RULES:
        if re.search(pattern, low):
            return disposition
    return "unclassified"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def producer_catalog(producer: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for rel in SCAN_DIRS:
        base = producer / rel
        if not base.is_dir():
            raise SystemExit(f"BLOCKED: producer scans not readable at {base}")
        for path in base.rglob("*"):
            if path.is_file() and not path.is_symlink() and path.suffix.lower() in SCAN_SUFFIXES:
                files.setdefault(path.name, path)
    return files


def manifest_records(producer: Path) -> tuple[dict[str, list[str]], dict[str, str]]:
    """ARK-keyed page lists and alias → current filename."""
    data = json.loads((producer / "research/output/ledgers/records-manifest.json").read_text(encoding="utf-8"))
    pages_by_ark: dict[str, list[str]] = {}
    alias_to_name: dict[str, str] = {}
    for key, record in data.items():
        pages = [Path(p).name for p in record.get("pages") or [] if isinstance(p, str)]
        if key.startswith("ft_"):
            pages_by_ark[key[3:].replace("-", ":", 2)] = pages
        for alias in record.get("aliases") or []:
            if isinstance(alias, str) and pages:
                alias_to_name[Path(alias).name] = pages[0] if len(pages) == 1 else ""
    return pages_by_ark, alias_to_name


def expand_key(key: str, names: list[str]) -> list[str]:
    """Resolve a ledger key cell to concrete producer filenames."""
    found: list[str] = []
    tokens = re.findall(r"`([^`]+)`", key) or [key]
    stems = {Path(n).stem: n for n in names}
    for token in tokens:
        token = token.strip().rstrip(".,;")
        if not token:
            continue
        if any(ch in token for ch in "*?{"):
            pattern = re.sub(r"\{[^}]*\}", "*", token)
            found += [n for n in names if fnmatch.fnmatch(n, pattern) or fnmatch.fnmatch(Path(n).stem, pattern)]
            continue
        if token in names:
            found.append(token)
            continue
        if token in stems:
            found.append(stems[token])
            continue
        # Page ranges: "<stem>-p3 … through p5", "<stem>-p1/p2", "<stem> (p1+p2)".
        base = re.match(r"^(.*-p)(\d+)$", token)
        if base:
            first = int(base.group(2))
            last = re.search(r"through\s*`?p?(\d+)", key) or re.search(rf"{re.escape(token)}\s*/\s*p?(\d+)", key)
            end = int(last.group(1)) if last else first
            for page in range(first, end + 1):
                stem = f"{base.group(1)}{page}"
                if stem in stems:
                    found.append(stems[stem])
            continue
        prefix = [n for n in names if Path(n).stem.startswith(token + "-p") or Path(n).stem == token]
        if prefix:
            found += prefix
    seen: set[str] = set()
    return [n for n in found if not (n in seen or seen.add(n))]


def living_name_tokens(root: Path) -> list[str]:
    tokens = []
    for path in (root / "data" / "people").glob("*.yaml"):
        person = yaml.safe_load(path.read_text(encoding="utf-8"))
        if person.get("privacy") == "living":
            parts = [p.lower() for p in person["preferred_name"].split()]
            tokens += ["-".join(parts[:2]), parts[0] + "-" + parts[-1]]
    return tokens


def consumer_holdings(root: Path) -> tuple[dict[str, set[str]], dict[str, list[tuple[str, int]]]]:
    """SHA-256 → IDs holding that file, and ID → its files (path, size) in page order."""
    held: dict[str, set[str]] = defaultdict(set)
    files_of: dict[str, list[tuple[str, int]]] = {}
    for path in sorted((root / "data" / "sources").glob("*/*.yaml")) + sorted((root / "data" / "fan").glob("*.yaml")):
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        refs = [r for r in [record.get("digital_file"), *(record.get("additional_pages") or [])] if isinstance(r, dict)]
        files_of[record["id"]] = [(r["sha256"], r["path"]) for r in refs if r.get("sha256")]
        for digest, _ in files_of[record["id"]]:
            held[digest].add(record["id"])
    inventory = yaml.safe_load((root / "data" / "document-inventory.yaml").read_text(encoding="utf-8"))
    for document in inventory["documents"]:
        for record_file in document.get("files") or []:
            held[record_file["sha256"]].add(document.get("proposed_source_id") or document["inventory_id"])
        files_of.setdefault(document["inventory_id"], [(f["sha256"], f["path"]) for f in document.get("files") or []])
    return held, files_of


def parse_ledger(text: str) -> list[dict]:
    rows, section, header = [], None, None
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("#"):
            section = line.lstrip("#").strip()
            continue
        if not line.startswith("|") or re.match(r"^\|\s*-", line):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) >= 2 and cells[1].lower() in ("disposition", "where recorded"):
            header = cells[0]
            continue
        if len(cells) < 2:
            continue
        rows.append({"line": number, "section": section, "key_type": header, "key": cells[0],
                     "disposition_text": cells[1], "note": cells[2] if len(cells) > 2 else ""})
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--producer", type=Path, default=PRODUCER)
    parser.add_argument("--index", type=Path, default=INDEX)
    parser.add_argument("--report", type=Path, default=REPORT)
    args = parser.parse_args(argv)

    rows = parse_ledger(args.ledger.read_text(encoding="utf-8"))
    catalog = producer_catalog(args.producer)
    names = sorted(catalog)
    pages_by_ark, alias_to_name = manifest_records(args.producer)
    living = living_name_tokens(ROOT)
    hashes: dict[str, str] = {}
    held, files_of = consumer_holdings(ROOT)
    overrides: list[str] = []

    entries: dict[str, dict] = {}
    report: list[str] = []
    unmapped: list[tuple[dict, str]] = []
    for row in rows:
        disposition = classify(row["disposition_text"] + " " + row["note"])
        targets = sorted(set(ENTITY_ID.findall(row["disposition_text"] + " " + row["note"])))
        files = expand_key(row["key"], names)
        ark = re.search(r"3:1:[0-9A-Z]{4}-[0-9A-Z]{3,4}-[0-9A-Z]{2,4}(?:-[0-9A-Z]{1,4})?", row["key"])
        if not files and ark and ark.group(0) in pages_by_ark:
            files = [n for n in pages_by_ark[ark.group(0)] if n in catalog]
        if not files:
            for token in re.findall(r"`([^`]+)`", row["key"]):
                current = alias_to_name.get(token) or alias_to_name.get(Path(token).name)
                if current and current in catalog:
                    files.append(current)
        if not files and targets and row["key_type"] not in ("item", "cluster"):
            # Renamed at the producer without an alias: the consumer holds the promoted
            # bytes, so the target record's own evidence gives the file's identity.
            page = re.search(r"-p(\d+)`?\s*$", row["key"].strip())
            held_files = [f for t in targets for f in files_of.get(t, [])]
            if page and len(held_files) >= int(page.group(1)):
                held_files = [held_files[int(page.group(1)) - 1]]
            for digest, path in held_files:
                entry = entries.setdefault(digest, {
                    "sha256": digest,
                    "size": (ROOT / path).stat().st_size if (ROOT / path).is_file() else None,
                    "media_type": mimetypes.guess_type(path)[0] or "application/octet-stream",
                    "producer_path": None,
                    "disposition": disposition,
                    "target_ids": [],
                    "decided": None,
                    "source": "ledger-migration-2026-10-11",
                })
                entry["target_ids"] = sorted(set(entry["target_ids"]) | set(targets))
                report.append(f"| {row['line']} | {digest[:12]} | {disposition} (by the target's held file; renamed at the producer) |")
            if held_files:
                continue
        if not files:
            reason = ("FamilySearch ARK not in the producer manifest" if ark else
                      "no file identity in the key (a cluster, set summary or item)" if row["key_type"] in ("cluster", "item", "set", "set (pages)")
                      else "file not found among the producer's scans")
            unmapped.append((row, reason))
            report.append(f"| {row['line']} | UNMAPPED | {reason} |")
            continue
        for name in files:
            path = catalog[name]
            digest = hashes.get(name) or hashes.setdefault(name, sha256_file(path))
            rel = path.relative_to(args.producer / "research").as_posix()
            entry = entries.setdefault(digest, {
                "sha256": digest,
                "size": path.stat().st_size,
                "media_type": mimetypes.guess_type(name)[0] or "application/octet-stream",
                "producer_path": None if any(t in name.lower() for t in living) else rel,
                "disposition": disposition,
                "target_ids": [],
                "decided": None,
                "source": "ledger-migration-2026-10-11",
            })
            if PRECEDENCE.index(disposition) < PRECEDENCE.index(entry["disposition"]):
                entry["disposition"] = disposition
            entry["target_ids"] = sorted(set(entry["target_ids"]) | set(targets))
            when = DATE.search(row["section"] or "")
            if when and (entry["decided"] is None or when.group(1) > entry["decided"]):
                entry["decided"] = when.group(1)
            report.append(f"| {row['line']} | {digest[:12]} | {disposition} |")

    # Holdings outrank free text: a file held as evidence is promoted (or FAN context),
    # and the IDs holding it are its targets. The ledger wording stays in the private report.
    for digest, entry in entries.items():
        holders = held.get(digest)
        if not holders:
            continue
        kind = "fan" if all(h.startswith("FAN-") for h in holders) else "promoted"
        if entry["disposition"] not in ("promoted", "duplicate", "fan") or entry["disposition"] != kind and kind == "promoted":
            overrides.append(f"| {digest[:12]} | {entry['disposition']} → {kind} | held by {', '.join(sorted(holders))} |")
            entry["disposition"] = kind
        entry["target_ids"] = sorted(set(entry["target_ids"]) | holders)
    # "promoted" means the bytes are held. A page the ledger counted inside a promoted set
    # whose own bytes are not held was read, not promoted: flag it for the page audit.
    not_held: list[str] = []
    for digest, entry in entries.items():
        if entry["disposition"] == "promoted" and digest not in held:
            entry["disposition"] = "reviewed"
            not_held.append(f"| {digest[:12]} | {entry['producer_path'] or '(path withheld)'} | {', '.join(entry['target_ids']) or '—'} |")

    index = {
        "version": 1,
        "generated": date.today().isoformat(),
        "entries": [entries[k] for k in sorted(entries)],
    }
    header = (
        "# Public triage index: one disposition per producer file, keyed by SHA-256 (plan §11.1).\n"
        "# No record content, names or reasons here; the narrative detail is private\n"
        "# (private/triage/). Migrated from the narrative ledger on 2026-10-11 by\n"
        "# scripts/migrate_triage_ledger.py; maintained by the value gate thereafter.\n"
    )
    args.index.write_text(header + yaml.safe_dump(index, sort_keys=False, allow_unicode=True), encoding="utf-8")

    counts = defaultdict(int)
    for _, reason in unmapped:
        counts[reason] += 1
    summary = [
        "# Triage ledger migration report (2026-10-11) — PRIVATE",
        "",
        f"- Ledger data rows: {len(rows)}",
        f"- Rows mapped to producer files: {len(rows) - len(unmapped)}",
        f"- Distinct files (index entries): {len(entries)}",
        f"- Rows not mapped: {len(unmapped)}",
        *[f"  - {reason}: {n}" for reason, n in sorted(counts.items())],
        "",
        "Every row is listed below by its ledger line. Unmapped rows stay authoritative in the",
        "narrative ledger; none was discarded.",
        "",
        "| ledger line | result | detail |",
        "| --- | --- | --- |",
        *report,
        "",
        "## Dispositions corrected from holdings",
        "",
        "| file | ledger reading → stored | why |",
        "| --- | --- | --- |",
        *overrides,
        "",
        "## Read inside a promoted set, bytes not held (check page completeness)",
        "",
        "| file | producer path | ledger targets |",
        "| --- | --- | --- |",
        *not_held,
        "",
        "## Unmapped rows (full key and disposition)",
        "",
        *[f"- line {r['line']} ({reason}): key {r['key']} — {r['disposition_text']}" for r, reason in unmapped],
        "",
    ]
    args.report.write_text("\n".join(summary), encoding="utf-8")
    print(f"rows {len(rows)} | mapped {len(rows) - len(unmapped)} | index entries {len(entries)} | unmapped {len(unmapped)}")
    for reason, n in sorted(counts.items()):
        print(f"  unmapped — {reason}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
