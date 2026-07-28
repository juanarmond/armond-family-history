from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github/workflows/check.yml"
CHECKOUT_SHA = "de0fac2e4500dabe0009e67214ff5f5447ce83dd"
SETUP_UV_SHA = "08807647e7069bb48b6ef5acd8ec9567f424441b"


class WorkflowTests(unittest.TestCase):
    def load_workflow(self) -> dict[str, Any]:
        document = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
        self.assertIsInstance(document, dict)
        return document

    def test_health_workflow_is_read_only_and_cancellable(self) -> None:
        workflow = self.load_workflow()
        self.assertEqual({"contents": "read"}, workflow["permissions"])
        self.assertEqual(True, workflow["concurrency"]["cancel-in-progress"])
        self.assertIn("push", workflow["on"])
        self.assertIn("pull_request", workflow["on"])

    def test_health_workflow_pins_actions_and_matches_local_check(self) -> None:
        workflow = self.load_workflow()
        job = workflow["jobs"]["check"]
        self.assertEqual(["3.11", "3.13"], job["strategy"]["matrix"]["python-version"])
        steps = job["steps"]
        self.assertEqual(f"actions/checkout@{CHECKOUT_SHA}", steps[0]["uses"])
        self.assertEqual(False, steps[0]["with"]["persist-credentials"])
        self.assertEqual(f"astral-sh/setup-uv@{SETUP_UV_SHA}", steps[1]["uses"])
        self.assertEqual("0.11.32", steps[1]["with"]["version"])
        self.assertEqual("uv run --frozen make check", steps[2]["run"])


if __name__ == "__main__":
    unittest.main()
