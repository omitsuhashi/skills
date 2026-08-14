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
AUTHORIZED_MARKER_BLOB = "ef384328ad21f49f4c2e4834cef3d401c350d9a8"
AUTHORIZED_SQUASH_POLICY_ROOT = "82dcd32157ff9690ae038f982f3916009e449f80"
AUTHORIZED_MIGRATION_ENTRIES = (
    (
        "b50ed8e434725cb70bc0f1d2c6daa1a053e0ccc1",
        ".superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/"
        "approved-residual-fix-report.md",
    ),
    (
        "c884197bf566cc93f319f3c2a1b6d2ad1563d10e",
        ".superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/"
        "final-fix-report.md",
    ),
    (
        "da22b7580961fb9a2087ab1eb034fb34000711f8",
        ".superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/"
        "task-2-report.md",
    ),
)


def run_git(repository: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def read_blob(repository: Path, blob: str) -> bytes:
    return subprocess.run(
        ["git", "cat-file", "blob", blob],
        cwd=repository,
        check=True,
        capture_output=True,
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
        marker.write_bytes(read_blob(REPO_ROOT, AUTHORIZED_MARKER_BLOB))
        for blob, relative_path in AUTHORIZED_MIGRATION_ENTRIES:
            artifact = self.root / relative_path
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_bytes(read_blob(REPO_ROOT, blob))
        run_git(
            self.root,
            "add",
            "-f",
            MIGRATION_MARKER,
            *(path for _blob, path in AUTHORIZED_MIGRATION_ENTRIES),
        )
        run_git(self.root, "commit", "-m", "add exact migration state")
        run_git(self.root, "rm", MIGRATION_MARKER)
        run_git(
            self.root,
            "rm",
            "--cached",
            *(path for _blob, path in AUTHORIZED_MIGRATION_ENTRIES),
        )
        run_git(self.root, "commit", "-m", "remove exact migration state")
        return run_git(self.root, "rev-parse", "HEAD").strip()

    def commit_transient_add_then_delete(self) -> tuple[str, str]:
        transient = self.root / ".superpowers" / "post-cleanup.md"
        transient.parent.mkdir(parents=True, exist_ok=True)
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
        """Catches rejecting the exact unsquashed semantic cleanup transition."""
        fixture = CiHistoryFixture()
        try:
            fixture.commit_cleanup_boundary()
            result = fixture.run_ci_validation()
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        finally:
            fixture.close()

    def test_transient_validation_step_accepts_known_squash_cleanup_boundary(self) -> None:
        """Catches skipping validation when squash removes cleanup history."""
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "squash-main"
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--quiet",
                    "--no-hardlinks",
                    str(REPO_ROOT),
                    str(repository),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            shutil.copyfile(
                TRANSIENT_VALIDATOR,
                repository / "scripts" / TRANSIENT_VALIDATOR.name,
            )
            self.assertEqual(
                "",
                run_git(
                    repository,
                    "log",
                    "--full-history",
                    "--diff-filter=D",
                    "--format=%H",
                    "HEAD",
                    "--",
                    MIGRATION_MARKER,
                ).strip(),
            )
            result = subprocess.run(
                ["bash", "-c", transient_validation_step()],
                cwd=repository,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_transient_validation_step_accepts_updated_main_policy_import(self) -> None:
        """Catches pinning every later main integration to the root policy blob."""
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "updated-main-integration"
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--quiet",
                    "--no-hardlinks",
                    str(REPO_ROOT),
                    str(repository),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            run_git(repository, "config", "user.name", "Test User")
            run_git(repository, "config", "user.email", "test@example.invalid")
            run_git(repository, "checkout", "--detach", AUTHORIZED_SQUASH_POLICY_ROOT)
            shutil.copyfile(
                TRANSIENT_VALIDATOR,
                repository / "scripts" / TRANSIENT_VALIDATOR.name,
            )
            run_git(repository, "add", "scripts/validate_sdd_transient_artifacts.py")
            run_git(repository, "commit", "-m", "update strict policy on main")
            updated_main = run_git(repository, "rev-parse", "HEAD").strip()
            pre_policy_task = run_git(
                REPO_ROOT, "rev-parse", "523e90969d0c15499c74f0c1b8c897c3607bd53b^1"
            ).strip()
            merge_tree = run_git(repository, "rev-parse", f"{updated_main}^{{tree}}").strip()
            integration = run_git(
                repository,
                "commit-tree",
                merge_tree,
                "-p",
                pre_policy_task,
                "-p",
                updated_main,
                "-m",
                "integrate updated main policy",
            ).strip()
            run_git(repository, "checkout", "--detach", integration)
            result = subprocess.run(
                ["bash", "-c", transient_validation_step()],
                cwd=repository,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

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
        """Catches treating an unknown clean history as an authorized boundary."""
        fixture = CiHistoryFixture()
        try:
            result = fixture.run_ci_validation()
            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        finally:
            fixture.close()

    def test_transient_validation_step_rejects_multiple_cleanup_boundaries(self) -> None:
        """Catches selecting one of multiple semantic cleanup transitions."""
        fixture = CiHistoryFixture()
        try:
            fixture.commit_cleanup_boundary()
            fixture.commit_cleanup_boundary()
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
