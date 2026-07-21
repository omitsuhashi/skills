"""Deterministic approval identity binding for backend-neutral task operations."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from typing import Any

from .contracts import (
    ContractValidationError,
    validate_approval_preview,
    validate_approval_receipt,
)


class ApprovalBindingError(ValueError):
    """Fail-closed approval identity or policy failure."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class CanonicalJsonError(ValueError):
    """Canonical JSON domain failure with a stable machine-readable code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _invalid_canonical_value() -> CanonicalJsonError:
    return CanonicalJsonError(
        "invalid_canonical_value",
        "Canonical JSON accepts only null, booleans, integers, strings, arrays, and objects.",
    )


def _normalize_canonical(value: Any) -> Any:
    if value is None or type(value) in {bool, int}:
        return value
    if type(value) is str:
        return unicodedata.normalize("NFC", value)
    if type(value) is list:
        return [_normalize_canonical(item) for item in value]
    if type(value) is dict:
        normalized = {}
        for key, item in value.items():
            if type(key) is not str:
                raise _invalid_canonical_value()
            canonical_key = unicodedata.normalize("NFC", key)
            if canonical_key in normalized:
                raise _invalid_canonical_value()
            normalized[canonical_key] = _normalize_canonical(item)
        return normalized
    raise _invalid_canonical_value()


def canonical_json(value: Any) -> str:
    """Encode one value with NFC strings, sorted keys, and compact separators."""
    return json.dumps(
        _normalize_canonical(value),
        allow_nan=False,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def canonical_digest(value: Any) -> str:
    """Return a lowercase SHA-256 digest over canonical UTF-8 JSON."""
    encoded = canonical_json(value).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def approval_digest(preview: Any) -> str:
    """Bind the complete validated ApprovalPreview to one deterministic digest."""
    try:
        validated = validate_approval_preview(preview)
    except ContractValidationError as error:
        raise ApprovalBindingError(error.code, str(error))
    return canonical_digest(validated)


def _approval_mismatch() -> ApprovalBindingError:
    return ApprovalBindingError(
        "approval_mismatch",
        "The approved operation no longer matches the current preflight preview.",
    )


def authorize_apply(
    approved_preview: Any,
    receipt: Any,
    current_preview: Any,
    *,
    approval_mode: str,
    preflight_passed: bool,
    unresolved_uncertainty: bool,
) -> Any:
    """Return the current preview only when its complete identity is unchanged."""
    try:
        approved = validate_approval_preview(approved_preview)
        current = validate_approval_preview(current_preview)
        validated_receipt = validate_approval_receipt(receipt)
    except ContractValidationError:
        raise _approval_mismatch()

    approved_digest = canonical_digest(approved)
    if validated_receipt["operation_digest"] != approved_digest:
        raise _approval_mismatch()
    if canonical_digest(current) != approved_digest:
        raise _approval_mismatch()

    if type(preflight_passed) is not bool or not preflight_passed:
        raise ApprovalBindingError(
            "preflight_not_ready",
            "Write approval cannot override a failed or missing current preflight.",
        )
    if approval_mode not in {"human_required", "confidence_eligible"}:
        raise ApprovalBindingError(
            "invalid_approval_mode",
            "Current preflight approval mode is invalid.",
        )
    if type(unresolved_uncertainty) is not bool:
        raise ApprovalBindingError(
            "invalid_approval_policy",
            "Current preflight uncertainty must be an explicit boolean.",
        )
    if validated_receipt["decision"] == "confidence_authorized" and (
        approval_mode != "confidence_eligible" or unresolved_uncertainty
    ):
        raise ApprovalBindingError(
            "human_approval_required",
            "Confidence authorization is unavailable for this operation.",
        )
    return current
