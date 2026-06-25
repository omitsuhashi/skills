from __future__ import annotations

import re
from pathlib import Path
from typing import Any


WORD_RE = re.compile(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*|[^\W\s_]+", re.UNICODE)


class ContextContractError(Exception):
    """Raised when a context contract cannot be read for operation selection."""


def _strip_comment(line: str) -> str:
    in_string = False
    escaped = False
    result: list[str] = []
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
        raise ContextContractError("invalid TOML: unterminated string")
    return "".join(result).strip()


def _parse_string(value: str) -> str:
    if not (value.startswith('"') and value.endswith('"')):
        raise ContextContractError(f"invalid TOML string: {value}")
    return bytes(value[1:-1], "utf-8").decode("unicode_escape")


def _parse_array(value: str) -> list[str]:
    if not (value.startswith("[") and value.endswith("]")):
        raise ContextContractError(f"invalid TOML array: {value}")
    body = value[1:-1].strip()
    if not body:
        return []
    items: list[str] = []
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
        raise ContextContractError("invalid TOML array: unterminated string")
    tail = body[start:].strip()
    if tail:
        items.append(_parse_string(tail))
    return items


def _parse_value(value: str) -> Any:
    if value.startswith('"'):
        return _parse_string(value)
    if value.startswith("["):
        return _parse_array(value)
    if re.fullmatch(r"[0-9]+", value):
        return int(value)
    raise ContextContractError(f"invalid TOML value: {value}")


def _parse_operation_header(header: str) -> str:
    if not header.startswith("operations."):
        raise ContextContractError(f"invalid TOML table: [{header}]")
    operation = header.removeprefix("operations.")
    if operation.startswith('"') and operation.endswith('"'):
        return _parse_string(operation)
    if re.fullmatch(r"[A-Za-z0-9_-]+", operation):
        return operation
    raise ContextContractError(f"invalid TOML operation table: [{header}]")


def parse_context_contract(text: str) -> dict[str, Any]:
    contract: dict[str, Any] = {"operations": {}}
    current: dict[str, Any] = contract
    pending_array: str | None = None
    logical_lines: list[str] = []
    for raw_line in text.splitlines():
        line = _strip_comment(raw_line)
        if not line:
            continue
        if pending_array is not None:
            pending_array = f"{pending_array} {line}"
            if line.endswith("]"):
                logical_lines.append(pending_array)
                pending_array = None
            continue
        if "=" in line:
            _, raw_value = [part.strip() for part in line.split("=", 1)]
            if raw_value.startswith("[") and not raw_value.endswith("]"):
                pending_array = line
                continue
        logical_lines.append(line)
    if pending_array is not None:
        raise ContextContractError("invalid TOML array: missing closing bracket")

    for line in logical_lines:
        if line.startswith("[") and line.endswith("]"):
            operation = _parse_operation_header(line[1:-1].strip())
            operations = contract["operations"]
            if operation in operations:
                raise ContextContractError(f"duplicate operation table: {operation}")
            operations[operation] = {}
            current = operations[operation]
            continue
        if "=" not in line:
            raise ContextContractError(f"invalid TOML syntax: {line}")
        key, raw_value = [part.strip() for part in line.split("=", 1)]
        current[key] = _parse_value(raw_value)
    return contract


def load_context_contract(skill_dir: Path) -> dict[str, Any]:
    return parse_context_contract((skill_dir / "context-contract.toml").read_text(encoding="utf-8"))


def operation_read_set(skill_dir: Path, repo_root: Path, operation: str) -> dict[str, Any]:
    contract = load_context_contract(skill_dir)
    operations = contract.get("operations")
    if not isinstance(operations, dict) or operation not in operations:
        raise ContextContractError(f"unknown operation: {operation}")
    operation_config = operations[operation]
    if not isinstance(operation_config, dict):
        raise ContextContractError(f"invalid operation config: {operation}")

    entrypoint = contract.get("entrypoint")
    base_references = contract.get("base_references")
    operation_references = operation_config.get("references", [])
    if not isinstance(entrypoint, str):
        raise ContextContractError("entrypoint must be a string")
    if not isinstance(base_references, list):
        raise ContextContractError("base_references must be an array")
    if not isinstance(operation_references, list):
        raise ContextContractError(f"operations.{operation}.references must be an array")
    word_budget = operation_config.get("word_budget", contract.get("word_budget"))
    max_file_count = operation_config.get("max_file_count", contract.get("max_file_count"))
    if not isinstance(word_budget, int) or not isinstance(max_file_count, int):
        raise ContextContractError("word_budget and max_file_count must be integers")

    relative_files = [entrypoint, *base_references, *operation_references]
    absolute_files = [skill_dir / path for path in relative_files]
    missing = [path.as_posix() for path in absolute_files if not path.is_file()]
    if missing:
        raise ContextContractError("missing context file: " + ", ".join(missing))

    word_count = sum(len(WORD_RE.findall(path.read_text(encoding="utf-8"))) for path in absolute_files)
    file_count = len(absolute_files)
    return {
        "files": [path.relative_to(repo_root).as_posix() for path in absolute_files],
        "file_count": file_count,
        "max_file_count": max_file_count,
        "word_count": word_count,
        "word_budget": word_budget,
        "budget_headroom": word_budget - word_count,
        "within_budget": word_count <= word_budget and file_count <= max_file_count,
    }
