from __future__ import annotations

import os
from typing import Any

from ..constants import (
    BASE_EFFECTS,
    BASE_POLICY_TYPES,
    EDGE_STRENGTHS,
    FINAL_PR_HEADS,
    FINAL_PR_MERGE_POLICIES,
    ISSUE_PR_BASES,
    ISSUE_PR_MERGE_POLICIES,
    MAX_REVIEW_CYCLES,
    RELEASE_ON,
    REMOTE_MODES,
    WORKTREE_STATES,
)
from ..graph import dependency_cycle
from ..identifiers import (
    canonical_issue_branch,
    is_canonical_issue_branch,
    is_full_commit_sha,
    is_issue_id,
    is_lower_kebab,
)


def validate_execution_envelope(envelope: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if envelope.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    epic_id = envelope.get("epic_id")
    if not isinstance(epic_id, str) or not is_lower_kebab(epic_id):
        errors.append("epic_id must be lower-kebab-case ASCII")

    if not isinstance(envelope.get("revision"), int) or envelope.get("revision", 0) < 1:
        errors.append("revision must be a positive integer")

    execution_policy = envelope.get("execution_policy")
    if not isinstance(execution_policy, dict):
        errors.append("execution_policy is required")
    else:
        if execution_policy.get("worker_context_required") is not True:
            errors.append("execution_policy.worker_context_required must be true")
        if execution_policy.get("coordinator_may_implement") is not False:
            errors.append("execution_policy.coordinator_may_implement must be false")
        if execution_policy.get("serial_fallback_mode") != "worker_context_only":
            errors.append("execution_policy.serial_fallback_mode must be worker_context_only")

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
        epic_base_branch_state = epic_base.get("branch_state")
        if epic_base_branch_state is not None and epic_base_branch_state not in WORKTREE_STATES:
            errors.append(f"epic_base.branch_state must be one of {sorted(WORKTREE_STATES)}")
        epic_base_worktree_path = epic_base.get("worktree_path")
        if epic_base_worktree_path is not None and (
            not isinstance(epic_base_worktree_path, str)
            or not os.path.isabs(epic_base_worktree_path)
        ):
            errors.append("epic_base.worktree_path must be an absolute path when provided")

    review_policy = envelope.get("review_policy")
    if not isinstance(review_policy, dict):
        errors.append("review_policy is required")
    else:
        max_review_cycles = review_policy.get("max_review_cycles")
        if (
            not isinstance(max_review_cycles, int)
            or max_review_cycles < 1
            or max_review_cycles > MAX_REVIEW_CYCLES
        ):
            errors.append("review_policy.max_review_cycles must be an integer between 1 and 2")
        max_fix_cycles = review_policy.get("max_fix_cycles")
        if max_fix_cycles is not None and (
            not isinstance(max_fix_cycles, int)
            or max_fix_cycles < 0
            or max_fix_cycles > MAX_REVIEW_CYCLES
        ):
            errors.append("review_policy.max_fix_cycles must be an integer between 0 and 2")

    remote_policy = envelope.get("remote_write_policy")
    batch_issue_prs = False
    if not isinstance(remote_policy, dict):
        errors.append("remote_write_policy must be an object")
    else:
        if remote_policy.get("mode") not in REMOTE_MODES:
            errors.append(f"remote_write_policy.mode must be one of {sorted(REMOTE_MODES)}")
        elif remote_policy.get("mode") == "batch_issue_prs":
            batch_issue_prs = True
            expected_epic_base_ref = f"codex/{epic_id}/epic-base" if isinstance(epic_id, str) else None
            if isinstance(epic_base, dict) and epic_base.get("ref") != expected_epic_base_ref:
                errors.append(f"epic_base.ref must be {expected_epic_base_ref} for batch_issue_prs")
            if isinstance(epic_base, dict) and epic_base.get("branch_state") not in WORKTREE_STATES:
                errors.append(
                    f"epic_base.branch_state must be one of {sorted(WORKTREE_STATES)} for batch_issue_prs"
                )
            issue_prs = remote_policy.get("issue_prs")
            if not isinstance(issue_prs, dict):
                errors.append("remote_write_policy.issue_prs is required for batch_issue_prs")
            else:
                if issue_prs.get("base") not in ISSUE_PR_BASES:
                    errors.append("remote_write_policy.issue_prs.base must be epic_base.ref")
                if issue_prs.get("merge") not in ISSUE_PR_MERGE_POLICIES:
                    errors.append(
                        "remote_write_policy.issue_prs.merge must be agent_default_with_human_escalation"
                    )
            final_pr = remote_policy.get("final_pr")
            if not isinstance(final_pr, dict):
                errors.append("remote_write_policy.final_pr is required for batch_issue_prs")
            else:
                if final_pr.get("head") not in FINAL_PR_HEADS:
                    errors.append("remote_write_policy.final_pr.head must be epic_base.ref")
                if final_pr.get("base") != "main":
                    errors.append("remote_write_policy.final_pr.base must be main")
                if final_pr.get("merge") not in FINAL_PR_MERGE_POLICIES:
                    errors.append("remote_write_policy.final_pr.merge must be human_only")

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
        for field in (
            "worker_packet_schema",
            "worker_packet_template",
            "worker_packet_validator",
        ):
            value = context_policy.get(field)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                errors.append(f"context_policy.{field} must be a non-empty string")

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
            if batch_issue_prs and isinstance(epic_id, str) and not is_canonical_issue_branch(branch, epic_id, issue_id):
                errors.append(
                    f"{prefix}.branch must match {canonical_issue_branch(epic_id, issue_id)}"
                )
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
