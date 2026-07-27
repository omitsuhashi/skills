"""Test-only fake GitHub MCP and declarative contract runner."""

from __future__ import annotations

import configparser
import copy
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


class UnknownOutcome(RuntimeError):
    """The remote result is unknown and must be read back before retry."""


class WriteFailed(RuntimeError):
    """The remote write failed before it changed state."""


@dataclass(frozen=True)
class ReadObservation:
    action: str
    payload: dict[str, Any]


@dataclass
class FakeGitHubMCP:
    issues: dict[str, dict[str, Any]] = field(default_factory=dict)
    project_items: dict[str, dict[str, Any]] = field(default_factory=dict)
    calls: list[str] = field(default_factory=list)
    failures: dict[str, list[str]] = field(default_factory=dict)

    def fail_next(self, action: str, mode: str) -> None:
        self.failures.setdefault(action, []).append(mode)

    @property
    def writes(self) -> list[str]:
        return [
            call.removeprefix("write:")
            for call in self.calls
            if call.startswith("write:")
        ]

    def read(
        self, action: str, context: dict[str, Any]
    ) -> ReadObservation:
        self.calls.append(f"read:{action}")
        task_key = context["task_key"]
        if action in {"issue_search_exact", "issue_read_exact"}:
            issue = copy.deepcopy(self.issues.get(task_key))
            payload = {"issue": issue}
        elif action == "project_item_read_exact":
            item = copy.deepcopy(self.project_items.get(task_key))
            payload = {"item": item}
        elif action == "project_status_read":
            item = copy.deepcopy(self.project_items.get(task_key))
            payload = {
                "exists": item is not None,
                "value": None if item is None else item["fields"].get("Status"),
            }
        elif action == "project_priority_read":
            item = copy.deepcopy(self.project_items.get(task_key))
            payload = {
                "exists": item is not None,
                "value": None
                if item is None
                else item["fields"].get("Priority"),
            }
        elif action == "project_due_date_read":
            item = copy.deepcopy(self.project_items.get(task_key))
            payload = {
                "exists": item is not None,
                "value": None
                if item is None
                else item["fields"].get("Due date"),
            }
        elif action == "project_field_read":
            item = copy.deepcopy(self.project_items.get(task_key))
            field_name = context["requested_field"]
            payload = {
                "exists": item is not None,
                "field": field_name,
                "value": None
                if item is None
                else item["fields"].get(field_name),
            }
        elif action == "issue_comment_read":
            issue = copy.deepcopy(self.issues.get(task_key))
            payload = {
                "exists": issue is not None,
                "comments": [] if issue is None else issue["comments"],
            }
        elif action == "issue_terminal_read":
            issue = copy.deepcopy(self.issues.get(task_key))
            payload = {
                "exists": issue is not None,
                "close_reason": None
                if issue is None
                else issue["close_reason"],
            }
        elif action == "project_terminal_status_read":
            item = copy.deepcopy(self.project_items.get(task_key))
            payload = {
                "exists": item is not None,
                "status": None
                if item is None
                else item["fields"].get("Status"),
            }
        else:
            raise AssertionError(f"unknown fake read: {action}")
        return ReadObservation(action=action, payload=payload)

    def observe(
        self,
        condition: str,
        observation: ReadObservation,
        context: dict[str, Any],
    ) -> bool:
        compatible_actions = {
            "issue_search_match": {"issue_search_exact"},
            "exact_issue_readback": {"issue_read_exact"},
            "project_item_exists": {"project_item_read_exact"},
            "default_status_observed": {"project_status_read"},
            "default_priority_observed": {"project_priority_read"},
            "due_date_empty_observed": {"project_due_date_read"},
            "requested_issue_property_observed": {"issue_read_exact"},
            "requested_project_field_observed": {"project_field_read"},
            "exact_comment_observed": {"issue_comment_read"},
            "issue_terminal_observed": {"issue_terminal_read"},
            "project_terminal_observed": {"project_terminal_status_read"},
        }
        if condition not in compatible_actions:
            raise AssertionError(f"unknown observation condition: {condition}")
        if observation.action not in compatible_actions[condition]:
            return False

        payload = observation.payload
        if condition in {"issue_search_match", "exact_issue_readback"}:
            return payload["issue"] is not None
        if condition == "project_item_exists":
            return payload["item"] is not None
        if condition == "default_status_observed":
            return payload["exists"] and payload["value"] == "Inbox"
        if condition == "default_priority_observed":
            return payload["exists"] and payload["value"] == "P2"
        if condition == "due_date_empty_observed":
            return payload["exists"] and payload["value"] is None
        if condition == "requested_issue_property_observed":
            issue = payload["issue"]
            return issue is not None and issue.get(
                context["requested_field"]
            ) == context["requested_value"]
        if condition == "requested_project_field_observed":
            return (
                payload["exists"]
                and payload["field"] == context["requested_field"]
                and payload["value"] == context["requested_value"]
            )
        if condition == "exact_comment_observed":
            return (
                payload["exists"]
                and context["comment"] in payload["comments"]
            )
        if condition == "issue_terminal_observed":
            return (
                payload["exists"]
                and payload["close_reason"] == context["close_reason"]
            )
        return (
            payload["exists"]
            and payload["status"] == context["terminal_status"]
        )

    def write(self, action: str, context: dict[str, Any]) -> None:
        self.calls.append(f"write:{action}")
        failure = self.failures.get(action, [])
        mode = failure.pop(0) if failure else None
        if mode == "before":
            raise WriteFailed(action)

        task_key = context["task_key"]
        issue = self.issues.get(task_key)
        item = self.project_items.get(task_key)
        if action == "issue_create":
            self.issues.setdefault(
                task_key,
                {
                    "number": len(self.issues) + 1,
                    "title": context.get("title", "Task"),
                    "body": context.get("body", ""),
                    "comments": [],
                    "close_reason": None,
                },
            )
        elif action == "project_item_add":
            self.project_items.setdefault(
                task_key,
                {"issue_number": self.issues[task_key]["number"], "fields": {}},
            )
        elif action == "project_status_set_default":
            item["fields"]["Status"] = "Inbox"
        elif action == "project_priority_set_default":
            item["fields"]["Priority"] = "P2"
        elif action == "issue_update_requested":
            issue[context["requested_field"]] = context["requested_value"]
        elif action == "project_field_update_requested":
            item["fields"][context["requested_field"]] = context["requested_value"]
        elif action == "issue_comment_create":
            if context["comment"] not in issue["comments"]:
                issue["comments"].append(context["comment"])
        elif action == "issue_close_requested":
            issue["close_reason"] = context["close_reason"]
        elif action == "project_status_set_terminal":
            item["fields"]["Status"] = context["terminal_status"]
        else:
            raise AssertionError(f"unknown fake write: {action}")

        if mode == "after":
            raise UnknownOutcome(action)
        if mode == "unknown_before":
            self._undo(action, context)
            raise UnknownOutcome(action)

    def _undo(self, action: str, context: dict[str, Any]) -> None:
        task_key = context["task_key"]
        if action == "project_item_add":
            self.project_items.pop(task_key, None)
        elif action == "issue_create":
            self.issues.pop(task_key, None)
        else:
            raise AssertionError("unknown_before is used only for create/add tests")


def load_contract(path: Path) -> dict[str, Any]:
    """Load the simple scalar/section TOML subset with the Python 3.9 stdlib."""
    def decode(values: configparser.SectionProxy) -> dict[str, Any]:
        return {key: json.loads(value) for key, value in values.items()}

    parser = configparser.ConfigParser(interpolation=None)
    parser.read(path, encoding="utf-8")
    contract: dict[str, Any] = {
        "contract": decode(parser["contract"]),
        "operations": [],
    }
    operations: dict[str, dict[str, Any]] = {}
    for section_name in parser.sections():
        parts = section_name.split(".")
        if parts[0] != "operation":
            continue
        operation = operations.setdefault(
            parts[1],
            {
                "name": parts[1],
                "steps": [],
                "final_observations": [],
            },
        )
        if len(parts) == 2:
            operation.update(decode(parser[section_name]))
        elif parts[2] == "step":
            operation["steps"].append(
                {"id": parts[3], **decode(parser[section_name])}
            )
        elif parts[2] == "final":
            operation["final_observations"].append(
                {"id": parts[3], **decode(parser[section_name])}
            )
    contract["operations"] = list(operations.values())
    for operation in contract["operations"]:
        for step in operation.get("steps", []):
            step.setdefault("retry_after_unknown", False)
    validate_contract(contract)
    return contract


def validate_contract(contract: dict[str, Any]) -> None:
    allowed_preflights = {"once", "per_remaining_side"}
    for operation in contract.get("operations", []):
        if operation.get("local_preflight") not in allowed_preflights:
            raise AssertionError(
                f"{operation.get('name', '<unnamed>')} has unknown local_preflight"
            )
        if not isinstance(operation.get("retry_only"), bool):
            raise AssertionError(
                f"{operation.get('name', '<unnamed>')} has invalid retry_only"
            )
        for step in operation.get("steps", []):
            missing = {
                "id",
                "read_before",
                "write",
                "read_after",
                "observed",
            } - step.keys()
            if missing:
                raise AssertionError(
                    f"{operation.get('name', '<unnamed>')} step lacks {sorted(missing)}"
                )
        for observation in operation.get("final_observations", []):
            if {"read", "observed"} - observation.keys():
                raise AssertionError(
                    f"{operation.get('name', '<unnamed>')} final observation is incomplete"
                )

    terminal = next(
        (
            operation
            for operation in contract.get("operations", [])
            if operation.get("name") == "task_complete"
        ),
        None,
    )
    if terminal is None:
        raise AssertionError("missing task_complete operation")
    terminal_steps = {step["id"]: step for step in terminal["steps"]}
    terminal_finals = {
        observation["id"]: observation
        for observation in terminal["final_observations"]
    }
    expected_sides = {"issue", "project"}
    if terminal_steps.keys() != expected_sides:
        raise AssertionError("task_complete must have exact issue/project steps")
    if terminal_finals.keys() != expected_sides:
        raise AssertionError(
            "task_complete must have exact issue/project final observations"
        )
    for side in expected_sides:
        if terminal_steps[side].get("side") != side:
            raise AssertionError(
                f"task_complete {side} step has invalid side"
            )
        if terminal_finals[side].get("side") != side:
            raise AssertionError(
                f"task_complete {side} final observation has invalid side"
            )


class ContractRunner:
    """Interpret the reference contract against the test-only fake remote."""

    def __init__(self, contract: dict[str, Any], mcp: FakeGitHubMCP):
        validate_contract(contract)
        self.contract = contract
        self.mcp = mcp
        self.local_preflights: list[str] = []
        self.events: list[str] = []

    def run(self, operation_name: str, context: dict[str, Any]) -> str:
        guarded = set(self.contract["contract"]["zero_write_outcomes"])
        if context.get("guard_outcome") in guarded:
            return context["guard_outcome"]

        operation = next(
            operation
            for operation in self.contract["operations"]
            if operation["name"] == operation_name
        )
        if operation["retry_only"] and context.get("partial_resume") is not True:
            return "blocked"

        remaining_sides: frozenset[str] | None = None
        if operation_name == "task_complete":
            supplied_sides = context.get("remaining_sides")
            if not isinstance(supplied_sides, (set, frozenset, list, tuple)):
                return "blocked"
            remaining_sides = frozenset(supplied_sides)
            if not remaining_sides or not remaining_sides <= {
                "issue",
                "project",
            }:
                return "blocked"

        preflighted_once = False
        preflighted_sides: set[str] = set()

        for step in operation["steps"]:
            if not self._applies(step, remaining_sides):
                continue
            read_before_observed = step.get(
                "read_before_observed", step["observed"]
            )
            if self._read_observed(
                step["read_before"], read_before_observed, context
            ):
                continue
            preflighted_once = self._record_preflight(
                operation,
                step,
                remaining_sides,
                preflighted_once,
                preflighted_sides,
            )
            if not self._write_then_observe(step, context):
                return "partial"

        for observation in operation["final_observations"]:
            if not self._applies(observation, remaining_sides):
                continue
            if not self._read_observed(
                observation["read"], observation["observed"], context
            ):
                return "partial"
        return "success"

    def _write_then_observe(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> bool:
        outcome_unknown = False
        self.events.append(f"write:{step['write']}")
        try:
            self.mcp.write(step["write"], context)
        except UnknownOutcome:
            outcome_unknown = True
        except WriteFailed:
            pass
        if self._read_observed(step["read_after"], step["observed"], context):
            return True
        if outcome_unknown and step.get("retry_after_unknown", False):
            self.events.append(f"write:{step['write']}")
            try:
                self.mcp.write(step["write"], context)
            except (UnknownOutcome, WriteFailed):
                pass
            return self._read_observed(
                step["read_after"], step["observed"], context
            )
        return False

    def _read_observed(
        self, read_action: str, condition: str, context: dict[str, Any]
    ) -> bool:
        observation = self.mcp.read(read_action, context)
        return self.mcp.observe(condition, observation, context)

    def _record_preflight(
        self,
        operation: dict[str, Any],
        step: dict[str, Any],
        remaining_sides: frozenset[str] | None,
        preflighted_once: bool,
        preflighted_sides: set[str],
    ) -> bool:
        mode = operation["local_preflight"]
        if mode == "once":
            if not preflighted_once:
                entry = operation["name"]
                self.local_preflights.append(entry)
                self.events.append(f"preflight:{entry}")
            return True

        side = step.get("side")
        if (
            side is None
            or remaining_sides is None
            or side not in remaining_sides
        ):
            raise AssertionError("per-side preflight lacks declared side")
        if side not in preflighted_sides:
            entry = f"{operation['name']}:{side}"
            self.local_preflights.append(entry)
            self.events.append(f"preflight:{entry}")
            preflighted_sides.add(side)
        return preflighted_once

    @staticmethod
    def _applies(
        transition: dict[str, Any],
        remaining_sides: frozenset[str] | None,
    ) -> bool:
        side = transition.get("side")
        return side is None or (
            remaining_sides is not None and side in remaining_sides
        )
