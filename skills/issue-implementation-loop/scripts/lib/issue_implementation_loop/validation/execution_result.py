from __future__ import annotations

import os
import subprocess
from pathlib import Path
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


def _resolve_git_branch(repo_root: str | os.PathLike[str], branch: Any) -> str | None:
    if not isinstance(branch, str) or not branch.strip():
        return None
    branch_ref = branch if branch.startswith("refs/heads/") else f"refs/heads/{branch}"
    try:
        resolved = subprocess.run(
            [
                "git",
                "-C",
                str(Path(repo_root).resolve(strict=False)),
                "show-ref",
                "--verify",
                "--hash",
                branch_ref,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if resolved.returncode != 0:
        return None
    sha = resolved.stdout.strip().lower()
    return sha if is_full_commit_sha(sha) else None


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

    candidate_report = hardening_candidate_report(
        runtime,
        candidate_registry,
        candidate_registry_path=candidate_registry_path,
        candidate_registry_load_error=candidate_registry_load_error,
    )
    registry_errors = candidate_report["errors"]
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
        resolved_epic_sha = _resolve_git_branch(repo_root, envelope_epic_base.get("ref"))
        if (
            resolved_epic_sha is None
            or epic_base.get("branch_exists") is not True
            or epic_base.get("current_sha") != resolved_epic_sha
        ):
            errors.append("BINDING_MISMATCH")

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
        residual_risks = record.get("residual_risks")
        if not isinstance(residual_risks, list):
            errors.append(f"issues.{issue_id}.residual_risks must be a list")
        elif (
            any(not isinstance(risk, str) or not risk.strip() for risk in residual_risks)
            or len(residual_risks) != len(set(residual_risks))
        ):
            errors.append(
                f"issues.{issue_id}.residual_risks must contain unique non-empty strings"
            )
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
    for candidate in candidate_report["residual_risks"]:
        if not isinstance(candidate, dict):
            errors.append("BINDING_MISMATCH")
            continue
        source_issue = candidate.get("source_issue")
        required_risk = candidate.get("risk")
        source_record = result_issues.get(source_issue)
        recorded_risks = (
            source_record.get("residual_risks")
            if isinstance(source_record, dict)
            else None
        )
        if (
            not isinstance(required_risk, str)
            or not required_risk.strip()
            or not isinstance(recorded_risks, list)
            or required_risk not in recorded_risks
        ):
            errors.append("BINDING_MISMATCH")
    return errors
