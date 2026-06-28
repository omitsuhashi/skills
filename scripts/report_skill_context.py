#!/usr/bin/env python3
"""Report current loop-skill context metrics."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

from skill_context.contract import (
    ContractError,
    REPO_ROOT,
    all_skill_dirs,
    load_contract,
)
from validate_skill_architecture import DEFAULT_POLICY_PATH, REQUIRED_FAMILY_ID, PolicyError, load_policy
from validate_skill_context import inspect_context_operation, operation_names_for_context


DEFAULT_BASELINE_PATH = REPO_ROOT / "knowledge" / "wiki" / "syntheses" / "skill-repository-optimization-v4-context-baseline.json"
GROWTH_WARNING_THRESHOLD_PERCENT = 10

GATE_OPERATIONS = {
    "grill-to-pr-loop": {
        "spec": "spec_gate",
        "issue-gate": "issue_gate",
        "execution-plan": "execution_plan_gate",
        "delivery": "remote_gate",
    },
    "issue-implementation-loop": {
        "execute.review": "implementation_review_gate",
        "deliver": "remote_gate",
    },
}
RUNTIME_ARTIFACT_NAME_FRAGMENTS = (
    "event",
    "human-request",
    "human_request",
    "resume-brief",
    "resume_brief",
    "runtime-state",
    "runtime_state",
    "worker-report",
    "worker_report",
)


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


def _repository_change_loop_skill_names() -> set[str]:
    try:
        policy = load_policy(DEFAULT_POLICY_PATH)
    except PolicyError as exc:
        raise ContractError(str(exc)) from exc
    families = policy.get("families")
    if not isinstance(families, dict):
        raise ContractError("skill architecture policy must contain families")
    family = families.get(REQUIRED_FAMILY_ID)
    if not isinstance(family, dict):
        raise ContractError(f"skill architecture policy missing family: {REQUIRED_FAMILY_ID}")
    skill_names = family.get("user_facing_skills")
    if not isinstance(skill_names, list) or not all(isinstance(item, str) and item for item in skill_names):
        raise ContractError(f"{REQUIRED_FAMILY_ID}.user_facing_skills must be an array of non-empty strings")
    return set(skill_names)


def _loop_skill_reports(report: Mapping[str, object]) -> List[Mapping[str, object]]:
    skill_names = _repository_change_loop_skill_names()
    skills = report.get("skills")
    if not isinstance(skills, list):
        return []
    return [skill for skill in skills if isinstance(skill, dict) and skill.get("skill") in skill_names]


def _operation_names_from_reports(skills: Iterable[Mapping[str, object]]) -> List[tuple[str, str]]:
    names: List[tuple[str, str]] = []
    for skill in skills:
        skill_name = skill.get("skill")
        operations = skill.get("operations")
        if not isinstance(skill_name, str) or not isinstance(operations, list):
            continue
        for operation in operations:
            if isinstance(operation, dict) and isinstance(operation.get("operation"), str):
                names.append((skill_name, operation["operation"]))
    return names


def _gate_breakdown(operations: Iterable[tuple[str, str]]) -> List[Dict[str, str]]:
    seen: set[str] = set()
    gates: List[Dict[str, str]] = []
    for skill_name, operation_name in operations:
        gate_name = GATE_OPERATIONS.get(skill_name, {}).get(operation_name)
        if not gate_name:
            continue
        if gate_name in seen:
            continue
        seen.add(gate_name)
        gates.append({"gate": gate_name, "skill": skill_name, "operation": operation_name})
    return gates


def _runtime_artifacts(skill_reports: Sequence[Mapping[str, object]]) -> List[str]:
    paths: set[str] = set()
    for skill in skill_reports:
        raw_path = skill.get("path")
        if not isinstance(raw_path, str):
            continue
        skill_dir = REPO_ROOT / raw_path
        for child in skill_dir.rglob("*"):
            if not child.is_file():
                continue
            if "tests" in child.relative_to(skill_dir).parts:
                continue
            name = child.name.lower()
            if any(fragment in name for fragment in RUNTIME_ARTIFACT_NAME_FRAGMENTS):
                paths.add(_relative(child))
    return sorted(paths)


def collect_workflow_complexity(report: Mapping[str, object]) -> Dict[str, object]:
    skill_reports = _loop_skill_reports(report)
    operations = _operation_names_from_reports(skill_reports)
    operation_names = {operation_name for _, operation_name in operations}
    gate_breakdown = _gate_breakdown(operations)
    runtime_artifacts = _runtime_artifacts(skill_reports)

    selected_skill_names = {str(skill.get("skill")) for skill in skill_reports}
    worker_context_required = "issue-implementation-loop" in selected_skill_names
    review_cycle_required = "execute.review" in operation_names
    human_wait_present = "execute.wait" in operation_names
    remote_delivery_present = bool({"delivery", "deliver"} & operation_names)

    warnings: List[str] = []
    if worker_context_required:
        warnings.append("worker context required")
    if review_cycle_required:
        warnings.append("review cycle required")
    if human_wait_present:
        warnings.append("human wait path present")
    if remote_delivery_present:
        warnings.append("remote delivery gated")

    return {
        "advisory_only": True,
        "family": REQUIRED_FAMILY_ID,
        "skill_count": len(skill_reports),
        "operation_count": len(operations),
        "gate_count": len(gate_breakdown),
        "gate_breakdown": gate_breakdown,
        "runtime_artifact_count": len(runtime_artifacts),
        "runtime_artifacts": runtime_artifacts,
        "worker_context_required": worker_context_required,
        "review_cycle_required": review_cycle_required,
        "human_wait_present": human_wait_present,
        "remote_delivery_present": remote_delivery_present,
        "warnings": warnings,
    }


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
    complexity = report.get("workflow_complexity")
    if isinstance(complexity, dict):
        warnings = complexity.get("warnings")
        if isinstance(warnings, list):
            warning_text = "; ".join(warning for warning in warnings if isinstance(warning, str))
            if warning_text:
                lines.append(f"Workflow complexity: {warning_text}.")
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
    report["workflow_complexity"] = collect_workflow_complexity(report)
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
