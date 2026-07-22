"""Normalize GitHub Projects item responses into safe adapter-v2 snapshots."""

from __future__ import annotations

from datetime import date
import re
from typing import Any, Dict, Mapping
from urllib.parse import urlparse

from .config import FieldMapping
from .safety import SafetyValidationError, validate_safe_url, validate_safe_value


class NormalizationError(ValueError):
    """Provider item could not be represented by the safe wire contract."""


_LINKED_ISSUE_REF_RE = re.compile(
    r"^github-issue:([A-Za-z0-9][A-Za-z0-9._-]{0,99})/"
    r"([A-Za-z0-9][A-Za-z0-9._-]{0,99})#([1-9][0-9]*)$"
)


def _mapped_value(
    values: Mapping[str, Any],
    mapping: FieldMapping,
) -> Any:
    if mapping.field_name not in values:
        if mapping.required:
            raise NormalizationError("A required task field is unavailable.")
        return None
    value = values[mapping.field_name]
    if value is None and mapping.field_type == "date":
        return None
    if value is None:
        raise NormalizationError("A task field has an invalid value.")
    if mapping.field_type in {"text", "date"}:
        if not isinstance(value, str) or not value:
            raise NormalizationError("A task field has an invalid value.")
        if mapping.field_type == "date":
            try:
                if date.fromisoformat(value).isoformat() != value:
                    raise ValueError("non-canonical date")
            except ValueError:
                raise NormalizationError("A task date field is invalid.")
        return value
    if not isinstance(value, str):
        raise NormalizationError("A task option field is invalid.")
    canonical = {
        provider_label: canonical_value
        for canonical_value, provider_label in mapping.options.items()
    }.get(value)
    if canonical is None:
        raise NormalizationError("A task option field is unmapped.")
    return canonical


def _provider_values(value: Any) -> Dict[str, Any]:
    if not isinstance(value, list):
        raise NormalizationError("GitHub Project item fields are invalid.")
    result = {}
    for field in value:
        if not isinstance(field, dict):
            raise NormalizationError("GitHub Project item field is invalid.")
        name = field.get("name")
        if not isinstance(name, str) or not name or name in result:
            raise NormalizationError("GitHub Project item field name is invalid.")
        provider_value = field.get("value")
        if isinstance(provider_value, dict):
            provider_value = provider_value.get("name")
        result[name] = provider_value
    return result


def normalize_project_item(
    value: Any,
    *,
    backend_key: str,
    field_mappings: Mapping[str, FieldMapping],
) -> Dict[str, Any]:
    """Discard provider IDs and return one backend-neutral snapshot candidate."""
    if not isinstance(value, dict):
        raise NormalizationError("A GitHub Project item is invalid.")
    content = value.get("content")
    if not isinstance(content, dict):
        raise NormalizationError("A GitHub Project item is incomplete.")
    if value.get("content_type") != "Issue":
        raise NormalizationError("Only linked GitHub Issues are supported.")
    field_values = _provider_values(value.get("fields"))
    number = content.get("number")
    title = content.get("title")
    task_url = content.get("html_url")
    if (
        type(number) is not int
        or number <= 0
        or not isinstance(title, str)
        or not title
    ):
        raise NormalizationError("GitHub Issue content is invalid.")
    try:
        validate_safe_url(task_url, path="$.task_url")
        parsed_url = urlparse(task_url)
    except SafetyValidationError:
        raise NormalizationError("GitHub Issue URL is unsafe.")
    path_parts = [part for part in parsed_url.path.split("/") if part]
    if (
        len(path_parts) != 4
        or path_parts[2] != "issues"
        or path_parts[3] != str(number)
        or content.get("repository") != f"{path_parts[0]}/{path_parts[1]}"
    ):
        raise NormalizationError("GitHub Issue URL does not identify the item.")

    mapped = {
        key: _mapped_value(field_values, mapping)
        for key, mapping in field_mappings.items()
    }
    status = field_values.get("Status")
    if not isinstance(status, str) or not status:
        raise NormalizationError("Task status is unavailable.")
    approval_value = mapped["approval_required"]
    if approval_value not in {"true", "false"}:
        raise NormalizationError("Task approval mapping is invalid.")

    opaque_ref = (
        f"github-issue:{path_parts[0]}/{path_parts[1]}#{path_parts[3]}"
    )
    source_url = mapped.get("source_url")
    source_label = mapped.get("source_label")
    if source_url is not None:
        try:
            validate_safe_url(source_url, path="$.source_ref.ref")
        except SafetyValidationError:
            raise NormalizationError("Task source URL is unsafe.")
    source_ref = {
        "kind": "source" if source_url is not None else "task_backend",
        "ref": source_url or opaque_ref,
        "label": source_label or "GitHub Issue",
    }
    snapshot = {
        "task_ref": {
            "backend_key": backend_key,
            "task_ref": opaque_ref,
            "task_url": task_url,
            "title": title,
        },
        "title": title,
        "body": "",
        "work_unit_id": mapped["work_unit_id"],
        "work_unit_name": mapped["work_unit_name"],
        "task_type": mapped["task_type"],
        "status": status,
        "due_date": mapped["due_date"],
        "urgency": mapped["urgency"],
        "importance": mapped["importance"],
        "automation_mode": mapped["automation_mode"],
        "approval_required": approval_value == "true",
        "source_ref": source_ref,
        "backend_metadata": {
            "display_link": {"name": "Open GitHub Issue", "url": task_url}
        },
    }
    try:
        validate_safe_value(snapshot)
    except SafetyValidationError:
        raise NormalizationError("Normalized task data is unsafe.")
    return snapshot


def _normalize_linked_issue_task_ref(
    value: Any,
    *,
    backend_key: str,
    owner: str,
    repository: str,
    expected_number: Any = None,
) -> Dict[str, Any]:
    """Extract only the safe public identity of one configured linked Issue."""
    if not isinstance(value, dict):
        raise NormalizationError("GitHub Issue content is invalid.")
    number = value.get("number")
    title = value.get("title")
    task_url = value.get("html_url")
    if (
        type(number) is not int
        or number <= 0
        or (expected_number is not None and number != expected_number)
        or not isinstance(title, str)
        or not title
    ):
        raise NormalizationError("GitHub Issue content is invalid.")
    try:
        validate_safe_url(task_url, path="$.task_url")
        parsed_url = urlparse(task_url)
    except SafetyValidationError:
        raise NormalizationError("GitHub Issue URL is unsafe.")
    expected_path = f"/{owner}/{repository}/issues/{number}"
    if parsed_url.netloc.casefold() != "github.com" or parsed_url.path != expected_path:
        raise NormalizationError("GitHub Issue URL does not identify the item.")
    task_ref = {
        "backend_key": backend_key,
        "task_ref": f"github-issue:{owner}/{repository}#{number}",
        "task_url": task_url,
        "title": title,
    }
    try:
        validate_safe_value(task_ref)
    except SafetyValidationError:
        raise NormalizationError("GitHub Issue identity is unsafe.")
    return task_ref


def _parse_linked_issue_task_ref(value: Any, *, backend_key: str) -> Dict[str, Any]:
    """Validate an adapter-owned public task reference and recover safe coordinates."""
    if not isinstance(value, dict) or set(value) != {
        "backend_key",
        "task_ref",
        "task_url",
        "title",
    }:
        raise NormalizationError("GitHub Issue task reference is invalid.")
    match = (
        _LINKED_ISSUE_REF_RE.fullmatch(value.get("task_ref", ""))
        if isinstance(value.get("task_ref"), str)
        else None
    )
    if match is None or value.get("backend_key") != backend_key:
        raise NormalizationError("GitHub Issue task reference is invalid.")
    owner, repository, raw_number = match.groups()
    number = int(raw_number)
    normalized = _normalize_linked_issue_task_ref(
        {
            "number": number,
            "title": value.get("title"),
            "html_url": value.get("task_url"),
        },
        backend_key=backend_key,
        owner=owner,
        repository=repository,
        expected_number=number,
    )
    if normalized != value:
        raise NormalizationError("GitHub Issue task reference is inconsistent.")
    return {
        "owner": owner,
        "repository": repository,
        "number": number,
        "task_ref": normalized,
    }


def matches_query(snapshot: Mapping[str, Any], query: Mapping[str, Any]) -> bool:
    """Apply canonical filters after provider payload normalization."""
    for field in ("work_unit_id", "task_type", "status"):
        if field in query and snapshot.get(field) != query[field]:
            return False
    due_before = query.get("due_before")
    if due_before is not None:
        due_date = snapshot.get("due_date")
        if not isinstance(due_date, str) or due_date > due_before:
            return False
    return True
