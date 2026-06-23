#!/usr/bin/env python3
"""Validate a normalized issue-implementation-loop input packet."""

from __future__ import annotations

import argparse
import sys

from _common import load_json, validate_input_packet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    errors = validate_input_packet(load_json(args.packet))
    if args.json:
        from _common import dump_json

        print(dump_json({"ok": not errors, "errors": errors}), end="")
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print("INPUT PACKET OK")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
