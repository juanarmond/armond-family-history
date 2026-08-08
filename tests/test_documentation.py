from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ROOT_MARKDOWN = {
    "AGENTS.md",
    "CHANGELOG.md",
    "CLAUDE.md",  # Claude Code loader; imports AGENTS.md (single source of truth)
    "README.md",
    "STATUS.md",
}
REQUIRED_STATUS_HEADINGS = {
    "## Current objective",
    "## Next steps",
    "## Current blockers and dependencies",
    "## Repository snapshot",
    "## Research snapshot",
    "## Material unresolved conflicts",
    "## Strategic research priorities",
    "## Engineering state",
}
OBSOLETE_STATUS_HEADINGS = {
    "## Repository status",
    "## Subject",
    "## Parents",
    "## Paternal grandparents",
    "## Maternal grandparents",
    "## Great-grandparents and earlier lines",
    "## Prioritised backlog",
    "## Definition of done for a research task",
}
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class DocumentationTests(unittest.TestCase):
    def test_root_markdown_has_one_canonical_file_per_concern(self) -> None:
        root_markdown = {path.name for path in PROJECT_ROOT.glob("*.md")}
        self.assertEqual(CANONICAL_ROOT_MARKDOWN, root_markdown)

    def test_relative_markdown_links_resolve(self) -> None:
        broken: list[str] = []
        for document in PROJECT_ROOT.rglob("*.md"):
            if ".git" in document.parts or ".venv" in document.parts:
                continue
            # skip gitignored retrieval-agent working area (overwritten on re-sync)
            if "from-retrieval" in document.parts:
                continue
            for target in MARKDOWN_LINK.findall(
                document.read_text(encoding="utf-8")
            ):
                if target.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                relative_target = target.split("#", 1)[0]
                if relative_target and not (document.parent / relative_target).exists():
                    broken.append(f"{document.relative_to(PROJECT_ROOT)} -> {target}")

        self.assertEqual([], broken)

    def test_status_remains_a_current_snapshot(self) -> None:
        status = (PROJECT_ROOT / "STATUS.md").read_text(encoding="utf-8")
        headings = {
            line
            for line in status.splitlines()
            if line.startswith("## ")
        }

        self.assertTrue(REQUIRED_STATUS_HEADINGS.issubset(headings))
        self.assertTrue(OBSOLETE_STATUS_HEADINGS.isdisjoint(headings))
        self.assertLessEqual(
            len(status.splitlines()),
            200,
            "STATUS.md is accumulating history or record-level detail",
        )


if __name__ == "__main__":
    unittest.main()
