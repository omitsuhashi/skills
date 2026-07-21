from __future__ import annotations

import os
from typing import Any

from ..approved_spec_binding import BindingError, approved_spec_binding_ref
from ..constants import SUCCESS_STATUSES
from ..identifiers import commit_range_parts, is_full_commit_sha, is_issue_id, is_lower_kebab
from ..review import review_approved_or_accepted
from .execution_envelope import validate_execution_envelope
from .runtime_state import validate_runtime_epoch, validate_runtime_state
from .worker_packet import validate_worker_packet


REPORT_FIELDS = {
    "approved_spec_binding",
    "base_sha",
    "branch",
    "changed_files",
    "dispatch_id",
    "epic_id",
    "head_sha",
    "implementation_review",
    "issue_id",
    "residual_risks",
    "schema_version",
    "status",
    "verification",
    "worktree",
}


def validate_worker_report(
    report: dict[str, Any],
    dispatch_packet: dict[str, Any] | None = None,
    runtime_state: dict[str, Any] | None = None,
    envelope: dict[str, Any] | None = None,
    repo_root: str | os.PathLike[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(envelope, dict) or repo_root is None:
        return ["BINDING_MISMATCH"]
    envelope_errors = validate_execution_envelope(envelope, repo_root)
    if envelope_errors:
        return envelope_errors
    if not isinstance(runtime_state, dict):
        return ["BINDING_MISMATCH"]
    runtime_errors = validate_runtime_state(runtime_state)
    if runtime_errors:
        return runtime_errors
    epoch_errors = validate_runtime_epoch(envelope, runtime_state)
    if epoch_errors:
        return epoch_errors
    if not isinstance(dispatch_packet, dict):
        return ["BINDING_MISMATCH"]
    packet_errors = validate_worker_packet(dispatch_packet)
    if packet_errors:
        return packet_errors
    if report.get("schema_version") != 2:
        return ["SCHEMA_UNSUPPORTED"]
    for field in sorted(report):
        if field not in REPORT_FIELDS:
            errors.append(f"unknown field: {field}")
    try:
        binding = approved_spec_binding_ref(
            report.get("approved_spec_binding")
        ).to_dict()
    except BindingError as error:
        return [error.code]
    dispatch_id = report.get("dispatch_id")
    if not isinstance(dispatch_id, str) or not dispatch_id.strip():
        errors.append("dispatch_id is required")
    if isinstance(dispatch_packet, dict):
        dispatch_binding = (
            dispatch_packet.get("source_revision", {}).get("approved_spec_binding")
            if isinstance(dispatch_packet.get("source_revision"), dict)
            else None
        )
        runtime_binding = runtime_state.get("approved_spec_binding")
        identity_fields = ("dispatch_id", "epic_id", "issue_id", "branch", "worktree")
        if (
            dispatch_binding != binding
            or runtime_binding != binding
            or envelope.get("approved_spec_binding") != binding
            or any(report.get(field) != dispatch_packet.get(field) for field in identity_fields)
        ):
            return ["BINDING_MISMATCH"]
    epic_id = report.get("epic_id")
    if not isinstance(epic_id, str) or not is_lower_kebab(epic_id):
        errors.append("epic_id must be lower-kebab-case ASCII")
    issue_id = report.get("issue_id")
    if not isinstance(issue_id, str) or not is_issue_id(issue_id):
        errors.append("issue_id must look like G2PR-001")
    branch = report.get("branch")
    if not isinstance(branch, str) or not branch:
        errors.append("branch is required")
    worktree = report.get("worktree")
    if not isinstance(worktree, str) or not os.path.isabs(worktree):
        errors.append("worktree must be an absolute path")
    if not isinstance(report.get("changed_files"), list):
        errors.append("changed_files must be a list")
    if not isinstance(report.get("verification"), list):
        errors.append("verification must be a list")
    residual_risks = report.get("residual_risks")
    if not isinstance(residual_risks, list):
        errors.append("residual_risks must be a list")
    else:
        for index, risk in enumerate(residual_risks):
            if not isinstance(risk, str) or not risk.strip():
                errors.append(
                    f"residual_risks[{index}] must be a non-empty string"
                )

    status = report.get("status")
    if not isinstance(status, str) or not status:
        errors.append("status is required")
    if status in SUCCESS_STATUSES:
        base_sha = report.get("base_sha")
        head_sha = report.get("head_sha")
        if not isinstance(base_sha, str) or not is_full_commit_sha(base_sha):
            errors.append("base_sha must be a full commit SHA for success statuses")
        if not isinstance(head_sha, str) or not is_full_commit_sha(head_sha):
            errors.append("head_sha must be a full commit SHA for success statuses")
        review = report.get("implementation_review")
        if not isinstance(review, dict):
            errors.append("implementation_review.range must use committed BASE_SHA..HEAD_SHA")
            return errors
        review_range = review.get("range") or review.get("review_range")
        range_parts = commit_range_parts(review_range) if isinstance(review_range, str) else None
        if range_parts is None:
            errors.append("implementation_review.range must use committed BASE_SHA..HEAD_SHA, not working-tree")
            return errors
        if (
            isinstance(base_sha, str)
            and isinstance(head_sha, str)
            and is_full_commit_sha(base_sha)
            and is_full_commit_sha(head_sha)
            and (base_sha.lower(), head_sha.lower()) != (range_parts[0].lower(), range_parts[1].lower())
        ):
            errors.append("implementation_review.range must match base_sha..head_sha")
        if not review_approved_or_accepted(report, "implementation_review"):
            errors.append("implementation_review.status must be approved or have human risk acceptance")
    return errors
