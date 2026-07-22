#!/usr/bin/env python3
"""Validate a terminal Execution Result against the active binding epoch."""

from __future__ import annotations

import argparse
import json
import sys

from _common import (
    dump_json,
    load_hardening_candidate_registry,
    load_json,
    validate_execution_result,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope")
    parser.add_argument("runtime_state")
    parser.add_argument("execution_result")
    parser.add_argument("--repo-root", required=True, help="Trusted Git worktree root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    try:
        envelope = load_json(args.envelope)
        runtime = load_json(args.runtime_state)
        execution_result = load_json(args.execution_result)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        errors = ["SCHEMA_UNSUPPORTED"]
        if args.json:
            print(dump_json({"ok": False, "errors": errors}), end="")
        else:
            print(errors[0], file=sys.stderr)
        return 1
    registry, registry_path, registry_load_error = load_hardening_candidate_registry(args.runtime_state)
    errors = validate_execution_result(
        envelope,
        runtime,
        execution_result,
        repo_root=args.repo_root,
        candidate_registry=registry,
        candidate_registry_path=registry_path,
        candidate_registry_load_error=registry_load_error,
    )
    if args.json:
        print(dump_json({"ok": not errors, "errors": errors}), end="")
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print("EXECUTION RESULT OK")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
