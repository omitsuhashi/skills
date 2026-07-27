import copy
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

    def test_create_issue_search_and_exact_readback_conditions_are_distinct(
        self,
    ) -> None:
        create = next(
            op for op in self.contract["operations"] if op["name"] == "task_create"
        )
        issue_step = next(
            step for step in create["steps"] if step["id"] == "issue"
        )
        self.assertEqual(
            "issue_search_match", issue_step["read_before_observed"]
        )
        self.assertEqual("exact_issue_readback", issue_step["observed"])
        issue_final = next(
            observation
            for observation in create["final_observations"]
            if observation["id"] == "issue"
        )
        self.assertEqual("exact_issue_readback", issue_final["observed"])

    def test_create_rejects_issue_search_as_post_write_readback(self) -> None:
        mutated = copy.deepcopy(self.contract)
        create = next(
            op for op in mutated["operations"] if op["name"] == "task_create"
        )
        issue_step = next(
            step for step in create["steps"] if step["id"] == "issue"
        )
        issue_step["read_after"] = "issue_search_exact"

        runner = ContractRunner(mutated, self.mcp)
        self.assertEqual("partial", runner.run("task_create", context()))
        self.assertEqual(1, self.mcp.writes.count("issue_create"))

    def test_duplicate_search_skips_create_but_final_exact_read_succeeds(
        self,
    ) -> None:
        self.mcp.issues["sha256:abc"] = {
            "number": 1,
            "title": "Ship exact readback",
            "body": "Observable result",
            "comments": [],
            "close_reason": None,
        }
        self.assertEqual("success", self.runner.run("task_create", context()))
        self.assertEqual(0, self.mcp.writes.count("issue_create"))
        self.assertEqual("read:issue_search_exact", self.mcp.calls[0])
        self.assertIn("read:issue_read_exact", self.mcp.calls)

    def test_partial_create_resumes_with_register_and_only_unfinished_steps(self) -> None:
        self.mcp.fail_next("project_priority_set_default", "before")
        self.assertEqual("partial", self.runner.run("task_create", context()))
        self.assertEqual("Inbox", self.mcp.project_items["sha256:abc"]["fields"]["Status"])

        self.assertEqual(
            "success",
            self.runner.run(
                "task_project_register", context(partial_resume=True)
            ),
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
            "success",
            self.runner.run(
                "task_project_register", context(partial_resume=True)
            ),
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
            "success",
            self.runner.run(
                "task_project_register", context(partial_resume=True)
            ),
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

    def test_wrong_update_read_after_cannot_observe_global_state(self) -> None:
        self.mcp.issues["sha256:abc"] = {
            "number": 1,
            "title": "Task",
            "body": "",
            "comments": [],
            "close_reason": None,
        }
        mutated = copy.deepcopy(self.contract)
        update = next(
            op for op in mutated["operations"] if op["name"] == "task_update_issue"
        )
        update["steps"][0]["read_after"] = "project_status_read"

        runner = ContractRunner(mutated, self.mcp)
        self.assertEqual(
            "partial",
            runner.run(
                "task_update_issue",
                {
                    "task_key": "sha256:abc",
                    "requested_field": "title",
                    "requested_value": "Updated title",
                },
            ),
        )

    def test_wrong_terminal_read_after_cannot_be_masked_by_final_read(self) -> None:
        self.mcp.issues["sha256:abc"] = {
            "number": 1,
            "title": "Task",
            "body": "",
            "comments": [],
            "close_reason": None,
        }
        mutated = copy.deepcopy(self.contract)
        terminal = next(
            op for op in mutated["operations"] if op["name"] == "task_complete"
        )
        issue_step = next(step for step in terminal["steps"] if step["id"] == "issue")
        issue_step["read_after"] = "project_terminal_status_read"

        runner = ContractRunner(mutated, self.mcp)
        self.assertEqual(
            "partial",
            runner.run(
                "task_complete",
                {
                    "task_key": "sha256:abc",
                    "remaining_sides": {"issue"},
                    "terminal_status": "Done",
                    "close_reason": "completed",
                },
            ),
        )

    def test_unknown_read_action_fails_instead_of_inspecting_global_state(self) -> None:
        self.mcp.issues["sha256:abc"] = {
            "number": 1,
            "title": "Task",
            "body": "",
            "comments": [],
            "close_reason": None,
        }
        mutated = copy.deepcopy(self.contract)
        update = next(
            op for op in mutated["operations"] if op["name"] == "task_update_issue"
        )
        update["steps"][0]["read_after"] = "nonsense_read"

        runner = ContractRunner(mutated, self.mcp)
        with self.assertRaises(AssertionError):
            runner.run(
                "task_update_issue",
                {
                    "task_key": "sha256:abc",
                    "requested_field": "title",
                    "requested_value": "Updated title",
                },
            )

    def test_register_requires_explicit_partial_resume_before_preflight_or_write(
        self,
    ) -> None:
        self.mcp.issues["sha256:abc"] = {
            "number": 1,
            "title": "Task",
            "body": "",
            "comments": [],
            "close_reason": None,
        }
        self.assertEqual(
            "blocked",
            self.runner.run(
                "task_project_register", {"task_key": "sha256:abc"}
            ),
        )
        self.assertEqual([], self.runner.local_preflights)
        self.assertEqual([], self.mcp.writes)

    def test_preflight_metadata_is_enforced_before_exact_writes(self) -> None:
        self.assertEqual("success", self.runner.run("task_create", context()))
        self.assertEqual(["task_create"], self.runner.local_preflights)
        self.assertLess(
            self.runner.events.index("preflight:task_create"),
            self.runner.events.index("write:issue_create"),
        )

        terminal_mcp = FakeGitHubMCP(
            issues={
                "sha256:abc": {
                    "number": 1,
                    "title": "Task",
                    "body": "",
                    "comments": [],
                    "close_reason": None,
                }
            },
            project_items={
                "sha256:abc": {
                    "issue_number": 1,
                    "fields": {
                        "Status": "Inbox",
                        "Priority": "P2",
                        "Due date": None,
                    },
                }
            },
        )
        terminal_runner = ContractRunner(self.contract, terminal_mcp)
        self.assertEqual(
            "success",
            terminal_runner.run(
                "task_complete",
                {
                    "task_key": "sha256:abc",
                    "remaining_sides": {"issue", "project"},
                    "terminal_status": "Done",
                    "close_reason": "completed",
                },
            ),
        )
        self.assertEqual(
            ["task_complete:issue", "task_complete:project"],
            terminal_runner.local_preflights,
        )
        for side, write in (
            ("issue", "issue_close_requested"),
            ("project", "project_status_set_terminal"),
        ):
            self.assertLess(
                terminal_runner.events.index(f"preflight:task_complete:{side}"),
                terminal_runner.events.index(f"write:{write}"),
            )

    def test_unknown_preflight_and_retry_metadata_fail_closed(self) -> None:
        for field, value in (
            ("local_preflight", "unknown"),
            ("retry_only", "unknown"),
        ):
            with self.subTest(field=field):
                mutated = copy.deepcopy(self.contract)
                create = next(
                    op
                    for op in mutated["operations"]
                    if op["name"] == "task_create"
                )
                create[field] = value
                mcp = FakeGitHubMCP()
                with self.assertRaises(AssertionError):
                    ContractRunner(mutated, mcp)
                self.assertEqual([], mcp.writes)

    def test_terminal_side_schema_mutations_are_rejected(self) -> None:
        mutations = ("missing_step_side", "wrong_final_side")
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                mutated = copy.deepcopy(self.contract)
                terminal = next(
                    op
                    for op in mutated["operations"]
                    if op["name"] == "task_complete"
                )
                if mutation == "missing_step_side":
                    issue_step = next(
                        step for step in terminal["steps"] if step["id"] == "issue"
                    )
                    issue_step.pop("side")
                else:
                    project_final = next(
                        observation
                        for observation in terminal["final_observations"]
                        if observation["id"] == "project"
                    )
                    project_final["side"] = "issue"
                with self.assertRaises(AssertionError):
                    ContractRunner(mutated, FakeGitHubMCP())

    def test_terminal_remaining_sides_are_nonempty_known_and_exact(self) -> None:
        for remaining_sides in (set(), {"unknown"}, {"issue", "unknown"}):
            with self.subTest(remaining_sides=remaining_sides):
                mcp = FakeGitHubMCP()
                runner = ContractRunner(self.contract, mcp)
                self.assertEqual(
                    "blocked",
                    runner.run(
                        "task_complete",
                        {
                            "task_key": "sha256:abc",
                            "remaining_sides": remaining_sides,
                            "terminal_status": "Done",
                            "close_reason": "completed",
                        },
                    ),
                )
                self.assertEqual([], mcp.writes)

        mcp = FakeGitHubMCP(
            issues={
                "sha256:abc": {
                    "number": 1,
                    "title": "Task",
                    "body": "",
                    "comments": [],
                    "close_reason": None,
                }
            },
            project_items={
                "sha256:abc": {
                    "issue_number": 1,
                    "fields": {
                        "Status": "Done",
                        "Priority": "P2",
                        "Due date": None,
                    },
                }
            },
        )
        runner = ContractRunner(self.contract, mcp)
        self.assertEqual(
            "success",
            runner.run(
                "task_complete",
                {
                    "task_key": "sha256:abc",
                    "remaining_sides": {"issue"},
                    "terminal_status": "Done",
                    "close_reason": "completed",
                },
            ),
        )
        self.assertEqual(["issue_close_requested"], mcp.writes)
        self.assertEqual(["task_complete:issue"], runner.local_preflights)

    def test_register_and_update_accept_minimal_operation_contexts(self) -> None:
        self.mcp.issues["sha256:abc"] = {
            "number": 1,
            "title": "Task",
            "body": "",
            "comments": [],
            "close_reason": None,
        }
        self.assertEqual(
            "success",
            self.runner.run(
                "task_project_register",
                {"task_key": "sha256:abc", "partial_resume": True},
            ),
        )
        self.assertEqual(
            "success",
            self.runner.run(
                "task_update_issue",
                {
                    "task_key": "sha256:abc",
                    "requested_field": "title",
                    "requested_value": "Minimal update",
                },
            ),
        )


if __name__ == "__main__":
    unittest.main()
