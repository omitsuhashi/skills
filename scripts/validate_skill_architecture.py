#!/usr/bin/env python3
"""Validate repository skill architecture policy.

This script intentionally parses the small TOML subset used by
skill-architecture.toml so the repository stays compatible with Python 3.9.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, MutableMapping, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = REPO_ROOT / "skill-architecture.toml"
SKILLS_ROOT = REPO_ROOT / "skills"
REQUIRED_FAMILY_ID = "repository-change-loop"
SKILL_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
EXPECTED_CONTEXT_COMPACTION_POLICY = {
    "soft_trigger_percent": 65,
    "hard_stop_percent": 75,
    "mandatory_handoff_compaction": 1,
}


class PolicyError(Exception):
    """Raised when the architecture policy cannot be parsed."""


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
        raise PolicyError("invalid TOML: unterminated string")
    return "".join(result).strip()


def _parse_string(value: str) -> str:
    if not (value.startswith('"') and value.endswith('"')):
        raise PolicyError(f"invalid TOML string: {value}")
    body = value[1:-1]
    try:
        return bytes(body, "utf-8").decode("unicode_escape")
    except UnicodeDecodeError as exc:
        raise PolicyError(f"invalid TOML string escape: {value}") from exc


def _parse_array(value: str) -> List[str]:
    if not (value.startswith("[") and value.endswith("]")):
        raise PolicyError(f"invalid TOML array: {value}")
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
        raise PolicyError("invalid TOML array: unterminated string")
    tail = body[start:].strip()
    if tail:
        items.append(_parse_string(tail))
    elif not body.rstrip().endswith(","):
        raise PolicyError(f"invalid TOML array: {value}")
    return items


def _parse_value(value: str) -> object:
    if value.startswith('"'):
        return _parse_string(value)
    if value.startswith("["):
        return _parse_array(value)
    if re.fullmatch(r"[0-9]+", value):
        return int(value)
    raise PolicyError(f"invalid TOML value: {value}")


def _logical_lines(text: str) -> List[Tuple[int, str]]:
    logical: List[Tuple[int, str]] = []
    pending_array: str | None = None
    pending_line_number: int | None = None
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw_line)
        if not line:
            continue
        if pending_array is not None:
            pending_array = f"{pending_array} {line}"
            if line.endswith("]"):
                logical.append((pending_line_number or line_number, pending_array))
                pending_array = None
                pending_line_number = None
            continue
        if "=" in line:
            _, raw_value = [part.strip() for part in line.split("=", 1)]
            if raw_value.startswith("[") and not raw_value.endswith("]"):
                pending_array = line
                pending_line_number = line_number
                continue
        logical.append((line_number, line))
    if pending_array is not None:
        raise PolicyError(f"invalid TOML array at line {pending_line_number}: missing closing bracket")
    return logical


def _table_for_path(root: MutableMapping[str, object], header: str) -> MutableMapping[str, object]:
    parts = header.split(".")
    if not parts or not all(SKILL_NAME_RE.fullmatch(part) for part in parts):
        raise PolicyError(f"invalid TOML table: [{header}]")
    current = root
    for part in parts:
        existing = current.get(part)
        if existing is None:
            existing = {}
            current[part] = existing
        if not isinstance(existing, dict):
            raise PolicyError(f"invalid TOML table: [{header}]")
        current = existing
    return current


def parse_policy_text(text: str) -> Dict[str, object]:
    policy: Dict[str, object] = {}
    current: MutableMapping[str, object] = policy
    seen_keys: Dict[int, set[str]] = {}
    for line_number, line in _logical_lines(text):
        if line.startswith("[") and line.endswith("]"):
            current = _table_for_path(policy, line[1:-1].strip())
            seen_keys.setdefault(id(current), set())
            continue
        if "=" not in line:
            raise PolicyError(f"invalid TOML syntax at line {line_number}")
        key, raw_value = [part.strip() for part in line.split("=", 1)]
        if not SKILL_NAME_RE.fullmatch(key):
            raise PolicyError(f"invalid TOML key at line {line_number}: {key}")
        table_seen = seen_keys.setdefault(id(current), set())
        if key in table_seen:
            raise PolicyError(f"invalid TOML: duplicate key {key} at line {line_number}")
        table_seen.add(key)
        current[key] = _parse_value(raw_value)
    return policy


def load_policy(path: Path) -> Dict[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise PolicyError(f"missing policy: {path}") from exc
    try:
        return parse_policy_text(text)
    except PolicyError as exc:
        raise PolicyError(f"{path}: {exc}") from exc


def _as_string_list(mapping: Dict[str, object], field: str, errors: List[str]) -> List[str] | None:
    value = mapping.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{field} must be an array of non-empty strings")
        return None
    return list(value)


def _duplicates(values: Sequence[str]) -> List[str]:
    return sorted({value for value in values if values.count(value) > 1})


def _validate_context_compaction_policy(family: Dict[str, object], errors: List[str]) -> None:
    policy = family.get("context_compaction")
    if not isinstance(policy, dict):
        errors.append("repository-change-loop.context_compaction must be a table")
        return

    soft_trigger = policy.get("soft_trigger_percent")
    if type(soft_trigger) is not int or soft_trigger != EXPECTED_CONTEXT_COMPACTION_POLICY["soft_trigger_percent"]:
        errors.append("context_compaction.soft_trigger_percent must be 65")

    hard_stop = policy.get("hard_stop_percent")
    if type(hard_stop) is not int or hard_stop != EXPECTED_CONTEXT_COMPACTION_POLICY["hard_stop_percent"]:
        errors.append("context_compaction.hard_stop_percent must be exactly 75")

    mandatory_handoff = policy.get("mandatory_handoff_compaction")
    if (
        type(mandatory_handoff) is not int
        or mandatory_handoff != EXPECTED_CONTEXT_COMPACTION_POLICY["mandatory_handoff_compaction"]
    ):
        errors.append("context_compaction.mandatory_handoff_compaction must be integer flag 1")


def _actual_skill_names() -> List[str]:
    if not SKILLS_ROOT.is_dir():
        return []
    return sorted(path.parent.name for path in SKILLS_ROOT.glob("*/SKILL.md"))


def validate_policy(policy: Dict[str, object]) -> List[str]:
    errors: List[str] = []
    if policy.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    families = policy.get("families")
    if not isinstance(families, dict):
        errors.append("families must contain repository-change-loop")
        return errors
    family = families.get(REQUIRED_FAMILY_ID)
    if not isinstance(family, dict):
        errors.append(f"missing family: {REQUIRED_FAMILY_ID}")
        return errors

    user_facing = _as_string_list(family, "user_facing_skills", errors) or []
    forbidden = _as_string_list(family, "forbidden_standalone_skill_names", errors) or []
    internal_components = _as_string_list(family, "internal_components", errors) or []

    if len(user_facing) != 2:
        errors.append("repository-change-loop.user_facing_skills must contain exactly 2 skills")
    for duplicate in _duplicates(user_facing):
        errors.append(f"duplicate user-facing skill: {duplicate}")
    for duplicate in _duplicates(forbidden):
        errors.append(f"duplicate forbidden standalone skill name: {duplicate}")
    for skill_name in user_facing + forbidden:
        if not SKILL_NAME_RE.fullmatch(skill_name):
            errors.append(f"invalid skill name: {skill_name}")

    actual_skills = set(_actual_skill_names())
    for skill_name in user_facing:
        if skill_name not in actual_skills:
            errors.append(f"missing user-facing skill directory: skills/{skill_name}/SKILL.md")
    for skill_name in sorted(set(forbidden) & actual_skills):
        errors.append(f"forbidden standalone skill exists: skills/{skill_name}/SKILL.md")
    for skill_name in sorted(set(forbidden) & set(user_facing)):
        errors.append(f"forbidden skill listed as user-facing: {skill_name}")

    if not forbidden:
        errors.append("forbidden_standalone_skill_names must not be empty")
    if not internal_components:
        errors.append("internal_components must not be empty")
    _validate_context_compaction_policy(family, errors)
    return errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="validate the repository architecture policy")
    parser.add_argument("--policy", default=str(DEFAULT_POLICY_PATH), help="policy file path")
    parser.add_argument("--json", action="store_true", help="emit JSON result")
    args = parser.parse_args(argv)

    if not args.all:
        parser.error("--all is required for repository policy validation")

    policy_path = Path(args.policy)
    if not policy_path.is_absolute():
        policy_path = REPO_ROOT / policy_path

    result = {
        "ok": False,
        "policy": policy_path.relative_to(REPO_ROOT).as_posix()
        if policy_path.is_relative_to(REPO_ROOT)
        else str(policy_path),
        "family": REQUIRED_FAMILY_ID,
        "errors": [],
    }
    try:
        policy = load_policy(policy_path)
        errors = validate_policy(policy)
    except PolicyError as exc:
        errors = [str(exc)]
    result["errors"] = errors
    result["ok"] = not errors

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["ok"]:
        print(f"OK: validated skill architecture policy ({REQUIRED_FAMILY_ID})")
    if errors:
        print("\n".join(errors), file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
