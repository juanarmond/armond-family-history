from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
JS_TEST_DIR = PROJECT_ROOT / "tests" / "js"


class DataLoaderJsTests(unittest.TestCase):
    """Run the viewer's JavaScript projection tests through Node.

    The projection logic (marriage matching, spouse pairing, evidence-path
    gating, conflict detection) lives in JavaScript, so it is tested there.
    Node is optional: contributors and CI without it skip cleanly, while a
    local `make check` with Node installed exercises the real code.
    """

    def test_data_loader_projection_under_node(self) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not installed; skipping JavaScript unit tests")

        test_files = sorted(str(path) for path in JS_TEST_DIR.glob("*.test.mjs"))
        if not test_files:
            self.skipTest("no JavaScript test files found")

        result = subprocess.run(
            [node, "--test", *test_files],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode != 0:
            self.fail(
                "Node data-loader tests failed:\n"
                f"{result.stdout}\n{result.stderr}"
            )


if __name__ == "__main__":
    unittest.main()
