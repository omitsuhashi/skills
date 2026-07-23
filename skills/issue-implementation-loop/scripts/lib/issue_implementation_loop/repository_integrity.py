from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Any

from .identifiers import is_full_commit_sha


GUARD_FIELDS = {
    "planning_worktree_path",
    "planning_branch",
    "planning_base_sha",
    "default_checkout",
}
DEFAULT_CHECKOUT_FIELDS = {
    "path",
    "branch",
    "head",
    "status_porcelain_v1",
}


def _git(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        environment = os.environ.copy()
        environment["GIT_OPTIONAL_LOCKS"] = "0"
        return subprocess.run(
            ["git", "-C", str(path), *args],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
    except (OSError, TypeError, ValueError):
        return subprocess.CompletedProcess([], 1, "", "")


def _absolute_directory(value: Any) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    candidate = Path(value)
    if not candidate.is_absolute():
        return None
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return None
    return resolved if resolved.is_dir() else None


def _git_common_directory(worktree: Path) -> Path | None:
    result = _git(worktree, "rev-parse", "--git-common-dir")
    if result.returncode:
        return None
    common = Path(result.stdout.strip())
    if not common.is_absolute():
        common = worktree / common
    try:
        return common.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return None


def _registered_worktrees(repo_root: Path) -> dict[Path, dict[str, str]] | None:
    result = _git(repo_root, "worktree", "list", "--porcelain")
    if result.returncode:
        return None
    records: dict[Path, dict[str, str]] = {}
    current: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if not line:
            if current:
                value = current.get("worktree")
                if value is not None:
                    path = _absolute_directory(value)
                    if path is not None:
                        records[path] = current
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    if current:
        value = current.get("worktree")
        if value is not None:
            path = _absolute_directory(value)
            if path is not None:
                records[path] = current
    return records


def _valid_shape(guard: Any) -> bool:
    if not isinstance(guard, dict) or set(guard) != GUARD_FIELDS:
        return False
    default = guard.get("default_checkout")
    if not isinstance(default, dict) or set(default) != DEFAULT_CHECKOUT_FIELDS:
        return False
    strings = (
        guard.get("planning_branch"),
        guard.get("planning_base_sha"),
        default.get("branch"),
        default.get("head"),
        default.get("status_porcelain_v1"),
    )
    if not all(isinstance(value, str) for value in strings):
        return False
    planning_base = guard["planning_base_sha"]
    default_head = default["head"]
    return (
        bool(guard["planning_branch"])
        and is_full_commit_sha(planning_base)
        and planning_base == planning_base.lower()
        and bool(default["branch"])
        and is_full_commit_sha(default_head)
        and default_head == default_head.lower()
        and _absolute_directory(guard.get("planning_worktree_path")) is not None
        and _absolute_directory(default.get("path")) is not None
    )


def validate_repository_guard(
    envelope: dict[str, Any],
    packet: dict[str, Any],
    repo_root: str | os.PathLike[str],
) -> list[str]:
    """Validate planning/default checkout identity without mutating repository state."""

    planning_fields_present = {
        "planning_branch",
        "planning_base_sha",
    } <= set(packet)
    guard = envelope.get("repository_guard")
    if guard is None:
        return ["REPOSITORY_GUARD_MISSING"] if planning_fields_present else []
    if not _valid_shape(guard):
        return ["REPOSITORY_GUARD_INVALID"]

    expected_planning_branch = f"codex/{packet.get('epic_id')}/planning"
    if (
        guard["planning_branch"] != expected_planning_branch
        or (
            planning_fields_present
            and (
                guard["planning_branch"] != packet["planning_branch"]
                or guard["planning_base_sha"] != packet["planning_base_sha"]
            )
        )
    ):
        return ["REPOSITORY_GUARD_MISMATCH"]

    default = guard["default_checkout"]
    if guard["planning_base_sha"] != default["head"]:
        return ["REPOSITORY_GUARD_MISMATCH"]

    trusted_root = _absolute_directory(os.fspath(repo_root))
    planning_worktree = _absolute_directory(guard["planning_worktree_path"])
    default_checkout = _absolute_directory(default["path"])
    if (
        trusted_root is None
        or planning_worktree is None
        or default_checkout is None
        or planning_worktree == default_checkout
    ):
        return ["REPOSITORY_GUARD_WORKTREE_INVALID"]

    trusted_common = _git_common_directory(trusted_root)
    worktrees = _registered_worktrees(trusted_root)
    if (
        trusted_common is None
        or worktrees is None
        or trusted_root not in worktrees
        or planning_worktree not in worktrees
        or default_checkout not in worktrees
    ):
        return ["REPOSITORY_GUARD_WORKTREE_INVALID"]
    if any(
        _git_common_directory(path) != trusted_common
        for path in (planning_worktree, default_checkout)
    ):
        return ["REPOSITORY_GUARD_WORKTREE_INVALID"]

    planning_record = worktrees[planning_worktree]
    default_record = worktrees[default_checkout]
    if (
        planning_record.get("branch")
        != f"refs/heads/{guard['planning_branch']}"
        or default_record.get("branch") != f"refs/heads/{default['branch']}"
    ):
        return ["REPOSITORY_GUARD_WORKTREE_INVALID"]
    ancestor = _git(
        planning_worktree,
        "merge-base",
        "--is-ancestor",
        guard["planning_base_sha"],
        "HEAD",
    )
    if ancestor.returncode:
        return ["REPOSITORY_GUARD_WORKTREE_INVALID"]

    head = _git(default_checkout, "rev-parse", "HEAD")
    status = _git(
        default_checkout,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if (
        head.returncode
        or status.returncode
        or head.stdout.strip() != default["head"]
        or status.stdout != default["status_porcelain_v1"]
    ):
        return ["DEFAULT_CHECKOUT_DRIFT"]
    return []
