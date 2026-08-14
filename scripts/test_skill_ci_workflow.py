from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Optional
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
TRANSIENT_VALIDATOR = REPO_ROOT / "scripts" / "validate_sdd_transient_artifacts.py"
MIGRATION_MARKER = "scripts/sdd-transient-artifact-migration.json"


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


class CiHistoryFixture:
    def __init__(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "repository"
        self.root.mkdir()
        run_git(self.root, "init", "-b", "main")
        run_git(self.root, "config", "user.name", "Test User")
        run_git(self.root, "config", "user.email", "test@example.invalid")
        scripts = self.root / "scripts"
        scripts.mkdir()
        shutil.copyfile(TRANSIENT_VALIDATOR, scripts / TRANSIENT_VALIDATOR.name)
        (self.root / ".gitignore").write_text(".superpowers/\n", encoding="utf-8")
        (self.root / "tracked.txt").write_text("base\n", encoding="utf-8")
        run_git(self.root, "add", ".gitignore", "scripts", "tracked.txt")
        run_git(self.root, "commit", "-m", "base")

    def close(self) -> None:
        self.temporary_directory.cleanup()

    def commit_cleanup_boundary(self) -> str:
        marker = self.root / MIGRATION_MARKER
        marker.write_text("{}\n", encoding="utf-8")
        run_git(self.root, "add", MIGRATION_MARKER)
        run_git(self.root, "commit", "-m", "add migration marker")
        run_git(self.root, "rm", MIGRATION_MARKER)
        run_git(self.root, "commit", "-m", "remove migration marker")
        return run_git(self.root, "rev-parse", "HEAD").strip()

    def commit_transient_add_then_delete(self) -> tuple[str, str]:
        transient = self.root / ".superpowers" / "post-cleanup.md"
        transient.parent.mkdir(parents=True)
        transient.write_text("must never enter a post-cleanup commit\n", encoding="utf-8")
        run_git(self.root, "add", "-f", ".superpowers/post-cleanup.md")
        run_git(self.root, "commit", "-m", "add forbidden transient artifact")
        added = run_git(self.root, "rev-parse", "HEAD").strip()
        run_git(self.root, "rm", ".superpowers/post-cleanup.md")
        run_git(self.root, "commit", "-m", "delete forbidden transient artifact")
        deleted = run_git(self.root, "rev-parse", "HEAD").strip()
        return added, deleted

    def run_ci_validation(self, repository: Optional[Path] = None) -> subprocess.CompletedProcess[str]:
        target = repository or self.root
        return subprocess.run(
            ["bash", "-c", transient_validation_step()],
            cwd=target,
            check=False,
            capture_output=True,
            text=True,
        )

    def shallow_clone(self) -> Path:
        clone = Path(self.temporary_directory.name) / "shallow"
        subprocess.run(
            ["git", "clone", "--quiet", "--depth", "1", self.root.as_uri(), str(clone)],
            check=True,
            capture_output=True,
            text=True,
        )
        return clone


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

    def test_workflow_runs_transient_artifact_regression_and_repository_validation(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Test SDD transient artifact validator", text)
        self.assertIn("python3 scripts/test_validate_sdd_transient_artifacts.py", text)
        self.assertIn("Validate SDD transient artifacts", text)
        self.assertIn("python3 scripts/validate_sdd_transient_artifacts.py", text)
        self.assertNotIn("--migration-baseline", text)

    def test_transient_validation_step_accepts_clean_post_cleanup_history(self) -> None:
        fixture = CiHistoryFixture()
        try:
            fixture.commit_cleanup_boundary()
            result = fixture.run_ci_validation()
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        finally:
            fixture.close()

    def test_transient_validation_step_rejects_add_then_delete_commit_history(self) -> None:
        fixture = CiHistoryFixture()
        try:
            fixture.commit_cleanup_boundary()
            added, deleted = fixture.commit_transient_add_then_delete()
            self.assertTrue(run_git(fixture.root, "ls-tree", "-r", added, "--", ".superpowers").strip())
            self.assertEqual("", run_git(fixture.root, "ls-tree", "-r", deleted, "--", ".superpowers"))
            result = fixture.run_ci_validation()
            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("category=new_commit_entry", result.stdout + result.stderr)
        finally:
            fixture.close()

    def test_transient_validation_step_rejects_missing_cleanup_boundary(self) -> None:
        fixture = CiHistoryFixture()
        try:
            result = fixture.run_ci_validation()
            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        finally:
            fixture.close()

    def test_transient_validation_step_rejects_shallow_history(self) -> None:
        fixture = CiHistoryFixture()
        try:
            fixture.commit_cleanup_boundary()
            shallow = fixture.shallow_clone()
            self.assertEqual("true", run_git(shallow, "rev-parse", "--is-shallow-repository").strip())
            result = fixture.run_ci_validation(shallow)
            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
