"""Fail-closed safety checks shared by task contract validators."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qsl, urlparse


_CREDENTIAL_KEYS = {
    "authorization",
    "token",
    "api_key",
    "password",
    "passwd",
    "secret",
    "client_secret",
    "access_token",
    "refresh_token",
}
_RAW_PROVIDER_KEYS = {
    "node_id",
    "project_id",
    "project_number",
    "repository_id",
    "field_id",
    "option_id",
    "item_id",
    "record_id",
    "provider_id",
    "raw_id",
}
_RAW_PAYLOAD_KEYS = {
    "raw_payload",
    "provider_payload",
    "raw_provider_payload",
    "raw_response",
    "provider_response",
    "trace_dump",
}
_UNSAFE_STRING_RE = re.compile(
    r"\bauthorization\s*[:=]|\bbearer\s+[A-Za-z0-9._~+/=-]+|"
    r"\b(?:api[_-]?key|password|passwd|client[_-]?secret|access[_-]?token|"
    r"refresh[_-]?token|token)\s*[\"']?\s*[:=]|"
    r"\b(?:node|field|project|repository|option|item|record|raw)_id\s*[\"']?\s*[:=]|"
    r"\b(?:ghp_|github_pat_|PVT_|PVTI_|PVTF_|PVTS_|PVTR_)[A-Za-z0-9_-]+|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    re.IGNORECASE,
)


class SafetyValidationError(ValueError):
    """Safe validation failure with a stable code and JSON-style path."""

    def __init__(self, code: str, message: str, *, path: str):
        super().__init__(message)
        self.code = code
        self.path = path


def validate_safe_value(value: Any, *, path: str = "$") -> None:
    """Require JSON-compatible canonical values without floating point data."""
    if value is None or isinstance(value, (bool, int)):
        return
    if isinstance(value, str):
        if _UNSAFE_STRING_RE.search(value):
            raise SafetyValidationError(
                "unsafe_data",
                "Contract values must not contain credential or raw provider data.",
                path=path,
            )
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_safe_value(item, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise SafetyValidationError(
                    "invalid_canonical_value",
                    "Contract object keys must be strings.",
                    path=path,
                )
            normalized_key = key.lower().replace("-", "_")
            if normalized_key in _CREDENTIAL_KEYS:
                raise SafetyValidationError(
                    "unsafe_data",
                    "Contract values must not contain credential fields.",
                    path=f"{path}.{key}",
                )
            if normalized_key in _RAW_PROVIDER_KEYS | _RAW_PAYLOAD_KEYS:
                raise SafetyValidationError(
                    "unsafe_data",
                    "Contract values must not contain raw provider data.",
                    path=f"{path}.{key}",
                )
            validate_safe_value(item, path=f"{path}.{key}")
        return
    raise SafetyValidationError(
        "invalid_canonical_value",
        "Contract values must use canonical JSON types without floats.",
        path=path,
    )


def validate_safe_url(value: Any, *, path: str = "$") -> str:
    """Require an HTTPS URL without userinfo or credential-bearing components."""
    if not isinstance(value, str):
        raise SafetyValidationError(
            "unsafe_url",
            "Public task URLs must be HTTPS URLs.",
            path=path,
        )
    try:
        parsed = urlparse(value)
        if (
            parsed.scheme.lower() != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ValueError("unsafe URL authority")
        query_items = parse_qsl(parsed.query, keep_blank_values=True)
        if any(
            key.lower().replace("-", "_") in _CREDENTIAL_KEYS
            or _UNSAFE_STRING_RE.search(f"{key}={item}")
            for key, item in query_items
        ):
            raise ValueError("credential query")
        if parsed.fragment and _UNSAFE_STRING_RE.search(parsed.fragment):
            raise ValueError("credential fragment")
        _ = parsed.port
    except (ValueError, UnicodeError):
        raise SafetyValidationError(
            "unsafe_url",
            "Public task URLs must use safe HTTPS URLs without credentials.",
            path=path,
        )
    return value
