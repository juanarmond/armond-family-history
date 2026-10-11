"""Check that private strings never reach a public surface.

The repository is public (owner decision, 2026-10-11): records naming living people
are held in the gitignored private store, ``private/``. This audit reads the private
list of strings that must never be published — ``private/redaction-terms.txt``, one
per line — and searches every tracked text file and, when built, the Pages output in
``_site/``. With ``--history`` it also counts the commits in all of Git history that
add or remove each string, which scopes a history cleanup.

It never prints a term: hits are reported as the term's line number in the private
list, with the file or commit count. Without a private store there is nothing to
check; ``--strict`` then fails rather than reporting a silent pass.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERMS = ROOT / "private" / "redaction-terms.txt"
SITE = ROOT / "_site"


def load_terms(path: Path) -> list[tuple[int, str]]:
    terms = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        value = line.strip()
        if value and not value.startswith("#"):
            terms.append((number, value))
    return terms


def tracked_files() -> list[Path]:
    output = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout.decode("utf-8")
    return [ROOT / name for name in output.split("\0") if name]


def normalise(text: str) -> str:
    # Lowercase and collapse whitespace, so a phrase still matches when YAML
    # folding has wrapped it across lines.
    return " ".join(text.split()).lower()


def read_text(path: Path) -> str | None:
    try:
        return normalise(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, OSError):
        return None


def term_pattern(term: str) -> re.Pattern[str]:
    # Whole-token match, so a short number never matches inside a checksum.
    return re.compile(r"(?<![0-9a-z])" + re.escape(normalise(term)) + r"(?![0-9a-z])")


def scan(paths: list[Path], terms: list[tuple[int, str]]) -> dict[str, list[int]]:
    patterns = [(number, term_pattern(term)) for number, term in terms]
    hits: dict[str, list[int]] = {}
    for path in paths:
        text = read_text(path)
        if text is None:
            continue
        matched = [number for number, pattern in patterns if pattern.search(text)]
        if matched:
            hits[path.relative_to(ROOT).as_posix()] = matched
    return hits


def history_counts(terms: list[tuple[int, str]]) -> dict[int, int]:
    counts = {}
    for number, term in terms:
        output = subprocess.run(
            ["git", "log", "--all", "--format=%H", "-S", term],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.split()
        counts[number] = len(output)
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--strict", action="store_true", help="fail when there is nothing to check")
    parser.add_argument("--history", action="store_true", help="also count commits in all Git history")
    args = parser.parse_args(argv)

    if not TERMS.is_file():
        print("Privacy audit: no private store (private/redaction-terms.txt) on this machine.")
        return 1 if args.strict else 0
    terms = load_terms(TERMS)
    surfaces = {"tracked files": tracked_files()}
    if SITE.is_dir():
        surfaces["built site (_site/)"] = [p for p in SITE.rglob("*") if p.is_file()]

    failed = False
    for label, paths in surfaces.items():
        hits = scan(paths, terms)
        if hits:
            failed = True
            print(f"FAIL {label}: {len(hits)} file(s) contain private strings")
            for name, numbers in sorted(hits.items()):
                print(f"  {name}: term line(s) {', '.join(map(str, numbers))}")
        else:
            print(f"ok   {label}: none of {len(terms)} private strings in {len(paths)} files")
    if args.history:
        counts = history_counts(terms)
        reachable = {number: count for number, count in counts.items() if count}
        print(f"history: {len(reachable)} of {len(terms)} private strings appear in past commits")
        for number, count in sorted(reachable.items()):
            print(f"  term line {number}: {count} commit(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
