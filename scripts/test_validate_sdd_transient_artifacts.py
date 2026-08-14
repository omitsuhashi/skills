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
        run_git(self.root, "commit", "-m", "pre-amendment reports")
        return run_git(self.root, "rev-parse", "HEAD").strip()

    def contaminated_tree(self, relative_path: str = ".superpowers/contaminated.md") -> str:
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


class AuthorizedRepositoryFixture:
    def __init__(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "repository"
        subprocess.run(
            ["git", "clone", "--quiet", "--no-hardlinks", str(REPOSITORY_ROOT), str(self.root)],
            check=True,
            capture_output=True,
            text=True,
        )
        run_git(self.root, "config", "user.name", "Test User")
        run_git(self.root, "config", "user.email", "test@example.invalid")

    def close(self) -> None:
        self.temporary_directory.cleanup()

    def install_counterfeit_baseline(self, mutation: str) -> tuple[str, ...]:
        run_git(self.root, "read-tree", f"{AMENDMENT_MIGRATION_BASELINE}^{{tree}}")
        first_mode, _, first_blob_and_path = EXPECTED_BASELINE_ENTRIES[0].partition(" blob ")
        first_blob, _, first_path = first_blob_and_path.partition("\t")
        if mutation == "mode":
            run_git(
                self.root,
                "update-index",
                "--cacheinfo",
                f"100755,{first_blob},{first_path}",
            )
        elif mutation == "blob":
            wrong_blob = hash_blob(self.root, "counterfeit report\n")
            run_git(
                self.root,
                "update-index",
                "--cacheinfo",
                f"{first_mode},{wrong_blob},{first_path}",
            )
        elif mutation == "path":
            run_git(self.root, "update-index", "--force-remove", first_path)
            run_git(
                self.root,
                "update-index",
                "--add",
                "--cacheinfo",
                f"{first_mode},{first_blob},{first_path}.renamed",
            )
        else:
            raise ValueError(f"unknown counterfeit mutation: {mutation}")
        counterfeit_tree = run_git(self.root, "write-tree").strip()
        counterfeit_commit = run_git(
            self.root,
            "commit-tree",
            counterfeit_tree,
            "-m",
            f"counterfeit baseline {mutation}",
        ).strip()
        run_git(self.root, "read-tree", "HEAD")
        run_git(self.root, "replace", AMENDMENT_MIGRATION_BASELINE, counterfeit_commit)
        return tuple(
            line
            for line in run_git(
                self.root,
                "ls-tree",
                "-r",
                AMENDMENT_MIGRATION_BASELINE,
                "--",
                ".superpowers",
            ).splitlines()
            if line
        )


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

    def test_only_the_immutable_authorized_baseline_can_enable_precleanup_migration(self) -> None:
        authorized = AuthorizedRepositoryFixture()
        try:
            self.assert_validator_accepts(
                "--migration-baseline",
                AMENDMENT_MIGRATION_BASELINE,
                repository=authorized.root,
            )
            alternate = run_git(authorized.root, "rev-parse", "HEAD^").strip()
            self.assertNotEqual(AMENDMENT_MIGRATION_BASELINE, alternate)
            self.assert_validator_rejects(
                "migration_baseline_unauthorized",
                "--migration-baseline",
                alternate,
                repository=authorized.root,
            )
        finally:
            authorized.close()

    def test_authorized_baseline_rejects_wrong_mode_blob_or_path(self) -> None:
        for mutation in ("mode", "blob", "path"):
            with self.subTest(mutation=mutation):
                authorized = AuthorizedRepositoryFixture()
                try:
                    counterfeit = authorized.install_counterfeit_baseline(mutation)
                    self.assertNotEqual(EXPECTED_BASELINE_ENTRIES, counterfeit)
                    self.assert_validator_rejects(
                        "migration_baseline_mismatch",
                        "--migration-baseline",
                        AMENDMENT_MIGRATION_BASELINE,
                        repository=authorized.root,
                    )
                finally:
                    authorized.close()

    def test_authorized_baseline_rejects_additional_current_index_entry(self) -> None:
        authorized = AuthorizedRepositoryFixture()
        try:
            additional = authorized.root / ".superpowers" / "additional.md"
            additional.write_text("additional\n", encoding="utf-8")
            run_git(authorized.root, "add", "-f", ".superpowers/additional.md")
            self.assert_validator_rejects(
                "migration_baseline_mismatch",
                "--migration-baseline",
                AMENDMENT_MIGRATION_BASELINE,
                repository=authorized.root,
            )
        finally:
            authorized.close()

    def test_authorized_baseline_rejects_changed_staged_report(self) -> None:
        authorized = AuthorizedRepositoryFixture()
        try:
            changed = authorized.root / MIGRATION_PATHS[0]
            changed.write_text("changed report\n", encoding="utf-8")
            run_git(authorized.root, "add", "-f", MIGRATION_PATHS[0])
            self.assert_validator_rejects(
                "migration_baseline_mismatch",
                "--migration-baseline",
                AMENDMENT_MIGRATION_BASELINE,
                repository=authorized.root,
            )
        finally:
            authorized.close()

    def test_repository_local_scratch_requires_ignore_coverage_and_concrete_reason(self) -> None:
        scratch = ".superpowers/local/notes.md"
        (self.fixture.root / ".gitignore").write_text("", encoding="utf-8")
        self.assert_validator_rejects(
            "scratch_ignore_missing",
            "--scratch-path",
            scratch,
            "--scratch-reason",
            "tool requires a repository-local cache",
        )

        (self.fixture.root / ".gitignore").write_text(".superpowers/\n", encoding="utf-8")
        self.assert_validator_rejects("scratch_reason_missing", "--scratch-path", scratch)

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

    def test_current_index_entry_is_rejected_without_other_contaminated_surfaces(self) -> None:
        tracked = self.fixture.root / ".superpowers" / "tracked.md"
        tracked.parent.mkdir(parents=True)
        tracked.write_text("tracked\n", encoding="utf-8")
        run_git(self.fixture.root, "add", "-f", ".superpowers/tracked.md")
        self.assertEqual("", run_git(self.fixture.root, "ls-tree", "-r", "HEAD", "--", ".superpowers"))
        self.assert_validator_rejects("index_entry")

    def test_nominated_candidate_tree_entry_is_rejected_with_clean_current_index(self) -> None:
        candidate_tree = self.fixture.contaminated_tree()
        self.assertEqual("", run_git(self.fixture.root, "ls-files", "--stage", "--", ".superpowers"))
        self.assertEqual("", run_git(self.fixture.root, "ls-tree", "-r", "HEAD", "--", ".superpowers"))
        self.assert_validator_rejects(
            "candidate_tree_entry", "--candidate-tree", candidate_tree
        )

    def test_post_cleanup_new_commit_entry_is_rejected_with_clean_index_and_head(self) -> None:
        new_commit = self.fixture.contaminated_commit()
        self.assertEqual("", run_git(self.fixture.root, "ls-files", "--stage", "--", ".superpowers"))
        self.assertEqual("", run_git(self.fixture.root, "ls-tree", "-r", "HEAD", "--", ".superpowers"))
        self.assert_validator_rejects("new_commit_entry", "--new-commit", new_commit)

    def test_final_tree_entry_is_rejected_with_clean_index_and_head(self) -> None:
        final_tree = self.fixture.contaminated_tree()
        self.assertEqual("", run_git(self.fixture.root, "ls-files", "--stage", "--", ".superpowers"))
        self.assertEqual("", run_git(self.fixture.root, "ls-tree", "-r", "HEAD", "--", ".superpowers"))
        self.assert_validator_rejects("final_tree_entry", "--final-tree", final_tree)

    def test_staged_deletion_and_historical_ancestor_blob_are_allowed(self) -> None:
        baseline = self.fixture.commit_migration_baseline()
        run_git(self.fixture.root, "rm", "--cached", *MIGRATION_PATHS)
        self.assertEqual("", run_git(self.fixture.root, "ls-files", "--stage", "--", ".superpowers"))
        self.assertTrue(run_git(self.fixture.root, "ls-tree", "-r", baseline, "--", ".superpowers").strip())
        self.assert_validator_accepts()


if __name__ == "__main__":
    unittest.main()
