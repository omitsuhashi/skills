#!/usr/bin/env python3
"""Rebuild runtime-state JSON from an events.jsonl stream."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _common import dump_json


def apply_event(state: dict[str, Any], event: dict[str, Any]) -> None:
    event_type = event.get("type")
    issue = event.get("issue")
    if event.get("epic_id") and not state.get("epic_id"):
        state["epic_id"] = event["epic_id"]
    if event.get("envelope_revision") and not state.get("envelope_revision"):
        state["envelope_revision"] = event["envelope_revision"]

    if event_type == "issue_status_changed" and isinstance(issue, str):
        record = state["issues"].setdefault(issue, {})
        record["status"] = event.get("status", record.get("status", "PENDING"))
    elif event_type == "review_status_changed" and isinstance(issue, str):
        record = state["issues"].setdefault(issue, {})
        review = record.setdefault("review", {})
        review["status"] = event.get("status", review.get("status", "pending"))
    elif event_type == "signal_recorded" and isinstance(issue, str):
        record = state["issues"].setdefault(issue, {})
        signals = record.setdefault("signals", [])
        signal = event.get("signal")
        if isinstance(signal, str) and signal not in signals:
            signals.append(signal)
    elif event_type == "human_request_opened":
        state["human_requests"].append(
            {
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
            }
        )
    elif event_type == "human_request_resolved":
        request_id = event.get("id")
        state["human_requests"] = [
            request for request in state["human_requests"] if request.get("id") != request_id
        ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events_jsonl")
    args = parser.parse_args()

    path = Path(args.events_jsonl)
    seen: set[str] = set()
    duplicate_events = 0
    state: dict[str, Any] = {
        "schema_version": 1,
        "epic_id": None,
        "envelope_revision": None,
        "issues": {},
        "human_requests": [],
    }

    try:
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                event = json.loads(line)
                event_id = event.get("event_id")
                if not isinstance(event_id, str):
                    print(f"line {line_number}: event_id is required", file=sys.stderr)
                    return 1
                if event_id in seen:
                    duplicate_events += 1
                    continue
                seen.add(event_id)
                apply_event(state, event)
    except json.JSONDecodeError as exc:
        print(f"invalid jsonl: {exc}", file=sys.stderr)
        return 1

    if state["epic_id"] is None:
        state["epic_id"] = "unknown"
    if state["envelope_revision"] is None:
        state["envelope_revision"] = 1
    state["rebuild"] = {
        "events_applied": len(seen),
        "duplicate_events_ignored": duplicate_events,
    }
    print(dump_json(state), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
