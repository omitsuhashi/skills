#!/usr/bin/env python3
"""Validate skill context contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Sequence, Tuple

from skill_context.contract import ContractError, REPO_ROOT, all_skill_dirs, load_contract, validate_skill_dir
from skill_context.metrics import collect_file_metrics
from validate_skill_architecture import DEFAULT_POLICY_PATH, REQUIRED_FAMILY_ID, load_policy


def resolve_skill_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def _safe_relative_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts and value == path.as_posix()


def _as_string(contract: Mapping[str, object], field: str, errors: List[str]) -> str | None:
    value = contract.get(field)
    if not isinstance(value, str) or not value:
        errors.append(f"{field} must be a non-empty string")
        return None
    return value


def _as_string_list(mapping: Mapping[str, object], field: str, errors: List[str]) -> List[str] | None:
    value = mapping.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{field} must be an array of non-empty strings")
        return None
    return list(value)


def _positive_int(mapping: Mapping[str, object], field: str, errors: List[str]) -> int | None:
    value = mapping.get(field)
    if not isinstance(value, int) or value <= 0:
        errors.append(f"{field} must be a positive integer")
        return None
    return value


def _non_negative_int(mapping: Mapping[str, object], field: str, errors: List[str]) -> int | None:
    value = mapping.get(field)
    if not isinstance(value, int) or value < 0:
        errors.append(f"{field} must be a non-negative integer")
        return None
    return value


def _is_topology_mode_contract(contract: Mapping[str, object]) -> bool:
    return "topologies" in contract or "modes" in contract


def _validate_name_list(field: str, values: Sequence[str], errors: List[str]) -> None:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    for duplicate in duplicates:
        errors.append(f"duplicate {field}: {duplicate}")
    for value in values:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", value):
            errors.append(f"invalid {field}: {value}")


def _validate_reference(skill_dir: Path, reference: str, errors: List[str]) -> None:
    if not _safe_relative_path(reference):
        errors.append(f"invalid reference path: {reference}")
        return
    parts = Path(reference).parts
    if not parts or parts[0] != "references":
        errors.append(f"reference must be under references/: {reference}")
    elif len(parts) > 2 and not (len(parts) == 3 and parts[1] == "modes" and parts[2].endswith(".md")):
        errors.append(f"reference depth > 1: {reference}")
    if not (skill_dir / reference).is_file():
        errors.append(f"missing reference: {reference}")


def _matrix_budget(contract: Mapping[str, object], raw_config: Mapping[str, object]) -> Dict[str, int | None]:
    budget: Dict[str, int | None] = {
        "word_budget": None,
        "character_budget": None,
        "non_whitespace_character_budget": None,
        "estimated_token_budget": None,
        "max_file_count": None,
        "min_headroom_percent": None,
    }
    for field in budget:
        value = raw_config.get(field, contract.get(field))
        if isinstance(value, int):
            budget[field] = value
    return budget


def _matrix_operation_read_set(
    skill_dir: Path,
    contract: Mapping[str, object],
    operation: str,
) -> Tuple[List[Path], Dict[str, int | None]]:
    entrypoint = contract["entrypoint"]
    base_references = contract["base_references"]
    operations = contract["operations"]
    assert isinstance(entrypoint, str)
    assert isinstance(base_references, list)
    assert isinstance(operations, dict)
    raw_config = operations[operation]
    assert isinstance(raw_config, dict)
    references = raw_config.get("references", [])
    assert isinstance(references, list)
    files = [skill_dir / entrypoint]
    files.extend(skill_dir / reference for reference in base_references)
    files.extend(skill_dir / reference for reference in references)
    return files, _matrix_budget(contract, raw_config)


def inspect_context_operation(skill_dir: Path, operation: str) -> Dict[str, object]:
    contract = load_contract(skill_dir)
    if not _is_topology_mode_contract(contract):
        from skill_context.contract import inspect_operation

        return inspect_operation(skill_dir, operation)
    errors = validate_skill_dir_for_context(skill_dir)
    if errors:
        raise ContractError("; ".join(errors))
    operations = contract["operations"]
    assert isinstance(operations, dict)
    if operation not in operations:
        raise ContractError(f"unknown operation: {operation}")
    raw_config = operations[operation]
    assert isinstance(raw_config, dict)
    files, budget = _matrix_operation_read_set(skill_dir, contract, operation)
    metrics = collect_file_metrics(files, budget)

    def display_path(path: Path) -> str:
        return path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else str(path)

    result: Dict[str, object] = {
        "schema_version": contract.get("schema_version", 1),
        "skill": contract["skill"],
        "operation": operation,
        "files": [display_path(path) for path in files],
        "file_count": metrics["file_count"],
        "max_file_count": budget.get("max_file_count"),
        "word_count": metrics["word_count"],
        "word_budget": budget.get("word_budget"),
        "budget_headroom": None,
        "character_count": metrics["character_count"],
        "non_whitespace_character_count": metrics["non_whitespace_character_count"],
        "estimated_token_count": metrics["estimated_token_count"],
        "headroom_percent": metrics["headroom_percent"],
        "budget": budget,
    }
    if isinstance(budget.get("word_budget"), int):
        result["budget_headroom"] = budget["word_budget"] - metrics["word_count"]
    for field in ("topology", "mode"):
        value = raw_config.get(field)
        if isinstance(value, str):
            result[field] = value
    return result


def operation_names_for_context(skill_dir: Path) -> List[str]:
    contract = load_contract(skill_dir)
    if not _is_topology_mode_contract(contract):
        errors = validate_skill_dir(skill_dir)
        if errors:
            raise ContractError("; ".join(errors))
    else:
        errors = validate_skill_dir_for_context(skill_dir)
        if errors:
            raise ContractError("; ".join(errors))
    operations = contract.get("operations")
    if not isinstance(operations, dict):
        raise ContractError(f"{skill_dir}: operations must be a table")
    return list(operations.keys())


def validate_topology_mode_contract(skill_dir: Path, contract: Mapping[str, object]) -> List[str]:
    errors: List[str] = []
    if contract.get("schema_version") != 2:
        errors.append("schema_version must be 2 for topology/mode contracts")
    skill = _as_string(contract, "skill", errors)
    entrypoint = _as_string(contract, "entrypoint", errors)
    base_references = _as_string_list(contract, "base_references", errors) or []
    topologies = _as_string_list(contract, "topologies", errors) or []
    modes = _as_string_list(contract, "modes", errors) or []
    character_budget = _positive_int(contract, "character_budget", errors)
    estimated_token_budget = _positive_int(contract, "estimated_token_budget", errors)
    max_file_count = _positive_int(contract, "max_file_count", errors)
    min_headroom_percent = _non_negative_int(contract, "min_headroom_percent", errors)
    operations = contract.get("operations")
    if not isinstance(operations, dict) or not operations:
        errors.append("operations must contain at least one operation table")
        operations = {}

    _validate_name_list("topology", topologies, errors)
    _validate_name_list("mode", modes, errors)
    if skill and skill != skill_dir.name:
        errors.append(f"skill must match directory name: {skill_dir.name}")
    if entrypoint and not _safe_relative_path(entrypoint):
        errors.append(f"invalid entrypoint path: {entrypoint}")
    if entrypoint and not (skill_dir / entrypoint).is_file():
        errors.append(f"missing entrypoint: {entrypoint}")
    for reference in base_references:
        _validate_reference(skill_dir, reference, errors)
    for topology in topologies:
        _validate_reference(skill_dir, f"references/{topology}.md", errors)
    for mode in modes:
        _validate_reference(skill_dir, f"references/modes/{mode}.md", errors)

    expected_operations = {f"{topology}.{mode}" for topology in topologies for mode in modes}
    for operation in sorted(expected_operations - set(operations)):
        errors.append(f"missing topology/mode operation: {operation}")

    for operation, raw_config in operations.items():
        if operation not in expected_operations:
            errors.append(f"unexpected topology/mode operation: {operation}")
        if not isinstance(raw_config, dict):
            errors.append(f"operation {operation} must be a table")
            continue
        references = _as_string_list(raw_config, "references", errors) or []
        topology = _as_string(raw_config, "topology", errors)
        mode = _as_string(raw_config, "mode", errors)
        combined = ([entrypoint] if entrypoint else []) + base_references + references
        for duplicate in sorted({item for item in combined if combined.count(item) > 1}):
            errors.append(f"duplicate reference in operation {operation}: {duplicate}")
        for reference in references:
            _validate_reference(skill_dir, reference, errors)
        if topology and topology not in topologies:
            errors.append(f"operation {operation} uses unknown topology: {topology}")
        if mode and mode not in modes:
            errors.append(f"operation {operation} uses unknown mode: {mode}")
        if topology and mode:
            expected_name = f"{topology}.{mode}"
            if operation != expected_name:
                errors.append(f"operation {operation} must be named {expected_name}")
            topology_reference = f"references/{topology}.md"
            mode_reference = f"references/modes/{mode}.md"
            if topology_reference not in references:
                errors.append(f"operation {operation} missing topology reference: {topology_reference}")
            if mode_reference not in references:
                errors.append(f"operation {operation} missing mode reference: {mode_reference}")
        if entrypoint and character_budget and estimated_token_budget and max_file_count and min_headroom_percent is not None:
            files = [skill_dir / entrypoint]
            files.extend(skill_dir / reference for reference in base_references)
            files.extend(skill_dir / reference for reference in references)
            budget = _matrix_budget(contract, raw_config)
            metrics = collect_file_metrics([path for path in files if path.is_file()], budget)
            if len(combined) > max_file_count:
                errors.append(f"max file count exceeded in operation {operation}: {len(combined)} > {max_file_count}")
            if metrics["character_count"] > character_budget:
                errors.append(
                    f"character budget exceeded in operation {operation}: "
                    f"{metrics['character_count']} > {character_budget}"
                )
            if metrics["estimated_token_count"] > estimated_token_budget:
                errors.append(
                    "estimated token budget exceeded in operation "
                    f"{operation}: {metrics['estimated_token_count']} > {estimated_token_budget}"
                )
            headroom = metrics.get("headroom_percent")
            if isinstance(headroom, int) and headroom < min_headroom_percent:
                errors.append(
                    f"headroom below minimum in operation {operation}: {headroom}% < {min_headroom_percent}%"
                )
    return errors


def validate_skill_dir_for_context(skill_dir: Path) -> List[str]:
    try:
        contract = load_contract(skill_dir)
    except ContractError as exc:
        return [str(exc)]
    if _is_topology_mode_contract(contract):
        return validate_topology_mode_contract(skill_dir, contract)
    return validate_skill_dir(skill_dir)


def _policy_user_facing_skill_dirs() -> List[Path]:
    try:
        policy = load_policy(DEFAULT_POLICY_PATH)
    except Exception as exc:  # pragma: no cover - surfaced as ContractError.
        raise ContractError(str(exc)) from exc
    families = policy.get("families")
    if not isinstance(families, dict):
        raise ContractError("skill architecture policy must contain families")
    family = families.get(REQUIRED_FAMILY_ID)
    if not isinstance(family, dict):
        raise ContractError(f"skill architecture policy missing family: {REQUIRED_FAMILY_ID}")
    skill_names = family.get("user_facing_skills")
    if not isinstance(skill_names, list) or not all(isinstance(name, str) for name in skill_names):
        raise ContractError(f"{REQUIRED_FAMILY_ID}.user_facing_skills must be an array of strings")
    return [REPO_ROOT / "skills" / name for name in skill_names]


def run_validation(
    argv: Sequence[str] | None = None,
    *,
    success_label: str = "skill context",
    resolve_skill: Callable[[str], Path] = resolve_skill_path,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--all", action="store_true", help="validate all skill context contracts")
    target.add_argument("--skill", help="skill directory to validate")
    parser.add_argument("--json", action="store_true", help="emit JSON result")
    args = parser.parse_args(argv)

    try:
        if args.all:
            skill_dirs = _policy_user_facing_skill_dirs() if success_label.startswith("loop skill") else all_skill_dirs()
        else:
            skill_dirs = [resolve_skill(args.skill)]
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
        errors = validate_skill_dir_for_context(skill_dir)
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
