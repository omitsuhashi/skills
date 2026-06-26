#!/usr/bin/env python3
"""Report current loop-skill context metrics."""

from __future__ import annotations

import argparse
import json
import sys
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


def collect_report(skill_dirs: Sequence[Path], baseline_path: Path = DEFAULT_BASELINE_PATH) -> Dict[str, object]:
    baseline = _load_baseline(baseline_path)
    warnings: List[str] = []
    report: Dict[str, object] = {
        "schema_version": 2,
        "report_type": "skill-context-report",
        "metric_source": "context-contract.toml schema v1/v2 character and estimated-token metrics",
        "baseline_path": _relative(baseline_path),
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
            if comparison and comparison["warning"]:
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
        report = collect_report(skill_dirs, baseline_path=baseline_path)
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
                headroom = operation["budget_headroom"]
                if headroom is None:
                    headroom = f"{operation['headroom_percent']}%"
                print(
                    f"- {operation['operation']}: "
                    f"{operation['word_count']} words, "
                    f"{operation['file_count']} files, "
                    f"headroom {headroom}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
