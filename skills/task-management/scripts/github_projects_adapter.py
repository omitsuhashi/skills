#!/usr/bin/env python3
"""GitHub Projects adapter shapes and dry-run fixture implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from task_backend import (
    TASK_FIELD_NAMES,
    TaskDraft,
    TaskQuery,
    TaskRef,
    TaskSnapshot,
    TaskWriteResult,
    validate_backend_neutral_fields,
)


DEFAULT_FIELD_MAPPING = {
    "work_unit_id": "Work Unit",
    "task_type": "Task Type",
    "due_date": "Due Date",
    "status": "Status",
    "urgency": "Urgency",
    "importance": "Importance",
    "automation_mode": "Automation Mode",
    "approval_required": "Approval Required",
    "source_ref": "Source Ref",
    "assignee": "Assignee",
}


@dataclass(frozen=True)
class GitHubProjectsConfig:
    owner: str
    project_number: int
    repository: str | None = None
    default_work_unit_id: str = "inbox"
    field_mapping: Mapping[str, str] = field(default_factory=lambda: dict(DEFAULT_FIELD_MAPPING))

    def __post_init__(self) -> None:
        if not self.owner:
            raise ValueError("owner is required")
        if self.project_number <= 0:
            raise ValueError("project_number must be positive")
        invalid = sorted(set(self.field_mapping) - TASK_FIELD_NAMES)
        if invalid:
            raise ValueError(f"unknown field mapping key(s): {', '.join(invalid)}")


class InMemoryGitHubProjectsAdapter:
    """Dry-run GitHub Projects adapter for tests, design, and fixture-backed demos."""

    backend = "github-projects"

    def __init__(self, config: GitHubProjectsConfig) -> None:
        self.config = config
        self._items: dict[str, TaskSnapshot] = {}
        self._idempotency_index: dict[str, str] = {}
        self._next_number = 1

    def create_task(self, draft: TaskDraft) -> TaskWriteResult:
        key = draft.idempotency_key
        if key and key in self._idempotency_index:
            task_id = self._idempotency_index[key]
            return TaskWriteResult(
                task_ref=self._items[task_id].task_ref,
                operation="create",
                created=False,
                message="duplicate idempotency key; returned existing task",
            )

        task_id = f"ghp-task-{self._next_number}"
        self._next_number += 1
        task_ref = TaskRef(backend=self.backend, id=task_id, url=self._task_url(task_id))
        fields = {
            "work_unit_id": draft.work_unit_id or self.config.default_work_unit_id,
            "task_type": draft.task_type,
            "due_date": draft.due_date,
            "status": "todo",
            "urgency": draft.urgency,
            "importance": draft.importance,
            "automation_mode": draft.automation_mode,
            "approval_required": draft.approval_required,
            "source_ref": draft.source_ref,
            "assignee": draft.assignee,
        }
        snapshot = TaskSnapshot(
            task_ref=task_ref,
            title=draft.title,
            body=draft.body,
            fields={key: value for key, value in fields.items() if value is not None},
            backend_metadata=self._safe_metadata(),
        )
        self._items[task_id] = snapshot
        if key:
            self._idempotency_index[key] = task_id
        return TaskWriteResult(task_ref=task_ref, operation="create", created=True)

    def read_task(self, task_ref: TaskRef) -> TaskSnapshot:
        return self._copy_snapshot(self._stored_snapshot(task_ref))

    def query_tasks(self, query: TaskQuery) -> list[TaskSnapshot]:
        filters = query.as_filters()
        return [
            self._copy_snapshot(snapshot)
            for snapshot in self._items.values()
            if all(snapshot.fields.get(field) == value for field, value in filters.items())
        ]

    def update_fields(self, task_ref: TaskRef, fields: Mapping[str, object]) -> TaskWriteResult:
        validate_backend_neutral_fields(fields)
        snapshot = self._stored_snapshot(task_ref)
        changed: list[str] = []
        for field_name, value in fields.items():
            if snapshot.fields.get(field_name) != value:
                snapshot.fields[field_name] = value
                changed.append(field_name)
        return TaskWriteResult(
            task_ref=snapshot.task_ref,
            operation="update",
            updated=bool(changed),
            changed_fields=tuple(changed),
        )

    def add_progress_comment(self, task_ref: TaskRef, body: str) -> TaskWriteResult:
        if not body.strip():
            raise ValueError("comment body is required")
        snapshot = self._stored_snapshot(task_ref)
        snapshot.comments.append(body.strip())
        return TaskWriteResult(
            task_ref=snapshot.task_ref,
            operation="comment",
            updated=True,
            message="comment added",
        )

    def _stored_snapshot(self, task_ref: TaskRef) -> TaskSnapshot:
        if task_ref.backend != self.backend:
            raise ValueError(f"wrong backend: {task_ref.backend}")
        try:
            return self._items[task_ref.id]
        except KeyError as exc:
            raise KeyError(f"unknown task ref: {task_ref.id}") from exc

    def _copy_snapshot(self, snapshot: TaskSnapshot) -> TaskSnapshot:
        return TaskSnapshot(
            task_ref=snapshot.task_ref,
            title=snapshot.title,
            body=snapshot.body,
            fields=dict(snapshot.fields),
            comments=list(snapshot.comments),
            backend_metadata=dict(snapshot.backend_metadata),
        )

    def _task_url(self, task_id: str) -> str:
        if self.config.repository:
            return f"https://github.com/{self.config.repository}/projects/{self.config.project_number}?task={task_id}"
        return f"https://github.com/orgs/{self.config.owner}/projects/{self.config.project_number}?task={task_id}"

    def _safe_metadata(self) -> dict[str, object]:
        return {
            "owner": self.config.owner,
            "project_number": self.config.project_number,
            "repository": self.config.repository,
            "field_mapping": dict(self.config.field_mapping),
        }
