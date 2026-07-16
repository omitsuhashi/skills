#!/usr/bin/env python3
"""Exercise plugin load -> Hermes registry -> local route -> normalized result."""

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
INNER_ENV = "TASK_MANAGEMENT_HERMES_SMOKE_INNER"


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
        "task_management_plugin_smoke",
        PLUGIN_ROOT / "__init__.py",
        submodule_search_locations=[str(PLUGIN_ROOT)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load task-management plugin")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    _run_with_hermes_python_if_needed()
    if not HERMES_ROOT.is_dir():
        raise RuntimeError("Hermes Agent source was not found")
    sys.path.insert(0, str(HERMES_ROOT))

    fixture = PLUGIN_ROOT / "tests" / "fixtures" / "local_tasks.json"
    with tempfile.TemporaryDirectory(prefix="task-management-hermes-smoke-") as tmp:
        temp_root = Path(tmp)
        hermes_home = temp_root / "hermes-profile"
        hermes_home.mkdir()
        source = temp_root / "tasks.json"
        source.write_text(fixture.read_text(encoding="utf-8"), encoding="utf-8")
        routes = temp_root / "routes.toml"
        routes.write_text(
            f'''contract_version = 1
default_backend = "local_tasks"
[backends.local_tasks]
kind = "local_json"
capability = "task_read"
read_root = "{temp_root}"
source_path = "tasks.json"
[backends.local_tasks.destinations.default]
public_ref = "tasks:default"
provider_ref = "tasks:default"
''',
            encoding="utf-8",
        )

        old_home = os.environ.get("HERMES_HOME")
        old_routes = os.environ.get("TASK_MANAGEMENT_READ_ROUTES_FILE")
        os.environ["HERMES_HOME"] = str(hermes_home)
        os.environ["TASK_MANAGEMENT_READ_ROUTES_FILE"] = str(routes)
        try:
            from hermes_cli.plugins import PluginContext, PluginManager, PluginManifest
            from tools.registry import registry

            if registry.get_entry("task_query") is not None:
                raise RuntimeError("task_query is already registered; smoke isolation failed")
            manager = PluginManager()
            context = PluginContext(
                PluginManifest(
                    name="task-management",
                    version="0.3.0",
                    path=str(PLUGIN_ROOT),
                    kind="standalone",
                ),
                manager,
            )
            _load_plugin().register(context)
            raw_result = registry.dispatch(
                "task_query",
                {"query": {"status": "ready", "limit": 20}, "destination_ref": "tasks:default"},
            )
            result = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
            assert result["ok"] is True
            assert result["backend_key"] == "local_tasks"
            assert [item["title"] for item in result["task_snapshots"]] == [
                "Prepare quarterly plan"
            ]
            assert registry.get_entry("task_query").toolset == "task-management-read"
        finally:
            if "registry" in locals():
                registry.deregister("task_query")
            if old_home is None:
                os.environ.pop("HERMES_HOME", None)
            else:
                os.environ["HERMES_HOME"] = old_home
            if old_routes is None:
                os.environ.pop("TASK_MANAGEMENT_READ_ROUTES_FILE", None)
            else:
                os.environ["TASK_MANAGEMENT_READ_ROUTES_FILE"] = old_routes

    print("OK: Hermes task_query resolved local_tasks and returned 1 normalized snapshot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
