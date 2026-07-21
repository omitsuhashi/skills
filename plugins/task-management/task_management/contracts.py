"""Strict backend-neutral task and adapter wire contracts."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
import re
from typing import Any, Dict, List, Optional, TypedDict

from .safety import SafetyValidationError, validate_safe_url, validate_safe_value


__all__ = [
    "ADAPTER_CONTRACT_VERSION",
    "ContractValidationError",
    "TaskDraft",
    "TaskBackendDestination",
    "OperationEnvelope",
    "ApprovalPreview",
    "ApprovalReceipt",
    "TaskPreflightResult",
    "TaskWriteResult",
    "validate_task_draft",
    "validate_task_backend_destination",
    "validate_operation_envelope",
    "validate_approval_preview",
    "validate_approval_receipt",
    "validate_task_preflight_result",
    "validate_task_write_result",
    "validate_contract",
]
ADAPTER_CONTRACT_VERSION = 2
_OPERATION_FIELDS = {
    "adapter_contract_version",
    "operation_type",
    "backend_key",
    "destination_ref",
    "task_ref",
    "payload",
}
_OPERATION_TYPES = {
    "task.create",
    "task.update",
    "task.comment",
    "task.report",
}
_TASK_DRAFT_FIELDS = {
    "title",
    "body",
    "work_unit_id",
    "work_unit_name",
    "task_type",
    "due_date",
    "urgency",
    "importance",
    "automation_mode",
    "approval_required",
    "source_ref",
    "fields",
}
_TASK_TYPES = {
    "implementation",
    "review",
    "research",
    "decision",
    "coordination",
    "maintenance",
    "inbox_triage",
}
_URGENCY_VALUES = {"low", "normal", "high", "blocked"}
_IMPORTANCE_VALUES = {"low", "normal", "high", "critical"}
_AUTOMATION_MODES = {"manual_only", "assistive", "trusted_after_approval"}
_CHANGE_FIELDS = _TASK_DRAFT_FIELDS
_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_ERROR_TYPES = {
    "setup_blocker",
    "provider_failure",
    "partial_failure",
    "approval_failure",
    "contract_failure",
}


class TaskDraft(TypedDict):
    title: str
    body: str
    work_unit_id: str
    work_unit_name: str
    task_type: str
    due_date: Optional[str]
    urgency: str
    importance: str
    automation_mode: str
    approval_required: bool
    source_ref: Dict[str, str]
    fields: Dict[str, Any]


class TaskBackendDestination(TypedDict, total=False):
    backend_key: str
    destination_ref: str
    destination_label: str
    content_target_ref: Optional[str]


class OperationEnvelope(TypedDict):
    adapter_contract_version: int
    operation_type: str
    backend_key: str
    destination_ref: str
    task_ref: Optional[Dict[str, Any]]
    payload: Dict[str, Any]


class ApprovalPreview(TypedDict):
    preview_version: int
    operation: OperationEnvelope
    destination: TaskBackendDestination
    route_binding: Dict[str, str]
    expected_side_effects: List[Dict[str, str]]


class ApprovalReceipt(TypedDict):
    receipt_version: int
    decision: str
    operation_digest: str


class TaskPreflightResult(TypedDict):
    result_type: str
    ok: bool
    status: str
    operation_type: str
    backend_key: str
    destination_ref: str
    approval_mode: Optional[str]
    approval_preview: Optional[ApprovalPreview]
    approval_digest: Optional[str]
    readiness: Dict[str, Any]
    error: Optional[Dict[str, Any]]


class TaskWriteResult(TypedDict):
    result_type: str
    ok: bool
    status: str
    operation_type: str
    backend_key: str
    destination_ref: str
    task_ref: Optional[Dict[str, Any]]
    retryable: bool
    human_action: Optional[str]
    error: Optional[Dict[str, Any]]


class ContractValidationError(ValueError):
    """A safe contract failure with a stable machine-readable code."""

    def __init__(self, code: str, message: str, *, path: str = "$"):
        super().__init__(message)
        self.code = code
        self.path = path


def _validate_safe(value: Any, *, path: str = "$") -> None:
    try:
        validate_safe_value(value, path=path)
    except SafetyValidationError as error:
        raise ContractValidationError(error.code, str(error), path=error.path)


def _require_object(value: Any, *, name: str, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractValidationError("invalid_type", f"{name} must be an object.", path=path)
    return value


def _require_exact_fields(
    value: Dict[str, Any],
    *,
    required: set,
    optional: set = frozenset(),
    name: str,
    path: str,
) -> None:
    unexpected = set(value) - required - optional
    if unexpected:
        field = sorted(unexpected)[0]
        raise ContractValidationError(
            "unexpected_field",
            f"{name} contains an unsupported field.",
            path=f"{path}.{field}",
        )
    missing = required - set(value)
    if missing:
        field = sorted(missing)[0]
        raise ContractValidationError(
            "missing_field",
            f"{name} is missing a required field.",
            path=f"{path}.{field}",
        )


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _validate_source_ref(value: Any, *, path: str) -> None:
    source_ref = _require_object(value, name="SourceRef", path=path)
    _require_exact_fields(
        source_ref,
        required={"kind", "ref", "label"},
        name="SourceRef",
        path=path,
    )
    if not all(_is_nonempty_string(source_ref[field]) for field in ("kind", "ref", "label")):
        raise ContractValidationError(
            "invalid_source_ref",
            "SourceRef fields must be non-empty strings.",
            path=path,
        )


def _validate_task_draft(value: Any, *, path: str) -> None:
    draft = _require_object(value, name="TaskDraft", path=path)
    _require_exact_fields(
        draft,
        required=_TASK_DRAFT_FIELDS,
        name="TaskDraft",
        path=path,
    )
    for field in ("title", "body", "work_unit_id", "work_unit_name"):
        if not _is_nonempty_string(draft[field]):
            raise ContractValidationError(
                "invalid_task_draft",
                "TaskDraft text fields must be non-empty strings.",
                path=f"{path}.{field}",
            )
    if draft["task_type"] not in _TASK_TYPES:
        raise ContractValidationError("invalid_enum", "TaskDraft task_type is invalid.", path=f"{path}.task_type")
    if draft["due_date"] is not None and not _is_iso_date(draft["due_date"]):
        raise ContractValidationError("invalid_date", "TaskDraft due_date must be an ISO date or null.", path=f"{path}.due_date")
    if draft["urgency"] not in _URGENCY_VALUES:
        raise ContractValidationError("invalid_enum", "TaskDraft urgency is invalid.", path=f"{path}.urgency")
    if draft["importance"] not in _IMPORTANCE_VALUES:
        raise ContractValidationError("invalid_enum", "TaskDraft importance is invalid.", path=f"{path}.importance")
    if draft["automation_mode"] not in _AUTOMATION_MODES:
        raise ContractValidationError("invalid_enum", "TaskDraft automation_mode is invalid.", path=f"{path}.automation_mode")
    if not isinstance(draft["approval_required"], bool):
        raise ContractValidationError("invalid_type", "TaskDraft approval_required must be boolean.", path=f"{path}.approval_required")
    _validate_source_ref(draft["source_ref"], path=f"{path}.source_ref")
    if not isinstance(draft["fields"], dict):
        raise ContractValidationError("invalid_type", "TaskDraft fields must be an object.", path=f"{path}.fields")
    review_notes = draft["fields"].get("review_notes")
    if review_notes is not None and not _is_string_list(review_notes):
        raise ContractValidationError("invalid_task_draft", "TaskDraft review_notes must be a string array.", path=f"{path}.fields.review_notes")


def validate_task_draft(value: Any) -> TaskDraft:
    """Validate a backend-neutral TaskDraft and return a safe copy."""
    _validate_safe(value)
    _validate_task_draft(value, path="$")
    return deepcopy(value)


def _validate_task_backend_destination(value: Any, *, path: str) -> None:
    destination = _require_object(value, name="TaskBackendDestination", path=path)
    _require_exact_fields(
        destination,
        required={"backend_key", "destination_ref", "destination_label"},
        optional={"content_target_ref"},
        name="TaskBackendDestination",
        path=path,
    )
    for field in ("backend_key", "destination_ref", "destination_label"):
        if not _is_nonempty_string(destination[field]):
            raise ContractValidationError(
                "invalid_destination",
                "TaskBackendDestination fields must be non-empty strings.",
                path=f"{path}.{field}",
            )
    if "://" in destination["destination_ref"]:
        try:
            validate_safe_url(
                destination["destination_ref"],
                path=f"{path}.destination_ref",
            )
        except SafetyValidationError as error:
            raise ContractValidationError(error.code, str(error), path=error.path)
    if "content_target_ref" in destination and destination["content_target_ref"] is not None:
        if not _is_nonempty_string(destination["content_target_ref"]):
            raise ContractValidationError(
                "invalid_destination",
                "TaskBackendDestination content_target_ref must be non-empty or null.",
                path=f"{path}.content_target_ref",
            )


def validate_task_backend_destination(value: Any) -> TaskBackendDestination:
    """Validate a backend-neutral TaskBackendDestination and return a safe copy."""
    _validate_safe(value)
    _validate_task_backend_destination(value, path="$")
    return deepcopy(value)


def validate_approval_receipt(value: Any) -> ApprovalReceipt:
    """Validate the minimal caller-owned approval receipt."""
    _validate_safe(value)
    receipt = _require_object(value, name="ApprovalReceipt", path="$")
    _require_exact_fields(
        receipt,
        required={"receipt_version", "decision", "operation_digest"},
        name="ApprovalReceipt",
        path="$",
    )
    if type(receipt["receipt_version"]) is not int or receipt["receipt_version"] != 1:
        raise ContractValidationError(
            "unsupported_receipt_version",
            "ApprovalReceipt version is unsupported.",
            path="$.receipt_version",
        )
    if receipt["decision"] not in {"approved", "confidence_authorized"}:
        raise ContractValidationError(
            "invalid_approval_decision",
            "ApprovalReceipt decision is unsupported.",
            path="$.decision",
        )
    if not isinstance(receipt["operation_digest"], str) or _DIGEST_RE.fullmatch(receipt["operation_digest"]) is None:
        raise ContractValidationError(
            "invalid_digest",
            "ApprovalReceipt operation_digest must be a lowercase SHA-256 digest.",
            path="$.operation_digest",
        )
    return deepcopy(receipt)


def validate_approval_preview(value: Any) -> ApprovalPreview:
    """Validate the exact reviewable operation, destination, route, and effects."""
    _validate_safe(value)
    preview = _require_object(value, name="ApprovalPreview", path="$")
    _require_exact_fields(
        preview,
        required={
            "preview_version",
            "operation",
            "destination",
            "route_binding",
            "expected_side_effects",
        },
        name="ApprovalPreview",
        path="$",
    )
    if type(preview["preview_version"]) is not int or preview["preview_version"] != 1:
        raise ContractValidationError(
            "unsupported_preview_version",
            "ApprovalPreview version is unsupported.",
            path="$.preview_version",
        )
    operation = validate_operation_envelope(preview["operation"])
    destination = validate_task_backend_destination(preview["destination"])
    if operation["backend_key"] != destination["backend_key"]:
        raise ContractValidationError(
            "contract_mismatch",
            "ApprovalPreview backend_key values must match.",
            path="$.destination.backend_key",
        )
    if operation["destination_ref"] != destination["destination_ref"]:
        raise ContractValidationError(
            "contract_mismatch",
            "ApprovalPreview destination_ref values must match.",
            path="$.destination.destination_ref",
        )
    route_binding = _require_object(
        preview["route_binding"],
        name="RouteBinding",
        path="$.route_binding",
    )
    _require_exact_fields(
        route_binding,
        required={"adapter_key", "binding_digest"},
        name="RouteBinding",
        path="$.route_binding",
    )
    if not _is_nonempty_string(route_binding["adapter_key"]):
        raise ContractValidationError(
            "invalid_route_binding",
            "RouteBinding adapter_key must be non-empty.",
            path="$.route_binding.adapter_key",
        )
    if not isinstance(route_binding["binding_digest"], str) or _DIGEST_RE.fullmatch(route_binding["binding_digest"]) is None:
        raise ContractValidationError(
            "invalid_digest",
            "RouteBinding binding_digest must be a lowercase SHA-256 digest.",
            path="$.route_binding.binding_digest",
        )
    side_effects = preview["expected_side_effects"]
    if not isinstance(side_effects, list) or not side_effects:
        raise ContractValidationError(
            "invalid_side_effects",
            "ApprovalPreview expected_side_effects must be a non-empty array.",
            path="$.expected_side_effects",
        )
    for index, side_effect in enumerate(side_effects):
        effect_path = f"$.expected_side_effects[{index}]"
        effect = _require_object(side_effect, name="ExpectedSideEffect", path=effect_path)
        _require_exact_fields(
            effect,
            required={"effect_type", "description"},
            name="ExpectedSideEffect",
            path=effect_path,
        )
        if not _is_nonempty_string(effect["effect_type"]) or not _is_nonempty_string(effect["description"]):
            raise ContractValidationError(
                "invalid_side_effects",
                "Expected side effects require non-empty type and description.",
                path=effect_path,
            )
    return deepcopy(preview)


def _validate_typed_error(value: Any, *, path: str) -> None:
    error = _require_object(value, name="TaskError", path=path)
    _require_exact_fields(
        error,
        required={"error_type", "code", "message"},
        optional={"stage"},
        name="TaskError",
        path=path,
    )
    if error["error_type"] not in _ERROR_TYPES:
        raise ContractValidationError("invalid_error", "TaskError error_type is invalid.", path=f"{path}.error_type")
    for field in ("code", "message"):
        if not _is_nonempty_string(error[field]):
            raise ContractValidationError("invalid_error", "TaskError fields must be non-empty strings.", path=f"{path}.{field}")
    if "stage" in error and not _is_nonempty_string(error["stage"]):
        raise ContractValidationError("invalid_error", "TaskError stage must be non-empty when present.", path=f"{path}.stage")


def validate_task_preflight_result(value: Any) -> TaskPreflightResult:
    """Validate a public preflight result without treating readiness as approval."""
    _validate_safe(value)
    result = _require_object(value, name="TaskPreflightResult", path="$")
    _require_exact_fields(
        result,
        required={
            "result_type",
            "ok",
            "status",
            "operation_type",
            "backend_key",
            "destination_ref",
            "approval_mode",
            "approval_preview",
            "approval_digest",
            "readiness",
            "error",
        },
        name="TaskPreflightResult",
        path="$",
    )
    if result["result_type"] != "TaskPreflightResult":
        raise ContractValidationError("invalid_result_type", "TaskPreflightResult result_type is invalid.", path="$.result_type")
    if not isinstance(result["ok"], bool):
        raise ContractValidationError("invalid_type", "TaskPreflightResult ok must be boolean.", path="$.ok")
    if result["operation_type"] not in _OPERATION_TYPES:
        raise ContractValidationError("unsupported_operation", "TaskPreflightResult operation is unsupported.", path="$.operation_type")
    for field in ("backend_key", "destination_ref"):
        if not _is_nonempty_string(result[field]):
            raise ContractValidationError("invalid_result", "TaskPreflightResult references must be non-empty.", path=f"$.{field}")
    readiness = _require_object(result["readiness"], name="Readiness", path="$.readiness")
    _require_exact_fields(readiness, required={"ok", "checks"}, name="Readiness", path="$.readiness")
    if not isinstance(readiness["ok"], bool) or not isinstance(readiness["checks"], list):
        raise ContractValidationError("invalid_readiness", "Readiness requires boolean ok and an array of checks.", path="$.readiness")
    if result["ok"]:
        if result["status"] != "ready" or readiness["ok"] is not True or result["error"] is not None:
            raise ContractValidationError("invalid_result_state", "Successful preflight state is inconsistent.", path="$")
        if result["approval_mode"] not in {"human_required", "confidence_eligible"}:
            raise ContractValidationError("invalid_approval_mode", "Successful preflight approval_mode is invalid.", path="$.approval_mode")
        preview = validate_approval_preview(result["approval_preview"])
        if not isinstance(result["approval_digest"], str) or _DIGEST_RE.fullmatch(result["approval_digest"]) is None:
            raise ContractValidationError("invalid_digest", "TaskPreflightResult approval_digest is invalid.", path="$.approval_digest")
        operation = preview["operation"]
        for field in ("operation_type", "backend_key", "destination_ref"):
            if result[field] != operation[field]:
                raise ContractValidationError("contract_mismatch", "TaskPreflightResult does not match its preview.", path=f"$.{field}")
    else:
        if result["status"] != "blocked":
            raise ContractValidationError("invalid_result_state", "Failed preflight status must be blocked.", path="$.status")
        if result["approval_mode"] is not None or result["approval_preview"] is not None or result["approval_digest"] is not None:
            raise ContractValidationError("invalid_result_state", "Blocked preflight must not issue approval material.", path="$")
        if readiness["ok"] is not False or not isinstance(result["error"], dict):
            raise ContractValidationError("invalid_result_state", "Blocked preflight requires failed readiness and a typed error.", path="$")
        _validate_typed_error(result["error"], path="$.error")
    return deepcopy(result)


def validate_task_write_result(value: Any) -> TaskWriteResult:
    """Validate the allowlisted public result of an adapter write."""
    _validate_safe(value)
    result = _require_object(value, name="TaskWriteResult", path="$")
    _require_exact_fields(
        result,
        required={
            "result_type",
            "ok",
            "status",
            "operation_type",
            "backend_key",
            "destination_ref",
            "task_ref",
            "retryable",
            "human_action",
            "error",
        },
        name="TaskWriteResult",
        path="$",
    )
    if result["result_type"] != "TaskWriteResult":
        raise ContractValidationError("invalid_result_type", "TaskWriteResult result_type is invalid.", path="$.result_type")
    if not isinstance(result["ok"], bool) or not isinstance(result["retryable"], bool):
        raise ContractValidationError("invalid_type", "TaskWriteResult ok and retryable must be boolean.", path="$")
    operation_type = result["operation_type"]
    if operation_type not in _OPERATION_TYPES:
        raise ContractValidationError("unsupported_operation", "TaskWriteResult operation is unsupported.", path="$.operation_type")
    for field in ("backend_key", "destination_ref"):
        if not _is_nonempty_string(result[field]):
            raise ContractValidationError("invalid_result", "TaskWriteResult references must be non-empty.", path=f"$.{field}")
    if result["human_action"] is not None and not _is_nonempty_string(result["human_action"]):
        raise ContractValidationError("invalid_result", "TaskWriteResult human_action must be non-empty or null.", path="$.human_action")
    if result["task_ref"] is not None:
        _validate_task_ref(result["task_ref"], path="$.task_ref", backend_key=result["backend_key"])

    success_status = {
        "task.create": "created",
        "task.update": "updated",
        "task.comment": "commented",
        "task.report": "reported",
    }[operation_type]
    if result["ok"]:
        if (
            result["status"] != success_status
            or result["error"] is not None
            or result["retryable"] is not False
            or result["task_ref"] is None
        ):
            raise ContractValidationError("invalid_result_state", "Successful TaskWriteResult state is inconsistent.", path="$")
    else:
        if result["status"] not in {"blocked", "failed", "partial"} or not isinstance(result["error"], dict):
            raise ContractValidationError("invalid_result_state", "Failed TaskWriteResult state is inconsistent.", path="$")
        if result["status"] == "partial" and result["task_ref"] is None:
            raise ContractValidationError("invalid_result_state", "Partial TaskWriteResult requires a safe task_ref.", path="$.task_ref")
        _validate_typed_error(result["error"], path="$.error")
    return deepcopy(result)


def _validate_task_ref(value: Any, *, path: str, backend_key: Optional[str] = None) -> None:
    task_ref = _require_object(value, name="TaskRef", path=path)
    _require_exact_fields(
        task_ref,
        required={"backend_key", "task_ref", "task_url", "title"},
        name="TaskRef",
        path=path,
    )
    for field in ("backend_key", "task_ref", "title"):
        if not _is_nonempty_string(task_ref[field]):
            raise ContractValidationError(
                "invalid_task_ref",
                "TaskRef fields must be non-empty strings.",
                path=f"{path}.{field}",
            )
    if backend_key is not None and task_ref["backend_key"] != backend_key:
        raise ContractValidationError(
            "invalid_task_ref",
            "TaskRef backend_key must match the operation backend_key.",
            path=f"{path}.backend_key",
        )
    if task_ref["task_url"] is not None:
        try:
            validate_safe_url(task_ref["task_url"], path=f"{path}.task_url")
        except SafetyValidationError as error:
            raise ContractValidationError(error.code, str(error), path=error.path)


def _validate_update_changes(value: Any, *, path: str) -> None:
    changes = _require_object(value, name="Task update changes", path=path)
    if not changes:
        raise ContractValidationError(
            "invalid_payload",
            "task.update changes must not be empty.",
            path=path,
        )
    unexpected = set(changes) - _CHANGE_FIELDS
    if unexpected:
        field = sorted(unexpected)[0]
        raise ContractValidationError(
            "unexpected_field",
            "task.update changes contain an unsupported field.",
            path=f"{path}.{field}",
        )
    for field in ("title", "body", "work_unit_id", "work_unit_name"):
        if field in changes and not _is_nonempty_string(changes[field]):
            raise ContractValidationError("invalid_payload", "Task text changes must be non-empty strings.", path=f"{path}.{field}")
    if "task_type" in changes and changes["task_type"] not in _TASK_TYPES:
        raise ContractValidationError("invalid_enum", "task_type change is invalid.", path=f"{path}.task_type")
    if "due_date" in changes and changes["due_date"] is not None and not _is_iso_date(changes["due_date"]):
        raise ContractValidationError("invalid_date", "due_date change must be an ISO date or null.", path=f"{path}.due_date")
    if "urgency" in changes and changes["urgency"] not in _URGENCY_VALUES:
        raise ContractValidationError("invalid_enum", "urgency change is invalid.", path=f"{path}.urgency")
    if "importance" in changes and changes["importance"] not in _IMPORTANCE_VALUES:
        raise ContractValidationError("invalid_enum", "importance change is invalid.", path=f"{path}.importance")
    if "automation_mode" in changes and changes["automation_mode"] not in _AUTOMATION_MODES:
        raise ContractValidationError("invalid_enum", "automation_mode change is invalid.", path=f"{path}.automation_mode")
    if "approval_required" in changes and not isinstance(changes["approval_required"], bool):
        raise ContractValidationError("invalid_type", "approval_required change must be boolean.", path=f"{path}.approval_required")
    if "source_ref" in changes:
        _validate_source_ref(changes["source_ref"], path=f"{path}.source_ref")
    if "fields" in changes and not isinstance(changes["fields"], dict):
        raise ContractValidationError("invalid_type", "fields change must be an object.", path=f"{path}.fields")


def validate_operation_envelope(value: Any) -> Dict[str, Any]:
    """Validate and copy one adapter-neutral write operation."""
    _validate_safe(value)
    value = _require_object(value, name="OperationEnvelope", path="$")
    _require_exact_fields(
        value,
        required=_OPERATION_FIELDS,
        name="OperationEnvelope",
        path="$",
    )
    if value.get("adapter_contract_version") != ADAPTER_CONTRACT_VERSION:
        raise ContractValidationError(
            "unsupported_contract_version",
            "OperationEnvelope contract version is unsupported.",
            path="$.adapter_contract_version",
        )
    operation_type = value.get("operation_type")
    if operation_type not in _OPERATION_TYPES:
        raise ContractValidationError(
            "unsupported_operation",
            "OperationEnvelope operation is unsupported.",
            path="$.operation_type",
        )
    for field in ("backend_key", "destination_ref"):
        if not _is_nonempty_string(value[field]):
            raise ContractValidationError(
                "invalid_operation",
                "OperationEnvelope references must be non-empty strings.",
                path=f"$.{field}",
            )
    payload = value.get("payload")
    if operation_type == "task.create":
        if value.get("task_ref") is not None:
            raise ContractValidationError(
                "invalid_task_ref",
                "task.create forbids task_ref.",
                path="$.task_ref",
            )
        if not isinstance(payload, dict) or set(payload) != {"task"}:
            raise ContractValidationError(
                "invalid_payload",
                "task.create requires only payload.task.",
                path="$.payload",
            )
        _validate_task_draft(payload["task"], path="$.payload.task")
    if operation_type == "task.update":
        if not isinstance(payload, dict) or set(payload) != {"changes"}:
            raise ContractValidationError(
                "invalid_payload",
                "task.update requires only payload.changes.",
                path="$.payload",
            )
        _validate_task_ref(value.get("task_ref"), path="$.task_ref", backend_key=value.get("backend_key"))
        _validate_update_changes(payload["changes"], path="$.payload.changes")
    if operation_type == "task.comment":
        if (
            not isinstance(payload, dict)
            or set(payload) != {"comment"}
            or not isinstance(payload.get("comment"), dict)
            or set(payload["comment"]) != {"body"}
            or not _is_nonempty_string(payload["comment"].get("body"))
        ):
            raise ContractValidationError(
                "invalid_payload",
                "task.comment requires task_ref and non-empty payload.comment.body.",
                path="$.payload",
            )
        _validate_task_ref(value["task_ref"], path="$.task_ref", backend_key=value["backend_key"])
    if operation_type == "task.report":
        report = payload.get("report") if isinstance(payload, dict) else None
        report_fields = {"summary", "work_performed", "verification", "residuals"}
        report_is_valid = (
            isinstance(payload, dict)
            and set(payload) == {"report"}
            and isinstance(report, dict)
            and set(report) == report_fields
            and isinstance(report.get("summary"), str)
            and bool(report["summary"].strip())
            and _is_nonempty_string_list(report.get("work_performed"))
            and _is_nonempty_string_list(report.get("verification"))
            and _is_string_list(report.get("residuals"))
        )
        if not report_is_valid:
            raise ContractValidationError(
                "invalid_payload",
                "task.report requires a complete structured work report.",
                path="$.payload",
            )
        _validate_task_ref(value["task_ref"], path="$.task_ref", backend_key=value["backend_key"])
    return deepcopy(value)


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def _is_nonempty_string_list(value: Any) -> bool:
    return _is_string_list(value) and bool(value)


def validate_contract(contract_name: str, value: Any) -> Dict[str, Any]:
    """Validate one named normative adapter-v2 fixture contract."""
    validators = {
        "TaskDraft": validate_task_draft,
        "TaskBackendDestination": validate_task_backend_destination,
        "OperationEnvelope": validate_operation_envelope,
        "ApprovalPreview": validate_approval_preview,
        "ApprovalReceipt": validate_approval_receipt,
        "TaskPreflightResult": validate_task_preflight_result,
        "TaskWriteResult": validate_task_write_result,
    }
    validator = validators.get(contract_name)
    if validator is None:
        raise ContractValidationError(
            "unknown_contract",
            "Requested contract validator is unsupported.",
            path="$",
        )
    return validator(value)
