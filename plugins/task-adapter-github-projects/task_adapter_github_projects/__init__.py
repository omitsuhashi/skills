"""GitHub Projects task adapter contract and fail-closed runtime registration."""

import json
from typing import Any

from .config import CONFIG_FILE_ENV
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


def _placeholder_handler(tool_name: str):
    def handler(arguments: Any, **_kwargs: Any) -> str:
        try:
            validate_adapter_arguments(arguments)
        except SafetyValidationError as error:
            return _blocked(tool_name, error.code, str(error))
        return _blocked(
            tool_name,
            "adapter_not_implemented",
            "Provider orchestration is unavailable until the executable adapter is installed.",
        )

    return handler


def register_adapter_tools(ctx: Any) -> None:
    """Register exact adapter tools; POTASK-016 handlers intentionally do not dispatch."""
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
            handler=_placeholder_handler(tool_name),
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
