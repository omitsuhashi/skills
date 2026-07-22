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


def public_error(message):
    return json.dumps({"error": message}, ensure_ascii=False)


def request_for(operation_name):
    operation = json.loads(
        (FIXTURE_ROOT / f"operation-{operation_name}.json").read_text(
            encoding="utf-8"
        )
    )
    operation["destination_ref"] = "tasks:portfolio-os"
    content_target_ref = None
    if operation_name == "create":
        content_target_ref = "task-content:portfolio-os"
    else:
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
        "content_target_ref": content_target_ref,
        "operation_digest": "sha256:" + "d" * 64,
    }


def issue_result(title="Implement write contracts"):
    return {"number": 42, "title": title, "html_url": TASK_URL}


def readback_result():
    return {
        "id": "PVTI_must_not_escape",
        "content_type": "Issue",
        "content": {
            **issue_result(),
            "repository": "example-owner/example-repository",
        },
    }


def readback_page():
    return {
        "items": [readback_result()],
        "pageInfo": {"hasNextPage": False, "nextCursor": None},
    }


class GithubProjectsPartialFailureTests(unittest.TestCase):
    def _create_with_failure(self, failed_method, message):
        def dispatch(_tool_name, arguments):
            method = arguments["method"]
            if method == failed_method:
                return public_error(message)
            if method == "create":
                return public_success(issue_result())
            if method == "add_project_item":
                return public_success(
                    {"id": "PVTI_private", "item_id": 8101, "message": "private"}
                )
            if method == "update_project_item":
                return public_success({"id": 8101})
            if method == "get_project_item":
                return public_success(readback_result())
            self.fail(f"unexpected method: {method}")

        return GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        ).apply(request_for("create"))

    def test_create_stage_failures_are_typed_safe_and_not_blindly_retryable(self):
        cases = (
            ("create", "issue_create", "failed", False),
            ("add_project_item", "project_item_add", "partial", True),
            ("update_project_item", "project_fields_update", "partial", True),
            ("get_project_item", "task_read_back", "partial", True),
        )
        raw_error = (
            "provider timeout after unknown outcome; Authorization: Bearer must-not-leak; "
            "PVTI_private"
        )
        for failed_method, stage, status, has_task_ref in cases:
            with self.subTest(failed_method=failed_method):
                result = self._create_with_failure(failed_method, raw_error)

                self.assertFalse(result["ok"])
                self.assertEqual(status, result["status"])
                self.assertEqual(stage, result["error"]["stage"])
                self.assertEqual("adapter_unavailable", result["error"]["code"])
                self.assertFalse(result["retryable"])
                self.assertEqual(has_task_ref, result["task_ref"] is not None)
                self.assertIn("retry", result["human_action"].casefold())
                self.assertEqual(result, validate_task_write_result(result))
                serialized = json.dumps(result)
                self.assertNotIn("must-not-leak", serialized)
                self.assertNotIn("PVTI_", serialized)
                self.assertNotIn("Authorization", serialized)

    def test_only_explicit_no_write_rate_limit_is_retryable_before_first_write(self):
        retryable = self._create_with_failure(
            "create",
            "rate limit exceeded; write not executed",
        )
        unknown = self._create_with_failure(
            "create",
            "rate limit exceeded after unknown outcome",
        )
        already_partial = self._create_with_failure(
            "add_project_item",
            "rate limit exceeded; write not executed",
        )

        self.assertEqual("rate_limited", retryable["error"]["code"])
        self.assertTrue(retryable["retryable"])
        self.assertFalse(unknown["retryable"])
        self.assertFalse(already_partial["retryable"])
        self.assertEqual("partial", already_partial["status"])

    def test_comment_and_report_unknown_write_outcomes_preserve_safe_task_identity(self):
        for operation_name, expected_stage in (
            ("comment", "comment_create"),
            ("report", "report_create"),
        ):
            with self.subTest(operation_name=operation_name):
                result = GithubProjectsAdapter(
                    config=load_config(EXAMPLE_CONFIG),
                    dispatch=lambda *_args: public_error(
                        "timeout; token=must-not-leak; IC_private"
                    ),
                ).apply(request_for(operation_name))

                self.assertEqual("partial", result["status"])
                self.assertEqual(expected_stage, result["error"]["stage"])
                self.assertFalse(result["retryable"])
                self.assertEqual(
                    "github-issue:example-owner/example-repository#42",
                    result["task_ref"]["task_ref"],
                )
                self.assertIn("retry", result["human_action"].casefold())
                self.assertNotIn("must-not-leak", json.dumps(result))

    def test_invalid_adapter_owned_task_reference_blocks_before_dispatch(self):
        request = request_for("comment")
        request["operation"]["task_ref"] = {
            "backend_key": "remote_tasks",
            "task_ref": "task:opaque",
            "task_url": "https://example.invalid/tasks/opaque",
            "title": "Implement write contracts",
        }
        calls = []

        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=lambda *args: calls.append(args),
        ).apply(request)

        self.assertEqual([], calls)
        self.assertEqual("blocked", result["status"])
        self.assertEqual("task_reference", result["error"]["stage"])
        self.assertFalse(result["retryable"])


if __name__ == "__main__":
    unittest.main()
