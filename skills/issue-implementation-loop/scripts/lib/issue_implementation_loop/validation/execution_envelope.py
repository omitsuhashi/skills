from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ..approved_spec_binding import BindingError, load_verified_input_packet
from ..constants import (
    APPROVED_REMOTE_ACTIONS,
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


TOP_LEVEL_FIELDS = {
    "schema_version",
    "epic_id",
    "revision",
    "approved_spec_binding",
    "epic_base",
    "execution_policy",
    "review_policy",
    "human_policy",
    "context_policy",
    "phase_branch_policy",
    "remote_write_policy",
    "work_items",
}
EPIC_BASE_FIELDS = {"ref", "sha", "branch_state", "worktree_path"}
EXECUTION_POLICY_FIELDS = {
    "parallel_preferred",
    "serial_fallback_preapproved",
    "worker_context_required",
    "coordinator_may_implement",
    "serial_fallback_mode",
    "implementation_slots",
    "review_slots",
    "wave_is_barrier",
}
EXECUTION_POLICY_REQUIRED = {
    "worker_context_required",
    "coordinator_may_implement",
    "serial_fallback_mode",
}
REVIEW_POLICY_FIELDS = {
    "primary",
    "fallbacks",
    "manual_fallback_preapproved",
    "max_review_cycles",
    "max_fix_cycles",
    "same_finding_limit",
    "hardening_candidates",
}
HUMAN_POLICY_FIELDS = {"default_scope", "epic_scope_requires_reason"}
CONTEXT_POLICY_FIELDS = {
    "paths_first",
    "max_worker_packet_words",
    "max_worker_report_words",
    "include_full_spec_text",
    "include_full_ledger_text",
    "worker_packet_schema",
    "worker_packet_template",
    "worker_packet_validator",
    "session_compaction",
}
CONTEXT_POLICY_REQUIRED = {
    "paths_first",
    "max_worker_packet_words",
    "max_worker_report_words",
    "include_full_spec_text",
    "include_full_ledger_text",
    "session_compaction",
}
REMOTE_POLICY_FIELDS = {"mode", "approved_actions", "issue_prs", "final_pr"}
ISSUE_PR_FIELDS = {"base", "merge"}
FINAL_PR_FIELDS = {"head", "base", "merge", "draft_default"}
WORK_ITEM_FIELDS = {
    "title",
    "source",
    "acceptance_criteria",
    "non_goals",
    "verification",
    "branch",
    "worktree_path",
    "worktree_state",
    "base_policy",
    "write_scope",
    "dependencies",
}
SOURCE_FIELDS = {"type", "path"}
BASE_POLICY_FIELDS = {"type", "issue", "integration_issue"}
DEPENDENCY_FIELDS = {"issue", "strength", "release_on", "base_effect"}

SESSION_COMPACTION_REQUIRED_VALUES = {
    "soft_trigger_percent": 65,
    "hard_stop_percent": 75,
    "mandatory_handoff_compaction": 1,
    "mandatory_phase_transition_gc": True,
    "carry_forward_capsule_words_default": 400,
    "carry_forward_capsule_words_hard": 600,
    "inline_json_code_diff_lines_hard": 80,
}

PHASE_BRANCH_POLICY_REQUIRED_VALUES = {
    "planning_artifacts_branch": "current_session_branch",
    "phase_approval_commit_required": True,
    "phase_transition_requires_clean_scope": True,
    "execution_coordinator_context": "fresh_or_compacted",
    "main_planning_session_may_implement": False,
    "worktree_per_issue": True,
    "branch_prefix": "codex",
    "epic_base_ref_pattern": "codex/<epic-id>/epic-base",
    "issue_branch_pattern": "codex/<epic-id>/<local-id>-<slug>",
    "epic_base_owner": "execution_coordinator",
    "issue_branch_owner": "worker",
    "integration_branch_policy": "approved_integration_work_item_only",
}

HARDENING_CANDIDATES_REQUIRED_FIELDS = {
    "candidate_registry_path",
    "issue_completion_blocking",
    "max_candidates_per_issue",
    "max_summary_words",
    "ready_or_merge_requires_decisions",
    "worker_packet_decision_state",
}


def _closed(
    value: Any,
    *,
    allowed: set[str],
    required: set[str],
    prefix: str,
    errors: list[str],
) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return False
    for field in sorted(set(value) - allowed):
        errors.append(f"unknown field: {prefix}.{field}" if prefix else f"unknown field: {field}")
    for field in sorted(required - set(value)):
        errors.append(f"{prefix}.{field} is required" if prefix else f"{field} is required")
    return True


def _positive_int(value: Any) -> bool:
    return type(value) is int and value > 0


def _string_list(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def _validate_exact_policy_object(
    value: Any,
    *,
    prefix: str,
    required_values: dict[str, object],
    errors: list[str],
) -> None:
    if not _closed(
        value,
        allowed=set(required_values),
        required=set(required_values),
        prefix=prefix,
        errors=errors,
    ):
        return
    for field, expected in required_values.items():
        if value.get(field) != expected or (
            type(expected) is int and type(value.get(field)) is not int
        ):
            rendered = str(expected).lower() if isinstance(expected, bool) else str(expected)
            errors.append(f"{prefix}.{field} must be {rendered}")


def _validate_hardening_candidates_policy(policy: Any, errors: list[str]) -> None:
    prefix = "review_policy.hardening_candidates"
    if policy is None:
        return
    if not _closed(
        policy,
        allowed=HARDENING_CANDIDATES_REQUIRED_FIELDS,
        required=HARDENING_CANDIDATES_REQUIRED_FIELDS,
        prefix=prefix,
        errors=errors,
    ):
        return
    if policy.get("candidate_registry_path") != "decisions/hardening-candidates.json":
        errors.append(f"{prefix}.candidate_registry_path must be decisions/hardening-candidates.json")
    max_candidates = policy.get("max_candidates_per_issue")
    if type(max_candidates) is not int or not 1 <= max_candidates <= 5:
        errors.append(f"{prefix}.max_candidates_per_issue must be an integer between 1 and 5")
    max_summary_words = policy.get("max_summary_words")
    if type(max_summary_words) is not int or not 1 <= max_summary_words <= 80:
        errors.append(f"{prefix}.max_summary_words must be an integer between 1 and 80")
    if policy.get("issue_completion_blocking") is not False:
        errors.append(f"{prefix}.issue_completion_blocking must be false")
    if policy.get("ready_or_merge_requires_decisions") is not True:
        errors.append(f"{prefix}.ready_or_merge_requires_decisions must be true")
    if policy.get("worker_packet_decision_state") != "forbidden":
        errors.append(f"{prefix}.worker_packet_decision_state must be forbidden")


def _validate_approved_intent(envelope: dict[str, Any], packet: dict[str, Any]) -> bool:
    if envelope.get("epic_id") != packet.get("epic_id"):
        return False
    remote = envelope.get("remote_write_policy")
    if not isinstance(remote, dict) or remote.get("mode") != packet.get("delivery_intent"):
        return False
    if packet.get("delivery_intent") == "local_only" and remote.get("approved_actions") != []:
        return False
    work_items = envelope.get("work_items")
    approved_items = packet.get("work_items")
    if not isinstance(work_items, dict) or not isinstance(approved_items, list):
        return False
    approved_by_id = {
        item.get("id"): item for item in approved_items if isinstance(item, dict)
    }
    if set(work_items) != set(approved_by_id):
        return False
    for issue_id, item in work_items.items():
        approved = approved_by_id[issue_id]
        for field in (
            "title",
            "source",
            "acceptance_criteria",
            "non_goals",
            "verification",
            "write_scope",
        ):
            if item.get(field) != approved.get(field):
                return False
        dependencies = item.get("dependencies")
        if not isinstance(dependencies, list):
            return False
        projected = [
            dependency.get("issue")
            for dependency in dependencies
            if isinstance(dependency, dict)
        ]
        if projected != approved.get("dependencies"):
            return False
    return True


def validate_execution_envelope(
    envelope: dict[str, Any], repo_root: str | os.PathLike[str] | None = None
) -> list[str]:
    errors: list[str] = []
    if not isinstance(envelope, dict) or envelope.get("schema_version") != 4:
        return ["SCHEMA_UNSUPPORTED"]
    _closed(
        envelope,
        allowed=TOP_LEVEL_FIELDS,
        required=TOP_LEVEL_FIELDS,
        prefix="",
        errors=errors,
    )

    epic_id = envelope.get("epic_id")
    if not isinstance(epic_id, str) or not is_lower_kebab(epic_id):
        errors.append("epic_id must be lower-kebab-case ASCII")
    if not _positive_int(envelope.get("revision")):
        errors.append("revision must be a positive integer")

    epic_base = envelope.get("epic_base")
    if _closed(
        epic_base,
        allowed=EPIC_BASE_FIELDS,
        required={"ref", "sha"},
        prefix="epic_base",
        errors=errors,
    ):
        if not isinstance(epic_base.get("ref"), str) or not epic_base["ref"].strip():
            errors.append("epic_base.ref must be a non-empty string")
        if not isinstance(epic_base.get("sha"), str) or not is_full_commit_sha(epic_base["sha"]):
            errors.append("epic_base.sha must be a full 40- or 64-character hex commit SHA")
        if "branch_state" in epic_base and epic_base.get("branch_state") not in WORKTREE_STATES:
            errors.append(f"epic_base.branch_state must be one of {sorted(WORKTREE_STATES)}")
        if "worktree_path" in epic_base and (
            not isinstance(epic_base.get("worktree_path"), str)
            or not os.path.isabs(epic_base["worktree_path"])
        ):
            errors.append("epic_base.worktree_path must be an absolute path when provided")

    execution_policy = envelope.get("execution_policy")
    if _closed(
        execution_policy,
        allowed=EXECUTION_POLICY_FIELDS,
        required=EXECUTION_POLICY_REQUIRED,
        prefix="execution_policy",
        errors=errors,
    ):
        if execution_policy.get("worker_context_required") is not True:
            errors.append("execution_policy.worker_context_required must be true")
        if execution_policy.get("coordinator_may_implement") is not False:
            errors.append("execution_policy.coordinator_may_implement must be false")
        if execution_policy.get("serial_fallback_mode") != "worker_context_only":
            errors.append("execution_policy.serial_fallback_mode must be worker_context_only")
        for field in ("parallel_preferred", "serial_fallback_preapproved", "wave_is_barrier"):
            if field in execution_policy and type(execution_policy[field]) is not bool:
                errors.append(f"execution_policy.{field} must be boolean")
        for field in ("implementation_slots", "review_slots"):
            if field in execution_policy and not _positive_int(execution_policy[field]):
                errors.append(f"execution_policy.{field} must be a positive integer")

    review_policy = envelope.get("review_policy")
    if _closed(
        review_policy,
        allowed=REVIEW_POLICY_FIELDS,
        required={"max_review_cycles"},
        prefix="review_policy",
        errors=errors,
    ):
        max_review_cycles = review_policy.get("max_review_cycles")
        if type(max_review_cycles) is not int or not 1 <= max_review_cycles <= MAX_REVIEW_CYCLES:
            errors.append("review_policy.max_review_cycles must be an integer between 1 and 2")
        if "max_fix_cycles" in review_policy:
            max_fix_cycles = review_policy.get("max_fix_cycles")
            if type(max_fix_cycles) is not int or not 0 <= max_fix_cycles <= MAX_REVIEW_CYCLES:
                errors.append("review_policy.max_fix_cycles must be an integer between 0 and 2")
        if "same_finding_limit" in review_policy and not _positive_int(review_policy["same_finding_limit"]):
            errors.append("review_policy.same_finding_limit must be a positive integer")
        if "primary" in review_policy and (
            not isinstance(review_policy["primary"], str) or not review_policy["primary"].strip()
        ):
            errors.append("review_policy.primary must be a non-empty string")
        if "fallbacks" in review_policy and not _string_list(review_policy["fallbacks"], allow_empty=True):
            errors.append("review_policy.fallbacks must be a string list")
        if "manual_fallback_preapproved" in review_policy and type(review_policy["manual_fallback_preapproved"]) is not bool:
            errors.append("review_policy.manual_fallback_preapproved must be boolean")
        _validate_hardening_candidates_policy(review_policy.get("hardening_candidates"), errors)

    human_policy = envelope.get("human_policy")
    if _closed(
        human_policy,
        allowed=HUMAN_POLICY_FIELDS,
        required=HUMAN_POLICY_FIELDS,
        prefix="human_policy",
        errors=errors,
    ):
        if human_policy.get("default_scope") != "issue":
            errors.append("human_policy.default_scope must be issue")
        if human_policy.get("epic_scope_requires_reason") is not True:
            errors.append("human_policy.epic_scope_requires_reason must be true")

    context_policy = envelope.get("context_policy")
    if _closed(
        context_policy,
        allowed=CONTEXT_POLICY_FIELDS,
        required=CONTEXT_POLICY_REQUIRED,
        prefix="context_policy",
        errors=errors,
    ):
        if context_policy.get("paths_first") is not True:
            errors.append("context_policy.paths_first must be true")
        for field in ("max_worker_packet_words", "max_worker_report_words"):
            if not _positive_int(context_policy.get(field)):
                errors.append(f"context_policy.{field} must be a positive integer")
        if context_policy.get("include_full_spec_text") is not False:
            errors.append("context_policy.include_full_spec_text must be false")
        if context_policy.get("include_full_ledger_text") is not False:
            errors.append("context_policy.include_full_ledger_text must be false")
        _validate_exact_policy_object(
            context_policy.get("session_compaction"),
            prefix="context_policy.session_compaction",
            required_values=SESSION_COMPACTION_REQUIRED_VALUES,
            errors=errors,
        )
        ref_fields = {"worker_packet_schema", "worker_packet_template", "worker_packet_validator"}
        if set(context_policy) & ref_fields:
            for field in ref_fields:
                if not isinstance(context_policy.get(field), str) or not context_policy[field].strip():
                    errors.append(f"context_policy.{field} must be a non-empty string")

    _validate_exact_policy_object(
        envelope.get("phase_branch_policy"),
        prefix="phase_branch_policy",
        required_values=PHASE_BRANCH_POLICY_REQUIRED_VALUES,
        errors=errors,
    )

    remote_policy = envelope.get("remote_write_policy")
    batch_issue_prs = False
    if _closed(
        remote_policy,
        allowed=REMOTE_POLICY_FIELDS,
        required={"mode", "approved_actions"},
        prefix="remote_write_policy",
        errors=errors,
    ):
        mode = remote_policy.get("mode")
        if mode not in REMOTE_MODES:
            errors.append(f"remote_write_policy.mode must be one of {sorted(REMOTE_MODES)}")
        approved_actions = remote_policy.get("approved_actions")
        if not isinstance(approved_actions, list):
            errors.append("remote_write_policy.approved_actions must be a list")
        else:
            seen: set[str] = set()
            for index, action in enumerate(approved_actions):
                if action not in APPROVED_REMOTE_ACTIONS:
                    errors.append(f"remote_write_policy.approved_actions[{index}] must be one of {sorted(APPROVED_REMOTE_ACTIONS)}")
                elif action in seen:
                    errors.append(f"remote_write_policy.approved_actions[{index}] duplicates {action}")
                seen.add(action)
        if mode == "batch_issue_prs":
            batch_issue_prs = True
            expected_ref = f"codex/{epic_id}/epic-base" if isinstance(epic_id, str) else None
            if isinstance(epic_base, dict) and epic_base.get("ref") != expected_ref:
                errors.append(f"epic_base.ref must be {expected_ref} for batch_issue_prs")
            if isinstance(epic_base, dict) and epic_base.get("branch_state") not in WORKTREE_STATES:
                errors.append(f"epic_base.branch_state must be one of {sorted(WORKTREE_STATES)} for batch_issue_prs")
            issue_prs = remote_policy.get("issue_prs")
            if not _closed(issue_prs, allowed=ISSUE_PR_FIELDS, required=ISSUE_PR_FIELDS, prefix="remote_write_policy.issue_prs", errors=errors):
                pass
            else:
                if issue_prs.get("base") not in ISSUE_PR_BASES:
                    errors.append("remote_write_policy.issue_prs.base must be epic_base.ref")
                if issue_prs.get("merge") not in ISSUE_PR_MERGE_POLICIES:
                    errors.append("remote_write_policy.issue_prs.merge must be agent_default_with_human_escalation")
            final_pr = remote_policy.get("final_pr")
            if isinstance(final_pr, dict) and set(final_pr) - FINAL_PR_FIELDS:
                errors.append(
                    "ready-for-review, force push, and high-risk final PR actions are human-only"
                )
            if not _closed(final_pr, allowed=FINAL_PR_FIELDS, required={"head", "base", "merge"}, prefix="remote_write_policy.final_pr", errors=errors):
                pass
            else:
                if final_pr.get("head") not in FINAL_PR_HEADS:
                    errors.append("remote_write_policy.final_pr.head must be epic_base.ref")
                if final_pr.get("base") != "main":
                    errors.append("remote_write_policy.final_pr.base must be main")
                if final_pr.get("merge") not in FINAL_PR_MERGE_POLICIES:
                    errors.append("remote_write_policy.final_pr.merge must be human_only")
                if "draft_default" in final_pr and final_pr.get("draft_default") is not True:
                    errors.append("remote_write_policy.final_pr.draft_default must be true when provided")
        elif isinstance(remote_policy, dict) and set(remote_policy) - {"mode", "approved_actions"}:
            errors.append("remote_write_policy issue_prs/final_pr are allowed only for batch_issue_prs")

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
        if not _closed(item, allowed=WORK_ITEM_FIELDS, required=WORK_ITEM_FIELDS, prefix=prefix, errors=errors):
            continue
        if not isinstance(item.get("title"), str) or not item["title"].strip():
            errors.append(f"{prefix}.title must be a non-empty string")
        source = item.get("source")
        if _closed(source, allowed=SOURCE_FIELDS, required=SOURCE_FIELDS, prefix=f"{prefix}.source", errors=errors):
            if source.get("type") != "local" or not isinstance(source.get("path"), str) or not source["path"].strip():
                errors.append(f"{prefix}.source must be a local source path")
        for field in ("acceptance_criteria", "non_goals", "verification", "write_scope"):
            if not _string_list(item.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string list")
        branch = item.get("branch")
        if not isinstance(branch, str) or not branch:
            errors.append(f"{prefix}.branch is required")
        else:
            if isinstance(epic_id, str) and f"/{epic_id}/" not in branch:
                errors.append(f"{prefix}.branch must include /{epic_id}/ namespace")
            if batch_issue_prs and isinstance(epic_id, str) and not is_canonical_issue_branch(branch, epic_id, issue_id):
                errors.append(f"{prefix}.branch must match {canonical_issue_branch(epic_id, issue_id)}")
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
        if _closed(base_policy, allowed=BASE_POLICY_FIELDS, required={"type"}, prefix=f"{prefix}.base_policy", errors=errors):
            base_policy_type = base_policy.get("type")
            if base_policy_type not in BASE_POLICY_TYPES:
                errors.append(f"{prefix}.base_policy.type must be one of {sorted(BASE_POLICY_TYPES)}")
            if base_policy_type == "blocker_head" and base_policy.get("issue") not in work_items:
                errors.append(f"{prefix}.base_policy.issue must reference a work item")
            if base_policy_type == "integration_head" and base_policy.get("integration_issue") not in work_items:
                errors.append(f"{prefix}.base_policy.integration_issue must reference a work item")
        dependencies = item.get("dependencies")
        if not isinstance(dependencies, list):
            errors.append(f"{prefix}.dependencies must be a list")
            continue
        if dependencies and item.get("worktree_state") == "active":
            errors.append(f"{prefix} is blocked but has active worktree_state")
        for index, dependency in enumerate(dependencies):
            dep_prefix = f"{prefix}.dependencies[{index}]"
            if not _closed(dependency, allowed=DEPENDENCY_FIELDS, required=DEPENDENCY_FIELDS, prefix=dep_prefix, errors=errors):
                continue
            if dependency.get("issue") not in work_items:
                errors.append(f"{dep_prefix}.issue references unknown issue {dependency.get('issue')}")
            if dependency.get("strength") not in EDGE_STRENGTHS:
                errors.append(f"{dep_prefix}.strength must be one of {sorted(EDGE_STRENGTHS)}")
            if dependency.get("release_on") not in RELEASE_ON:
                errors.append(f"{dep_prefix}.release_on must be one of {sorted(RELEASE_ON)}")
            if dependency.get("base_effect") not in BASE_EFFECTS:
                errors.append(f"{dep_prefix}.base_effect must be one of {sorted(BASE_EFFECTS)}")
        blocker_heads = [dependency.get("issue") for dependency in dependencies if isinstance(dependency, dict) and dependency.get("base_effect") == "branch_from_blocker_head"]
        integration_heads = [dependency.get("issue") for dependency in dependencies if isinstance(dependency, dict) and dependency.get("base_effect") == "branch_from_integration_head"]
        if len(blocker_heads) > 1:
            errors.append(f"{prefix} uses branch_from_blocker_head with multiple blocker heads; use an integration work item and branch_from_integration_head")
        if blocker_heads:
            if base_policy_type != "blocker_head":
                errors.append(f"{prefix}.base_policy.type must be blocker_head")
            elif base_policy.get("issue") != blocker_heads[0]:
                errors.append(f"{prefix}.base_policy.issue must match dependency {blocker_heads[0]}")
        elif base_policy_type == "blocker_head":
            errors.append(f"{prefix}.base_policy.type blocker_head requires branch_from_blocker_head dependency")
        if integration_heads:
            if len(integration_heads) > 1:
                errors.append(f"{prefix} uses branch_from_integration_head with multiple integration heads; use one integration work item as the base and set other dependencies to base_effect none")
            if base_policy_type != "integration_head":
                errors.append(f"{prefix}.base_policy.type must be integration_head")
            elif base_policy.get("integration_issue") not in integration_heads:
                errors.append(f"{prefix}.base_policy.integration_issue must match a branch_from_integration_head dependency")
        elif base_policy_type == "integration_head":
            errors.append(f"{prefix}.base_policy.type integration_head requires branch_from_integration_head dependency")

    cycle = dependency_cycle(work_items)
    if cycle:
        errors.append("dependency cycle detected: " + " -> ".join(cycle))
    if errors:
        return errors
    try:
        packet = load_verified_input_packet(
            Path.cwd() if repo_root is None else repo_root,
            envelope.get("approved_spec_binding"),
            ancestor_ref=epic_base.get("sha") if isinstance(epic_base, dict) else None,
        )
    except BindingError as error:
        return [error.code]
    if not _validate_approved_intent(envelope, packet):
        return ["BINDING_MISMATCH"]
    return []
