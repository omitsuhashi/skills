from __future__ import annotations
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from tests.harnesses.fail_closed_scenario import (  # noqa: E402
    ControlReturn,
    ScopedWriter,
    run_repository_change,
)

def run_git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout

def fingerprint(root: Path) -> tuple[str, str, str, str, str, str, tuple[tuple[str, bytes], ...]]:
    untracked = tuple(name for name in run_git(root, "ls-files", "--others", "--exclude-standard", "-z").split("\0") if name)
    return (
        run_git(root, "branch", "--show-current").strip(),
        run_git(root, "rev-parse", "HEAD").strip(),
        run_git(root, "ls-files", "--stage", "-z"),
        run_git(root, "diff", "--cached", "--binary"),
        run_git(root, "diff", "--binary"),
        run_git(root, "status", "--porcelain=v1", "--untracked-files=all"),
        tuple((name, (root / name).read_bytes()) for name in untracked),
    )

class NativeWorktreeContractTests(unittest.TestCase):
    def make_repository(self, root: Path) -> None:
        run_git(root, "init", "-b", "main")
        run_git(root, "config", "user.name", "Test User")
        run_git(root, "config", "user.email", "test@example.invalid")
        (root / "tracked.txt").write_text("base\n", encoding="utf-8")
        run_git(root, "add", "tracked.txt")
        run_git(root, "commit", "-m", "base")

    def test_clean_default_branch_allocation_is_isolated(self) -> None:
        """Catches writing or committing task work on the original main branch."""
        with tempfile.TemporaryDirectory() as directory:
            original, planning = Path(directory) / "original", Path(directory) / "planning"
            original.mkdir(); self.make_repository(original)
            branch, sha = run_git(original, "branch", "--show-current").strip(), run_git(original, "rev-parse", "HEAD").strip()
            self.assertEqual("main", branch)
            before = fingerprint(original)
            self.assertEqual("", before[5])
            integration_branch = "integration/default"
            run_git(original, "worktree", "add", "-b", integration_branch, str(planning), sha)
            report = planning / ".superpowers/research/default/report.md"; report.parent.mkdir(parents=True); report.write_text("report\n", encoding="utf-8")
            run_git(planning, "add", ".superpowers/research/default/report.md")
            run_git(planning, "commit", "-m", "task report")
            self.assertEqual(integration_branch, run_git(planning, "branch", "--show-current").strip())
            self.assertNotEqual(branch, integration_branch)
            run_git(planning, "merge-base", "--is-ancestor", branch, integration_branch)
            self.assertNotEqual(sha, run_git(planning, "rev-parse", "HEAD").strip())
            self.assertEqual(before, fingerprint(original))
            self.assertFalse((original / ".superpowers/research/default/report.md").exists())

    def test_dirty_named_branch_preserves_all_status_categories(self) -> None:
        """Catches allocation mutating any original checkout status category."""
        with tempfile.TemporaryDirectory() as directory:
            original, planning = Path(directory) / "original", Path(directory) / "planning"
            original.mkdir(); self.make_repository(original)
            run_git(original, "switch", "-c", "feature/start")
            (original / "unstaged.txt").write_text("committed\n", encoding="utf-8"); run_git(original, "add", "unstaged.txt"); run_git(original, "commit", "-m", "second tracked file")
            (original / "tracked.txt").write_text("staged\n", encoding="utf-8"); run_git(original, "add", "tracked.txt")
            (original / "unstaged.txt").write_text("unstaged\n", encoding="utf-8"); (original / "untracked.txt").write_text("untracked\n", encoding="utf-8")
            branch, sha = run_git(original, "branch", "--show-current").strip(), run_git(original, "rev-parse", "HEAD").strip()
            before = fingerprint(original)
            self.assertTrue(before[3]); self.assertTrue(before[4]); self.assertIn("?? untracked.txt", before[5])
            integration_branch = "integration/epic-42"
            run_git(original, "worktree", "add", "-b", integration_branch, str(planning), sha)
            report = planning / ".superpowers/research/epic-42/report.md"; report.parent.mkdir(parents=True); report.write_text("report\n", encoding="utf-8")
            self.assertEqual("feature/start", branch); self.assertEqual(sha, run_git(planning, "rev-parse", "HEAD").strip())
            self.assertEqual(integration_branch, run_git(planning, "branch", "--show-current").strip())
            self.assertNotEqual(branch, integration_branch)
            run_git(planning, "merge-base", "--is-ancestor", branch, integration_branch)
            self.assertEqual(before, fingerprint(original))
            self.assertTrue(report.is_relative_to(planning)); self.assertFalse((original / ".superpowers/research/epic-42/report.md").exists())

    def test_failed_allocation_preserves_original_and_creates_no_report(self) -> None:
        """Catches a failed allocation falling back to either available checkout."""
        with tempfile.TemporaryDirectory() as directory:
            original, first, failed = Path(directory) / "original", Path(directory) / "first", Path(directory) / "failed"
            original.mkdir(); self.make_repository(original)
            (original / "unstaged.txt").write_text("committed\n", encoding="utf-8"); run_git(original, "add", "unstaged.txt"); run_git(original, "commit", "-m", "second tracked file")
            (original / "tracked.txt").write_text("staged\n", encoding="utf-8"); run_git(original, "add", "tracked.txt")
            (original / "unstaged.txt").write_text("unstaged\n", encoding="utf-8")
            (original / "failed-untracked.txt").write_bytes(b"failed-allocation-untracked\n")
            starting_branch = run_git(original, "branch", "--show-current").strip()
            sha = run_git(original, "rev-parse", "HEAD").strip()
            before = fingerprint(original)
            self.assertTrue(before[3]); self.assertTrue(before[4])
            self.assertEqual((("failed-untracked.txt", b"failed-allocation-untracked\n"),), before[6])
            integration_branch = "integration/existing"
            run_git(original, "worktree", "add", "-b", integration_branch, str(first), sha)
            self.assertEqual(integration_branch, run_git(first, "branch", "--show-current").strip())
            self.assertNotEqual(starting_branch, integration_branch)
            run_git(first, "merge-base", "--is-ancestor", starting_branch, integration_branch)
            first_before = fingerprint(first)

            def colliding_allocator() -> Path:
                run_git(
                    original,
                    "worktree",
                    "add",
                    "-b",
                    "integration/existing",
                    str(failed),
                    sha,
                )
                return failed

            def writer(capability: ScopedWriter) -> tuple[Path, ...]:
                report = failed / ".superpowers/research/failed/report.md"
                return (capability.write(report, b"unexpected fallback\n"),)

            result = run_repository_change(
                original=original,
                entry_skill="sdd-implementation",
                task_worktree=failed,
                cwd=failed,
                writable_paths=(failed / ".superpowers/research/failed/report.md",),
                allocator=colliding_allocator,
                downstream_command=None,
                command_runner=lambda command: 0,
                writer=writer,
            )
            self.assertEqual(
                ControlReturn("blocked", "none", "none", "worktree allocation failed"),
                result.control_return,
            )
            self.assertEqual(0, result.writer_invocations)
            self.assertEqual(before, fingerprint(original))
            self.assertEqual(first_before, fingerprint(first))
            self.assertFalse((failed / ".superpowers/research/failed/report.md").exists())
            self.assertFalse((original / ".superpowers/research/failed/report.md").exists())
            self.assertFalse((first / ".superpowers/research/failed/report.md").exists())

if __name__ == "__main__":
    unittest.main()
