import importlib.util
import json
import os
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ADAPTER_ROOT = Path(__file__).resolve().parents[1]
TASK_MANAGEMENT_ROOT = ADAPTER_ROOT.parent / "task-management"
PROVIDER_FIXTURE = ADAPTER_ROOT / "tests" / "fixtures" / "provider" / "projects-query-pages.json"
OPERATION_FIXTURE = (
    TASK_MANAGEMENT_ROOT
    / "tests"
    / "fixtures"
    / "adapter-v2"
    / "accept"
    / "operation-create.json"
)


def _load_plugin(name, root):
    spec = importlib.util.spec_from_file_location(
        name,
        root / "__init__.py",
        submodule_search_locations=[str(root)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _public_success(payload):
    return json.dumps({"result": json.dumps(payload, ensure_ascii=False)})


class FakeGithubProvider:
    WRITE_METHODS = {
        "create",
        "add_project_item",
        "update_project_item",
        "update",
        "add_issue_comment",
    }

    def __init__(self):
        fixture = json.loads(PROVIDER_FIXTURE.read_text(encoding="utf-8"))
        self.fields = fixture["fields"]
        self.item_template = fixture["pages"][0]["items"][0]
        self.calls = []
        self.issue = None
        self.field_values = {}
        self.fail_method = None
        self.failure_message = None
        self.successful_write_methods = []

    @property
    def write_calls(self):
        return [call for call in self.calls if call[1]["method"] in self.WRITE_METHODS]

    def dispatch(self, tool_name, arguments):
        self.calls.append((tool_name, arguments))
        method = arguments["method"]
        if method == self.fail_method:
            return json.dumps({"error": self.failure_message})
        if method == "get_project":
            return _public_success(
                {
                    "number": 7,
                    "title": "Portfolio OS Tasks",
                    "owner": {"login": "example-owner"},
                }
            )
        if method == "list_project_fields":
            return _public_success(
                {
                    "fields": self.fields,
                    "pageInfo": {"hasNextPage": False, "nextCursor": None},
                }
            )
        if method == "list_project_items":
            items = [] if self.issue is None else [self._provider_item()]
            return _public_success(
                {
                    "items": items,
                    "pageInfo": {"hasNextPage": False, "nextCursor": None},
                }
            )
        if method == "create":
            self.successful_write_methods.append(method)
            self.issue = {
                "number": 42,
                "title": arguments["title"],
                "html_url": (
                    "https://github.com/example-owner/"
                    "example-repository/issues/42"
                ),
            }
            return _public_success(self.issue)
        if method == "add_project_item":
            self.successful_write_methods.append(method)
            return _public_success({"item_id": 8101})
        if method == "update_project_item":
            self.successful_write_methods.append(method)
            update = arguments["updated_field"]
            self.field_values[update["name"]] = update["value"]
            return _public_success({"item_id": 8101})
        if method == "get_project_item":
            return _public_success(self._provider_item())
        raise AssertionError(f"unexpected fake GitHub method: {method}")

    def _provider_item(self):
        item = deepcopy(self.item_template)
        item["content"]["title"] = self.issue["title"]
        for field in item["fields"]:
            if field["name"] not in self.field_values:
                continue
            value = self.field_values[field["name"]]
            field["value"] = (
                {"id": "provider-private", "name": value, "color": "GRAY"}
                if field["data_type"] == "single_select"
                else value
            )
        return item


class FakePluginContext:
    def __init__(self, provider):
        self.provider = provider
        self.tools = {}
        self.skills = {}

    def register_skill(self, name, path, **metadata):
        self.skills[name] = {"path": path, **metadata}

    def register_tool(self, *, name, handler, **_metadata):
        self.tools[name] = handler

    def dispatch_tool(self, name, arguments, **kwargs):
        if name.startswith("mcp__github__"):
            return self.provider.dispatch(name, arguments)
        return self.tools[name](arguments, **kwargs)


class TaskManagementGithubAdapterEndToEndTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.routes_path = Path(self.temp_dir.name) / "routes.toml"
        self.routes_path.write_text(
            '''contract_version = 2
default_backend = "remote_tasks"
[backends.remote_tasks]
adapter_key = "github_projects"
query_tool = "task_adapter__github_projects__task_query"
preflight_tool = "task_adapter__github_projects__task_preflight"
apply_tool = "task_adapter__github_projects__task_apply"
[backends.remote_tasks.destinations.portfolio_os]
public_ref = "tasks:portfolio-os"
destination_label = "Portfolio OS Tasks"
content_target_ref = "task-content:portfolio-os"
''',
            encoding="utf-8",
        )
        self.old_environment = {
            "TASK_MANAGEMENT_ROUTES_FILE": os.environ.get("TASK_MANAGEMENT_ROUTES_FILE"),
            "TASK_ADAPTER_GITHUB_PROJECTS_CONFIG_FILE": os.environ.get(
                "TASK_ADAPTER_GITHUB_PROJECTS_CONFIG_FILE"
            ),
        }
        os.environ["TASK_MANAGEMENT_ROUTES_FILE"] = str(self.routes_path)
        os.environ["TASK_ADAPTER_GITHUB_PROJECTS_CONFIG_FILE"] = str(
            ADAPTER_ROOT / "config" / "github-projects.example.toml"
        )
        self.provider = FakeGithubProvider()
        self.context = FakePluginContext(self.provider)
        self.loaded_modules = (
            "task_adapter_github_projects_e2e_plugin",
            "task_management_e2e_plugin",
        )
        _load_plugin(self.loaded_modules[0], ADAPTER_ROOT).register(self.context)
        _load_plugin(self.loaded_modules[1], TASK_MANAGEMENT_ROOT).register(self.context)

    def tearDown(self):
        for name, value in self.old_environment.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        for module_name in tuple(sys.modules):
            if any(
                module_name == root or module_name.startswith(root + ".")
                for root in self.loaded_modules
            ):
                sys.modules.pop(module_name, None)
        self.temp_dir.cleanup()

    def operation(self):
        value = json.loads(OPERATION_FIXTURE.read_text(encoding="utf-8"))
        value["destination_ref"] = "tasks:portfolio-os"
        return value

    def preflight(self):
        return json.loads(
            self.context.dispatch_tool(
                "task_preflight",
                {"interface_version": 2, "operation": self.operation()},
            )
        )

    def apply(self, preflight, *, decision="approved", preview=None):
        return json.loads(
            self.context.dispatch_tool(
                "task_apply",
                {
                    "interface_version": 2,
                    "approval_preview": preview or preflight["approval_preview"],
                    "approval_receipt": {
                        "receipt_version": 1,
                        "decision": decision,
                        "operation_digest": preflight["approval_digest"],
                    },
                },
            )
        )

    def test_public_preflight_reaches_executable_adapter_without_writes(self):
        result = json.loads(
            self.context.dispatch_tool(
                "task_preflight",
                {"interface_version": 2, "operation": self.operation()},
            )
        )

        self.assertTrue(result["ok"])
        self.assertEqual("human_required", result["approval_mode"])
        self.assertEqual([], self.provider.write_calls)
        self.assertEqual(
            ["get_project", "list_project_fields", "list_project_items"],
            [arguments["method"] for _tool, arguments in self.provider.calls],
        )

    def test_approved_apply_is_publicly_readable_through_task_query(self):
        preflight = self.preflight()
        applied = self.apply(preflight)
        read_back = json.loads(
            self.context.dispatch_tool(
                "task_query",
                {
                    "destination_ref": "tasks:portfolio-os",
                    "query": {"backend_key": "remote_tasks", "limit": 10},
                },
            )
        )

        self.assertTrue(applied["ok"])
        self.assertEqual("created", applied["status"])
        self.assertEqual(1, len(read_back["task_snapshots"]))
        self.assertEqual(
            "Implement write contracts",
            read_back["task_snapshots"][0]["title"],
        )
        self.assertEqual(
            "github-issue:example-owner/example-repository#42",
            read_back["task_snapshots"][0]["task_ref"]["task_ref"],
        )

    def test_human_required_confidence_decision_completes_no_write(self):
        preflight = self.preflight()
        result = self.apply(preflight, decision="confidence_authorized")

        self.assertFalse(result["ok"])
        self.assertEqual("approval_required", result["error"]["code"])
        self.assertEqual([], self.provider.write_calls)
        self.assertEqual([], self.provider.successful_write_methods)

    def test_approval_mismatch_completes_no_write(self):
        preflight = self.preflight()
        changed_preview = deepcopy(preflight["approval_preview"])
        changed_preview["expected_side_effects"][0]["description"] = (
            "A changed side effect that was not approved."
        )
        result = self.apply(preflight, preview=changed_preview)

        self.assertFalse(result["ok"])
        self.assertEqual("approval_mismatch", result["error"]["code"])
        self.assertEqual([], self.provider.write_calls)
        self.assertEqual([], self.provider.successful_write_methods)

    def test_partial_create_is_nonretryable_and_preserves_safe_task_ref(self):
        preflight = self.preflight()
        self.provider.fail_method = "add_project_item"
        self.provider.failure_message = "provider connection ended unexpectedly"

        result = self.apply(preflight)

        self.assertFalse(result["ok"])
        self.assertEqual("partial", result["status"])
        self.assertFalse(result["retryable"])
        self.assertEqual(
            "github-issue:example-owner/example-repository#42",
            result["task_ref"]["task_ref"],
        )
        self.assertEqual(["create"], self.provider.successful_write_methods)
        self.assertNotIn("provider connection", json.dumps(result))

    def test_explicit_no_write_rate_limit_is_retryable(self):
        preflight = self.preflight()
        self.provider.fail_method = "create"
        self.provider.failure_message = "rate limit; write not executed"

        result = self.apply(preflight)

        self.assertFalse(result["ok"])
        self.assertEqual("failed", result["status"])
        self.assertTrue(result["retryable"])
        self.assertEqual([], self.provider.successful_write_methods)
        self.assertEqual(
            ["create"],
            [
                arguments["method"]
                for _tool, arguments in self.provider.calls
                if arguments["method"] == "create"
            ],
        )


if __name__ == "__main__":
    unittest.main()
