from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_SKILL_CONTEXT = REPO_ROOT / "scripts" / "report_skill_context.py"
VALIDATE_SKILL_CONTEXT = REPO_ROOT / "scripts" / "validate_skill_context.py"


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


class SkillContextReportTests(unittest.TestCase):
    def test_all_context_contracts_are_discovered_without_architecture_coupling(self) -> None:
        result = run_script(REPORT_SKILL_CONTEXT, "--all", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(["llm-wiki"], [skill["skill"] for skill in payload["skills"]])
        self.assertNotIn("workflow_complexity", payload)
        self.assertNotIn("session_context", payload)
        self.assertNotIn("baseline_path", payload)

    def test_context_validator_remains_read_set_budget_only(self) -> None:
        result = run_script(VALIDATE_SKILL_CONTEXT, "--all")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("complexity", result.stdout.lower())
        self.assertNotIn("complexity", result.stderr.lower())



if __name__ == "__main__":
    unittest.main()
