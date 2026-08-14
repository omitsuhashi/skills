from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate_sdd_transient_artifacts.py"
AMENDMENT_MIGRATION_BASELINE = "f07aebce7bbf854cd64184311d204cf04055fd28"
MIGRATION_PATHS = (
    ".superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/approved-residual-fix-report.md",
    ".superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/final-fix-report.md",
    ".superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/task-2-report.md",
)
EXPECTED_BASELINE_ENTRIES = (
    "100644 blob b50ed8e434725cb70bc0f1d2c6daa1a053e0ccc1\t" + MIGRATION_PATHS[0],
    "100644 blob c884197bf566cc93f319f3c2a1b6d2ad1563d10e\t" + MIGRATION_PATHS[1],
    "100644 blob da22b7580961fb9a2087ab1eb034fb34000711f8\t" + MIGRATION_PATHS[2],
)


def run_git(repository: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


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
        run_git(self.root, "commit", "-m", "pre-amendment reports")
        return run_git(self.root, "rev-parse", "HEAD").strip()


class TransientArtifactValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def run_validator(self, *args: str) -> subprocess.CompletedProcess[str]:
        self.assertTrue(
            VALIDATOR.is_file(),
            f"repository transient-artifact validator is missing: {VALIDATOR}",
        )
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--repository",
                str(self.fixture.root),
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def assert_validator_accepts(self, *args: str) -> None:
        result = self.run_validator(*args)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def assert_validator_rejects(self, *args: str) -> None:
        result = self.run_validator(*args)
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)

    def test_single_use_baseline_commit_preserves_the_exact_three_mode_blob_path_entries(self) -> None:
        actual = tuple(
            line
            for line in run_git(
                REPOSITORY_ROOT,
                "ls-tree",
                "-r",
                AMENDMENT_MIGRATION_BASELINE,
                "--",
                ".superpowers",
            ).splitlines()
            if line
        )
        self.assertEqual(EXPECTED_BASELINE_ENTRIES, actual)

    def test_exact_inherited_three_path_migration_baseline_is_the_only_precleanup_allowance(self) -> None:
        baseline = self.fixture.commit_migration_baseline()
        self.assert_validator_accepts("--migration-baseline", baseline)

        additional = self.fixture.root / ".superpowers" / "additional.md"
        additional.write_text("additional\n", encoding="utf-8")
        run_git(self.fixture.root, "add", "-f", str(additional.relative_to(self.fixture.root)))
        self.assert_validator_rejects("--migration-baseline", baseline)

    def test_changed_or_staged_migration_report_is_rejected(self) -> None:
        baseline = self.fixture.commit_migration_baseline()
        changed = self.fixture.root / MIGRATION_PATHS[0]
        changed.write_text("changed report\n", encoding="utf-8")
        run_git(self.fixture.root, "add", "-f", MIGRATION_PATHS[0])
        self.assert_validator_rejects("--migration-baseline", baseline)

    def test_repository_local_scratch_requires_ignore_coverage_and_concrete_reason(self) -> None:
        scratch = ".superpowers/local/notes.md"
        (self.fixture.root / ".gitignore").write_text("", encoding="utf-8")
        self.assert_validator_rejects(
            "--scratch-path", scratch, "--scratch-reason", "tool requires a repository-local cache"
        )

        (self.fixture.root / ".gitignore").write_text(".superpowers/\n", encoding="utf-8")
        self.assert_validator_rejects("--scratch-path", scratch)

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
            "--scratch-path", scratch, "--scratch-reason", "tool requires a repository-local cache"
        )

    def test_tracked_and_candidate_tree_entries_are_rejected_after_cleanup(self) -> None:
        tracked = self.fixture.root / ".superpowers" / "tracked.md"
        tracked.parent.mkdir(parents=True)
        tracked.write_text("tracked\n", encoding="utf-8")
        run_git(self.fixture.root, "add", "-f", ".superpowers/tracked.md")
        candidate_tree = run_git(self.fixture.root, "write-tree").strip()
        self.assert_validator_rejects("--treeish", candidate_tree)

    def test_staged_deletion_and_historical_ancestor_blob_are_allowed(self) -> None:
        baseline = self.fixture.commit_migration_baseline()
        run_git(self.fixture.root, "rm", "--cached", *MIGRATION_PATHS)
        self.assert_validator_accepts()
        self.assertTrue(run_git(self.fixture.root, "ls-tree", "-r", baseline, "--", ".superpowers").strip())

    def test_cleanup_commit_reintroduction_is_rejected(self) -> None:
        self.fixture.commit_migration_baseline()
        run_git(self.fixture.root, "rm", "--cached", *MIGRATION_PATHS)
        run_git(self.fixture.root, "commit", "-m", "remove reports from final tree")
        reintroduced = self.fixture.root / ".superpowers" / "reintroduced.md"
        reintroduced.write_text("reintroduced\n", encoding="utf-8")
        run_git(self.fixture.root, "add", "-f", ".superpowers/reintroduced.md")
        run_git(self.fixture.root, "commit", "-m", "reintroduce transient artifact")
        self.assert_validator_rejects("--treeish", "HEAD")


if __name__ == "__main__":
    unittest.main()
