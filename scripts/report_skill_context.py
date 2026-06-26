#!/usr/bin/env python3
"""Report current loop-skill context metrics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence

from validate_loop_skill_context import ContractError, REPO_ROOT, inspect_operation, load_contract, validate_contract


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else str(path)


def _default_skill_dirs() -> List[Path]:
    return [
        REPO_ROOT / "skills/grill-to-pr-loop",
        REPO_ROOT / "skills/issue-implementation-loop",
    ]


def _operation_names(skill_dir: Path) -> List[str]:
    contract = load_contract(skill_dir)
    errors = validate_contract(skill_dir, contract)
    if errors:
        raise ContractError("; ".join(errors))
    operations = contract.get("operations")
    if not isinstance(operations, dict):
        raise ContractError(f"{skill_dir}: operations must be a table")
    return list(operations.keys())


def collect_report(skill_dirs: Sequence[Path]) -> Dict[str, object]:
    report: Dict[str, object] = {
        "schema_version": 1,
        "report_type": "skill-context-baseline",
        "metric_source": "context-contract.toml schema v1 word-count metrics",
        "skills": [],
    }
    for skill_dir in skill_dirs:
        operations = []
        for operation in _operation_names(skill_dir):
            operations.append(inspect_operation(skill_dir, operation))
        report["skills"].append(
            {
                "skill": skill_dir.name,
                "path": _relative(skill_dir),
                "operation_count": len(operations),
                "operations": operations,
            }
        )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--all", action="store_true", help="report all loop skill context contracts")
    target.add_argument("--skill", action="append", help="skill directory, absolute or repo-relative")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    skill_dirs = _default_skill_dirs() if args.all else []
    if args.skill:
        for value in args.skill:
            path = Path(value)
            skill_dirs.append(path if path.is_absolute() else REPO_ROOT / path)

    try:
        report = collect_report(skill_dirs)
    except ContractError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for skill in report["skills"]:
            assert isinstance(skill, dict)
            print(f"{skill['skill']} ({skill['path']})")
            operations = skill["operations"]
            assert isinstance(operations, list)
            for operation in operations:
                print(
                    f"- {operation['operation']}: "
                    f"{operation['word_count']} words, "
                    f"{operation['file_count']} files, "
                    f"headroom {operation['budget_headroom']}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
