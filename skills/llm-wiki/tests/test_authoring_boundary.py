from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
REPORT_CONTEXT = REPO_ROOT / "scripts" / "report_skill_context.py"


def read(name: str) -> str:
    return (SKILL_DIR / name).read_text(encoding="utf-8")


def report_operation(name: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(REPORT_CONTEXT), "--skill", "skills/llm-wiki", "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    payload = json.loads(result.stdout)
    return next(
        operation
        for operation in payload["skills"][0]["operations"]
        if operation["operation"] == name
    )


class AuthoringBoundaryTests(unittest.TestCase):
    def test_public_contract_declares_portable_handoff_and_fail_closed_boundary(self) -> None:
        skill = read("SKILL.md")

        for heading in ("## Inputs", "## Outputs", "## Required Capabilities"):
            self.assertIn(heading, skill)
        self.assertIn("existing skill discovery", skill)
        self.assertIn("`BLOCKED`", skill)
        self.assertNotIn("fallback renderer", skill.casefold())

    def test_context_operations_keep_only_structural_four_file_read_sets(self) -> None:
        operation = report_operation("single-root.ingest")

        self.assertEqual(len(operation["files"]), 4)
        self.assertNotIn("obsidian-markdown", "\n".join(operation["files"]))


if __name__ == "__main__":
    unittest.main()
