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
    run_repository_change,
)


def run_git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


class FailClosedEntryBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.original = self.root / "original"
        self.planning = self.root / "planning"
        self.original.mkdir()
        run_git(self.original, "init", "-b", "main")
        run_git(self.original, "config", "user.name", "Test User")
        run_git(self.original, "config", "user.email", "test@example.invalid")
        (self.original / "tracked.txt").write_text("base\n", encoding="utf-8")
        run_git(self.original, "add", "tracked.txt")
        run_git(self.original, "commit", "-m", "base")
        self.head = run_git(self.original, "rev-parse", "HEAD").strip()
        self.writer_calls = 0
        self.runner_calls = 0
        self.allocation_calls = 0

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def allocate(self) -> Path:
        self.allocation_calls += 1
        run_git(
            self.original,
            "worktree",
            "add",
            "-b",
            f"codex/scenario/planning-{self.allocation_calls}",
            str(self.planning),
            self.head,
        )
        return self.planning

    def write_report(self, planning: Path) -> None:
        self.writer_calls += 1
        report = planning / ".superpowers" / "research" / "scenario" / "report.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("report\n", encoding="utf-8")

    def no_op_writer(self, planning: Path) -> None:
        self.writer_calls += 1
        self.assertEqual(self.planning.resolve(), planning.resolve())

    def run_command(self, command: tuple[str, ...]) -> int:
        self.runner_calls += 1
        return subprocess.run(command, check=False).returncode

    def assert_no_repository_artifacts(self) -> None:
        for root in (self.original, self.planning):
            for relative in (
                ".superpowers/research/scenario/report.md",
                "knowledge/wiki/drafts/scenario-spec.md",
                "knowledge/wiki/syntheses/scenario-plan.md",
            ):
                self.assertFalse((root / relative).exists(), relative)

    def assert_blocked(self, result, reason: str, *, attempted=()) -> None:
        self.assertEqual(ControlReturn("blocked", "none", "none", reason), result.control_return)
        self.assertEqual(0, result.writer_invocations)
        self.assertEqual(0, result.runner_invocations)
        self.assertEqual(tuple(attempted), result.attempted_commands)
        self.assertEqual((), result.executed_commands)
        self.assertEqual(result.before, result.after)
        self.assertEqual(result.before.commit_count, result.after.commit_count)
        self.assertEqual(0, self.writer_calls)
        self.assertEqual(0, self.runner_calls)
        self.assert_no_repository_artifacts()

    def call(self, **overrides):
        arguments = {
            "original": self.original,
            "entry_skill": "sdd-implementation",
            "allocator": self.allocate,
            "writer": self.write_report,
            "downstream_command": None,
            "command_runner": self.run_command,
        }
        arguments.update(overrides)
        return run_repository_change(**arguments)

    def test_verified_linked_worktree_completes_without_guard_bootstrap_inputs(self) -> None:
        """Catches requiring obsolete guard/bootstrap state before the writer."""
        result = self.call()
        self.assertEqual(ControlReturn("complete", "none", "none", "none"), result.control_return)
        self.assertEqual(1, result.writer_invocations)
        self.assertEqual(0, result.runner_invocations)
        self.assertEqual((), result.attempted_commands)
        self.assertEqual((), result.executed_commands)
        self.assertEqual(result.before, result.after)
        self.assertEqual(1, self.writer_calls)
        self.assertTrue(
            (self.planning / ".superpowers/research/scenario/report.md").is_file()
        )
        self.assertFalse(
            (self.original / ".superpowers/research/scenario/report.md").exists()
        )

    def test_primary_main_is_blocked_before_writer_or_runner(self) -> None:
        """Catches accepting the original primary checkout as the writable root."""
        result = self.call(allocator=lambda: self.original)
        self.assert_blocked(
            result,
            "worktree registration/ownership/containment not proven",
        )

    def test_direct_writable_subskill_is_blocked_before_callback(self) -> None:
        """Catches bypassing SDD and reaching a writer or runner directly."""
        for entry_skill in (
            "superpowers:brainstorming",
            "superpowers:writing-plans",
            "superpowers:using-git-worktrees",
            "implementation",
        ):
            with self.subTest(entry_skill=entry_skill):
                result = self.call(entry_skill=entry_skill)
                self.assert_blocked(result, "SDD First-Write Worktree Gate required")

    def test_conflicting_downstream_command_is_recorded_but_not_executed(self) -> None:
        """Catches executing a downstream command that violates SDD containment."""
        marker = self.root / "unsafe-marker"
        fixture = SKILL_DIR / "tests" / "fixtures" / "unsafe_downstream.py"
        command = (sys.executable, str(fixture), str(marker))
        result = self.call(downstream_command=command)
        self.assert_blocked(
            result,
            "downstream incompatible with SDD containment",
            attempted=(command,),
        )
        self.assertFalse(marker.exists())

if __name__ == "__main__":
    unittest.main()
