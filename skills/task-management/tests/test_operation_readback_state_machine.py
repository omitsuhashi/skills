from pathlib import Path
import sys
import unittest

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL = SKILL_ROOT / "SKILL.md"
CONTRACT = SKILL_ROOT / "references" / "operation-readback-state-machine.toml"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fake_github_mcp import ContractRunner, FakeGitHubMCP, load_contract


def context(**overrides):
    values = {
        "task_key": "sha256:abc",
        "title": "Ship exact readback",
        "body": "Observable result",
        "requested_field": "title",
        "requested_value": "Updated title",
        "comment": "Confirmed",
        "terminal_status": "Done",
        "close_reason": "completed",
    }
    values.update(overrides)
    return values


class OperationReadbackStateMachineTests(unittest.TestCase):
    def test_contract_artifact_is_linked_from_the_skill(self) -> None:
        self.assertTrue(CONTRACT.is_file(), "missing semantic state-machine contract")
        self.assertIn(
            "references/operation-readback-state-machine.toml",
            SKILL.read_text(encoding="utf-8"),
        )

    def setUp(self) -> None:
        if not CONTRACT.is_file():
            if self._testMethodName != "test_contract_artifact_is_linked_from_the_skill":
                self.skipTest("contract is introduced during GREEN")
            return
        self.contract = load_contract(CONTRACT)
        self.mcp = FakeGitHubMCP()
        self.runner = ContractRunner(self.contract, self.mcp)

    def test_contract_requires_semantic_read_after_and_observed_per_write(self) -> None:
        operations = {op["name"]: op for op in self.contract["operations"]}
        self.assertEqual(
            {
                "task_create",
                "task_project_register",
                "task_update_issue",
                "task_update_project",
                "task_comment",
                "task_complete",
            },
            operations.keys(),
        )
        self.assertEqual("once", operations["task_create"]["local_preflight"])
        self.assertFalse(operations["task_create"]["retry_only"])
        self.assertTrue(operations["task_project_register"]["retry_only"])
        self.assertNotIn(
            "issue_create",
            {
                step["write"]
                for step in operations["task_project_register"]["steps"]
            },
        )
        for operation in operations.values():
            for step in operation["steps"]:
                self.assertTrue(step["read_before"])
                self.assertTrue(step["write"])
                self.assertTrue(step["read_after"])
                self.assertTrue(step["observed"])

    def test_task_create_observes_exact_remote_issue_item_and_defaults(self) -> None:
        result = self.runner.run("task_create", context())
        self.assertEqual("success", result)
        self.assertEqual(["task_create"], self.runner.local_preflights)
        self.assertEqual(1, self.mcp.writes.count("issue_create"))
        self.assertEqual(1, self.mcp.writes.count("project_item_add"))
        self.assertEqual(1, self.mcp.writes.count("project_status_set_default"))
        self.assertEqual(1, self.mcp.writes.count("project_priority_set_default"))
        calls = self.mcp.calls
        for write, readback in (
            ("write:issue_create", "read:issue_read_exact"),
            ("write:project_item_add", "read:project_item_read_exact"),
            ("write:project_status_set_default", "read:project_status_read"),
            ("write:project_priority_set_default", "read:project_priority_read"),
        ):
            self.assertLess(calls.index(write), calls.index(readback, calls.index(write)))
        self.assertEqual(
            "read:project_due_date_read",
            calls[-1],
            "success must end in an observed remote-state read",
        )

    def test_unknown_after_issue_create_reuses_readback_without_duplicate(self) -> None:
        self.mcp.fail_next("issue_create", "after")
        self.assertEqual("success", self.runner.run("task_create", context()))
        self.assertEqual(1, self.mcp.writes.count("issue_create"))
        self.assertLess(
            self.mcp.calls.index("read:issue_search_exact"),
            self.mcp.calls.index("write:issue_create"),
        )
        self.assertIn("read:issue_read_exact", self.mcp.calls)

    def test_partial_create_resumes_with_register_and_only_unfinished_steps(self) -> None:
        self.mcp.fail_next("project_priority_set_default", "before")
        self.assertEqual("partial", self.runner.run("task_create", context()))
        self.assertEqual("Inbox", self.mcp.project_items["sha256:abc"]["fields"]["Status"])

        self.assertEqual(
            "success", self.runner.run("task_project_register", context())
        )
        self.assertEqual(1, self.mcp.writes.count("issue_create"))
        self.assertEqual(1, self.mcp.writes.count("project_item_add"))
        self.assertEqual(1, self.mcp.writes.count("project_status_set_default"))
        self.assertEqual(2, self.mcp.writes.count("project_priority_set_default"))

    def test_unknown_project_add_and_update_read_back_before_any_retry(self) -> None:
        self.mcp.issues["sha256:abc"] = {
            "number": 1,
            "title": "Task",
            "body": "",
            "comments": [],
            "close_reason": None,
        }
        self.mcp.fail_next("project_item_add", "after")
        self.mcp.fail_next("project_status_set_default", "after")
        self.assertEqual(
            "success", self.runner.run("task_project_register", context())
        )
        self.assertEqual(1, self.mcp.writes.count("project_item_add"))
        self.assertEqual(1, self.mcp.writes.count("project_status_set_default"))

    def test_unknown_before_project_add_reads_back_before_retrying_once(self) -> None:
        self.mcp.issues["sha256:abc"] = {
            "number": 1,
            "title": "Task",
            "body": "",
            "comments": [],
            "close_reason": None,
        }
        self.mcp.fail_next("project_item_add", "unknown_before")
        self.assertEqual(
            "success", self.runner.run("task_project_register", context())
        )
        calls = self.mcp.calls
        first_write = calls.index("write:project_item_add")
        readback = calls.index("read:project_item_read_exact", first_write)
        retry = calls.index("write:project_item_add", first_write + 1)
        self.assertLess(first_write, readback)
        self.assertLess(readback, retry)
        self.assertEqual(2, self.mcp.writes.count("project_item_add"))

    def test_update_and_comment_each_require_post_write_readback(self) -> None:
        self.mcp.issues["sha256:abc"] = {
            "number": 1,
            "title": "Task",
            "body": "",
            "comments": [],
            "close_reason": None,
        }
        self.mcp.project_items["sha256:abc"] = {
            "issue_number": 1,
            "fields": {"Status": "Inbox", "Priority": "P2", "Due date": None},
        }
        scenarios = (
            ("task_update_issue", context(), "issue_update_requested", "issue_read_exact"),
            (
                "task_update_project",
                context(requested_field="Priority", requested_value="P1"),
                "project_field_update_requested",
                "project_field_read",
            ),
            ("task_comment", context(), "issue_comment_create", "issue_comment_read"),
        )
        for operation, operation_context, write, readback in scenarios:
            with self.subTest(operation=operation):
                start = len(self.mcp.calls)
                self.assertEqual(
                    "success", self.runner.run(operation, operation_context)
                )
                calls = self.mcp.calls[start:]
                self.assertLess(calls.index(f"write:{write}"), calls.index(f"read:{readback}", calls.index(f"write:{write}")))

    def test_terminal_partial_resume_changes_only_remaining_side(self) -> None:
        self.mcp.issues["sha256:abc"] = {
            "number": 1,
            "title": "Task",
            "body": "",
            "comments": [],
            "close_reason": None,
        }
        self.mcp.project_items["sha256:abc"] = {
            "issue_number": 1,
            "fields": {"Status": "Inbox", "Priority": "P2", "Due date": None},
        }
        self.mcp.fail_next("project_status_set_terminal", "before")
        self.assertEqual(
            "partial",
            self.runner.run(
                "task_complete", context(remaining_sides={"issue", "project"})
            ),
        )
        self.assertEqual(1, self.mcp.writes.count("issue_close_requested"))

        self.assertEqual(
            "success",
            self.runner.run(
                "task_complete", context(remaining_sides={"project"})
            ),
        )
        self.assertEqual(1, self.mcp.writes.count("issue_close_requested"))
        self.assertEqual(2, self.mcp.writes.count("project_status_set_terminal"))
        self.assertIn("read:issue_terminal_read", self.mcp.calls)
        self.assertIn("read:project_terminal_status_read", self.mcp.calls)

    def test_blocked_ambiguous_duplicate_and_bulk_are_zero_write(self) -> None:
        for outcome in ("blocked", "ambiguous", "duplicate", "bulk"):
            with self.subTest(outcome=outcome):
                mcp = FakeGitHubMCP()
                runner = ContractRunner(self.contract, mcp)
                self.assertEqual(
                    outcome,
                    runner.run("task_create", context(guard_outcome=outcome)),
                )
                self.assertEqual([], mcp.writes)

    def test_contract_keeps_direct_official_mcp_and_fake_out_of_production(self) -> None:
        meta = self.contract["contract"]
        self.assertEqual("direct_official_github_mcp", meta["instruction_path"])
        fake_path = Path(__file__).resolve().parent / "fake_github_mcp.py"
        self.assertEqual("tests", fake_path.parent.name)
        production_python = [
            path
            for path in SKILL_ROOT.rglob("*.py")
            if "tests" not in path.parts
        ]
        self.assertEqual([], production_python)


if __name__ == "__main__":
    unittest.main()
