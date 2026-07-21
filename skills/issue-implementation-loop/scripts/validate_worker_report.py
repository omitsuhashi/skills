#!/usr/bin/env python3
"""Validate an issue-implementation-loop worker report."""

from __future__ import annotations

import argparse
import json
import sys

from _common import dump_json, load_json, validate_worker_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("worker_report")
    parser.add_argument("--dispatch-packet", required=True)
    parser.add_argument("--runtime-state", required=True)
    parser.add_argument("--envelope", required=True)
    parser.add_argument("--repo-root", required=True, help="Trusted Git worktree root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    try:
        report = load_json(args.worker_report)
        dispatch_packet = load_json(args.dispatch_packet)
        runtime_state = load_json(args.runtime_state)
        envelope = load_json(args.envelope)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        errors = ["SCHEMA_UNSUPPORTED"]
    else:
        errors = validate_worker_report(
            report,
            dispatch_packet,
            runtime_state,
            envelope,
            args.repo_root,
            envelope_path=args.envelope,
            runtime_state_path=args.runtime_state,
        )
    if args.json:
        print(dump_json({"ok": not errors, "errors": errors}), end="")
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print("WORKER REPORT OK")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
