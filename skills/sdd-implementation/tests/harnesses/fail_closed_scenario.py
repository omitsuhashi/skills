"""Deterministic policy harness for the SDD First-Write Worktree Gate."""

from __future__ import annotations

from dataclasses import dataclass
import errno
from pathlib import Path
import subprocess
from typing import Callable, Optional


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


def _allocation_is_bound(
    original: Path,
    planning: Path,
    task_worktree: Path,
) -> bool:
    try:
        original = original.resolve(strict=True)
        planning = planning.resolve(strict=True)
        task_worktree = task_worktree.resolve(strict=True)
        if original == planning or planning != task_worktree or not planning.is_dir():
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


def _is_contained(root: Path, path: Path) -> bool:
    try:
        canonical_root = root.resolve(strict=True)
        canonical_path = path.resolve(strict=False)
        return canonical_path != canonical_root and canonical_path.is_relative_to(
            canonical_root
        )
    except (OSError, RuntimeError):
        return False


def _write_binding_is_proven(
    *,
    planning: Path,
    cwd: Path,
    writable_paths: tuple[Path, ...],
) -> bool:
    try:
        return bool(
            writable_paths
            and cwd.resolve(strict=True) == planning.resolve(strict=True)
            and all(_is_contained(planning, path) for path in writable_paths)
        )
    except (OSError, RuntimeError):
        return False


def _outputs_are_bound(
    *,
    planning: Path,
    writable_paths: tuple[Path, ...],
    outputs: tuple[Path, ...],
) -> bool:
    allowed = {path.resolve(strict=False) for path in writable_paths}
    return all(
        _is_contained(planning, output) and output.resolve(strict=False) in allowed
        for output in outputs
    )


def run_repository_change(
    *,
    original: Path,
    entry_skill: str,
    task_worktree: Path,
    cwd: Path,
    writable_paths: tuple[Path, ...],
    bound_writer_owner: str,
    writer_owner: str,
    writer_requests: tuple[tuple[Path, bytes], ...],
    allocator: Callable[[], Path],
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

    try:
        planning = allocator()
    except PermissionError as error:
        if error.errno == errno.EACCES:
            return blocked("worktree allocation denied: EACCES")
        raise
    except SandboxDenied:
        return blocked("worktree allocation denied: sandbox")
    except subprocess.CalledProcessError:
        return blocked("worktree allocation failed")

    if not _allocation_is_bound(original, planning, task_worktree):
        return blocked("task worktree binding not proven")

    if not _write_binding_is_proven(
        planning=planning,
        cwd=cwd,
        writable_paths=writable_paths,
    ):
        return blocked("write binding not proven")

    if not bound_writer_owner or writer_owner != bound_writer_owner:
        return blocked("writer ownership not proven")

    outputs = tuple(path for path, _content in writer_requests)
    if not _outputs_are_bound(
        planning=planning,
        writable_paths=writable_paths,
        outputs=outputs,
    ):
        return blocked("writer output binding not proven")

    if downstream_command is not None:
        return blocked("downstream incompatible with SDD containment")

    writer_invocations += 1
    for output, content in writer_requests:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(content)
    after = fingerprint_repository(original)
    if after != before:
        return blocked("original checkout preservation not proven")
    if not _outputs_are_bound(
        planning=planning,
        writable_paths=writable_paths,
        outputs=outputs,
    ):
        return blocked("writer output binding not proven")
    return ScenarioResult(
        ControlReturn("complete", "none", "none", "none"),
        writer_invocations,
        runner_invocations,
        attempted,
        executed,
        before,
        after,
    )
