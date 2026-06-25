from __future__ import annotations

from typing import Any

from .identifiers import is_issue_id
from .validation.execution_envelope import validate_execution_envelope
from .validation.runtime_state import validate_runtime_state


def issue_branch_owner(envelope: dict[str, Any], branch: Any) -> str | None:
    if not isinstance(branch, str):
        return None
    work_items = envelope.get("work_items", {})
    if not isinstance(work_items, dict):
        return None
    for issue_id, item in work_items.items():
        if isinstance(item, dict) and item.get("branch") == branch:
            return issue_id
    return None


def delivery_issue_scope(envelope: dict[str, Any], plan: dict[str, Any], errors: list[str]) -> list[str]:
    work_items = envelope.get("work_items", {})
    if not isinstance(work_items, dict):
        errors.append("work_items must be a non-empty object")
        return []
    scope = plan.get("issue_scope")
    if scope is None:
        return list(work_items)
    if not isinstance(scope, list) or not scope:
        errors.append("issue_scope must be a non-empty list when provided")
        return []
    issues: list[str] = []
    for index, issue_id in enumerate(scope):
        if not isinstance(issue_id, str) or not is_issue_id(issue_id):
            errors.append(f"issue_scope[{index}] must look like G2PR-001")
            continue
        if issue_id not in work_items:
            errors.append(f"issue_scope[{index}] references unknown issue {issue_id}")
            continue
        issues.append(issue_id)
    return issues


def validate_delivery_plan(envelope: dict[str, Any], runtime: dict[str, Any], plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(f"envelope: {error}" for error in validate_execution_envelope(envelope))
    errors.extend(f"runtime_state: {error}" for error in validate_runtime_state(runtime))
    if errors:
        return errors
    if runtime.get("epic_id") != envelope.get("epic_id"):
        errors.append("runtime_state.epic_id must match envelope.epic_id")
    if runtime.get("envelope_revision") != envelope.get("revision"):
        errors.append("runtime_state.envelope_revision must match envelope.revision")
    if errors:
        return errors

    if not isinstance(plan, dict):
        return ["delivery plan must be an object"]
    action = plan.get("action")
    if action not in {"issue_pr", "final_pr"}:
        errors.append("action must be issue_pr or final_pr")
        return errors

    remote_policy = envelope.get("remote_write_policy", {})
    if not isinstance(remote_policy, dict) or remote_policy.get("mode") != "batch_issue_prs":
        errors.append("delivery plan requires remote_write_policy.mode batch_issue_prs")
        return errors

    epic_base = envelope.get("epic_base", {})
    epic_base_ref = epic_base.get("ref") if isinstance(epic_base, dict) else None
    head = plan.get("head")
    base = plan.get("base")
    if not isinstance(head, str) or not head:
        errors.append("head must be a non-empty branch name")
    if not isinstance(base, str) or not base:
        errors.append("base must be a non-empty branch name")
    if errors:
        return errors

    if action == "issue_pr":
        issue_id = plan.get("issue")
        work_items = envelope.get("work_items", {})
        if not isinstance(issue_id, str) or not is_issue_id(issue_id) or issue_id not in work_items:
            errors.append("issue must reference an envelope work item for issue_pr")
            return errors
        item = work_items[issue_id]
        expected_head = item.get("branch") if isinstance(item, dict) else None
        if head != expected_head:
            errors.append(f"issue_pr.head must be {expected_head} for {issue_id}")
        if base != epic_base_ref:
            errors.append(f"issue_pr.base must be {epic_base_ref}")
        return errors

    if base != "main":
        errors.append("final_pr.base must be main")
    if head != epic_base_ref:
        owner = issue_branch_owner(envelope, head)
        if owner:
            errors.append(f"final_pr.head must be {epic_base_ref}, not issue branch {head} ({owner})")
        else:
            errors.append(f"final_pr.head must be {epic_base_ref}")
    if isinstance(epic_base, dict) and epic_base.get("branch_state") != "active":
        errors.append("epic_base.branch_state must be active before final PR")

    issues = delivery_issue_scope(envelope, plan, errors)
    runtime_issues = runtime.get("issues", {})
    if isinstance(runtime_issues, dict):
        for issue_id in issues:
            record = runtime_issues.get(issue_id)
            if not isinstance(record, dict) or record.get("pr_merged") is not True:
                errors.append(f"issues.{issue_id}.pr_merged must be true before final PR")
    return errors
