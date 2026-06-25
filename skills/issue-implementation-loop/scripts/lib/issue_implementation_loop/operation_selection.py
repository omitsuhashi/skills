from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .constants import TERMINAL_STATUSES, WORKTREE_STATES
from .context_contract import operation_read_set
from .graph import issue_status
from .io import load_json
from .scheduler import compute_next_actions
from .validation.execution_envelope import validate_execution_envelope
from .validation.runtime_state import validate_runtime_state


EXPLICIT_MODE_OPERATIONS = {
    "deliver": "deliver",
    "status": "status",
}


def select_operation(
    *,
    skill_dir: Path,
    repo_root: Path,
    requested_mode: str,
    envelope_path: Path | None,
    runtime_path: Path | None,
) -> dict[str, Any]:
    requested_mode = requested_mode.lower()
    if requested_mode in EXPLICIT_MODE_OPERATIONS:
        return _result(
            skill_dir=skill_dir,
            repo_root=repo_root,
            requested_mode=requested_mode,
            priority=f"explicit_{requested_mode}",
            operation=EXPLICIT_MODE_OPERATIONS[requested_mode],
            reason=f"requested mode is {requested_mode}",
        )
    if requested_mode == "prepare":
        return _result(
            skill_dir=skill_dir,
            repo_root=repo_root,
            requested_mode=requested_mode,
            priority="prepare",
            operation="prepare",
            reason="requested mode is prepare",
        )

    if envelope_path is None or not envelope_path.is_file():
        return _result(
            skill_dir=skill_dir,
            repo_root=repo_root,
            requested_mode=requested_mode,
            priority="missing_envelope",
            operation="prepare",
            reason="execution envelope is missing",
        )

    try:
        envelope = load_json(envelope_path)
    except (OSError, json.JSONDecodeError) as exc:
        return _result(
            skill_dir=skill_dir,
            repo_root=repo_root,
            requested_mode=requested_mode,
            priority="missing_envelope",
            operation="prepare",
            reason=f"execution envelope cannot be read: {exc}",
        )

    unreserved_issue = _first_unreserved_issue(envelope)
    if unreserved_issue:
        return _result(
            skill_dir=skill_dir,
            repo_root=repo_root,
            requested_mode=requested_mode,
            priority="unreserved",
            operation="prepare",
            reason="work item is missing a branch/worktree reservation",
            target_issue=unreserved_issue,
        )
    if _epic_base_unreserved(envelope):
        return _result(
            skill_dir=skill_dir,
            repo_root=repo_root,
            requested_mode=requested_mode,
            priority="unreserved",
            operation="prepare",
            reason="epic base reservation is incomplete",
        )

    envelope_errors = validate_execution_envelope(envelope)
    if envelope_errors:
        return _result(
            skill_dir=skill_dir,
            repo_root=repo_root,
            requested_mode=requested_mode,
            priority="git_state_mismatch",
            operation="resume",
            reason="execution envelope validation failed: " + "; ".join(envelope_errors),
        )

    if runtime_path is None or not runtime_path.is_file():
        return _result(
            skill_dir=skill_dir,
            repo_root=repo_root,
            requested_mode=requested_mode,
            priority="git_state_mismatch",
            operation="resume",
            reason="runtime state is missing",
        )
    try:
        runtime = load_json(runtime_path)
    except (OSError, json.JSONDecodeError) as exc:
        return _result(
            skill_dir=skill_dir,
            repo_root=repo_root,
            requested_mode=requested_mode,
            priority="git_state_mismatch",
            operation="resume",
            reason=f"runtime state cannot be read: {exc}",
        )

    state_mismatch = _state_mismatch(envelope, runtime)
    runtime_errors = validate_runtime_state(runtime)
    if runtime_errors or state_mismatch:
        reasons = []
        if runtime_errors:
            reasons.append("runtime state validation failed: " + "; ".join(runtime_errors))
        if state_mismatch:
            reasons.append(state_mismatch["reason"])
        return _result(
            skill_dir=skill_dir,
            repo_root=repo_root,
            requested_mode=requested_mode,
            priority="git_state_mismatch",
            operation="resume",
            reason="; ".join(reasons),
            target_issue=state_mismatch.get("issue") if state_mismatch else None,
        )

    next_actions = compute_next_actions(envelope, runtime)
    for priority, operation, reason in (
        ("reviewable", "execute.review", "issue is ready for implementation review"),
        ("fixable", "execute.dispatch", "issue needs a worker-context fix pass"),
        ("waiting_human", "execute.dispatch", "issue is waiting for a scoped human decision"),
        ("runnable", "execute.dispatch", "issue is runnable"),
    ):
        issue_ids = next_actions.get(priority, [])
        if issue_ids:
            return _result(
                skill_dir=skill_dir,
                repo_root=repo_root,
                requested_mode=requested_mode,
                priority=priority,
                operation=operation,
                reason=reason,
                target_issue=issue_ids[0],
            )

    if _all_terminal(envelope, runtime):
        return _result(
            skill_dir=skill_dir,
            repo_root=repo_root,
            requested_mode=requested_mode,
            priority="terminal",
            operation="deliver",
            reason="all work items are in terminal states",
        )

    return _result(
        skill_dir=skill_dir,
        repo_root=repo_root,
        requested_mode=requested_mode,
        priority="reconcile",
        operation="resume",
        reason="no runnable, reviewable, fixable, waiting, or terminal set was selected",
    )


def _result(
    *,
    skill_dir: Path,
    repo_root: Path,
    requested_mode: str,
    priority: str,
    operation: str,
    reason: str,
    target_issue: str | None = None,
) -> dict[str, Any]:
    read_set = operation_read_set(skill_dir, repo_root, operation)
    return {
        "schema_version": 1,
        "requested_mode": requested_mode,
        "priority": priority,
        "operation": operation,
        "reason": reason,
        "target_issue": target_issue,
        "read_set": read_set["files"],
        "word_budget_result": {
            "file_count": read_set["file_count"],
            "max_file_count": read_set["max_file_count"],
            "word_count": read_set["word_count"],
            "word_budget": read_set["word_budget"],
            "budget_headroom": read_set["budget_headroom"],
            "within_budget": read_set["within_budget"],
        },
    }


def _first_unreserved_issue(envelope: Any) -> str | None:
    if not isinstance(envelope, dict):
        return None
    work_items = envelope.get("work_items")
    if not isinstance(work_items, dict):
        return None
    for issue_id, item in work_items.items():
        if not isinstance(item, dict):
            return str(issue_id)
        branch = item.get("branch")
        worktree_path = item.get("worktree_path")
        worktree_state = item.get("worktree_state")
        if not isinstance(branch, str) or not branch.strip():
            return str(issue_id)
        if not isinstance(worktree_path, str) or not os.path.isabs(worktree_path):
            return str(issue_id)
        if worktree_state not in WORKTREE_STATES:
            return str(issue_id)
    return None


def _epic_base_unreserved(envelope: dict[str, Any]) -> bool:
    remote_policy = envelope.get("remote_write_policy")
    if not isinstance(remote_policy, dict) or remote_policy.get("mode") != "batch_issue_prs":
        return False
    epic_base = envelope.get("epic_base")
    if not isinstance(epic_base, dict):
        return True
    return epic_base.get("branch_state") not in WORKTREE_STATES


def _state_mismatch(envelope: dict[str, Any], runtime: dict[str, Any]) -> dict[str, str] | None:
    if runtime.get("epic_id") != envelope.get("epic_id"):
        return {"reason": "runtime epic_id does not match execution envelope"}
    if runtime.get("envelope_revision") != envelope.get("revision"):
        return {"reason": "runtime envelope_revision does not match execution envelope revision"}

    work_items = envelope.get("work_items", {})
    runtime_issues = runtime.get("issues", {})
    if not isinstance(work_items, dict) or not isinstance(runtime_issues, dict):
        return None
    for issue_id, record in runtime_issues.items():
        if issue_id not in work_items:
            return {"issue": str(issue_id), "reason": "runtime contains an issue outside the envelope"}
        if not isinstance(record, dict):
            continue
        item = work_items[issue_id]
        if not isinstance(item, dict):
            continue
        branch = record.get("branch")
        if isinstance(branch, str) and branch != item.get("branch"):
            return {"issue": str(issue_id), "reason": "runtime branch does not match envelope reservation"}
        worktree = record.get("worktree", record.get("worktree_path"))
        if isinstance(worktree, str) and worktree != item.get("worktree_path"):
            return {"issue": str(issue_id), "reason": "runtime worktree does not match envelope reservation"}
    return None


def _all_terminal(envelope: dict[str, Any], runtime: dict[str, Any]) -> bool:
    work_items = envelope.get("work_items", {})
    if not isinstance(work_items, dict) or not work_items:
        return False
    return all(issue_status(runtime, issue_id) in TERMINAL_STATUSES for issue_id in work_items)
