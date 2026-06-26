#!/usr/bin/env python3
"""Select the next issue-implementation-loop operation from structured state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence


LIB_DIR = Path(__file__).resolve().parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from issue_implementation_loop.context_contract import ContextContractError  # noqa: E402
from issue_implementation_loop.operation_selection import select_operation  # noqa: E402


REQUESTED_MODES = ("prepare", "execute", "resume", "status", "deliver")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--envelope", help="Execution Envelope JSON path")
    parser.add_argument("--runtime", help="runtime-state.json path")
    parser.add_argument("--requested-mode", required=True, choices=REQUESTED_MODES)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    script_path = Path(__file__).resolve()
    skill_dir = script_path.parents[1]
    repo_root = skill_dir.parents[1]
    try:
        result = select_operation(
            skill_dir=skill_dir,
            repo_root=repo_root,
            requested_mode=args.requested_mode,
            envelope_path=Path(args.envelope) if args.envelope else None,
            runtime_path=Path(args.runtime) if args.runtime else None,
        )
    except ContextContractError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"operation: {result['operation']}")
        print(f"priority: {result['priority']}")
        print(f"reason: {result['reason']}")
        if result.get("target_issue"):
            print(f"target_issue: {result['target_issue']}")
        budget = result["word_budget_result"]
        if budget.get("word_budget"):
            print(f"words: {budget['word_count']} / {budget['word_budget']}")
        else:
            print(f"estimated_tokens: {budget['estimated_token_count']} / {budget['estimated_token_budget']}")
            print(f"characters: {budget['character_count']} / {budget['character_budget']}")
            print(f"headroom_percent: {budget['headroom_percent']}")
        print(f"files: {budget['file_count']} / {budget['max_file_count']}")
        for path in result["read_set"]:
            print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
