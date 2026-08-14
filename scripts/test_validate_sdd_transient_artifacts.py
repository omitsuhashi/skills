from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate_sdd_transient_artifacts.py"
VALIDATION_FAILURE_EXIT = 1
MIGRATION_MARKER = "scripts/sdd-transient-artifact-migration.json"
MIGRATION_PATHS = (
    ".superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/approved-residual-fix-report.md",
    ".superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/final-fix-report.md",
    ".superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/task-2-report.md",
)


def run_git(repository: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def hash_blob(repository: Path, content: str) -> str:
    return subprocess.run(
        ["git", "hash-object", "-w", "--stdin"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
        input=content,
    ).stdout.strip()


def diagnostic_categories(output: str) -> list[str]:
    return re.findall(r"\bcategory=([a-z][a-z0-9_]*)\b", output)


class RepositoryFixture:
    def __init__(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        run_git(self.root, "init", "-b", "main")
        run_git(self.root, "config", "user.name", "Test User")
        run_git(self.root, "config", "user.email", "test@example.invalid")
        (self.root / ".gitignore").write_text(".superpowers/\n", encoding="utf-8")
        (self.root / "tracked.txt").write_text("base\n", encoding="utf-8")
        run_git(self.root, "add", ".gitignore", "tracked.txt")
        run_git(self.root, "commit", "-m", "base")

    def close(self) -> None:
        self.temporary_directory.cleanup()

    def commit_migration_baseline(self) -> str:
        for index, relative_path in enumerate(MIGRATION_PATHS, start=1):
            path = self.root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"baseline report {index}\n", encoding="utf-8")
            run_git(self.root, "add", "-f", relative_path)
        run_git(self.root, "commit", "-m", "pre-policy reports")
        return run_git(self.root, "rev-parse", "HEAD").strip()

    def contaminated_tree(
        self, relative_path: str = ".superpowers/contaminated.md"
    ) -> str:
        blob = hash_blob(self.root, "contaminated\n")
        run_git(
            self.root,
            "update-index",
            "--add",
            "--cacheinfo",
            f"100644,{blob},{relative_path}",
        )
        tree = run_git(self.root, "write-tree").strip()
        run_git(self.root, "read-tree", "HEAD")
        return tree

    def contaminated_commit(self) -> str:
        tree = self.contaminated_tree()
        return run_git(
            self.root,
            "commit-tree",
            tree,
            "-p",
            run_git(self.root, "rev-parse", "HEAD").strip(),
            "-m",
            "contaminated new commit",
        ).strip()


class TransientArtifactValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def run_validator(
        self,
        *args: str,
        repository: Path | None = None,
        validator: Path = VALIDATOR,
    ) -> subprocess.CompletedProcess[str]:
        self.assertTrue(
            validator.is_file(),
            f"repository transient-artifact validator is missing: {validator}",
        )
        return subprocess.run(
            [
                sys.executable,
                str(validator),
                "--repository",
                str(repository or self.fixture.root),
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def assert_validator_accepts(
        self,
        *args: str,
        repository: Path | None = None,
        validator: Path = VALIDATOR,
    ) -> None:
        result = self.run_validator(
            *args, repository=repository, validator=validator
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def assert_validator_rejects(
        self,
        category: str,
        *args: str,
        repository: Path | None = None,
        validator: Path = VALIDATOR,
    ) -> None:
        result = self.run_validator(
            *args, repository=repository, validator=validator
        )
        output = result.stdout + result.stderr
        self.assertEqual(VALIDATION_FAILURE_EXIT, result.returncode, output)
        self.assertEqual([category], diagnostic_categories(output), output)

    def write_fake_validator(
        self, *categories: str, exit_code: int = VALIDATION_FAILURE_EXIT
    ) -> Path:
        validator = self.fixture.root / "fake_validator.py"
        output_lines = "\n".join(
            f"print('category={category}')" for category in categories
        )
        validator.write_text(
            f"import sys\n{output_lines}\nsys.exit({exit_code})\n",
            encoding="utf-8",
        )
        return validator

    def test_rejection_contract_requires_one_exact_diagnostic_category(self) -> None:
        exact = self.write_fake_validator("index_entry")
        self.assert_validator_rejects("index_entry", validator=exact)

        prefixed = self.write_fake_validator("index_entry_extra")
        with self.assertRaises(AssertionError):
            self.assert_validator_rejects("index_entry", validator=prefixed)

        multiple = self.write_fake_validator("index_entry", "candidate_tree_entry")
        with self.assertRaises(AssertionError):
            self.assert_validator_rejects("index_entry", validator=multiple)

        wrong_exit = self.write_fake_validator("index_entry", exit_code=2)
        with self.assertRaises(AssertionError):
            self.assert_validator_rejects("index_entry", validator=wrong_exit)

    def test_migration_marker_does_not_authorize_a_nonzero_index(self) -> None:
        marker = self.fixture.root / MIGRATION_MARKER
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("historical marker\n", encoding="utf-8")
        transient = self.fixture.root / ".superpowers" / "tracked.md"
        transient.parent.mkdir(parents=True, exist_ok=True)
        transient.write_text("tracked\n", encoding="utf-8")
        run_git(
            self.fixture.root,
            "add",
            "-f",
            MIGRATION_MARKER,
            ".superpowers/tracked.md",
        )

        self.assert_validator_rejects("index_entry")

    def test_repository_local_scratch_requires_ignore_coverage_and_reason(self) -> None:
        scratch = ".superpowers/local/notes.md"
        (self.fixture.root / ".gitignore").write_text("", encoding="utf-8")
        self.assert_validator_rejects(
            "scratch_ignore_missing",
            "--scratch-path",
            scratch,
            "--scratch-reason",
            "tool requires a repository-local cache",
        )

        (self.fixture.root / ".gitignore").write_text(
            ".superpowers/\n", encoding="utf-8"
        )
        self.assert_validator_rejects(
            "scratch_reason_missing", "--scratch-path", scratch
        )

    def test_ignored_untracked_unstaged_scratch_is_allowed(self) -> None:
        scratch = ".superpowers/local/notes.md"
        path = self.fixture.root / scratch
        path.parent.mkdir(parents=True)
        path.write_text("scratch\n", encoding="utf-8")
        self.assertEqual(
            ".gitignore:1:.superpowers/\t.superpowers/local/notes.md",
            run_git(self.fixture.root, "check-ignore", "-v", scratch).strip(),
        )
        self.assert_validator_accepts(
            "--scratch-path",
            scratch,
            "--scratch-reason",
            "tool requires a repository-local cache",
        )

    def test_tracked_path_cannot_be_nominated_as_scratch(self) -> None:
        tracked = self.fixture.root / MIGRATION_PATHS[0]
        tracked.parent.mkdir(parents=True)
        tracked.write_text("tracked\n", encoding="utf-8")
        run_git(self.fixture.root, "add", "-f", MIGRATION_PATHS[0])
        self.assert_validator_rejects(
            "scratch_state_invalid",
            "--scratch-path",
            MIGRATION_PATHS[0],
            "--scratch-reason",
            "tool requires a repository-local cache",
        )

    def test_current_index_entry_is_rejected(self) -> None:
        tracked = self.fixture.root / ".superpowers" / "tracked.md"
        tracked.parent.mkdir(parents=True)
        tracked.write_text("tracked\n", encoding="utf-8")
        run_git(self.fixture.root, "add", "-f", ".superpowers/tracked.md")
        self.assert_validator_rejects("index_entry")

    def test_nominated_candidate_tree_entry_is_rejected(self) -> None:
        candidate_tree = self.fixture.contaminated_tree()
        self.assert_validator_rejects(
            "candidate_tree_entry", "--candidate-tree", candidate_tree
        )

    def test_post_policy_new_commit_entry_is_rejected(self) -> None:
        new_commit = self.fixture.contaminated_commit()
        self.assert_validator_rejects("new_commit_entry", "--new-commit", new_commit)

    def test_final_tree_entry_is_rejected(self) -> None:
        final_tree = self.fixture.contaminated_tree()
        self.assert_validator_rejects("final_tree_entry", "--final-tree", final_tree)

    def test_staged_deletion_and_historical_ancestor_blob_are_allowed(self) -> None:
        baseline = self.fixture.commit_migration_baseline()
        run_git(self.fixture.root, "rm", "--cached", *MIGRATION_PATHS)
        self.assertEqual(
            "", run_git(self.fixture.root, "ls-files", "--stage", "--", ".superpowers")
        )
        self.assertTrue(
            run_git(
                self.fixture.root, "ls-tree", "-r", baseline, "--", ".superpowers"
            ).strip()
        )
        self.assert_validator_accepts()


if __name__ == "__main__":
    unittest.main()
