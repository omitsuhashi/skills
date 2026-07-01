#!/usr/bin/env python3
"""Validate an approved remote delivery action before creating a PR."""

from __future__ import annotations

import argparse
import sys

from _common import (
    dump_json,
    hardening_candidate_report,
    load_hardening_candidate_registry,
    load_json,
    validate_delivery_plan,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope")
    parser.add_argument("runtime_state")
    parser.add_argument("delivery_plan")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    envelope = load_json(args.envelope)
    runtime = load_json(args.runtime_state)
    plan = load_json(args.delivery_plan)
    registry, registry_path, registry_load_error = load_hardening_candidate_registry(args.runtime_state)
    errors = validate_delivery_plan(
        envelope,
        runtime,
        plan,
        candidate_registry=registry,
        candidate_registry_path=registry_path,
        candidate_registry_load_error=registry_load_error,
    )
    candidate_report = hardening_candidate_report(
        runtime,
        registry,
        candidate_registry_path=registry_path,
        candidate_registry_load_error=registry_load_error,
    )
    if args.json:
        print(
            dump_json(
                {
                    "ok": not errors,
                    "errors": errors,
                    "pending_hardening_candidates": candidate_report["pending_hardening_candidates"],
                    "residual_risks": candidate_report["residual_risks"],
                    "decision_gate_blockers": candidate_report["decision_gate_blockers"],
                    "candidate_registry": registry_path,
                }
            ),
            end="",
        )
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print("DELIVERY PLAN OK")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
