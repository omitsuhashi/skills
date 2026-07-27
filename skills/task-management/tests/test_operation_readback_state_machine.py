import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL = SKILL_ROOT / "SKILL.md"
CONTRACT = SKILL_ROOT / "references" / "operation-readback-state-machine.toml"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fake_github_mcp import (
    ContractRunner,
    FakeGitHubMCP,
    UnknownOutcome,
    load_contract,
)


REPOSITORY = "the3-inc/companies"
PROJECT_URL = "https://github.com/orgs/the3-inc/projects/7"


def context(**overrides):
    values = {
        "task_key": "sha256:abc",
        "guard_outcome": "explicit",
        "repository": REPOSITORY,
        "project_url": PROJECT_URL,
        "issue_node_id": "I_1",
        "issue_number": None,
        "project_item_id": None,
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


def partial_receipt(**overrides):
    values = {
        "operation": "task_create",
        "repository": REPOSITORY,
        "project_url": PROJECT_URL,
        "task_key": "sha256:abc",
        "issue_number": None,
        "issue_node_id": "I_1",
        "state": "issue_observed",
        "project_item_id": None,
        "initial_field_plan": initial_field_plan(),
        "unfinished_transitions": [
            "project_item",
            "default_status",
            "default_priority",
        ],
    }
    values.update(overrides)
    return values


def initial_field_plan(**overrides):
    values = {
        "Status": {"source": "default", "value": "Inbox"},
        "Priority": {"source": "default", "value": "P2"},
        "Due date": {"source": "omitted", "value": None},
    }
    values.update(overrides)
    return values


def recovery_receipt(**overrides):
    values = partial_receipt(
        state="fields_incomplete",
        project_item_id="PVTI_1",
        initial_field_plan=initial_field_plan(),
        unfinished_transitions=["default_priority"],
    )
    values.update(overrides)
    return values


def issue_record(**overrides):
    values = {
        "number": 1,
        "node_id": "I_1",
        "repository": REPOSITORY,
        "marker": "sha256:abc",
        "title": "Task",
        "body": "",
        "comments": [],
        "close_reason": None,
    }
    values.update(overrides)
    return values


def project_item_record(**overrides):
    values = {
        "item_id": "PVTI_1",
        "project_url": PROJECT_URL,
        "issue_number": 1,
        "issue_node_id": "I_1",
        "fields": {
            "Status": "Inbox",
            "Priority": "P2",
            "Due date": None,
        },
    }
    values.update(overrides)
    return values


def only_project_item(mcp):
    return next(iter(mcp.project_items.values()))


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

    def _seed_issue(self, **overrides) -> None:
        self.mcp.issues["sha256:abc"] = issue_record(**overrides)

    def _seed_item(self, **overrides) -> None:
        self.mcp.project_items["sha256:abc"] = project_item_record(
            **overrides
        )

    def _seed_task(self) -> None:
        self._seed_issue()
        self._seed_item()

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
        self.assertEqual(
            {"eligible", "explicit", "inferred"},
            set(
                self.contract["contract"].get(
                    "write_eligible_outcomes", []
                )
            ),
        )
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
        write_index = self.mcp.calls.index("write:issue_create")
        after_write = self.mcp.calls[write_index + 1 :]
        self.assertIn(
            "read:issue_search_exact",
            after_write,
            "unknown create must resolve the marker after the write",
        )
        self.assertIn("read:issue_read_exact", after_write)
        self.assertLess(
            after_write.index("read:issue_search_exact"),
            after_write.index("read:issue_read_exact"),
        )

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
            "unique_issue_marker_match",
            issue_step["read_before_observed"],
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

    def test_duplicate_search_is_zero_write_for_normal_create(
        self,
    ) -> None:
        self._seed_issue(
            title="Ship exact readback",
            body="Observable result",
        )
        self.assertEqual("duplicate", self.runner.run("task_create", context()))
        self.assertEqual([], self.mcp.writes)
        self.assertEqual([], self.runner.local_preflights)
        self.assertEqual("read:issue_search_exact", self.mcp.calls[0])

    def test_unknown_issue_create_with_zero_marker_matches_fails_closed(
        self,
    ) -> None:
        self.mcp.fail_next("issue_create", "unknown_before")
        self.assertEqual("partial", self.runner.run("task_create", context()))
        self.assertEqual(1, self.mcp.writes.count("issue_create"))
        self.assertEqual({}, self.mcp.issues)

    def test_unknown_issue_create_with_multiple_marker_matches_fails_closed(
        self,
    ) -> None:
        class MultipleMatchAfterCreate(FakeGitHubMCP):
            def write(self, action, operation_context):
                try:
                    return super().write(action, operation_context)
                except UnknownOutcome:
                    if action == "issue_create":
                        self.issues["second-match"] = {
                            "number": 2,
                            "node_id": "I_2",
                            "repository": REPOSITORY,
                            "marker": operation_context["task_key"],
                            "title": "Second match",
                            "body": "Same marker",
                            "comments": [],
                            "close_reason": None,
                        }
                    raise

        mcp = MultipleMatchAfterCreate()
        mcp.fail_next("issue_create", "after")
        runner = ContractRunner(self.contract, mcp)
        self.assertEqual("partial", runner.run("task_create", context()))
        self.assertEqual(1, mcp.writes.count("issue_create"))

    def test_partial_create_resumes_with_register_and_only_unfinished_steps(self) -> None:
        self.mcp.fail_next("project_priority_set_default", "before")
        self.assertEqual("partial", self.runner.run("task_create", context()))
        self.assertEqual(
            "Inbox", only_project_item(self.mcp)["fields"]["Status"]
        )

        self.assertEqual(
            "success",
            self.runner.run(
                "task_project_register",
                context(
                    partial_resume=True,
                    project_item_id="PVTI_1",
                    partial_receipt=recovery_receipt(),
                ),
            ),
        )
        self.assertEqual(1, self.mcp.writes.count("issue_create"))
        self.assertEqual(1, self.mcp.writes.count("project_item_add"))
        self.assertEqual(1, self.mcp.writes.count("project_status_set_default"))
        self.assertEqual(2, self.mcp.writes.count("project_priority_set_default"))
        self.assertEqual(
            "P2", only_project_item(self.mcp)["fields"]["Priority"]
        )

    def test_fields_incomplete_receipt_runs_only_declared_field_transition(
        self,
    ) -> None:
        plan = initial_field_plan(
            Status={"source": "requested", "value": "Ready"},
            **{"Due date": {
                "source": "requested",
                "value": "2026-08-20",
            }},
        )
        self._seed_issue()
        self._seed_item(
            fields={"Status": "Ready", "Due date": "2026-08-20"}
        )

        self.assertEqual(
            "success",
            self.runner.run(
                "task_project_register",
                context(
                    project_item_id="PVTI_1",
                    partial_receipt=recovery_receipt(
                        initial_field_plan=plan,
                    ),
                ),
            ),
        )
        self.assertEqual(
            ["project_priority_set_default"],
            self.mcp.writes,
        )
        self.assertEqual(
            {
                "Status": "Ready",
                "Priority": "P2",
                "Due date": "2026-08-20",
            },
            only_project_item(self.mcp)["fields"],
        )
        write_index = self.mcp.calls.index(
            "write:project_priority_set_default"
        )
        self.assertEqual(
            2,
            self.mcp.calls[write_index + 1 :].count(
                "read:project_priority_read"
            ),
        )
        self.assertEqual("read:project_priority_read", self.mcp.calls[-1])

    def test_fields_incomplete_receipt_mismatch_blocks_zero_write(self) -> None:
        valid = recovery_receipt()
        cases = {}
        for name, mutate in (
            ("missing_item", lambda value: value.pop("project_item_id")),
            ("missing_plan", lambda value: value.pop("initial_field_plan")),
            (
                "missing_unfinished",
                lambda value: value.pop("unfinished_transitions"),
            ),
            (
                "plan_transition_mismatch",
                lambda value: value["initial_field_plan"].__setitem__(
                    "Priority",
                    {"source": "requested", "value": "P1"},
                ),
            ),
            (
                "unknown_unfinished",
                lambda value: value.__setitem__(
                    "unfinished_transitions", ["default_due_date"]
                ),
            ),
        ):
            receipt = copy.deepcopy(valid)
            mutate(receipt)
            cases[name] = (receipt, "PVTI_1")
        cases["item_identity_mismatch"] = (copy.deepcopy(valid), "PVTI_other")
        cases["remote_item_identity_mismatch"] = (
            recovery_receipt(project_item_id="PVTI_missing"),
            "PVTI_missing",
        )

        for name, (receipt, item_id) in cases.items():
            with self.subTest(name=name):
                mcp = FakeGitHubMCP(
                    issues={"issue": issue_record()},
                    project_items={"item": project_item_record()},
                )
                runner = ContractRunner(self.contract, mcp)
                self.assertEqual(
                    "blocked",
                    runner.run(
                        "task_project_register",
                        context(
                            project_item_id=item_id,
                            partial_receipt=receipt,
                        ),
                    ),
                )
                self.assertEqual([], mcp.writes)
                self.assertEqual([], runner.local_preflights)

    def test_missing_item_receipt_requires_every_planned_field_transition(
        self,
    ) -> None:
        self._seed_issue()
        malformed = partial_receipt(
            state="project_item_missing",
            unfinished_transitions=["project_item"],
        )

        self.assertEqual(
            "blocked",
            self.runner.run(
                "task_project_register",
                context(partial_receipt=malformed),
            ),
        )
        self.assertEqual([], self.mcp.writes)
        self.assertEqual([], self.runner.local_preflights)

    def test_preexisting_multiple_project_items_is_ambiguous_zero_write(
        self,
    ) -> None:
        self._seed_issue()
        self.mcp.project_items = {
            "first": project_item_record(item_id="PVTI_1"),
            "second": project_item_record(item_id="PVTI_2"),
        }
        receipt = partial_receipt(
            state="project_item_unknown",
        )

        self.assertEqual(
            "ambiguous",
            self.runner.run(
                "task_project_register",
                context(
                    project_item_id=None,
                    partial_receipt=receipt,
                ),
            ),
        )
        self.assertEqual([], self.mcp.writes)

    def test_unknown_item_add_multiple_readback_stops_before_retry(self) -> None:
        class DuplicateAfterUnknownAdd(FakeGitHubMCP):
            def write(self, action, operation_context):
                try:
                    return super().write(action, operation_context)
                except UnknownOutcome:
                    if action == "project_item_add":
                        created = next(iter(self.project_items.values()))
                        duplicate = copy.deepcopy(created)
                        duplicate["item_id"] = "PVTI_duplicate"
                        self.project_items["duplicate"] = duplicate
                    raise

        mcp = DuplicateAfterUnknownAdd(issues={"issue": issue_record()})
        mcp.fail_next("project_item_add", "after")
        runner = ContractRunner(self.contract, mcp)
        receipt = partial_receipt(
            state="project_item_missing",
        )

        self.assertEqual(
            "ambiguous",
            runner.run(
                "task_project_register",
                context(
                    project_item_id=None,
                    partial_receipt=receipt,
                ),
            ),
        )
        self.assertEqual(["project_item_add"], mcp.writes)

    def test_register_capabilities_follow_only_unfinished_transitions(
        self,
    ) -> None:
        self._seed_issue()
        self._seed_item(fields={"Status": "Inbox", "Due date": None})
        self.assertEqual(
            "success",
            self.runner.run(
                "task_project_register",
                context(
                    project_item_id="PVTI_1",
                    partial_receipt=recovery_receipt(),
                ),
            ),
        )
        self.assertEqual(
            [
                (
                    "default_priority",
                    (
                        "project_priority_read",
                        "project_priority_update",
                    ),
                )
            ],
            getattr(self.runner, "capability_preflights", []),
        )

        observed_mcp = FakeGitHubMCP(
            issues={"issue": issue_record()},
            project_items={"item": project_item_record()},
        )
        observed_runner = ContractRunner(self.contract, observed_mcp)
        self.assertEqual(
            "success",
            observed_runner.run(
                "task_project_register",
                context(
                    project_item_id="PVTI_1",
                    partial_receipt=recovery_receipt(),
                ),
            ),
        )
        self.assertEqual([], observed_runner.capability_preflights)
        self.assertEqual([], observed_mcp.writes)

        missing_mcp = FakeGitHubMCP(issues={"issue": issue_record()})
        missing_runner = ContractRunner(self.contract, missing_mcp)
        receipt = recovery_receipt(
            state="project_item_missing",
            project_item_id=None,
            initial_field_plan=initial_field_plan(
                Status={"source": "requested", "value": "Ready"}
            ),
            unfinished_transitions=[
                "project_item",
                "requested_status",
                "default_priority",
            ],
        )
        self.assertEqual(
            "success",
            missing_runner.run(
                "task_project_register",
                context(
                    project_item_id=None,
                    partial_receipt=receipt,
                ),
            ),
        )
        self.assertEqual(
            [
                (
                    "project_item",
                    ("project_item_read", "project_item_add"),
                ),
                (
                    "requested_status",
                    ("project_status_read", "project_status_update"),
                ),
                (
                    "default_priority",
                    (
                        "project_priority_read",
                        "project_priority_update",
                    ),
                ),
            ],
            getattr(missing_runner, "capability_preflights", []),
        )

    def test_unknown_project_add_and_update_read_back_before_any_retry(self) -> None:
        self._seed_issue()
        self.mcp.fail_next("project_item_add", "after")
        self.mcp.fail_next("project_status_set_default", "after")
        self.assertEqual(
            "success",
            self.runner.run(
                "task_project_register",
                context(partial_receipt=partial_receipt()),
            ),
        )
        self.assertEqual(1, self.mcp.writes.count("project_item_add"))
        self.assertEqual(1, self.mcp.writes.count("project_status_set_default"))

    def test_unknown_before_project_add_reads_back_before_retrying_once(self) -> None:
        self._seed_issue()
        self.mcp.fail_next("project_item_add", "unknown_before")
        self.assertEqual(
            "success",
            self.runner.run(
                "task_project_register",
                context(partial_receipt=partial_receipt()),
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
        self._seed_task()
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
        self._seed_task()
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
        for outcome in (
            "blocked",
            "ambiguous",
            "duplicate",
            "bulk",
            "destructive",
            "confirmation-needed",
        ):
            with self.subTest(outcome=outcome):
                mcp = FakeGitHubMCP()
                runner = ContractRunner(self.contract, mcp)
                self.assertEqual(
                    outcome,
                    runner.run("task_create", context(guard_outcome=outcome)),
                )
                self.assertEqual([], mcp.writes)

    def test_only_allowlisted_guard_outcomes_can_write(self) -> None:
        for outcome in ("eligible", "explicit", "inferred"):
            with self.subTest(outcome=outcome):
                mcp = FakeGitHubMCP()
                runner = ContractRunner(self.contract, mcp)
                self.assertEqual(
                    "success",
                    runner.run(
                        "task_create", context(guard_outcome=outcome)
                    ),
                )
                self.assertIn("issue_create", mcp.writes)

        for outcome in (None, "", "approved", "future-new-outcome"):
            with self.subTest(outcome=outcome):
                mcp = FakeGitHubMCP()
                runner = ContractRunner(self.contract, mcp)
                self.assertEqual(
                    "blocked",
                    runner.run(
                        "task_create", context(guard_outcome=outcome)
                    ),
                )
                self.assertEqual([], mcp.writes)

    def test_existing_project_item_is_preserved_during_register_resume(self) -> None:
        self._seed_issue()
        self._seed_item(
            item_id="PVTI_existing",
            fields={
                "Status": "Backlog",
                "Priority": "P1",
                "Due date": "2026-08-20",
            },
        )
        before = copy.deepcopy(self.mcp.project_items)

        self.assertEqual(
            "success",
            self.runner.run(
                "task_project_register",
                context(
                    issue_node_id="I_1",
                    partial_receipt=partial_receipt(),
                ),
            ),
        )
        self.assertEqual(before, self.mcp.project_items)
        self.assertEqual([], self.mcp.writes)

    def test_new_item_honors_explicit_initial_fields(self) -> None:
        requested = {
            "Status": "Ready",
            "Priority": "P1",
            "Due date": "2026-08-20",
        }
        self.assertEqual(
            "success",
            self.runner.run(
                "task_create", context(initial_fields=requested)
            ),
        )
        self.assertEqual(
            requested,
            only_project_item(self.mcp)["fields"],
        )

    def test_register_rejects_boolean_resume_without_exact_receipt(self) -> None:
        self._seed_issue()
        self.assertEqual(
            "blocked",
            self.runner.run(
                "task_project_register",
                context(partial_resume=True),
            ),
        )
        self.assertEqual([], self.runner.local_preflights)
        self.assertEqual([], self.mcp.writes)

    def test_register_rejects_boolean_issue_number_in_receipt(self) -> None:
        self._seed_issue()
        malformed = partial_receipt(
            issue_number=True,
            issue_node_id=None,
        )

        self.assertEqual(
            "blocked",
            self.runner.run(
                "task_project_register",
                context(
                    issue_number=True,
                    issue_node_id=None,
                    partial_receipt=malformed,
                ),
            ),
        )
        self.assertEqual([], self.mcp.writes)
        self.assertEqual([], self.runner.local_preflights)

    def test_wrong_project_link_is_not_accepted_as_exact_readback(self) -> None:
        self._seed_issue()
        self.mcp.project_items["sha256:abc"] = {
            "item_id": "PVTI_wrong",
            "project_url": "https://github.com/orgs/other/projects/99",
            "issue_number": 99,
            "issue_node_id": "I_wrong",
            "fields": {
                "Status": "Inbox",
                "Priority": "P2",
                "Due date": None,
            },
        }
        self.assertEqual(
            "success",
            self.runner.run(
                "task_project_register",
                context(
                    issue_node_id="I_1",
                    partial_receipt=partial_receipt(),
                ),
            ),
        )
        self.assertIn("project_item_add", self.mcp.writes)
        linked_items = [
            item
            for item in self.mcp.project_items.values()
            if item.get("project_url") == PROJECT_URL
            and item.get("issue_node_id") == "I_1"
        ]
        self.assertEqual(1, len(linked_items))

    def test_wrong_issue_identity_cannot_satisfy_exact_readback(self) -> None:
        self._seed_issue()
        self.assertEqual(
            "partial",
            self.runner.run(
                "task_update_issue",
                context(
                    issue_number=99,
                    issue_node_id=None,
                    requested_field="title",
                    requested_value="Wrong target",
                ),
            ),
        )

    def test_canonical_task_key_vectors_are_cross_host_stable(self) -> None:
        canonical_bytes = (
            '{"repository":"the3-inc/companies",'
            '"project_url":"https://github.com/orgs/the3-inc/projects/7",'
            '"outcome":"Café launch\\nnow",'
            '"acceptance_criteria":["Ready for use","Docs\\npublished"],'
            '"references":["https://example.com/a","specs/plan.md"]}'
        ).encode("utf-8")
        payload = json.loads(canonical_bytes)
        self.assertEqual(
            [
                "repository",
                "project_url",
                "outcome",
                "acceptance_criteria",
                "references",
            ],
            list(payload),
        )
        self.assertEqual(
            canonical_bytes,
            json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8"),
        )
        self.assertEqual(
            "3f9fc3661920a8d3fefaa15a83789083a99521dd61994da2b396f5a03b6ed7f2",
            hashlib.sha256(canonical_bytes).hexdigest(),
        )
        self.assertIn(
            canonical_bytes.decode("utf-8"),
            (SKILL_ROOT / "references" / "issue-contract.md").read_text(
                encoding="utf-8"
            ),
        )

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
        self._seed_issue()
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
                context(
                    requested_field="title",
                    requested_value="Updated title",
                ),
            ),
        )

    def test_wrong_terminal_read_after_cannot_be_masked_by_final_read(self) -> None:
        self._seed_issue()
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
                context(remaining_sides={"issue"}),
            ),
        )

    def test_unknown_read_action_fails_instead_of_inspecting_global_state(self) -> None:
        self._seed_issue()
        mutated = copy.deepcopy(self.contract)
        update = next(
            op for op in mutated["operations"] if op["name"] == "task_update_issue"
        )
        update["steps"][0]["read_after"] = "nonsense_read"

        runner = ContractRunner(mutated, self.mcp)
        with self.assertRaises(AssertionError):
            runner.run(
                "task_update_issue",
                context(
                    requested_field="title",
                    requested_value="Updated title",
                ),
            )

    def test_register_requires_explicit_partial_resume_before_preflight_or_write(
        self,
    ) -> None:
        self._seed_issue()
        self.assertEqual(
            "blocked",
            self.runner.run(
                "task_project_register", context()
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
            issues={"sha256:abc": issue_record()},
            project_items={
                "sha256:abc": project_item_record()
            },
        )
        terminal_runner = ContractRunner(self.contract, terminal_mcp)
        self.assertEqual(
            "success",
            terminal_runner.run(
                "task_complete",
                context(remaining_sides={"issue", "project"}),
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
                        context(remaining_sides=remaining_sides),
                    ),
                )
                self.assertEqual([], mcp.writes)

        mcp = FakeGitHubMCP(
            issues={"sha256:abc": issue_record()},
            project_items={
                "sha256:abc": project_item_record(
                    fields={
                        "Status": "Done",
                        "Priority": "P2",
                        "Due date": None,
                    }
                )
            },
        )
        runner = ContractRunner(self.contract, mcp)
        self.assertEqual(
            "success",
            runner.run(
                "task_complete",
                context(remaining_sides={"issue"}),
            ),
        )
        self.assertEqual(["issue_close_requested"], mcp.writes)
        self.assertEqual(["task_complete:issue"], runner.local_preflights)

    def test_register_and_update_accept_exact_minimal_operation_contexts(self) -> None:
        self._seed_issue()
        self.assertEqual(
            "success",
            self.runner.run(
                "task_project_register",
                context(partial_receipt=partial_receipt()),
            ),
        )
        self.assertEqual(
            "success",
            self.runner.run(
                "task_update_issue",
                context(
                    requested_field="title",
                    requested_value="Minimal update",
                ),
            ),
        )


if __name__ == "__main__":
    unittest.main()
