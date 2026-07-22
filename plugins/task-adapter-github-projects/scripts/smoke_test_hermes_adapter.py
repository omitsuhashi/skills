#!/usr/bin/env python3
"""Exercise adapter apply through real Hermes PluginContext fake MCP dispatch."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HERMES_ROOT = Path(
    os.environ.get("HERMES_AGENT_ROOT", str(Path.home() / ".hermes" / "hermes-agent"))
)
INNER_ENV = "TASK_ADAPTER_GITHUB_PROJECTS_HERMES_SMOKE_INNER"
FAKE_TOOLS = (
    "mcp__github__issue_write",
    "mcp__github__projects_write",
    "mcp__github__projects_get",
)


def _run_with_hermes_python_if_needed() -> None:
    if os.environ.get(INNER_ENV) == "1" or sys.version_info >= (3, 10):
        return
    hermes_python = HERMES_ROOT / "venv" / "bin" / "python"
    if not hermes_python.is_file():
        raise RuntimeError("Hermes Python runtime was not found")
    environment = dict(os.environ)
    environment[INNER_ENV] = "1"
    completed = subprocess.run(
        [str(hermes_python), str(Path(__file__).resolve())],
        env=environment,
        check=False,
    )
    raise SystemExit(completed.returncode)


def _public_success(payload):
    return json.dumps({"result": json.dumps(payload, ensure_ascii=False)})


def main() -> int:
    _run_with_hermes_python_if_needed()
    if not HERMES_ROOT.is_dir():
        raise RuntimeError("Hermes Agent source was not found")
    sys.path[:0] = [str(PLUGIN_ROOT), str(HERMES_ROOT)]

    from task_adapter_github_projects.adapter import GithubProjectsAdapter
    from task_adapter_github_projects.config import load_config
    from task_adapter_github_projects.contracts import validate_task_write_result

    calls = []

    def handler_for(tool_name):
        def handler(arguments, **_kwargs):
            calls.append((tool_name, arguments))
            method = arguments["method"]
            if method == "create":
                return _public_success(
                    {
                        "number": 42,
                        "title": "Implement write contracts",
                        "html_url": (
                            "https://github.com/example-owner/"
                            "example-repository/issues/42"
                        ),
                    }
                )
            if method == "add_project_item":
                return _public_success({"id": "PVTI_private", "item_id": 8101})
            if method == "update_project_item":
                return _public_success({"id": 8101})
            if method == "get_project_item":
                return _public_success(
                    {
                        "id": "PVTI_private",
                        "content_type": "Issue",
                        "content": {
                            "number": 42,
                            "title": "Implement write contracts",
                            "html_url": (
                                "https://github.com/example-owner/"
                                "example-repository/issues/42"
                            ),
                            "repository": "example-owner/example-repository",
                        },
                    }
                )
            raise AssertionError(f"Unexpected fake MCP method: {method}")

        return handler

    with tempfile.TemporaryDirectory(prefix="github-adapter-hermes-smoke-") as tmp:
        old_home = os.environ.get("HERMES_HOME")
        os.environ["HERMES_HOME"] = tmp
        try:
            from hermes_cli.plugins import PluginContext, PluginManager, PluginManifest
            from tools.registry import registry

            context = PluginContext(
                PluginManifest(
                    name="task-adapter-github-projects-smoke",
                    version="0.1.0",
                    path=str(PLUGIN_ROOT),
                    kind="standalone",
                ),
                PluginManager(),
            )
            for tool_name in FAKE_TOOLS:
                if registry.get_entry(tool_name) is not None:
                    raise RuntimeError(f"Smoke tool is already registered: {tool_name}")
                context.register_tool(
                    name=tool_name,
                    toolset="mcp-github-smoke",
                    schema={
                        "name": tool_name,
                        "description": "Hermetic fake GitHub MCP tool.",
                        "inputSchema": {"type": "object"},
                    },
                    handler=handler_for(tool_name),
                    description="Hermetic fake GitHub MCP tool.",
                )

            operation = json.loads(
                (
                    PLUGIN_ROOT
                    / "tests"
                    / "fixtures"
                    / "adapter-v2"
                    / "accept"
                    / "operation-create.json"
                ).read_text(encoding="utf-8")
            )
            operation["destination_ref"] = "tasks:portfolio-os"
            result = GithubProjectsAdapter(
                config=load_config(
                    PLUGIN_ROOT / "config" / "github-projects.example.toml"
                ),
                dispatch=context.dispatch_tool,
            ).apply(
                {
                    "adapter_contract_version": 2,
                    "operation": operation,
                    "destination_label": "Portfolio OS Tasks",
                    "content_target_ref": "task-content:portfolio-os",
                    "operation_digest": "sha256:" + "e" * 64,
                }
            )

            assert validate_task_write_result(result) == result
            assert result["status"] == "created"
            assert [arguments["method"] for _tool, arguments in calls] == [
                "create",
                "add_project_item",
                *("update_project_item" for _index in range(9)),
                "get_project_item",
            ]
            assert all(registry.get_entry(name) is not None for name in FAKE_TOOLS)
        finally:
            if "registry" in locals():
                for tool_name in FAKE_TOOLS:
                    registry.deregister(tool_name)
            if old_home is None:
                os.environ.pop("HERMES_HOME", None)
            else:
                os.environ["HERMES_HOME"] = old_home

    print("OK: Hermes PluginContext fake MCP dispatch created and read back 1 task")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
