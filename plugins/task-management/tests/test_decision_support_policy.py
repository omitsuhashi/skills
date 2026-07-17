from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL = REPO_ROOT / "plugins/task-management/skills/task-management/SKILL.md"
POLICY = REPO_ROOT / "plugins/task-management/skills/task-management/references/decision-support-policy.md"


class DecisionSupportPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = SKILL.read_text(encoding="utf-8")
        cls.policy_text = POLICY.read_text(encoding="utf-8")

    def test_skill_routes_decision_sensitive_intake_to_policy(self) -> None:
        self.assertIn("references/decision-support-policy.md", self.skill_text)
        self.assertIn("Before composing a new TaskDraft", self.skill_text)

    def test_policy_skips_mechanical_operations(self) -> None:
        for operation in (
            "Task snapshot read or search",
            "Backend or destination routing",
            "Adapter preflight or dispatch preview",
            "Simple status update or maintenance",
        ):
            self.assertIn(f"| {operation} | none |", self.policy_text)

    def test_policy_uses_deep_or_review_for_decision_sensitive_work(self) -> None:
        for row in (
            "| Ambiguous task intake | deep |",
            "| Prioritization or daily planning | deep |",
            "| Continue, stop, defer, or delegate | deep |",
            "| Periodic or post-action review | review |",
        ):
            self.assertIn(row, self.policy_text)

    def test_intake_gate_keeps_clear_execution_lightweight(self) -> None:
        self.assertIn("Is this ready for execution or is a decision unresolved?", self.policy_text)
        self.assertIn("If all three checks are clear, continue without displaying decision scaffolding.", self.policy_text)

    def test_unavailable_companion_preserves_mechanical_work_and_stops_material_decisions(self) -> None:
        self.assertIn("Mechanical reads, routing, and clear task intake continue.", self.policy_text)
        self.assertIn("Do not claim that decision support ran.", self.policy_text)
        self.assertIn("Stop before ordinary TaskDraft creation for severe irreversible harm.", self.policy_text)

    def test_policy_preserves_existing_approval_boundary_without_copying_core_method(self) -> None:
        self.assertIn("Adapter Dispatch Review remains required", self.policy_text)
        self.assertNotIn("1. `purpose`", self.policy_text)
        self.assertIn("Stop before adapter dispatch", self.skill_text)


if __name__ == "__main__":
    unittest.main()
