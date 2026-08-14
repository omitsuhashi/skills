from __future__ import annotations

import errno
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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
        self.report = self.planning / ".superpowers/research/scenario/report.md"
        self.original.mkdir()
        run_git(self.original, "init", "-b", "main")
        run_git(self.original, "config", "user.name", "Test User")
        run_git(self.original, "config", "user.email", "test@example.invalid")
        (self.original / "tracked.txt").write_text("base\n", encoding="utf-8")
        run_git(self.original, "add", "tracked.txt")
        run_git(self.original, "commit", "-m", "base")
        self.head = run_git(self.original, "rev-parse", "HEAD").strip()
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
        self.assertEqual(0, self.runner_calls)
        self.assert_no_repository_artifacts()

    def call(self, **overrides):
        arguments = {
            "original": self.original,
            "entry_skill": "sdd-implementation",
            "task_worktree": self.planning,
            "cwd": self.planning,
            "writable_paths": (self.report,),
            "write_plan": ((self.report, b"report\n"),),
            "output_paths": (self.report,),
            "allocator": self.allocate,
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
        self.assertTrue(
            (self.planning / ".superpowers/research/scenario/report.md").is_file()
        )
        self.assertFalse(
            (self.original / ".superpowers/research/scenario/report.md").exists()
        )

    def test_non_task_linked_worktree_is_blocked_before_writer(self) -> None:
        """Catches accepting another workflow's registered linked worktree."""
        foreign = self.root / "foreign"

        def allocate_foreign() -> Path:
            run_git(
                self.original,
                "worktree",
                "add",
                "-b",
                "codex/foreign/planning",
                str(foreign),
                self.head,
            )
            return foreign

        result = self.call(allocator=allocate_foreign)
        self.assert_blocked(result, "task worktree binding not proven")
        self.assertFalse((foreign / ".superpowers/research/scenario/report.md").exists())

    def test_mismatched_cwd_is_blocked_before_writer(self) -> None:
        """Catches dispatching a writer from outside the bound task root."""
        result = self.call(cwd=self.original)
        self.assert_blocked(result, "write binding not proven")

    def test_escaped_writable_path_is_blocked_before_writer(self) -> None:
        """Catches a declared writable path escaping the task worktree."""
        result = self.call(writable_paths=(self.root / "escaped-report.md",))
        self.assert_blocked(result, "write binding not proven")

    def test_data_write_plan_targeting_original_is_zero_write_blocked(self) -> None:
        """Catches a collected data request targeting the original checkout."""
        original_report = self.original / "data-plan-report.md"
        result = self.call(
            write_plan=((original_report, b"unsafe\n"),),
            output_paths=(original_report,),
        )
        self.assertEqual(
            ControlReturn("blocked", "none", "none", "writer output binding not proven"),
            result.control_return,
        )
        self.assertEqual(0, result.writer_invocations)
        self.assertEqual(result.before, result.after)
        self.assertFalse(original_report.exists())

    def test_mismatched_data_outputs_leave_approved_target_unwritten(self) -> None:
        """Catches partial writes before the complete output contract is validated."""
        escaped = self.root / "data-plan-escape.md"
        result = self.call(
            write_plan=((self.report, b"report\n"),),
            output_paths=(self.report, escaped),
        )
        self.assertEqual(
            ControlReturn("blocked", "none", "none", "writer output binding not proven"),
            result.control_return,
        )
        self.assertEqual(0, result.writer_invocations)
        self.assertEqual(result.before, result.after)
        self.assertFalse(self.report.exists())
        self.assertFalse(escaped.exists())

    def test_runtime_failure_on_later_target_is_zero_write_blocked(self) -> None:
        """Catches a later filesystem failure leaving an earlier target written."""
        blocking_parent = self.planning / "blocked-parent"
        failed_target = blocking_parent / "result.md"

        def allocate_with_blocking_parent() -> Path:
            planning = self.allocate()
            blocking_parent.write_bytes(b"pre-existing blocker\n")
            return planning

        try:
            result = self.call(
                allocator=allocate_with_blocking_parent,
                writable_paths=(self.report, failed_target),
                write_plan=(
                    (self.report, b"partial write\n"),
                    (failed_target, b"must not be written\n"),
                ),
                output_paths=(self.report, failed_target),
            )
        except OSError as error:
            self.fail(
                "runtime filesystem failure propagated "
                f"with partial_write={self.report.exists()}: "
                f"{type(error).__name__}: {error}"
            )

        self.assertEqual(
            ControlReturn("blocked", "none", "none", "writer execution failed"),
            result.control_return,
        )
        self.assertEqual(1, result.writer_invocations)
        self.assertEqual(result.before, result.after)
        self.assertFalse(self.report.exists())
        self.assertFalse((self.planning / ".superpowers").exists())
        self.assertEqual(b"pre-existing blocker\n", blocking_parent.read_bytes())
        self.assertFalse(failed_target.exists())

    def test_runtime_failure_restores_preexisting_earlier_target(self) -> None:
        """Catches cleanup replacing the prior bytes or metadata of an existing file."""
        failed_target = self.planning / "second-report.md"
        original_write_bytes = Path.write_bytes
        original_metadata = None

        def allocate_with_existing_report() -> Path:
            nonlocal original_metadata
            planning = self.allocate()
            self.report.parent.mkdir(parents=True, exist_ok=True)
            self.report.write_bytes(b"original report\n")
            original_metadata = self.report.stat()
            return planning

        def fail_second_write(path: Path, content: bytes) -> int:
            if path.resolve(strict=False) == failed_target.resolve(strict=False):
                raise OSError(errno.EIO, "injected later-target failure", path)
            return original_write_bytes(path, content)

        with mock.patch.object(
            Path,
            "write_bytes",
            autospec=True,
            side_effect=fail_second_write,
        ):
            result = self.call(
                allocator=allocate_with_existing_report,
                writable_paths=(self.report, failed_target),
                write_plan=(
                    (self.report, b"replacement report\n"),
                    (failed_target, b"must not be written\n"),
                ),
                output_paths=(self.report, failed_target),
            )

        self.assertEqual(
            ControlReturn("blocked", "none", "none", "writer execution failed"),
            result.control_return,
        )
        self.assertEqual(1, result.writer_invocations)
        self.assertEqual(result.before, result.after)
        self.assertEqual(b"original report\n", self.report.read_bytes())
        self.assertIsNotNone(original_metadata)
        restored_metadata = self.report.stat()
        self.assertEqual(original_metadata.st_mode, restored_metadata.st_mode)
        self.assertEqual(original_metadata.st_mtime_ns, restored_metadata.st_mtime_ns)
        self.assertFalse(failed_target.exists())

    def test_write_plan_is_required(self) -> None:
        """Catches completing without a data-only write plan."""
        result = self.call(write_plan=None, output_paths=())
        self.assert_blocked(result, "writer plan not bound")

    def test_primary_main_is_blocked_before_writer_or_runner(self) -> None:
        """Catches accepting the original primary checkout as the writable root."""
        result = self.call(allocator=lambda: self.original)
        self.assert_blocked(
            result,
            "task worktree binding not proven",
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
