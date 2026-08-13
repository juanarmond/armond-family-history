#!/usr/bin/env python3
"""Advisory audit: catch catalogued documents that are missing pages still in the drop.

`validate_data.py` already errors on an `evidence/<id>-*` page file that a source or
FAN does not reference (a page copied into the repo but not linked). What it CANNOT
see is a page that was never promoted at all — still sitting in the retrieval drop
(`research/from-retrieval/`, which is gitignored). That is the gap behind "the deed
has three pages but only one shows".

This heuristic closes it by **sha256**, which is robust to file renames: it groups the
drop's image sets by base name (stripping a trailing page marker like `-p2`, `-pp2-3`,
`-page3`), hashes every image, and compares against the sha256 set that the catalogued
sources/FANs actually reference (`digital_file` + `additional_pages`). For any drop set
where at least one page is already catalogued (so the document IS in the repo) but a
sibling page is NOT, it flags the missing page(s) and the owning entity — a page of a
known document that was never linked or transcribed.

It also lists multi-page drop sets where NO page is catalogued yet (promotion
candidates for the value gate — informational, not a defect).

Local-only (the drop is gitignored, so this cannot run in CI) and advisory; it never
mutates anything and exits 0 unless --strict is given (then non-zero if any catalogued
document is missing a page).

Usage:
    uv run --frozen python scripts/drop_page_audit.py [--strict]
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DROP_DIRS = [
    os.path.join(ROOT, "research", "from-retrieval", "output", "images"),
    os.path.join(ROOT, "research", "from-retrieval", "resources"),
]
SOURCE_GLOBS = [
    os.path.join(ROOT, "data", "sources", "*", "*.yaml"),
    os.path.join(ROOT, "data", "fan", "*.yaml"),
]
IMAGE_RE = re.compile(r"\.(jpe?g|png|tiff?)$", re.IGNORECASE)
# Trailing page markers: -p1, -p2, -pp2-3, -page3, -p1-2, _p1 ...
PAGE_MARKER_RE = re.compile(r"[-_]p+p?[-_]?\d+(?:[-_]\d+)?(?=\.[^.]+$)", re.IGNORECASE)


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def base_name(filename: str) -> str:
    stem = re.sub(r"\.[^.]+$", "", filename)
    return PAGE_MARKER_RE.sub("", filename).rsplit(".", 1)[0] if PAGE_MARKER_RE.search(filename) else stem


def load_catalogue() -> tuple[dict[str, str], dict[str, int]]:
    """Return (sha256 -> owning entity id) and (entity id -> its total linked page count),
    from every source/FAN digital_file + additional_pages."""
    shas: dict[str, str] = {}
    page_counts: dict[str, int] = {}
    for pattern in SOURCE_GLOBS:
        for path in glob.glob(pattern):
            with open(path, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            eid = data.get("id", os.path.basename(path))
            refs = []
            if isinstance(data.get("digital_file"), dict):
                refs.append(data["digital_file"])
            for extra in data.get("additional_pages") or []:
                if isinstance(extra, dict):
                    refs.append(extra)
            page_counts[eid] = page_counts.get(eid, 0) + len(refs)
            for ref in refs:
                sha = ref.get("sha256")
                if sha:
                    shas[sha.lower()] = eid
    return shas, page_counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero if a catalogued document is missing a page")
    args = parser.parse_args()

    drop_images = []
    for d in DROP_DIRS:
        for path in glob.glob(os.path.join(d, "**", "*"), recursive=True):
            if os.path.isfile(path) and IMAGE_RE.search(path):
                drop_images.append(path)

    if not drop_images:
        print("Drop-page audit: no retrieval-drop images found (research/from-retrieval/). "
              "Nothing to check.")
        return 0

    catalogued, page_counts = load_catalogue()

    # Group drop images by base name.
    sets: dict[str, list[str]] = {}
    for path in drop_images:
        sets.setdefault(base_name(os.path.basename(path)), []).append(path)

    missing_pages = []   # (entity, base, [uncatalogued page paths], catalogued_count, total)
    uncatalogued_sets = []  # (base, count)
    for base, paths in sorted(sets.items()):
        if len(paths) < 2:
            continue  # single image: cannot detect a "missing sibling" this way
        hashed = [(p, sha256_of(p)) for p in sorted(paths)]
        cat = [(p, s) for p, s in hashed if s in catalogued]
        uncat = [p for p, s in hashed if s not in catalogued]
        if cat and uncat:
            entity = catalogued[cat[0][1]]
            # If the owning document already links at least as many pages as the drop set, treat it
            # as complete — the unmatched drop images are just lower-quality copies of pages the
            # source holds in a better scan (different bytes → no sha match), not missing pages.
            if page_counts.get(entity, len(cat)) >= len(paths):
                continue
            missing_pages.append((entity, base, uncat, len(cat), len(paths)))
        elif not cat:
            uncatalogued_sets.append((base, len(paths)))

    if missing_pages:
        print("MISSING PAGES — a catalogued document is missing pages that are still in the drop:")
        for entity, base, uncat, ncat, total in missing_pages:
            print(f"  {entity}: {ncat}/{total} pages catalogued — add and transcribe:")
            for p in uncat:
                print(f"      {os.path.relpath(p, ROOT)}")
    else:
        print("MISSING PAGES: none — every catalogued multi-page document has all its drop pages linked.")

    if uncatalogued_sets:
        print("\nUncatalogued multi-page sets (value-gate candidates — informational, not a defect):")
        for base, count in uncatalogued_sets:
            print(f"  {base}  ({count} pages)")

    return 1 if (args.strict and missing_pages) else 0


if __name__ == "__main__":
    raise SystemExit(main())
