"""Confidence-aware approval policy kept separate from adapter readiness."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from .approval import approval_digest
from .contracts import validate_operation_envelope, validate_task_preflight_result


class PreflightPolicyError(ValueError):
    """Readiness or confidence-policy failure with a stable code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _approval_signals(operation: Dict[str, Any]) -> Dict[str, Any]:
    operation_type = operation["operation_type"]
    if operation_type == "task.create":
        return operation["payload"]["task"]
    if operation_type == "task.update":
        return operation["payload"]["changes"]
    return {}


def approval_mode_for_operation(
    operation: Any,
    *,
    preflight_passed: bool,
    adapter_uncertainty: bool,
) -> str:
    """Classify a validated ready operation without inferring semantic certainty."""
    validated = validate_operation_envelope(operation)
    signals = _approval_signals(validated)
    fields = signals.get("fields", {})
    review_notes = fields.get("review_notes", []) if isinstance(fields, dict) else []

    if type(preflight_passed) is not bool or not preflight_passed:
        raise PreflightPolicyError(
            "preflight_not_ready",
            "Approval policy cannot authorize a failed or missing preflight.",
        )
    if type(adapter_uncertainty) is not bool:
        raise PreflightPolicyError(
            "invalid_adapter_uncertainty",
            "Adapter uncertainty must be an explicit boolean.",
        )
    if (
        signals.get("approval_required") is True
        or bool(review_notes)
        or adapter_uncertainty
    ):
        return "human_required"
    return "confidence_eligible"


def build_preflight_result(
    operation: Any,
    destination: Any,
    route_binding: Any,
    expected_side_effects: Any,
    *,
    readiness: Any,
    adapter_uncertainty: bool,
    error: Any,
) -> Dict[str, Any]:
    """Build a contract-valid result while keeping blocked state approval-free."""
    validated_operation = validate_operation_envelope(operation)
    if not isinstance(readiness, dict):
        raise PreflightPolicyError(
            "invalid_readiness",
            "Adapter readiness must be an explicit object.",
        )
    if readiness.get("ok") is False:
        result = {
            "result_type": "TaskPreflightResult",
            "ok": False,
            "status": "blocked",
            "operation_type": validated_operation["operation_type"],
            "backend_key": validated_operation["backend_key"],
            "destination_ref": validated_operation["destination_ref"],
            "approval_mode": None,
            "approval_preview": None,
            "approval_digest": None,
            "readiness": readiness,
            "error": error,
        }
        return validate_task_preflight_result(result)

    preview = {
        "preview_version": 1,
        "operation": validated_operation,
        "destination": deepcopy(destination),
        "route_binding": deepcopy(route_binding),
        "expected_side_effects": deepcopy(expected_side_effects),
    }
    mode = approval_mode_for_operation(
        validated_operation,
        preflight_passed=True,
        adapter_uncertainty=adapter_uncertainty,
    )
    result = {
        "result_type": "TaskPreflightResult",
        "ok": True,
        "status": "ready",
        "operation_type": validated_operation["operation_type"],
        "backend_key": validated_operation["backend_key"],
        "destination_ref": validated_operation["destination_ref"],
        "approval_mode": mode,
        "approval_preview": preview,
        "approval_digest": approval_digest(preview),
        "readiness": readiness,
        "error": error,
    }
    return validate_task_preflight_result(result)
