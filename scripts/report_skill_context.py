#!/usr/bin/env python3
"""Report current loop-skill context metrics."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

from skill_context.contract import (
    ContractError,
    REPO_ROOT,
    all_skill_dirs,
    load_contract,
)
from validate_skill_context import inspect_context_operation, operation_names_for_context


DEFAULT_BASELINE_PATH = REPO_ROOT / "knowledge" / "wiki" / "syntheses" / "skill-repository-optimization-v4-context-baseline.json"
GROWTH_WARNING_THRESHOLD_PERCENT = 10


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else str(path)


def _operation_names(skill_dir: Path) -> List[str]:
    return operation_names_for_context(skill_dir)


def _load_baseline(path: Path) -> Dict[tuple[str, str], Mapping[str, object]]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"{path}: invalid JSON: {exc}") from exc
    baseline: Dict[tuple[str, str], Mapping[str, object]] = {}
    skills = payload.get("skills")
    if not isinstance(skills, list):
        return baseline
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        skill_name = skill.get("skill")
        operations = skill.get("operations")
        if not isinstance(skill_name, str) or not isinstance(operations, list):
            continue
        for operation in operations:
            if isinstance(operation, dict) and isinstance(operation.get("operation"), str):
                baseline[(skill_name, operation["operation"])] = operation
    return baseline


def _comparison(
    operation: Mapping[str, object],
    baseline: Mapping[tuple[str, str], Mapping[str, object]],
) -> Dict[str, object] | None:
    key = (str(operation.get("skill")), str(operation.get("operation")))
    previous = baseline.get(key)
    if not previous:
        return None
    metric = "estimated_token_count" if "estimated_token_count" in previous else "word_count"
    previous_value = previous.get(metric)
    current_value = operation.get(metric)
    if not isinstance(previous_value, int) or previous_value <= 0 or not isinstance(current_value, int):
        return None
    delta = current_value - previous_value
    growth_percent = round((delta / previous_value) * 100, 2)
    return {
        "baseline_metric": metric,
        "baseline_value": previous_value,
        "current_value": current_value,
        "delta": delta,
        "growth_percent": growth_percent,
        "warning": growth_percent > GROWTH_WARNING_THRESHOLD_PERCENT,
    }


def _warning_lines(report: Mapping[str, object]) -> List[str]:
    warnings = report.get("warnings")
    if not isinstance(warnings, list):
        return []
    return [warning for warning in warnings if isinstance(warning, str)]


def _print_warnings(report: Mapping[str, object]) -> None:
    for warning in _warning_lines(report):
        print(f"WARNING: {warning}", file=sys.stderr)


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


def collect_baseline(skill_dirs: Sequence[Path]) -> Dict[str, object]:
    report: Dict[str, object] = {
        "schema_version": 2,
        "report_type": "skill-context-baseline",
        "metric_source": "context-contract.toml schema v1/v2 character and estimated-token metrics",
        "captured_at": date.today().isoformat(),
        "growth_warning_threshold_percent": GROWTH_WARNING_THRESHOLD_PERCENT,
        "skills": [],
    }
    for skill_dir in skill_dirs:
        contract = load_contract(skill_dir)
        operations = []
        for operation in _operation_names(skill_dir):
            operation_report = copy.deepcopy(inspect_context_operation(skill_dir, operation))
            operation_report.pop("baseline_comparison", None)
            operations.append(operation_report)
        report["skills"].append(
            {
                "skill": skill_dir.name,
                "path": _relative(skill_dir),
                "operation_count": len(operations),
                "topologies": contract.get("topologies", []),
                "modes": contract.get("modes", []),
                "operations": operations,
            }
        )
    return report


def collect_report(
    skill_dirs: Sequence[Path],
    baseline_path: Path = DEFAULT_BASELINE_PATH,
    require_baseline: bool = False,
) -> Dict[str, object]:
    baseline = _load_baseline(baseline_path)
    warnings: List[str] = []
    report: Dict[str, object] = {
        "schema_version": 2,
        "report_type": "skill-context-report",
        "metric_source": "context-contract.toml schema v1/v2 character and estimated-token metrics",
        "baseline_path": _relative(baseline_path),
        "baseline_required": require_baseline,
        "growth_warning_threshold_percent": GROWTH_WARNING_THRESHOLD_PERCENT,
        "warnings": warnings,
        "skills": [],
    }
    for skill_dir in skill_dirs:
        contract = load_contract(skill_dir)
        operations = []
        for operation in _operation_names(skill_dir):
            operation_report = inspect_context_operation(skill_dir, operation)
            comparison = _comparison(operation_report, baseline)
            operation_report["baseline_comparison"] = comparison
            if comparison is None and require_baseline:
                warnings.append(f"{operation_report['skill']} {operation_report['operation']} missing baseline")
            elif comparison and comparison["warning"]:
                warnings.append(
                    f"{operation_report['skill']} {operation_report['operation']} "
                    f"{comparison['baseline_metric']} grew {comparison['growth_percent']}%"
                )
            operations.append(operation_report)
        report["skills"].append(
            {
                "skill": skill_dir.name,
                "path": _relative(skill_dir),
                "operation_count": len(operations),
                "topologies": contract.get("topologies", []),
                "modes": contract.get("modes", []),
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
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE_PATH), help="baseline report JSON path")
    parser.add_argument("--emit-baseline", action="store_true", help="emit current metrics as a baseline artifact")
    parser.add_argument("--require-baseline", action="store_true", help="warn when any operation is absent from baseline")
    parser.add_argument("--fail-on-warning", action="store_true", help="return non-zero when warnings are emitted")
    parser.add_argument("--output", help="write output to path instead of stdout")
    args = parser.parse_args(argv)

    try:
        skill_dirs = all_skill_dirs() if args.all else []
        if args.skill:
            for value in args.skill:
                path = Path(value)
                skill_dirs.append(path if path.is_absolute() else REPO_ROOT / path)
        baseline_path = Path(args.baseline)
        if not baseline_path.is_absolute():
            baseline_path = REPO_ROOT / baseline_path
        if args.emit_baseline:
            report = collect_baseline(skill_dirs)
        else:
            report = collect_report(skill_dirs, baseline_path=baseline_path, require_baseline=args.require_baseline)
    except ContractError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    _print_warnings(report)
    if args.json:
        output = json.dumps(report, indent=2, sort_keys=True)
    else:
        output = _render_text_report(report)
    _write_or_print(output, args.output)
    return 2 if args.fail_on_warning and _warning_lines(report) else 0


if __name__ == "__main__":
    raise SystemExit(main())
