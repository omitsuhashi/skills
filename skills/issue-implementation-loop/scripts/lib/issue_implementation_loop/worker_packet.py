from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_PACKET_WORDS = 450
HARD_PACKET_WORDS = 800
MAX_READ_PATHS = 8
MAX_INLINE_EXCERPT_WORDS_PER_FILE = 120
MAX_INLINE_EXCERPT_WORDS_TOTAL = 300
PACKET_CONTEXT_BUDGET_EXCEEDED = "PACKET_CONTEXT_BUDGET_EXCEEDED"

WORD_RE = re.compile(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*|[^\W\s_]+", re.UNICODE)
TASK_KINDS = {"implement", "fix", "review", "inspect"}
ACCESS_MODES = {"read_write", "read_only"}


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def packet_word_count(value: Any) -> int:
    if isinstance(value, str):
        return count_words(value)
    if isinstance(value, list):
        return sum(packet_word_count(item) for item in value)
    if isinstance(value, dict):
        return sum(packet_word_count(item) for item in value.values())
    return 0


def worker_packet_context_policy(max_packet_words: int = DEFAULT_PACKET_WORDS) -> dict[str, Any]:
    return {
        "paths_first": True,
        "max_packet_words": max_packet_words,
        "hard_max_packet_words": HARD_PACKET_WORDS,
        "max_read_paths": MAX_READ_PATHS,
        "max_inline_excerpt_words_per_file": MAX_INLINE_EXCERPT_WORDS_PER_FILE,
        "max_inline_excerpt_words_total": MAX_INLINE_EXCERPT_WORDS_TOTAL,
        "include_full_spec_text": False,
        "include_full_ledger_text": False,
    }


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def source_revision_record(
    *,
    envelope_path: str | Path,
    runtime_path: str | Path,
    issue_source_path: str | Path,
) -> dict[str, Any]:
    envelope_file = Path(envelope_path).resolve(strict=False)
    runtime_file = Path(runtime_path).resolve(strict=False)
    issue_source_file = Path(issue_source_path).resolve(strict=False)
    envelope = _load_json(envelope_file)
    runtime = _load_json(runtime_file)
    return {
        "execution_envelope": {
            "path": str(envelope_file),
            "revision": envelope.get("revision"),
            "sha256": file_sha256(envelope_file),
        },
        "runtime_state": {
            "path": str(runtime_file),
            "envelope_revision": runtime.get("envelope_revision"),
            "sha256": file_sha256(runtime_file),
        },
        "issue_source": {
            "path": str(issue_source_file),
            "sha256": file_sha256(issue_source_file),
        },
    }


def read_path_record(path: str, purpose: str = "source") -> dict[str, str]:
    return {"path": path, "purpose": purpose}


def inline_excerpt_record(raw: str) -> dict[str, str]:
    path, separator, excerpt = raw.partition("::")
    if not separator or not path.strip() or not excerpt.strip():
        raise ValueError("inline excerpt must use PATH::EXCERPT")
    return {"path": path.strip(), "excerpt": excerpt.strip()}


def build_worker_packet(
    *,
    epic_id: str,
    issue_id: str,
    issue_title: str,
    dispatch_id: str,
    branch: str,
    worktree: str,
    write_scope: list[str],
    read_paths: list[str],
    read_purposes: list[str] | None = None,
    summary: str,
    acceptance: list[str],
    verification: list[str],
    stop_conditions: list[str],
    inline_excerpts: list[str],
    max_packet_words: int = DEFAULT_PACKET_WORDS,
    schema_version: int = 2,
    task_kind: str = "implement",
    access_mode: str = "read_write",
    source_envelope: str | None = None,
    source_runtime: str | None = None,
    source_issue: str | None = None,
) -> dict[str, Any]:
    if schema_version not in {1, 2}:
        raise ValueError("schema_version must be 1 or 2")
    if read_purposes is None:
        read_purposes = ["source"] * len(read_paths)
    if len(read_purposes) != len(read_paths):
        raise ValueError("--read-purpose must be provided once per --read-path")

    packet: dict[str, Any] = {
        "schema_version": schema_version,
        "packet_type": "issue_worker_dispatch",
        "epic_id": epic_id,
        "issue_id": issue_id,
        "issue_title": issue_title,
        "dispatch_id": dispatch_id,
        "branch": branch,
        "worktree": worktree,
        "write_scope": write_scope,
        "context_policy": worker_packet_context_policy(max_packet_words),
        "read_paths": [
            read_path_record(path, purpose)
            for path, purpose in zip(read_paths, read_purposes)
        ],
        "inline_context": [inline_excerpt_record(excerpt) for excerpt in inline_excerpts],
        "task": {
            "summary": summary,
            "acceptance_criteria": acceptance,
            "verification": verification,
            "stop_conditions": stop_conditions,
        },
        "report_contract": {
            "format": "worker-report.json",
            "validator": "skills/issue-implementation-loop/scripts/validate_worker_report.py",
        },
    }
    if schema_version == 1:
        return packet

    if task_kind not in TASK_KINDS:
        raise ValueError(f"task_kind must be one of {sorted(TASK_KINDS)}")
    if access_mode not in ACCESS_MODES:
        raise ValueError(f"access_mode must be one of {sorted(ACCESS_MODES)}")
    if not source_envelope or not source_runtime or not source_issue:
        raise ValueError(
            "schema version 2 requires --source-envelope, --source-runtime, and --source-issue"
        )
    packet["task_kind"] = task_kind
    packet["access_mode"] = access_mode
    packet["source_revision"] = source_revision_record(
        envelope_path=source_envelope,
        runtime_path=source_runtime,
        issue_source_path=source_issue,
    )
    return packet
