from __future__ import annotations

from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
PLAN_CONTRACT = SKILL_DIR / "references" / "plan-contract.md"
PLANNING_CONTEXT = SKILL_DIR / "references" / "planning-context.md"
RESEARCH_STAGE = SKILL_DIR / "references" / "research-stage.md"
PROMPTS = tuple(sorted((SKILL_DIR / "prompts").glob("*.md")))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TransientArtifactContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = read(SKILL)
        cls.plan_contract_text = read(PLAN_CONTRACT)
        cls.planning_text = read(PLANNING_CONTEXT)
        cls.research_text = read(RESEARCH_STAGE)
        cls.prompt_text = "\n".join(read(path) for path in PROMPTS)
        cls.all_text = "\n".join(
            (
                cls.skill_text,
                cls.plan_contract_text,
                cls.planning_text,
                cls.research_text,
                cls.prompt_text,
            )
        )

    def test_normal_stage_handoffs_default_to_bounded_repository_external_temporary_paths(self) -> None:
        normalized = " ".join(self.all_text.split()).lower()
        for stage in (
            "research",
            "spec",
            "plan",
            "implementation",
            "task review",
            "repair",
            "integration",
            "final review",
            "knowledge closeout",
        ):
            self.assertIn(stage, normalized)
        self.assertIn("repository-external", normalized)
        self.assertIn("task / session", normalized)
        self.assertIn("temporary", normalized)
        self.assertNotIn(".superpowers/research/<epic-id>/", self.all_text)

    def test_repository_local_scratch_is_an_explicit_fail_closed_exception(self) -> None:
        normalized = " ".join(self.all_text.split()).lower()
        for required in (
            "concrete operational reason",
            "before the first write",
            "gitignore",
            "ignored",
            "untracked",
            "unstaged",
            "uncommitted",
        ):
            self.assertIn(required, normalized)
        self.assertIn("fail", normalized)
        self.assertIn("repository-external", normalized)

    def test_raw_worker_and_review_outputs_never_become_durable_duplicates(self) -> None:
        durable = self.skill_text.split("## Durable Knowledge", 1)[1].split("## Plan Stage", 1)[0]
        normalized = " ".join(durable.split()).lower()
        for durable_target in (
            "canonical specification",
            "reviewed implementation plan",
            "knowledge/log.md",
        ):
            self.assertIn(durable_target, normalized)
        for transient in (
            "raw worker report",
            "raw review output",
            "raw fix report",
            "transcript",
        ):
            self.assertIn(transient, normalized)
        self.assertIn("decision", normalized)
        self.assertIn("verdict", normalized)
        self.assertIn("evidence identity", normalized)

    def test_plan_review_prompt_separates_raw_output_from_durable_verdict_summary(self) -> None:
        plan_reviewer = read(SKILL_DIR / "prompts" / "plan-reviewer.md")
        normalized = " ".join(plan_reviewer.split()).lower()
        self.assertIn("repository-external", normalized)
        self.assertIn("raw review", normalized)
        self.assertIn("durable", normalized)
        self.assertIn("verdict", normalized)


if __name__ == "__main__":
    unittest.main()
