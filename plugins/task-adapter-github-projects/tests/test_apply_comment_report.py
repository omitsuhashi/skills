import json
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = PLUGIN_ROOT / "config" / "github-projects.example.toml"
FIXTURE_ROOT = PLUGIN_ROOT / "tests" / "fixtures" / "adapter-v2" / "accept"
sys.path.insert(0, str(PLUGIN_ROOT))

from task_adapter_github_projects.adapter import GithubProjectsAdapter  # noqa: E402
from task_adapter_github_projects.config import load_config  # noqa: E402
from task_adapter_github_projects.contracts import validate_task_write_result  # noqa: E402


TASK_URL = "https://github.com/example-owner/example-repository/issues/42"


def public_success(payload):
    return json.dumps({"result": json.dumps(payload, ensure_ascii=False)})


def apply_request(operation_name):
    operation = json.loads(
        (FIXTURE_ROOT / f"operation-{operation_name}.json").read_text(
            encoding="utf-8"
        )
    )
    operation["destination_ref"] = "tasks:portfolio-os"
    operation["task_ref"] = {
        "backend_key": "remote_tasks",
        "task_ref": "github-issue:example-owner/example-repository#42",
        "task_url": TASK_URL,
        "title": "Implement write contracts",
    }
    return {
        "adapter_contract_version": 2,
        "operation": operation,
        "destination_label": "Portfolio OS Tasks",
        "content_target_ref": None,
        "operation_digest": "sha256:" + "c" * 64,
    }


def readback_page():
    return {
        "items": [
            {
                "id": "PVTI_must_not_escape",
                "content_type": "Issue",
                "content": {
                    "number": 42,
                    "title": "Implement write contracts",
                    "html_url": TASK_URL,
                    "repository": "example-owner/example-repository",
                },
            }
        ],
        "pageInfo": {"hasNextPage": False, "nextCursor": None},
    }


class GithubProjectsCommentReportApplyTests(unittest.TestCase):
    def test_comment_writes_the_short_issue_comment_and_returns_commented(self):
        calls = []

        def dispatch(tool_name, arguments):
            calls.append((tool_name, arguments))
            if tool_name.endswith("add_issue_comment"):
                return public_success(
                    {
                        "id": "IC_must_not_escape",
                        "body": arguments["body"],
                    }
                )
            if arguments["method"] == "list_project_items":
                return public_success(readback_page())
            self.fail(f"unexpected provider call: {tool_name} {arguments}")

        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        ).apply(apply_request("comment"))

        self.assertEqual(2, len(calls))
        self.assertEqual(
            {
                "owner": "example-owner",
                "repo": "example-repository",
                "issue_number": 42,
                "body": "Contract implementation is ready.",
            },
            calls[0][1],
        )
        self.assertEqual("commented", result["status"])
        self.assertTrue(result["ok"])
        self.assertEqual(result, validate_task_write_result(result))
        self.assertNotIn("IC_", json.dumps(result))

    def test_report_renders_structured_markdown_without_project_status_write(self):
        calls = []

        def dispatch(tool_name, arguments):
            calls.append((tool_name, arguments))
            if tool_name.endswith("add_issue_comment"):
                return public_success(
                    {
                        "id": "IC_must_not_escape",
                        "body": arguments["body"],
                    }
                )
            if arguments["method"] == "list_project_items":
                return public_success(readback_page())
            self.fail(f"unexpected provider call: {tool_name} {arguments}")

        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        ).apply(apply_request("report"))

        self.assertEqual(
            "## Task report\n\n"
            "### Summary\n\n"
            "Implemented contract v2.\n\n"
            "### Work performed\n\n"
            "- Added strict validators.\n\n"
            "### Verification\n\n"
            "- Contract tests passed.\n\n"
            "### Residuals\n\n"
            "- None.",
            calls[0][1]["body"],
        )
        self.assertEqual("reported", result["status"])
        self.assertTrue(result["ok"])
        self.assertEqual(result, validate_task_write_result(result))
        serialized_calls = json.dumps(calls)
        self.assertNotIn("projects_write", serialized_calls)
        self.assertNotIn("status_update", serialized_calls)
        self.assertNotIn("update_project", serialized_calls)


if __name__ == "__main__":
    unittest.main()
