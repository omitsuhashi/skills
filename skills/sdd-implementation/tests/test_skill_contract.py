from __future__ import annotations

from pathlib import Path
import re
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"


def read_or_empty(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


class SddImplementationSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = read_or_empty(SKILL)
        cls.openai_text = read_or_empty(OPENAI_YAML)

    def test_frontmatter_has_exact_name_and_trigger_only_description(self) -> None:
        frontmatter = self.skill_text.split("---", 2)[1] if "---" in self.skill_text else ""
        self.assertIn("name: sdd-implementation", frontmatter)
        self.assertIn(
            "description: Use when a human-approved implementation plan is ready "
            "for local execution in the current repository.",
            frontmatter,
        )

    def test_existing_sdd_is_required_and_main_is_coordinator_only(self) -> None:
        self.assertIn(
            "**REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development",
            self.skill_text,
        )
        self.assertIn("Main session is the orchestrator", self.skill_text)
        self.assertIn(
            "Never implement production code, perform task review, or author wiki "
            "content in the main session.",
            self.skill_text,
        )
        for forbidden in ("custom scheduler", "worker packet schema", "runtime snapshot"):
            self.assertIn(forbidden, self.skill_text)

    def test_dispatch_is_isolated_and_scout_is_conditional(self) -> None:
        self.assertIn("Do not inherit the parent conversation.", self.skill_text)
        self.assertIn('fork_turns="none"', self.skill_text)
        self.assertIn("Skip Scout when the plan binds the current tree exactly.", self.skill_text)
        self.assertIn("read-only Scout", self.skill_text)
        self.assertIn("Human makes the authority-bearing decision.", self.skill_text)

    def test_routing_is_abstract_runtime_only_and_complete(self) -> None:
        for role in (
            "orchestrator",
            "Scout",
            "mechanical implementer",
            "integration implementer",
            "high-risk implementer",
            "task reviewer",
            "adjudicator",
            "knowledge closeout worker",
            "final reviewer",
        ):
            self.assertIn(role, self.skill_text)
        for capability in (
            "economical balanced",
            "balanced-to-high",
            "highest available",
        ):
            self.assertIn(capability, self.skill_text)
        self.assertIn(
            "Persist no concrete model name, reasoning effort value, provider, "
            "agent ID, or run-specific routing result.",
            self.skill_text,
        )
        self.assertNotRegex(self.skill_text, re.compile(r"\bgpt-[0-9]"))

    def test_review_is_bounded_to_material_findings(self) -> None:
        for lens in ("requirements fit", "material simplicity", "material current risk"):
            self.assertIn(lens, self.skill_text)
        self.assertIn("concrete simpler alternative", self.skill_text)
        self.assertIn("material impact", self.skill_text)
        self.assertIn(
            "Non-blocking observations never enter the fix loop or block completion.",
            self.skill_text,
        )
        self.assertIn(
            "Do not reduce mechanical validation or required test coverage.",
            self.skill_text,
        )

    def test_knowledge_closeout_precedes_final_review(self) -> None:
        task_review = self.skill_text.index("All implementation tasks and task reviews")
        closeout = self.skill_text.index("Knowledge Closeout Worker")
        final_review = self.skill_text.index("final whole-branch review")
        self.assertLess(task_review, closeout)
        self.assertLess(closeout, final_review)
        for required in (
            "llm-wiki",
            "knowledge/index.md",
            "knowledge/log.md",
            "Japanese",
            "not_applicable",
        ):
            self.assertIn(required, self.skill_text)

    def test_dual_host_and_local_only_boundaries_are_explicit(self) -> None:
        self.assertIn("skills.external_dirs", self.skill_text)
        self.assertIn("BLOCKED", self.skill_text)
        self.assertIn("Do not fall back to another implementation workflow.", self.skill_text)
        self.assertIn(
            "Do not push, create a PR, merge, release, or install live.",
            self.skill_text,
        )

    def test_skill_has_only_the_minimal_resource_shape(self) -> None:
        children = {path.name for path in SKILL_DIR.iterdir()} if SKILL_DIR.is_dir() else set()
        self.assertEqual({"SKILL.md", "agents", "tests"}, children)
        self.assertFalse((SKILL_DIR / "description.md").exists())

    def test_openai_metadata_matches_the_skill(self) -> None:
        self.assertIn('display_name: "SDD Implementation"', self.openai_text)
        self.assertIn(
            'short_description: "Execute approved plans with isolated SDD workers."',
            self.openai_text,
        )
        self.assertIn(
            'default_prompt: "Use $sdd-implementation to execute this approved '
            'implementation plan through local completion."',
            self.openai_text,
        )


if __name__ == "__main__":
    unittest.main()
