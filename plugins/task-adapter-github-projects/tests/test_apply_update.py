import json
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = PLUGIN_ROOT / "config" / "github-projects.example.toml"
UPDATE_OPERATION = (
    PLUGIN_ROOT
    / "tests"
    / "fixtures"
    / "adapter-v2"
    / "accept"
    / "operation-update.json"
)
sys.path.insert(0, str(PLUGIN_ROOT))

from task_adapter_github_projects.adapter import GithubProjectsAdapter  # noqa: E402
from task_adapter_github_projects.config import load_config  # noqa: E402
from task_adapter_github_projects.contracts import validate_task_write_result  # noqa: E402


TASK_URL = "https://github.com/example-owner/example-repository/issues/42"


def public_success(payload):
    return json.dumps({"result": json.dumps(payload, ensure_ascii=False)})


def update_request(changes):
    operation = json.loads(UPDATE_OPERATION.read_text(encoding="utf-8"))
    operation["destination_ref"] = "tasks:portfolio-os"
    operation["task_ref"] = {
        "backend_key": "remote_tasks",
        "task_ref": "github-issue:example-owner/example-repository#42",
        "task_url": TASK_URL,
        "title": "Implement write contracts",
    }
    operation["payload"]["changes"] = changes
    return {
        "adapter_contract_version": 2,
        "operation": operation,
        "destination_label": "Portfolio OS Tasks",
        "content_target_ref": None,
        "operation_digest": "sha256:" + "b" * 64,
    }


def readback_page(title):
    return {
        "items": [
            {
                "id": "PVTI_must_not_escape",
                "content_type": "Issue",
                "content": {
                    "number": 42,
                    "title": title,
                    "html_url": TASK_URL,
                    "repository": "example-owner/example-repository",
                },
            }
        ],
        "pageInfo": {"hasNextPage": False, "nextCursor": None},
    }


class GithubProjectsUpdateApplyTests(unittest.TestCase):
    def test_update_keeps_issue_content_and_project_fields_distinct(self):
        calls = []

        def dispatch(tool_name, arguments):
            calls.append((tool_name, arguments))
            if arguments["method"] == "update":
                return public_success(
                    {
                        "number": 42,
                        "title": "Implement reviewed write contracts",
                        "html_url": TASK_URL,
                    }
                )
            if arguments["method"] == "update_project_item":
                return public_success({"id": 8101})
            if arguments["method"] == "list_project_items":
                return public_success(readback_page("Implement reviewed write contracts"))
            self.fail(f"unexpected provider call: {tool_name} {arguments}")

        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        ).apply(
            update_request(
                {
                    "title": "Implement reviewed write contracts",
                    "body": "Apply the reviewed provider write behavior.",
                    "due_date": "2026-08-01",
                    "importance": "critical",
                }
            )
        )

        self.assertEqual(
            ["update", "update_project_item", "update_project_item", "list_project_items"],
            [arguments["method"] for _tool_name, arguments in calls],
        )
        self.assertEqual(
            {
                "method": "update",
                "owner": "example-owner",
                "repo": "example-repository",
                "issue_number": 42,
                "title": "Implement reviewed write contracts",
                "body": "Apply the reviewed provider write behavior.",
            },
            calls[0][1],
        )
        self.assertEqual(
            ["Due Date", "Importance"],
            [
                arguments["updated_field"]["name"]
                for _tool_name, arguments in calls
                if arguments["method"] == "update_project_item"
            ],
        )
        for _tool_name, arguments in calls[1:3]:
            self.assertEqual("example-owner", arguments["item_owner"])
            self.assertEqual("example-repository", arguments["item_repo"])
            self.assertEqual(42, arguments["issue_number"])
            self.assertNotIn("item_id", arguments)
        self.assertTrue(result["ok"])
        self.assertEqual("updated", result["status"])
        self.assertEqual("Implement reviewed write contracts", result["task_ref"]["title"])
        self.assertEqual(result, validate_task_write_result(result))
        self.assertNotIn("PVTI_", json.dumps(result))

    def test_content_only_update_does_not_write_project_fields(self):
        calls = []

        def dispatch(tool_name, arguments):
            calls.append((tool_name, arguments))
            if arguments["method"] == "update":
                return public_success(
                    {
                        "number": 42,
                        "title": "Renamed task",
                        "html_url": TASK_URL,
                    }
                )
            if arguments["method"] == "list_project_items":
                return public_success(readback_page("Renamed task"))
            self.fail(f"unexpected provider call: {tool_name} {arguments}")

        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        ).apply(update_request({"title": "Renamed task"}))

        self.assertEqual(
            ["update", "list_project_items"],
            [arguments["method"] for _tool_name, arguments in calls],
        )
        self.assertNotIn(
            "projects_write",
            [tool_name.rsplit("__", 1)[-1] for tool_name, _arguments in calls],
        )
        self.assertEqual("updated", result["status"])
        self.assertEqual(result, validate_task_write_result(result))


if __name__ == "__main__":
    unittest.main()
