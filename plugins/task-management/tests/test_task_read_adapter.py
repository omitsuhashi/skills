import json
import importlib
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
READ_ADAPTER = PLUGIN_ROOT / "task_management" / "read_adapter.py"
ROUTES_FILE_ENV = "TASK_MANAGEMENT_ROUTES_FILE"


class TaskReadAdapterBehaviorTests(unittest.TestCase):
    def load_adapter(self):
        self.assertTrue(
            READ_ADAPTER.is_file(),
            "task-management needs an executable backend-neutral read adapter",
        )
        sys.path.insert(0, str(PLUGIN_ROOT))
        return importlib.import_module("task_management.read_adapter")

    def valid_snapshot(self):
        return {
            "task_ref": {
                "backend_key": "github_projects_mcp",
                "task_ref": "external_ref",
                "task_url": "https://example.invalid/tasks/1",
                "title": "Prepare quarterly plan",
            },
            "title": "Prepare quarterly plan",
            "body": "Draft and review the quarterly plan.",
            "work_unit_id": "planning",
            "work_unit_name": "Planning",
            "task_type": "coordination",
            "status": "ready",
            "due_date": "2026-07-16",
            "urgency": "high",
            "importance": "high",
            "automation_mode": "assistive",
            "approval_required": False,
            "source_ref": {
                "kind": "task_backend",
                "ref": "external_ref",
                "label": "Portfolio OS Tasks",
            },
            "backend_metadata": {},
        }

    def query_external(self, arguments, *, dispatch, **dispatch_kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            routes = Path(tmp) / "routes.toml"
            routes.write_text(
                '''contract_version = 2
default_backend = "github_projects_mcp"
[backends.github_projects_mcp]
adapter_key = "github_projects"
query_tool = "task_adapter__github_projects__task_query"
preflight_tool = "task_adapter__github_projects__task_preflight"
apply_tool = "task_adapter__github_projects__task_apply"
[backends.github_projects_mcp.destinations.default]
public_ref = "github-projects:portfolio-os-task-board"
destination_label = "Portfolio OS Tasks"
''',
                encoding="utf-8",
            )
            return self.load_adapter().query_tasks(
                arguments,
                dispatch=dispatch,
                routes_file=str(routes),
                **dispatch_kwargs,
            )

    def test_query_dispatches_configured_read_adapter_and_returns_normalized_snapshots(self):
        adapter = self.load_adapter()
        calls = []

        def dispatch(tool_name, arguments, **kwargs):
            calls.append((tool_name, arguments, kwargs))
            return json.dumps(
                {
                    "adapter_contract_version": 2,
                    "items": [
                        {
                            "task_ref": {
                                "backend_key": "github_projects_mcp",
                                "task_ref": "external_ref",
                                "task_url": "https://example.invalid/tasks/1",
                                "title": "Prepare quarterly plan",
                                "node_id": "provider-only-id",
                            },
                            "title": "Prepare quarterly plan",
                            "body": "Draft and review the quarterly plan.",
                            "work_unit_id": "planning",
                            "work_unit_name": "Planning",
                            "task_type": "coordination",
                            "status": "ready",
                            "due_date": "2026-07-16",
                            "urgency": "high",
                            "importance": "high",
                            "automation_mode": "assistive",
                            "approval_required": False,
                            "source_ref": {
                                "kind": "task_backend",
                                "ref": "external_ref",
                                "label": "Portfolio OS Tasks",
                            },
                            "backend_metadata": {
                                "display_link": {
                                    "name": "Open task",
                                    "url": "https://example.invalid/tasks/1",
                                },
                                "provider_payload": {
                                    "field_id": "provider-only-field",
                                },
                            },
                        }
                    ]
                }
            )

        with tempfile.TemporaryDirectory() as tmp:
            routes = Path(tmp) / "routes.toml"
            routes.write_text(
                '''contract_version = 2
default_backend = "github_projects_mcp"
[backends.github_projects_mcp]
adapter_key = "github_projects"
query_tool = "task_adapter__github_projects__task_query"
preflight_tool = "task_adapter__github_projects__task_preflight"
apply_tool = "task_adapter__github_projects__task_apply"
[backends.github_projects_mcp.destinations.default]
public_ref = "github-projects:portfolio-os-task-board"
destination_label = "Portfolio OS Tasks"
''',
                encoding="utf-8",
            )
            result = adapter.query_tasks(
                {
                    "query": {
                        "backend_key": "github_projects_mcp",
                        "work_unit_id": "planning",
                        "status": "ready",
                        "limit": 20,
                    },
                    "destination_ref": "github-projects:portfolio-os-task-board",
                },
                dispatch=dispatch,
                routes_file=str(routes),
                task_id="task-123",
            )

        self.assertEqual(
            [
                (
                    "task_adapter__github_projects__task_query",
                    {
                        "adapter_contract_version": 2,
                        "backend_key": "github_projects_mcp",
                        "query": {
                            "backend_key": "github_projects_mcp",
                            "work_unit_id": "planning",
                            "status": "ready",
                            "limit": 20,
                        },
                        "destination_ref": "github-projects:portfolio-os-task-board",
                    },
                    {"task_id": "task-123"},
                )
            ],
            calls,
        )
        self.assertEqual("TaskSnapshotResult", result["result_type"])
        self.assertTrue(result["ok"])
        self.assertIsNone(result["error"])
        self.assertEqual(1, len(result["task_snapshots"]))
        snapshot = result["task_snapshots"][0]
        self.assertEqual("TaskSnapshot", snapshot["result_type"])
        self.assertEqual("external_ref", snapshot["task_ref"]["task_ref"])
        self.assertEqual(
            {"backend_key", "task_ref", "task_url", "title"},
            set(snapshot["task_ref"]),
        )
        self.assertEqual(
            {"display_link"},
            set(snapshot["backend_metadata"]),
        )
        self.assertNotIn("provider-only", json.dumps(result))
        self.assertNotIn("field_id", json.dumps(result))
        self.assertNotIn("node_id", json.dumps(result))

    def test_public_schema_does_not_require_backend_key(self):
        adapter = self.load_adapter()

        required = adapter.TASK_QUERY_SCHEMA["parameters"]["properties"]["query"].get(
            "required", []
        )

        self.assertNotIn("backend_key", required)

    def test_public_query_uses_host_default_local_route(self):
        adapter = self.load_adapter()
        fixture = PLUGIN_ROOT / "tests" / "fixtures" / "local_tasks.json"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "tasks.json"
            document = json.loads(fixture.read_text(encoding="utf-8"))
            document["adapter_contract_version"] = 2
            source.write_text(json.dumps(document), encoding="utf-8")
            routes = root / "routes.toml"
            routes.write_text(
                f'''contract_version = 2
default_backend = "local_tasks"
[backends.local_tasks]
adapter_key = "local_json"
query_tool = "task_adapter__local_json__task_query"
preflight_tool = "task_adapter__local_json__task_preflight"
apply_tool = "task_adapter__local_json__task_apply"
read_root = "{root}"
source_path = "tasks.json"
[backends.local_tasks.destinations.default]
public_ref = "tasks:default"
destination_label = "Local test tasks"
''',
                encoding="utf-8",
            )

            result = adapter.query_tasks(
                {"query": {"status": "ready", "limit": 20}, "destination_ref": "tasks:default"},
                dispatch=lambda *_args, **_kwargs: self.fail("local route must not dispatch"),
                routes_file=str(routes),
            )

        self.assertTrue(result["ok"])
        self.assertEqual("local_tasks", result["backend_key"])
        self.assertEqual(["Prepare quarterly plan"], [item["title"] for item in result["task_snapshots"]])

    def test_public_limit_is_applied_before_normalizing_string_or_dict_results(self):
        first = self.valid_snapshot()
        responses = (
            {"adapter_contract_version": 2, "items": [first, {}]},
            json.dumps({"adapter_contract_version": 2, "items": [first, {}]}),
        )
        for response in responses:
            with self.subTest(response_type=type(response).__name__):
                result = self.query_external(
                    {
                        "query": {"backend_key": "github_projects_mcp", "limit": 1},
                        "destination_ref": "github-projects:portfolio-os-task-board",
                    },
                    dispatch=lambda *_args, **_kwargs: response,
                )

                self.assertTrue(result["ok"])
                self.assertEqual(1, len(result["task_snapshots"]))

    def test_public_facade_maps_local_resolve_failure_to_typed_source_error(self):
        adapter = self.load_adapter()
        route_type = importlib.import_module(
            "task_management.route_config"
        ).ResolvedTaskReadRoute
        route = route_type(
            backend_key="local_tasks",
            adapter_key="local_json",
            kind="local_json",
            destination_ref="tasks:default",
            destination_label="Local test tasks",
            query_tool="task_adapter__local_json__task_query",
            preflight_tool="task_adapter__local_json__task_preflight",
            apply_tool="task_adapter__local_json__task_apply",
            read_root=Path("/tmp/task-read-root"),
            source_path=Path("/tmp/task-read-root/tasks.json"),
        )
        with patch.object(adapter, "load_read_route", return_value=route), patch.object(
            adapter.Path, "resolve", side_effect=OSError("must-not-leak")
        ):
            result = adapter.query_tasks(
                {"query": {}, "destination_ref": "tasks:default"},
                dispatch=lambda *_args, **_kwargs: self.fail("dispatch must not run"),
                routes_file="routes.toml",
            )

        self.assertFalse(result["ok"])
        self.assertEqual("task_source_unreadable", result["error"]["code"])
        self.assertNotIn("must-not-leak", json.dumps(result))

    def test_query_fails_closed_when_routes_file_is_not_configured(self):
        adapter = self.load_adapter()
        result = adapter.query_tasks(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: self.fail("dispatch must not run"),
        )

        self.assertEqual("TaskSnapshotResult", result["result_type"])
        self.assertFalse(result["ok"])
        self.assertEqual("read_route_missing", result["error"]["code"])
        self.assertEqual(ROUTES_FILE_ENV, result["error"]["configuration"])

    def test_legacy_adapter_environment_cannot_replace_the_routes_file(self):
        adapter = self.load_adapter()

        class Context:
            def dispatch_tool(self, *_args, **_kwargs):
                raise AssertionError("dispatch must not run")

            def register_tool(self, **kwargs):
                self.handler = kwargs["handler"]

        context = Context()
        with patch.dict(
            os.environ,
            {"TASK_MANAGEMENT_READ_ADAPTER_TOOL": "mcp__github__projects_write"},
            clear=True,
        ):
            adapter.register_read_tool(context)
            result = json.loads(
                context.handler(
                    {
                        "query": {"backend_key": "github_projects_mcp", "limit": 20},
                        "destination_ref": "github-projects:portfolio-os-task-board",
                    }
                )
            )

        self.assertFalse(result["ok"])
        self.assertEqual("read_route_missing", result["error"]["code"])
        self.assertEqual(ROUTES_FILE_ENV, result["error"]["configuration"])

    def test_query_rejects_invalid_optional_field_types_before_dispatch(self):
        adapter = self.load_adapter()
        result = adapter.query_tasks(
            {
                "query": {
                    "backend_key": "github_projects_mcp",
                    "status": ["ready"],
                    "limit": True,
                },
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: self.fail("dispatch must not run"),
        )

        self.assertFalse(result["ok"])
        self.assertEqual("invalid_task_query", result["error"]["code"])

    def test_query_normalizes_adapter_exceptions_without_leaking_details(self):
        adapter = self.load_adapter()

        def dispatch(*_args, **_kwargs):
            raise RuntimeError("authorization: Bearer must-not-leak")

        result = self.query_external(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=dispatch,
        )

        serialized = json.dumps(result)
        self.assertFalse(result["ok"])
        self.assertEqual("read_adapter_unavailable", result["error"]["code"])
        self.assertNotIn("must-not-leak", serialized)
        self.assertNotIn("Bearer", serialized)

    def test_query_rejects_credential_values_before_dispatch(self):
        adapter = self.load_adapter()
        result = self.query_external(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "token=must-not-leak",
            },
            dispatch=lambda *_args, **_kwargs: self.fail("dispatch must not run"),
        )

        serialized = json.dumps(result)
        self.assertFalse(result["ok"])
        self.assertEqual("invalid_task_query", result["error"]["code"])
        self.assertNotIn("must-not-leak", serialized)

    def test_query_rejects_credentials_in_normalized_snapshot_values(self):
        result = self.query_external(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: json.dumps(
                {
                    "adapter_contract_version": 2,
                    "items": [
                        {
                            "task_ref": {
                                "backend_key": "github_projects_mcp",
                                "task_ref": "external_ref",
                                "task_url": "https://example.invalid/tasks/1",
                                "title": "Credential leak",
                            },
                            "title": "Credential leak",
                            "body": "authorization: Bearer must-not-leak",
                            "work_unit_id": "security",
                            "work_unit_name": "Security",
                            "task_type": "review",
                            "status": "ready",
                            "due_date": None,
                            "urgency": "high",
                            "importance": "critical",
                            "automation_mode": "manual_only",
                            "approval_required": True,
                            "source_ref": {
                                "kind": "task_backend",
                                "ref": "external_ref",
                                "label": "Portfolio OS Tasks",
                            },
                            "backend_metadata": {},
                        }
                    ]
                }
            ),
        )

        serialized = json.dumps(result)
        self.assertFalse(result["ok"])
        self.assertEqual("unsafe_task_snapshot", result["error"]["code"])
        self.assertNotIn("must-not-leak", serialized)
        self.assertNotIn("Bearer", serialized)

    def test_query_rejects_provider_ids_hidden_in_canonical_scalar_fields(self):
        result = self.query_external(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: json.dumps(
                {
                    "adapter_contract_version": 2,
                    "items": [
                        {
                            "task_ref": {
                                "backend_key": "github_projects_mcp",
                                "task_ref": "external_ref",
                                "task_url": {"node_id": "must-not-leak"},
                                "title": "Malformed task",
                            },
                            "title": "Malformed task",
                            "body": "Body",
                            "work_unit_id": "security",
                            "work_unit_name": "Security",
                            "task_type": "review",
                            "status": "ready",
                            "due_date": None,
                            "urgency": "high",
                            "importance": "critical",
                            "automation_mode": "manual_only",
                            "approval_required": True,
                            "source_ref": {
                                "kind": "task_backend",
                                "ref": "external_ref",
                                "label": "Portfolio OS Tasks",
                            },
                            "backend_metadata": {},
                        }
                    ]
                }
            ),
        )

        serialized = json.dumps(result)
        self.assertFalse(result["ok"])
        self.assertEqual("invalid_task_snapshot", result["error"]["code"])
        self.assertNotIn("node_id", serialized)
        self.assertNotIn("must-not-leak", serialized)

    def test_query_rejects_provider_id_markers_hidden_in_text_fields(self):
        adapter = self.load_adapter()
        snapshot = self.valid_snapshot()
        snapshot["body"] = (
            'raw JSON: {"field_id":"provider-only-field",'
            '"api_key":"must-not-leak"}'
        )

        result = self.query_external(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: json.dumps(
                {"adapter_contract_version": 2, "items": [snapshot]}
            ),
        )

        serialized = json.dumps(result)
        self.assertFalse(result["ok"])
        self.assertEqual("unsafe_task_snapshot", result["error"]["code"])
        self.assertNotIn("provider-only-field", serialized)
        self.assertNotIn("must-not-leak", serialized)

    def test_query_rejects_snapshot_for_a_different_backend(self):
        adapter = self.load_adapter()
        snapshot = self.valid_snapshot()
        snapshot["task_ref"]["backend_key"] = "different_backend"

        result = self.query_external(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: json.dumps(
                {"adapter_contract_version": 2, "items": [snapshot]}
            ),
        )

        self.assertFalse(result["ok"])
        self.assertEqual("invalid_task_snapshot", result["error"]["code"])

    def test_query_rejects_noncanonical_snapshot_taxonomy_and_date(self):
        adapter = self.load_adapter()
        for field, invalid_value in (("urgency", "urgent"), ("due_date", "tomorrow")):
            with self.subTest(field=field):
                snapshot = self.valid_snapshot()
                snapshot[field] = invalid_value
                result = self.query_external(
                    {
                        "query": {
                            "backend_key": "github_projects_mcp",
                            "limit": 20,
                        },
                        "destination_ref": "github-projects:portfolio-os-task-board",
                    },
                    dispatch=lambda *_args, **_kwargs: json.dumps(
                        {"adapter_contract_version": 2, "items": [snapshot]}
                    ),
                )

                self.assertFalse(result["ok"])
                self.assertEqual("invalid_task_snapshot", result["error"]["code"])

    def test_query_rejects_noncanonical_query_taxonomy_and_date(self):
        adapter = self.load_adapter()
        for field, invalid_value in (
            ("task_type", "github_custom"),
            ("due_before", "tomorrow"),
        ):
            with self.subTest(field=field):
                result = adapter.query_tasks(
                    {
                        "query": {
                            "backend_key": "github_projects_mcp",
                            field: invalid_value,
                        },
                        "destination_ref": "github-projects:portfolio-os-task-board",
                    },
                    dispatch=lambda *_args, **_kwargs: self.fail(
                        "dispatch must not run"
                    ),
                )

                self.assertFalse(result["ok"])
                self.assertEqual("invalid_task_query", result["error"]["code"])

    def test_query_rejects_unsafe_link_schemes(self):
        adapter = self.load_adapter()
        for link_target in ("task_url", "display_link"):
            with self.subTest(link_target=link_target):
                snapshot = self.valid_snapshot()
                if link_target == "task_url":
                    snapshot["task_ref"]["task_url"] = "javascript:alert(1)"
                else:
                    snapshot["backend_metadata"] = {
                        "display_link": {
                            "name": "Unsafe link",
                            "url": "file:///private/provider-payload",
                        }
                    }
                result = self.query_external(
                    {
                        "query": {
                            "backend_key": "github_projects_mcp",
                            "limit": 20,
                        },
                        "destination_ref": "github-projects:portfolio-os-task-board",
                    },
                    dispatch=lambda *_args, **_kwargs: json.dumps(
                        {"adapter_contract_version": 2, "items": [snapshot]}
                    ),
                )

                self.assertFalse(result["ok"])
                self.assertEqual("invalid_task_snapshot", result["error"]["code"])

    def test_query_rejects_missing_required_backend_metadata(self):
        adapter = self.load_adapter()
        snapshot = self.valid_snapshot()
        snapshot.pop("backend_metadata")

        result = self.query_external(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: json.dumps(
                {"adapter_contract_version": 2, "items": [snapshot]}
            ),
        )

        self.assertFalse(result["ok"])
        self.assertEqual("invalid_task_snapshot", result["error"]["code"])


if __name__ == "__main__":
    unittest.main()
