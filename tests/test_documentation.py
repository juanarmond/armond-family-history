from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ROOT_MARKDOWN = {
    "AGENTS.md",
    "CHANGELOG.md",
    "README.md",
    "STATUS.md",
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
            for target in MARKDOWN_LINK.findall(
                document.read_text(encoding="utf-8")
            ):
                if target.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                relative_target = target.split("#", 1)[0]
                if relative_target and not (document.parent / relative_target).exists():
                    broken.append(f"{document.relative_to(PROJECT_ROOT)} -> {target}")

        self.assertEqual([], broken)


if __name__ == "__main__":
    unittest.main()
