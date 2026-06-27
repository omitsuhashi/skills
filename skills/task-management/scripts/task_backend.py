#!/usr/bin/env python3
"""Backend-neutral task contract objects for task-management workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Mapping, Protocol, Sequence


TASK_FIELD_NAMES = frozenset(
    {
        "title",
        "body",
        "work_unit_id",
        "task_type",
        "due_date",
        "status",
        "urgency",
        "importance",
        "automation_mode",
        "approval_required",
        "source_ref",
        "assignee",
    }
)

PROVIDER_SPECIFIC_MARKERS = (
    "graphql",
    "project_field",
    "projectfield",
    "status_option",
    "statusoption",
    "repository_id",
    "repositoryid",
    "auth",
    "token",
    "raw_payload",
    "message_id",
)


def _compact(value: object) -> object:
    if isinstance(value, dict):
        return {key: _compact(item) for key, item in value.items() if item not in (None, {}, [])}
    if isinstance(value, list):
        return [_compact(item) for item in value]
    return value


def validate_backend_neutral_fields(fields: Mapping[str, object]) -> None:
    invalid = sorted(set(fields) - TASK_FIELD_NAMES)
    provider_leaks = [
        field
        for field in fields
        if any(marker in field.lower() for marker in PROVIDER_SPECIFIC_MARKERS)
    ]
    if invalid or provider_leaks:
        details = ", ".join(sorted(set(invalid + provider_leaks)))
        raise ValueError(f"non-neutral task field(s): {details}")


def _provider_specific_keys(value: Mapping[str, object], prefix: str = "") -> list[str]:
    leaks: list[str] = []
    for key, item in value.items():
        path = f"{prefix}.{key}" if prefix else key
        if any(marker in key.lower() for marker in PROVIDER_SPECIFIC_MARKERS):
            leaks.append(path)
        if isinstance(item, Mapping):
            leaks.extend(_provider_specific_keys(item, path))
    return leaks


@dataclass(frozen=True)
class TaskDraft:
    title: str
    body: str
    work_unit_id: str
    task_type: str = "follow_up"
    due_date: str | None = None
    urgency: str | None = None
    importance: str | None = None
    automation_mode: str = "draft_only"
    approval_required: bool = True
    source_ref: str | None = None
    assignee: str | None = None
    idempotency_key: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title is required")
        if not self.work_unit_id.strip():
            raise ValueError("work_unit_id is required")
        metadata_leaks = _provider_specific_keys(self.metadata)
        if metadata_leaks:
            raise ValueError(f"provider-specific metadata key(s): {', '.join(metadata_leaks)}")

    def to_public_dict(self) -> dict[str, object]:
        return _compact(asdict(self))  # type: ignore[return-value]


@dataclass(frozen=True)
class TaskRef:
    backend: str
    id: str
    url: str

    def to_public_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TaskQuery:
    work_unit_id: str | None = None
    due_date: str | None = None
    status: str | None = None
    urgency: str | None = None
    importance: str | None = None
    automation_mode: str | None = None
    assignee: str | None = None

    def as_filters(self) -> dict[str, str]:
        return {
            key: value
            for key, value in asdict(self).items()
            if isinstance(value, str) and value
        }


@dataclass
class TaskSnapshot:
    task_ref: TaskRef
    title: str
    body: str
    fields: dict[str, object]
    comments: list[str] = field(default_factory=list)
    backend_metadata: Mapping[str, object] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, object]:
        return _compact(
            {
                "task_ref": self.task_ref.to_public_dict(),
                "title": self.title,
                "body": self.body,
                "fields": dict(self.fields),
                "comments": list(self.comments),
                "backend_metadata": dict(self.backend_metadata),
            }
        )  # type: ignore[return-value]


@dataclass(frozen=True)
class TaskWriteResult:
    task_ref: TaskRef
    operation: str
    created: bool = False
    updated: bool = False
    changed_fields: Sequence[str] = field(default_factory=tuple)
    message: str | None = None
    backend_metadata: Mapping[str, object] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, object]:
        return _compact(
            {
                "task_ref": self.task_ref.to_public_dict(),
                "operation": self.operation,
                "created": self.created,
                "updated": self.updated,
                "changed_fields": list(self.changed_fields),
                "message": self.message,
                "backend_metadata": dict(self.backend_metadata),
            }
        )  # type: ignore[return-value]


class TaskBackendAdapter(Protocol):
    backend: str

    def create_task(self, draft: TaskDraft) -> TaskWriteResult:
        raise NotImplementedError

    def read_task(self, task_ref: TaskRef) -> TaskSnapshot:
        raise NotImplementedError

    def query_tasks(self, query: TaskQuery) -> list[TaskSnapshot]:
        raise NotImplementedError

    def update_fields(self, task_ref: TaskRef, fields: Mapping[str, object]) -> TaskWriteResult:
        raise NotImplementedError

    def add_progress_comment(self, task_ref: TaskRef, body: str) -> TaskWriteResult:
        raise NotImplementedError
