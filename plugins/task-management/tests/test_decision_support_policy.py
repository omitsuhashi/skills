from __future__ import annotations

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL = REPO_ROOT / "plugins/task-management/skills/task-management/SKILL.md"
POLICY = REPO_ROOT / "plugins/task-management/skills/task-management/references/decision-support-policy.md"
CORE = REPO_ROOT / "skills/decide-in-order/references/core.md"

CANONICAL_METHOD_ROW = re.compile(r"^(\d+)\. (`([^`]+)`: .+)$", re.MULTILINE)


class DecisionSupportPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = SKILL.read_text(encoding="utf-8")
        cls.policy_text = POLICY.read_text(encoding="utf-8")
        cls.core_text = CORE.read_text(encoding="utf-8")
        cls.canonical_method_rows = CANONICAL_METHOD_ROW.findall(cls.core_text)

    def test_skill_routes_decision_sensitive_intake_to_policy(self) -> None:
        self.assertIn("references/decision-support-policy.md", self.skill_text)
        self.assertIn("Before composing a new TaskDraft", self.skill_text)
        self.assertIn(
            "Do not use it for task reads, backend routing, or adapter previews;",
            self.skill_text,
        )
        self.assertIn(
            "skip decision support for current-state reads, routing, and adapter previews.",
            self.skill_text,
        )

    def test_policy_skips_mechanical_operations(self) -> None:
        for operation in (
            "Task snapshot read or search",
            "Backend or destination routing",
            "Adapter preflight or dispatch preview",
            "Simple status update or maintenance",
        ):
            self.assertIn(f"| {operation} | none |", self.policy_text)
        self.assertIn("| Clear execution task intake | light |", self.policy_text)

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
        self.assertIn(
            "Use `$decide-in-order` as an optional companion when it is discoverable.",
            self.policy_text,
        )
        self.assertIn("Mechanical reads, routing, and clear task intake continue.", self.policy_text)
        self.assertIn("Do not claim that decision support ran.", self.policy_text)
        self.assertIn("Stop before ordinary TaskDraft creation for severe irreversible harm.", self.policy_text)

    def test_policy_preserves_existing_approval_boundary_without_copying_core_method(self) -> None:
        self.assertEqual(
            list(range(1, 10)),
            [int(number) for number, _body, _field in self.canonical_method_rows],
        )
        for number, body, _field in self.canonical_method_rows:
            with self.subTest(canonical_method_row=number):
                self.assertNotIn(f"{number}. {body}", self.policy_text)
                self.assertNotIn(body, self.policy_text)

        ordered_fields = [re.escape(field) for _number, _body, field in self.canonical_method_rows]
        complete_sequence = re.compile(
            r"\b" + r"\b.*?\b".join(ordered_fields) + r"\b",
            re.DOTALL,
        )
        self.assertIsNone(complete_sequence.search(self.policy_text))

        for retained_clause in (
            "call `task_query(destination_ref, query)`",
            "backend-neutral TaskDraft and operation envelope",
            "Call `task_preflight(interface_version=2, operation=...)`",
            "Use `decision: approved` only after explicit human approval",
            "Call `task_apply` with the exact preview and receipt",
        ):
            with self.subTest(retained_default_flow_clause=retained_clause):
                self.assertIn(retained_clause, self.skill_text)

        self.assertIn("Adapter Dispatch Review remains required", self.policy_text)
        self.assertIn("requires human approval or a new preflight", self.skill_text)


if __name__ == "__main__":
    unittest.main()
