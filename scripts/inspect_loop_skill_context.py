#!/usr/bin/env python3
"""Inspect a loop-skill context contract read set."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from validate_loop_skill_context import ContractError, REPO_ROOT, inspect_operation


def resolve_skill_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True, help="skill directory, absolute or repo-relative")
    parser.add_argument("--operation", required=True, help="operation name from context-contract.toml")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    try:
        result = inspect_operation(resolve_skill_path(args.skill), args.operation)
    except ContractError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"skill: {result['skill']}")
        print(f"operation: {result['operation']}")
        print(f"files: {result['file_count']} / {result['max_file_count']}")
        print(f"words: {result['word_count']} / {result['word_budget']}")
        print(f"budget_headroom: {result['budget_headroom']}")
        for file_path in result["files"]:
            print(f"- {file_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
