from __future__ import annotations

import re
from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
CORE = SKILL_DIR / "references" / "core.md"
MODES = SKILL_DIR / "references" / "modes.md"
CONTRACTS = SKILL_DIR / "references" / "decision-contracts.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"


class DecideInOrderSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = SKILL.read_text(encoding="utf-8")
        cls.core_text = CORE.read_text(encoding="utf-8")
        cls.modes_text = MODES.read_text(encoding="utf-8")
        cls.contracts_text = CONTRACTS.read_text(encoding="utf-8")

    def test_frontmatter_names_skill_and_covers_primary_triggers(self) -> None:
        frontmatter = self.skill_text.split("---", 2)[1]
        self.assertIn("name: decide-in-order", frontmatter)
        for trigger in (
            "prioritization",
            "daily planning",
            "research framing",
            "continue",
            "sunk-cost",
            "review",
        ):
            self.assertIn(trigger, frontmatter)

    def test_portable_skill_uses_the_standard_entrypoint(self) -> None:
        frontmatter = self.skill_text.split("---", 2)[1]
        self.assertIn("name: decide-in-order", frontmatter)
        self.assertIn("description:", frontmatter)
        self.assertFalse((SKILL_DIR / "description.md").exists())
        self.assertTrue(OPENAI_YAML.is_file())

    def test_entrypoint_routes_to_each_reference_without_copying_the_numbered_order(self) -> None:
        for reference in (
            "references/core.md",
            "references/modes.md",
            "references/decision-contracts.md",
        ):
            self.assertIn(reference, self.skill_text)
        self.assertNotIn("1. `purpose`", self.skill_text)

    def test_core_keeps_the_canonical_order(self) -> None:
        fields = (
            "purpose",
            "must_protect",
            "acceptable_loss",
            "core_question",
            "decision_order",
            "constraints",
            "method",
            "risk",
            "review",
        )
        positions = [self.core_text.index(f"`{field}`") for field in fields]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("## Prohibited Reversals", self.core_text)

    def test_modes_keep_clear_execution_light_and_deep_questions_singular(self) -> None:
        for heading in ("## Light Handling", "## Deep Handling", "## Review Handling"):
            self.assertIn(heading, self.modes_text)
        self.assertIn("Ask at most one material question per turn.", self.modes_text)
        self.assertIn("Do not show a skill-shaped block", self.modes_text)

    def test_contracts_keep_working_state_sparse_and_record_storage_caller_owned(self) -> None:
        text = self.contracts_text
        self.assertIn("DecisionFrame", text)
        self.assertIn("Do not serialize it by default", text)
        self.assertIn("DecisionGuidance is a rendering rule", text)
        for field in (
            "schema_version",
            "decision_status",
            "purpose",
            "core_question",
            "decision",
            "must_protect",
            "acceptable_loss",
            "next_action",
            "review",
        ):
            self.assertRegex(text, rf"(?m)^  {re.escape(field)}:")
        self.assertIn("The caller owns identifiers, timestamps, storage, and writes.", text)

    def test_skill_has_only_the_planned_resource_shape(self) -> None:
        self.assertTrue(OPENAI_YAML.is_file())
        self.assertFalse((SKILL_DIR / "README.md").exists())
        self.assertFalse((SKILL_DIR / "scripts").exists())
        self.assertFalse((SKILL_DIR / "assets").exists())


if __name__ == "__main__":
    unittest.main()
