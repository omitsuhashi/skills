#!/usr/bin/env python3
"""Exercise real Hermes registration and approval-bound fake Adapter dispatch."""

from __future__ import annotations

import importlib.util
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
INNER_ENV = "TASK_MANAGEMENT_HERMES_WRITE_SMOKE_INNER"
ADAPTER_TOOLS = (
    "task_adapter__github_projects__task_preflight",
    "task_adapter__github_projects__task_apply",
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


def _load_plugin():
    spec = importlib.util.spec_from_file_location(
        "task_management_plugin_write_smoke",
        PLUGIN_ROOT / "__init__.py",
        submodule_search_locations=[str(PLUGIN_ROOT)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load task-management plugin")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _operation():
    return {
        "adapter_contract_version": 2,
        "operation_type": "task.create",
        "backend_key": "remote_tasks",
        "destination_ref": "tasks:default",
        "task_ref": None,
        "payload": {
            "task": {
                "title": "Smoke test write facade",
                "body": "Verify approval-bound fake Adapter dispatch.",
                "work_unit_id": "portfolio-os",
                "work_unit_name": "Portfolio OS",
                "task_type": "implementation",
                "due_date": None,
                "urgency": "normal",
                "importance": "high",
                "automation_mode": "assistive",
                "approval_required": True,
                "source_ref": {
                    "kind": "test",
                    "ref": "source:smoke",
                    "label": "Write smoke fixture",
                },
                "fields": {"review_notes": []},
            }
        },
    }


def main() -> int:
    _run_with_hermes_python_if_needed()
    if not HERMES_ROOT.is_dir():
        raise RuntimeError("Hermes Agent source was not found")
    sys.path.insert(0, str(HERMES_ROOT))

    with tempfile.TemporaryDirectory(prefix="task-management-hermes-write-smoke-") as tmp:
        temp_root = Path(tmp)
        hermes_home = temp_root / "hermes-profile"
        hermes_home.mkdir()
        routes = temp_root / "routes.toml"
        routes.write_text(
            '''contract_version = 2
default_backend = "remote_tasks"
[backends.remote_tasks]
adapter_key = "github_projects"
query_tool = "task_adapter__github_projects__task_query"
preflight_tool = "task_adapter__github_projects__task_preflight"
apply_tool = "task_adapter__github_projects__task_apply"
[backends.remote_tasks.destinations.default]
public_ref = "tasks:default"
destination_label = "Default tasks"
content_target_ref = "task-content:default"
''',
            encoding="utf-8",
        )

        old_home = os.environ.get("HERMES_HOME")
        old_routes = os.environ.get("TASK_MANAGEMENT_ROUTES_FILE")
        os.environ["HERMES_HOME"] = str(hermes_home)
        os.environ["TASK_MANAGEMENT_ROUTES_FILE"] = str(routes)
        registered_names = []
        state = {"apply_calls": 0, "side_effect_revision": 1}
        try:
            from hermes_cli.plugins import PluginContext, PluginManager, PluginManifest
            from tools.registry import registry

            manager = PluginManager()
            context = PluginContext(
                PluginManifest(
                    name="task-management",
                    version="0.4.0",
                    path=str(PLUGIN_ROOT),
                    kind="standalone",
                ),
                manager,
            )

            def fake_preflight(arguments, **_kwargs):
                operation = arguments["operation"]
                effects = [
                    {
                        "effect_type": "content.create",
                        "description": "Create a linked task.",
                    }
                ]
                if state["side_effect_revision"] == 2:
                    effects.append(
                        {
                            "effect_type": "fields.update",
                            "description": "Update reviewed fields.",
                        }
                    )
                return json.dumps(
                    {
                        "adapter_contract_version": 2,
                        "ok": True,
                        "operation_type": operation["operation_type"],
                        "backend_key": operation["backend_key"],
                        "destination_ref": operation["destination_ref"],
                        "readiness": {"ok": True, "checks": []},
                        "expected_side_effects": effects,
                        "requires_human_confirmation": False,
                        "error": None,
                    }
                )

            def fake_apply(arguments, **_kwargs):
                state["apply_calls"] += 1
                operation = arguments["operation"]
                return json.dumps(
                    {
                        "adapter_contract_version": 2,
                        "ok": True,
                        "status": "created",
                        "operation_type": operation["operation_type"],
                        "backend_key": operation["backend_key"],
                        "destination_ref": operation["destination_ref"],
                        "task_ref": {
                            "backend_key": operation["backend_key"],
                            "task_ref": "task:smoke",
                            "task_url": "https://example.invalid/tasks/smoke",
                            "title": "Smoke test write facade",
                        },
                        "retryable": False,
                        "human_action": None,
                        "error": None,
                    }
                )

            for name, handler in zip(ADAPTER_TOOLS, (fake_preflight, fake_apply)):
                context.register_tool(
                    name=name,
                    toolset="fake-task-adapter-write",
                    schema={"name": name, "parameters": {"type": "object"}},
                    handler=handler,
                    requires_env=[],
                    description="Fake adapter tool for task-management write smoke.",
                )
                registered_names.append(name)

            _load_plugin().register(context)
            registered_names.extend(("task_query", "task_preflight", "task_apply"))

            preflight = registry.dispatch(
                "task_preflight",
                {"interface_version": 2, "operation": _operation()},
            )
            preflight = json.loads(preflight) if isinstance(preflight, str) else preflight
            assert preflight.get("ok") is True, preflight
            assert preflight["approval_mode"] == "human_required", preflight
            assert state["apply_calls"] == 0

            confidence = registry.dispatch(
                "task_apply",
                {
                    "interface_version": 2,
                    "approval_preview": preflight["approval_preview"],
                    "approval_receipt": {
                        "receipt_version": 1,
                        "decision": "confidence_authorized",
                        "operation_digest": preflight["approval_digest"],
                    },
                },
            )
            confidence = json.loads(confidence) if isinstance(confidence, str) else confidence
            assert confidence["error"]["code"] == "approval_required", confidence
            assert state["apply_calls"] == 0

            approved = registry.dispatch(
                "task_apply",
                {
                    "interface_version": 2,
                    "approval_preview": preflight["approval_preview"],
                    "approval_receipt": {
                        "receipt_version": 1,
                        "decision": "approved",
                        "operation_digest": preflight["approval_digest"],
                    },
                },
            )
            approved = json.loads(approved) if isinstance(approved, str) else approved
            assert approved["ok"] is True, approved
            assert approved["status"] == "created", approved
            assert state["apply_calls"] == 1

            fresh = registry.dispatch(
                "task_preflight",
                {"interface_version": 2, "operation": _operation()},
            )
            fresh = json.loads(fresh) if isinstance(fresh, str) else fresh
            state["side_effect_revision"] = 2
            mismatch = registry.dispatch(
                "task_apply",
                {
                    "interface_version": 2,
                    "approval_preview": fresh["approval_preview"],
                    "approval_receipt": {
                        "receipt_version": 1,
                        "decision": "approved",
                        "operation_digest": fresh["approval_digest"],
                    },
                },
            )
            mismatch = json.loads(mismatch) if isinstance(mismatch, str) else mismatch
            assert mismatch["error"]["code"] == "approval_mismatch", mismatch
            assert state["apply_calls"] == 1
        finally:
            if "registry" in locals():
                for name in reversed(registered_names):
                    registry.deregister(name)
            if old_home is None:
                os.environ.pop("HERMES_HOME", None)
            else:
                os.environ["HERMES_HOME"] = old_home
            if old_routes is None:
                os.environ.pop("TASK_MANAGEMENT_ROUTES_FILE", None)
            else:
                os.environ["TASK_MANAGEMENT_ROUTES_FILE"] = old_routes

    print("OK: Hermes write facade enforced human approval, applied once, and rejected drift")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
