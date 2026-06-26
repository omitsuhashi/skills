"""Parse, inspect, and validate skill context contracts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Mapping, MutableMapping, Sequence, Tuple

from validate_skill_architecture import (
    DEFAULT_POLICY_PATH,
    PolicyError,
    REQUIRED_FAMILY_ID,
    load_policy,
)

from skill_context.metrics import collect_file_metrics


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills"


class ContractError(Exception):
    """Raised when a context contract cannot be parsed."""


def _policy_family(errors: List[str]) -> Dict[str, object]:
    try:
        policy = load_policy(DEFAULT_POLICY_PATH)
    except PolicyError as exc:
        errors.append(str(exc))
        return {}
    families = policy.get("families")
    if not isinstance(families, dict):
        errors.append("skill architecture policy must contain families")
        return {}
    family = families.get(REQUIRED_FAMILY_ID)
    if not isinstance(family, dict):
        errors.append(f"skill architecture policy missing family: {REQUIRED_FAMILY_ID}")
        return {}
    return family


def _policy_string_list(family: Dict[str, object], field: str, errors: List[str]) -> List[str]:
    value = family.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{REQUIRED_FAMILY_ID}.{field} must be an array of non-empty strings")
        return []
    return list(value)


def _forbidden_standalone_skill_names(errors: List[str]) -> set[str]:
    family = _policy_family(errors)
    if not family:
        return set()
    return set(_policy_string_list(family, "forbidden_standalone_skill_names", errors))


def all_skill_dirs() -> List[Path]:
    errors: List[str] = []
    family = _policy_family(errors)
    skill_names = _policy_string_list(family, "user_facing_skills", errors) if family else []
    if errors:
        raise ContractError("; ".join(errors))

    skill_dirs: List[Path] = []
    seen: set[Path] = set()
    for skill_name in skill_names:
        skill_dir = SKILLS_ROOT / skill_name
        skill_dirs.append(skill_dir)
        seen.add(skill_dir)
    for contract_path in sorted(SKILLS_ROOT.glob("*/context-contract.toml")):
        skill_dir = contract_path.parent
        if skill_dir not in seen:
            skill_dirs.append(skill_dir)
            seen.add(skill_dir)
    return skill_dirs


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


def _logical_lines(text: str) -> List[Tuple[int, str]]:
    logical_lines: List[Tuple[int, str]] = []
    pending_array: str | None = None
    pending_line_number: int | None = None
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
    return logical_lines


def parse_contract_text(text: str) -> Dict[str, object]:
    contract: Dict[str, object] = {"operations": {}}
    current: MutableMapping[str, object] = contract
    seen_top_level = set()
    seen_operation_keys: Dict[str, set] = {}
    current_operation: str | None = None

    for line_number, line in _logical_lines(text):
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


def _schema_version(contract: Mapping[str, object], errors: List[str]) -> int:
    value = contract.get("schema_version", 1)
    if value not in (1, 2):
        errors.append("schema_version must be 1 or 2")
        return 1
    assert isinstance(value, int)
    return value


def _as_string(contract: Mapping[str, object], field: str, errors: List[str]) -> str | None:
    value = contract.get(field)
    if not isinstance(value, str) or not value:
        errors.append(f"{field} must be a non-empty string")
        return None
    return value


def _as_positive_int(mapping: Mapping[str, object], field: str, errors: List[str]) -> int | None:
    value = mapping.get(field)
    if not isinstance(value, int) or value <= 0:
        errors.append(f"{field} must be a positive integer")
        return None
    return value


def _as_non_negative_int(mapping: Mapping[str, object], field: str, errors: List[str]) -> int | None:
    value = mapping.get(field)
    if not isinstance(value, int) or value < 0:
        errors.append(f"{field} must be a non-negative integer")
        return None
    return value


def _as_string_list(
    mapping: Mapping[str, object], field: str, errors: List[str], display: str | None = None
) -> List[str] | None:
    value = mapping.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{display or field} must be an array of non-empty strings")
        return None
    return list(value)


def _safe_relative_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts and value == path.as_posix()


def _optional_positive_int(mapping: Mapping[str, object], field: str, errors: List[str]) -> int | None:
    value = mapping.get(field)
    if value is None:
        return None
    if not isinstance(value, int) or value <= 0:
        errors.append(f"{field} must be a positive integer")
        return None
    return value


def _optional_non_negative_int(mapping: Mapping[str, object], field: str, errors: List[str]) -> int | None:
    value = mapping.get(field)
    if value is None:
        return None
    if not isinstance(value, int) or value < 0:
        errors.append(f"{field} must be a non-negative integer")
        return None
    return value


def _first_int(mapping: Mapping[str, object], fields: Sequence[str]) -> int | None:
    for field in fields:
        value = mapping.get(field)
        if isinstance(value, int):
            return value
    return None


def _override_int(
    raw_config: Mapping[str, object],
    contract: Mapping[str, object],
    fields: Sequence[str],
) -> int | None:
    value = _first_int(raw_config, fields)
    return value if value is not None else _first_int(contract, fields)


def _budget(contract: Mapping[str, object], raw_config: Mapping[str, object]) -> Dict[str, int | None]:
    return {
        "word_budget": _override_int(raw_config, contract, ("word_budget",)),
        "character_budget": _override_int(raw_config, contract, ("character_budget", "char_budget")),
        "non_whitespace_character_budget": _override_int(
            raw_config,
            contract,
            ("non_whitespace_character_budget",),
        ),
        "estimated_token_budget": _override_int(
            raw_config,
            contract,
            ("estimated_token_budget", "token_budget"),
        ),
        "max_file_count": _override_int(raw_config, contract, ("max_file_count",)),
        "min_headroom_percent": _override_int(
            raw_config,
            contract,
            ("min_headroom_percent", "minimum_headroom_percent", "headroom_percent"),
        ),
    }


def _validate_budget_fields(contract: Mapping[str, object], schema_version: int, errors: List[str]) -> None:
    _as_positive_int(contract, "max_file_count", errors)
    if schema_version == 1:
        _as_positive_int(contract, "word_budget", errors)
        _optional_positive_int(contract, "character_budget", errors)
        _optional_positive_int(contract, "estimated_token_budget", errors)
        _optional_non_negative_int(contract, "min_headroom_percent", errors)
        return
    _as_positive_int(contract, "character_budget", errors)
    _as_positive_int(contract, "estimated_token_budget", errors)
    if not any(field in contract for field in ("min_headroom_percent", "minimum_headroom_percent", "headroom_percent")):
        errors.append("min_headroom_percent must be a non-negative integer")
    else:
        for field in ("min_headroom_percent", "minimum_headroom_percent", "headroom_percent"):
            if field in contract:
                _as_non_negative_int(contract, field, errors)


def _validate_operation_budget_fields(
    operation: str,
    raw_config: Mapping[str, object],
    errors: List[str],
) -> None:
    for field in (
        "word_budget",
        "character_budget",
        "char_budget",
        "non_whitespace_character_budget",
        "estimated_token_budget",
        "token_budget",
        "max_file_count",
    ):
        if field in raw_config:
            value = raw_config.get(field)
            if not isinstance(value, int) or value <= 0:
                errors.append(f"operations.{operation}.{field} must be a positive integer")
    for field in ("min_headroom_percent", "minimum_headroom_percent", "headroom_percent"):
        if field in raw_config:
            value = raw_config.get(field)
            if not isinstance(value, int) or value < 0:
                errors.append(f"operations.{operation}.{field} must be a non-negative integer")


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


def operation_read_set(
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
    operation_config = operations[operation]
    assert isinstance(operation_config, dict)
    operation_references = operation_config.get("references", [])
    assert isinstance(operation_references, list)
    files = [skill_dir / entrypoint]
    files.extend(skill_dir / reference for reference in base_references)
    files.extend(skill_dir / reference for reference in operation_references)
    return files, _budget(contract, operation_config)


def inspect_operation(skill_dir: Path, operation: str) -> Dict[str, object]:
    contract = load_contract(skill_dir)
    errors = validate_contract(skill_dir, contract)
    if errors:
        raise ContractError("; ".join(errors))
    operations = contract["operations"]
    assert isinstance(operations, dict)
    if operation not in operations:
        raise ContractError(f"unknown operation: {operation}")
    schema = contract.get("schema_version", 1)
    assert isinstance(schema, int)
    files, budget = operation_read_set(skill_dir, contract, operation)
    metrics = collect_file_metrics(files, budget)
    word_budget = budget.get("word_budget")
    def display_path(path: Path) -> str:
        return path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else str(path)

    return {
        "schema_version": schema,
        "skill": contract["skill"],
        "operation": operation,
        "files": [display_path(path) for path in files],
        "file_count": metrics["file_count"],
        "max_file_count": budget.get("max_file_count"),
        "word_count": metrics["word_count"],
        "word_budget": word_budget,
        "budget_headroom": word_budget - metrics["word_count"] if word_budget else None,
        "character_count": metrics["character_count"],
        "non_whitespace_character_count": metrics["non_whitespace_character_count"],
        "estimated_token_count": metrics["estimated_token_count"],
        "headroom_percent": metrics["headroom_percent"],
        "budget": budget,
    }


def _existing_files(skill_dir: Path, paths: Sequence[str]) -> List[Path]:
    return [skill_dir / value for value in paths if value and (skill_dir / value).is_file()]


def _validate_operation_metrics(
    operation: str,
    files: List[Path],
    declared_file_count: int,
    budget: Mapping[str, int | None],
    errors: List[str],
) -> None:
    metrics = collect_file_metrics(files, budget)
    max_file_count = budget.get("max_file_count")
    if isinstance(max_file_count, int) and declared_file_count > max_file_count:
        errors.append(f"max file count exceeded in operation {operation}: {declared_file_count} > {max_file_count}")
    word_budget = budget.get("word_budget")
    if isinstance(word_budget, int) and metrics["word_count"] > word_budget:
        errors.append(f"word budget exceeded in operation {operation}: {metrics['word_count']} > {word_budget}")
    character_budget = budget.get("character_budget")
    if isinstance(character_budget, int) and metrics["character_count"] > character_budget:
        errors.append(
            f"character budget exceeded in operation {operation}: {metrics['character_count']} > {character_budget}"
        )
    non_whitespace_budget = budget.get("non_whitespace_character_budget")
    if isinstance(non_whitespace_budget, int) and metrics["non_whitespace_character_count"] > non_whitespace_budget:
        errors.append(
            "non-whitespace character budget exceeded in operation "
            f"{operation}: {metrics['non_whitespace_character_count']} > {non_whitespace_budget}"
        )
    estimated_token_budget = budget.get("estimated_token_budget")
    if isinstance(estimated_token_budget, int) and metrics["estimated_token_count"] > estimated_token_budget:
        errors.append(
            "estimated token budget exceeded in operation "
            f"{operation}: {metrics['estimated_token_count']} > {estimated_token_budget}"
        )
    min_headroom = budget.get("min_headroom_percent")
    headroom = metrics.get("headroom_percent")
    if isinstance(min_headroom, int) and isinstance(headroom, int) and headroom < min_headroom:
        errors.append(f"headroom below minimum in operation {operation}: {headroom}% < {min_headroom}%")


def validate_contract(skill_dir: Path, contract: Dict[str, object]) -> List[str]:
    errors: List[str] = []
    forbidden_standalone_skill_names = _forbidden_standalone_skill_names(errors)
    schema = _schema_version(contract, errors)
    skill = _as_string(contract, "skill", errors)
    entrypoint = _as_string(contract, "entrypoint", errors)
    base_references = _as_string_list(contract, "base_references", errors)
    _validate_budget_fields(contract, schema, errors)
    operations = contract.get("operations")
    if not isinstance(operations, dict) or not operations:
        errors.append("operations must contain at least one operation table")
        operations = {}

    if skill:
        if skill != skill_dir.name:
            errors.append(f"skill must match directory name: {skill_dir.name}")
        if skill in forbidden_standalone_skill_names:
            errors.append(f"forbidden standalone skill name: {skill}")

    if entrypoint and not _safe_relative_path(entrypoint):
        errors.append(f"invalid entrypoint path: {entrypoint}")
    if entrypoint and not (skill_dir / entrypoint).is_file():
        errors.append(f"missing entrypoint: {entrypoint}")

    references = base_references or []
    for reference in references:
        validate_reference_path(skill_dir, reference, errors)

    for operation, raw_config in operations.items():
        if operation in forbidden_standalone_skill_names:
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
        _validate_operation_budget_fields(operation, raw_config, errors)
        combined = ([entrypoint] if entrypoint else []) + references + (operation_references or [])
        duplicates = sorted({item for item in combined if combined.count(item) > 1})
        for duplicate in duplicates:
            errors.append(f"duplicate reference in operation {operation}: {duplicate}")
        for reference in operation_references or []:
            validate_reference_path(skill_dir, reference, errors)
        budget = _budget(contract, raw_config)
        existing_files = _existing_files(skill_dir, combined)
        if entrypoint and operation_references is not None:
            _validate_operation_metrics(operation, existing_files, len(combined), budget, errors)
    return errors


def validate_skill_dir(skill_dir: Path) -> List[str]:
    try:
        contract = load_contract(skill_dir)
    except ContractError as exc:
        return [str(exc)]
    return validate_contract(skill_dir, contract)
