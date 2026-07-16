"""Dispatch task reads to one exact MCP or provider-plugin read tool."""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict

from . import ADAPTER_CONTRACT_VERSION, AdapterError, AdapterTaskSnapshotResult
from ..route_config import ResolvedTaskReadRequest


_TOOL_RE = re.compile(
    r"^(?:mcp__[a-z0-9_]+__task_query|task_adapter__[a-z0-9_]+__task_query)$"
)
_PROVIDER_ERRORS = {
    "adapter_unavailable": "read_adapter_unavailable",
    "auth_missing": "read_adapter_auth_missing",
    "permission_denied": "read_adapter_permission_denied",
    "destination_not_found": "read_destination_not_found",
    "field_missing": "read_adapter_field_missing",
    "rate_limited": "read_adapter_rate_limited",
    "timeout": "read_adapter_timeout",
}


class ExternalToolAdapter:
    def __init__(self, *, tool_name: str, dispatch: Callable[..., Any]):
        if _TOOL_RE.fullmatch(tool_name) is None:
            raise AdapterError("invalid_read_adapter_tool", "Configured task adapter tool is not read-only.")
        self._tool_name = tool_name
        self._dispatch = dispatch

    def query(self, request: ResolvedTaskReadRequest, **dispatch_kwargs: Any) -> AdapterTaskSnapshotResult:
        envelope = {
            "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
            "capability": "task_read",
            "destination_ref": request.provider_destination_ref,
            "query": request.query,
        }
        try:
            raw = self._dispatch(self._tool_name, envelope, **dispatch_kwargs)
        except Exception:
            raise AdapterError("read_adapter_unavailable", "External task read adapter is unavailable.")
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                raise AdapterError("invalid_adapter_result", "External task read adapter returned invalid JSON.")
        if not isinstance(raw, dict):
            raise AdapterError("invalid_adapter_result", "External task read adapter returned an invalid result.")
        if raw.get("adapter_contract_version") != ADAPTER_CONTRACT_VERSION:
            raise AdapterError("adapter_contract_mismatch", "External task read adapter contract version is unsupported.")
        provider_error = raw.get("error")
        if provider_error:
            provider_code = provider_error.get("code") if isinstance(provider_error, dict) else None
            code = _PROVIDER_ERRORS.get(provider_code, "read_adapter_failed")
            raise AdapterError(code, "External task read adapter reported a failure.")
        items = raw.get("items")
        if not isinstance(items, list):
            raise AdapterError("invalid_adapter_result", "External task read adapter must return an items array.")
        return AdapterTaskSnapshotResult(ADAPTER_CONTRACT_VERSION, items)

