#!/usr/bin/env python3
"""Advisory audit: catch NEWLY-SYNCED drop images that haven't been catalogued or dispositioned.

`drop_page_audit.py` catches MISSING PAGES of an already-catalogued multi-page document, but it
deliberately skips single images — because the wholesale drop (`research/from-retrieval/`) always
holds many legitimately-un-promoted images (namesakes, unconnected-trunk fragments, photos), so a
blanket "uncatalogued single image" flag would cry wolf dozens of times.

This audit avoids that noise by scoping to **new arrivals only**: an image whose mtime is newer
than the repo's last commit (i.e. it landed in a sync AFTER you last worked). For each such image
it reports NEEDS-DECISION unless the image is already resolved — either catalogued (its sha256
matches a source/FAN `digital_file`/`additional_pages`) or given a "completed → <ID>" / "duplicate"
line in `research/from-retrieval-triage-ledger.md`.

The point is the owner rule (see the `feedback-attach-every-doc-naming-a-modelled-person` memory):
a record image that names a modelled person MUST be catalogued — "already proven", "only
corroborates" and "imperfect provenance" are caveats to record inside the source, never reasons to
leave it uncatalogued. Only a byte-identical duplicate or an image naming no modelled person may be
skipped. The flag clears for the cycle once you catalogue each new image or record a resolved
disposition and commit.

Local-only (drop + ledger are gitignored) and advisory; never mutates; exits 0 unless --strict
(then non-zero if any new arrival still needs a decision). If git is unavailable the cutoff falls
back to 0 (every uncatalogued image is considered new).

Usage:
    uv run --frozen python scripts/triage_audit.py [--strict]
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import os
import re
import subprocess

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DROP_DIRS = [
    os.path.join(ROOT, "research", "from-retrieval", "output", "images"),
    os.path.join(ROOT, "research", "from-retrieval", "resources"),
]
LEDGER = os.path.join(ROOT, "research", "from-retrieval-triage-ledger.md")
SOURCE_GLOBS = [
    os.path.join(ROOT, "data", "sources", "*", "*.yaml"),
    os.path.join(ROOT, "data", "fan", "*.yaml"),
]
IMAGE_RE = re.compile(r"\.(jpe?g|png|tiff?|pdf)$", re.IGNORECASE)
PAGE_MARKER_RE = re.compile(r"[-_]p+p?[-_]?\d+(?:[-_]\d+)?(?=\.[^.]+$)", re.IGNORECASE)
RESOLVED_RE = re.compile(r"completed\s*(?:→|->)|duplicate", re.IGNORECASE)


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def base_stem(filename: str) -> str:
    no_ext = re.sub(r"\.[^.]+$", "", filename)
    if PAGE_MARKER_RE.search(filename):
        return PAGE_MARKER_RE.sub("", filename).rsplit(".", 1)[0]
    return no_ext


def normalise(text: str) -> str:
    """Lower-case and collapse the separators that vary between filenames and ledger refs
    (a drop file `ft_3-1-3QHJ-…` vs a ledger `3:1:3QHJ-…`)."""
    return re.sub(r"[:_]", "-", text).lower()


def last_commit_epoch() -> int:
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "log", "-1", "--format=%ct"],
            capture_output=True, text=True, check=True,
        )
        return int(out.stdout.strip())
    except (subprocess.SubprocessError, ValueError, FileNotFoundError):
        return 0


def load_catalogued_shas() -> set[str]:
    shas: set[str] = set()
    for pattern in SOURCE_GLOBS:
        for path in glob.glob(pattern):
            with open(path, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            refs = []
            if isinstance(data.get("digital_file"), dict):
                refs.append(data["digital_file"])
            for extra in data.get("additional_pages") or []:
                if isinstance(extra, dict):
                    refs.append(extra)
            for ref in refs:
                sha = ref.get("sha256")
                if sha:
                    shas.add(sha.lower())
    return shas


def ledger_lines_for(filename: str, ledger_norm_lines: list[str]) -> list[str]:
    keys = {normalise(filename), normalise(base_stem(filename))}
    return [ln for ln in ledger_norm_lines if any(k and k in ln for k in keys)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero if any new arrival still needs a decision")
    args = parser.parse_args()

    drop_images = []
    for d in DROP_DIRS:
        for path in glob.glob(os.path.join(d, "**", "*"), recursive=True):
            if os.path.isfile(path) and IMAGE_RE.search(path):
                drop_images.append(path)

    if not drop_images:
        print("Triage audit: no retrieval-drop images found (research/from-retrieval/). "
              "Nothing to check.")
        return 0

    cutoff = last_commit_epoch()
    catalogued = load_catalogued_shas()
    ledger_norm_lines = []
    if os.path.exists(LEDGER):
        with open(LEDGER, encoding="utf-8") as fh:
            ledger_norm_lines = [normalise(ln) for ln in fh.read().splitlines()]

    needs_decision = []  # (path, reason)
    checked_new = 0
    for path in sorted(drop_images):
        if os.path.getmtime(path) <= cutoff:
            continue  # not a new arrival since the last commit
        checked_new += 1
        if sha256_of(path) in catalogued:
            continue  # catalogued
        lines = ledger_lines_for(os.path.basename(path), ledger_norm_lines)
        if not lines:
            needs_decision.append((path, "no catalogue entry, no triage-ledger disposition"))
        elif not any(RESOLVED_RE.search(ln) for ln in lines):
            needs_decision.append((path, "soft-skip disposition (lead/corroborative/read) — confirm"))

    if needs_decision:
        print("NEEDS DECISION — drop images synced since the last commit that are not yet catalogued")
        print("or resolved (owner rule: a record image naming a modelled person must be catalogued —")
        print("only a byte-identical duplicate or an image naming NO modelled person may be skipped):")
        for path, reason in needs_decision:
            print(f"  {os.path.relpath(path, ROOT)}  — {reason}")
    else:
        print(f"NEEDS DECISION: none — the {checked_new} drop image(s) newer than the last commit "
              "are all catalogued or resolved.")

    return 1 if (args.strict and needs_decision) else 0


if __name__ == "__main__":
    raise SystemExit(main())
