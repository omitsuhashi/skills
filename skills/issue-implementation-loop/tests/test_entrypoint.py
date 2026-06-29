from __future__ import annotations

from _helpers import *


class EntrypointTests(unittest.TestCase):
    def test_skill_entrypoint_is_bounded_and_trigger_only(self) -> None:
        text = SKILL_FILE.read_text(encoding="utf-8")
        description = re.search(r"^description: (.+)$", text, re.MULTILINE)

        self.assertIsNotNone(description)
        self.assertEqual(
            description.group(1),
            "Use when implementing approved repository issues after spec, acceptance criteria, and issue decomposition are approved.",
        )
        self.assertLessEqual(len(re.findall(r"\S+", text)), 620)

    def test_skill_entrypoint_names_session_and_worker_semantics(self) -> None:
        text = SKILL_FILE.read_text(encoding="utf-8")

        for required in (
            "one execution coordinator context",
            "planning/grill session must not implement issue work",
            "Do not create user-owned Codex threads",
            "bounded worker-context jobs",
        ):
            self.assertIn(required, text)

    def test_skill_entrypoint_defines_execution_applicability(self) -> None:
        text = SKILL_FILE.read_text(encoding="utf-8")

        for required in (
            "Use this skill only when",
            "normalized approved packet",
            "worker context is available",
            "coordinator must not implement",
            "Do not use this skill for",
            "small one-off edits",
            "unapproved or changing scope",
        ):
            self.assertIn(required, text)

    def test_skill_entrypoint_keeps_ledger_and_report_updates_japanese_base(self) -> None:
        text = SKILL_FILE.read_text(encoding="utf-8")

        for required in (
            "human-facing report updates in Japanese",
            "stable IDs",
            "schema keys",
            "external issue/PR references",
        ):
            self.assertIn(required, text)

    def test_skill_entrypoint_routes_through_context_contract(self) -> None:
        text = SKILL_FILE.read_text(encoding="utf-8")

        self.assertIn("context-contract.toml", text)
        self.assertIn("select_operation.py", text)
        for operation_reference in (
            "execution-envelope.md",
            "dependency-contract.md",
            "worktree-lifecycle.md",
            "scheduler.md",
            "worker-contract.md",
            "review-gate.md",
            "human-wait.md",
            "runtime-state.md",
            "recovery.md",
            "remote-delivery.md",
        ):
            self.assertNotIn(operation_reference, text)

    def test_skill_entrypoint_discovers_role_boundary_mental_model(self) -> None:
        text = SKILL_FILE.read_text(encoding="utf-8")
        mental_model = SKILL_DIR / "references" / "mental-model.md"

        self.assertIn("references/mental-model.md", text)
        self.assertTrue(mental_model.exists())

        model_text = mental_model.read_text(encoding="utf-8")
        self.assertLessEqual(len(model_text.split()), 900)
        for required in (
            "coordinator",
            "worker",
            "reviewer",
            "runtime state",
            "local ledger",
            "remote delivery",
            "Role Boundary",
        ):
            self.assertIn(required, model_text)

    def test_mental_model_keeps_final_pr_merge_human_only(self) -> None:
        mental_model = SKILL_DIR / "references" / "mental-model.md"
        model_text = mental_model.read_text(encoding="utf-8")

        self.assertIn("Final PR merge is always human-only", model_text)
        self.assertNotRegex(
            model_text,
            r"final PR merge,.*require explicit current approval",
        )
