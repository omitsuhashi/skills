from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "skill-architecture.yml"
LEGACY_GRILL_SKILL = "-".join(("grill", "to", "pr", "loop"))
LEGACY_ISSUE_SKILL = "-".join(("issue", "implementation", "loop"))
TASK_MANAGEMENT_TEST = (
    REPO_ROOT
    / "skills"
    / "task-management"
    / "tests"
    / "test_task_management_contract.py"
)


class SkillCiWorkflowTests(unittest.TestCase):
    def test_python_matrix_runs_standalone_skill_contracts(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('python-version:\n          - "3.9"\n          - "3.12"', text)
        self.assertIn("Run decide-in-order tests", text)
        self.assertIn(
            "python3 -m unittest discover -s skills/decide-in-order/tests", text
        )
        self.assertIn("Run task-management tests", text)
        self.assertIn(
            "python3 -m unittest discover -s skills/task-management/tests", text
        )
        self.assertIn("Run sdd-implementation tests", text)
        self.assertIn(
            "python3 -m unittest discover -s skills/sdd-implementation/tests",
            text,
        )
        self.assertNotIn(f"Run {LEGACY_GRILL_SKILL} tests", text)
        self.assertNotIn(f"Run {LEGACY_ISSUE_SKILL} tests", text)
        self.assertNotIn("plugins/task-management", text)

    def test_task_management_contract_is_host_neutral(self) -> None:
        text = TASK_MANAGEMENT_TEST.read_text(encoding="utf-8")
        self.assertIn("test_skill_has_no_host_specific_or_runtime_surface", text)
        self.assertIn("test_capability_and_partial_failures_are_fail_closed", text)

    def test_workflow_omits_repository_compatibility_entrypoints(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Test skill authoring guidance", text)
        self.assertIn("scripts/test_skill_authoring_guidance.py", text)
        self.assertIn("Test skill CI workflow contract", text)
        self.assertIn("scripts/test_skill_ci_workflow.py", text)
        self.assertNotIn("Test repository compatibility validator", text)
        self.assertNotIn("scripts/test_validate_repository_compatibility.py", text)
        self.assertNotIn("Validate repository compatibility", text)
        self.assertNotIn("scripts/validate_repository_compatibility.py", text)


if __name__ == "__main__":
    unittest.main()
