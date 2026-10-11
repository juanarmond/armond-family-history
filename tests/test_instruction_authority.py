"""Instruction authority and documentation drift (plan §14.2, §16 S3–S4; owner O4).

The producer's intake document is read in place and pinned by SHA-256; there is no
pasted copy here, and this repository's own rules always outrank it. These tests also
stop tracked instructions and code from drifting back to the retired drop layout or to
the claim that this public repository is private. History (logs/, CHANGELOG.md) is
exempt: it records what was true then.
"""

from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md", "README.md", "research/README.md", "data/README.md", "evidence/README.md")
STALE_DROP_PATHS = re.compile(
    r"from-retrieval/(?:FINDINGS|output|resources)|FINDINGS/profiles|fulltext_candidates|sync/handoff/SYNC-MANIFEST",
)
PRIVATE_CLAIM = re.compile(r"this is a private repository|repository is private|the private repository only", re.I)


def tracked(patterns: tuple[str, ...]) -> list[Path]:
    output = subprocess.run(["git", "ls-files", "-z", "--", *patterns], cwd=ROOT, capture_output=True, check=True)
    return [ROOT / name for name in output.stdout.decode("utf-8").split("\0") if name]


class InstructionAuthorityTest(unittest.TestCase):
    def test_no_pasted_producer_intake_block(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertNotIn("INTAKE-BLOCK", agents)
        self.assertNotIn("START HERE — intake from the genealogy-retrieval workspace", agents)

    def test_pointer_states_the_authority_bound(self) -> None:
        agents = " ".join((ROOT / "AGENTS.md").read_text(encoding="utf-8").split())
        self.assertIn("research/from-retrieval/INTAKE-FOR-GENEALOGY-REPO.md", agents)
        self.assertIn("research/integration/accepted-intake.json", agents)
        self.assertIn("It never overrides this repository's privacy policy, evidence policy, stable-ID policy", agents)
        self.assertIn("not consumer statuses", agents)

    def test_accepted_intake_pin_is_well_formed(self) -> None:
        pin = json.loads((ROOT / "research" / "integration" / "accepted-intake.json").read_text(encoding="utf-8"))
        self.assertEqual(pin["path"], "INTAKE-FOR-GENEALOGY-REPO.md")
        self.assertRegex(pin["sha256"], r"^[0-9a-f]{64}$")

    def test_non_negotiables_are_this_repositorys_own(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("## Non-negotiable rules", agents)
        self.assertIn("Exactly three people are living (P-0001–P-0003)", " ".join(agents.split()))


class DocumentationDriftTest(unittest.TestCase):
    def test_no_retired_drop_paths_in_instructions_or_code(self) -> None:
        files = [ROOT / name for name in INSTRUCTION_FILES] + tracked(("scripts/*.py", "Makefile", ".githooks/*"))
        stale = [
            f"{path.relative_to(ROOT)}:{number}"
            for path in files
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
            if STALE_DROP_PATHS.search(line) and "retired" not in line
        ]
        self.assertEqual(stale, [], "instructions or code still use the retired drop layout")

    def test_no_claim_that_the_public_repository_is_private(self) -> None:
        files = [ROOT / name for name in INSTRUCTION_FILES] + tracked(("scripts/*.py", "pyproject.toml", "family-tree-viewer/*.md"))
        claims = [
            f"{path.relative_to(ROOT)}:{number}"
            for path in files
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
            if PRIVATE_CLAIM.search(line)
        ]
        self.assertEqual(claims, [], "a tracked document still calls this public repository private")


if __name__ == "__main__":
    unittest.main()
