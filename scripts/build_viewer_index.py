#!/usr/bin/env python3
"""Generate the static viewer entity index from canonical YAML filenames."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ENTITY_DIRECTORIES = ("people", "families", "events", "places", "fan")


def build_index(data_root: Path) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for kind in ENTITY_DIRECTORIES:
        directory = data_root / kind
        index[kind] = sorted(path.stem for path in directory.glob("*.yaml")) if directory.exists() else []
    # Sources live in category subfolders (data/sources/<category>/); aggregate
    # them under a single "sources" key for the viewer.
    sources_root = data_root / "sources"
    index["sources"] = (
        sorted(path.stem for path in sources_root.rglob("*.yaml"))
        if sources_root.exists()
        else []
    )
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("family-tree-viewer/entity-index.json"),
    )
    args = parser.parse_args()

    index = build_index(args.data_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output} with {sum(map(len, index.values()))} entities.")


if __name__ == "__main__":
    main()
