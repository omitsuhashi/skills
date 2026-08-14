from __future__ import annotations

import errno
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from tests.harnesses.fail_closed_scenario import (  # noqa: E402
    ControlReturn,
    SandboxDenied,
    run_repository_change,
)


def run_git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


class FailClosedAllocationBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.original = self.root / "original"
        self.original.mkdir()
        run_git(self.original, "init", "-b", "main")
        run_git(self.original, "config", "user.name", "Test User")
        run_git(self.original, "config", "user.email", "test@example.invalid")
        (self.original / "tracked.txt").write_text("base\n", encoding="utf-8")
        run_git(self.original, "add", "tracked.txt")
        run_git(self.original, "commit", "-m", "base")
        self.runner_calls = 0

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def runner(self, command: tuple[str, ...]) -> int:
        self.runner_calls += 1
        return 0

    def assert_denial_is_zero_write(self, allocator, reason: str) -> None:
        result = run_repository_change(
            original=self.original,
            entry_skill="sdd-implementation",
            task_worktree=self.root / "planning",
            cwd=self.root / "planning",
            writable_paths=(
                self.root / "planning/.superpowers/research/scenario/report.md",
            ),
            bound_writer_owner="research-worker",
            writer_owner="research-worker",
            writer_requests=(
                (
                    self.root / "planning/.superpowers/research/scenario/report.md",
                    b"report\n",
                ),
            ),
            allocator=allocator,
            downstream_command=None,
            command_runner=self.runner,
        )
        self.assertEqual(ControlReturn("blocked", "none", "none", reason), result.control_return)
        self.assertEqual(0, result.writer_invocations)
        self.assertEqual(0, result.runner_invocations)
        self.assertEqual((), result.attempted_commands)
        self.assertEqual((), result.executed_commands)
        self.assertEqual(result.before, result.after)
        self.assertEqual(result.before.commit_count, result.after.commit_count)
        self.assertEqual(0, self.runner_calls)
        for relative in (
            ".superpowers/research/scenario/report.md",
            "knowledge/wiki/drafts/scenario-spec.md",
            "knowledge/wiki/syntheses/scenario-plan.md",
        ):
            self.assertFalse((self.original / relative).exists(), relative)
            self.assertFalse((self.root / "planning" / relative).exists(), relative)

    def test_eacces_is_zero_write_blocked(self) -> None:
        """Catches EACCES fallback to the primary checkout or any writer/runner."""
        def deny() -> Path:
            raise PermissionError(errno.EACCES, "permission denied")

        self.assert_denial_is_zero_write(
            deny,
            "worktree allocation denied: EACCES",
        )

    def test_sandbox_denial_is_zero_write_blocked(self) -> None:
        """Catches sandbox-denial fallback to any writable checkout."""
        def deny() -> Path:
            raise SandboxDenied("sandbox policy denied worktree allocation")

        self.assert_denial_is_zero_write(
            deny,
            "worktree allocation denied: sandbox",
        )


if __name__ == "__main__":
    unittest.main()
