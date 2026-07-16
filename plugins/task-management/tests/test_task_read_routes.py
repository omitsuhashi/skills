import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

import task_management.provider_adapters.external_tool as external_tool
from task_management.provider_adapters.external_tool import ExternalToolAdapter
from task_management.provider_adapters.local_json import LocalJsonAdapter
from task_management.route_config import (
    ResolvedTaskReadRequest,
    RouteConfigError,
    load_read_route,
)


FIXTURE = PLUGIN_ROOT / "tests" / "fixtures" / "local_tasks.json"


def route_file(directory, body):
    path = Path(directory) / "routes.toml"
    path.write_text(body, encoding="utf-8")
    return path


class RouteConfigTests(unittest.TestCase):
    def test_default_backend_resolves_a_host_owned_local_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "tasks.json"
            source.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
            config = route_file(
                root,
                f'''contract_version = 1
default_backend = "local_tasks"

[backends.local_tasks]
kind = "local_json"
capability = "task_read"
read_root = "{root}"
source_path = "tasks.json"

[backends.local_tasks.destinations.default]
public_ref = "tasks:default"
provider_ref = "tasks:default"
''',
            )

            route = load_read_route(config, None, "tasks:default")

            self.assertEqual("local_tasks", route.backend_key)
            self.assertEqual("local_json", route.kind)
            self.assertEqual(source.resolve(), route.source_path)
            self.assertEqual("tasks:default", route.provider_destination_ref)

    def test_missing_route_file_is_a_typed_setup_error(self):
        with self.assertRaises(RouteConfigError) as raised:
            load_read_route(Path("/definitely/missing/routes.toml"), None, "tasks:default")

        self.assertEqual("read_route_missing", raised.exception.code)

    def test_unknown_destination_fails_before_reading_a_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = route_file(
                tmp,
                '''contract_version = 1
default_backend = "local_tasks"
[backends.local_tasks]
kind = "local_json"
capability = "task_read"
read_root = "."
source_path = "tasks.json"
[backends.local_tasks.destinations.default]
public_ref = "tasks:default"
provider_ref = "tasks:default"
''',
            )

            with self.assertRaises(RouteConfigError) as raised:
                load_read_route(config, None, "tasks:other")

        self.assertEqual("read_route_not_found", raised.exception.code)

    def test_config_rejects_a_source_outside_the_fixed_read_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = route_file(
                tmp,
                '''contract_version = 1
default_backend = "local_tasks"
[backends.local_tasks]
kind = "local_json"
capability = "task_read"
read_root = "data"
source_path = "../tasks.json"
[backends.local_tasks.destinations.default]
public_ref = "tasks:default"
provider_ref = "tasks:default"
''',
            )

            with self.assertRaises(RouteConfigError) as raised:
                load_read_route(config, None, "tasks:default")

        self.assertEqual("invalid_read_route", raised.exception.code)

    def test_duplicate_public_destination_refs_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = route_file(
                tmp,
                '''contract_version = 1
default_backend = "remote"
[backends.remote]
kind = "mcp"
capability = "task_read"
tool_name = "mcp__tasks__task_query"
[backends.remote.destinations.one]
public_ref = "tasks:default"
provider_ref = "provider:one"
[backends.remote.destinations.two]
public_ref = "tasks:default"
provider_ref = "provider:two"
''',
            )

            with self.assertRaises(RouteConfigError) as raised:
                load_read_route(config, None, "tasks:default")

        self.assertEqual("invalid_read_route", raised.exception.code)

    def test_duplicate_unselected_destination_refs_still_invalidate_the_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = route_file(
                tmp,
                '''contract_version = 1
default_backend = "remote"
[backends.remote]
kind = "mcp"
capability = "task_read"
tool_name = "mcp__tasks__task_query"
[backends.remote.destinations.selected]
public_ref = "tasks:selected"
provider_ref = "provider:selected"
[backends.remote.destinations.one]
public_ref = "tasks:duplicate"
provider_ref = "provider:one"
[backends.remote.destinations.two]
public_ref = "tasks:duplicate"
provider_ref = "provider:two"
''',
            )

            with self.assertRaises(RouteConfigError) as raised:
                load_read_route(config, None, "tasks:selected")

        self.assertEqual("invalid_read_route", raised.exception.code)

    def test_route_kind_must_match_the_external_tool_namespace(self):
        for kind, tool_name in (
            ("mcp", "task_adapter__linear__task_query"),
            ("plugin", "mcp__tasks__task_query"),
        ):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                config = route_file(
                    tmp,
                    f'''contract_version = 1
default_backend = "remote"
[backends.remote]
kind = "{kind}"
capability = "task_read"
tool_name = "{tool_name}"
[backends.remote.destinations.default]
public_ref = "tasks:default"
provider_ref = "provider:default"
''',
                )

                with self.assertRaises(RouteConfigError) as raised:
                    load_read_route(config, None, "tasks:default")

                self.assertEqual("invalid_read_route", raised.exception.code)

    def test_symlink_loop_becomes_a_typed_public_route_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            loop = root / "loop"
            try:
                os.symlink("loop", loop)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable")
            config = route_file(
                root,
                '''contract_version = 1
default_backend = "local"
[backends.local]
kind = "local_json"
capability = "task_read"
read_root = "loop"
source_path = "tasks.json"
[backends.local.destinations.default]
public_ref = "tasks:default"
provider_ref = "tasks:default"
''',
            )
            from task_management.read_adapter import query_tasks

            result = query_tasks(
                {"query": {}, "destination_ref": "tasks:default"},
                dispatch=lambda *_args, **_kwargs: self.fail("dispatch must not run"),
                routes_file=str(config),
            )

        self.assertFalse(result["ok"])
        self.assertEqual("invalid_read_route", result["error"]["code"])


class LocalJsonAdapterTests(unittest.TestCase):
    def test_local_snapshot_applies_filters_and_limit(self):
        request = ResolvedTaskReadRequest(
            backend_key="local_tasks",
            destination_ref="tasks:default",
            provider_destination_ref="tasks:default",
            query={"status": "ready", "due_before": "2026-07-17", "limit": 1},
        )
        adapter = LocalJsonAdapter(read_root=FIXTURE.parent, source_path=FIXTURE)

        result = adapter.query(request)

        self.assertEqual(1, result.adapter_contract_version)
        self.assertEqual(1, len(result.items))
        self.assertEqual("Prepare quarterly plan", result.items[0]["title"])

    def test_local_snapshot_contract_version_mismatch_is_typed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.json"
            path.write_text('{"adapter_contract_version": 2, "items": []}', encoding="utf-8")
            request = ResolvedTaskReadRequest("local", "tasks:default", "tasks:default", {})
            adapter = LocalJsonAdapter(read_root=Path(tmp), source_path=path)

            with self.assertRaises(Exception) as raised:
                adapter.query(request)

        self.assertEqual("adapter_contract_mismatch", raised.exception.code)

    def test_source_resolve_failure_is_typed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            loop = root / "loop"
            try:
                os.symlink("loop", loop)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable")

            with self.assertRaises(Exception) as raised:
                LocalJsonAdapter(read_root=root, source_path=loop)

        self.assertEqual(
            "task_source_unreadable",
            getattr(raised.exception, "code", None),
        )


class ExternalToolAdapterTests(unittest.TestCase):
    def request(self):
        return ResolvedTaskReadRequest(
            backend_key="remote_tasks",
            destination_ref="tasks:default",
            provider_destination_ref="provider:project-1",
            query={"status": "ready", "limit": 20},
        )

    def test_mcp_adapter_dispatches_only_the_fixed_route_tool(self):
        calls = []

        def dispatch(tool_name, arguments, **kwargs):
            calls.append((tool_name, arguments, kwargs))
            return {"adapter_contract_version": 1, "items": []}

        result = ExternalToolAdapter(
            tool_name="mcp__task_backend__task_query",
            dispatch=dispatch,
        ).query(self.request(), task_id="task-123")

        self.assertEqual(1, result.adapter_contract_version)
        self.assertEqual(
            [("mcp__task_backend__task_query", {
                "adapter_contract_version": 1,
                "capability": "task_read",
                "destination_ref": "provider:project-1",
                "query": {"status": "ready", "limit": 20},
            }, {"task_id": "task-123"})],
            calls,
        )

    def test_provider_plugin_adapter_name_is_allowed(self):
        calls = []
        adapter = ExternalToolAdapter(
            tool_name="task_adapter__linear__task_query",
            dispatch=lambda name, args, **kwargs: calls.append(name)
            or {"adapter_contract_version": 1, "items": []},
        )

        adapter.query(self.request())

        self.assertEqual(["task_adapter__linear__task_query"], calls)

    def test_write_or_arbitrary_tool_name_is_rejected(self):
        with self.assertRaises(Exception) as raised:
            ExternalToolAdapter(
                tool_name="mcp__github__projects_write",
                dispatch=lambda *_args, **_kwargs: None,
            )

        self.assertEqual("invalid_read_adapter_tool", raised.exception.code)

    def test_external_contract_mismatch_is_typed_without_raw_payload(self):
        adapter = ExternalToolAdapter(
            tool_name="mcp__task_backend__task_query",
            dispatch=lambda *_args, **_kwargs: {
                "adapter_contract_version": 2,
                "items": [],
                "token": "must-not-leak",
            },
        )

        with self.assertRaises(Exception) as raised:
            adapter.query(self.request())

        self.assertEqual("adapter_contract_mismatch", raised.exception.code)
        self.assertNotIn("must-not-leak", str(raised.exception))

    def test_provider_failure_uses_allowlisted_error_taxonomy(self):
        adapter = ExternalToolAdapter(
            tool_name="mcp__task_backend__task_query",
            dispatch=lambda *_args, **_kwargs: {
                "adapter_contract_version": 1,
                "items": [],
                "error": {"code": "auth_missing", "message": "Bearer must-not-leak"},
            },
        )

        with self.assertRaises(Exception) as raised:
            adapter.query(self.request())

        self.assertEqual("read_adapter_auth_missing", raised.exception.code)
        self.assertNotIn("must-not-leak", str(raised.exception))

    def test_external_response_size_is_bounded_for_strings_and_dicts(self):
        responses = (
            json.dumps({"adapter_contract_version": 1, "items": [], "padding": "x" * 100}),
            {"adapter_contract_version": 1, "items": [], "padding": "x" * 100},
        )
        for response in responses:
            with self.subTest(response_type=type(response).__name__), patch.object(
                external_tool, "MAX_EXTERNAL_RESPONSE_BYTES", 64, create=True
            ):
                adapter = ExternalToolAdapter(
                    tool_name="mcp__task_backend__task_query",
                    dispatch=lambda *_args, **_kwargs: response,
                )

                with self.assertRaises(Exception) as raised:
                    adapter.query(self.request())

                self.assertEqual("invalid_adapter_result", raised.exception.code)

    def test_external_item_array_is_bounded(self):
        adapter = ExternalToolAdapter(
            tool_name="mcp__task_backend__task_query",
            dispatch=lambda *_args, **_kwargs: {
                "adapter_contract_version": 1,
                "items": [{} for _ in range(101)],
            },
        )

        with self.assertRaises(Exception) as raised:
            adapter.query(self.request())

        self.assertEqual("invalid_adapter_result", raised.exception.code)


if __name__ == "__main__":
    unittest.main()
