from __future__ import annotations

import os
from typing import Any

from ..constants import SUCCESS_STATUSES
from ..identifiers import commit_range_parts, is_full_commit_sha, is_issue_id, is_lower_kebab
from ..review import review_approved_or_accepted


def validate_worker_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
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
