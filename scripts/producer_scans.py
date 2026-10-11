"""Read-only access to the producer's scans, for the consumer's audits.

The producer (``armond-genealogy-retrieval``) keeps its record scans in
``research/evidence/images`` and its reference documents in ``research/resources``.
The consumer reads them by path and never runs Git there (plan §14.12). Identity is
content: every scan is known by its SHA-256, cached by (path, size, mtime) in the
gitignored intake state so repeated audits stay fast.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRODUCER = Path.home() / "Documents" / "meu" / "armond-genealogy-retrieval"
SCAN_DIRS = ("research/evidence/images", "research/resources")
SCAN_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".pdf"}
CACHE = ROOT / "research" / ".intake" / "hash-cache.json"
INTAKE_LOG = ROOT / "research" / "integration" / "intake-log.yaml"
SNAPSHOTS = ROOT / "research" / ".intake" / "snapshots"


class ProducerUnavailable(RuntimeError):
    """The producer's scan directories cannot be read (absent, or blocked by the OS)."""


def producer_root() -> Path:
    return Path(os.environ.get("ARMOND_PRODUCER_ROOT", DEFAULT_PRODUCER))


def scan_files(producer: Path | None = None) -> list[Path]:
    producer = producer or producer_root()
    found: list[Path] = []
    for rel in SCAN_DIRS:
        base = producer / rel
        try:
            entries = list(base.rglob("*"))
        except OSError as exc:
            raise ProducerUnavailable(f"cannot read {base}: {exc}") from exc
        if not base.is_dir():
            raise ProducerUnavailable(f"producer scans not found at {base}")
        found += [p for p in entries if p.is_file() and not p.is_symlink() and p.suffix.lower() in SCAN_SUFFIXES]
    return sorted(found)


class HashCache:
    def __init__(self, path: Path = CACHE) -> None:
        self.path = path
        try:
            self.data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.data = {}
        self.dirty = False

    def sha256(self, file: Path) -> str:
        stat = file.stat()
        key = str(file)
        cached = self.data.get(key)
        if cached and cached["size"] == stat.st_size and cached["mtime_ns"] == stat.st_mtime_ns:
            return cached["sha256"]
        digest = hashlib.sha256()
        with file.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
        value = digest.hexdigest()
        self.data[key] = {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns, "sha256": value}
        self.dirty = True
        return value

    def save(self) -> None:
        if self.dirty:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, sort_keys=True), encoding="utf-8")


def record_groups(producer: Path | None = None) -> dict[str, str]:
    """Filename → the producer's record key, so pages are grouped per record.

    Prefers the v1 evidence index in the pinned handoff snapshot; otherwise reads the
    producer's records manifest by path. Unknown files are absent from the result.
    """
    snapshot = pinned_snapshot()
    if snapshot and (snapshot / "EVIDENCE-INDEX.json").is_file():
        index = json.loads((snapshot / "EVIDENCE-INDEX.json").read_text(encoding="utf-8"))
        return {Path(s["path"]).name: s["record"] for s in index.get("scans") or [] if s.get("record")}
    manifest = (producer or producer_root()) / "research" / "output" / "ledgers" / "records-manifest.json"
    try:
        records = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    groups: dict[str, str] = {}
    for key, record in records.items():
        for page in record.get("pages") or []:
            if isinstance(page, str):
                groups[Path(page).name] = key
    return groups


def pinned_snapshot() -> Path | None:
    """The most recently accepted, pinned handoff snapshot (from ``make intake``), if any."""
    try:
        import yaml

        log = yaml.safe_load(INTAKE_LOG.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError):
        return None
    for entry in reversed(log.get("generations") or []):
        if entry.get("status") == "accepted":
            candidate = SNAPSHOTS / entry["content_digest"]
            return candidate if candidate.is_dir() else None
    return None
