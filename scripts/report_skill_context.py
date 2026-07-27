#!/usr/bin/env python3
"""Report current skill context metrics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

from skill_context.contract import ContractError, REPO_ROOT, all_skill_dirs
from validate_skill_context import inspect_context_operation, operation_names_for_context


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else str(path)


def _warning_lines(report: Mapping[str, object]) -> List[str]:
    warnings = report.get("warnings")
    if not isinstance(warnings, list):
        return []
    return [warning for warning in warnings if isinstance(warning, str)]


def collect_report(skill_dirs: Sequence[Path]) -> Dict[str, object]:
    report: Dict[str, object] = {
        "schema_version": 1,
        "report_type": "skill-context-report",
        "metric_source": "context-contract.toml schema v1/v2/v3 character and estimated-token metrics",
        "warnings": [],
        "skills": [],
    }
    for skill_dir in skill_dirs:
        operations = [
            inspect_context_operation(skill_dir, operation)
            for operation in operation_names_for_context(skill_dir)
        ]
        report["skills"].append(
            {
                "skill": skill_dir.name,
                "path": _relative(skill_dir),
                "operation_count": len(operations),
                "operations": operations,
            }
        )
    return report


def _render_text_report(report: Mapping[str, object]) -> str:
    lines: List[str] = []
    skills = report["skills"]
    assert isinstance(skills, list)
    for skill in skills:
        assert isinstance(skill, dict)
        lines.append(f"{skill['skill']} ({skill['path']})")
        operations = skill["operations"]
        assert isinstance(operations, list)
        for operation in operations:
            assert isinstance(operation, dict)
            headroom = operation["budget_headroom"]
            if headroom is None:
                headroom = f"{operation['headroom_percent']}%"
            lines.append(
                f"- {operation['operation']}: "
                f"{operation['word_count']} words, "
                f"{operation['file_count']} files, "
                f"headroom {headroom}"
            )
    return "\n".join(lines)


def _write_or_print(output: str, output_path: str | None) -> None:
    if output_path:
        path = Path(output_path)
        if not path.is_absolute():
            path = REPO_ROOT / path
        path.write_text(f"{output}\n", encoding="utf-8")
    else:
        print(output)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--all", action="store_true", help="report all skill context contracts")
    target.add_argument("--skill", action="append", help="skill directory, absolute or repo-relative")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--fail-on-warning", action="store_true", help="return non-zero when warnings are emitted")
    parser.add_argument("--output", help="write output to path instead of stdout")
    args = parser.parse_args(argv)

    try:
        skill_dirs = all_skill_dirs() if args.all else []
        if args.skill:
            for value in args.skill:
                path = Path(value)
                skill_dirs.append(path if path.is_absolute() else REPO_ROOT / path)
        report = collect_report(skill_dirs)
    except ContractError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    for warning in _warning_lines(report):
        print(f"WARNING: {warning}", file=sys.stderr)
    output = json.dumps(report, indent=2, sort_keys=True) if args.json else _render_text_report(report)
    _write_or_print(output, args.output)
    return 2 if args.fail_on_warning and _warning_lines(report) else 0


if __name__ == "__main__":
    raise SystemExit(main())
