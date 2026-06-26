#!/usr/bin/env python3
"""Validate skill context contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Sequence

from skill_context.contract import ContractError, REPO_ROOT, all_skill_dirs, validate_skill_dir


def resolve_skill_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def run_validation(argv: Sequence[str] | None = None, *, success_label: str = "skill context") -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--all", action="store_true", help="validate all skill context contracts")
    target.add_argument("--skill", help="skill directory to validate")
    parser.add_argument("--json", action="store_true", help="emit JSON result")
    args = parser.parse_args(argv)

    try:
        skill_dirs = all_skill_dirs() if args.all else [resolve_skill_path(args.skill)]
    except ContractError as exc:
        result = {"ok": False, "skills": [], "errors": [str(exc)]}
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(str(exc), file=sys.stderr)
        return 1

    result = {"ok": True, "skills": []}
    stderr_lines: List[str] = []
    for skill_dir in skill_dirs:
        errors = validate_skill_dir(skill_dir)
        result["skills"].append({"path": str(skill_dir), "ok": not errors, "errors": errors})
        if errors:
            result["ok"] = False
            stderr_lines.extend(f"{skill_dir}: {error}" for error in errors)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["ok"]:
        print(f"OK: validated {len(skill_dirs)} {success_label} contract(s)")
    if stderr_lines:
        print("\n".join(stderr_lines), file=sys.stderr)
    return 0 if result["ok"] else 1


def main(argv: Sequence[str] | None = None) -> int:
    return run_validation(argv)


if __name__ == "__main__":
    raise SystemExit(main())
