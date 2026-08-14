"""Deterministic policy harness for the SDD First-Write Worktree Gate."""

from __future__ import annotations

from dataclasses import dataclass
import errno
from pathlib import Path
import subprocess
from typing import Callable, Optional


BOOTSTRAP_EPIC = "sdd-fail-closed-worktree-gate"
BOOTSTRAP_BRANCH = "codex/sdd-fail-closed-worktree-gate/planning"
BOOTSTRAP_WORKTREE = Path(
    "/Users/omitsuhashi/repos/omitsuhashi/skills/.worktrees/"
    "sdd-fail-closed-worktree-gate-planning"
)
BOOTSTRAP_STARTING_HEAD_SHA = "c370fe14de1641aa5ee30b3fa001f4d857078091"
BOOTSTRAP_SCOPES = frozenset(("source", "test", "spec", "plan"))


@dataclass(frozen=True)
class BootstrapContext:
    epic: str
    branch: str
    worktree: Path
    starting_head_sha: str
    same_controller: bool
    tuple_trusted: bool
    lifecycle: str
    requested_scope: str


@dataclass(frozen=True)
class ControlReturn:
    status: str
    artifact_path: str
    decision_requests: str
    material_risks: str


@dataclass(frozen=True)
class RepositoryFingerprint:
    branch: str
    head: str
    index: bytes
    cached_diff: bytes
    worktree_diff: bytes
    status: bytes
    tracked_and_untracked: tuple[tuple[str, bytes], ...]
    commit_count: int


@dataclass(frozen=True)
class ScenarioResult:
    control_return: ControlReturn
    writer_invocations: int
    runner_invocations: int
    attempted_commands: tuple[tuple[str, ...], ...]
    executed_commands: tuple[tuple[str, ...], ...]
    before: RepositoryFingerprint
    after: RepositoryFingerprint


class SandboxDenied(RuntimeError):
    """An injected sandbox policy denied worktree allocation."""


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout


def _canonical_git_path(root: Path, value: bytes) -> Path:
    path = Path(value.decode("utf-8").strip())
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def fingerprint_repository(root: Path) -> RepositoryFingerprint:
    names = tuple(
        name.decode("utf-8", errors="surrogateescape")
        for name in _git(root, "ls-files", "-co", "--exclude-standard", "-z").split(b"\0")
        if name
    )
    return RepositoryFingerprint(
        branch=_git(root, "branch", "--show-current").decode("utf-8").strip(),
        head=_git(root, "rev-parse", "HEAD").decode("ascii").strip(),
        index=_git(root, "ls-files", "--stage", "-z"),
        cached_diff=_git(root, "diff", "--cached", "--binary"),
        worktree_diff=_git(root, "diff", "--binary"),
        status=_git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all"),
        tracked_and_untracked=tuple((name, (root / name).read_bytes()) for name in names),
        commit_count=int(_git(root, "rev-list", "--count", "HEAD").decode("ascii")),
    )


def _bootstrap_is_exact(bootstrap: Optional[BootstrapContext]) -> bool:
    return bool(
        bootstrap is not None
        and bootstrap.epic == BOOTSTRAP_EPIC
        and bootstrap.branch == BOOTSTRAP_BRANCH
        and bootstrap.worktree == BOOTSTRAP_WORKTREE
        and bootstrap.starting_head_sha == BOOTSTRAP_STARTING_HEAD_SHA
        and bootstrap.same_controller
        and bootstrap.tuple_trusted
        and bootstrap.lifecycle == "bootstrap"
        and bootstrap.requested_scope in BOOTSTRAP_SCOPES
    )


def _allocation_is_bound(original: Path, planning: Path) -> bool:
    try:
        original = original.resolve(strict=True)
        planning = planning.resolve(strict=True)
        if original == planning or not planning.is_dir():
            return False
        if _canonical_git_path(planning, _git(planning, "rev-parse", "--show-toplevel")) != planning:
            return False
        original_common = _canonical_git_path(
            original, _git(original, "rev-parse", "--git-common-dir")
        )
        planning_common = _canonical_git_path(
            planning, _git(planning, "rev-parse", "--git-common-dir")
        )
        planning_branch = _git(planning, "branch", "--show-current").decode("utf-8").strip()
        original_branch = _git(original, "branch", "--show-current").decode("utf-8").strip()
        return bool(planning_branch and planning_branch != original_branch and planning_common == original_common)
    except (OSError, subprocess.CalledProcessError, UnicodeError):
        return False


def run_repository_change(
    *,
    original: Path,
    entry_skill: str,
    guard_status: str,
    bootstrap: Optional[BootstrapContext],
    allocator: Callable[[], Path],
    writer: Callable[[Path], None],
    downstream_command: Optional[tuple[str, ...]],
    command_runner: Callable[[tuple[str, ...]], int],
) -> ScenarioResult:
    before = fingerprint_repository(original)
    attempted = (downstream_command,) if downstream_command is not None else ()
    writer_invocations = 0
    runner_invocations = 0
    executed: tuple[tuple[str, ...], ...] = ()

    def blocked(reason: str) -> ScenarioResult:
        return ScenarioResult(
            ControlReturn("blocked", "none", "none", reason),
            writer_invocations,
            runner_invocations,
            attempted,
            executed,
            before,
            fingerprint_repository(original),
        )

    if entry_skill != "sdd-implementation":
        return blocked("SDD First-Write Worktree Gate required")

    if guard_status != "active" and not _bootstrap_is_exact(bootstrap):
        return blocked(guard_status)

    try:
        planning = allocator()
    except PermissionError as error:
        if error.errno == errno.EACCES:
            return blocked("worktree allocation denied: EACCES")
        raise
    except SandboxDenied:
        return blocked("worktree allocation denied: sandbox")

    if not _allocation_is_bound(original, planning):
        return blocked("worktree registration/ownership/containment not proven")

    if downstream_command is not None:
        return blocked("downstream incompatible with SDD containment")

    writer_invocations += 1
    writer(planning)
    return ScenarioResult(
        ControlReturn("complete", "none", "none", "none"),
        writer_invocations,
        runner_invocations,
        attempted,
        executed,
        before,
        fingerprint_repository(original),
    )
