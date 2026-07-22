"""Executable backend-neutral task preflight and approval-bound apply facade."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from .approval import ApprovalBindingError, authorize_apply, canonical_digest
from .contracts import (
    ADAPTER_CONTRACT_VERSION,
    ContractValidationError,
    validate_approval_preview,
    validate_approval_receipt,
    validate_operation_envelope,
)
from .normalization import (
    normalize_preflight_result,
    normalize_write_result,
    preflight_failure_result,
    write_failure_result,
)
from .route_config import (
    ROUTES_FILE_ENV,
    ROUTE_CONTRACT_VERSION,
    ResolvedTaskReadRoute,
    RouteConfigError,
    load_read_route,
)


WRITE_TOOLSET = "task-management-write"
PREFLIGHT_TOOL_NAME = "task_preflight"
APPLY_TOOL_NAME = "task_apply"
INTERFACE_VERSION = 2

_OPERATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "adapter_contract_version": {"type": "integer", "enum": [2]},
        "operation_type": {
            "type": "string",
            "enum": ["task.create", "task.update", "task.comment", "task.report"],
        },
        "backend_key": {"type": "string"},
        "destination_ref": {"type": "string"},
        "task_ref": {"type": ["object", "null"]},
        "payload": {"type": "object"},
    },
    "required": [
        "adapter_contract_version",
        "operation_type",
        "backend_key",
        "destination_ref",
        "task_ref",
        "payload",
    ],
}

TASK_PREFLIGHT_SCHEMA = {
    "name": PREFLIGHT_TOOL_NAME,
    "description": (
        "Validate one backend-neutral task operation and return an approval preview. "
        "This tool never mutates a task."
    ),
    "parameters": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "interface_version": {"type": "integer", "enum": [2]},
            "operation": _OPERATION_SCHEMA,
        },
        "required": ["interface_version", "operation"],
    },
}

TASK_APPLY_SCHEMA = {
    "name": APPLY_TOOL_NAME,
    "description": (
        "Re-preflight and apply one exact approved task operation. The approval "
        "preview and receipt must match current routing and side effects."
    ),
    "parameters": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "interface_version": {"type": "integer", "enum": [2]},
            "approval_preview": {"type": "object"},
            "approval_receipt": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "receipt_version": {"type": "integer", "enum": [1]},
                    "decision": {
                        "type": "string",
                        "enum": ["approved", "confidence_authorized"],
                    },
                    "operation_digest": {"type": "string"},
                },
                "required": ["receipt_version", "decision", "operation_digest"],
            },
        },
        "required": ["interface_version", "approval_preview", "approval_receipt"],
    },
}


def _is_interface_v2(arguments: Any, expected_fields: set) -> bool:
    return (
        isinstance(arguments, dict)
        and set(arguments) == expected_fields
        and type(arguments.get("interface_version")) is int
        and arguments["interface_version"] == INTERFACE_VERSION
    )


def _destination(route: ResolvedTaskReadRoute) -> Dict[str, Any]:
    return {
        "backend_key": route.backend_key,
        "destination_ref": route.destination_ref,
        "destination_label": route.destination_label,
        "content_target_ref": route.content_target_ref,
    }


def _route_binding(route: ResolvedTaskReadRoute) -> Dict[str, str]:
    binding_digest = canonical_digest(
        {
            "route_contract_version": ROUTE_CONTRACT_VERSION,
            "backend_key": route.backend_key,
            "adapter_key": route.adapter_key,
            "query_tool": route.query_tool,
            "preflight_tool": route.preflight_tool,
            "apply_tool": route.apply_tool,
        }
    )
    return {
        "adapter_key": route.adapter_key,
        "binding_digest": binding_digest,
    }


def _resolve_write_route(
    operation: Dict[str, Any], routes_file: Optional[str]
) -> Tuple[ResolvedTaskReadRoute, Dict[str, Any]]:
    if not routes_file:
        raise RouteConfigError(
            "read_route_missing",
            "Task route configuration is unavailable.",
        )
    route = load_read_route(
        Path(routes_file),
        operation["backend_key"],
        operation["destination_ref"],
    )
    if route.kind == "local_json":
        raise RouteConfigError(
            "capability_mismatch",
            "Local task fixtures do not provide a write capability.",
        )
    return route, _destination(route)


def _adapter_preflight_arguments(
    operation: Dict[str, Any], destination: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
        "operation": deepcopy(operation),
        "destination": deepcopy(destination),
        "required_capability": operation["operation_type"],
    }


def _dispatch_preflight(
    route: ResolvedTaskReadRoute,
    operation: Dict[str, Any],
    destination: Dict[str, Any],
    *,
    dispatch: Callable[..., Any],
    dispatch_kwargs: Dict[str, Any],
) -> Dict[str, Any]:
    try:
        raw_result = dispatch(
            route.preflight_tool,
            _adapter_preflight_arguments(operation, destination),
            **dispatch_kwargs,
        )
    except Exception:
        return preflight_failure_result(
            operation,
            code="adapter_unavailable",
            error_type="setup_blocker",
        )
    return normalize_preflight_result(
        raw_result,
        operation=operation,
        destination=destination,
        route_binding=_route_binding(route),
    )


def preflight_task(
    arguments: Any,
    *,
    dispatch: Callable[..., Any],
    routes_file: Optional[str] = None,
    **dispatch_kwargs: Any,
) -> Dict[str, Any]:
    """Resolve and preflight one operation without performing a mutation."""
    operation = arguments.get("operation") if isinstance(arguments, dict) else None
    if not _is_interface_v2(arguments, {"interface_version", "operation"}):
        return preflight_failure_result(
            operation,
            code="invalid_write_request",
            error_type="contract_failure",
        )
    try:
        validated_operation = validate_operation_envelope(operation)
    except ContractValidationError:
        return preflight_failure_result(
            operation,
            code="invalid_task_operation",
            error_type="contract_failure",
        )
    try:
        route, destination = _resolve_write_route(
            validated_operation,
            routes_file,
        )
    except RouteConfigError as error:
        return preflight_failure_result(
            validated_operation,
            code=error.code,
            error_type="setup_blocker",
        )
    return _dispatch_preflight(
        route,
        validated_operation,
        destination,
        dispatch=dispatch,
        dispatch_kwargs=dispatch_kwargs,
    )


def _write_from_blocked_preflight(
    operation: Dict[str, Any], preflight_result: Dict[str, Any]
) -> Dict[str, Any]:
    error = preflight_result["error"]
    return write_failure_result(
        operation,
        code=error["code"],
        error_type=error["error_type"],
        status="blocked" if error["error_type"] == "setup_blocker" else "failed",
    )


def apply_task(
    arguments: Any,
    *,
    dispatch: Callable[..., Any],
    routes_file: Optional[str] = None,
    **dispatch_kwargs: Any,
) -> Dict[str, Any]:
    """Re-preflight and apply only the exact operation bound by an approval receipt."""
    preview = arguments.get("approval_preview") if isinstance(arguments, dict) else None
    operation = preview.get("operation") if isinstance(preview, dict) else None
    if not _is_interface_v2(
        arguments,
        {"interface_version", "approval_preview", "approval_receipt"},
    ):
        return write_failure_result(
            operation,
            code="invalid_write_request",
            error_type="contract_failure",
        )
    try:
        approved_preview = validate_approval_preview(preview)
        receipt = validate_approval_receipt(arguments["approval_receipt"])
        validated_operation = approved_preview["operation"]
    except ContractValidationError:
        return write_failure_result(
            operation,
            code="approval_mismatch",
            error_type="approval_failure",
        )
    try:
        route, destination = _resolve_write_route(
            validated_operation,
            routes_file,
        )
    except RouteConfigError as error:
        return write_failure_result(
            validated_operation,
            code=error.code,
            error_type="setup_blocker",
        )

    current_preflight = _dispatch_preflight(
        route,
        validated_operation,
        destination,
        dispatch=dispatch,
        dispatch_kwargs=dispatch_kwargs,
    )
    if not current_preflight["ok"]:
        return _write_from_blocked_preflight(validated_operation, current_preflight)

    current_preview = current_preflight["approval_preview"]
    try:
        authorized_preview = authorize_apply(
            approved_preview,
            receipt,
            current_preview,
            approval_mode=current_preflight["approval_mode"],
            preflight_passed=current_preflight["readiness"]["ok"],
            unresolved_uncertainty=current_preflight["approval_mode"]
            == "human_required",
        )
    except ApprovalBindingError as error:
        code = (
            "approval_required"
            if error.code == "human_approval_required"
            else "approval_mismatch"
        )
        return write_failure_result(
            validated_operation,
            code=code,
            error_type="approval_failure",
        )

    adapter_arguments = {
        "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
        "operation": deepcopy(authorized_preview["operation"]),
        "destination": deepcopy(authorized_preview["destination"]),
        "expected_side_effects": deepcopy(
            authorized_preview["expected_side_effects"]
        ),
        "operation_digest": receipt["operation_digest"],
    }
    try:
        raw_result = dispatch(
            route.apply_tool,
            adapter_arguments,
            **dispatch_kwargs,
        )
    except Exception:
        return write_failure_result(
            validated_operation,
            code="adapter_unavailable",
            error_type="setup_blocker",
        )
    return normalize_write_result(raw_result, operation=validated_operation)


def register_write_tools(ctx: Any) -> None:
    """Register the public v2 write facade without exposing adapter tools."""

    def preflight_handler(arguments: Any, **kwargs: Any) -> str:
        result = preflight_task(
            arguments,
            dispatch=ctx.dispatch_tool,
            routes_file=os.environ.get(ROUTES_FILE_ENV),
            **kwargs,
        )
        return json.dumps(result, ensure_ascii=False)

    def apply_handler(arguments: Any, **kwargs: Any) -> str:
        result = apply_task(
            arguments,
            dispatch=ctx.dispatch_tool,
            routes_file=os.environ.get(ROUTES_FILE_ENV),
            **kwargs,
        )
        return json.dumps(result, ensure_ascii=False)

    for name, schema, handler, description in (
        (
            PREFLIGHT_TOOL_NAME,
            TASK_PREFLIGHT_SCHEMA,
            preflight_handler,
            "Preview one backend-neutral task write without mutation.",
        ),
        (
            APPLY_TOOL_NAME,
            TASK_APPLY_SCHEMA,
            apply_handler,
            "Apply one exact approval-bound backend-neutral task operation.",
        ),
    ):
        ctx.register_tool(
            name=name,
            toolset=WRITE_TOOLSET,
            schema=schema,
            handler=handler,
            requires_env=[],
            description=description,
        )
