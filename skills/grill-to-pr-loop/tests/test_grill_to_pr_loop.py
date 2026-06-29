from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
CHECK_PREREQS = SKILL_DIR / "scripts" / "check_prereqs.py"
CORE_REFERENCE = SKILL_DIR / "references" / "core.md"
PLANNING_CONTRACT = SKILL_DIR / "references" / "planning-contract.md"
GRILL_AGENT_YAML = SKILL_DIR / "agents" / "openai.yaml"
ISSUE_AGENT_YAML = REPO_ROOT / "skills" / "issue-implementation-loop" / "agents" / "openai.yaml"


def load_check_prereqs():
    spec = importlib.util.spec_from_file_location("grill_to_pr_check_prereqs", CHECK_PREREQS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_default_prompt(path: Path) -> str:
    prefix = "  default_prompt: "
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            value = line[len(prefix) :]
            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]
    raise AssertionError(f"default_prompt not found in {path}")


class GrillToPrLoopTests(unittest.TestCase):
    def test_core_reference_owns_global_workflow_context(self) -> None:
        text = CORE_REFERENCE.read_text(encoding="utf-8")
        self.assertLessEqual(len(text.split()), 600)
        for required in (
            "Lifecycle",
            "Responsibilities",
            "Gates",
            "Local-first",
            "Remote approval",
        ):
            self.assertIn(required, text)

    def test_github_mirror_read_set_contains_remote_gate(self) -> None:
        contract_text = (SKILL_DIR / "context-contract.toml").read_text(encoding="utf-8")
        remote_text = (SKILL_DIR / "references" / "remote-delivery.md").read_text(encoding="utf-8")

        self.assertIn('[operations.delivery]', contract_text)
        self.assertIn('"references/remote-delivery.md"', contract_text)
        self.assertIn("## GitHub Mirror Gate", remote_text)
        for required in (
            "Confirm the remote points to GitHub.",
            "Confirm GitHub tool/CLI auth.",
            "Present exact local issues to publish.",
            "Ask for explicit approval.",
            "Update the local ledger before continuing.",
        ):
            self.assertIn(required, remote_text)

    def test_skill_entrypoint_points_to_context_contract_router(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

        self.assertLessEqual(len(text.split()), 950)
        self.assertIn("references/core.md", text)
        self.assertIn("context-contract.toml", text)
        self.assertIn("operation router", text)
        for operation_reference in (
            "planning-contract.md",
            "local-issue-ledger.md",
            "execution-handoff.md",
            "remote-delivery.md",
            "common-mistakes.md",
            "workflow-contract.md",
        ):
            self.assertNotIn(operation_reference, text)

    def test_skill_entrypoint_defines_loop_applicability(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

        for required in (
            "Use loop skills when",
            "Do not use loop skills for",
            "Stop before implementation when",
            "small one-off edits",
            "direct implementation",
            "approved packet",
            "worker context",
        ):
            self.assertIn(required, text)

    def test_entrypoint_discovers_issue_execution_mental_model_without_default_read_set(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        contract_text = (SKILL_DIR / "context-contract.toml").read_text(encoding="utf-8")
        issue_mental_model = REPO_ROOT / "skills" / "issue-implementation-loop" / "references" / "mental-model.md"

        self.assertIn("mental-model.md", text)
        self.assertTrue(issue_mental_model.exists())
        self.assertNotIn("mental-model.md", contract_text)

        model_text = issue_mental_model.read_text(encoding="utf-8")
        for required in (
            "coordinator",
            "worker",
            "reviewer",
            "runtime state",
            "local ledger",
            "remote delivery",
        ):
            self.assertIn(required, model_text)

    def test_generated_specs_and_packets_default_to_japanese_base_language(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        core_text = CORE_REFERENCE.read_text(encoding="utf-8")
        planning_text = PLANNING_CONTRACT.read_text(encoding="utf-8")
        mistakes_text = (SKILL_DIR / "references" / "common-mistakes.md").read_text(encoding="utf-8")
        input_template = (REPO_ROOT / "skills" / "issue-implementation-loop" / "assets" / "templates" / "input-packet.json").read_text(encoding="utf-8")
        worker_template = (REPO_ROOT / "skills" / "issue-implementation-loop" / "assets" / "templates" / "worker-packet.json").read_text(encoding="utf-8")

        for text in (skill_text, core_text, planning_text):
            self.assertIn("Japanese", text)
            self.assertIn("schema keys", text)

        for required in (
            "問題設定 / 成功条件",
            "採用した判断",
            "非目標",
            "Issue 分解方針",
            "受け入れ条件",
            "リモート書き込み方針",
            "人間レビューゲート",
            "停止条件 / 既知のリスク",
        ):
            self.assertIn(required, planning_text)

        self.assertIn("English spec/PRD", mistakes_text)
        self.assertIn("短い日本語 issue タイトル", input_template)
        self.assertIn("必要な挙動の短い要約", worker_template)
        self.assertNotIn("Short issue title", input_template + worker_template)

    def test_phase_gate_approvals_require_local_commit(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        core_text = CORE_REFERENCE.read_text(encoding="utf-8")
        planning_text = PLANNING_CONTRACT.read_text(encoding="utf-8")
        handoff_text = (SKILL_DIR / "references" / "execution-handoff.md").read_text(encoding="utf-8")
        mistakes_text = (SKILL_DIR / "references" / "common-mistakes.md").read_text(encoding="utf-8")

        self.assertIn("phase approval commit", skill_text)
        self.assertIn("commit the approved artifacts", core_text)
        self.assertIn("Spec Gate approval", planning_text)
        self.assertIn("Issue Gate approval", planning_text)
        self.assertIn("Execution Plan Gate approval", handoff_text)
        self.assertIn("Moving to the next phase without committing an approved gate", mistakes_text)

    def test_agent_default_prompts_are_short_and_policy_free(self) -> None:
        for path, skill_name in (
            (GRILL_AGENT_YAML, "$grill-to-pr-loop"),
            (ISSUE_AGENT_YAML, "$issue-implementation-loop"),
        ):
            default_prompt = extract_default_prompt(path)
            self.assertIn(skill_name, default_prompt)
            self.assertLessEqual(len(default_prompt.split()), 32)
            for forbidden in (
                "branch",
                "delivery",
                "review",
                "merge",
                "worktree",
                "epic-base",
            ):
                self.assertNotIn(forbidden, default_prompt.lower())

    def test_candidate_roots_prefers_explicit_then_repo_local_then_global(self) -> None:
        module = load_check_prereqs()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            home = root / "home"
            explicit = root / "explicit-skills"
            repo.mkdir()
            home.mkdir()

            previous_cwd = Path.cwd()
            try:
                os.chdir(repo)
                with (
                    mock.patch.object(module.Path, "home", return_value=home),
                    mock.patch.dict(module.os.environ, {}, clear=True),
                ):
                    roots = module.candidate_roots([str(explicit)])
            finally:
                os.chdir(previous_cwd)

        self.assertEqual(roots[:5], [
            explicit,
            repo.resolve() / "skills",
            repo.resolve() / ".agents" / "skills",
            repo.resolve() / "agents" / "skills",
            home / ".agents" / "skills",
        ])

    def test_find_skill_prefers_repo_local_over_global(self) -> None:
        module = load_check_prereqs()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            home = root / "home"
            local_skill = repo / "skills" / "example" / "SKILL.md"
            global_skill = home / ".agents" / "skills" / "example" / "SKILL.md"
            local_skill.parent.mkdir(parents=True)
            global_skill.parent.mkdir(parents=True)
            local_skill.write_text("---\nname: example\ndescription: local\n---\n", encoding="utf-8")
            global_skill.write_text("---\nname: example\ndescription: global\n---\n", encoding="utf-8")

            previous_cwd = Path.cwd()
            try:
                os.chdir(repo)
                with (
                    mock.patch.object(module.Path, "home", return_value=home),
                    mock.patch.dict(module.os.environ, {}, clear=True),
                ):
                    found = module.find_skill("example", module.candidate_roots([]))
            finally:
                os.chdir(previous_cwd)

        self.assertEqual(found, local_skill.resolve())


if __name__ == "__main__":
    unittest.main()
