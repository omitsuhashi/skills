from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Optional
import unittest
from unittest.mock import patch

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from tests.harnesses import fail_closed_scenario as scenario  # noqa: E402
from tests.harnesses.fail_closed_scenario import (  # noqa: E402
    BootstrapContext,
    ControlReturn,
    run_repository_change,
)

BOOTSTRAP = BootstrapContext(
    epic="sdd-fail-closed-worktree-gate",
    branch="codex/sdd-fail-closed-worktree-gate/planning",
    worktree=Path(
        "/Users/omitsuhashi/repos/omitsuhashi/skills/.worktrees/"
        "sdd-fail-closed-worktree-gate-planning"
    ),
    starting_head_sha="c370fe14de1641aa5ee30b3fa001f4d857078091",
    same_controller=True,
    tuple_trusted=True,
    lifecycle="bootstrap",
    requested_scope="source",
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

    def trusted_bootstrap(
        self,
        *,
        requested_scope: str = "source",
        branch: Optional[str] = None,
        worktree: Optional[Path] = None,
        starting_head_sha: Optional[str] = None,
    ) -> BootstrapContext:
        return BootstrapContext(
            epic=BOOTSTRAP.epic,
            branch=branch or f"codex/scenario/planning-{self.allocation_calls + 1}",
            worktree=worktree or self.planning,
            starting_head_sha=starting_head_sha or self.head,
            same_controller=True,
            tuple_trusted=True,
            lifecycle="bootstrap",
            requested_scope=requested_scope,
        )

    def call(self, **overrides):
        approved_bootstrap = overrides.pop("approved_bootstrap", None)
        arguments = {
            "original": self.original,
            "entry_skill": "sdd-implementation",
            "guard_status": "active",
            "bootstrap": None,
            "allocator": self.allocate,
            "writer": self.write_report,
            "downstream_command": None,
            "command_runner": self.run_command,
        }
        arguments.update(overrides)
        if approved_bootstrap is None:
            return run_repository_change(**arguments)
        with patch.multiple(
            scenario,
            BOOTSTRAP_EPIC=approved_bootstrap.epic,
            BOOTSTRAP_BRANCH=approved_bootstrap.branch,
            BOOTSTRAP_WORKTREE=approved_bootstrap.worktree,
            BOOTSTRAP_STARTING_HEAD_SHA=approved_bootstrap.starting_head_sha,
        ):
            return run_repository_change(**arguments)

    def test_sdd_is_the_only_allowed_first_entry(self) -> None:
        result = self.call(writer=self.no_op_writer)
        self.assertEqual(ControlReturn("complete", "none", "none", "none"), result.control_return)
        self.assertEqual(1, result.writer_invocations)
        self.assertEqual(0, result.runner_invocations)
        self.assertEqual((), result.attempted_commands)
        self.assertEqual((), result.executed_commands)
        self.assertEqual(result.before, result.after)
        self.assertEqual(1, self.writer_calls)

    def test_direct_writable_subskill_is_blocked_before_callback(self) -> None:
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

    def test_bootstrap_observed_allocation_identity_mismatch_is_blocked(self) -> None:
        fixture = SKILL_DIR / "tests" / "fixtures" / "unsafe_downstream.py"
        alternate_base = run_git(
            self.original,
            "commit-tree",
            "HEAD^{tree}",
            "-p",
            self.head,
            "-m",
            "alternate allocation base",
        ).strip()
        for mismatch in ("path", "branch", "base"):
            with self.subTest(mismatch=mismatch):
                actual_path = self.root / f"planning-{mismatch}"
                actual_branch = f"codex/scenario/{mismatch}-actual"
                allocation_base = alternate_base if mismatch == "base" else self.head
                trusted = self.trusted_bootstrap(
                    branch=(
                        f"codex/scenario/{mismatch}-expected"
                        if mismatch == "branch"
                        else actual_branch
                    ),
                    worktree=(
                        self.root / "planning-path-expected"
                        if mismatch == "path"
                        else actual_path
                    ),
                )
                marker = self.root / f"bootstrap-{mismatch}-mismatch-marker"
                command = (sys.executable, str(fixture), str(marker))

                def allocate() -> Path:
                    run_git(
                        self.original,
                        "worktree",
                        "add",
                        "-b",
                        actual_branch,
                        str(actual_path),
                        allocation_base,
                    )
                    return actual_path

                self.planning = actual_path
                result = self.call(
                    guard_status="guard_missing",
                    bootstrap=trusted,
                    approved_bootstrap=trusted,
                    allocator=allocate,
                    downstream_command=command,
                )
                self.assert_blocked(
                    result,
                    "worktree bootstrap identity mismatch",
                    attempted=(command,),
                )
                self.assertFalse(marker.exists())

    def test_guard_failure_blocks_ordinary_task_without_writer(self) -> None:
        for guard_status in ("guard_missing", "guard_unconfigured", "guard_damaged"):
            with self.subTest(guard_status=guard_status):
                result = self.call(guard_status=guard_status)
                self.assert_blocked(result, guard_status)

    def test_exact_bootstrap_tuple_allows_only_source_test_spec_plan(self) -> None:
        for scope in ("source", "test", "spec", "plan"):
            with self.subTest(scope=scope):
                trusted = self.trusted_bootstrap(requested_scope=scope)
                result = self.call(
                    guard_status="guard_missing",
                    bootstrap=trusted,
                    approved_bootstrap=trusted,
                    writer=self.no_op_writer,
                )
                self.assertEqual(
                    ControlReturn("complete", "none", "none", "none"),
                    result.control_return,
                )
                self.assertEqual(1, result.writer_invocations)
                self.assertEqual(0, result.runner_invocations)
                self.assertEqual((), result.executed_commands)
                self.assertEqual(result.before, result.after)
                self.planning = self.root / f"planning-{scope}"

        self.planning = self.root / "planning-activation"
        self.writer_calls = 0
        trusted = self.trusted_bootstrap()
        blocked = self.call(
            guard_status="guard_missing",
            bootstrap=replace(trusted, requested_scope="activation"),
            approved_bootstrap=trusted,
        )
        self.assert_blocked(blocked, "guard_missing")

    def test_bootstrap_cannot_be_reused_or_reconstructed(self) -> None:
        trusted = self.trusted_bootstrap()
        mismatch_cases = {
            "epic": replace(trusted, epic="another-epic"),
            "branch": replace(trusted, branch="codex/another/planning"),
            "worktree": replace(trusted, worktree=Path("/tmp/another-worktree")),
            "starting_head_sha": replace(trusted, starting_head_sha="0" * 40),
            "different_controller": replace(trusted, same_controller=False),
            "untrusted_tuple": replace(trusted, tuple_trusted=False),
            "later_task": replace(trusted, lifecycle="later_task"),
            "activation_scope": replace(trusted, requested_scope="activation"),
            "tuple_loss": None,
        }
        for name, bootstrap in mismatch_cases.items():
            with self.subTest(name=name):
                result = self.call(
                    guard_status="guard_missing",
                    bootstrap=bootstrap,
                    approved_bootstrap=trusted,
                )
                self.assert_blocked(result, "guard_missing")


class PortableLifecycleContractTests(unittest.TestCase):
    def test_repository_source_completion_is_independent_from_operational_states(
        self,
    ) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        lifecycle = skill_text.split("## Lifecycle State Separation", 1)[1].split(
            "## Planning Controller", 1
        )[0]
        for state in (
            "`repository_source_completion`",
            "`active_installed_copy`",
            "`external_dependency_cache_state`",
            "`guard_activation`",
            "`operational_verification`",
        ):
            self.assertIn(state, lifecycle)
        self.assertIn(
            "Success in one state is not evidence of success in any other state.",
            lifecycle,
        )


if __name__ == "__main__":
    unittest.main()
