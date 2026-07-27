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

    def test_frontmatter_triggers_for_the_full_repository_change_lifecycle(self) -> None:
        frontmatter = self.skill_text.split("---", 2)[1] if "---" in self.skill_text else ""
        self.assertIn("name: sdd-implementation", frontmatter)
        self.assertIn(
            "description: Use when a repository change needs specification, planning, "
            "or local implementation through the Superpowers development lifecycle.",
            frontmatter,
        )

    def test_superpowers_owns_the_ordered_lifecycle(self) -> None:
        brainstorming = self.skill_text.index("superpowers:brainstorming")
        writing_plans = self.skill_text.index("superpowers:writing-plans")
        sdd = self.skill_text.index("superpowers:subagent-driven-development")
        self.assertLess(brainstorming, writing_plans)
        self.assertLess(writing_plans, sdd)
        self.assertIn("Superpowers is the authoritative development methodology.", self.skill_text)
        for forbidden in ("custom scheduler", "worker packet schema", "runtime snapshot"):
            self.assertIn(forbidden, self.skill_text)

    def test_entry_maturity_skips_completed_stages(self) -> None:
        for state in (
            "Change request or incomplete specification",
            "Human-approved current specification",
            "Approved plan bound to the current specification",
        ):
            self.assertIn(state, self.skill_text)
        self.assertIn("Do not repeat a completed stage.", self.skill_text)

    def test_grill_with_docs_is_required_for_spec_authoring_and_refinement(self) -> None:
        self.assertIn("REQUIRED SUB-SKILL: Use grill-with-docs", self.skill_text)
        for trigger in (
            "no Human-approved written specification exists",
            "material ambiguity remains",
            "repository evidence conflicts with the proposed specification",
        ):
            self.assertIn(trigger, self.skill_text)
        self.assertIn("Ask one decision question at a time.", self.skill_text)
        self.assertIn("Do not silently replace Grill with Docs with ad hoc questioning.", self.skill_text)
        self.assertIn("not_needed", self.skill_text)

    def test_llm_wiki_owns_query_and_three_durable_checkpoints(self) -> None:
        self.assertIn("REQUIRED SUB-SKILL: Use llm-wiki", self.skill_text)
        for checkpoint in (
            "Human-approved written specification",
            "Repository-approved implementation plan",
            "Implementation closeout",
        ):
            self.assertIn(checkpoint, self.skill_text)
        self.assertIn("knowledge/index.md", self.skill_text)
        self.assertIn("knowledge/log.md", self.skill_text)
        self.assertIn("Do not create parallel `CONTEXT.md` or `docs/adr/` stores.", self.skill_text)
        self.assertIn("not_applicable", self.skill_text)

    def test_upstream_owns_model_tiers_and_local_contract_only_adds_effort(self) -> None:
        self.assertIn("Follow the current Superpowers SDD Model Selection contract.", self.skill_text)
        self.assertIn("Every subagent dispatch must state its model.", self.skill_text)
        self.assertIn("| Mechanical task or small scoped re-review | `low` |", self.skill_text)
        self.assertIn("| Multi-file integration, normal debugging, or task review | `medium` |", self.skill_text)
        self.assertIn("| Architecture-sensitive or high-risk task, or final review | `high` |", self.skill_text)
        self.assertIn("Honor an explicit user runtime override.", self.skill_text)
        self.assertIn("`not_supported`", self.skill_text)
        self.assertNotIn("| orchestrator |", self.skill_text)
        self.assertNotIn("economical balanced", self.skill_text)
        self.assertNotRegex(self.skill_text, re.compile(r"\bgpt-[0-9]"))

    def test_host_boundary_distinguishes_optional_effort_from_required_dispatch(self) -> None:
        self.assertIn(
            "Lack of independent effort control does not block the flow.",
            self.skill_text,
        )
        self.assertIn(
            "Lack of isolated dispatch with an explicit model is `BLOCKED`.",
            self.skill_text,
        )
        self.assertIn("Codex", self.skill_text)
        self.assertIn("Hermes Agent", self.skill_text)
        self.assertIn("skills.external_dirs", self.skill_text)

    def test_knowledge_closeout_precedes_final_review(self) -> None:
        task_review = self.skill_text.index("All implementation tasks and task reviews")
        closeout = self.skill_text.index("## Implementation Closeout")
        final_review = self.skill_text.index("## Final Whole-Branch Review")
        self.assertLess(task_review, closeout)
        self.assertLess(closeout, final_review)

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
