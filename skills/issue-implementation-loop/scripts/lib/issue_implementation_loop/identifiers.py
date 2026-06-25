from __future__ import annotations

import re

from .constants import COMMIT_RANGE_RE, EPIC_RE, FULL_SHA_RE, ISSUE_RE


def is_lower_kebab(value: str) -> bool:
    return bool(EPIC_RE.fullmatch(value))


def is_issue_id(value: str) -> bool:
    return bool(ISSUE_RE.fullmatch(value))


def is_full_commit_sha(value: str) -> bool:
    return bool(FULL_SHA_RE.fullmatch(value)) and set(value.lower()) != {"0"}


def is_commit_range(value: str) -> bool:
    if not COMMIT_RANGE_RE.fullmatch(value):
        return False
    base, head = value.split("..", 1)
    return is_full_commit_sha(base) and is_full_commit_sha(head)


def commit_range_parts(value: str) -> tuple[str, str] | None:
    if not is_commit_range(value):
        return None
    base, head = value.split("..", 1)
    return base, head


def canonical_issue_branch(epic_id: str, issue_id: str) -> str:
    return f"codex/{epic_id}/{issue_id}-<slug>"


def is_canonical_issue_branch(branch: str, epic_id: str, issue_id: str) -> bool:
    pattern = re.compile(
        rf"^codex/{re.escape(epic_id)}/{re.escape(issue_id)}-[a-z0-9]+(?:-[a-z0-9]+)*$"
    )
    return bool(pattern.fullmatch(branch))
