"""Deterministic policy harness for the SDD First-Write Worktree Gate."""

from __future__ import annotations

from dataclasses import dataclass
import errno
import os
from pathlib import Path
import subprocess
import tempfile
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


class TaskOwnerCapability:
    """Opaque controller-minted identity for one task's worktree allocation."""

    __slots__ = ()


@dataclass(frozen=True)
class BoundWorktree:
    path: Path
    owner: TaskOwnerCapability

    def resolve(self, *, strict: bool = False) -> Path:
        return self.path.resolve(strict=strict)


def bind_task_worktree(path: Path, owner: TaskOwnerCapability) -> BoundWorktree:
    """Bind a controller-owned capability to an allocated worktree path."""

    return BoundWorktree(path=path, owner=owner)


def mint_task_owner_capability() -> TaskOwnerCapability:
    """Mint an unforgeable-by-value task identity for allocation comparison."""

    return TaskOwnerCapability()


class SandboxDenied(RuntimeError):
    """An injected sandbox policy denied worktree allocation."""


class WriteDenied(RuntimeError):
    """A scoped writer rejected a path before filesystem mutation."""


class WriteFailed(RuntimeError):
    """A scoped writer could not complete its validated write plan."""


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
        return bool(planning_branch and planning_common == original_common)
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


class ScopedWriter:
    """Gate-owned executor for one validated new artifact."""

    def __init__(self, root: Path, writable_paths: tuple[Path, ...]) -> None:
        self._root = root.resolve(strict=True)
        if len(writable_paths) != 1:
            raise WriteDenied("new artifact binding not proven")
        self._target = writable_paths[0].resolve(strict=False)
        self._parent = self._target.parent.resolve(strict=True)
        if (
            not self._parent.is_dir()
            or not _is_contained(self._root, self._target)
            or self._target.exists()
        ):
            raise WriteDenied("new artifact binding not proven")

    def execute(
        self,
        write_plan: tuple[tuple[Path, bytes], ...],
    ) -> tuple[Path, ...]:
        if len(write_plan) != 1:
            raise WriteDenied("new artifact binding not proven")
        output, content = write_plan[0]
        output = output.resolve(strict=False)
        if output != self._target or not isinstance(content, bytes):
            raise WriteDenied("new artifact binding not proven")
        stage_path: Optional[Path] = None
        try:
            descriptor, stage_name = tempfile.mkstemp(
                prefix=".sdd-stage-",
                dir=self._parent,
            )
            stage_path = Path(stage_name)
            with os.fdopen(descriptor, "wb") as staged:
                staged.write(content)
                staged.flush()
                os.fsync(staged.fileno())
        except OSError as error:
            if stage_path is not None:
                stage_path.unlink(missing_ok=True)
            raise WriteFailed("artifact staging failed") from error
        try:
            if self._target.exists():
                raise FileExistsError(errno.EEXIST, "artifact already exists", self._target)
            os.replace(stage_path, self._target)
        except OSError as error:
            stage_path.unlink(missing_ok=True)
            raise WriteFailed("artifact publish failed") from error
        return (self._target,)


def _validated_write_plan(
    *,
    planning: Path,
    writable_paths: tuple[Path, ...],
    write_plan: tuple[tuple[Path, bytes], ...],
    output_paths: tuple[Path, ...],
) -> tuple[Optional[tuple[tuple[Path, bytes], ...]], str]:
    try:
        allowed = {path.resolve(strict=False) for path in writable_paths}
        normalized = tuple(
            (path.resolve(strict=False), content) for path, content in write_plan
        )
        outputs = tuple(path.resolve(strict=False) for path in output_paths)
        targets = tuple(path for path, _content in normalized)
        if len(writable_paths) != 1 or len(normalized) != 1 or outputs != targets:
            return None, "new artifact binding not proven"
        if any(
            not isinstance(content, bytes)
            or not _is_contained(planning, path)
            or path not in allowed
            for path, content in normalized
        ):
            return None, "writer output binding not proven"
        target = targets[0]
        parent = target.parent.resolve(strict=True)
        if not parent.is_dir() or target.exists():
            return None, "new artifact binding not proven"
        return normalized, "none"
    except (OSError, RuntimeError, TypeError, ValueError):
        return None, "new artifact binding not proven"


def run_repository_change(
    *,
    original: Path,
    entry_skill: str,
    task_worktree: object,
    cwd: Path,
    writable_paths: tuple[Path, ...],
    write_plan: Optional[tuple[tuple[Path, bytes], ...]],
    output_paths: tuple[Path, ...],
    allocator: Callable[[], object],
    command_plan: Optional[tuple[str, ...]],
) -> ScenarioResult:
    before = fingerprint_repository(original)
    attempted = (command_plan,) if command_plan is not None else ()
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
        allocation = allocator()
    except PermissionError as error:
        if error.errno == errno.EACCES:
            return blocked("worktree allocation denied: EACCES")
        if error.errno == errno.EPERM:
            return blocked("worktree allocation denied: EPERM")
        return blocked("worktree allocation failed: PermissionError")
    except SandboxDenied:
        return blocked("worktree allocation denied: sandbox")
    except subprocess.CalledProcessError:
        return blocked("worktree allocation failed")
    except FileNotFoundError:
        return blocked("worktree allocation failed: FileNotFoundError")
    except OSError as error:
        return blocked(f"worktree allocation failed: {type(error).__name__}")

    expected_owner = getattr(task_worktree, "owner", None)
    allocation_owner = getattr(allocation, "owner", None)
    if expected_owner is None or allocation_owner is not expected_owner:
        return blocked("task worktree ownership not proven")

    try:
        planning = allocation.resolve(strict=True)
        expected_worktree = task_worktree.resolve(strict=True)
    except (OSError, RuntimeError, TypeError, ValueError):
        return blocked("task worktree binding not proven")

    if not _allocation_is_bound(original, planning, expected_worktree):
        return blocked("task worktree binding not proven")

    if command_plan is not None:
        if (
            writable_paths
            or write_plan is not None
            or output_paths
            or len(command_plan) != 4
            or command_plan[:3] != ("git", "commit", "-m")
            or not command_plan[3]
        ):
            return blocked("downstream incompatible with SDD containment")
        try:
            command_cwd = cwd.resolve(strict=True)
        except (OSError, RuntimeError):
            return blocked("commit binding not proven")
        if command_cwd != planning:
            return blocked("commit binding not proven")
        runner_invocations += 1
        try:
            subprocess.run(
                command_plan,
                cwd=planning,
                check=True,
                capture_output=True,
            )
        except (OSError, subprocess.CalledProcessError):
            return blocked("commit execution failed")
        executed = (command_plan,)
        after = fingerprint_repository(original)
        if after != before:
            return blocked("original checkout preservation not proven")
        return ScenarioResult(
            ControlReturn("complete", "none", "none", "none"),
            writer_invocations,
            runner_invocations,
            attempted,
            executed,
            before,
            after,
        )

    if not _write_binding_is_proven(
        planning=planning,
        cwd=cwd,
        writable_paths=writable_paths,
    ):
        return blocked("write binding not proven")

    if write_plan is None:
        return blocked("writer plan not bound")

    validated_plan, invalid_reason = _validated_write_plan(
        planning=planning,
        writable_paths=writable_paths,
        write_plan=write_plan,
        output_paths=output_paths,
    )
    if validated_plan is None:
        return blocked(invalid_reason)

    try:
        scoped_writer = ScopedWriter(planning, writable_paths)
    except WriteDenied as error:
        return blocked(str(error))
    except OSError:
        return blocked("artifact writer unavailable")
    writer_invocations += 1
    try:
        outputs = scoped_writer.execute(validated_plan)
    except (WriteDenied, WriteFailed) as error:
        return blocked(str(error))
    after = fingerprint_repository(original)
    if after != before:
        return blocked("original checkout preservation not proven")
    if outputs != tuple(path.resolve(strict=False) for path in output_paths):
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
