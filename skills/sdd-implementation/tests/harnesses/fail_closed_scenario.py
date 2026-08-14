"""Deterministic policy harness for the SDD First-Write Worktree Gate."""

from __future__ import annotations

from dataclasses import dataclass
import errno
import os
from pathlib import Path
import stat
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


class ScopedWriter:
    """Gate-owned executor for a fully validated data-only write plan."""

    def __init__(self, root: Path, writable_paths: tuple[Path, ...]) -> None:
        self._root = root.resolve(strict=True)
        self._allowed = frozenset(
            path.resolve(strict=False) for path in writable_paths
        )

    def execute(
        self,
        write_plan: tuple[tuple[Path, bytes], ...],
    ) -> tuple[Path, ...]:
        normalized = tuple(
            (path.resolve(strict=False), content) for path, content in write_plan
        )
        if any(
            not _is_contained(self._root, path) or path not in self._allowed
            for path, _content in normalized
        ):
            raise WriteDenied("writer output binding not proven")

        snapshots: dict[Path, Optional[tuple[bytes, int, int, int]]] = {}
        try:
            for output, _content in normalized:
                if output not in snapshots:
                    try:
                        metadata = output.stat()
                    except FileNotFoundError:
                        snapshots[output] = None
                    else:
                        if not stat.S_ISREG(metadata.st_mode):
                            raise IsADirectoryError(
                                errno.EISDIR,
                                "target is not a file",
                                output,
                            )
                        snapshots[output] = (
                            output.read_bytes(),
                            stat.S_IMODE(metadata.st_mode),
                            metadata.st_atime_ns,
                            metadata.st_mtime_ns,
                        )
                parent = output.parent
                while parent != self._root:
                    try:
                        metadata = parent.stat()
                    except FileNotFoundError:
                        parent = parent.parent
                        continue
                    if not stat.S_ISDIR(metadata.st_mode):
                        raise NotADirectoryError(
                            errno.ENOTDIR,
                            "parent is not a directory",
                            parent,
                        )
                    break
        except OSError as error:
            raise WriteFailed("writer execution failed") from error

        created_directories: list[Path] = []
        touched: list[Path] = []
        try:
            for output, content in normalized:
                missing_parents: list[Path] = []
                parent = output.parent
                while parent != self._root and not parent.exists():
                    missing_parents.append(parent)
                    parent = parent.parent
                for directory in reversed(missing_parents):
                    try:
                        directory.mkdir()
                    except FileExistsError:
                        if not directory.is_dir():
                            raise
                    else:
                        created_directories.append(directory)
                touched.append(output)
                output.write_bytes(content)
        except OSError as error:
            restoration_failed = False
            for output in reversed(tuple(dict.fromkeys(touched))):
                snapshot = snapshots[output]
                try:
                    if snapshot is None:
                        output.unlink(missing_ok=True)
                    else:
                        content, mode, atime_ns, mtime_ns = snapshot
                        output.write_bytes(content)
                        os.chmod(output, mode)
                        os.utime(output, ns=(atime_ns, mtime_ns))
                except OSError:
                    restoration_failed = True
            for directory in reversed(created_directories):
                try:
                    directory.rmdir()
                except FileNotFoundError:
                    pass
                except OSError:
                    restoration_failed = True
            reason = (
                "writer restoration failed"
                if restoration_failed
                else "writer execution failed"
            )
            raise WriteFailed(reason) from error
        return tuple(path for path, _content in normalized)


def _validated_write_plan(
    *,
    planning: Path,
    writable_paths: tuple[Path, ...],
    write_plan: tuple[tuple[Path, bytes], ...],
    output_paths: tuple[Path, ...],
) -> Optional[tuple[tuple[Path, bytes], ...]]:
    try:
        allowed = {path.resolve(strict=False) for path in writable_paths}
        normalized = tuple(
            (path.resolve(strict=False), content) for path, content in write_plan
        )
        outputs = tuple(path.resolve(strict=False) for path in output_paths)
        targets = tuple(path for path, _content in normalized)
        if not normalized or outputs != targets:
            return None
        if any(
            not isinstance(content, bytes)
            or not _is_contained(planning, path)
            or path not in allowed
            for path, content in normalized
        ):
            return None
        return normalized
    except (OSError, RuntimeError, TypeError, ValueError):
        return None


def run_repository_change(
    *,
    original: Path,
    entry_skill: str,
    task_worktree: Path,
    cwd: Path,
    writable_paths: tuple[Path, ...],
    write_plan: Optional[tuple[tuple[Path, bytes], ...]],
    output_paths: tuple[Path, ...],
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

    if write_plan is None:
        return blocked("writer plan not bound")

    validated_plan = _validated_write_plan(
        planning=planning,
        writable_paths=writable_paths,
        write_plan=write_plan,
        output_paths=output_paths,
    )
    if validated_plan is None:
        return blocked("writer output binding not proven")

    if downstream_command is not None:
        return blocked("downstream incompatible with SDD containment")

    scoped_writer = ScopedWriter(planning, writable_paths)
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
