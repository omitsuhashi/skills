"""Test-only fake GitHub MCP and declarative contract runner."""

from __future__ import annotations

import configparser
import copy
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


_PROJECT_FIELD_READS = {
    "project_status_read": "Status",
    "project_priority_read": "Priority",
    "project_due_date_read": "Due date",
}
_PROJECT_FIELD_WRITES = {
    "project_status_set_default": ("Status", "Inbox"),
    "project_status_set_requested_initial": ("Status", None),
    "project_priority_set_default": ("Priority", "P2"),
    "project_priority_set_requested_initial": ("Priority", None),
    "project_due_date_set_requested_initial": ("Due date", None),
}
_STATIC_FIELD_OBSERVATIONS = {
    "default_status_observed": "Inbox",
    "default_priority_observed": "P2",
    "due_date_empty_observed": None,
}
_REQUESTED_FIELD_OBSERVATIONS = {
    "requested_initial_status_observed": "Status",
    "requested_initial_priority_observed": "Priority",
    "requested_initial_due_date_observed": "Due date",
}


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
    _last_created_issue_key: str | None = field(default=None, init=False)
    _last_created_item_key: str | None = field(default=None, init=False)

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
        if action == "issue_search_exact":
            matches = [
                copy.deepcopy(issue)
                for issue in self._marker_issue_matches(context)
            ]
            payload = {"matches": matches, "match_count": len(matches)}
        elif action == "issue_read_exact":
            payload = {"issue": copy.deepcopy(self._exact_issue(context))}
        elif action == "project_item_read_exact":
            matches = self._project_item_matches(context)
            payload = {
                "item": copy.deepcopy(matches[0])
                if len(matches) == 1
                else None,
                "match_count": len(matches),
            }
        elif action in _PROJECT_FIELD_READS:
            item = copy.deepcopy(self._exact_item(context))
            field_name = _PROJECT_FIELD_READS[action]
            payload = {
                "exists": item is not None,
                "value": None
                if item is None
                else item["fields"].get(field_name),
            }
        elif action == "project_field_read":
            item = copy.deepcopy(self._exact_item(context))
            field_name = context["requested_field"]
            payload = {
                "exists": item is not None,
                "field": field_name,
                "value": None
                if item is None
                else item["fields"].get(field_name),
            }
        elif action == "issue_comment_read":
            issue = copy.deepcopy(self._exact_issue(context))
            payload = {
                "exists": issue is not None,
                "comments": [] if issue is None else issue["comments"],
            }
        elif action == "issue_terminal_read":
            issue = copy.deepcopy(self._exact_issue(context))
            payload = {
                "exists": issue is not None,
                "close_reason": None
                if issue is None
                else issue["close_reason"],
            }
        elif action == "project_terminal_status_read":
            item = copy.deepcopy(self._exact_item(context))
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
            "unique_issue_marker_match": {"issue_search_exact"},
            "unique_issue_identity_resolved": {"issue_search_exact"},
            "multiple_issue_marker_matches": {"issue_search_exact"},
            "exact_issue_readback": {"issue_read_exact"},
            "project_item_exists": {"project_item_read_exact"},
            "default_status_observed": {"project_status_read"},
            "requested_initial_status_observed": {"project_status_read"},
            "default_priority_observed": {"project_priority_read"},
            "requested_initial_priority_observed": {"project_priority_read"},
            "due_date_empty_observed": {"project_due_date_read"},
            "requested_initial_due_date_observed": {"project_due_date_read"},
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
        if condition in {
            "issue_search_match",
            "unique_issue_marker_match",
            "unique_issue_identity_resolved",
        }:
            return payload["match_count"] == 1
        if condition == "multiple_issue_marker_matches":
            return payload["match_count"] > 1
        if condition == "exact_issue_readback":
            return payload["issue"] is not None
        if condition == "project_item_exists":
            return payload["match_count"] == 1 and payload["item"] is not None
        if condition in _STATIC_FIELD_OBSERVATIONS:
            return (
                payload["exists"]
                and payload["value"]
                == _STATIC_FIELD_OBSERVATIONS[condition]
            )
        if condition in _REQUESTED_FIELD_OBSERVATIONS:
            field_name = _REQUESTED_FIELD_OBSERVATIONS[condition]
            return (
                payload["exists"]
                and payload["value"]
                == context.get("initial_fields", {}).get(field_name)
            )
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

        issue = self._exact_issue(context)
        item = self._exact_item(context)
        created_issue: dict[str, Any] | None = None
        created_item: dict[str, Any] | None = None
        if action == "issue_create":
            number = max(
                (
                    value.get("number", 0)
                    for value in self.issues.values()
                    if isinstance(value.get("number"), int)
                ),
                default=0,
            ) + 1
            node_id = f"I_{number}"
            created_issue = {
                "number": number,
                "node_id": node_id,
                "repository": context["repository"],
                "marker": context["task_key"],
                "title": context.get("title", "Task"),
                "body": context.get("body", ""),
                "comments": [],
                "close_reason": None,
            }
            self.issues[node_id] = created_issue
            self._last_created_issue_key = node_id
        elif action == "project_item_add":
            if issue is None:
                raise WriteFailed("project_item_add lacks exact Issue")
            item_id = f"PVTI_{len(self.project_items) + 1}"
            created_item = {
                "item_id": item_id,
                "project_url": context["project_url"],
                "issue_number": issue["number"],
                "issue_node_id": issue["node_id"],
                "fields": {},
            }
            self.project_items[item_id] = created_item
            self._last_created_item_key = item_id
        elif action in _PROJECT_FIELD_WRITES:
            if item is None:
                raise WriteFailed(action)
            field_name, default = _PROJECT_FIELD_WRITES[action]
            item["fields"][field_name] = (
                default
                if default is not None
                else context["initial_fields"][field_name]
            )
        elif action == "issue_update_requested":
            if issue is None:
                raise WriteFailed(action)
            issue[context["requested_field"]] = context["requested_value"]
        elif action == "project_field_update_requested":
            if item is None:
                raise WriteFailed(action)
            item["fields"][context["requested_field"]] = context["requested_value"]
        elif action == "issue_comment_create":
            if issue is None:
                raise WriteFailed(action)
            if context["comment"] not in issue["comments"]:
                issue["comments"].append(context["comment"])
        elif action == "issue_close_requested":
            if issue is None:
                raise WriteFailed(action)
            issue["close_reason"] = context["close_reason"]
        elif action == "project_status_set_terminal":
            if item is None:
                raise WriteFailed(action)
            item["fields"]["Status"] = context["terminal_status"]
        else:
            raise AssertionError(f"unknown fake write: {action}")

        if mode == "after":
            raise UnknownOutcome(action)
        if mode == "unknown_before":
            self._undo(action, context)
            raise UnknownOutcome(action)
        if created_issue is not None:
            context["issue_number"] = created_issue["number"]
            context["issue_node_id"] = created_issue["node_id"]
        if created_item is not None:
            context["project_item_id"] = created_item["item_id"]

    def _undo(self, action: str, context: dict[str, Any]) -> None:
        if action == "project_item_add":
            if self._last_created_item_key is not None:
                self.project_items.pop(self._last_created_item_key, None)
        elif action == "issue_create":
            if self._last_created_issue_key is not None:
                self.issues.pop(self._last_created_issue_key, None)
        else:
            raise AssertionError("unknown_before is used only for create/add tests")

    def bind_unique_issue_identity(
        self, observation: ReadObservation, context: dict[str, Any]
    ) -> bool:
        matches = observation.payload.get("matches", [])
        if len(matches) != 1:
            return False
        issue = matches[0]
        context["issue_number"] = issue["number"]
        context["issue_node_id"] = issue["node_id"]
        return True

    def bind_project_item_identity(
        self, observation: ReadObservation, context: dict[str, Any]
    ) -> bool:
        item = observation.payload.get("item")
        if item is None:
            return False
        context["project_item_id"] = item["item_id"]
        return True

    def _marker_issue_matches(
        self, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        return [
            issue
            for issue in self.issues.values()
            if issue.get("repository") == context.get("repository")
            and issue.get("marker") == context.get("task_key")
            and isinstance(issue.get("number"), int)
            and issue.get("number", 0) > 0
            and isinstance(issue.get("node_id"), str)
            and issue.get("node_id")
        ]

    def _exact_issue(
        self, context: dict[str, Any]
    ) -> dict[str, Any] | None:
        number = context.get("issue_number")
        node_id = context.get("issue_node_id")
        if number is None and node_id is None:
            return None
        matches = [
            issue
            for issue in self._marker_issue_matches(context)
            if (number is None or issue.get("number") == number)
            and (node_id is None or issue.get("node_id") == node_id)
        ]
        return matches[0] if len(matches) == 1 else None

    def _project_item_matches(
        self, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        issue = self._exact_issue(context)
        if issue is None:
            return []
        item_id = context.get("project_item_id")
        return [
            item
            for item in self.project_items.values()
            if item.get("project_url") == context.get("project_url")
            and item.get("issue_number") == issue.get("number")
            and item.get("issue_node_id") == issue.get("node_id")
            and (item_id is None or item.get("item_id") == item_id)
        ]

    def _exact_item(
        self, context: dict[str, Any]
    ) -> dict[str, Any] | None:
        matches = self._project_item_matches(context)
        return matches[0] if len(matches) == 1 else None


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
    allowed_conditions = {
        "project_item_created_this_invocation_and_status_omitted",
        "project_item_created_this_invocation_and_status_supplied",
        "project_item_created_this_invocation_and_priority_omitted",
        "project_item_created_this_invocation_and_priority_supplied",
        "project_item_created_this_invocation_and_due_date_omitted",
        "project_item_created_this_invocation_and_due_date_supplied",
    }
    metadata = contract.get("contract", {})
    write_eligible = metadata.get("write_eligible_outcomes")
    zero_write = metadata.get("zero_write_outcomes")
    if (
        not isinstance(write_eligible, list)
        or not write_eligible
        or not all(isinstance(value, str) for value in write_eligible)
    ):
        raise AssertionError("contract lacks a write-outcome allowlist")
    if (
        not isinstance(zero_write, list)
        or not all(isinstance(value, str) for value in zero_write)
        or set(write_eligible) & set(zero_write)
    ):
        raise AssertionError("contract has an invalid zero-write outcome set")
    if metadata.get("unknown_guard_outcome") not in zero_write:
        raise AssertionError("unknown guard outcome must fail closed")

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
            if (
                "applies_when" in step
                and step["applies_when"] not in allowed_conditions
            ):
                raise AssertionError(
                    f"{operation.get('name', '<unnamed>')} step has unknown condition"
                )
            if "unknown_resolver" in step and {
                "unknown_resolver_observed",
                "unknown_resolver_ambiguous",
            } - step.keys():
                raise AssertionError(
                    f"{operation.get('name', '<unnamed>')} unknown resolver is incomplete"
                )
        for observation in operation.get("final_observations", []):
            if {"read", "observed"} - observation.keys():
                raise AssertionError(
                    f"{operation.get('name', '<unnamed>')} final observation is incomplete"
                )
            if (
                "applies_when" in observation
                and observation["applies_when"] not in allowed_conditions
            ):
                raise AssertionError(
                    f"{operation.get('name', '<unnamed>')} final has unknown condition"
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
        metadata = self.contract["contract"]
        zero_write = set(metadata["zero_write_outcomes"])
        write_eligible = set(metadata["write_eligible_outcomes"])
        guard_outcome = context.get("guard_outcome")
        if guard_outcome in zero_write:
            return guard_outcome
        if guard_outcome not in write_eligible:
            return metadata["unknown_guard_outcome"]

        operation = next(
            operation
            for operation in self.contract["operations"]
            if operation["name"] == operation_name
        )
        if operation["retry_only"] and not self._bind_partial_receipt(
            operation, context
        ):
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
            if not self._applies(step, remaining_sides, context):
                continue
            read_before_observed = step.get(
                "read_before_observed", step["observed"]
            )
            before = self.mcp.read(step["read_before"], context)
            ambiguous_condition = step.get("read_before_ambiguous")
            if (
                ambiguous_condition is not None
                and self.mcp.observe(
                    ambiguous_condition, before, context
                )
            ):
                return "ambiguous"
            if self.mcp.observe(read_before_observed, before, context):
                if step["read_before"] == "project_item_read_exact":
                    self.mcp.bind_project_item_identity(before, context)
                observed_outcome = step.get("on_read_before_observed")
                if observed_outcome is not None:
                    return observed_outcome
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
            if step["write"] == "project_item_add":
                context["_project_item_created_this_invocation"] = True

        for observation in operation["final_observations"]:
            if not self._applies(
                observation, remaining_sides, context
            ):
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
        if outcome_unknown and "unknown_resolver" in step:
            resolution = self.mcp.read(step["unknown_resolver"], context)
            if self.mcp.observe(
                step["unknown_resolver_ambiguous"],
                resolution,
                context,
            ):
                return False
            if not self.mcp.observe(
                step["unknown_resolver_observed"],
                resolution,
                context,
            ):
                return False
            if not self.mcp.bind_unique_issue_identity(
                resolution, context
            ):
                return False
            return self._read_observed(
                step["read_after"], step["observed"], context
            )

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
        observed = self.mcp.observe(condition, observation, context)
        if observed and read_action == "project_item_read_exact":
            self.mcp.bind_project_item_identity(observation, context)
        return observed

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
        context: dict[str, Any],
    ) -> bool:
        side = transition.get("side")
        side_applies = side is None or (
            remaining_sides is not None and side in remaining_sides
        )
        if not side_applies:
            return False
        condition = transition.get("applies_when")
        if condition is None:
            return True
        created = context.get(
            "_project_item_created_this_invocation"
        ) is True
        initial_fields = context.get("initial_fields") or {}
        predicates = {
            "project_item_created_this_invocation_and_status_omitted":
                created and "Status" not in initial_fields,
            "project_item_created_this_invocation_and_status_supplied":
                created and "Status" in initial_fields,
            "project_item_created_this_invocation_and_priority_omitted":
                created and "Priority" not in initial_fields,
            "project_item_created_this_invocation_and_priority_supplied":
                created and "Priority" in initial_fields,
            "project_item_created_this_invocation_and_due_date_omitted":
                created and "Due date" not in initial_fields,
            "project_item_created_this_invocation_and_due_date_supplied":
                created and "Due date" in initial_fields,
        }
        if condition not in predicates:
            raise AssertionError(f"unknown transition condition: {condition}")
        return predicates[condition]

    @staticmethod
    def _bind_partial_receipt(
        operation: dict[str, Any], context: dict[str, Any]
    ) -> bool:
        if (
            operation.get("partial_receipt")
            != "required_exact_prior_task_create_receipt"
        ):
            return False
        receipt = context.get("partial_receipt")
        if not isinstance(receipt, dict):
            return False
        if receipt.get("operation") != "task_create":
            return False
        for field in ("repository", "project_url", "task_key"):
            if receipt.get(field) != context.get(field):
                return False
        if receipt.get("state") not in {
            "issue_observed",
            "project_item_unknown",
            "project_item_missing",
            "fields_incomplete",
        }:
            return False
        number = receipt.get("issue_number")
        node_id = receipt.get("issue_node_id")
        if (number is None) == (node_id is None):
            return False
        if number is not None and (
            not isinstance(number, int) or number <= 0
        ):
            return False
        if node_id is not None and (
            not isinstance(node_id, str) or not node_id
        ):
            return False
        supplied_number = context.get("issue_number")
        supplied_node = context.get("issue_node_id")
        if supplied_number not in {None, number}:
            return False
        if supplied_node not in {None, node_id}:
            return False
        context["issue_number"] = number
        context["issue_node_id"] = node_id
        return True
