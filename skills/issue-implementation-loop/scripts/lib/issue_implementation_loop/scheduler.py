from __future__ import annotations

from typing import Any

from .constants import ACTIVE_STATUSES, REVIEWABLE_STATUSES, TERMINAL_STATUSES, WAITING_STATUSES
from .graph import dependency_satisfied, descendants_of, issue_status


def path_scope_conflicts(left: str, right: str) -> bool:
    if not left.startswith("path:") or not right.startswith("path:"):
        return left == right
    left_path = left.removeprefix("path:").rstrip("/")
    right_path = right.removeprefix("path:").rstrip("/")
    return (
        left_path == right_path
        or left_path.startswith(right_path + "/")
        or right_path.startswith(left_path + "/")
    )


def scope_conflicts(left: list[str], right: list[str]) -> bool:
    return any(path_scope_conflicts(a, b) for a in left for b in right)


def human_blocked_reason(
    issue_id: str,
    item: dict[str, Any],
    work_items: dict[str, Any],
    runtime: dict[str, Any],
) -> str | None:
    for request in runtime.get("human_requests", []):
        if not isinstance(request, dict):
            continue
        scope = request.get("scope")
        if scope == "epic":
            return request.get("id", "human_request")
        if scope == "issue" and request.get("issue") == issue_id:
            return request.get("id", "human_request")
        if scope == "descendants":
            root = request.get("issue")
            if isinstance(root, str) and issue_id in descendants_of(root, work_items):
                return request.get("id", "human_request")
        if scope == "resource":
            resource = request.get("resource")
            if isinstance(resource, str) and scope_conflicts(item.get("write_scope", []), [resource]):
                return request.get("id", "human_request")
    return None


def compute_next_actions(envelope: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    work_items = envelope["work_items"]
    active_scopes: dict[str, list[str]] = {}
    for issue_id, item in work_items.items():
        if issue_status(runtime, issue_id) in ACTIVE_STATUSES:
            active_scopes[issue_id] = item.get("write_scope", [])
    reserved_dispatch_scopes: dict[str, list[str]] = dict(active_scopes)

    runnable: list[str] = []
    blocked: dict[str, list[str]] = {}
    waiting_human: list[str] = []
    reviewable: list[str] = []
    fixable: list[str] = []

    for issue_id, item in work_items.items():
        status = issue_status(runtime, issue_id)
        if status in TERMINAL_STATUSES or status in ACTIVE_STATUSES:
            continue
        if status in REVIEWABLE_STATUSES:
            reviewable.append(issue_id)
            continue
        if status == "REVIEW_CHANGES_REQUESTED":
            fixable.append(issue_id)
            continue
        human_reason = human_blocked_reason(issue_id, item, work_items, runtime)
        if status in WAITING_STATUSES or human_reason:
            waiting_human.append(issue_id)
            if human_reason:
                blocked.setdefault(issue_id, []).append(f"human:{human_reason}")
            continue
        incomplete_deps = [
            dep["issue"]
            for dep in item.get("dependencies", [])
            if isinstance(dep, dict) and not dependency_satisfied(dep, runtime)
        ]
        if incomplete_deps:
            blocked[issue_id] = incomplete_deps
            continue
        conflict = next(
            (
                active_issue
                for active_issue, scope in reserved_dispatch_scopes.items()
                if active_issue != issue_id and scope_conflicts(item.get("write_scope", []), scope)
            ),
            None,
        )
        if conflict:
            blocked.setdefault(issue_id, []).append(f"resource:{conflict}")
            continue
        runnable.append(issue_id)
        reserved_dispatch_scopes[issue_id] = item.get("write_scope", [])

    return {
        "epic_id": envelope.get("epic_id"),
        "envelope_revision": envelope.get("revision"),
        "runnable": runnable,
        "reviewable": reviewable,
        "fixable": fixable,
        "waiting_human": waiting_human,
        "blocked": blocked,
    }
