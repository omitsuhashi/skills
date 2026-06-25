from __future__ import annotations

import re
from typing import Any


DEFAULT_PACKET_WORDS = 450
HARD_PACKET_WORDS = 800
MAX_READ_PATHS = 8
MAX_INLINE_EXCERPT_WORDS_PER_FILE = 120
MAX_INLINE_EXCERPT_WORDS_TOTAL = 300
PACKET_CONTEXT_BUDGET_EXCEEDED = "PACKET_CONTEXT_BUDGET_EXCEEDED"

WORD_RE = re.compile(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*|[^\W\s_]+", re.UNICODE)


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


def read_path_record(path: str) -> dict[str, str]:
    return {"path": path, "purpose": "source"}


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
    summary: str,
    acceptance: list[str],
    verification: list[str],
    stop_conditions: list[str],
    inline_excerpts: list[str],
    max_packet_words: int = DEFAULT_PACKET_WORDS,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "packet_type": "issue_worker_dispatch",
        "epic_id": epic_id,
        "issue_id": issue_id,
        "issue_title": issue_title,
        "dispatch_id": dispatch_id,
        "branch": branch,
        "worktree": worktree,
        "write_scope": write_scope,
        "context_policy": worker_packet_context_policy(max_packet_words),
        "read_paths": [read_path_record(path) for path in read_paths],
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
