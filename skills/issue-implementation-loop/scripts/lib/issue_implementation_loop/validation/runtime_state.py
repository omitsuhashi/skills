from __future__ import annotations

from typing import Any

from ..approved_spec_binding import BindingError, approved_spec_binding_ref
from ..constants import SUCCESS_STATUSES
from ..identifiers import commit_range_parts, is_full_commit_sha, is_lower_kebab
from ..review import review_approved_or_accepted


RUNTIME_FIELDS = {
    "schema_version",
    "epic_id",
    "envelope_revision",
    "approved_spec_binding",
    "issues",
    "human_requests",
    "rebuild",
}
ISSUE_FIELDS = {
    "status",
    "review",
    "signals",
    "branch",
    "worktree",
    "base_sha",
    "head_sha",
    "pr",
    "pr_opened",
    "pr_merged",
    "merge_commit",
}
HUMAN_REQUEST_FIELDS = {
    "schema_version",
    "approved_spec_binding",
    "id",
    "scope",
    "issue",
    "resource",
    "reason",
    "created_at",
}
RUNTIME_REQUIRED = {
    "schema_version",
    "epic_id",
    "envelope_revision",
    "approved_spec_binding",
    "issues",
    "human_requests",
}
HUMAN_REQUEST_REQUIRED = {
    "schema_version",
    "approved_spec_binding",
    "id",
    "scope",
    "reason",
}


def validate_runtime_state(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(state, dict) or state.get("schema_version") != 2:
        return ["SCHEMA_UNSUPPORTED"]
    if set(state) - RUNTIME_FIELDS or not RUNTIME_REQUIRED.issubset(state):
        return ["SCHEMA_UNSUPPORTED"]
    binding = state.get("approved_spec_binding")
    if not isinstance(binding, dict):
        return ["SCHEMA_UNSUPPORTED"]
    try:
        approved_spec_binding_ref(binding)
    except BindingError as error:
        return [error.code]
    epic_id = state.get("epic_id")
    if not isinstance(epic_id, str) or not is_lower_kebab(epic_id):
        errors.append("epic_id must be lower-kebab-case ASCII")
    if (
        type(state.get("envelope_revision")) is not int
        or state["envelope_revision"] < 1
    ):
        errors.append("SCHEMA_UNSUPPORTED")
    rebuild = state.get("rebuild")
    if rebuild is not None and (
        not isinstance(rebuild, dict)
        or set(rebuild) != {"events_applied", "duplicate_events_ignored"}
        or any(
            type(rebuild.get(field)) is not int or rebuild[field] < 0
            for field in rebuild
        )
    ):
        errors.append("SCHEMA_UNSUPPORTED")
    if not isinstance(state.get("issues", {}), dict):
        errors.append("issues must be an object")
    else:
        for issue_id, record in state.get("issues", {}).items():
            if not isinstance(record, dict):
                errors.append(f"issues.{issue_id} must be an object")
                continue
            if set(record) - ISSUE_FIELDS:
                errors.append("SCHEMA_UNSUPPORTED")
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
                range_parts = commit_range_parts(review_range) if isinstance(review_range, str) else None
                if range_parts is None:
                    errors.append(
                        f"issues.{issue_id}.review.range must use committed BASE_SHA..HEAD_SHA, not working-tree"
                    )
                    continue
                base_sha = record.get("base_sha")
                head_sha = record.get("head_sha")
                if not isinstance(base_sha, str) or not is_full_commit_sha(base_sha):
                    errors.append(f"issues.{issue_id}.base_sha must be a full commit SHA for success statuses")
                if not isinstance(head_sha, str) or not is_full_commit_sha(head_sha):
                    errors.append(f"issues.{issue_id}.head_sha must be a full commit SHA for success statuses")
                if (
                    isinstance(base_sha, str)
                    and isinstance(head_sha, str)
                    and is_full_commit_sha(base_sha)
                    and is_full_commit_sha(head_sha)
                    and (base_sha.lower(), head_sha.lower()) != (range_parts[0].lower(), range_parts[1].lower())
                ):
                    errors.append(f"issues.{issue_id}.review.range must match base_sha..head_sha")
                if not review_approved_or_accepted(record, "review"):
                    errors.append(
                        f"issues.{issue_id}.review.status must be approved or have human risk acceptance"
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
            if set(request) - HUMAN_REQUEST_FIELDS or not HUMAN_REQUEST_REQUIRED.issubset(
                request
            ):
                errors.append("SCHEMA_UNSUPPORTED")
                continue
            if request.get("schema_version") != 2 or not isinstance(
                request.get("approved_spec_binding"), dict
            ):
                errors.append("SCHEMA_UNSUPPORTED")
                continue
            try:
                approved_spec_binding_ref(request["approved_spec_binding"])
            except BindingError as error:
                errors.append(error.code)
                continue
            if request["approved_spec_binding"] != binding:
                errors.append("AUXILIARY_ARTIFACT_BINDING_MISMATCH")
                continue
            if not isinstance(request.get("id"), str) or not request["id"].strip():
                errors.append("SCHEMA_UNSUPPORTED")
                continue
            if not isinstance(request.get("reason"), str) or not request["reason"].strip():
                errors.append("SCHEMA_UNSUPPORTED")
                continue
            if request.get("scope") not in {"issue", "descendants", "resource", "epic"}:
                errors.append("SCHEMA_UNSUPPORTED")
    return errors


def validate_runtime_epoch(
    envelope: dict[str, Any], runtime: dict[str, Any]
) -> list[str]:
    if envelope.get("approved_spec_binding") != runtime.get("approved_spec_binding"):
        return ["BINDING_MISMATCH"]
    errors: list[str] = []
    if runtime.get("epic_id") != envelope.get("epic_id"):
        errors.append("runtime_state.epic_id must match envelope.epic_id")
    if runtime.get("envelope_revision") != envelope.get("revision"):
        errors.append("runtime_state.envelope_revision must match envelope.revision")
    return errors
