"""Test-only fake GitHub MCP and declarative contract runner."""

from __future__ import annotations

import configparser
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


class UnknownOutcome(RuntimeError):
    """The remote result is unknown and must be read back before retry."""


class WriteFailed(RuntimeError):
    """The remote write failed before it changed state."""


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
        return [call.removeprefix("write:") for call in self.calls if call.startswith("write:")]

    def read(self, action: str, context: dict[str, Any]) -> None:
        self.calls.append(f"read:{action}")

    def observe(self, condition: str, context: dict[str, Any]) -> bool:
        issue = self.issues.get(context["task_key"])
        item = self.project_items.get(context["task_key"])
        observations = {
            "issue_exists": issue is not None,
            "project_item_exists": item is not None,
            "default_status_observed": item is not None
            and item["fields"].get("Status") == "Inbox",
            "default_priority_observed": item is not None
            and item["fields"].get("Priority") == "P2",
            "due_date_empty_observed": item is not None
            and item["fields"].get("Due date") is None,
            "requested_issue_property_observed": issue is not None
            and issue.get(context["requested_field"]) == context["requested_value"],
            "requested_project_field_observed": item is not None
            and item["fields"].get(context["requested_field"])
            == context["requested_value"],
            "exact_comment_observed": issue is not None
            and context["comment"] in issue["comments"],
            "issue_terminal_observed": issue is not None
            and issue["close_reason"] == context["close_reason"],
            "project_terminal_observed": item is not None
            and item["fields"].get("Status") == context["terminal_status"],
        }
        return observations[condition]

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
    for operation in contract["operations"]:
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
    return contract


class ContractRunner:
    """Interpret the reference contract against the test-only fake remote."""

    def __init__(self, contract: dict[str, Any], mcp: FakeGitHubMCP):
        self.contract = contract
        self.mcp = mcp
        self.local_preflights: list[str] = []

    def run(self, operation_name: str, context: dict[str, Any]) -> str:
        guarded = set(self.contract["contract"]["zero_write_outcomes"])
        if context.get("guard_outcome") in guarded:
            return context["guard_outcome"]

        operation = next(
            operation
            for operation in self.contract["operations"]
            if operation["name"] == operation_name
        )
        preflight = operation["local_preflight"]
        if preflight == "once":
            self.local_preflights.append(operation_name)

        for step in operation["steps"]:
            if not self._applies(step, context):
                continue
            if self._read_observed(step["read_before"], step["observed"], context):
                continue
            if not self._write_then_observe(step, context):
                return "partial"

        for observation in operation["final_observations"]:
            if not self._read_observed(
                observation["read"], observation["observed"], context
            ):
                return "partial"
        return "success"

    def _write_then_observe(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> bool:
        outcome_unknown = False
        try:
            self.mcp.write(step["write"], context)
        except UnknownOutcome:
            outcome_unknown = True
        except WriteFailed:
            pass
        if self._read_observed(step["read_after"], step["observed"], context):
            return True
        if outcome_unknown and step.get("retry_after_unknown", False):
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
        self.mcp.read(read_action, context)
        return self.mcp.observe(condition, context)

    @staticmethod
    def _applies(step: dict[str, Any], context: dict[str, Any]) -> bool:
        side = step.get("side")
        return side is None or side in context.get("remaining_sides", {"issue", "project"})
