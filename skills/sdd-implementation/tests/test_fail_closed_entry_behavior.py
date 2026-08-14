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
    BoundWorktree,
    ControlReturn,
    bind_task_worktree,
    mint_task_owner_capability,
    run_repository_change,
)
from tests.harnesses import fail_closed_scenario  # noqa: E402


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
        self.report = self.planning / "report.md"
        self.original.mkdir()
        run_git(self.original, "init", "-b", "main")
        run_git(self.original, "config", "user.name", "Test User")
        run_git(self.original, "config", "user.email", "test@example.invalid")
        (self.original / "tracked.txt").write_text("base\n", encoding="utf-8")
        run_git(self.original, "add", "tracked.txt")
        run_git(self.original, "commit", "-m", "base")
        self.head = run_git(self.original, "rev-parse", "HEAD").strip()
        self.allocation_calls = 0
        self.owner = mint_task_owner_capability()
        self.task_worktree = bind_task_worktree(self.planning, self.owner)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def allocate(self) -> BoundWorktree:
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
        return bind_task_worktree(self.planning, self.owner)

    def assert_no_repository_artifacts(self) -> None:
        for root in (self.original, self.planning):
            for relative in (
                ".superpowers/research/scenario/report.md",
                "knowledge/wiki/drafts/scenario-spec.md",
                "knowledge/wiki/syntheses/scenario-plan.md",
                "report.md",
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
        self.assert_no_repository_artifacts()

    def call(self, **overrides):
        arguments = {
            "original": self.original,
            "entry_skill": "sdd-implementation",
            "task_worktree": self.task_worktree,
            "cwd": self.planning,
            "writable_paths": (self.report,),
            "write_plan": ((self.report, b"report\n"),),
            "output_paths": (self.report,),
            "allocator": self.allocate,
            "command_plan": None,
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
            (self.planning / "report.md").is_file()
        )
        self.assertFalse(
            (self.original / "report.md").exists()
        )

    def test_non_task_linked_worktree_is_blocked_before_writer(self) -> None:
        """Catches accepting another workflow's registered linked worktree."""
        foreign = self.root / "foreign"

        def allocate_foreign() -> BoundWorktree:
            run_git(
                self.original,
                "worktree",
                "add",
                "-b",
                "codex/foreign/planning",
                str(foreign),
                self.head,
            )
            return bind_task_worktree(foreign, self.owner)

        result = self.call(allocator=allocate_foreign)
        self.assert_blocked(result, "task worktree binding not proven")
        self.assertFalse((foreign / ".superpowers/research/scenario/report.md").exists())

    def test_allocator_ignored_original_artifact_is_blocked_before_writer(self) -> None:
        """Catches preservation evidence omitting ignored original artifacts."""
        (self.original / ".gitignore").write_text(".superpowers/\n", encoding="utf-8")
        run_git(self.original, "add", ".gitignore")
        run_git(self.original, "commit", "-m", "ignore transient artifacts")
        self.head = run_git(self.original, "rev-parse", "HEAD").strip()
        leak = self.original / ".superpowers/leak.md"

        def allocate_with_ignored_original_artifact() -> BoundWorktree:
            allocation = self.allocate()
            leak.parent.mkdir()
            leak.write_bytes(b"leak\n")
            return allocation

        result = self.call(allocator=allocate_with_ignored_original_artifact)

        self.assertEqual(
            ControlReturn(
                "blocked",
                "none",
                "none",
                "original checkout preservation not proven",
            ),
            result.control_return,
        )
        self.assertEqual(0, result.writer_invocations)
        self.assertEqual(0, result.runner_invocations)
        self.assertNotEqual(result.before, result.after)
        self.assertIn(
            (".superpowers/leak.md", b"leak\n"),
            result.after.tracked_and_untracked,
        )
        self.assertTrue(leak.is_file())
        self.assertFalse(self.report.exists())

    def test_foreign_owner_for_expected_path_is_blocked_before_writer(self) -> None:
        """Catches treating path equality as task ownership evidence."""
        foreign_owner = mint_task_owner_capability()

        def allocate_foreign_owner() -> BoundWorktree:
            self.allocate()
            return bind_task_worktree(self.planning, foreign_owner)

        result = self.call(allocator=allocate_foreign_owner)
        self.assert_blocked(result, "task worktree ownership not proven")

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

    def test_multiple_artifact_plan_is_blocked_before_writer(self) -> None:
        """Catches reintroducing a best-effort multi-output transaction."""
        second = self.planning / "second-report.md"
        result = self.call(
            writable_paths=(self.report, second),
            write_plan=((self.report, b"report\n"), (second, b"second\n")),
            output_paths=(self.report, second),
        )
        self.assertEqual(
            ControlReturn("blocked", "none", "none", "new artifact binding not proven"),
            result.control_return,
        )
        self.assertEqual(0, result.writer_invocations)
        self.assertEqual(result.before, result.after)
        self.assertFalse(self.report.exists())
        self.assertFalse(second.exists())

    def test_preexisting_artifact_is_blocked_before_writer(self) -> None:
        """Catches pretending an overwrite can provide zero-write rollback."""
        def allocate_with_existing_report() -> BoundWorktree:
            allocation = self.allocate()
            self.report.write_bytes(b"existing\n")
            return allocation

        result = self.call(allocator=allocate_with_existing_report)
        self.assertEqual(
            ControlReturn("blocked", "none", "none", "new artifact binding not proven"),
            result.control_return,
        )
        self.assertEqual(0, result.writer_invocations)
        self.assertEqual(b"existing\n", self.report.read_bytes())

    def test_publish_failure_leaves_no_target_or_staging_artifact(self) -> None:
        """Catches a failed atomic publish leaking repository artifacts."""
        with mock.patch.object(
            fail_closed_scenario.os,
            "replace",
            side_effect=OSError(errno.EIO, "injected publish failure"),
        ):
            result = self.call()

        self.assertEqual(
            ControlReturn("blocked", "none", "none", "artifact publish failed"),
            result.control_return,
        )
        self.assertEqual(1, result.writer_invocations)
        self.assertFalse(self.report.exists())
        self.assertEqual([], list(self.planning.glob(".sdd-stage-*")))

    def test_writer_construction_failure_is_zero_write_blocked(self) -> None:
        """Catches path/dependency failure escaping while the scoped writer is built."""
        with mock.patch.object(
            fail_closed_scenario,
            "ScopedWriter",
            side_effect=FileNotFoundError(errno.ENOENT, "writer dependency missing"),
        ):
            result = self.call()

        self.assertEqual(
            ControlReturn("blocked", "none", "none", "artifact writer unavailable"),
            result.control_return,
        )
        self.assertEqual(0, result.writer_invocations)
        self.assertFalse(self.report.exists())

    def test_write_plan_is_required(self) -> None:
        """Catches completing without a data-only write plan."""
        result = self.call(write_plan=None, output_paths=())
        self.assert_blocked(result, "writer plan not bound")

    def test_primary_main_is_blocked_before_writer_or_runner(self) -> None:
        """Catches accepting the original primary checkout as the writable root."""
        result = self.call(
            allocator=lambda: bind_task_worktree(self.original, self.owner)
        )
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

    def test_original_cwd_commit_is_blocked_before_native_runner(self) -> None:
        """Catches committing through the gate from the original checkout."""
        allocation = self.allocate()
        command = ("git", "commit", "-m", "task commit")
        result = self.call(
            allocator=lambda: allocation,
            cwd=self.original,
            writable_paths=(),
            write_plan=None,
            output_paths=(),
            command_plan=command,
        )
        self.assert_blocked(result, "commit binding not proven", attempted=(command,))

    def test_stale_cwd_commit_is_blocked_before_native_runner(self) -> None:
        """Catches committing through the gate from a sibling worktree."""
        allocation = self.allocate()
        stale = self.root / "stale"
        run_git(self.original, "worktree", "add", "-b", "codex/stale", str(stale), self.head)
        command = ("git", "commit", "-m", "task commit")
        result = self.call(
            allocator=lambda: allocation,
            cwd=stale,
            writable_paths=(),
            write_plan=None,
            output_paths=(),
            command_plan=command,
        )
        self.assert_blocked(result, "commit binding not proven", attempted=(command,))

    def test_conflicting_downstream_command_is_recorded_but_not_executed(self) -> None:
        """Catches executing a downstream command that violates SDD containment."""
        marker = self.root / "unsafe-marker"
        fixture = SKILL_DIR / "tests" / "fixtures" / "unsafe_downstream.py"
        command = (sys.executable, str(fixture), str(marker))
        result = self.call(command_plan=command)
        self.assert_blocked(
            result,
            "downstream incompatible with SDD containment",
            attempted=(command,),
        )
        self.assertFalse(marker.exists())

if __name__ == "__main__":
    unittest.main()
