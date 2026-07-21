#!/usr/bin/env python3
"""Validate an issue-implementation-loop worker dispatch packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

LIB_DIR = Path(__file__).resolve().parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from issue_implementation_loop import dump_json, load_json, validate_worker_packet  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("worker_packet")
    parser.add_argument("--repo-root", required=True, help="Trusted coordinator repo root.")
    parser.add_argument(
        "--assigned-worktree",
        required=True,
        help="Trusted coordinator-assigned worker worktree.",
    )
    parser.add_argument("--envelope", required=True, help="Trusted active Envelope path.")
    parser.add_argument(
        "--runtime-state", required=True, help="Trusted active Runtime State path."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    errors = validate_worker_packet(
        load_json(args.worker_packet),
        repo_root=args.repo_root,
        assigned_worktree=args.assigned_worktree,
        envelope_path=args.envelope,
        runtime_state_path=args.runtime_state,
    )
    if args.json:
        print(dump_json({"ok": not errors, "errors": errors}), end="")
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print("WORKER PACKET OK")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
