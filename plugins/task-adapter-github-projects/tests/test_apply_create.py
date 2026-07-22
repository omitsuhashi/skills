import json
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = PLUGIN_ROOT / "config" / "github-projects.example.toml"
CREATE_OPERATION = (
    PLUGIN_ROOT
    / "tests"
    / "fixtures"
    / "adapter-v2"
    / "accept"
    / "operation-create.json"
)
sys.path.insert(0, str(PLUGIN_ROOT))

from task_adapter_github_projects.adapter import GithubProjectsAdapter  # noqa: E402
from task_adapter_github_projects.config import load_config  # noqa: E402
from task_adapter_github_projects.contracts import validate_task_write_result  # noqa: E402


def public_success(payload):
    return json.dumps({"result": json.dumps(payload, ensure_ascii=False)})


def create_request(*, content_target_ref="task-content:portfolio-os"):
    operation = json.loads(CREATE_OPERATION.read_text(encoding="utf-8"))
    operation["destination_ref"] = "tasks:portfolio-os"
    return {
        "adapter_contract_version": 2,
        "operation": operation,
        "destination_label": "Portfolio OS Tasks",
        "content_target_ref": content_target_ref,
        "operation_digest": "sha256:" + "a" * 64,
    }


class GithubProjectsCreateApplyTests(unittest.TestCase):
    def test_create_uses_exact_linked_issue_project_fields_readback_order(self):
        calls = []

        def dispatch(tool_name, arguments):
            calls.append((tool_name, arguments))
            if arguments["method"] == "create":
                return public_success(
                    {
                        "number": 42,
                        "title": "Implement write contracts",
                        "html_url": (
                            "https://github.com/example-owner/"
                            "example-repository/issues/42"
                        ),
                    }
                )
            if arguments["method"] == "add_project_item":
                return public_success(
                    {
                        "id": "PVTI_must_not_escape",
                        "item_id": 8101,
                        "message": "raw provider message must not escape",
                    }
                )
            if arguments["method"] == "update_project_item":
                return public_success({"item_id": 8101})
            if arguments["method"] == "get_project_item":
                return public_success(
                    {
                        "id": "PVTI_must_not_escape",
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
            self.fail(f"unexpected provider call: {tool_name} {arguments}")

        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        ).apply(create_request())

        self.assertEqual(
            [
                "create",
                "add_project_item",
                "update_project_item",
                "update_project_item",
                "update_project_item",
                "update_project_item",
                "update_project_item",
                "update_project_item",
                "update_project_item",
                "update_project_item",
                "update_project_item",
                "get_project_item",
            ],
            [arguments["method"] for _tool_name, arguments in calls],
        )
        self.assertEqual(
            [
                "Work Unit ID",
                "Work Unit",
                "Task Type",
                "Due Date",
                "Urgency",
                "Importance",
                "Automation Mode",
                "Approval Required",
                "Source",
            ],
            [
                arguments["updated_field"]["name"]
                for _tool_name, arguments in calls
                if arguments["method"] == "update_project_item"
            ],
        )
        issue_arguments = calls[0][1]
        self.assertEqual(
            {
                "method": "create",
                "owner": "example-owner",
                "repo": "example-repository",
                "title": "Implement write contracts",
                "body": "Add strict backend-neutral contract validation.",
            },
            issue_arguments,
        )
        add_arguments = calls[1][1]
        self.assertEqual("issue", add_arguments["item_type"])
        self.assertEqual(42, add_arguments["issue_number"])
        self.assertNotIn("content_policy", json.dumps(calls))
        self.assertNotIn("draft", json.dumps(calls).casefold())
        self.assertEqual(
            {
                "backend_key": "remote_tasks",
                "task_ref": "github-issue:example-owner/example-repository#42",
                "task_url": (
                    "https://github.com/example-owner/example-repository/issues/42"
                ),
                "title": "Implement write contracts",
            },
            result["task_ref"],
        )
        self.assertTrue(result["ok"])
        self.assertEqual("created", result["status"])
        self.assertIn("retry", result["human_action"].casefold())
        self.assertEqual(result, validate_task_write_result(result))
        serialized = json.dumps(result)
        self.assertNotIn("PVTI_", serialized)
        self.assertNotIn("raw provider", serialized)

    def test_create_without_configured_opaque_content_target_blocks_before_dispatch(self):
        calls = []
        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=lambda *args: calls.append(args),
        ).apply(create_request(content_target_ref=None))

        self.assertEqual([], calls)
        self.assertFalse(result["ok"])
        self.assertEqual("blocked", result["status"])
        self.assertEqual("destination_unresolved", result["error"]["code"])
        self.assertEqual("content_target_lookup", result["error"]["stage"])
        self.assertEqual(result, validate_task_write_result(result))


if __name__ == "__main__":
    unittest.main()
