from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .approved_spec_binding import BindingError, approved_spec_binding_ref
from .validation.runtime_state import validate_runtime_state


EVENT_TYPES = {
    "issue_status_changed",
    "review_status_changed",
    "pr_created",
    "pr_merged",
    "signal_recorded",
    "human_request_opened",
    "human_request_resolved",
}
EVENT_FIELDS = {
    "schema_version",
    "event_id",
    "epic_id",
    "envelope_revision",
    "approved_spec_binding",
    "type",
    "issue",
    "status",
    "branch",
    "worktree",
    "base_sha",
    "head_sha",
    "range",
    "review_range",
    "pr",
    "merge_commit",
    "signal",
    "id",
    "scope",
    "resource",
    "reason",
    "created_at",
}


class EventFoldError(Exception):
    def __init__(self, code: str, detail: str | None = None) -> None:
        self.code = code
        self.detail = detail
        message = code if detail is None else f"{code}: {detail}"
        super().__init__(message)


def _binding(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        raise EventFoldError("SCHEMA_UNSUPPORTED")
    try:
        parsed = approved_spec_binding_ref(value)
    except BindingError as error:
        raise EventFoldError(error.code) from None
    return {
        "path": parsed.path,
        "sha256": parsed.sha256,
        "gate_commit": parsed.gate_commit,
    }


def validate_event(event: Any) -> list[str]:
    if not isinstance(event, dict) or event.get("schema_version") != 2:
        return ["SCHEMA_UNSUPPORTED"]
    if "approved_spec_binding" not in event:
        return ["SCHEMA_UNSUPPORTED"]
    if set(event) - EVENT_FIELDS or event.get("type") not in EVENT_TYPES:
        return ["SCHEMA_UNSUPPORTED"]
    try:
        _binding(event["approved_spec_binding"])
    except EventFoldError as error:
        return [error.code]
    if not isinstance(event.get("event_id"), str) or not event["event_id"]:
        return ["event_id is required"]
    if not isinstance(event.get("epic_id"), str) or not event["epic_id"]:
        return ["epic_id is required"]
    if (
        not isinstance(event.get("envelope_revision"), int)
        or event["envelope_revision"] < 1
    ):
        return ["SCHEMA_UNSUPPORTED"]
    return []


def _copy_issue_metadata(record: dict[str, Any], event: dict[str, Any]) -> None:
    for field in ("branch", "worktree", "base_sha", "head_sha"):
        value = event.get(field)
        if isinstance(value, str):
            record[field] = value


def _apply_event(state: dict[str, Any], event: dict[str, Any]) -> None:
    event_type = event.get("type")
    issue = event.get("issue")

    if event_type == "issue_status_changed" and isinstance(issue, str):
        record = state["issues"].setdefault(issue, {})
        record["status"] = event.get("status", record.get("status", "PENDING"))
        _copy_issue_metadata(record, event)
    elif event_type == "review_status_changed" and isinstance(issue, str):
        record = state["issues"].setdefault(issue, {})
        _copy_issue_metadata(record, event)
        review = record.setdefault("review", {})
        review["status"] = event.get("status", review.get("status", "pending"))
        review_range = event.get("range") or event.get("review_range")
        if isinstance(review_range, str):
            review["range"] = review_range
    elif event_type == "pr_created" and isinstance(issue, str):
        record = state["issues"].setdefault(issue, {})
        _copy_issue_metadata(record, event)
        if isinstance(event.get("pr"), str):
            record["pr"] = event["pr"]
        record["pr_opened"] = True
    elif event_type == "pr_merged" and isinstance(issue, str):
        record = state["issues"].setdefault(issue, {})
        _copy_issue_metadata(record, event)
        if isinstance(event.get("pr"), str):
            record["pr"] = event["pr"]
        if isinstance(event.get("merge_commit"), str):
            record["merge_commit"] = event["merge_commit"]
        record["pr_opened"] = True
        record["pr_merged"] = True
    elif event_type == "signal_recorded" and isinstance(issue, str):
        record = state["issues"].setdefault(issue, {})
        signals = record.setdefault("signals", [])
        signal = event.get("signal")
        if isinstance(signal, str) and signal not in signals:
            signals.append(signal)
    elif event_type == "human_request_opened":
        state["human_requests"].append(
            {
                "schema_version": 2,
                "approved_spec_binding": dict(state["approved_spec_binding"]),
                **{
                    key: value
                    for key, value in event.items()
                    if key
                    in {
                        "id",
                        "scope",
                        "issue",
                        "resource",
                        "reason",
                        "created_at",
                    }
                },
            }
        )
    elif event_type == "human_request_resolved":
        request_id = event.get("id")
        state["human_requests"] = [
            request
            for request in state["human_requests"]
            if request.get("id") != request_id
        ]


def rebuild_state_from_events(
    events_path: str | Path,
) -> tuple[dict[str, Any], list[str]]:
    path = Path(events_path)
    seen: set[str] = set()
    duplicate_events = 0
    binding: dict[str, str] | None = None
    epic_id: str | None = None
    envelope_revision: int | None = None
    state: dict[str, Any] = {
        "schema_version": 2,
        "epic_id": None,
        "envelope_revision": None,
        "approved_spec_binding": None,
        "issues": {},
        "human_requests": [],
    }

    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise EventFoldError("SCHEMA_UNSUPPORTED", f"line {line_number}: {exc}") from exc
            event_errors = validate_event(event)
            if event_errors:
                raise EventFoldError(event_errors[0], f"line {line_number}")
            event_binding = _binding(event["approved_spec_binding"])
            if binding is None:
                binding = event_binding
                state["approved_spec_binding"] = dict(binding)
            elif event_binding != binding:
                raise EventFoldError("BINDING_MISMATCH", f"line {line_number}")
            if epic_id is None:
                epic_id = event["epic_id"]
                state["epic_id"] = epic_id
            elif event["epic_id"] != epic_id:
                raise EventFoldError("BINDING_MISMATCH", f"line {line_number}: epic_id")
            current_revision = event.get("envelope_revision")
            if not isinstance(current_revision, int) or current_revision < 1:
                raise EventFoldError("SCHEMA_UNSUPPORTED", f"line {line_number}: envelope_revision")
            if envelope_revision is None:
                envelope_revision = current_revision
                state["envelope_revision"] = envelope_revision
            elif current_revision != envelope_revision:
                raise EventFoldError("BINDING_MISMATCH", f"line {line_number}: envelope_revision")

            event_id = event["event_id"]
            if event_id in seen:
                duplicate_events += 1
                continue
            seen.add(event_id)
            _apply_event(state, event)

    if binding is None:
        raise EventFoldError("BINDING_MISMATCH", "event stream has no binding epoch")
    state["rebuild"] = {
        "events_applied": len(seen),
        "duplicate_events_ignored": duplicate_events,
    }
    errors = validate_runtime_state(state)
    if errors:
        raise EventFoldError(errors[0])
    warnings: list[str] = []
    if duplicate_events:
        warnings.append(f"{duplicate_events} duplicate event IDs ignored")
    return state, warnings
