from __future__ import annotations

from pathlib import Path
import re
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "skill-architecture.yml"
LEGACY_GRILL_SKILL = "-".join(("grill", "to", "pr", "loop"))
LEGACY_ISSUE_SKILL = "-".join(("issue", "implementation", "loop"))
TASK_MANAGEMENT_TEST = (
    REPO_ROOT
    / "skills"
    / "task-management"
    / "tests"
    / "test_task_management_contract.py"
)


def run_git(repository: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def transient_validation_step() -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(
        r"^      - name: Validate SDD transient artifacts\n"
        r"(?P<body>.*?)(?=^      - name: |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError("transient validation workflow step is missing")
    lines = match.group("body").splitlines()
    for index, line in enumerate(lines):
        if line.startswith("        run: "):
            value = line.removeprefix("        run: ")
            if value != "|":
                return value
            command_lines = []
            for command_line in lines[index + 1 :]:
                if not command_line:
                    command_lines.append("")
                    continue
                if not command_line.startswith("          "):
                    break
                command_lines.append(command_line[10:])
            return "\n".join(command_lines)
    raise AssertionError("transient validation workflow command is missing")


def clone_reachable_repository(destination: Path, *, depth: int | None = None) -> None:
    command = ["git", "clone", "--quiet", "--no-local"]
    if depth is not None:
        command.extend(("--depth", str(depth)))
    command.extend((REPO_ROOT.as_uri(), str(destination)))
    subprocess.run(command, check=True, capture_output=True, text=True)


def run_ci_validation(repository: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", transient_validation_step()],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
    )


class SkillCiWorkflowTests(unittest.TestCase):
    def test_python_matrix_runs_standalone_skill_contracts(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('python-version:\n          - "3.9"\n          - "3.12"', text)
        self.assertIn("Run decide-in-order tests", text)
        self.assertIn(
            "python3 -m unittest discover -s skills/decide-in-order/tests", text
        )
        self.assertIn("Run task-management tests", text)
        self.assertIn(
            "python3 -m unittest discover -s skills/task-management/tests", text
        )
        self.assertIn("Run sdd-implementation tests", text)
        self.assertIn(
            "python3 -m unittest discover -s skills/sdd-implementation/tests",
            text,
        )
        self.assertNotIn(f"Run {LEGACY_GRILL_SKILL} tests", text)
        self.assertNotIn(f"Run {LEGACY_ISSUE_SKILL} tests", text)
        self.assertNotIn("plugins/task-management", text)

    def test_task_management_contract_is_host_neutral(self) -> None:
        text = TASK_MANAGEMENT_TEST.read_text(encoding="utf-8")
        self.assertIn("test_skill_has_no_host_specific_or_runtime_surface", text)
        self.assertIn("test_capability_and_partial_failures_are_fail_closed", text)

    def test_workflow_omits_repository_compatibility_entrypoints(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Test skill authoring guidance", text)
        self.assertIn("scripts/test_skill_authoring_guidance.py", text)
        self.assertIn("Test skill CI workflow contract", text)
        self.assertIn("scripts/test_skill_ci_workflow.py", text)
        self.assertNotIn("Test repository compatibility validator", text)
        self.assertNotIn("scripts/test_validate_repository_compatibility.py", text)
        self.assertNotIn("Validate repository compatibility", text)
        self.assertNotIn("scripts/validate_repository_compatibility.py", text)

    def test_workflow_runs_transient_artifact_regression_and_validation(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Test SDD transient artifact validator", text)
        self.assertIn("python3 scripts/test_validate_sdd_transient_artifacts.py", text)
        self.assertIn("Validate SDD transient artifacts", text)
        self.assertIn("python3 scripts/validate_sdd_transient_artifacts.py", text)
        self.assertIn("--post-policy-history", text)
        self.assertNotIn("--post-cleanup-history", text)
        self.assertNotIn("--migration-baseline", text)

    def test_workflow_runs_root_parity_and_isolated_package_closure(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "      - name: Test SDD canonical plan parity\n"
            "        run: PYTHONPYCACHEPREFIX=/tmp/skills-pycache "
            "python3 scripts/test_sdd_canonical_plan_parity.py",
            text,
        )
        self.assertIn(
            "      - name: Test isolated SDD package closure\n"
            "        run: PYTHONPYCACHEPREFIX=/tmp/skills-pycache "
            "python3 skills/sdd-implementation/tests/test_isolated_install.py",
            text,
        )

    def test_transient_validation_step_accepts_reachable_only_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            clone_reachable_repository(repository)

            result = run_ci_validation(repository)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_transient_validation_does_not_require_origin_main(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            clone_reachable_repository(repository)
            run_git(repository, "update-ref", "-d", "refs/remotes/origin/main")
            with self.assertRaises(subprocess.CalledProcessError):
                run_git(repository, "rev-parse", "--verify", "refs/remotes/origin/main")

            result = run_ci_validation(repository)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_transient_validation_rejects_post_policy_add_then_delete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            clone_reachable_repository(repository)
            run_git(repository, "config", "user.name", "Test User")
            run_git(repository, "config", "user.email", "test@example.invalid")
            transient = repository / ".superpowers" / "smuggled.md"
            transient.parent.mkdir(parents=True, exist_ok=True)
            transient.write_text("must be rejected\n", encoding="utf-8")
            run_git(repository, "add", "-f", ".superpowers/smuggled.md")
            run_git(repository, "commit", "-m", "add forbidden transient artifact")
            added = run_git(repository, "rev-parse", "HEAD").strip()
            run_git(repository, "rm", ".superpowers/smuggled.md")
            run_git(repository, "commit", "-m", "delete forbidden transient artifact")
            self.assertTrue(
                run_git(repository, "ls-tree", "-r", added, "--", ".superpowers").strip()
            )

            result = run_ci_validation(repository)

            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("category=new_commit_entry", result.stdout + result.stderr)

    def test_transient_validation_rejects_shallow_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            clone_reachable_repository(repository, depth=1)
            self.assertEqual(
                "true",
                run_git(repository, "rev-parse", "--is-shallow-repository").strip(),
            )

            result = run_ci_validation(repository)

            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("category=history_unavailable", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
