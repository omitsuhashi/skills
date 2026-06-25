#!/usr/bin/env python3
"""Validate loop-skill context contracts.

The repository runs on Python 3.9 in the default developer environment, so this
script intentionally parses the small TOML subset used by context contracts
instead of depending on tomllib or an external package.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, MutableMapping, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_RELATIVE_PATHS = (
    Path("skills/grill-to-pr-loop"),
    Path("skills/issue-implementation-loop"),
)
FORBIDDEN_STANDALONE_SKILL_NAMES = {
    "context-manager",
    "dependency-graph",
    "execution-envelope",
    "human-wait",
    "remote-delivery",
    "review-gate",
    "runtime-state",
    "scheduler",
    "worker-contract",
    "worktree-lifecycle",
}
WORD_RE = re.compile(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*|[^\W\s_]+", re.UNICODE)


class ContractError(Exception):
    """Raised when a context contract cannot be parsed."""


def _strip_comment(line: str) -> str:
    in_string = False
    escaped = False
    result = []
    for char in line:
        if escaped:
            result.append(char)
            escaped = False
            continue
        if char == "\\" and in_string:
            result.append(char)
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            result.append(char)
            continue
        if char == "#" and not in_string:
            break
        result.append(char)
    if in_string:
        raise ContractError("invalid TOML: unterminated string")
    return "".join(result).strip()


def _parse_string(value: str) -> str:
    if not (value.startswith('"') and value.endswith('"')):
        raise ContractError(f"invalid TOML string: {value}")
    body = value[1:-1]
    try:
        return bytes(body, "utf-8").decode("unicode_escape")
    except UnicodeDecodeError as exc:
        raise ContractError(f"invalid TOML string escape: {value}") from exc


def _parse_array(value: str) -> List[str]:
    if not (value.startswith("[") and value.endswith("]")):
        raise ContractError(f"invalid TOML array: {value}")
    body = value[1:-1].strip()
    if not body:
        return []
    items: List[str] = []
    start = 0
    in_string = False
    escaped = False
    for index, char in enumerate(body):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if char == "," and not in_string:
            items.append(_parse_string(body[start:index].strip()))
            start = index + 1
    if in_string:
        raise ContractError("invalid TOML array: unterminated string")
    tail = body[start:].strip()
    if tail:
        items.append(_parse_string(tail))
    elif not body.rstrip().endswith(","):
        raise ContractError(f"invalid TOML array: {value}")
    return items


def _parse_value(value: str) -> object:
    if value.startswith('"'):
        return _parse_string(value)
    if value.startswith("["):
        return _parse_array(value)
    if re.fullmatch(r"[0-9]+", value):
        return int(value)
    raise ContractError(f"invalid TOML value: {value}")


def _parse_table_header(header: str) -> str:
    if not header.startswith("operations."):
        raise ContractError(f"invalid TOML table: [{header}]")
    operation = header[len("operations.") :]
    if operation.startswith('"') and operation.endswith('"'):
        operation_name = _parse_string(operation)
    elif re.fullmatch(r"[A-Za-z0-9_-]+", operation):
        operation_name = operation
    else:
        raise ContractError(f"invalid TOML operation table: [{header}]")
    if not operation_name:
        raise ContractError(f"invalid TOML operation table: [{header}]")
    return operation_name


def parse_contract_text(text: str) -> Dict[str, object]:
    contract: Dict[str, object] = {"operations": {}}
    current: MutableMapping[str, object] = contract
    seen_top_level = set()
    seen_operation_keys: Dict[str, set] = {}
    current_operation: str | None = None
    pending_array: str | None = None
    pending_line_number: int | None = None
    logical_lines: List[Tuple[int, str]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw_line)
        if not line:
            continue
        if pending_array is not None:
            pending_array = f"{pending_array} {line}"
            if line.endswith("]"):
                logical_lines.append((pending_line_number or line_number, pending_array))
                pending_array = None
                pending_line_number = None
            continue
        if "=" in line:
            _, raw_value = [part.strip() for part in line.split("=", 1)]
            if raw_value.startswith("[") and not raw_value.endswith("]"):
                pending_array = line
                pending_line_number = line_number
                continue
        logical_lines.append((line_number, line))
    if pending_array is not None:
        raise ContractError(f"invalid TOML array at line {pending_line_number}: missing closing bracket")

    for line_number, line in logical_lines:
        if line.startswith("[") and line.endswith("]"):
            current_operation = _parse_table_header(line[1:-1].strip())
            operations = contract["operations"]
            assert isinstance(operations, dict)
            if current_operation in operations:
                raise ContractError(f"invalid TOML: duplicate operation table at line {line_number}")
            operations[current_operation] = {}
            seen_operation_keys[current_operation] = set()
            current = operations[current_operation]
            continue
        if "=" not in line:
            raise ContractError(f"invalid TOML syntax at line {line_number}")
        key, raw_value = [part.strip() for part in line.split("=", 1)]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", key):
            raise ContractError(f"invalid TOML key at line {line_number}: {key}")
        if current_operation is None:
            if key in seen_top_level:
                raise ContractError(f"invalid TOML: duplicate key {key} at line {line_number}")
            seen_top_level.add(key)
        else:
            if key in seen_operation_keys[current_operation]:
                raise ContractError(f"invalid TOML: duplicate key {key} at line {line_number}")
            seen_operation_keys[current_operation].add(key)
        current[key] = _parse_value(raw_value)
    return contract


def load_contract(skill_dir: Path) -> Dict[str, object]:
    contract_path = skill_dir / "context-contract.toml"
    try:
        text = contract_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ContractError(f"missing contract: {contract_path}") from exc
    try:
        return parse_contract_text(text)
    except ContractError as exc:
        raise ContractError(f"{contract_path}: {exc}") from exc


def _as_string(contract: Dict[str, object], field: str, errors: List[str]) -> str | None:
    value = contract.get(field)
    if not isinstance(value, str) or not value:
        errors.append(f"{field} must be a non-empty string")
        return None
    return value


def _as_positive_int(mapping: Dict[str, object], field: str, errors: List[str]) -> int | None:
    value = mapping.get(field)
    if not isinstance(value, int) or value <= 0:
        errors.append(f"{field} must be a positive integer")
        return None
    return value


def _as_string_list(
    mapping: Dict[str, object], field: str, errors: List[str], display: str | None = None
) -> List[str] | None:
    value = mapping.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{display or field} must be an array of non-empty strings")
        return None
    return list(value)


def _safe_relative_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts and value == path.as_posix()


def _word_count(path: Path) -> int:
    return len(WORD_RE.findall(path.read_text(encoding="utf-8")))


def operation_read_set(skill_dir: Path, contract: Dict[str, object], operation: str) -> Tuple[List[Path], int, int]:
    entrypoint = contract["entrypoint"]
    base_references = contract["base_references"]
    operations = contract["operations"]
    assert isinstance(entrypoint, str)
    assert isinstance(base_references, list)
    assert isinstance(operations, dict)
    operation_config = operations[operation]
    assert isinstance(operation_config, dict)
    operation_references = operation_config.get("references", [])
    assert isinstance(operation_references, list)
    budget = operation_config.get("word_budget", contract["word_budget"])
    max_files = operation_config.get("max_file_count", contract["max_file_count"])
    assert isinstance(budget, int)
    assert isinstance(max_files, int)
    files = [skill_dir / entrypoint]
    files.extend(skill_dir / reference for reference in base_references)
    files.extend(skill_dir / reference for reference in operation_references)
    return files, budget, max_files


def inspect_operation(skill_dir: Path, operation: str) -> Dict[str, object]:
    contract = load_contract(skill_dir)
    errors = validate_contract(skill_dir, contract)
    if errors:
        raise ContractError("; ".join(errors))
    operations = contract["operations"]
    assert isinstance(operations, dict)
    if operation not in operations:
        raise ContractError(f"unknown operation: {operation}")
    files, budget, max_files = operation_read_set(skill_dir, contract, operation)
    word_count = sum(_word_count(path) for path in files)
    return {
        "skill": contract["skill"],
        "operation": operation,
        "files": [path.relative_to(REPO_ROOT).as_posix() for path in files],
        "file_count": len(files),
        "max_file_count": max_files,
        "word_count": word_count,
        "word_budget": budget,
        "budget_headroom": budget - word_count,
    }


def validate_contract(skill_dir: Path, contract: Dict[str, object]) -> List[str]:
    errors: List[str] = []
    skill = _as_string(contract, "skill", errors)
    entrypoint = _as_string(contract, "entrypoint", errors)
    base_references = _as_string_list(contract, "base_references", errors)
    word_budget = _as_positive_int(contract, "word_budget", errors)
    max_file_count = _as_positive_int(contract, "max_file_count", errors)
    operations = contract.get("operations")
    if not isinstance(operations, dict) or not operations:
        errors.append("operations must contain at least one operation table")
        operations = {}

    if skill:
        if skill != skill_dir.name:
            errors.append(f"skill must match directory name: {skill_dir.name}")
        if skill in FORBIDDEN_STANDALONE_SKILL_NAMES:
            errors.append(f"forbidden standalone skill name: {skill}")

    if entrypoint and not _safe_relative_path(entrypoint):
        errors.append(f"invalid entrypoint path: {entrypoint}")
    if entrypoint and not (skill_dir / entrypoint).is_file():
        errors.append(f"missing entrypoint: {entrypoint}")

    references = base_references or []
    for reference in references:
        validate_reference_path(skill_dir, reference, errors)

    for operation, raw_config in operations.items():
        if operation in FORBIDDEN_STANDALONE_SKILL_NAMES:
            errors.append(f"forbidden standalone skill name: {operation}")
        if not isinstance(raw_config, dict):
            errors.append(f"operation {operation} must be a table")
            continue
        operation_references = _as_string_list(
            raw_config,
            "references",
            errors,
            display=f"operations.{operation}.references",
        )
        operation_budget = raw_config.get("word_budget", word_budget)
        operation_max_files = raw_config.get("max_file_count", max_file_count)
        if not isinstance(operation_budget, int) or operation_budget <= 0:
            errors.append(f"operations.{operation}.word_budget must be a positive integer")
        if not isinstance(operation_max_files, int) or operation_max_files <= 0:
            errors.append(f"operations.{operation}.max_file_count must be a positive integer")
        combined = ([entrypoint] if entrypoint else []) + references + (operation_references or [])
        duplicates = sorted({item for item in combined if combined.count(item) > 1})
        for duplicate in duplicates:
            errors.append(f"duplicate reference in operation {operation}: {duplicate}")
        for reference in operation_references or []:
            validate_reference_path(skill_dir, reference, errors)
        if entrypoint and operation_references is not None and isinstance(operation_budget, int):
            existing_files = [skill_dir / item for item in combined if item and (skill_dir / item).is_file()]
            word_count = sum(_word_count(path) for path in existing_files)
            if word_count > operation_budget:
                errors.append(
                    f"word budget exceeded in operation {operation}: {word_count} > {operation_budget}"
                )
        if isinstance(operation_max_files, int) and len(combined) > operation_max_files:
            errors.append(
                f"max file count exceeded in operation {operation}: {len(combined)} > {operation_max_files}"
            )
    return errors


def validate_reference_path(skill_dir: Path, reference: str, errors: List[str]) -> None:
    if not _safe_relative_path(reference):
        errors.append(f"invalid reference path: {reference}")
        return
    parts = Path(reference).parts
    if not parts or parts[0] != "references":
        errors.append(f"reference must be under references/: {reference}")
    elif len(parts) > 2:
        errors.append(f"reference depth > 1: {reference}")
    if not (skill_dir / reference).is_file():
        errors.append(f"missing reference: {reference}")


def validate_skill_dir(skill_dir: Path) -> List[str]:
    try:
        contract = load_contract(skill_dir)
    except ContractError as exc:
        return [str(exc)]
    return validate_contract(skill_dir, contract)


def all_skill_dirs() -> List[Path]:
    return [REPO_ROOT / relative for relative in CONTRACT_RELATIVE_PATHS]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--all", action="store_true", help="validate all loop skill context contracts")
    target.add_argument("--skill", help="skill directory to validate")
    parser.add_argument("--json", action="store_true", help="emit JSON result")
    args = parser.parse_args(argv)

    skill_dirs = all_skill_dirs() if args.all else [Path(args.skill).resolve()]
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
        print(f"OK: validated {len(skill_dirs)} loop skill context contract(s)")
    if stderr_lines:
        print("\n".join(stderr_lines), file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
