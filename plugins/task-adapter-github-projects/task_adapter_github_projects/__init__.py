"""GitHub Projects task adapter contract and executable runtime registration."""

import json
from typing import Any

from .adapter import GithubProjectsAdapter
from .config import CONFIG_FILE_ENV, ConfigError, load_config_from_env
from .contracts import ADAPTER_CONTRACT_VERSION, ContractValidationError, validate_contract
from .safety import SafetyValidationError, validate_adapter_arguments


QUERY_TOOL = "task_adapter__github_projects__task_query"
PREFLIGHT_TOOL = "task_adapter__github_projects__task_preflight"
APPLY_TOOL = "task_adapter__github_projects__task_apply"
READ_TOOLSET = "task-adapter-github-projects-read"
WRITE_TOOLSET = "task-adapter-github-projects-write"
TOOLSETS = {
    QUERY_TOOL: READ_TOOLSET,
    PREFLIGHT_TOOL: WRITE_TOOLSET,
    APPLY_TOOL: WRITE_TOOLSET,
}
_DESCRIPTIONS = {
    QUERY_TOOL: "Query normalized GitHub Projects tasks through the configured adapter.",
    PREFLIGHT_TOOL: "Validate GitHub Projects adapter readiness without write side effects.",
    APPLY_TOOL: "Apply one approval-bound task operation through task-management.",
}


def _blocked(tool_name: str, code: str, message: str) -> str:
    return json.dumps(
        {
            "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
            "ok": False,
            "status": "blocked",
            "tool": tool_name,
            "error": {
                "error_type": "setup_blocker",
                "code": code,
                "message": message,
                "stage": "adapter_registration",
            },
        },
        ensure_ascii=False,
    )


_DESTINATION_FIELDS = {
    "backend_key",
    "destination_ref",
    "destination_label",
    "content_target_ref",
}


def _destination(arguments: Any) -> dict:
    validate_adapter_arguments(arguments)
    if not isinstance(arguments, dict):
        raise ValueError("Adapter request must be an object.")
    destination = arguments.get("destination")
    operation = arguments.get("operation")
    if (
        not isinstance(destination, dict)
        or set(destination) != _DESTINATION_FIELDS
        or not isinstance(operation, dict)
        or destination["backend_key"] != operation.get("backend_key")
        or destination["destination_ref"] != operation.get("destination_ref")
    ):
        raise ValueError("Adapter destination binding is invalid.")
    return destination


def _preflight_request(arguments: Any) -> dict:
    if not isinstance(arguments, dict) or set(arguments) != {
        "adapter_contract_version",
        "operation",
        "destination",
        "required_capability",
    }:
        raise ValueError("Adapter preflight envelope is invalid.")
    destination = _destination(arguments)
    return {
        "adapter_contract_version": arguments["adapter_contract_version"],
        "operation": arguments["operation"],
        "destination_label": destination["destination_label"],
        "content_target_ref": destination["content_target_ref"],
        "required_capability": arguments["required_capability"],
    }


def _apply_request(arguments: Any) -> dict:
    if not isinstance(arguments, dict) or set(arguments) != {
        "adapter_contract_version",
        "operation",
        "destination",
        "expected_side_effects",
        "operation_digest",
    }:
        raise ValueError("Adapter apply envelope is invalid.")
    destination = _destination(arguments)
    expected_side_effects = arguments["expected_side_effects"]
    if not isinstance(expected_side_effects, list) or not expected_side_effects:
        raise ValueError("Adapter expected side effects are invalid.")
    return {
        "adapter_contract_version": arguments["adapter_contract_version"],
        "operation": arguments["operation"],
        "destination_label": destination["destination_label"],
        "content_target_ref": destination["content_target_ref"],
        "operation_digest": arguments["operation_digest"],
    }


def _query_request(arguments: Any) -> dict:
    validate_adapter_arguments(arguments)
    if not isinstance(arguments, dict) or set(arguments) != {
        "adapter_contract_version",
        "backend_key",
        "destination_ref",
        "query",
    }:
        raise ValueError("Adapter query envelope is invalid.")
    query = arguments["query"]
    if not isinstance(query, dict):
        raise ValueError("Adapter query is invalid.")
    query = dict(query)
    nested_backend_key = query.pop("backend_key", arguments["backend_key"])
    if nested_backend_key != arguments["backend_key"]:
        raise ValueError("Adapter query backend binding is invalid.")
    return {**arguments, "query": query}


def _write_wire_result(result: dict) -> dict:
    """Map adapter execution detail to the stable task-management wire taxonomy."""
    value = dict(result)
    error = value.get("error")
    if value.get("status") == "partial":
        value["human_action"] = "Inspect the linked task before retrying field updates."
        value["error"] = {
            "error_type": "partial_failure",
            "code": "partial_update_failure",
            "message": "Task content was created but one or more fields were not updated.",
            "stage": error.get("stage", "fields_update") if isinstance(error, dict) else "fields_update",
        }
    elif value.get("status") == "failed" and value.get("retryable") is True:
        value["human_action"] = "Retry after the backend service becomes available."
    elif value.get("status") == "failed":
        value["human_action"] = "Confirm whether the linked task was created before retrying."
        value["error"] = {
            "error_type": "provider_failure",
            "code": "unknown_write_outcome",
            "message": "The backend did not confirm whether the task write completed.",
            "stage": error.get("stage", "write") if isinstance(error, dict) else "write",
        }
    return {"adapter_contract_version": ADAPTER_CONTRACT_VERSION, **value}


def _runtime_handler(ctx: Any, tool_name: str):
    def handler(arguments: Any, **kwargs: Any) -> str:
        try:
            validate_adapter_arguments(arguments)
            config = load_config_from_env()
            adapter = GithubProjectsAdapter(
                config=config,
                dispatch=lambda name, value: ctx.dispatch_tool(name, value, **kwargs),
            )
            if tool_name == QUERY_TOOL:
                result = adapter.query(_query_request(arguments))
            elif tool_name == PREFLIGHT_TOOL:
                result = adapter.preflight(_preflight_request(arguments))
            else:
                result = adapter.apply(_apply_request(arguments))
                result = _write_wire_result(result)
        except SafetyValidationError as error:
            return _blocked(tool_name, error.code, str(error))
        except ConfigError as error:
            return _blocked(tool_name, error.code, str(error))
        except (ContractValidationError, ValueError):
            return _blocked(
                tool_name,
                "invalid_adapter_request",
                "The adapter request did not match the public contract.",
            )
        return json.dumps(result, ensure_ascii=False)

    return handler


def register_adapter_tools(ctx: Any) -> None:
    """Register the exact adapter trio behind host-owned configuration."""
    for tool_name, toolset in TOOLSETS.items():
        ctx.register_tool(
            name=tool_name,
            toolset=toolset,
            schema={
                "name": tool_name,
                "description": _DESCRIPTIONS[tool_name],
                "inputSchema": {
                    "type": "object",
                    "additionalProperties": True,
                },
            },
            handler=_runtime_handler(ctx, tool_name),
            requires_env=[CONFIG_FILE_ENV],
            description=_DESCRIPTIONS[tool_name],
        )

__all__ = [
    "ADAPTER_CONTRACT_VERSION",
    "APPLY_TOOL",
    "ContractValidationError",
    "PREFLIGHT_TOOL",
    "QUERY_TOOL",
    "TOOLSETS",
    "register_adapter_tools",
    "validate_contract",
]
