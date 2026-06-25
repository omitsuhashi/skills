from __future__ import annotations

import os
from typing import Any

from ..constants import DELIVERY_INTENTS
from ..identifiers import is_issue_id, is_lower_kebab


def validate_input_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    repo_root = packet.get("repo_root")
    if not isinstance(repo_root, str) or not os.path.isabs(repo_root):
        errors.append("repo_root must be an absolute path")

    epic_id = packet.get("epic_id")
    if not isinstance(epic_id, str) or not is_lower_kebab(epic_id):
        errors.append("epic_id must be lower-kebab-case ASCII")

    spec = packet.get("spec")
    if not isinstance(spec, dict) or not spec.get("path"):
        errors.append("spec.path is required")

    delivery_intent = packet.get("delivery_intent")
    if delivery_intent not in DELIVERY_INTENTS:
        errors.append(f"delivery_intent must be one of {sorted(DELIVERY_INTENTS)}")

    work_items = packet.get("work_items")
    if not isinstance(work_items, list) or not work_items:
        errors.append("work_items must be a non-empty list")
        return errors

    seen: set[str] = set()
    for index, item in enumerate(work_items):
        prefix = f"work_items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not is_issue_id(item_id):
            errors.append(f"{prefix}.id must look like G2PR-001")
        elif item_id in seen:
            errors.append(f"{prefix}.id duplicates {item_id}")
        else:
            seen.add(item_id)
        if not item.get("title"):
            errors.append(f"{prefix}.title is required")
        for field in ("acceptance_criteria", "verification", "write_scope"):
            value = item.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"{prefix}.{field} must be a non-empty list")
        dependencies = item.get("dependencies", [])
        if not isinstance(dependencies, list):
            errors.append(f"{prefix}.dependencies must be a list")
            continue
        for dep_index, dep in enumerate(dependencies):
            dep_prefix = f"{prefix}.dependencies[{dep_index}]"
            if isinstance(dep, str):
                dep_issue = dep
            elif isinstance(dep, dict):
                dep_issue = dep.get("issue")
            else:
                errors.append(f"{dep_prefix} must be an issue ID or object")
                continue
            if not isinstance(dep_issue, str) or not is_issue_id(dep_issue):
                errors.append(f"{dep_prefix}.issue must look like G2PR-001")
            elif dep_issue not in seen and dep_issue not in {w.get("id") for w in work_items if isinstance(w, dict)}:
                errors.append(f"{dep_prefix}.issue references unknown issue {dep_issue}")
    return errors
