#!/usr/bin/env python3
"""Deterministic helpers for turning simple capture text into TaskDrafts."""

from __future__ import annotations

import hashlib
import re

from task_backend import TaskDraft


DATE_RE = re.compile(r"\b(20[0-9]{2}-[01][0-9]-[0-3][0-9])\b")
WORK_UNIT_RE = re.compile(
    r"\b(?:work_unit_id|work unit|wu)\s*[:=]\s*([A-Za-z0-9_.-]+)",
    re.IGNORECASE,
)
KEY_VALUE_RE = re.compile(r"\b(urgency|importance|task_type)\s*[:=]\s*([A-Za-z0-9_-]+)", re.IGNORECASE)


def _first_sentence(text: str) -> str:
    compact = " ".join(text.strip().split())
    if not compact:
        raise ValueError("capture text is required")
    first = re.split(r"(?<=[.!?])\s+", compact, maxsplit=1)[0]
    return first[:90].rstrip(" .")


def _extract_key_values(text: str) -> dict[str, str]:
    return {match.group(1).lower(): match.group(2).lower() for match in KEY_VALUE_RE.finditer(text)}


def _idempotency_key(text: str, work_unit_id: str, source_ref: str | None) -> str:
    material = f"{source_ref or ''}\n{work_unit_id}\n{text.strip()}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()[:32]


def normalize_capture_text(
    text: str,
    *,
    default_work_unit_id: str = "inbox",
    source_ref: str | None = None,
) -> TaskDraft:
    values = _extract_key_values(text)
    work_unit_match = WORK_UNIT_RE.search(text)
    date_match = DATE_RE.search(text)
    work_unit_id = work_unit_match.group(1) if work_unit_match else default_work_unit_id
    title = _first_sentence(text)

    return TaskDraft(
        title=title,
        body=text.strip(),
        work_unit_id=work_unit_id,
        task_type=values.get("task_type", "follow_up"),
        due_date=date_match.group(1) if date_match else None,
        urgency=values.get("urgency"),
        importance=values.get("importance"),
        automation_mode="draft_only",
        approval_required=True,
        source_ref=source_ref,
        idempotency_key=_idempotency_key(text, work_unit_id, source_ref),
    )
