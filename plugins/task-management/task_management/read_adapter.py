"""Backend-neutral task reads exposed through the Hermes plugin toolset."""

from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from urllib.parse import urlparse

from .provider_adapters import AdapterError
from .provider_adapters.external_tool import ExternalToolAdapter
from .provider_adapters.local_json import LocalJsonAdapter
from .route_config import (
    ROUTES_FILE_ENV,
    ResolvedTaskReadRequest,
    RouteConfigError,
    load_read_route,
)


ADAPTER_TOOL_ENV = "TASK_MANAGEMENT_READ_ADAPTER_TOOL"
READ_TOOLSET = "task-management-read"
PUBLIC_TOOL_NAME = "task_query"
_ADAPTER_TOOL_RE = re.compile(r"^mcp__[a-z0-9_]+__task_query$")
_UNSAFE_VALUE_RE = re.compile(
    r"\bauthorization\b|\bbearer\s+|\bghp_[a-z0-9_]+|"
    r"\bgithub_pat_[a-z0-9_]+|\btoken\s*[\"']?\s*[:=]|"
    r"\b(?:api[_-]?key|password|passwd|client[_-]?secret|"
    r"access[_-]?token|refresh[_-]?token)\s*[\"']?\s*[:=]|"
    r"\b(?:node|field|project|repository|item|record|raw)_id\s*[\"']?\s*[:=]|"
    r"\b(?:PVT|PVTI|PVTF|PVTS|PVTR)_[a-z0-9_-]+|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    re.IGNORECASE,
)
_QUERY_FIELDS = {
    "backend_key",
    "work_unit_id",
    "task_type",
    "status",
    "due_before",
    "limit",
}
_QUERY_STRING_FIELDS = {
    "backend_key",
    "work_unit_id",
    "task_type",
    "status",
}
_SNAPSHOT_FIELDS = (
    "title",
    "body",
    "work_unit_id",
    "work_unit_name",
    "task_type",
    "status",
    "due_date",
    "urgency",
    "importance",
    "automation_mode",
    "approval_required",
)
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
MAX_ADAPTER_RESPONSE_BYTES = 5 * 1024 * 1024
MAX_ADAPTER_ITEMS = 100


TASK_QUERY_SCHEMA = {
    "name": PUBLIC_TOOL_NAME,
    "description": (
        "Read tasks through the configured backend adapter and return only "
        "backend-neutral TaskSnapshot values. This tool never mutates tasks."
    ),
    "parameters": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "destination_ref": {
                "type": "string",
                "description": "Opaque host-owned task destination reference.",
            },
            "query": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "backend_key": {"type": "string"},
                    "work_unit_id": {"type": "string"},
                    "task_type": {"type": "string"},
                    "status": {"type": "string"},
                    "due_before": {"type": ["string", "null"]},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                },
            },
        },
        "required": ["destination_ref", "query"],
    },
}


def _error(code: str, message: str, **details: Any) -> Dict[str, Any]:
    error = {"code": code, "message": message}
    error.update(details)
    return {
        "result_type": "TaskSnapshotResult",
        "ok": False,
        "task_snapshots": [],
        "error": error,
    }


def _parse_adapter_result(raw_result: Any) -> Optional[Dict[str, Any]]:
    if isinstance(raw_result, dict):
        try:
            serialized = json.dumps(
                raw_result,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            if len(serialized.encode("utf-8")) > MAX_ADAPTER_RESPONSE_BYTES:
                return None
        except (TypeError, ValueError, OverflowError, UnicodeError, RecursionError):
            return None
        return raw_result
    if not isinstance(raw_result, str):
        return None
    try:
        if len(raw_result.encode("utf-8")) > MAX_ADAPTER_RESPONSE_BYTES:
            return None
    except UnicodeError:
        return None
    try:
        value = json.loads(raw_result)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _is_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _is_safe_link(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urlparse(value)
        return (
            parsed.scheme.lower() in {"http", "https"}
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
        )
    except ValueError:
        return False


def _normalize_task_ref(value: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(value, dict):
        return None
    required = ("backend_key", "task_ref", "task_url", "title")
    if any(key not in value for key in required):
        return None
    if not all(isinstance(value[key], str) for key in ("backend_key", "task_ref", "title")):
        return None
    if value["task_url"] is not None and not _is_safe_link(value["task_url"]):
        return None
    return {key: value[key] for key in required}


def _normalize_source_ref(value: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(value, dict):
        return None
    required = ("kind", "ref", "label")
    if any(key not in value for key in required):
        return None
    if not all(isinstance(value[key], str) for key in required):
        return None
    return {key: value[key] for key in required}


def _normalize_backend_metadata(value: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(value, dict):
        return None
    display_link = value.get("display_link")
    if display_link is None:
        return {}
    if not isinstance(display_link, dict):
        return None
    if not isinstance(display_link.get("name"), str) or not _is_safe_link(
        display_link.get("url")
    ):
        return None
    return {
        "display_link": {
            "name": display_link["name"],
            "url": display_link["url"],
        }
    }


def _normalize_snapshot(
    value: Any,
    *,
    expected_backend_key: str,
) -> Optional[Dict[str, Any]]:
    if not isinstance(value, dict):
        return None
    task_ref = _normalize_task_ref(value.get("task_ref"))
    source_ref = _normalize_source_ref(value.get("source_ref"))
    backend_metadata = _normalize_backend_metadata(value.get("backend_metadata"))
    if task_ref is None or source_ref is None or backend_metadata is None:
        return None
    if task_ref["backend_key"] != expected_backend_key:
        return None
    if any(field not in value for field in _SNAPSHOT_FIELDS):
        return None
    string_fields = tuple(
        field
        for field in _SNAPSHOT_FIELDS
        if field not in {"due_date", "approval_required"}
    )
    if any(not isinstance(value[field], str) for field in string_fields):
        return None
    if value["due_date"] is not None and not _is_iso_date(value["due_date"]):
        return None
    if not isinstance(value["approval_required"], bool):
        return None
    if value["task_type"] not in _TASK_TYPES:
        return None
    if value["urgency"] not in _URGENCY_VALUES:
        return None
    if value["importance"] not in _IMPORTANCE_VALUES:
        return None
    if value["automation_mode"] not in _AUTOMATION_MODES:
        return None

    snapshot = {
        "result_type": "TaskSnapshot",
        "task_ref": task_ref,
        **{field: value[field] for field in _SNAPSHOT_FIELDS},
        "source_ref": source_ref,
        "backend_metadata": backend_metadata,
    }
    return snapshot


def _contains_unsafe_value(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_contains_unsafe_value(child) for child in value.values())
    if isinstance(value, list):
        return any(_contains_unsafe_value(child) for child in value)
    return isinstance(value, str) and _UNSAFE_VALUE_RE.search(value) is not None


def query_tasks(
    arguments: Any,
    *,
    dispatch: Callable[..., Any],
    adapter_tool_name: Optional[str] = None,
    routes_file: Optional[str] = None,
    **dispatch_kwargs: Any,
) -> Dict[str, Any]:
    """Dispatch one backend-neutral TaskQuery and normalize TaskSnapshot values."""
    if not isinstance(arguments, dict):
        return _error("invalid_task_query", "Tool arguments must be an object.")

    query = arguments.get("query")
    destination_ref = arguments.get("destination_ref")
    if not isinstance(query, dict) or not isinstance(destination_ref, str) or not destination_ref:
        return _error(
            "invalid_task_query",
            "TaskQuery and destination_ref are required.",
        )
    if set(query) - _QUERY_FIELDS:
        return _error("invalid_task_query", "TaskQuery contains unsupported fields.")
    if any(
        field in query and not isinstance(query[field], str)
        for field in _QUERY_STRING_FIELDS
    ):
        return _error("invalid_task_query", "TaskQuery string fields must be strings.")
    due_before = query.get("due_before")
    if due_before is not None and not isinstance(due_before, str):
        return _error("invalid_task_query", "TaskQuery due_before must be a string or null.")
    if due_before is not None and not _is_iso_date(due_before):
        return _error("invalid_task_query", "TaskQuery due_before must be an ISO date.")
    if "task_type" in query and query["task_type"] not in _TASK_TYPES:
        return _error("invalid_task_query", "TaskQuery task_type is not canonical.")
    limit = query.get("limit")
    if limit is not None and (
        isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100
    ):
        return _error("invalid_task_query", "TaskQuery limit must be between 1 and 100.")
    if _contains_unsafe_value({"query": query, "destination_ref": destination_ref}):
        return _error(
            "invalid_task_query",
            "TaskQuery and destination_ref must not contain credential data.",
        )

    expected_backend_key = query.get("backend_key")
    if routes_file:
        try:
            route = load_read_route(
                Path(routes_file),
                expected_backend_key,
                destination_ref,
            )
            expected_backend_key = route.backend_key
            resolved_query = dict(query)
            resolved_query["backend_key"] = route.backend_key
            request = ResolvedTaskReadRequest(
                backend_key=route.backend_key,
                destination_ref=destination_ref,
                provider_destination_ref=route.provider_destination_ref,
                query=resolved_query,
            )
            if route.kind == "local_json":
                adapter = LocalJsonAdapter(
                    read_root=route.read_root,
                    source_path=route.source_path,
                )
            else:
                adapter = ExternalToolAdapter(
                    tool_name=route.tool_name,
                    dispatch=dispatch,
                )
            adapter_result = adapter.query(request, **dispatch_kwargs)
            raw_result = {
                "adapter_contract_version": adapter_result.adapter_contract_version,
                "items": adapter_result.items,
            }
        except RouteConfigError as exc:
            return _error(exc.code, str(exc), configuration=ROUTES_FILE_ENV)
        except AdapterError as exc:
            return _error(exc.code, str(exc))
    else:
        if not adapter_tool_name:
            return _error(
                "read_adapter_unavailable",
                "No backend read adapter tool is configured.",
                configuration=ADAPTER_TOOL_ENV,
            )
        if _ADAPTER_TOOL_RE.fullmatch(adapter_tool_name) is None:
            return _error(
                "invalid_read_adapter_tool",
                "The configured adapter must be an MCP task_query read tool.",
                configuration=ADAPTER_TOOL_ENV,
            )
        if not isinstance(expected_backend_key, str) or not expected_backend_key:
            return _error(
                "invalid_task_query",
                "TaskQuery backend_key is required in legacy adapter mode.",
            )
        try:
            raw_result = dispatch(
                adapter_tool_name,
                {"query": query, "destination_ref": destination_ref},
                **dispatch_kwargs,
            )
        except Exception:
            return _error("read_adapter_failed", "Backend read adapter failed.")
    adapter_result = _parse_adapter_result(raw_result)
    if adapter_result is None:
        return _error("invalid_adapter_result", "Backend read adapter returned invalid JSON.")
    if adapter_result.get("error"):
        return _error(
            "read_adapter_failed",
            "Backend read adapter failed.",
        )

    items = adapter_result.get("items", adapter_result.get("task_snapshots"))
    if not isinstance(items, list):
        return _error(
            "invalid_adapter_result",
            "Backend read adapter must return an items array.",
        )
    if len(items) > MAX_ADAPTER_ITEMS:
        return _error(
            "invalid_adapter_result",
            "Backend read adapter returned too many items.",
        )
    items = items[: query.get("limit", MAX_ADAPTER_ITEMS)]

    snapshots = []
    for item in items:
        snapshot = _normalize_snapshot(
            item,
            expected_backend_key=expected_backend_key,
        )
        if snapshot is None:
            return _error(
                "invalid_task_snapshot",
                "Backend read adapter returned an invalid task snapshot.",
            )
        if _contains_unsafe_value(snapshot):
            return _error(
                "unsafe_task_snapshot",
                "Backend read adapter returned a snapshot containing forbidden "
                "provider or credential data.",
            )
        snapshots.append(snapshot)

    return {
        "result_type": "TaskSnapshotResult",
        "ok": True,
        "backend_key": expected_backend_key,
        "destination_ref": destination_ref,
        "task_snapshots": snapshots,
        "error": None,
    }


def register_read_tool(ctx: Any, adapter_tool_name: Optional[str] = None) -> None:
    """Register the read-only Hermes tool while keeping backend dispatch fixed."""

    def handler(arguments: Any, **kwargs: Any) -> str:
        result = query_tasks(
            arguments,
            dispatch=ctx.dispatch_tool,
            adapter_tool_name=os.environ.get(ADAPTER_TOOL_ENV, adapter_tool_name),
            routes_file=os.environ.get(ROUTES_FILE_ENV),
            **kwargs,
        )
        return json.dumps(result, ensure_ascii=False)

    ctx.register_tool(
        name=PUBLIC_TOOL_NAME,
        toolset=READ_TOOLSET,
        schema=TASK_QUERY_SCHEMA,
        handler=handler,
        requires_env=[],
        description="Read backend-neutral task snapshots without task mutations.",
    )
