import json
import importlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
READ_ADAPTER = PLUGIN_ROOT / "task_management" / "read_adapter.py"
ADAPTER_TOOL_ENV = "TASK_MANAGEMENT_READ_ADAPTER_TOOL"


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

    def test_query_dispatches_configured_read_adapter_and_returns_normalized_snapshots(self):
        adapter = self.load_adapter()
        calls = []

        def dispatch(tool_name, arguments, **kwargs):
            calls.append((tool_name, arguments, kwargs))
            return json.dumps(
                {
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
            adapter_tool_name="mcp__task_backend__task_query",
            task_id="task-123",
        )

        self.assertEqual(
            [
                (
                    "mcp__task_backend__task_query",
                    {
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
            source.write_text(fixture.read_text(encoding="utf-8"), encoding="utf-8")
            routes = root / "routes.toml"
            routes.write_text(
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

    def test_query_fails_closed_when_read_adapter_is_not_configured(self):
        adapter = self.load_adapter()
        result = adapter.query_tasks(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: self.fail("dispatch must not run"),
            adapter_tool_name=None,
        )

        self.assertEqual("TaskSnapshotResult", result["result_type"])
        self.assertFalse(result["ok"])
        self.assertEqual("read_adapter_unavailable", result["error"]["code"])
        self.assertEqual(ADAPTER_TOOL_ENV, result["error"]["configuration"])

    def test_query_rejects_non_read_adapter_tool_names(self):
        adapter = self.load_adapter()
        result = adapter.query_tasks(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: self.fail("dispatch must not run"),
            adapter_tool_name="mcp__github__projects_write",
        )

        self.assertFalse(result["ok"])
        self.assertEqual("invalid_read_adapter_tool", result["error"]["code"])

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
            adapter_tool_name="mcp__task_backend__task_query",
        )

        self.assertFalse(result["ok"])
        self.assertEqual("invalid_task_query", result["error"]["code"])

    def test_query_normalizes_adapter_exceptions_without_leaking_details(self):
        adapter = self.load_adapter()

        def dispatch(*_args, **_kwargs):
            raise RuntimeError("authorization: Bearer must-not-leak")

        result = adapter.query_tasks(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=dispatch,
            adapter_tool_name="mcp__task_backend__task_query",
        )

        serialized = json.dumps(result)
        self.assertFalse(result["ok"])
        self.assertEqual("read_adapter_failed", result["error"]["code"])
        self.assertNotIn("must-not-leak", serialized)
        self.assertNotIn("Bearer", serialized)

    def test_query_rejects_credential_values_before_dispatch(self):
        adapter = self.load_adapter()
        result = adapter.query_tasks(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "token=must-not-leak",
            },
            dispatch=lambda *_args, **_kwargs: self.fail("dispatch must not run"),
            adapter_tool_name="mcp__task_backend__task_query",
        )

        serialized = json.dumps(result)
        self.assertFalse(result["ok"])
        self.assertEqual("invalid_task_query", result["error"]["code"])
        self.assertNotIn("must-not-leak", serialized)

    def test_query_rejects_credentials_in_normalized_snapshot_values(self):
        adapter = self.load_adapter()

        result = adapter.query_tasks(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: json.dumps(
                {
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
            adapter_tool_name="mcp__task_backend__task_query",
        )

        serialized = json.dumps(result)
        self.assertFalse(result["ok"])
        self.assertEqual("unsafe_task_snapshot", result["error"]["code"])
        self.assertNotIn("must-not-leak", serialized)
        self.assertNotIn("Bearer", serialized)

    def test_query_rejects_provider_ids_hidden_in_canonical_scalar_fields(self):
        adapter = self.load_adapter()

        result = adapter.query_tasks(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: json.dumps(
                {
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
            adapter_tool_name="mcp__task_backend__task_query",
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

        result = adapter.query_tasks(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: json.dumps({"items": [snapshot]}),
            adapter_tool_name="mcp__task_backend__task_query",
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

        result = adapter.query_tasks(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: json.dumps({"items": [snapshot]}),
            adapter_tool_name="mcp__task_backend__task_query",
        )

        self.assertFalse(result["ok"])
        self.assertEqual("invalid_task_snapshot", result["error"]["code"])

    def test_query_rejects_noncanonical_snapshot_taxonomy_and_date(self):
        adapter = self.load_adapter()
        for field, invalid_value in (("urgency", "urgent"), ("due_date", "tomorrow")):
            with self.subTest(field=field):
                snapshot = self.valid_snapshot()
                snapshot[field] = invalid_value
                result = adapter.query_tasks(
                    {
                        "query": {
                            "backend_key": "github_projects_mcp",
                            "limit": 20,
                        },
                        "destination_ref": "github-projects:portfolio-os-task-board",
                    },
                    dispatch=lambda *_args, **_kwargs: json.dumps(
                        {"items": [snapshot]}
                    ),
                    adapter_tool_name="mcp__task_backend__task_query",
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
                    adapter_tool_name="mcp__task_backend__task_query",
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
                result = adapter.query_tasks(
                    {
                        "query": {
                            "backend_key": "github_projects_mcp",
                            "limit": 20,
                        },
                        "destination_ref": "github-projects:portfolio-os-task-board",
                    },
                    dispatch=lambda *_args, **_kwargs: json.dumps(
                        {"items": [snapshot]}
                    ),
                    adapter_tool_name="mcp__task_backend__task_query",
                )

                self.assertFalse(result["ok"])
                self.assertEqual("invalid_task_snapshot", result["error"]["code"])

    def test_query_rejects_missing_required_backend_metadata(self):
        adapter = self.load_adapter()
        snapshot = self.valid_snapshot()
        snapshot.pop("backend_metadata")

        result = adapter.query_tasks(
            {
                "query": {"backend_key": "github_projects_mcp", "limit": 20},
                "destination_ref": "github-projects:portfolio-os-task-board",
            },
            dispatch=lambda *_args, **_kwargs: json.dumps({"items": [snapshot]}),
            adapter_tool_name="mcp__task_backend__task_query",
        )

        self.assertFalse(result["ok"])
        self.assertEqual("invalid_task_snapshot", result["error"]["code"])


if __name__ == "__main__":
    unittest.main()
