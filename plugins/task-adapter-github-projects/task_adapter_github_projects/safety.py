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
_CALLER_TOOL_KEYS = {
    "tool",
    "tool_name",
    "mcp_tool",
    "mcp_tool_name",
}
_ARBITRARY_DISPATCH_KEYS = {
    "dispatch",
    "dispatcher",
    "dispatch_tool",
}
_HOST_ATTESTATION_FIELDS = {
    "projects_toolset_enabled",
    "issue_write_enabled",
    "comment_write_enabled",
    "raw_mcp_exposure",
    "adapter_write_exposure",
}
_MCP_TOOL_NAME_RE = re.compile(r"^mcp__[a-z0-9_]+__[a-z0-9_]+$")
_CREDENTIAL_STRING_RE = re.compile(
    r"\bauthorization\s*[:=]|\bbearer\s+[A-Za-z0-9._~+/=-]+|"
    r"\b(?:api[_-]?key|password|passwd|client[_-]?secret|access[_-]?token|"
    r"refresh[_-]?token|token)\s*[\"']?\s*[:=]|"
    r"\b(?:ghp_|github_pat_)[A-Za-z0-9_-]+|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    re.IGNORECASE,
)
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


def _reject_caller_dispatch(value: Any, *, path: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized_key = key.lower().replace("-", "_")
            item_path = f"{path}.{key}"
            if normalized_key in _ARBITRARY_DISPATCH_KEYS:
                raise SafetyValidationError(
                    "arbitrary_dispatch",
                    "Adapter callers must not supply a dispatch seam.",
                    path=item_path,
                )
            if normalized_key in _CALLER_TOOL_KEYS:
                raise SafetyValidationError(
                    "caller_tool_selection",
                    "Adapter callers must not select MCP tools.",
                    path=item_path,
                )
            _reject_caller_dispatch(item, path=item_path)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _reject_caller_dispatch(item, path=f"{path}[{index}]")
        return
    if isinstance(value, str) and _MCP_TOOL_NAME_RE.fullmatch(value):
        raise SafetyValidationError(
            "caller_tool_selection",
            "Adapter callers must not supply raw MCP tool names.",
            path=path,
        )


def validate_adapter_arguments(value: Any, *, path: str = "$") -> Any:
    """Reject credentials and all caller-controlled provider dispatch choices."""
    validate_safe_value(value, path=path)
    _reject_caller_dispatch(value, path=path)
    return value


def validate_host_attestation(value: Any, *, path: str = "$") -> dict:
    """Require the exact fail-closed host exposure contract."""
    validate_safe_value(value, path=path)
    if not isinstance(value, dict) or set(value) != _HOST_ATTESTATION_FIELDS:
        raise SafetyValidationError(
            "unsafe_delegation_exposure",
            "Host attestation must use the exact approved fields.",
            path=path,
        )
    safe = (
        value["projects_toolset_enabled"] is True
        and value["issue_write_enabled"] is True
        and value["comment_write_enabled"] is True
        and value["raw_mcp_exposure"] == "adapter_only"
        and value["adapter_write_exposure"] == "task_management_only"
    )
    if not safe:
        raise SafetyValidationError(
            "unsafe_delegation_exposure",
            "Adapter tools require adapter-only MCP and task-management-only write exposure.",
            path=path,
        )
    return dict(value)


def validate_credential_free_config(value: Any, *, path: str = "$") -> None:
    """Reject credentials while permitting adapter-private provider coordinates."""
    if value is None or isinstance(value, (bool, int)):
        return
    if isinstance(value, str):
        if _CREDENTIAL_STRING_RE.search(value):
            raise SafetyValidationError(
                "unsafe_data",
                "Host config must not contain credential material.",
                path=path,
            )
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_credential_free_config(item, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise SafetyValidationError(
                    "invalid_canonical_value",
                    "Host config keys must be strings.",
                    path=path,
                )
            normalized_key = key.lower().replace("-", "_")
            if normalized_key in _CREDENTIAL_KEYS:
                raise SafetyValidationError(
                    "unsafe_data",
                    "Host config must not contain credential fields.",
                    path=f"{path}.{key}",
                )
            validate_credential_free_config(item, path=f"{path}.{key}")
        return
    raise SafetyValidationError(
        "invalid_canonical_value",
        "Host config values must use canonical TOML scalar types.",
        path=path,
    )


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
