from __future__ import annotations

import os
from typing import Any

from ..approved_spec_binding import BindingError, approved_spec_binding_ref
from ..identifiers import commit_range_parts, is_full_commit_sha
from ..review import review_approved_or_accepted
from .execution_envelope import validate_execution_envelope
from .runtime_state import validate_runtime_epoch, validate_runtime_state


RESULT_FIELDS = {
    "schema_version",
    "approved_spec_binding",
    "epic_id",
    "status",
    "envelope_revision",
    "epic_base",
    "issues",
    "pending_human_requests",
    "delivery_candidates",
    "runtime_state_root",
}
RESULT_REQUIRED = RESULT_FIELDS
ISSUE_FIELDS = {
    "status",
    "branch",
    "worktree",
    "base_sha",
    "head_sha",
    "verification",
    "implementation_review",
    "pr",
    "pr_opened",
    "pr_merged",
    "residual_risks",
}
ISSUE_REQUIRED = {
    "status",
    "branch",
    "worktree",
    "base_sha",
    "head_sha",
    "verification",
    "implementation_review",
    "residual_risks",
}
EPIC_BASE_FIELDS = {"branch", "initial_sha", "current_sha", "branch_exists"}
OPTIONAL_PR_FIELDS = {"pr", "pr_opened", "pr_merged"}


def validate_execution_result(
    envelope: dict[str, Any],
    runtime: dict[str, Any],
    result: dict[str, Any],
    *,
    repo_root: str | os.PathLike[str],
    candidate_registry: dict[str, Any] | None = None,
    candidate_registry_path: str = "hardening-candidates.json",
    candidate_registry_load_error: str | None = None,
) -> list[str]:
    if not isinstance(result, dict) or result.get("schema_version") != 2:
        return ["SCHEMA_UNSUPPORTED"]
    if set(result) != RESULT_REQUIRED:
        return ["SCHEMA_UNSUPPORTED"]
    try:
        result_binding = approved_spec_binding_ref(
            result.get("approved_spec_binding")
        ).to_dict()
    except BindingError as error:
        return [error.code]

    envelope_errors = validate_execution_envelope(envelope, repo_root)
    if envelope_errors:
        return envelope_errors
    runtime_errors = validate_runtime_state(runtime)
    if runtime_errors:
        return runtime_errors
    epoch_errors = validate_runtime_epoch(envelope, runtime)
    if epoch_errors:
        return epoch_errors
    active_binding = envelope.get("approved_spec_binding")
    if result_binding != active_binding:
        return ["BINDING_MISMATCH"]

    from ..delivery import hardening_candidate_report

    registry_errors = hardening_candidate_report(
        runtime,
        candidate_registry,
        candidate_registry_path=candidate_registry_path,
        candidate_registry_load_error=candidate_registry_load_error,
    )["errors"]
    if registry_errors:
        return registry_errors

    errors: list[str] = []
    if result.get("epic_id") != envelope.get("epic_id"):
        errors.append("BINDING_MISMATCH")
    if result.get("envelope_revision") != envelope.get("revision"):
        errors.append("BINDING_MISMATCH")
    if result.get("status") not in {"local_complete", "delivered"}:
        errors.append("status must be local_complete or delivered")
    if result.get("pending_human_requests") != runtime.get("human_requests"):
        errors.append("BINDING_MISMATCH")
    runtime_root = result.get("runtime_state_root")
    if not isinstance(runtime_root, str) or not os.path.isabs(runtime_root):
        errors.append("runtime_state_root must be an absolute path")

    epic_base = result.get("epic_base")
    envelope_epic_base = envelope.get("epic_base", {})
    if not isinstance(epic_base, dict) or set(epic_base) != EPIC_BASE_FIELDS:
        errors.append("SCHEMA_UNSUPPORTED")
    else:
        if epic_base.get("branch") != envelope_epic_base.get("ref"):
            errors.append("BINDING_MISMATCH")
        if epic_base.get("initial_sha") != envelope_epic_base.get("sha"):
            errors.append("BINDING_MISMATCH")
        if not isinstance(epic_base.get("current_sha"), str) or not is_full_commit_sha(
            epic_base["current_sha"]
        ):
            errors.append("SCHEMA_UNSUPPORTED")
        if epic_base.get("branch_exists") is not True:
            errors.append("SCHEMA_UNSUPPORTED")

    work_items = envelope.get("work_items", {})
    result_issues = result.get("issues")
    runtime_issues = runtime.get("issues", {})
    if not isinstance(result_issues, dict) or set(result_issues) != set(work_items):
        return errors + ["BINDING_MISMATCH"]
    if not isinstance(runtime_issues, dict):
        return errors + ["BINDING_MISMATCH"]
    candidates = result.get("delivery_candidates")
    if (
        not isinstance(candidates, list)
        or not candidates
        or candidates != list(work_items)
        or len(candidates) != len(set(candidates))
    ):
        errors.append("BINDING_MISMATCH")

    for issue_id, item in work_items.items():
        record = result_issues.get(issue_id)
        runtime_record = runtime_issues.get(issue_id)
        if (
            not isinstance(record, dict)
            or set(record) - ISSUE_FIELDS
            or not ISSUE_REQUIRED.issubset(record)
            or not isinstance(runtime_record, dict)
        ):
            errors.append("BINDING_MISMATCH")
            continue
        if record.get("status") != runtime_record.get("status"):
            errors.append("BINDING_MISMATCH")
        if (
            record.get("branch") != item.get("branch")
            or runtime_record.get("branch", item.get("branch")) != item.get("branch")
        ):
            errors.append("BINDING_MISMATCH")
        if (
            record.get("worktree") != item.get("worktree_path")
            or runtime_record.get("worktree", item.get("worktree_path"))
            != item.get("worktree_path")
        ):
            errors.append("BINDING_MISMATCH")
        for field in ("base_sha", "head_sha"):
            value = record.get(field)
            if (
                not isinstance(value, str)
                or not is_full_commit_sha(value)
                or value != runtime_record.get(field)
            ):
                errors.append("BINDING_MISMATCH")
        review = record.get("implementation_review")
        runtime_review = runtime_record.get("review")
        if not isinstance(review, dict) or review != runtime_review:
            errors.append("BINDING_MISMATCH")
            continue
        review_range = review.get("range") or review.get("review_range")
        parts = commit_range_parts(review_range) if isinstance(review_range, str) else None
        if parts != (str(record.get("base_sha")).lower(), str(record.get("head_sha")).lower()):
            errors.append("BINDING_MISMATCH")
        if not review_approved_or_accepted(record, "implementation_review"):
            errors.append("implementation_review.status must be approved or have human risk acceptance")
        if record.get("verification") != "passed":
            errors.append(f"issues.{issue_id}.verification must be passed")
        if not isinstance(record.get("residual_risks"), list):
            errors.append(f"issues.{issue_id}.residual_risks must be a list")
        for field in OPTIONAL_PR_FIELDS:
            runtime_has = field in runtime_record
            result_has = field in record
            if runtime_has != result_has:
                errors.append("BINDING_MISMATCH")
                continue
            if not runtime_has:
                continue
            value = record[field]
            if field == "pr":
                if not isinstance(value, str) or not value.strip():
                    errors.append("SCHEMA_UNSUPPORTED")
            elif type(value) is not bool:
                errors.append("SCHEMA_UNSUPPORTED")
            if value != runtime_record[field]:
                errors.append("BINDING_MISMATCH")
    return errors
