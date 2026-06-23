#!/usr/bin/env python3
"""Shared helpers for issue-implementation-loop scripts."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any


EPIC_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ISSUE_RE = re.compile(r"^[A-Z0-9]+-[0-9]+$")
FULL_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$", re.IGNORECASE)
COMMIT_RANGE_RE = re.compile(
    r"^(?:[0-9a-f]{40}|[0-9a-f]{64})\.\.(?:[0-9a-f]{40}|[0-9a-f]{64})$",
    re.IGNORECASE,
)

EDGE_STRENGTHS = {"hard", "soft"}
RELEASE_ON = {
    "artifact_ready",
    "review_approved",
    "integrated",
    "pr_opened",
    "pr_merged",
    "human_decision",
    "external_condition",
}
BASE_EFFECTS = {"none", "branch_from_blocker_head", "branch_from_integration_head"}
BASE_POLICY_TYPES = {"epic_base", "blocker_head", "integration_head"}
WORKTREE_STATES = {"reserved", "create_on_run", "active", "missing"}
REMOTE_MODES = {"local_only", "per_action", "batch_draft_prs"}

ACTIVE_STATUSES = {"RUNNING", "FIXING"}
TERMINAL_STATUSES = {"PR_READY", "COMPLETE", "DONE", "FAILED", "CANCELLED"}
SUCCESS_STATUSES = {"PR_READY", "COMPLETE", "DONE"}
REVIEWABLE_STATUSES = {"IMPLEMENTED", "VERIFICATION_PASSED"}
WAITING_STATUSES = {"WAITING_HUMAN"}


class ValidationError(Exception):
    """Raised when a validation script finds invalid input."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("\n".join(errors))
        self.errors = errors


def load_json(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def is_lower_kebab(value: str) -> bool:
    return bool(EPIC_RE.fullmatch(value))


def is_issue_id(value: str) -> bool:
    return bool(ISSUE_RE.fullmatch(value))


def is_full_commit_sha(value: str) -> bool:
    return bool(FULL_SHA_RE.fullmatch(value)) and set(value.lower()) != {"0"}


def is_commit_range(value: str) -> bool:
    if not COMMIT_RANGE_RE.fullmatch(value):
        return False
    base, head = value.split("..", 1)
    return is_full_commit_sha(base) and is_full_commit_sha(head)


def validate_input_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    repo_root = packet.get("repo_root")
    if not isinstance(repo_root, str) or not os.path.isabs(repo_root):
        errors.append("repo_root must be an absolute path")

    epic_id = packet.get("epic_id")
    if not isinstance(epic_id, str) or not is_lower_kebab(epic_id):
        errors.append("epic_id must be lower-kebab-case ASCII")

    spec = packet.get("spec")
    if not isinstance(spec, dict) or not spec.get("path"):
        errors.append("spec.path is required")

    work_items = packet.get("work_items")
    if not isinstance(work_items, list) or not work_items:
        errors.append("work_items must be a non-empty list")
        return errors

    seen: set[str] = set()
    for index, item in enumerate(work_items):
        prefix = f"work_items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not is_issue_id(item_id):
            errors.append(f"{prefix}.id must look like G2PR-001")
        elif item_id in seen:
            errors.append(f"{prefix}.id duplicates {item_id}")
        else:
            seen.add(item_id)
        if not item.get("title"):
            errors.append(f"{prefix}.title is required")
        for field in ("acceptance_criteria", "verification", "write_scope"):
            value = item.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"{prefix}.{field} must be a non-empty list")
        dependencies = item.get("dependencies", [])
        if not isinstance(dependencies, list):
            errors.append(f"{prefix}.dependencies must be a list")
            continue
        for dep_index, dep in enumerate(dependencies):
            dep_prefix = f"{prefix}.dependencies[{dep_index}]"
            if isinstance(dep, str):
                dep_issue = dep
            elif isinstance(dep, dict):
                dep_issue = dep.get("issue")
            else:
                errors.append(f"{dep_prefix} must be an issue ID or object")
                continue
            if not isinstance(dep_issue, str) or not is_issue_id(dep_issue):
                errors.append(f"{dep_prefix}.issue must look like G2PR-001")
            elif dep_issue not in seen and dep_issue not in {w.get("id") for w in work_items if isinstance(w, dict)}:
                errors.append(f"{dep_prefix}.issue references unknown issue {dep_issue}")
    return errors


def validate_execution_envelope(envelope: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if envelope.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    epic_id = envelope.get("epic_id")
    if not isinstance(epic_id, str) or not is_lower_kebab(epic_id):
        errors.append("epic_id must be lower-kebab-case ASCII")

    if not isinstance(envelope.get("revision"), int) or envelope.get("revision", 0) < 1:
        errors.append("revision must be a positive integer")

    epic_base = envelope.get("epic_base")
    if not isinstance(epic_base, dict):
        errors.append("epic_base is required")
    else:
        epic_base_ref = epic_base.get("ref")
        if not isinstance(epic_base_ref, str) or not epic_base_ref.strip():
            errors.append("epic_base.ref must be a non-empty string")
        epic_base_sha = epic_base.get("sha")
        if not isinstance(epic_base_sha, str) or not is_full_commit_sha(epic_base_sha):
            errors.append("epic_base.sha must be a full 40- or 64-character hex commit SHA")

    remote_policy = envelope.get("remote_write_policy", {})
    if remote_policy.get("mode") not in REMOTE_MODES:
        errors.append(f"remote_write_policy.mode must be one of {sorted(REMOTE_MODES)}")

    context_policy = envelope.get("context_policy")
    if not isinstance(context_policy, dict):
        errors.append("context_policy is required")
    else:
        if context_policy.get("paths_first") is not True:
            errors.append("context_policy.paths_first must be true")
        packet_words = context_policy.get("max_worker_packet_words")
        if not isinstance(packet_words, int) or packet_words < 1:
            errors.append("context_policy.max_worker_packet_words must be a positive integer")
        report_words = context_policy.get("max_worker_report_words")
        if not isinstance(report_words, int) or report_words < 1:
            errors.append("context_policy.max_worker_report_words must be a positive integer")
        if context_policy.get("include_full_spec_text") is not False:
            errors.append("context_policy.include_full_spec_text must be false")
        if context_policy.get("include_full_ledger_text") is not False:
            errors.append("context_policy.include_full_ledger_text must be false")

    work_items = envelope.get("work_items")
    if not isinstance(work_items, dict) or not work_items:
        errors.append("work_items must be a non-empty object")
        return errors

    branches: dict[str, str] = {}
    worktrees: dict[str, str] = {}
    for issue_id, item in work_items.items():
        prefix = f"work_items.{issue_id}"
        if not is_issue_id(issue_id):
            errors.append(f"{prefix} key must look like G2PR-001")
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        branch = item.get("branch")
        if not isinstance(branch, str) or not branch:
            errors.append(f"{prefix}.branch is required")
        else:
            if epic_id and f"/{epic_id}/" not in branch:
                errors.append(f"{prefix}.branch must include /{epic_id}/ namespace")
            if branch in branches:
                errors.append(f"{prefix}.branch duplicates {branches[branch]}")
            branches[branch] = issue_id
        worktree_path = item.get("worktree_path")
        if not isinstance(worktree_path, str) or not os.path.isabs(worktree_path):
            errors.append(f"{prefix}.worktree_path must be an absolute path")
        else:
            if worktree_path in worktrees:
                errors.append(f"{prefix}.worktree_path duplicates {worktrees[worktree_path]}")
            worktrees[worktree_path] = issue_id
        if item.get("worktree_state") not in WORKTREE_STATES:
            errors.append(f"{prefix}.worktree_state must be one of {sorted(WORKTREE_STATES)}")
        base_policy = item.get("base_policy")
        base_policy_type = None
        if not isinstance(base_policy, dict):
            errors.append(f"{prefix}.base_policy must be an object")
        else:
            base_policy_type = base_policy.get("type")
            if base_policy_type not in BASE_POLICY_TYPES:
                errors.append(f"{prefix}.base_policy.type must be one of {sorted(BASE_POLICY_TYPES)}")
            if base_policy_type == "blocker_head" and base_policy.get("issue") not in work_items:
                errors.append(f"{prefix}.base_policy.issue must reference a work item")
            if base_policy_type == "integration_head" and base_policy.get("integration_issue") not in work_items:
                errors.append(f"{prefix}.base_policy.integration_issue must reference a work item")
        write_scope = item.get("write_scope")
        if not isinstance(write_scope, list) or not write_scope:
            errors.append(f"{prefix}.write_scope must be a non-empty list")
        dependencies = item.get("dependencies", [])
        if not isinstance(dependencies, list):
            errors.append(f"{prefix}.dependencies must be a list")
            continue
        if dependencies and item.get("worktree_state") == "active":
            errors.append(f"{prefix} is blocked but has active worktree_state")
        for index, dep in enumerate(dependencies):
            dep_prefix = f"{prefix}.dependencies[{index}]"
            if not isinstance(dep, dict):
                errors.append(f"{dep_prefix} must be an object")
                continue
            dep_issue = dep.get("issue")
            if dep_issue not in work_items:
                errors.append(f"{dep_prefix}.issue references unknown issue {dep_issue}")
            if dep.get("strength") not in EDGE_STRENGTHS:
                errors.append(f"{dep_prefix}.strength must be one of {sorted(EDGE_STRENGTHS)}")
            if dep.get("release_on") not in RELEASE_ON:
                errors.append(f"{dep_prefix}.release_on must be one of {sorted(RELEASE_ON)}")
            if dep.get("base_effect") not in BASE_EFFECTS:
                errors.append(f"{dep_prefix}.base_effect must be one of {sorted(BASE_EFFECTS)}")
        if isinstance(base_policy, dict) and isinstance(dependencies, list):
            blocker_head_deps = [
                dep.get("issue")
                for dep in dependencies
                if isinstance(dep, dict) and dep.get("base_effect") == "branch_from_blocker_head"
            ]
            integration_head_deps = [
                dep.get("issue")
                for dep in dependencies
                if isinstance(dep, dict) and dep.get("base_effect") == "branch_from_integration_head"
            ]
            if len(blocker_head_deps) > 1:
                errors.append(
                    f"{prefix} uses branch_from_blocker_head with multiple blocker heads; "
                    "use an integration work item and branch_from_integration_head"
                )
            if blocker_head_deps:
                blocker_issue = blocker_head_deps[0]
                if base_policy_type != "blocker_head":
                    errors.append(f"{prefix}.base_policy.type must be blocker_head")
                elif base_policy.get("issue") != blocker_issue:
                    errors.append(f"{prefix}.base_policy.issue must match dependency {blocker_issue}")
            elif base_policy_type == "blocker_head":
                errors.append(f"{prefix}.base_policy.type blocker_head requires branch_from_blocker_head dependency")
            if integration_head_deps:
                if len(integration_head_deps) > 1:
                    errors.append(
                        f"{prefix} uses branch_from_integration_head with multiple integration heads; "
                        "use one integration work item as the base and set other dependencies to base_effect none"
                    )
                if base_policy_type != "integration_head":
                    errors.append(f"{prefix}.base_policy.type must be integration_head")
                elif base_policy.get("integration_issue") not in integration_head_deps:
                    errors.append(
                        f"{prefix}.base_policy.integration_issue must match a branch_from_integration_head dependency"
                    )
            elif base_policy_type == "integration_head":
                errors.append(
                    f"{prefix}.base_policy.type integration_head requires branch_from_integration_head dependency"
                )

    cycle = dependency_cycle(work_items)
    if cycle:
        errors.append("dependency cycle detected: " + " -> ".join(cycle))
    return errors


def validate_runtime_state(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    epic_id = state.get("epic_id")
    if not isinstance(epic_id, str) or not is_lower_kebab(epic_id):
        errors.append("epic_id must be lower-kebab-case ASCII")
    if not isinstance(state.get("issues", {}), dict):
        errors.append("issues must be an object")
    else:
        for issue_id, record in state.get("issues", {}).items():
            if not isinstance(record, dict):
                errors.append(f"issues.{issue_id} must be an object")
                continue
            status = record.get("status")
            review = record.get("review", {})
            if status in SUCCESS_STATUSES and not isinstance(review, dict):
                errors.append(
                    f"issues.{issue_id}.review.range must use committed BASE_SHA..HEAD_SHA"
                )
                continue
            if status in SUCCESS_STATUSES and isinstance(review, dict):
                review_range = review.get("range") or review.get("review_range")
                if not isinstance(review_range, str) or not is_commit_range(review_range):
                    errors.append(
                        f"issues.{issue_id}.review.range must use committed BASE_SHA..HEAD_SHA, not working-tree"
                    )
    human_requests = state.get("human_requests", [])
    if not isinstance(human_requests, list):
        errors.append("human_requests must be a list")
    else:
        for index, request in enumerate(human_requests):
            prefix = f"human_requests[{index}]"
            if not isinstance(request, dict):
                errors.append(f"{prefix} must be an object")
                continue
            if request.get("scope") not in {"issue", "descendants", "resource", "epic"}:
                errors.append(f"{prefix}.scope must be issue, descendants, resource, or epic")
    return errors


def dependency_cycle(work_items: dict[str, Any]) -> list[str]:
    graph = {
        issue_id: [
            dep["issue"]
            for dep in item.get("dependencies", [])
            if isinstance(dep, dict) and dep.get("issue") in work_items
        ]
        for issue_id, item in work_items.items()
        if isinstance(item, dict)
    }
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in visiting:
            start = stack.index(node)
            return stack[start:] + [node]
        if node in visited:
            return None
        visiting.add(node)
        stack.append(node)
        for dep in graph.get(node, []):
            found = visit(dep)
            if found:
                return found
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for issue_id in graph:
        found = visit(issue_id)
        if found:
            return found
    return []


def issue_record(runtime: dict[str, Any], issue_id: str) -> dict[str, Any]:
    issues = runtime.get("issues", {})
    if isinstance(issues, dict) and isinstance(issues.get(issue_id), dict):
        return issues[issue_id]
    return {"status": "PENDING"}


def issue_status(runtime: dict[str, Any], issue_id: str) -> str:
    status = issue_record(runtime, issue_id).get("status", "PENDING")
    return status if isinstance(status, str) else "PENDING"


def dependency_satisfied(dep: dict[str, Any], runtime: dict[str, Any]) -> bool:
    record = issue_record(runtime, dep["issue"])
    release_on = dep.get("release_on")
    signals = record.get("signals", [])
    if release_on in signals:
        return True
    if release_on == "review_approved":
        review = record.get("review", {})
        return (
            isinstance(review, dict)
            and review.get("status") in {"approved", "承認済み"}
        ) or record.get("status") in {"PR_READY", "COMPLETE", "DONE"}
    if release_on == "artifact_ready":
        return record.get("status") in {
            "ARTIFACT_READY",
            "IMPLEMENTED",
            "VERIFICATION_PASSED",
            "PR_READY",
            "COMPLETE",
            "DONE",
        }
    if release_on == "integrated":
        return record.get("status") in {"INTEGRATED", "COMPLETE", "DONE"}
    if release_on == "pr_opened":
        return bool(record.get("pr_opened") or record.get("pr"))
    if release_on == "pr_merged":
        return bool(record.get("pr_merged"))
    if release_on in {"human_decision", "external_condition"}:
        return bool(record.get(release_on))
    return False


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


def descendants_of(issue_id: str, work_items: dict[str, Any]) -> set[str]:
    children: dict[str, set[str]] = {key: set() for key in work_items}
    for child, item in work_items.items():
        for dep in item.get("dependencies", []):
            if isinstance(dep, dict) and dep.get("issue") in children:
                children[dep["issue"]].add(child)

    descendants: set[str] = set()
    queue = list(children.get(issue_id, set()))
    while queue:
        child = queue.pop(0)
        if child in descendants:
            continue
        descendants.add(child)
        queue.extend(children.get(child, set()))
    return descendants


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


def git_output(args: list[str], cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )


def skill_roots() -> list[Path]:
    home = Path.home()
    roots = [
        home / ".agents" / "skills",
        home / ".codex" / "skills",
        Path.cwd() / "skills",
    ]
    cache = home / ".codex" / "plugins" / "cache"
    if cache.exists():
        for pattern in ("*/skills", "*/*/skills", "*/*/*/skills"):
            roots.extend(path for path in cache.glob(pattern) if path.is_dir())
    unique: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        if root not in seen:
            unique.append(root)
            seen.add(root)
    return unique


def find_skill(name: str) -> str | None:
    for root in skill_roots():
        skill_file = root / name / "SKILL.md"
        if skill_file.exists():
            return str(skill_file)
    return None
