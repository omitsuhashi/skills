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

    def test_incomplete_spec_preserves_settled_portions(self) -> None:
        self.assertIn(
            "Preserve approved and complete portions of an incomplete specification.",
            self.skill_text,
        )
        self.assertIn(
            "Use Grill with Docs only for unresolved material decisions.",
            self.skill_text,
        )

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
        self.assertIn("`not_supported`", self.skill_text)
        self.assertNotIn("| orchestrator |", self.skill_text)
        self.assertNotIn("economical balanced", self.skill_text)
        self.assertNotRegex(self.skill_text, re.compile(r"\bgpt-[0-9]"))

    def test_user_model_and_effort_overrides_have_independent_precedence(self) -> None:
        self.assertIn(
            "An explicit user runtime model override takes precedence over "
            "upstream model-tier resolution.",
            self.skill_text,
        )
        self.assertIn(
            "An explicit user runtime effort override takes precedence over "
            "the default effort overlay.",
            self.skill_text,
        )

    def test_task_complexity_and_risk_override_role_effort_defaults(self) -> None:
        self.assertIn(
            "Task complexity and current risk take precedence over role defaults.",
            self.skill_text,
        )
        self.assertIn(
            "A high-risk task review uses `high`, regardless of its role default.",
            self.skill_text,
        )
        self.assertIn(
            "The shared default effort vocabulary is limited to `low`, `medium`, and `high`.",
            self.skill_text,
        )

    def test_required_skill_families_are_preflighted_in_the_active_runtime(self) -> None:
        self.assertIn(
            "Before entering a selected route, use the active runtime's skill discovery "
            "to verify applicable dependencies and required capabilities.",
            self.skill_text,
        )
        for dependency in (
            "Superpowers lifecycle skills",
            "`grill-with-docs`",
            "`llm-wiki`",
        ):
            self.assertIn(dependency, self.skill_text)
        for blocker in (
            "`BLOCKED: missing Superpowers lifecycle dependency`",
            "`BLOCKED: missing grill-with-docs dependency`",
            "`BLOCKED: missing llm-wiki dependency`",
        ):
            self.assertIn(blocker, self.skill_text)

    def test_dependency_preflight_respects_route_conditions(self) -> None:
        self.assertIn(
            "Check the Superpowers lifecycle skills for every route.",
            self.skill_text,
        )
        self.assertIn(
            "Check `grill-with-docs` when the Spec Stage requires it.",
            self.skill_text,
        )
        self.assertIn(
            "Check `llm-wiki` when a knowledge root exists.",
            self.skill_text,
        )

    def test_runtime_capability_boundary_distinguishes_optional_effort_from_required_dispatch(self) -> None:
        self.assertIn("## Runtime Capability Boundary", self.skill_text)
        for capability in (
            "isolated dispatch",
            "explicit model",
            "optional effort",
            "wait",
            "resume",
        ):
            self.assertIn(capability, self.skill_text)
        self.assertIn(
            "Lack of independent effort control does not block the flow.",
            self.skill_text,
        )
        self.assertIn(
            "Lack of isolated dispatch with an explicit model is `BLOCKED`.",
            self.skill_text,
        )
        self.assertNotIn("Codex", self.skill_text)
        self.assertNotIn("Hermes Agent", self.skill_text)

    def test_review_is_bounded_to_material_findings(self) -> None:
        for lens in ("requirements fit", "material simplicity", "material current risk"):
            self.assertIn(lens, self.skill_text)
        self.assertIn(
            "A blocking finding needs evidence of a requirement gap,",
            self.skill_text,
        )
        self.assertRegex(
            self.skill_text,
            re.compile(
                r"Do not block on\s+style, formatting, future-only concerns, "
                r"scope-external hardening, or equivalent\s+preferences\."
            ),
        )
        self.assertIn(
            "Do not reduce mechanical validation or required test coverage.",
            self.skill_text,
        )

    def test_local_only_remote_boundary_is_explicit(self) -> None:
        self.assertIn(
            "Do not push, create a PR, merge, release, or install live without separate",
            self.skill_text,
        )
        self.assertIn("explicit authorization.", self.skill_text)

    def test_every_remote_write_requires_explicit_authorization(self) -> None:
        self.assertIn(
            "Do not perform any remote write without separate explicit authorization.",
            self.skill_text,
        )
        self.assertIn(
            "This includes push, PR, merge, release, live install, issue, comment, "
            "and project changes.",
            self.skill_text,
        )

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
            'short_description: "Develop changes with Superpowers, Grill, and LLM Wiki."',
            self.openai_text,
        )
        self.assertIn(
            'default_prompt: "Use $sdd-implementation to take this repository change '
            'through specification, planning, implementation, and local completion."',
            self.openai_text,
        )


if __name__ == "__main__":
    unittest.main()
