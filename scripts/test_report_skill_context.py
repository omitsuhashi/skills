from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

from validate_skill_architecture import DEFAULT_POLICY_PATH, REQUIRED_FAMILY_ID, load_policy


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


def loop_skill_names() -> set[str]:
    policy = load_policy(DEFAULT_POLICY_PATH)
    families = policy["families"]
    assert isinstance(families, dict)
    family = families[REQUIRED_FAMILY_ID]
    assert isinstance(family, dict)
    return set(family["user_facing_skills"])


class SkillContextReportTests(unittest.TestCase):
    def test_json_report_includes_workflow_complexity_summary(self) -> None:
        result = run_script(REPORT_SKILL_CONTEXT, "--all", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        complexity = payload["workflow_complexity"]
        loop_operation_count = sum(
            len(skill["operations"])
            for skill in payload["skills"]
            if skill["skill"] in loop_skill_names()
        )

        required_keys = {
            "operation_count": int,
            "gate_count": int,
            "gate_breakdown": list,
            "runtime_artifact_count": int,
            "runtime_artifacts": list,
            "worker_context_required": bool,
            "review_cycle_required": bool,
            "remote_delivery_present": bool,
            "advisory_only": bool,
            "warnings": list,
        }
        for key, expected_type in required_keys.items():
            self.assertIn(key, complexity)
            self.assertIsInstance(complexity[key], expected_type)

        self.assertEqual(complexity["operation_count"], loop_operation_count)
        self.assertEqual(complexity["gate_count"], len(complexity["gate_breakdown"]))
        self.assertGreaterEqual(complexity["runtime_artifact_count"], 1)
        self.assertTrue(complexity["worker_context_required"])
        self.assertTrue(complexity["review_cycle_required"])
        self.assertTrue(complexity["remote_delivery_present"])
        self.assertTrue(complexity["advisory_only"])

    def test_json_report_includes_family_context_compaction_policy(self) -> None:
        result = run_script(REPORT_SKILL_CONTEXT, "--all", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        complexity = json.loads(result.stdout)["workflow_complexity"]
        self.assertEqual(
            complexity["context_compaction_policy"],
            {
                "soft_trigger_percent": 65,
                "hard_stop_percent": 75,
                "mandatory_handoff_compaction": 1,
            },
        )

    def test_text_report_keeps_complexity_advisory_brief(self) -> None:
        result = run_script(REPORT_SKILL_CONTEXT, "--all")

        self.assertEqual(result.returncode, 0, result.stderr)
        advisory_lines = [line for line in result.stdout.splitlines() if line.startswith("Workflow complexity:")]

        self.assertLessEqual(len(advisory_lines), 1)
        self.assertTrue(advisory_lines)
        self.assertIn("review cycle", advisory_lines[0])
        self.assertNotIn("runtime artifact count", result.stdout)

    def test_non_loop_skill_report_does_not_emit_workflow_advisory(self) -> None:
        text_result = run_script(REPORT_SKILL_CONTEXT, "--skill", "skills/llm-wiki")
        json_result = run_script(REPORT_SKILL_CONTEXT, "--skill", "skills/llm-wiki", "--json")

        self.assertEqual(text_result.returncode, 0, text_result.stderr)
        self.assertEqual(json_result.returncode, 0, json_result.stderr)
        self.assertNotIn("Workflow complexity:", text_result.stdout)

        complexity = json.loads(json_result.stdout)["workflow_complexity"]
        self.assertEqual(complexity["skill_count"], 0)
        self.assertEqual(complexity["operation_count"], 0)
        self.assertFalse(complexity["worker_context_required"])
        self.assertEqual(complexity["warnings"], [])

    def test_context_validator_remains_read_set_budget_only(self) -> None:
        result = run_script(VALIDATE_SKILL_CONTEXT, "--all")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("complexity", result.stdout.lower())
        self.assertNotIn("complexity", result.stderr.lower())

    def test_session_pressure_json_marks_soft_compaction_required(self) -> None:
        result = run_script(REPORT_SKILL_CONTEXT, "--all", "--json", "--session-pressure-percent", "65")

        self.assertEqual(result.returncode, 0, result.stderr)
        session_context = json.loads(result.stdout)["session_context"]

        self.assertTrue(session_context["advisory_only"])
        self.assertEqual(session_context["source"], "operator_supplied")
        self.assertEqual(session_context["session_pressure_percent"], 65)
        self.assertTrue(session_context["compaction_required"])
        self.assertFalse(session_context["hard_stop_required"])

    def test_session_pressure_text_adds_single_brief_advisory_line(self) -> None:
        without_pressure = run_script(REPORT_SKILL_CONTEXT, "--all")
        with_pressure = run_script(REPORT_SKILL_CONTEXT, "--all", "--session-pressure-percent", "65")

        self.assertEqual(without_pressure.returncode, 0, without_pressure.stderr)
        self.assertEqual(with_pressure.returncode, 0, with_pressure.stderr)

        added_lines = [
            line
            for line in with_pressure.stdout.splitlines()
            if line not in without_pressure.stdout.splitlines()
        ]
        self.assertEqual(len(added_lines), 1)
        self.assertTrue(added_lines[0].startswith("Session context:"))
        self.assertIn("compaction checkpoint required", added_lines[0])

    def test_session_pressure_hard_stop_warning_fails_on_warning(self) -> None:
        result = run_script(
            REPORT_SKILL_CONTEXT,
            "--all",
            "--session-pressure-percent",
            "75",
            "--fail-on-warning",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("WARNING:", result.stderr)
        self.assertIn("hard stop", result.stderr)
        self.assertIn("Session context:", result.stdout)

    def test_session_pressure_advisory_is_not_checkpoint_or_overlay_replacement(self) -> None:
        result = run_script(REPORT_SKILL_CONTEXT, "--all", "--json", "--session-pressure-percent", "65")

        self.assertEqual(result.returncode, 0, result.stderr)
        session_context = json.loads(result.stdout)["session_context"]

        self.assertTrue(session_context["requires_phase_checkpoint"])
        self.assertTrue(session_context["requires_conditional_overlay"])
        self.assertEqual(
            session_context["not_a_substitute_for"],
            ["phase checkpoint", "conditional overlay"],
        )

    def test_session_pressure_advisory_is_limited_to_loop_skills(self) -> None:
        text_result = run_script(REPORT_SKILL_CONTEXT, "--skill", "skills/llm-wiki", "--session-pressure-percent", "75")
        json_result = run_script(
            REPORT_SKILL_CONTEXT,
            "--skill",
            "skills/llm-wiki",
            "--json",
            "--session-pressure-percent",
            "75",
        )

        self.assertEqual(text_result.returncode, 0, text_result.stderr)
        self.assertEqual(json_result.returncode, 0, json_result.stderr)
        self.assertNotIn("Session context:", text_result.stdout)
        self.assertNotIn("session_context", json.loads(json_result.stdout))

    def test_context_validator_does_not_accept_session_pressure_flag(self) -> None:
        result = run_script(VALIDATE_SKILL_CONTEXT, "--all", "--session-pressure-percent", "65")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments: --session-pressure-percent 65", result.stderr)


if __name__ == "__main__":
    unittest.main()
