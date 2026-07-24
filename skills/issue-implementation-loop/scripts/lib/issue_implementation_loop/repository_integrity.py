from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Any

from .constants import SUCCESS_STATUSES
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
REPOSITORY_LOCAL_GIT_ENVIRONMENT = frozenset(
    {
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_CEILING_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_CONFIG",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_PARAMETERS",
        "GIT_DIR",
        "GIT_DISCOVERY_ACROSS_FILESYSTEM",
        "GIT_GRAFT_FILE",
        "GIT_IMPLICIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_NAMESPACE",
        "GIT_NO_REPLACE_OBJECTS",
        "GIT_OBJECT_DIRECTORY",
        "GIT_PREFIX",
        "GIT_QUARANTINE_PATH",
        "GIT_REPLACE_REF_BASE",
        "GIT_SHALLOW_FILE",
        "GIT_WORK_TREE",
    }
)


def _git_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for name in tuple(environment):
        if (
            name in REPOSITORY_LOCAL_GIT_ENVIRONMENT
            or name.startswith("GIT_CONFIG_KEY_")
            or name.startswith("GIT_CONFIG_VALUE_")
        ):
            environment.pop(name)
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_GRAFT_FILE"] = os.devnull
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    return environment


def _git(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(path), *args],
            check=False,
            capture_output=True,
            text=True,
            env=_git_environment(),
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

    binding = envelope.get("approved_spec_binding")
    epic_base = envelope.get("epic_base")
    if isinstance(binding, dict) and isinstance(epic_base, dict):
        gate_commit = binding.get("gate_commit")
        epic_base_sha = epic_base.get("sha")
        if not _is_ancestor(trusted_root, gate_commit, epic_base_sha):
            return ["GATE_COMMIT_NOT_ANCESTOR"]

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


def validate_success_repository_integrity(
    envelope: dict[str, Any],
    runtime: dict[str, Any],
    repo_root: str | os.PathLike[str],
) -> list[str]:
    """Re-run the repository guard before accepting any successful issue state."""

    issues = runtime.get("issues")
    if (
        not isinstance(issues, dict)
        or not any(
            isinstance(record, dict)
            and record.get("status") in SUCCESS_STATUSES
            for record in issues.values()
        )
        or envelope.get("repository_guard") is None
    ):
        return []
    guard = envelope["repository_guard"]
    packet = {
        "epic_id": envelope.get("epic_id"),
        "planning_branch": guard.get("planning_branch"),
        "planning_base_sha": guard.get("planning_base_sha"),
    }
    return validate_repository_guard(envelope, packet, repo_root)


def resolve_local_branch(
    repo_root: str | os.PathLike[str],
    head_ref: Any,
) -> str | None:
    if not isinstance(head_ref, str) or not head_ref:
        return None
    if head_ref.startswith("refs/") and not head_ref.startswith("refs/heads/"):
        return None
    trusted_root = _absolute_directory(os.fspath(repo_root))
    if trusted_root is None:
        return None
    branch_ref = (
        head_ref if head_ref.startswith("refs/heads/") else f"refs/heads/{head_ref}"
    )
    resolved = _git(trusted_root, "show-ref", "--verify", "--hash", branch_ref)
    if resolved.returncode:
        return None
    sha = resolved.stdout.strip().lower()
    return sha if is_full_commit_sha(sha) else None


def _is_ancestor(repo_root: Path, required_sha: Any, head_sha: str) -> bool:
    if (
        not isinstance(required_sha, str)
        or not is_full_commit_sha(required_sha)
    ):
        return False
    return (
        _git(
            repo_root,
            "merge-base",
            "--is-ancestor",
            required_sha,
            head_sha,
        ).returncode
        == 0
    )


def validate_final_head_integrity(
    envelope: dict[str, Any],
    execution_result: dict[str, Any],
    head_ref: str,
    repo_root: str | os.PathLike[str],
) -> list[str]:
    """Require the local final branch to contain planning and delivery commits."""

    trusted_root = _absolute_directory(os.fspath(repo_root))
    if trusted_root is None:
        return ["FINAL_HEAD_REF_UNRESOLVED"]
    head_sha = resolve_local_branch(trusted_root, head_ref)
    if head_sha is None:
        return ["FINAL_HEAD_REF_UNRESOLVED"]

    errors: list[str] = []
    guard = envelope.get("repository_guard")
    if isinstance(guard, dict):
        planning_base = guard.get("planning_base_sha")
        if not _is_ancestor(trusted_root, planning_base, head_sha):
            errors.append("FINAL_HEAD_MISSING_PLANNING_BASE")

    binding = envelope.get("approved_spec_binding")
    gate_commit = binding.get("gate_commit") if isinstance(binding, dict) else None
    if not _is_ancestor(trusted_root, gate_commit, head_sha):
        errors.append("FINAL_HEAD_MISSING_GATE_COMMIT")

    result_issues = execution_result.get("issues")
    candidates = execution_result.get("delivery_candidates")
    if isinstance(result_issues, dict) and isinstance(candidates, list):
        for issue_id in candidates:
            record = result_issues.get(issue_id)
            candidate_head = (
                record.get("head_sha") if isinstance(record, dict) else None
            )
            if not _is_ancestor(trusted_root, candidate_head, head_sha):
                errors.append(
                    f"FINAL_HEAD_MISSING_DELIVERY_CANDIDATE:{issue_id}"
                )
    return errors
