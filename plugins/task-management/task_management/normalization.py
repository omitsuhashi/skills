"""Fail-closed normalization for TaskBackendAdapter preflight and apply results."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any, Dict, Mapping, Optional

from .contracts import (
    ADAPTER_CONTRACT_VERSION,
    ContractValidationError,
    validate_task_preflight_result,
    validate_task_write_result,
)
from .preflight import build_preflight_result
from .safety import SafetyValidationError, validate_safe_value


MAX_ADAPTER_RESPONSE_BYTES = 5 * 1024 * 1024
MAX_EXPECTED_SIDE_EFFECTS = 20
MAX_EFFECT_TYPE_LENGTH = 64
MAX_EFFECT_DESCRIPTION_LENGTH = 500
_EFFECT_TYPE_RE = re.compile(r"^[a-z][a-z0-9_.-]*$")
_PREFLIGHT_FIELDS = {
    "adapter_contract_version",
    "ok",
    "operation_type",
    "backend_key",
    "destination_ref",
    "readiness",
    "expected_side_effects",
    "requires_human_confirmation",
    "error",
}
_WRITE_FIELDS = {
    "adapter_contract_version",
    "ok",
    "status",
    "operation_type",
    "backend_key",
    "destination_ref",
    "task_ref",
    "retryable",
    "human_action",
    "error",
}
_ERROR_FIELDS = {"error_type", "code", "message"}
_ERROR_OPTIONAL_FIELDS = {"stage"}
_ERROR_TYPES = {
    "adapter_unavailable": "setup_blocker",
    "tool_disabled": "setup_blocker",
    "auth_missing": "setup_blocker",
    "permission_failure": "setup_blocker",
    "destination_unresolved": "setup_blocker",
    "required_field_missing": "setup_blocker",
    "field_type_mismatch": "setup_blocker",
    "capability_mismatch": "setup_blocker",
    "read_route_missing": "setup_blocker",
    "read_route_not_found": "setup_blocker",
    "read_route_contract_mismatch": "setup_blocker",
    "invalid_read_route": "setup_blocker",
    "approval_required": "approval_failure",
    "approval_mismatch": "approval_failure",
    "timeout": "provider_failure",
    "rate_limited": "provider_failure",
    "partial_update_failure": "partial_failure",
    "adapter_contract_mismatch": "contract_failure",
    "invalid_adapter_result": "contract_failure",
    "invalid_task_operation": "contract_failure",
    "invalid_write_request": "contract_failure",
    "unsafe_delegation_exposure": "contract_failure",
}
_ERROR_MESSAGES = {
    "adapter_unavailable": "The configured task adapter is unavailable.",
    "tool_disabled": "The configured task adapter tool is disabled.",
    "auth_missing": "The configured task adapter is missing authentication.",
    "permission_failure": "The configured task destination is not permitted.",
    "destination_unresolved": "The configured task destination could not be resolved.",
    "required_field_missing": "The task destination is missing a required field.",
    "field_type_mismatch": "A task destination field has an incompatible type.",
    "capability_mismatch": "The configured task adapter lacks the required capability.",
    "read_route_missing": "Task route configuration is unavailable.",
    "read_route_not_found": "No task route matches the requested operation.",
    "read_route_contract_mismatch": "Task route contract version is unsupported.",
    "invalid_read_route": "Task route configuration is invalid.",
    "approval_required": "This task operation requires explicit human approval.",
    "approval_mismatch": "The approved operation no longer matches current preflight.",
    "timeout": "The task adapter timed out before confirming the write.",
    "rate_limited": "The task adapter is temporarily rate limited.",
    "partial_update_failure": "Task content was created but one or more fields were not updated.",
    "adapter_contract_mismatch": "Task adapter contract version is unsupported.",
    "invalid_adapter_result": "The task adapter returned an invalid result.",
    "invalid_task_operation": "The task operation is invalid.",
    "invalid_write_request": "The task write request is invalid.",
    "unsafe_delegation_exposure": "The task adapter exposed forbidden provider or credential data.",
}
_HUMAN_ACTIONS = {
    "Inspect the linked task before retrying field updates.",
    "Retry after the backend service becomes available.",
    "Review the new preflight preview before retrying.",
}


class NormalizationError(ValueError):
    """Internal adapter contract failure that never carries raw provider text."""

    def __init__(self, code: str = "invalid_adapter_result"):
        super().__init__(_ERROR_MESSAGES[code])
        self.code = code


def _parse_result(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, str):
        try:
            if len(raw.encode("utf-8")) > MAX_ADAPTER_RESPONSE_BYTES:
                raise NormalizationError()
            raw = json.loads(raw)
        except (UnicodeError, json.JSONDecodeError):
            raise NormalizationError()
    if not isinstance(raw, dict):
        raise NormalizationError()
    try:
        encoded = json.dumps(raw, ensure_ascii=False, separators=(",", ":"))
        if len(encoded.encode("utf-8")) > MAX_ADAPTER_RESPONSE_BYTES:
            raise NormalizationError()
    except (TypeError, ValueError, OverflowError, UnicodeError, RecursionError):
        raise NormalizationError()
    return deepcopy(raw)


def _require_exact_fields(
    value: Mapping[str, Any], required: set, optional: set = frozenset()
) -> None:
    keys = set(value)
    if keys - required - optional or required - keys:
        raise NormalizationError()


def _operation_identity(operation: Any) -> Dict[str, str]:
    if not isinstance(operation, dict):
        operation = {}
    operation_type = operation.get("operation_type")
    if operation_type not in {
        "task.create",
        "task.update",
        "task.comment",
        "task.report",
    }:
        operation_type = "task.create"
    backend_key = operation.get("backend_key")
    destination_ref = operation.get("destination_ref")
    for value_name, value in (
        ("backend_key", backend_key),
        ("destination_ref", destination_ref),
    ):
        try:
            validate_safe_value(value, path=f"$.{value_name}")
        except SafetyValidationError:
            if value_name == "backend_key":
                backend_key = "unresolved"
            else:
                destination_ref = "unresolved"
    if not isinstance(backend_key, str) or not backend_key.strip():
        backend_key = "unresolved"
    if not isinstance(destination_ref, str) or not destination_ref.strip():
        destination_ref = "unresolved"
    return {
        "operation_type": operation_type,
        "backend_key": backend_key,
        "destination_ref": destination_ref,
    }


def _typed_error(
    code: str,
    *,
    error_type: Optional[str] = None,
    stage: Optional[str] = None,
) -> Dict[str, Any]:
    resolved_type = error_type or _ERROR_TYPES.get(code)
    if resolved_type is None or code not in _ERROR_MESSAGES:
        code = "invalid_adapter_result"
        resolved_type = "contract_failure"
        stage = None
    error = {
        "error_type": resolved_type,
        "code": code,
        "message": _ERROR_MESSAGES[code],
    }
    if stage is not None:
        error["stage"] = stage
    return error


def preflight_failure_result(
    operation: Any,
    *,
    code: str,
    error_type: Optional[str] = None,
) -> Dict[str, Any]:
    identity = _operation_identity(operation)
    result = {
        "result_type": "TaskPreflightResult",
        "ok": False,
        "status": "blocked",
        **identity,
        "approval_mode": None,
        "approval_preview": None,
        "approval_digest": None,
        "readiness": {"ok": False, "checks": []},
        "error": _typed_error(code, error_type=error_type),
    }
    return validate_task_preflight_result(result)


def write_failure_result(
    operation: Any,
    *,
    code: str,
    error_type: Optional[str] = None,
    status: Optional[str] = None,
    retryable: bool = False,
    task_ref: Any = None,
    stage: Optional[str] = None,
) -> Dict[str, Any]:
    identity = _operation_identity(operation)
    resolved_type = error_type or _ERROR_TYPES.get(code, "contract_failure")
    if status is None:
        status = "blocked" if resolved_type in {"setup_blocker", "approval_failure"} else "failed"
    action = None
    if code == "partial_update_failure":
        action = "Inspect the linked task before retrying field updates."
    elif code in {"timeout", "rate_limited"}:
        action = "Retry after the backend service becomes available."
    elif code == "approval_mismatch":
        action = "Review the new preflight preview before retrying."
    result = {
        "result_type": "TaskWriteResult",
        "ok": False,
        "status": status,
        **identity,
        "task_ref": deepcopy(task_ref),
        "retryable": retryable,
        "human_action": action,
        "error": _typed_error(code, error_type=resolved_type, stage=stage),
    }
    return validate_task_write_result(result)


def _normalize_error(error: Any) -> Dict[str, Any]:
    if not isinstance(error, dict):
        raise NormalizationError()
    _require_exact_fields(error, _ERROR_FIELDS, _ERROR_OPTIONAL_FIELDS)
    code = error.get("code")
    error_type = error.get("error_type")
    if (
        not isinstance(code, str)
        or _ERROR_TYPES.get(code) != error_type
        or not isinstance(error.get("message"), str)
        or not error["message"].strip()
    ):
        raise NormalizationError()
    stage = error.get("stage")
    if stage is not None and (not isinstance(stage, str) or not stage.strip()):
        raise NormalizationError()
    return _typed_error(code, error_type=error_type, stage=stage)


def _validate_expected_side_effects(effects: Any) -> None:
    if (
        not isinstance(effects, list)
        or not effects
        or len(effects) > MAX_EXPECTED_SIDE_EFFECTS
    ):
        raise NormalizationError()
    for effect in effects:
        if not isinstance(effect, dict):
            raise NormalizationError()
        _require_exact_fields(effect, {"effect_type", "description"})
        effect_type = effect.get("effect_type")
        description = effect.get("description")
        if (
            not isinstance(effect_type, str)
            or not effect_type
            or len(effect_type) > MAX_EFFECT_TYPE_LENGTH
            or _EFFECT_TYPE_RE.fullmatch(effect_type) is None
            or not isinstance(description, str)
            or not description.strip()
            or len(description) > MAX_EFFECT_DESCRIPTION_LENGTH
        ):
            raise NormalizationError()


def normalize_preflight_result(
    raw_result: Any,
    *,
    operation: Any,
    destination: Any,
    route_binding: Any,
) -> Dict[str, Any]:
    """Normalize one exact Adapter preflight response into TaskPreflightResult."""
    try:
        raw = _parse_result(raw_result)
        validate_safe_value(raw)
        _require_exact_fields(raw, _PREFLIGHT_FIELDS)
        if type(raw["adapter_contract_version"]) is not int or raw["adapter_contract_version"] != ADAPTER_CONTRACT_VERSION:
            raise NormalizationError("adapter_contract_mismatch")
        if type(raw["ok"]) is not bool or type(raw["requires_human_confirmation"]) is not bool:
            raise NormalizationError()
        identity = _operation_identity(operation)
        if any(raw.get(field) != identity[field] for field in identity):
            raise NormalizationError()
        readiness = raw.get("readiness")
        if not isinstance(readiness, dict):
            raise NormalizationError()
        _require_exact_fields(readiness, {"ok", "checks"})
        if type(readiness.get("ok")) is not bool or not isinstance(readiness.get("checks"), list):
            raise NormalizationError()
        effects = raw.get("expected_side_effects")
        if not isinstance(effects, list):
            raise NormalizationError()
        if raw["ok"]:
            if readiness["ok"] is not True or raw["error"] is not None or not effects:
                raise NormalizationError()
            _validate_expected_side_effects(effects)
            return build_preflight_result(
                operation,
                destination,
                route_binding,
                effects,
                readiness=readiness,
                adapter_uncertainty=raw["requires_human_confirmation"],
                error=None,
            )
        if (
            readiness["ok"] is not False
            or effects
            or raw["requires_human_confirmation"]
        ):
            raise NormalizationError()
        return build_preflight_result(
            operation,
            destination,
            route_binding,
            [],
            readiness=readiness,
            adapter_uncertainty=False,
            error=_normalize_error(raw["error"]),
        )
    except SafetyValidationError:
        return preflight_failure_result(
            operation,
            code="unsafe_delegation_exposure",
            error_type="contract_failure",
        )
    except (NormalizationError, ContractValidationError, TypeError, ValueError) as error:
        code = error.code if isinstance(error, NormalizationError) else "invalid_adapter_result"
        return preflight_failure_result(operation, code=code, error_type="contract_failure")


def normalize_write_result(raw_result: Any, *, operation: Any) -> Dict[str, Any]:
    """Normalize one exact Adapter apply response into safe TaskWriteResult."""
    try:
        raw = _parse_result(raw_result)
        validate_safe_value(raw)
        _require_exact_fields(raw, _WRITE_FIELDS)
        if type(raw["adapter_contract_version"]) is not int or raw["adapter_contract_version"] != ADAPTER_CONTRACT_VERSION:
            raise NormalizationError("adapter_contract_mismatch")
        identity = _operation_identity(operation)
        if any(raw.get(field) != identity[field] for field in identity):
            raise NormalizationError()
        if raw.get("human_action") not in _HUMAN_ACTIONS | {None}:
            raise NormalizationError()
        public = {key: deepcopy(value) for key, value in raw.items() if key != "adapter_contract_version"}
        public["result_type"] = "TaskWriteResult"
        if public.get("error") is not None:
            public["error"] = _normalize_error(public["error"])
        return validate_task_write_result(public)
    except SafetyValidationError:
        return write_failure_result(
            operation,
            code="unsafe_delegation_exposure",
            error_type="contract_failure",
        )
    except (NormalizationError, ContractValidationError, TypeError, ValueError) as error:
        code = error.code if isinstance(error, NormalizationError) else "invalid_adapter_result"
        return write_failure_result(operation, code=code, error_type="contract_failure")
