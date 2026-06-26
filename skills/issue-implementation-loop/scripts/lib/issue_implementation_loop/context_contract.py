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


def _first_int(mapping: dict[str, Any], fields: tuple[str, ...]) -> int | None:
    for field in fields:
        value = mapping.get(field)
        if isinstance(value, int):
            return value
    return None


def _budget(contract: dict[str, Any], operation_config: dict[str, Any]) -> dict[str, int | None]:
    def override(fields: tuple[str, ...]) -> int | None:
        value = _first_int(operation_config, fields)
        return value if value is not None else _first_int(contract, fields)

    return {
        "word_budget": override(("word_budget",)),
        "character_budget": override(("character_budget", "char_budget")),
        "non_whitespace_character_budget": override(("non_whitespace_character_budget",)),
        "estimated_token_budget": override(("estimated_token_budget", "token_budget")),
        "max_file_count": override(("max_file_count",)),
        "min_headroom_percent": override(
            ("min_headroom_percent", "minimum_headroom_percent", "headroom_percent")
        ),
    }


def _is_cjk(char: str) -> bool:
    codepoint = ord(char)
    return (
        0x3040 <= codepoint <= 0x30FF
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0xAC00 <= codepoint <= 0xD7AF
    )


def _estimated_token_count(text: str) -> int:
    tokens = 0
    ascii_run = 0

    def flush_ascii() -> None:
        nonlocal ascii_run, tokens
        if ascii_run:
            tokens += (ascii_run + 2) // 3
            ascii_run = 0

    for char in text:
        if char.isspace():
            flush_ascii()
            continue
        if _is_cjk(char):
            flush_ascii()
            tokens += 1
        elif ord(char) < 128 and (char.isalnum() or char == "_"):
            ascii_run += 1
        elif ord(char) < 128:
            flush_ascii()
            tokens += 1
        else:
            flush_ascii()
            tokens += 1
    flush_ascii()
    return tokens


def _headroom_percent(used: int, budget: int | None) -> int | None:
    if not budget:
        return None
    return ((budget - used) * 100) // budget


def _require_positive(value: int | None, field: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ContextContractError(f"{field} must be a positive integer")
    return value


def _require_non_negative(value: int | None, field: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ContextContractError(f"{field} must be a non-negative integer")
    return value


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
    schema_version = contract.get("schema_version", 1)
    if schema_version not in (1, 2):
        raise ContextContractError("schema_version must be 1 or 2")
    budget = _budget(contract, operation_config)
    max_file_count = _require_positive(budget["max_file_count"], "max_file_count")
    if schema_version == 1:
        _require_positive(budget["word_budget"], "word_budget")
    else:
        _require_positive(budget["character_budget"], "character_budget")
        _require_positive(budget["estimated_token_budget"], "estimated_token_budget")
        _require_non_negative(budget["min_headroom_percent"], "min_headroom_percent")

    relative_files = [entrypoint, *base_references, *operation_references]
    absolute_files = [skill_dir / path for path in relative_files]
    missing = [path.as_posix() for path in absolute_files if not path.is_file()]
    if missing:
        raise ContextContractError("missing context file: " + ", ".join(missing))

    texts = [path.read_text(encoding="utf-8") for path in absolute_files]
    word_count = sum(len(WORD_RE.findall(text)) for text in texts)
    character_count = sum(len(text) for text in texts)
    non_whitespace_character_count = sum(1 for text in texts for char in text if not char.isspace())
    estimated_token_count = sum(_estimated_token_count(text) for text in texts)
    file_count = len(absolute_files)
    word_budget = budget["word_budget"]
    character_budget = budget["character_budget"]
    non_whitespace_budget = budget["non_whitespace_character_budget"]
    estimated_token_budget = budget["estimated_token_budget"]
    headroom_percent = (
        _headroom_percent(estimated_token_count, estimated_token_budget)
        if estimated_token_budget
        else _headroom_percent(character_count, character_budget)
        if character_budget
        else _headroom_percent(word_count, word_budget)
    )
    min_headroom = budget["min_headroom_percent"]
    within_budget = file_count <= max_file_count
    if word_budget:
        within_budget = within_budget and word_count <= word_budget
    if character_budget:
        within_budget = within_budget and character_count <= character_budget
    if non_whitespace_budget:
        within_budget = within_budget and non_whitespace_character_count <= non_whitespace_budget
    if estimated_token_budget:
        within_budget = within_budget and estimated_token_count <= estimated_token_budget
    if isinstance(min_headroom, int) and isinstance(headroom_percent, int):
        within_budget = within_budget and headroom_percent >= min_headroom

    return {
        "files": [path.relative_to(repo_root).as_posix() for path in absolute_files],
        "file_count": file_count,
        "max_file_count": max_file_count,
        "word_count": word_count,
        "word_budget": word_budget,
        "budget_headroom": word_budget - word_count if word_budget else None,
        "character_count": character_count,
        "character_budget": character_budget,
        "non_whitespace_character_count": non_whitespace_character_count,
        "non_whitespace_character_budget": non_whitespace_budget,
        "estimated_token_count": estimated_token_count,
        "estimated_token_budget": estimated_token_budget,
        "headroom_percent": headroom_percent,
        "min_headroom_percent": min_headroom,
        "within_budget": within_budget,
    }
