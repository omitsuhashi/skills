#!/usr/bin/env python3
"""Validate an approved remote delivery action before creating a PR."""

from __future__ import annotations

import argparse
import sys

from _common import dump_json, load_json, validate_delivery_plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope")
    parser.add_argument("runtime_state")
    parser.add_argument("delivery_plan")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    errors = validate_delivery_plan(
        load_json(args.envelope),
        load_json(args.runtime_state),
        load_json(args.delivery_plan),
    )
    if args.json:
        print(dump_json({"ok": not errors, "errors": errors}), end="")
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print("DELIVERY PLAN OK")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
