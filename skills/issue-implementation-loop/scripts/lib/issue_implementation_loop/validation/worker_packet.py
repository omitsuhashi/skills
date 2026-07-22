from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ..approved_spec_binding import (
    BindingError,
    approved_spec_binding_ref,
)
from ..identifiers import is_issue_id, is_lower_kebab
from ..worker_packet import (
    ACCESS_MODES,
    DEFAULT_PACKET_WORDS,
    HARD_PACKET_WORDS,
    MAX_INLINE_EXCERPT_WORDS_PER_FILE,
    MAX_INLINE_EXCERPT_WORDS_TOTAL,
    MAX_READ_PATHS,
    PACKET_CONTEXT_BUDGET_EXCEEDED,
    TASK_KINDS,
    count_words,
    packet_word_count,
    source_revision_record,
    trusted_worker_context,
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
TOP_LEVEL_FIELDS_V3 = TOP_LEVEL_FIELDS | {"access_mode", "source_revision", "task_kind"}
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
SOURCE_REVISION_FIELDS = {
    "approved_spec_binding",
    "execution_envelope",
    "runtime_state",
    "issue_source",
}
SOURCE_EXECUTION_ENVELOPE_FIELDS = {"path", "revision", "sha256"}
SOURCE_RUNTIME_STATE_FIELDS = {"path", "envelope_revision", "sha256"}
SOURCE_ISSUE_SOURCE_FIELDS = {"path", "sha256"}


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


def _require_fields(
    value: dict[str, Any],
    required: set[str],
    path: str,
    errors: list[str],
) -> None:
    for key in sorted(required - set(value)):
        display = f"{path}.{key}" if path else key
        errors.append(f"{display} is required")


def _resolve_packet_path(worktree: str, raw_path: str) -> Path | None:
    if not raw_path.strip() or raw_path.startswith("~"):
        return None
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = Path(worktree) / raw_path
    return candidate.resolve(strict=False)


def _path_stays_within_worktree(worktree: str, raw_path: str) -> bool:
    root = Path(worktree).resolve(strict=False)
    candidate = _resolve_packet_path(worktree, raw_path)
    if candidate is None:
        return False
    try:
        return os.path.commonpath([str(root), str(candidate)]) == str(root)
    except ValueError:
        return False


def _validate_packet_path(
    *,
    worktree: str,
    raw_path: Any,
    field: str,
    errors: list[str],
) -> None:
    if not isinstance(raw_path, str) or not raw_path.strip():
        return
    if not _path_stays_within_worktree(worktree, raw_path):
        errors.append(f"{field} must stay within worktree")


def _write_scope_path(scope: str) -> str:
    return scope.removeprefix("path:")


def _validate_source_record(
    record: Any,
    *,
    fields: set[str],
    integer_field: str | None,
    field: str,
    errors: list[str],
) -> None:
    if not isinstance(record, dict):
        errors.append(f"{field} is required")
        return
    _reject_unknown_fields(record, fields, field, errors)
    _require_fields(record, fields, field, errors)
    path = record.get("path")
    if not isinstance(path, str) or not path.strip() or not os.path.isabs(path):
        errors.append(f"{field}.path must be an absolute path")
    digest = record.get("sha256")
    if not (
        isinstance(digest, str)
        and len(digest) == 64
        and digest == digest.lower()
        and all(character in "0123456789abcdef" for character in digest)
    ):
        errors.append(f"{field}.sha256 must be lowercase sha256 hex")
    if integer_field is not None:
        revision = record.get(integer_field)
        if type(revision) is not int or revision < 1:
            errors.append(f"{field}.{integer_field} must be a positive integer")


def _validate_source_revision(packet: dict[str, Any], errors: list[str]) -> dict[str, str] | None:
    source_revision = packet.get("source_revision")
    if not isinstance(source_revision, dict):
        errors.append("source_revision is required")
        return None
    _reject_unknown_fields(source_revision, SOURCE_REVISION_FIELDS, "source_revision", errors)
    _require_fields(source_revision, SOURCE_REVISION_FIELDS, "source_revision", errors)
    try:
        binding = approved_spec_binding_ref(
            source_revision.get("approved_spec_binding")
        ).to_dict()
    except BindingError as error:
        errors.append(error.code)
        binding = None

    _validate_source_record(
        source_revision.get("execution_envelope"),
        fields=SOURCE_EXECUTION_ENVELOPE_FIELDS,
        integer_field="revision",
        field="source_revision.execution_envelope",
        errors=errors,
    )
    _validate_source_record(
        source_revision.get("runtime_state"),
        fields=SOURCE_RUNTIME_STATE_FIELDS,
        integer_field="envelope_revision",
        field="source_revision.runtime_state",
        errors=errors,
    )
    _validate_source_record(
        source_revision.get("issue_source"),
        fields=SOURCE_ISSUE_SOURCE_FIELDS,
        integer_field=None,
        field="source_revision.issue_source",
        errors=errors,
    )
    return binding


def _approved_semantics_match(packet: dict[str, Any], trusted: Any) -> bool:
    source_revision = packet.get("source_revision")
    if not isinstance(source_revision, dict):
        return False
    envelope = trusted.envelope
    approved_packet = trusted.approved_packet
    issue_id = packet.get("issue_id")
    approved = next(
        (
            item
            for item in approved_packet.get("work_items", [])
            if isinstance(item, dict) and item.get("id") == issue_id
        ),
        None,
    )
    envelope_item = envelope.get("work_items", {}).get(issue_id)
    if not isinstance(approved, dict) or not isinstance(envelope_item, dict):
        return False
    task_kind = packet.get("task_kind")
    expected_scope = [] if task_kind in {"review", "inspect"} else approved["write_scope"]
    expected_task = {
        "summary": approved["title"],
        "acceptance_criteria": approved["acceptance_criteria"],
        "verification": approved["verification"],
        "stop_conditions": approved["non_goals"],
    }
    expected_sources = source_revision_record(
        envelope_path=trusted.envelope_path,
        runtime_path=trusted.runtime_state_path,
        issue_source_path=trusted.issue_source,
    )
    return (
        source_revision == expected_sources
        and packet.get("worktree") == str(trusted.assigned_worktree)
        and packet.get("epic_id") == approved_packet.get("epic_id")
        and envelope.get("epic_id") == approved_packet.get("epic_id")
        and packet.get("issue_title") == approved["title"]
        and packet.get("branch") == envelope_item.get("branch")
        and packet.get("write_scope") == expected_scope
        and packet.get("task") == expected_task
    )


def validate_worker_packet(
    packet: dict[str, Any],
    *,
    repo_root: str | os.PathLike[str],
    assigned_worktree: str | os.PathLike[str],
    envelope_path: str | os.PathLike[str],
    runtime_state_path: str | os.PathLike[str],
) -> list[str]:
    errors: list[str] = []
    schema_version = packet.get("schema_version")
    if schema_version != 3:
        return ["SCHEMA_UNSUPPORTED"]
    _reject_unknown_fields(packet, TOP_LEVEL_FIELDS_V3, "", errors)
    _require_fields(packet, TOP_LEVEL_FIELDS_V3, "", errors)
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
    try:
        trusted_path_root = str(Path(assigned_worktree).resolve(strict=False))
    except (OSError, TypeError):
        return ["BINDING_MISMATCH"]

    task_kind = packet.get("task_kind")
    access_mode = packet.get("access_mode")
    if task_kind not in TASK_KINDS:
        errors.append(f"task_kind must be one of {sorted(TASK_KINDS)}")
    if access_mode not in ACCESS_MODES:
        errors.append(f"access_mode must be one of {sorted(ACCESS_MODES)}")
    binding = _validate_source_revision(packet, errors)

    write_scope = packet.get("write_scope")
    if task_kind in {"review", "inspect"}:
        if write_scope != []:
            errors.append(f"{task_kind} packets require write_scope=[]")
    elif task_kind in {"implement", "fix"}:
        _as_string_list(write_scope, "write_scope", errors)
    else:
        _as_string_list(write_scope, "write_scope", errors)

    if task_kind in {"implement", "fix"}:
        if access_mode != "read_write":
            errors.append(f"{task_kind} packets require access_mode=read_write")
        if not isinstance(write_scope, list) or not write_scope:
            errors.append(f"{task_kind} packets require a non-empty write_scope")
    if task_kind in {"review", "inspect"} and access_mode != "read_only":
        errors.append(f"{task_kind} packets require access_mode=read_only")
    if os.path.isabs(trusted_path_root) and isinstance(write_scope, list):
        for index, scope in enumerate(write_scope):
            if not isinstance(scope, str) or not scope.strip():
                continue
            if not scope.startswith("path:"):
                errors.append(f"write_scope[{index}] must use path:<path>")
                continue
            _validate_packet_path(
                worktree=trusted_path_root,
                raw_path=_write_scope_path(scope),
                field=f"write_scope[{index}]",
                errors=errors,
            )

    context_policy = packet.get("context_policy")
    if not isinstance(context_policy, dict):
        errors.append("context_policy is required")
        context_policy = {}
    else:
        _reject_unknown_fields(context_policy, CONTEXT_POLICY_FIELDS, "context_policy", errors)
        _require_fields(context_policy, CONTEXT_POLICY_FIELDS, "context_policy", errors)
    if context_policy.get("paths_first") is not True:
        errors.append("context_policy.paths_first must be true")
    max_packet_words = context_policy.get("max_packet_words")
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
        elif os.path.isabs(trusted_path_root):
            _validate_packet_path(
                worktree=trusted_path_root,
                raw_path=path,
                field=f"{prefix}.path",
                errors=errors,
            )
        purpose = entry.get("purpose")
        if not isinstance(purpose, str) or not purpose.strip():
            errors.append(f"{prefix}.purpose must be a non-empty string")
        elif purpose is not None and (not isinstance(purpose, str) or not purpose.strip()):
            errors.append(f"{prefix}.purpose must be a non-empty string")

    inline_context = packet.get("inline_context")
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
        elif os.path.isabs(trusted_path_root):
            _validate_packet_path(
                worktree=trusted_path_root,
                raw_path=path,
                field=f"{prefix}.path",
                errors=errors,
            )
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
        if "purpose" in entry and not isinstance(purpose, str):
            errors.append(f"{prefix}.purpose must be a string when provided")
        if "is_full_document" in entry and (
            type(entry.get("is_full_document")) is not bool
            or entry.get("is_full_document") is not False
        ):
            errors.append(f"{prefix}.is_full_document must be false when provided")
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
    if not errors and binding is not None and isinstance(issue_id, str):
        try:
            trusted = trusted_worker_context(
                repo_root=repo_root,
                assigned_worktree=assigned_worktree,
                envelope_path=envelope_path,
                runtime_state_path=runtime_state_path,
                issue_id=issue_id,
            )
        except ValueError as error:
            return [str(error)]
        if not _approved_semantics_match(packet, trusted):
            return ["BINDING_MISMATCH"]
    return errors
