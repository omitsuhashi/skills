from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .approved_spec_binding import BindingError, approved_spec_binding_ref
from .constants import FINAL_PR_REQUIRED_APPROVED_ACTIONS
from .identifiers import is_issue_id
from .repository_integrity import validate_final_head_integrity
from .review import review_approved_or_accepted
from .validation.execution_envelope import validate_execution_envelope
from .validation.execution_result import validate_execution_result
from .validation.runtime_state import validate_runtime_state


RESIDUAL_RISK_DECISIONS = {"deferred_follow_up", "declined", "risk_accepted"}
SAFETY_ESCALATION_RESOLUTION_DECISIONS = {"risk_accepted", "implemented"}
READY_IMPLEMENTATION_STATUSES = {"PR_READY"}
REGISTRY_FIELDS = {
    "schema_version",
    "approved_spec_binding",
    "epic_id",
    "registry_path",
    "limits",
    "candidates",
}
REGISTRY_LIMITS = {
    "hardening_candidate_summary_words_default": 80,
    "hardening_candidates_per_issue_default": 5,
}
CANDIDATE_REQUIRED_FIELDS = {
    "candidate_id",
    "source_issue",
    "classification",
    "summary",
    "risk",
    "estimated_scope",
    "decision",
    "implementation_issue",
}
CANDIDATE_FIELDS = CANDIDATE_REQUIRED_FIELDS | {
    "delivery_blocker",
    "recommended_decision",
    "decision_reason",
    "decided_by",
    "decided_at",
}
CANDIDATE_CLASSIFICATIONS = {
    "hardening_candidate",
    "safety_escalation",
    "classification_needed",
}
CANDIDATE_DECISIONS = {
    "pending_decision",
    "approved_for_current_pr",
    "deferred_follow_up",
    "declined",
    "risk_accepted",
    "implemented",
}
DELIVERY_PLAN_COMMON_FIELDS = {
    "schema_version",
    "approved_spec_binding",
    "action",
    "head",
    "base",
}
ISSUE_PR_PLAN_FIELDS = DELIVERY_PLAN_COMMON_FIELDS | {"issue"}
FINAL_PR_PLAN_FIELDS = DELIVERY_PLAN_COMMON_FIELDS | {"draft", "issue_scope"}
FINAL_PR_PLAN_FIELDS_SHORTHAND = DELIVERY_PLAN_COMMON_FIELDS | {"draft"}
RECOMMENDED_DECISIONS = {
    "approved_for_current_pr",
    "deferred_follow_up",
    "declined",
    "risk_accepted",
}


def hardening_candidate_registry_path(runtime_state_path: str | Path) -> Path:
    return Path(runtime_state_path).parent / "decisions" / "hardening-candidates.json"


def load_hardening_candidate_registry(
    runtime_state_path: str | Path,
) -> tuple[dict[str, Any] | None, str, str | None]:
    registry_path = hardening_candidate_registry_path(runtime_state_path)
    if not registry_path.exists():
        return None, str(registry_path), None
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, str(registry_path), f"{registry_path.name}: invalid JSON: {exc}"
    if not isinstance(registry, dict):
        return None, str(registry_path), f"{registry_path.name}: registry must be an object"
    return registry, str(registry_path), None


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


def delivery_issue_scope(
    envelope: dict[str, Any],
    execution_result: dict[str, Any],
    plan: dict[str, Any],
    errors: list[str],
) -> list[str]:
    work_items = envelope.get("work_items", {})
    if not isinstance(work_items, dict):
        errors.append("work_items must be a non-empty object")
        return []
    candidates = execution_result.get("delivery_candidates")
    if not isinstance(candidates, list):
        errors.append("delivery_candidates must be a list")
        return []
    scope = plan.get("issue_scope")
    if scope is None:
        return candidates
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
    if len(issues) != len(set(issues)) or set(issues) != set(candidates):
        errors.append("final_pr.issue_scope must exactly match delivery_candidates")
    return issues


def _candidate_id(candidate: Any, index: int) -> str:
    if isinstance(candidate, dict) and isinstance(candidate.get("candidate_id"), str):
        return candidate["candidate_id"]
    return f"candidates[{index}]"


def _valid_optional_string_or_null(value: Any) -> bool:
    return value is None or isinstance(value, str)


def _candidate_registry_is_closed(registry: dict[str, Any]) -> bool:
    if set(registry) != REGISTRY_FIELDS:
        return False
    if registry.get("schema_version") != 2:
        return False
    if not isinstance(registry.get("epic_id"), str) or not registry["epic_id"]:
        return False
    if (
        not isinstance(registry.get("registry_path"), str)
        or not registry["registry_path"]
    ):
        return False
    if registry.get("limits") != REGISTRY_LIMITS:
        return False
    candidates = registry.get("candidates")
    if not isinstance(candidates, list):
        return False

    source_counts: dict[str, int] = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            return False
        if set(candidate) - CANDIDATE_FIELDS or not CANDIDATE_REQUIRED_FIELDS.issubset(
            candidate
        ):
            return False
        for field in ("candidate_id", "source_issue", "summary", "risk"):
            if not isinstance(candidate.get(field), str) or not candidate[field]:
                return False
        if candidate.get("classification") not in CANDIDATE_CLASSIFICATIONS:
            return False
        if candidate.get("decision") not in CANDIDATE_DECISIONS:
            return False
        estimated_scope = candidate.get("estimated_scope")
        if not isinstance(estimated_scope, list) or any(
            not isinstance(scope, str) for scope in estimated_scope
        ):
            return False
        implementation_issue = candidate.get("implementation_issue")
        if not _valid_optional_string_or_null(implementation_issue):
            return False
        if "delivery_blocker" in candidate and not isinstance(
            candidate["delivery_blocker"], bool
        ):
            return False
        if (
            "recommended_decision" in candidate
            and candidate["recommended_decision"] not in RECOMMENDED_DECISIONS
        ):
            return False
        for field in ("decision_reason", "decided_by", "decided_at"):
            if field in candidate and not _valid_optional_string_or_null(
                candidate[field]
            ):
                return False

        source_issue = candidate["source_issue"]
        source_counts[source_issue] = source_counts.get(source_issue, 0) + 1
        if (
            source_counts[source_issue]
            > REGISTRY_LIMITS["hardening_candidates_per_issue_default"]
        ):
            return False
        if len(candidate["summary"].split()) > REGISTRY_LIMITS[
            "hardening_candidate_summary_words_default"
        ]:
            return False
    return True


def _candidate_completion_summary(candidate: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "candidate_id": _candidate_id(candidate, index),
        "source_issue": candidate.get("source_issue"),
        "classification": candidate.get("classification"),
        "decision": candidate.get("decision"),
        "implementation_issue": candidate.get("implementation_issue"),
        "summary": candidate.get("summary"),
        "risk": candidate.get("risk"),
    }


def _append_candidate_summary_once(
    report: dict[str, list[Any]],
    field: str,
    summary: dict[str, Any],
) -> None:
    candidate_id = summary.get("candidate_id")
    if any(existing.get("candidate_id") == candidate_id for existing in report[field] if isinstance(existing, dict)):
        return
    report[field].append(summary)


def _implementation_issue_ready(runtime: dict[str, Any], implementation_issue: Any) -> bool:
    if not isinstance(implementation_issue, str) or not implementation_issue:
        return False
    issues = runtime.get("issues", {})
    if not isinstance(issues, dict):
        return False
    record = issues.get(implementation_issue)
    if not isinstance(record, dict):
        return False
    if record.get("status") in READY_IMPLEMENTATION_STATUSES:
        return True
    if record.get("pr_merged") is True:
        return True
    signals = record.get("signals", [])
    if isinstance(signals, list) and "integrated" in signals:
        return True
    return review_approved_or_accepted(record, "review")


def hardening_candidate_report(
    runtime: dict[str, Any],
    candidate_registry: dict[str, Any] | None,
    *,
    candidate_registry_path: str = "hardening-candidates.json",
    candidate_registry_load_error: str | None = None,
) -> dict[str, list[Any]]:
    report: dict[str, list[Any]] = {
        "errors": [],
        "pending_hardening_candidates": [],
        "residual_risks": [],
        "decision_gate_blockers": [],
    }
    registry_label = Path(candidate_registry_path).name
    if candidate_registry_load_error:
        report["errors"].append(candidate_registry_load_error)
        return report
    if candidate_registry is None:
        return report
    if not _candidate_registry_is_closed(candidate_registry):
        report["errors"].append("SCHEMA_UNSUPPORTED")
        return report
    registry_binding = candidate_registry.get("approved_spec_binding")
    if not isinstance(registry_binding, dict):
        report["errors"].append("SCHEMA_UNSUPPORTED")
        return report
    try:
        approved_spec_binding_ref(registry_binding)
    except BindingError as error:
        report["errors"].append(error.code)
        return report
    if registry_binding != runtime.get("approved_spec_binding"):
        report["errors"].append("AUXILIARY_ARTIFACT_BINDING_MISMATCH")
        return report
    if candidate_registry.get("epic_id") != runtime.get("epic_id"):
        report["errors"].append(f"{registry_label}: epic_id must match runtime_state.epic_id")
    candidates = candidate_registry.get("candidates")
    if not isinstance(candidates, list):
        report["errors"].append(f"{registry_label}: candidates must be a list")
        return report

    for index, candidate in enumerate(candidates):
        candidate_label = _candidate_id(candidate, index)
        if not isinstance(candidate, dict):
            report["errors"].append(f"{registry_label}: candidates[{index}] must be an object")
            continue
        summary = _candidate_completion_summary(candidate, index)
        classification = candidate.get("classification")
        decision = candidate.get("decision")

        if decision == "pending_decision":
            _append_candidate_summary_once(report, "pending_hardening_candidates", summary)
            report["decision_gate_blockers"].append(
                f"{registry_label}: {candidate_label} has pending_decision; "
                "ready-for-review, merge, or candidate implementation requires a human decision"
            )
            continue

        implementation_ready = False
        if decision == "approved_for_current_pr":
            implementation_issue = candidate.get("implementation_issue")
            implementation_ready = _implementation_issue_ready(runtime, implementation_issue)
            if not implementation_ready:
                _append_candidate_summary_once(report, "pending_hardening_candidates", summary)
                report["decision_gate_blockers"].append(
                    f"{registry_label}: {candidate_label} approved_for_current_pr requires "
                    f"implementation_issue {implementation_issue} to be PR_READY, integrated, "
                    "or review approved before ready-for-review or merge"
                )

        if classification == "safety_escalation":
            safety_resolved = (
                decision in SAFETY_ESCALATION_RESOLUTION_DECISIONS
                or (decision == "approved_for_current_pr" and implementation_ready)
            )
            if not safety_resolved:
                _append_candidate_summary_once(report, "pending_hardening_candidates", summary)
                report["decision_gate_blockers"].append(
                    f"{registry_label}: {candidate_label} has unresolved safety_escalation; "
                    "risk acceptance or implemented approved scope is required before ready-for-review or merge"
                )

        if decision in RESIDUAL_RISK_DECISIONS:
            report["residual_risks"].append(summary)
    return report


def validate_delivery_plan(
    envelope: dict[str, Any],
    runtime: dict[str, Any],
    execution_result: dict[str, Any],
    plan: dict[str, Any],
    *,
    repo_root: str | Path,
    candidate_registry: dict[str, Any] | None = None,
    candidate_registry_path: str = "hardening-candidates.json",
    candidate_registry_load_error: str | None = None,
) -> list[str]:
    errors = validate_execution_result(
        envelope,
        runtime,
        execution_result,
        repo_root=repo_root,
        candidate_registry=candidate_registry,
        candidate_registry_path=candidate_registry_path,
        candidate_registry_load_error=candidate_registry_load_error,
    )
    if errors:
        return errors

    if not isinstance(plan, dict) or plan.get("schema_version") != 2:
        return ["SCHEMA_UNSUPPORTED"]
    try:
        plan_binding = approved_spec_binding_ref(
            plan.get("approved_spec_binding")
        ).to_dict()
    except BindingError as error:
        return [error.code]
    if plan_binding != envelope.get("approved_spec_binding"):
        return ["BINDING_MISMATCH"]
    action = plan.get("action")
    if action not in {"issue_pr", "final_pr"}:
        errors.append("action must be issue_pr or final_pr")
        return errors
    expected_field_sets = (
        (ISSUE_PR_PLAN_FIELDS,)
        if action == "issue_pr"
        else (FINAL_PR_PLAN_FIELDS, FINAL_PR_PLAN_FIELDS_SHORTHAND)
    )
    if all(set(plan) != expected_fields for expected_fields in expected_field_sets):
        if action == "final_pr" and "ready_for_review" in plan:
            return ["ready-for-review is a separate human action"]
        return ["SCHEMA_UNSUPPORTED"]

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
    approved_actions = remote_policy.get("approved_actions", [])
    if not isinstance(approved_actions, list):
        errors.append("remote_write_policy.approved_actions must be a list")
        approved_actions = []
    approved_action_set = {action for action in approved_actions if isinstance(action, str)}
    for action in sorted(FINAL_PR_REQUIRED_APPROVED_ACTIONS - approved_action_set):
        errors.append(f"remote_write_policy.approved_actions must include {action}")
    if plan.get("draft", True) is not True:
        errors.append("final_pr.draft must be true; ready-for-review is a separate human action")

    if not errors:
        errors.extend(
            validate_final_head_integrity(
                envelope,
                runtime,
                execution_result,
                head,
                repo_root,
            )
        )
    delivery_issue_scope(envelope, execution_result, plan, errors)
    runtime_issues = runtime.get("issues", {})
    if isinstance(runtime_issues, dict):
        for issue_id in execution_result.get("delivery_candidates", []):
            record = runtime_issues.get(issue_id)
            if not isinstance(record, dict) or record.get("pr_merged") is not True:
                errors.append(f"issues.{issue_id}.pr_merged must be true before final PR")
    errors.extend(
        hardening_candidate_report(
            runtime,
            candidate_registry,
            candidate_registry_path=candidate_registry_path,
            candidate_registry_load_error=candidate_registry_load_error,
        )["errors"]
    )
    return errors
