#!/usr/bin/env python3
"""Validate an issue-implementation-loop worker report."""

from __future__ import annotations

import argparse
import sys

from _common import dump_json, load_json, validate_worker_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("worker_report")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    errors = validate_worker_report(load_json(args.worker_report))
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
