"""Load host-owned task read routes without exposing provider details to callers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

try:  # Python 3.11+
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - exercised by the Python 3.9 test runtime
    tomllib = None


ROUTES_FILE_ENV = "TASK_MANAGEMENT_ROUTES_FILE"
ROUTE_CONTRACT_VERSION = 2
_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_ADAPTER_TOOL_RE = re.compile(
    r"^task_adapter__([a-z0-9_]+)__task_(query|preflight|apply)$"
)


class RouteConfigError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ResolvedTaskReadRoute:
    backend_key: str
    adapter_key: str
    kind: str
    destination_ref: str
    destination_label: str
    query_tool: str
    preflight_tool: str
    apply_tool: str
    content_target_ref: Optional[str] = None
    read_root: Optional[Path] = None
    source_path: Optional[Path] = None


@dataclass(frozen=True)
class ResolvedTaskReadRequest:
    backend_key: str
    destination_ref: str
    query: Dict[str, Any]


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.isdigit():
        return int(value)
    raise ValueError("unsupported TOML value")


def _loads_toml_compat(text: str) -> Dict[str, Any]:
    """Parse the deliberately small route-template TOML subset on Python 3.9."""
    root: Dict[str, Any] = {}
    current = root
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            parts = line[1:-1].split(".")
            if not parts or any(_KEY_RE.fullmatch(part) is None for part in parts):
                raise ValueError("invalid TOML table")
            current = root
            for part in parts:
                child = current.setdefault(part, {})
                if not isinstance(child, dict):
                    raise ValueError("TOML table conflicts with value")
                current = child
            continue
        if "=" not in line:
            raise ValueError("invalid TOML assignment")
        key, value = (part.strip() for part in line.split("=", 1))
        if _KEY_RE.fullmatch(key) is None or key in current:
            raise ValueError("invalid or duplicate TOML key")
        current[key] = _parse_scalar(value)
    return root


def _load_document(path: Path) -> Mapping[str, Any]:
    try:
        data = path.read_bytes()
    except (OSError, ValueError):
        raise RouteConfigError("read_route_missing", "Task read route configuration is unavailable.")
    try:
        if tomllib is not None:
            parsed = tomllib.loads(data.decode("utf-8"))
        else:
            parsed = _loads_toml_compat(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise RouteConfigError("invalid_read_route", "Task read route configuration is invalid.")
    if not isinstance(parsed, dict):
        raise RouteConfigError("invalid_read_route", "Task read route configuration is invalid.")
    return parsed


def _required_string(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise RouteConfigError("invalid_read_route", "Task read route configuration is invalid.")
    return value


def _require_exact_fields(
    mapping: Mapping[str, Any],
    *,
    required: set[str],
    optional: set[str] = frozenset(),
) -> None:
    if set(mapping) - required - optional or required - set(mapping):
        raise RouteConfigError("invalid_read_route", "Task route configuration fields are invalid.")


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _resolve_path(path: Path) -> Path:
    try:
        return path.resolve()
    except (OSError, RuntimeError):
        raise RouteConfigError("invalid_read_route", "Task read route path is invalid.")


def _validate_adapter_tool(
    tool_name: str,
    *,
    adapter_key: str,
    capability: str,
) -> None:
    match = _ADAPTER_TOOL_RE.fullmatch(tool_name)
    if match is None or match.group(2) != capability:
        raise RouteConfigError(
            "invalid_read_route",
            "Task route tool capability is invalid.",
        )
    if match.group(1) != adapter_key:
        raise RouteConfigError(
            "invalid_read_route",
            "Task route tools must share the configured adapter namespace.",
        )


def _load_v2_route(
    path: Path,
    document: Mapping[str, Any],
    backend_key: Optional[str],
    destination_ref: str,
) -> ResolvedTaskReadRoute:
    _require_exact_fields(
        document,
        required={"contract_version", "default_backend", "backends"},
    )
    selected_backend = backend_key or document.get("default_backend")
    if not isinstance(selected_backend, str) or not selected_backend:
        raise RouteConfigError("read_route_not_found", "No task read route matches the request.")
    backends = document.get("backends")
    backend = backends.get(selected_backend) if isinstance(backends, dict) else None
    if not isinstance(backend, dict):
        raise RouteConfigError("read_route_not_found", "No task read route matches the request.")
    _require_exact_fields(
        backend,
        required={
            "adapter_key",
            "query_tool",
            "preflight_tool",
            "apply_tool",
            "destinations",
        },
        optional={"read_root", "source_path"},
    )

    destinations = backend.get("destinations")
    if not isinstance(destinations, dict):
        raise RouteConfigError("invalid_read_route", "Task read route destinations are invalid.")
    for destination in destinations.values():
        if not isinstance(destination, dict):
            raise RouteConfigError("invalid_read_route", "Task read route destinations are invalid.")
        _require_exact_fields(
            destination,
            required={"public_ref", "destination_label"},
            optional={"content_target_ref"},
        )
        _required_string(destination, "public_ref")
        _required_string(destination, "destination_label")
        if "content_target_ref" in destination:
            _required_string(destination, "content_target_ref")
    public_refs = [
        item.get("public_ref")
        for item in destinations.values()
        if isinstance(item, dict) and isinstance(item.get("public_ref"), str)
    ]
    if len(public_refs) != len(set(public_refs)):
        raise RouteConfigError("invalid_read_route", "Task read route destinations are ambiguous.")
    matching_destinations = [
        item
        for item in destinations.values()
        if isinstance(item, dict) and item.get("public_ref") == destination_ref
    ]
    if not matching_destinations:
        raise RouteConfigError("read_route_not_found", "No task read route matches the request.")
    destination = matching_destinations[0]

    adapter_key = _required_string(backend, "adapter_key")
    query_tool = _required_string(backend, "query_tool")
    preflight_tool = _required_string(backend, "preflight_tool")
    apply_tool = _required_string(backend, "apply_tool")
    _validate_adapter_tool(
        query_tool,
        adapter_key=adapter_key,
        capability="query",
    )
    _validate_adapter_tool(
        preflight_tool,
        adapter_key=adapter_key,
        capability="preflight",
    )
    _validate_adapter_tool(
        apply_tool,
        adapter_key=adapter_key,
        capability="apply",
    )
    kind = "local_json" if adapter_key == "local_json" else "external"
    read_root = None
    source_path = None
    if kind == "local_json":
        config_dir = _resolve_path(path).parent
        read_root = _resolve_path(config_dir / _required_string(backend, "read_root"))
        source_path = _resolve_path(read_root / _required_string(backend, "source_path"))
        if not _within(source_path, read_root):
            raise RouteConfigError("invalid_read_route", "Local snapshot source is outside its read root.")
    return ResolvedTaskReadRoute(
        backend_key=selected_backend,
        adapter_key=adapter_key,
        kind=kind,
        destination_ref=destination_ref,
        destination_label=_required_string(destination, "destination_label"),
        query_tool=query_tool,
        preflight_tool=preflight_tool,
        apply_tool=apply_tool,
        content_target_ref=destination.get("content_target_ref"),
        read_root=read_root,
        source_path=source_path,
    )


def load_read_route(
    path: Path,
    backend_key: Optional[str],
    destination_ref: str,
) -> ResolvedTaskReadRoute:
    path = Path(path)
    document = _load_document(path)
    if document.get("contract_version") != ROUTE_CONTRACT_VERSION:
        raise RouteConfigError("read_route_contract_mismatch", "Task read route contract version is unsupported.")
    return _load_v2_route(path, document, backend_key, destination_ref)
