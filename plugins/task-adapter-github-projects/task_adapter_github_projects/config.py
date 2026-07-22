"""Strict host-owned GitHub Projects adapter configuration."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

try:  # Python 3.11+
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - exercised by the Python 3.9 runtime
    tomllib = None

from .safety import (
    SafetyValidationError,
    validate_credential_free_config,
    validate_host_attestation,
)


CONFIG_FILE_ENV = "TASK_ADAPTER_GITHUB_PROJECTS_CONFIG_FILE"
CONFIG_CONTRACT_VERSION = 1
MCP_TOOL_ALLOWLIST = {
    "projects_list": "mcp__github__projects_list",
    "projects_get": "mcp__github__projects_get",
    "projects_write": "mcp__github__projects_write",
    "issue_write": "mcp__github__issue_write",
    "add_issue_comment": "mcp__github__add_issue_comment",
}
CANONICAL_FIELD_KEYS = {
    "work_unit_id",
    "work_unit_name",
    "task_type",
    "due_date",
    "urgency",
    "importance",
    "automation_mode",
    "approval_required",
    "source_label",
    "source_url",
}
_TOP_LEVEL_FIELDS = {
    "contract_version",
    "mcp_tools",
    "host_attestation",
    "destinations",
    "content_targets",
    "field_mappings",
}
_FIELD_TYPES = {"text", "date", "single_select"}
_OPTION_FIELDS = {
    "task_type": {
        "implementation",
        "review",
        "research",
        "decision",
        "coordination",
        "maintenance",
        "inbox_triage",
    },
    "urgency": {"low", "normal", "high", "blocked"},
    "importance": {"low", "normal", "high", "critical"},
    "automation_mode": {"manual_only", "assistive", "trusted_after_approval"},
    "approval_required": {"true", "false"},
}
_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_OPAQUE_DESTINATION_RE = re.compile(r"^tasks:[a-z0-9][a-z0-9_-]*$")
_OPAQUE_CONTENT_TARGET_RE = re.compile(r"^task-content:[a-z0-9][a-z0-9_-]*$")
_GITHUB_NAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,99})$")


class ConfigError(ValueError):
    """Fail-closed configuration error with a stable code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class DestinationConfig:
    destination_ref: str
    owner: str
    project_number: int


@dataclass(frozen=True)
class ContentTargetConfig:
    content_target_ref: str
    owner: str
    repository: str


@dataclass(frozen=True)
class FieldMapping:
    field_name: str
    field_type: str
    required: bool
    options: Mapping[str, str]


@dataclass(frozen=True)
class GithubProjectsConfig:
    mcp_tools: Mapping[str, str]
    host_attestation: Mapping[str, Any]
    destinations: Mapping[str, DestinationConfig]
    content_targets: Mapping[str, ContentTargetConfig]
    field_mappings: Mapping[str, FieldMapping]

    def resolve_destination(self, destination_ref: str) -> DestinationConfig:
        try:
            return self.destinations[destination_ref]
        except (KeyError, TypeError):
            raise ConfigError(
                "destination_unresolved",
                "The opaque GitHub Projects destination is not configured.",
            )

    def resolve_content_target(self, content_target_ref: str) -> ContentTargetConfig:
        try:
            return self.content_targets[content_target_ref]
        except (KeyError, TypeError):
            raise ConfigError(
                "destination_unresolved",
                "The opaque GitHub Issue content target is not configured.",
            )


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    if value.isdigit():
        return int(value)
    raise ValueError("unsupported TOML value")


def _loads_toml_compat(text: str) -> Dict[str, Any]:
    """Parse the deliberately small host-config TOML subset on Python 3.9."""
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
        data = Path(path).read_bytes()
        if tomllib is not None:
            document = tomllib.loads(data.decode("utf-8"))
        else:
            document = _loads_toml_compat(data.decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        raise ConfigError("invalid_config", "GitHub Projects adapter config is invalid.")
    if not isinstance(document, dict):
        raise ConfigError("invalid_config", "GitHub Projects adapter config is invalid.")
    return document


def _exact_mapping(value: Any, fields: set, *, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ConfigError("invalid_config", f"{label} must use the exact approved fields.")
    return value


def _required_string(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError("invalid_config", f"{label} must be a non-empty string.")
    return value


def _github_name(value: Any, *, label: str) -> str:
    value = _required_string(value, label=label)
    if _GITHUB_NAME_RE.fullmatch(value) is None:
        raise ConfigError("invalid_config", f"{label} is invalid.")
    return value


def _load_destinations(value: Any) -> Dict[str, DestinationConfig]:
    if not isinstance(value, dict) or not value:
        raise ConfigError("invalid_config", "At least one destination is required.")
    result: Dict[str, DestinationConfig] = {}
    for alias, raw in value.items():
        raw = _exact_mapping(
            raw,
            {"destination_ref", "owner", "project_number"},
            label=f"destinations.{alias}",
        )
        destination_ref = _required_string(
            raw["destination_ref"], label="destination_ref"
        )
        if _OPAQUE_DESTINATION_RE.fullmatch(destination_ref) is None:
            raise ConfigError("invalid_config", "destination_ref must be opaque.")
        if destination_ref in result:
            raise ConfigError("invalid_config", "destination_ref values must be unique.")
        project_number = raw["project_number"]
        if type(project_number) is not int or project_number <= 0:
            raise ConfigError("invalid_config", "project_number must be a positive integer.")
        result[destination_ref] = DestinationConfig(
            destination_ref=destination_ref,
            owner=_github_name(raw["owner"], label="destination owner"),
            project_number=project_number,
        )
    return result


def _load_content_targets(value: Any) -> Dict[str, ContentTargetConfig]:
    if not isinstance(value, dict) or not value:
        raise ConfigError("invalid_config", "At least one content target is required.")
    result: Dict[str, ContentTargetConfig] = {}
    for alias, raw in value.items():
        raw = _exact_mapping(
            raw,
            {"content_target_ref", "owner", "repository"},
            label=f"content_targets.{alias}",
        )
        content_target_ref = _required_string(
            raw["content_target_ref"], label="content_target_ref"
        )
        if _OPAQUE_CONTENT_TARGET_RE.fullmatch(content_target_ref) is None:
            raise ConfigError("invalid_config", "content_target_ref must be opaque.")
        if content_target_ref in result:
            raise ConfigError("invalid_config", "content_target_ref values must be unique.")
        result[content_target_ref] = ContentTargetConfig(
            content_target_ref=content_target_ref,
            owner=_github_name(raw["owner"], label="content target owner"),
            repository=_github_name(raw["repository"], label="repository"),
        )
    return result


def _load_field_mappings(value: Any) -> Dict[str, FieldMapping]:
    if not isinstance(value, dict) or set(value) != CANONICAL_FIELD_KEYS:
        raise ConfigError("invalid_config", "Canonical field mappings are incomplete.")
    result = {}
    for canonical_field, raw in value.items():
        if not isinstance(raw, dict):
            raise ConfigError("invalid_config", "Field mapping must be an object.")
        expected_fields = {"field_name", "field_type", "required"}
        if canonical_field in _OPTION_FIELDS:
            expected_fields.add("options")
        raw = _exact_mapping(raw, expected_fields, label=canonical_field)
        field_type = _required_string(raw["field_type"], label="field_type")
        if field_type not in _FIELD_TYPES:
            raise ConfigError("invalid_config", "Field mapping type is unsupported.")
        required = raw["required"]
        if type(required) is not bool:
            raise ConfigError("invalid_config", "Field mapping required must be boolean.")
        options = raw.get("options", {})
        if canonical_field in _OPTION_FIELDS:
            if (
                not isinstance(options, dict)
                or set(options) != _OPTION_FIELDS[canonical_field]
                or not all(
                    isinstance(item, str) and bool(item.strip())
                    for item in options.values()
                )
            ):
                raise ConfigError("invalid_config", "Field mapping options are incomplete.")
            if field_type != "single_select":
                raise ConfigError("invalid_config", "Mapped options require single_select.")
        result[canonical_field] = FieldMapping(
            field_name=_required_string(raw["field_name"], label="field_name"),
            field_type=field_type,
            required=required,
            options=dict(options),
        )
    return result


def load_config(path: Path) -> GithubProjectsConfig:
    """Load and validate one credential-free host configuration."""
    document = _load_document(Path(path))
    try:
        validate_credential_free_config(document)
    except SafetyValidationError as error:
        raise ConfigError(error.code, str(error))
    if set(document) != _TOP_LEVEL_FIELDS:
        raise ConfigError("invalid_config", "Host config must use the exact top-level fields.")
    if document["contract_version"] != CONFIG_CONTRACT_VERSION:
        raise ConfigError("config_contract_mismatch", "Host config version is unsupported.")
    mcp_tools = document["mcp_tools"]
    if not isinstance(mcp_tools, dict) or mcp_tools != MCP_TOOL_ALLOWLIST:
        raise ConfigError(
            "invalid_mcp_tool_allowlist",
            "MCP tools must exactly match the approved GitHub allowlist.",
        )
    try:
        host_attestation = validate_host_attestation(document["host_attestation"])
    except SafetyValidationError as error:
        raise ConfigError(error.code, str(error))
    return GithubProjectsConfig(
        mcp_tools=dict(mcp_tools),
        host_attestation=host_attestation,
        destinations=_load_destinations(document["destinations"]),
        content_targets=_load_content_targets(document["content_targets"]),
        field_mappings=_load_field_mappings(document["field_mappings"]),
    )


def load_config_from_env(environ: Optional[Mapping[str, str]] = None) -> GithubProjectsConfig:
    """Load the host-owned config path without accepting a caller-supplied path."""
    source = os.environ if environ is None else environ
    path = source.get(CONFIG_FILE_ENV)
    if not path:
        raise ConfigError("config_missing", "GitHub Projects adapter config is unavailable.")
    return load_config(Path(path))
