from __future__ import annotations

import os
from typing import Any

from ..identifiers import is_issue_id, is_lower_kebab
from ..worker_packet import (
    DEFAULT_PACKET_WORDS,
    HARD_PACKET_WORDS,
    MAX_INLINE_EXCERPT_WORDS_PER_FILE,
    MAX_INLINE_EXCERPT_WORDS_TOTAL,
    MAX_READ_PATHS,
    PACKET_CONTEXT_BUDGET_EXCEEDED,
    count_words,
    packet_word_count,
)


FORBIDDEN_TEXT_FIELDS = {
    "fullledger",
    "fullledgertext",
    "fullspec",
    "fullspectext",
    "ledgertext",
    "spectext",
}
TOP_LEVEL_FIELDS = {
    "branch",
    "context_policy",
    "dispatch_id",
    "epic_id",
    "inline_context",
    "issue_id",
    "issue_title",
    "packet_type",
    "read_paths",
    "report_contract",
    "schema_version",
    "task",
    "worktree",
    "write_scope",
}
CONTEXT_POLICY_FIELDS = {
    "hard_max_packet_words",
    "include_full_ledger_text",
    "include_full_spec_text",
    "max_inline_excerpt_words_per_file",
    "max_inline_excerpt_words_total",
    "max_packet_words",
    "max_read_paths",
    "paths_first",
}
READ_PATH_FIELDS = {"path", "purpose"}
INLINE_CONTEXT_FIELDS = {"excerpt", "is_full_document", "path", "purpose"}
TASK_FIELDS = {"acceptance_criteria", "stop_conditions", "summary", "verification"}
REPORT_CONTRACT_FIELDS = {"format", "validator"}


def _field_key(value: str) -> str:
    return "".join(char for char in value.lower() if char.isalnum())


def _as_string_list(value: Any, field: str, errors: list[str], *, required: bool = True) -> None:
    if value is None and not required:
        return
    if not isinstance(value, list) or (required and not value):
        errors.append(f"{field} must be a non-empty list")
        return
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{field}[{index}] must be a non-empty string")


def _forbidden_text_fields(value: Any, path: str = "") -> list[str]:
    if isinstance(value, dict):
        matches: list[str] = []
        for key, item in value.items():
            key_path = f"{path}.{key}" if path else str(key)
            if _field_key(str(key)) in FORBIDDEN_TEXT_FIELDS:
                matches.append(key_path)
            matches.extend(_forbidden_text_fields(item, key_path))
        return matches
    if isinstance(value, list):
        matches = []
        for index, item in enumerate(value):
            matches.extend(_forbidden_text_fields(item, f"{path}[{index}]"))
        return matches
    return []


def _reject_unknown_fields(
    value: dict[str, Any],
    allowed: set[str],
    path: str,
    errors: list[str],
) -> None:
    for key in sorted(value):
        if key not in allowed:
            display = f"{path}.{key}" if path else key
            errors.append(f"unknown field: {display}")


def validate_worker_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _reject_unknown_fields(packet, TOP_LEVEL_FIELDS, "", errors)

    if packet.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if packet.get("packet_type") != "issue_worker_dispatch":
        errors.append("packet_type must be issue_worker_dispatch")

    epic_id = packet.get("epic_id")
    if not isinstance(epic_id, str) or not is_lower_kebab(epic_id):
        errors.append("epic_id must be lower-kebab-case ASCII")
    issue_id = packet.get("issue_id")
    if not isinstance(issue_id, str) or not is_issue_id(issue_id):
        errors.append("issue_id must look like G2PR-001")
    for field in ("issue_title", "dispatch_id", "branch"):
        if not isinstance(packet.get(field), str) or not packet.get(field, "").strip():
            errors.append(f"{field} must be a non-empty string")
    worktree = packet.get("worktree")
    if not isinstance(worktree, str) or not os.path.isabs(worktree):
        errors.append("worktree must be an absolute path")
    _as_string_list(packet.get("write_scope"), "write_scope", errors)

    context_policy = packet.get("context_policy")
    if not isinstance(context_policy, dict):
        errors.append("context_policy is required")
        context_policy = {}
    else:
        _reject_unknown_fields(context_policy, CONTEXT_POLICY_FIELDS, "context_policy", errors)
    if context_policy.get("paths_first") is not True:
        errors.append("context_policy.paths_first must be true")
    max_packet_words = context_policy.get("max_packet_words", DEFAULT_PACKET_WORDS)
    hard_max_words = context_policy.get("hard_max_packet_words", HARD_PACKET_WORDS)
    max_read_paths = context_policy.get("max_read_paths", MAX_READ_PATHS)
    per_file_words = context_policy.get(
        "max_inline_excerpt_words_per_file",
        MAX_INLINE_EXCERPT_WORDS_PER_FILE,
    )
    total_inline_words = context_policy.get(
        "max_inline_excerpt_words_total",
        MAX_INLINE_EXCERPT_WORDS_TOTAL,
    )
    if not isinstance(max_packet_words, int) or max_packet_words < 1:
        errors.append("context_policy.max_packet_words must be a positive integer")
        max_packet_words = DEFAULT_PACKET_WORDS
    if max_packet_words > HARD_PACKET_WORDS:
        errors.append(f"context_policy.max_packet_words must be <= {HARD_PACKET_WORDS}")
    if hard_max_words != HARD_PACKET_WORDS:
        errors.append(f"context_policy.hard_max_packet_words must be {HARD_PACKET_WORDS}")
    if max_read_paths != MAX_READ_PATHS:
        errors.append(f"context_policy.max_read_paths must be {MAX_READ_PATHS}")
    if per_file_words != MAX_INLINE_EXCERPT_WORDS_PER_FILE:
        errors.append(
            "context_policy.max_inline_excerpt_words_per_file "
            f"must be {MAX_INLINE_EXCERPT_WORDS_PER_FILE}"
        )
    if total_inline_words != MAX_INLINE_EXCERPT_WORDS_TOTAL:
        errors.append(
            "context_policy.max_inline_excerpt_words_total "
            f"must be {MAX_INLINE_EXCERPT_WORDS_TOTAL}"
        )
    if context_policy.get("include_full_spec_text") is not False:
        errors.append("context_policy.include_full_spec_text must be false")
    if context_policy.get("include_full_ledger_text") is not False:
        errors.append("context_policy.include_full_ledger_text must be false")

    read_paths = packet.get("read_paths")
    if not isinstance(read_paths, list) or not read_paths:
        errors.append("read_paths must be a non-empty list")
        read_paths = []
    if len(read_paths) > MAX_READ_PATHS:
        errors.append(f"read_paths must contain at most {MAX_READ_PATHS} paths")
    for index, entry in enumerate(read_paths):
        prefix = f"read_paths[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        _reject_unknown_fields(entry, READ_PATH_FIELDS, prefix, errors)
        path = entry.get("path")
        if not isinstance(path, str) or not path.strip():
            errors.append(f"{prefix}.path must be a non-empty string")
        purpose = entry.get("purpose")
        if purpose is not None and (not isinstance(purpose, str) or not purpose.strip()):
            errors.append(f"{prefix}.purpose must be a non-empty string")

    inline_context = packet.get("inline_context", [])
    if not isinstance(inline_context, list):
        errors.append("inline_context must be a list")
        inline_context = []
    inline_words = 0
    inline_words_by_path: dict[str, int] = {}
    for index, entry in enumerate(inline_context):
        prefix = f"inline_context[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        _reject_unknown_fields(entry, INLINE_CONTEXT_FIELDS, prefix, errors)
        path = entry.get("path")
        excerpt = entry.get("excerpt")
        if not isinstance(path, str) or not path.strip():
            errors.append(f"{prefix}.path must be a non-empty string")
        if not isinstance(excerpt, str) or not excerpt.strip():
            errors.append(f"{prefix}.excerpt must be a non-empty string")
            continue
        words = count_words(excerpt)
        inline_words += words
        if isinstance(path, str) and path.strip():
            clean_path = path.strip()
            inline_words_by_path[clean_path] = inline_words_by_path.get(clean_path, 0) + words
        if words > MAX_INLINE_EXCERPT_WORDS_PER_FILE:
            errors.append(
                f"{prefix}.excerpt exceeds {MAX_INLINE_EXCERPT_WORDS_PER_FILE} words"
            )
        purpose = entry.get("purpose")
        if entry.get("is_full_document") is True or _field_key(str(purpose or "")) in {
            "fullspec",
            "fullledger",
        }:
            errors.append(f"{prefix} must not include full spec or full ledger text")
    if inline_words > MAX_INLINE_EXCERPT_WORDS_TOTAL:
        errors.append(
            f"inline_context exceeds {MAX_INLINE_EXCERPT_WORDS_TOTAL} total words"
        )
    for path, words in sorted(inline_words_by_path.items()):
        if words > MAX_INLINE_EXCERPT_WORDS_PER_FILE:
            errors.append(
                f"inline_context path {path} exceeds {MAX_INLINE_EXCERPT_WORDS_PER_FILE} words"
            )

    task = packet.get("task")
    if not isinstance(task, dict):
        errors.append("task is required")
    else:
        _reject_unknown_fields(task, TASK_FIELDS, "task", errors)
        if not isinstance(task.get("summary"), str) or not task.get("summary", "").strip():
            errors.append("task.summary must be a non-empty string")
        _as_string_list(task.get("acceptance_criteria"), "task.acceptance_criteria", errors)
        _as_string_list(task.get("verification"), "task.verification", errors)
        _as_string_list(task.get("stop_conditions"), "task.stop_conditions", errors)

    report_contract = packet.get("report_contract")
    if not isinstance(report_contract, dict):
        errors.append("report_contract is required")
    else:
        _reject_unknown_fields(
            report_contract,
            REPORT_CONTRACT_FIELDS,
            "report_contract",
            errors,
        )
        for field in ("format", "validator"):
            if not isinstance(report_contract.get(field), str) or not report_contract.get(field, "").strip():
                errors.append(f"report_contract.{field} must be a non-empty string")

    forbidden_fields = _forbidden_text_fields(packet)
    if forbidden_fields:
        errors.append(
            "full spec/full ledger text is forbidden; use read_paths instead: "
            + ", ".join(forbidden_fields)
        )

    words = packet_word_count(packet)
    if words > max_packet_words:
        errors.append(f"{PACKET_CONTEXT_BUDGET_EXCEEDED}: packet words {words} > {max_packet_words}")
    if words > HARD_PACKET_WORDS:
        errors.append(f"{PACKET_CONTEXT_BUDGET_EXCEEDED}: packet words {words} > hard {HARD_PACKET_WORDS}")
    return errors
