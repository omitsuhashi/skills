from __future__ import annotations

from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
PLANNING_CONTEXT = SKILL_DIR / "references" / "planning-context.md"


def read_or_empty(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


class PreImplementationContextContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = read_or_empty(SKILL)
        cls.planning_text = read_or_empty(PLANNING_CONTEXT)

    def test_entrypoint_limits_main_session_to_planning_controller(self) -> None:
        self.assertIn("## Planning Controller", self.skill_text)
        for ownership in (
            "Human dialogue",
            "Decision Record",
            "approval state",
            "stage routing",
            "Control Return",
        ):
            self.assertIn(ownership, self.skill_text)
        self.assertIn(
            "Do not inspect source code, broad repository content, full artifacts, "
            "diffs, or raw command output.",
            " ".join(self.skill_text.split()),
        )

    def test_planning_controller_allowed_and_forbidden_reads_are_explicit(self) -> None:
        for allowed in (
            "applicable skill instructions and repository `AGENTS.md`",
            "repository root, branch, worktree, and status metadata",
            "Control Return and Stage Capsule",
            "short excerpt for the current decision",
            "approval state and canonical artifact paths",
        ):
            self.assertIn(allowed, self.planning_text)
        for forbidden in (
            "source code",
            "broad wiki or documentation pages",
            "full specification or full implementation plan",
            "git diff, test output, or raw command output",
            "multi-file repository exploration",
        ):
            self.assertIn(forbidden, self.planning_text)

    def test_spec_draft_is_the_only_decision_record(self) -> None:
        self.assertIn("## Decision Record", self.planning_text)
        self.assertIn("`Confirmed Decisions`", self.planning_text)
        self.assertIn("`Open Decisions`", self.planning_text)
        self.assertIn(
            "Do not create a separate ledger, `CONTEXT.md`, or repo-root `docs/adr/`.",
            self.planning_text,
        )
        self.assertIn(
            "Reopen a confirmed decision only when new repository evidence creates "
            "a material conflict.",
            " ".join(self.planning_text.split()),
        )

    def test_control_return_has_only_bounded_semantic_fields(self) -> None:
        self.assertIn("## Control Return", self.planning_text)
        for field in (
            "`status`",
            "`artifact_path`",
            "`decision_requests`",
            "`material_risks`",
        ):
            self.assertIn(field, self.planning_text)
        self.assertIn("Keep detailed findings in the artifact.", self.planning_text)
        self.assertIn(
            "Aim for about 200 words; do not add a word-count validator.",
            self.planning_text,
        )

    def test_stage_capsule_carries_only_current_control_state(self) -> None:
        self.assertIn("## Stage Capsule", self.planning_text)
        for field in (
            "current result",
            "canonical paths",
            "open decisions",
            "approval state",
            "material risks",
        ):
            self.assertIn(field, self.planning_text)
        self.assertIn(
            "Aim for about 400 words; do not copy raw discussion or tool output.",
            self.planning_text,
        )

    def test_plan_author_is_fresh_and_uses_upstream_writing_plans(self) -> None:
        normalized = " ".join(self.planning_text.split())
        self.assertIn("Plan Author Worker", self.planning_text)
        self.assertIn("superpowers:writing-plans", self.planning_text)
        self.assertIn("Do not inherit the parent conversation.", self.planning_text)
        self.assertIn(
            "The Planning Controller evaluates only the Control Return, plan path, "
            "spec binding, and repository-required approval.",
            normalized,
        )

    def test_missing_fresh_dispatch_never_falls_back_to_controller_exploration(self) -> None:
        self.assertIn(
            "If isolated fresh-context dispatch is unavailable, return `BLOCKED`.",
            self.planning_text,
        )
        self.assertIn(
            "Do not fall back to Planning Controller exploration or artifact authoring.",
            self.planning_text,
        )


if __name__ == "__main__":
    unittest.main()
