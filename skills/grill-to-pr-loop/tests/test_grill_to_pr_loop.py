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
WORKFLOW_ROUTER = SKILL_DIR / "references" / "workflow-contract.md"


def load_check_prereqs():
    spec = importlib.util.spec_from_file_location("grill_to_pr_check_prereqs", CHECK_PREREQS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GrillToPrLoopTests(unittest.TestCase):
    def test_workflow_contract_is_router_to_one_level_references(self) -> None:
        text = WORKFLOW_ROUTER.read_text(encoding="utf-8")
        self.assertLessEqual(len(text.split()), 520)

        expected = (
            "planning-contract.md",
            "local-issue-ledger.md",
            "execution-handoff.md",
            "remote-delivery.md",
            "common-mistakes.md",
        )
        for reference in expected:
            self.assertIn(reference, text)
            self.assertTrue((SKILL_DIR / "references" / reference).exists(), reference)

    def test_skill_entrypoint_points_to_workflow_router(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("references/workflow-contract.md", text)
        self.assertIn("It is a router", text)

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
