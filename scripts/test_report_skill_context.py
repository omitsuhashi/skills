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
    def test_json_report_includes_workflow_complexity_summary(self) -> None:
        result = run_script(REPORT_SKILL_CONTEXT, "--all", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        complexity = payload["workflow_complexity"]

        self.assertEqual(complexity["operation_count"], 16)
        self.assertEqual(complexity["gate_count"], 5)
        self.assertGreaterEqual(complexity["runtime_artifact_count"], 1)
        self.assertTrue(complexity["worker_context_required"])
        self.assertTrue(complexity["review_cycle_required"])
        self.assertTrue(complexity["remote_delivery_present"])
        self.assertTrue(complexity["advisory_only"])
        self.assertIsInstance(complexity["warnings"], list)

    def test_text_report_keeps_complexity_advisory_brief(self) -> None:
        result = run_script(REPORT_SKILL_CONTEXT, "--all")

        self.assertEqual(result.returncode, 0, result.stderr)
        advisory_lines = [line for line in result.stdout.splitlines() if line.startswith("Workflow complexity:")]

        self.assertLessEqual(len(advisory_lines), 1)
        self.assertTrue(advisory_lines)
        self.assertIn("review cycle", advisory_lines[0])
        self.assertNotIn("runtime artifact count", result.stdout)

    def test_context_validator_remains_read_set_budget_only(self) -> None:
        result = run_script(VALIDATE_SKILL_CONTEXT, "--all")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("complexity", result.stdout.lower())
        self.assertNotIn("complexity", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
