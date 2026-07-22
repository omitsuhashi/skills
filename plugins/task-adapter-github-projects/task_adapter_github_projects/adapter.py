"""Executable GitHub Projects adapter through an injected public dispatch seam."""

from __future__ import annotations

import json
import re
from datetime import date
from typing import Any, Callable, Dict, Mapping

from .config import ConfigError, GithubProjectsConfig
from .contracts import (
    ADAPTER_CONTRACT_VERSION,
    validate_operation_envelope,
    validate_task_write_result,
)
from .normalization import (
    NormalizationError,
    matches_query,
    _normalize_linked_issue_task_ref,
    normalize_project_item,
    _parse_linked_issue_task_ref,
)
from .safety import (
    SafetyValidationError,
    validate_adapter_arguments,
    validate_host_attestation,
)


_PROVIDER_FIELD_TYPES = {
    "text": "text",
    "date": "date",
    "single_select": "single_select",
}
_MAX_PROVIDER_PAGES = 10
_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_FIELD_WRITE_ORDER = (
    "work_unit_id",
    "work_unit_name",
    "task_type",
    "due_date",
    "urgency",
    "importance",
    "automation_mode",
    "approval_required",
    "source_label",
    "source_url",
)
_PUBLIC_ERROR_PATTERNS = (
    (("rate limit", "rate_limited"), "rate_limited"),
    (
        (
            "tool_disabled",
            "tool disabled",
            "method_not_found",
            "method not found",
            "not connected",
            "unknown tool",
        ),
        "tool_disabled",
    ),
    (
        (
            "unauthorized",
            "unauthenticated",
            "authentication required",
            "auth_missing",
        ),
        "auth_missing",
    ),
    (("forbidden", "permission_denied", "permission denied"), "permission_failure"),
    (("not_found", "not found"), "destination_unresolved"),
)
_EXPECTED_SIDE_EFFECTS = {
    "task.create": [
        {
            "effect_type": "content.create",
            "description": "Create a linked GitHub Issue.",
        },
        {
            "effect_type": "destination.attach",
            "description": "Add the linked task to the configured GitHub Project.",
        },
        {
            "effect_type": "fields.update",
            "description": "Update the reviewed task fields.",
        },
        {
            "effect_type": "task.read_back",
            "description": "Read the resulting task state.",
        },
    ],
    "task.update": [
        {
            "effect_type": "content.update",
            "description": "Update the linked GitHub Issue content.",
        },
        {
            "effect_type": "fields.update",
            "description": "Update the reviewed task fields.",
        },
        {
            "effect_type": "task.read_back",
            "description": "Read the resulting task state.",
        },
    ],
    "task.comment": [
        {
            "effect_type": "comment.create",
            "description": "Add a comment to the linked GitHub Issue.",
        },
        {
            "effect_type": "task.read_back",
            "description": "Read the resulting task state.",
        },
    ],
    "task.report": [
        {
            "effect_type": "report.create",
            "description": "Add a structured report to the linked GitHub Issue.",
        },
        {
            "effect_type": "task.read_back",
            "description": "Read the resulting task state.",
        },
    ],
}


class _AdapterBlocker(Exception):
    def __init__(self, code: str, stage: str, *, retryable: bool = False):
        super().__init__(code)
        self.code = code
        self.stage = stage
        self.retryable = retryable


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON object contains a duplicate key.")
        result[key] = value
    return result


def _reject_non_json_constant(_value):
    raise ValueError("JSON contains a non-standard numeric constant.")


class GithubProjectsAdapter:
    """Own provider-specific mapping while accepting only injected dispatch."""

    def __init__(
        self,
        *,
        config: GithubProjectsConfig,
        dispatch: Callable[[str, Mapping[str, Any]], Any],
    ):
        self._config = config
        self._dispatch = dispatch

    def preflight(self, request: Any) -> Dict[str, Any]:
        validate_adapter_arguments(request)
        if not isinstance(request, dict) or set(request) != {
            "adapter_contract_version",
            "operation",
            "destination_label",
            "content_target_ref",
            "required_capability",
        }:
            raise ValueError("Adapter preflight request is invalid.")
        if request["adapter_contract_version"] != ADAPTER_CONTRACT_VERSION:
            raise ValueError("Adapter contract version is unsupported.")
        operation = validate_operation_envelope(request["operation"])
        try:
            validate_host_attestation(self._config.host_attestation)
            if request["required_capability"] != operation["operation_type"]:
                raise _AdapterBlocker("capability_mismatch", "capability_check")

            destination = self._config.resolve_destination(
                operation["destination_ref"]
            )
            if operation["operation_type"] == "task.create":
                self._config.resolve_content_target(request["content_target_ref"])

            projects_get = self._config.mcp_tools["projects_get"]
            projects_list = self._config.mcp_tools["projects_list"]
            project = self._call_provider(
                projects_get,
                {
                    "method": "get_project",
                    "owner": destination.owner,
                    "project_number": destination.project_number,
                },
                stage="project_lookup",
            )
            self._validate_project_identity(project, destination)
            raw_fields = self._list_project_fields(
                projects_list,
                owner=destination.owner,
                project_number=destination.project_number,
            )
            self._validate_project_fields(raw_fields)
            self._call_provider(
                projects_list,
                {
                    "method": "list_project_items",
                    "owner": destination.owner,
                    "project_number": destination.project_number,
                    "per_page": 1,
                },
                stage="item_read_probe",
            )
        except SafetyValidationError:
            return self._blocked_result(
                operation,
                "unsafe_delegation_exposure",
                "host_attestation",
            )
        except ConfigError as error:
            code = (
                error.code
                if error.code == "destination_unresolved"
                else "adapter_unavailable"
            )
            return self._blocked_result(operation, code, "destination_lookup")
        except _AdapterBlocker as error:
            return self._blocked_result(operation, error.code, error.stage)
        except ValueError:
            return self._blocked_result(
                operation,
                "adapter_unavailable",
                "provider_pagination",
            )

        requires_human_confirmation = self._requires_human_confirmation(operation)
        return {
            "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
            "ok": True,
            "status": "ready",
            "operation_type": operation["operation_type"],
            "backend_key": operation["backend_key"],
            "destination_ref": operation["destination_ref"],
            "readiness": {
                "ok": True,
                "checks": [
                    "host_attestation",
                    "destination",
                    "project_read",
                    "field_mapping",
                    "item_read",
                ],
            },
            "expected_side_effects": list(
                _EXPECTED_SIDE_EFFECTS[operation["operation_type"]]
            ),
            "requires_human_confirmation": requires_human_confirmation,
            "error": None,
        }

    def query(self, request: Any) -> Dict[str, Any]:
        validate_adapter_arguments(request)
        if not isinstance(request, dict) or set(request) != {
            "adapter_contract_version",
            "backend_key",
            "destination_ref",
            "query",
        }:
            raise ValueError("Adapter query request is invalid.")
        if request["adapter_contract_version"] != ADAPTER_CONTRACT_VERSION:
            raise ValueError("Adapter contract version is unsupported.")
        backend_key = request["backend_key"]
        query = request["query"]
        if (
            not isinstance(backend_key, str)
            or not backend_key
            or not isinstance(request["destination_ref"], str)
            or not request["destination_ref"]
            or not self._query_is_valid(query)
        ):
            return self._query_failure("invalid_query")
        try:
            return self._execute_query(request, backend_key, query)
        except ConfigError as error:
            code = (
                error.code
                if error.code == "destination_unresolved"
                else "adapter_unavailable"
            )
            return self._query_failure(code)
        except SafetyValidationError:
            return self._query_failure("unsafe_delegation_exposure")
        except _AdapterBlocker as error:
            return self._query_failure(error.code)
        except (NormalizationError, ValueError):
            return self._query_failure("adapter_unavailable")

    def apply(self, request: Any) -> Dict[str, Any]:
        """Execute one already-approved operation through configured public tools."""
        validate_adapter_arguments(request)
        if not isinstance(request, dict) or set(request) != {
            "adapter_contract_version",
            "operation",
            "destination_label",
            "content_target_ref",
            "operation_digest",
        }:
            raise ValueError("Adapter apply request is invalid.")
        if request["adapter_contract_version"] != ADAPTER_CONTRACT_VERSION:
            raise ValueError("Adapter contract version is unsupported.")
        if (
            not isinstance(request["destination_label"], str)
            or not request["destination_label"].strip()
            or not isinstance(request["operation_digest"], str)
            or _DIGEST_RE.fullmatch(request["operation_digest"]) is None
        ):
            raise ValueError("Adapter apply request is invalid.")
        operation = validate_operation_envelope(request["operation"])
        try:
            validate_host_attestation(self._config.host_attestation)
            destination = self._config.resolve_destination(
                operation["destination_ref"]
            )
        except SafetyValidationError:
            return self._write_failure(
                operation,
                code="unsafe_delegation_exposure",
                stage="host_attestation",
                status="blocked",
                error_type="setup_blocker",
            )
        except ConfigError:
            return self._write_failure(
                operation,
                code="destination_unresolved",
                stage="destination_lookup",
                status="blocked",
                error_type="setup_blocker",
            )

        if operation["operation_type"] == "task.create":
            try:
                content_target = self._config.resolve_content_target(
                    request["content_target_ref"]
                )
            except ConfigError:
                return self._write_failure(
                    operation,
                    code="destination_unresolved",
                    stage="content_target_lookup",
                    status="blocked",
                    error_type="setup_blocker",
                )
            return self._apply_create(operation, destination, content_target)
        try:
            linked_issue = _parse_linked_issue_task_ref(
                operation["task_ref"],
                backend_key=operation["backend_key"],
            )
            self._require_configured_content_target(linked_issue)
        except (NormalizationError, ConfigError):
            return self._write_failure(
                operation,
                code="destination_unresolved",
                stage="task_reference",
                status="blocked",
                error_type="setup_blocker",
            )
        if operation["operation_type"] == "task.update":
            return self._apply_update(operation, destination, linked_issue)
        if operation["operation_type"] == "task.comment":
            return self._apply_issue_comment(
                operation,
                destination,
                linked_issue,
                body=operation["payload"]["comment"]["body"],
                status="commented",
                stage="comment_create",
            )
        if operation["operation_type"] == "task.report":
            return self._apply_issue_comment(
                operation,
                destination,
                linked_issue,
                body=self._render_report(operation["payload"]["report"]),
                status="reported",
                stage="report_create",
            )
        return self._write_failure(
            operation,
            code="capability_mismatch",
            stage="operation_dispatch",
            status="blocked",
            error_type="setup_blocker",
        )

    def _apply_create(self, operation, destination, content_target):
        task = operation["payload"]["task"]
        try:
            issue = self._call_provider(
                self._config.mcp_tools["issue_write"],
                {
                    "method": "create",
                    "owner": content_target.owner,
                    "repo": content_target.repository,
                    "title": task["title"],
                    "body": task["body"],
                },
                stage="issue_create",
            )
            task_ref = _normalize_linked_issue_task_ref(
                issue,
                backend_key=operation["backend_key"],
                owner=content_target.owner,
                repository=content_target.repository,
            )
        except (_AdapterBlocker, NormalizationError) as error:
            code = error.code if isinstance(error, _AdapterBlocker) else "adapter_unavailable"
            return self._write_failure(
                operation,
                code=code,
                stage="issue_create",
                status="failed",
                error_type="provider_failure",
                retryable=(
                    error.retryable if isinstance(error, _AdapterBlocker) else False
                ),
            )

        issue_number = issue["number"]
        try:
            added = self._call_provider(
                self._config.mcp_tools["projects_write"],
                {
                    "method": "add_project_item",
                    "owner": destination.owner,
                    "project_number": destination.project_number,
                    "item_type": "issue",
                    "item_owner": content_target.owner,
                    "item_repo": content_target.repository,
                    "issue_number": issue_number,
                },
                stage="project_item_add",
            )
            item_id = added.get("item_id")
            if type(item_id) is not int or item_id <= 0:
                raise NormalizationError("GitHub Project item identity is invalid.")
        except (_AdapterBlocker, NormalizationError) as error:
            code = error.code if isinstance(error, _AdapterBlocker) else "adapter_unavailable"
            return self._write_failure(
                operation,
                code=code,
                stage="project_item_add",
                status="partial",
                error_type="partial_failure",
                task_ref=task_ref,
            )

        field_names = []
        try:
            for canonical_key, value in self._field_write_values(task):
                mapping = self._config.field_mappings[canonical_key]
                field_names.append(mapping.field_name)
                self._call_provider(
                    self._config.mcp_tools["projects_write"],
                    {
                        "method": "update_project_item",
                        "owner": destination.owner,
                        "project_number": destination.project_number,
                        "item_id": item_id,
                        "updated_field": {
                            "name": mapping.field_name,
                            "value": value,
                        },
                    },
                    stage="project_fields_update",
                )
        except _AdapterBlocker as error:
            return self._write_failure(
                operation,
                code=error.code,
                stage="project_fields_update",
                status="partial",
                error_type="partial_failure",
                task_ref=task_ref,
            )

        try:
            read_back = self._call_provider(
                self._config.mcp_tools["projects_get"],
                {
                    "method": "get_project_item",
                    "owner": destination.owner,
                    "project_number": destination.project_number,
                    "item_id": item_id,
                    "field_names": field_names,
                },
                stage="task_read_back",
            )
            content = read_back.get("content")
            task_ref = _normalize_linked_issue_task_ref(
                content,
                backend_key=operation["backend_key"],
                owner=content_target.owner,
                repository=content_target.repository,
                expected_number=issue_number,
            )
        except (_AdapterBlocker, NormalizationError) as error:
            code = error.code if isinstance(error, _AdapterBlocker) else "adapter_unavailable"
            return self._write_failure(
                operation,
                code=code,
                stage="task_read_back",
                status="partial",
                error_type="partial_failure",
                task_ref=task_ref,
            )

        return self._write_success(
            operation,
            task_ref,
            status="created",
            human_action=(
                "Duplicate detection is stateless; inspect the linked task before "
                "retrying create."
            ),
        )

    def _apply_update(self, operation, destination, linked_issue):
        changes = operation["payload"]["changes"]
        task_ref = linked_issue["task_ref"]
        write_succeeded = False
        issue_changes = {
            key: changes[key]
            for key in ("title", "body")
            if key in changes
        }
        if issue_changes:
            try:
                issue = self._call_provider(
                    self._config.mcp_tools["issue_write"],
                    {
                        "method": "update",
                        "owner": linked_issue["owner"],
                        "repo": linked_issue["repository"],
                        "issue_number": linked_issue["number"],
                        **issue_changes,
                    },
                    stage="issue_update",
                )
                task_ref = _normalize_linked_issue_task_ref(
                    issue,
                    backend_key=operation["backend_key"],
                    owner=linked_issue["owner"],
                    repository=linked_issue["repository"],
                    expected_number=linked_issue["number"],
                )
                write_succeeded = True
            except (_AdapterBlocker, NormalizationError) as error:
                code = error.code if isinstance(error, _AdapterBlocker) else "adapter_unavailable"
                safe_retry = isinstance(error, _AdapterBlocker) and error.retryable
                return self._write_failure(
                    operation,
                    code=code,
                    stage="issue_update",
                    status="failed" if safe_retry else "partial",
                    error_type=(
                        "provider_failure" if safe_retry else "partial_failure"
                    ),
                    task_ref=task_ref,
                    retryable=safe_retry,
                )

        try:
            for canonical_key, value in self._changed_field_write_values(changes):
                mapping = self._config.field_mappings[canonical_key]
                self._call_provider(
                    self._config.mcp_tools["projects_write"],
                    {
                        "method": "update_project_item",
                        "owner": destination.owner,
                        "project_number": destination.project_number,
                        "item_owner": linked_issue["owner"],
                        "item_repo": linked_issue["repository"],
                        "issue_number": linked_issue["number"],
                        "updated_field": {
                            "name": mapping.field_name,
                            "value": value,
                        },
                    },
                    stage="project_fields_update",
                )
                write_succeeded = True
        except _AdapterBlocker as error:
            safe_retry = error.retryable and not write_succeeded
            return self._write_failure(
                operation,
                code=error.code,
                stage="project_fields_update",
                status="failed" if safe_retry else "partial",
                error_type=(
                    "provider_failure" if safe_retry else "partial_failure"
                ),
                task_ref=task_ref,
                retryable=safe_retry,
            )

        try:
            task_ref = self._read_back_linked_issue(
                operation,
                destination,
                linked_issue,
            )
        except (_AdapterBlocker, NormalizationError, ValueError) as error:
            code = error.code if isinstance(error, _AdapterBlocker) else "adapter_unavailable"
            return self._write_failure(
                operation,
                code=code,
                stage="task_read_back",
                status="partial",
                error_type="partial_failure",
                task_ref=task_ref,
            )
        return self._write_success(operation, task_ref, status="updated")

    def _apply_issue_comment(
        self,
        operation,
        destination,
        linked_issue,
        *,
        body,
        status,
        stage,
    ):
        task_ref = linked_issue["task_ref"]
        try:
            self._call_provider(
                self._config.mcp_tools["add_issue_comment"],
                {
                    "owner": linked_issue["owner"],
                    "repo": linked_issue["repository"],
                    "issue_number": linked_issue["number"],
                    "body": body,
                },
                stage=stage,
            )
        except _AdapterBlocker as error:
            safe_retry = error.retryable
            return self._write_failure(
                operation,
                code=error.code,
                stage=stage,
                status="failed" if safe_retry else "partial",
                error_type=(
                    "provider_failure" if safe_retry else "partial_failure"
                ),
                task_ref=task_ref,
                retryable=safe_retry,
            )
        try:
            task_ref = self._read_back_linked_issue(
                operation,
                destination,
                linked_issue,
            )
        except (_AdapterBlocker, NormalizationError, ValueError) as error:
            code = error.code if isinstance(error, _AdapterBlocker) else "adapter_unavailable"
            return self._write_failure(
                operation,
                code=code,
                stage="task_read_back",
                status="partial",
                error_type="partial_failure",
                task_ref=task_ref,
            )
        return self._write_success(operation, task_ref, status=status)

    @staticmethod
    def _render_report(report):
        def bullets(values):
            return "\n".join(f"- {value}" for value in values) or "- None."

        return (
            "## Task report\n\n"
            "### Summary\n\n"
            f"{report['summary']}\n\n"
            "### Work performed\n\n"
            f"{bullets(report['work_performed'])}\n\n"
            "### Verification\n\n"
            f"{bullets(report['verification'])}\n\n"
            "### Residuals\n\n"
            f"{bullets(report['residuals'])}"
        )

    def _read_back_linked_issue(self, operation, destination, linked_issue):
        after = None
        seen_cursors = set()
        for _page_number in range(_MAX_PROVIDER_PAGES):
            arguments = {
                "method": "list_project_items",
                "owner": destination.owner,
                "project_number": destination.project_number,
                "per_page": 50,
            }
            if after is not None:
                arguments["after"] = after
            page = self._call_provider(
                self._config.mcp_tools["projects_list"],
                arguments,
                stage="task_read_back",
            )
            page_items = page.get("items")
            page_info = page.get("pageInfo")
            if not isinstance(page_items, list) or not isinstance(page_info, dict):
                raise ValueError("Project item pagination is invalid.")
            for item in page_items:
                content = item.get("content") if isinstance(item, dict) else None
                if (
                    isinstance(content, dict)
                    and content.get("number") == linked_issue["number"]
                    and content.get("repository")
                    == f"{linked_issue['owner']}/{linked_issue['repository']}"
                ):
                    return _normalize_linked_issue_task_ref(
                        content,
                        backend_key=operation["backend_key"],
                        owner=linked_issue["owner"],
                        repository=linked_issue["repository"],
                        expected_number=linked_issue["number"],
                    )
            if page_info.get("hasNextPage") is not True:
                raise NormalizationError("Linked GitHub Issue is not in the Project.")
            after = page_info.get("nextCursor")
            if not isinstance(after, str) or not after or after in seen_cursors:
                raise ValueError("Project item pagination is invalid.")
            seen_cursors.add(after)
        raise ValueError("Project item pagination exceeded its bound.")

    def _require_configured_content_target(self, linked_issue):
        for target in self._config.content_targets.values():
            if (
                target.owner == linked_issue["owner"]
                and target.repository == linked_issue["repository"]
            ):
                return target
        raise ConfigError(
            "destination_unresolved",
            "The linked GitHub Issue content target is not configured.",
        )

    def _field_write_values(self, task):
        values = {
            "work_unit_id": task["work_unit_id"],
            "work_unit_name": task["work_unit_name"],
            "task_type": task["task_type"],
            "due_date": task["due_date"],
            "urgency": task["urgency"],
            "importance": task["importance"],
            "automation_mode": task["automation_mode"],
            "approval_required": str(task["approval_required"]).lower(),
            "source_label": task["source_ref"]["label"],
            "source_url": None,
        }
        source_ref = task["source_ref"]["ref"]
        if isinstance(source_ref, str) and source_ref.startswith("https://"):
            values["source_url"] = source_ref
        for canonical_key in _FIELD_WRITE_ORDER:
            value = values[canonical_key]
            mapping = self._config.field_mappings[canonical_key]
            if value is None and not mapping.required:
                continue
            if mapping.field_type == "single_select":
                value = mapping.options[value]
            yield canonical_key, value

    def _changed_field_write_values(self, changes):
        expanded = dict(changes)
        source_ref = expanded.pop("source_ref", None)
        if source_ref is not None:
            expanded["source_label"] = source_ref["label"]
            expanded["source_url"] = (
                source_ref["ref"]
                if source_ref["ref"].startswith("https://")
                else None
            )
        expanded.pop("title", None)
        expanded.pop("body", None)
        expanded.pop("fields", None)
        if "approval_required" in expanded:
            expanded["approval_required"] = str(
                expanded["approval_required"]
            ).lower()
        for canonical_key in _FIELD_WRITE_ORDER:
            if canonical_key not in expanded:
                continue
            value = expanded[canonical_key]
            mapping = self._config.field_mappings[canonical_key]
            if mapping.field_type == "single_select":
                value = mapping.options[value]
            yield canonical_key, value

    @staticmethod
    def _write_success(operation, task_ref, *, status, human_action=None):
        return validate_task_write_result(
            {
                "result_type": "TaskWriteResult",
                "ok": True,
                "status": status,
                "operation_type": operation["operation_type"],
                "backend_key": operation["backend_key"],
                "destination_ref": operation["destination_ref"],
                "task_ref": task_ref,
                "retryable": False,
                "human_action": human_action,
                "error": None,
            }
        )

    @staticmethod
    def _write_failure(
        operation,
        *,
        code,
        stage,
        status,
        error_type,
        task_ref=None,
        retryable=False,
    ):
        messages = {
            "adapter_unavailable": "GitHub Projects write access is unavailable.",
            "tool_disabled": "A required GitHub Projects write tool is disabled.",
            "auth_missing": "GitHub Projects authentication is unavailable.",
            "permission_failure": "GitHub Projects write permission is unavailable.",
            "rate_limited": "GitHub Projects write access is rate limited.",
            "destination_unresolved": "The configured GitHub task destination is unavailable.",
            "unsafe_delegation_exposure": "GitHub adapter delegation exposure is unsafe.",
            "capability_mismatch": "The requested GitHub adapter operation is unavailable.",
        }
        human_action = None
        if status == "partial":
            human_action = "Inspect the linked GitHub Issue before any retry."
        elif status == "failed" and retryable:
            human_action = "Retry after the provider rate limit clears."
        elif status == "failed":
            human_action = (
                "Confirm whether a GitHub Issue was created before retrying."
            )
        return validate_task_write_result(
            {
                "result_type": "TaskWriteResult",
                "ok": False,
                "status": status,
                "operation_type": operation["operation_type"],
                "backend_key": operation["backend_key"],
                "destination_ref": operation["destination_ref"],
                "task_ref": task_ref,
                "retryable": retryable,
                "human_action": human_action,
                "error": {
                    "error_type": error_type,
                    "code": code,
                    "message": messages[code],
                    "stage": stage,
                },
            }
        )

    def _execute_query(
        self,
        request: Mapping[str, Any],
        backend_key: str,
        query: Mapping[str, Any],
    ) -> Dict[str, Any]:
        destination = self._config.resolve_destination(request["destination_ref"])
        validate_host_attestation(self._config.host_attestation)

        projects_get = self._config.mcp_tools["projects_get"]
        projects_list = self._config.mcp_tools["projects_list"]
        project = self._call_provider(
            projects_get,
            {
                "method": "get_project",
                "owner": destination.owner,
                "project_number": destination.project_number,
            },
            stage="project_lookup",
        )
        self._validate_project_identity(project, destination)
        raw_fields = self._list_project_fields(
            projects_list,
            owner=destination.owner,
            project_number=destination.project_number,
        )
        self._validate_project_fields(raw_fields)
        field_ids = []
        for field in raw_fields["fields"]:
            field_id = field.get("id") if isinstance(field, dict) else None
            if type(field_id) is int and field_id > 0:
                field_ids.append(str(field_id))
            elif (
                isinstance(field_id, str)
                and field_id.isdigit()
                and int(field_id) > 0
            ):
                field_ids.append(field_id)
            else:
                raise ValueError("Project field ID is invalid.")
        limit = query.get("limit", 100)
        items = []
        after = None
        seen_cursors = set()
        for _page_number in range(_MAX_PROVIDER_PAGES):
            arguments = {
                "method": "list_project_items",
                "owner": destination.owner,
                "project_number": destination.project_number,
                "per_page": 50,
                "fields": field_ids,
            }
            if after is not None:
                arguments["after"] = after
            page = self._call_provider(
                projects_list,
                arguments,
                stage="item_query",
            )
            page_items = page.get("items")
            page_info = page.get("pageInfo")
            if not isinstance(page_items, list) or not isinstance(page_info, dict):
                raise ValueError("Project item pagination is invalid.")
            for provider_item in page_items:
                snapshot = normalize_project_item(
                    provider_item,
                    backend_key=backend_key,
                    field_mappings=self._config.field_mappings,
                )
                if matches_query(snapshot, query):
                    items.append(snapshot)
                    if len(items) == limit:
                        return {
                            "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
                            "items": items,
                        }
            if page_info.get("hasNextPage") is not True:
                return {
                    "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
                    "items": items,
                }
            after = page_info.get("nextCursor")
            if not isinstance(after, str) or not after or after in seen_cursors:
                raise ValueError("Project item pagination is invalid.")
            seen_cursors.add(after)
        raise ValueError("Project item pagination exceeded its bound.")

    @staticmethod
    def _query_failure(code: str) -> Dict[str, Any]:
        messages = {
            "adapter_unavailable": "GitHub Projects adapter read access is unavailable.",
            "tool_disabled": "A required GitHub Projects read tool is disabled.",
            "auth_missing": "GitHub Projects authentication is unavailable.",
            "permission_failure": "GitHub Projects read permission is unavailable.",
            "rate_limited": "GitHub Projects read access is rate limited.",
            "destination_unresolved": "The configured GitHub Project is unavailable.",
            "required_field_missing": "A required GitHub Project field is unavailable.",
            "field_type_mismatch": "A GitHub Project field has an incompatible type.",
            "unsafe_delegation_exposure": "GitHub adapter delegation exposure is unsafe.",
            "capability_mismatch": "A required GitHub adapter capability is unavailable.",
            "invalid_query": "The adapter query is invalid.",
        }
        return {
            "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
            "items": [],
            "error": {"code": code, "message": messages[code]},
        }

    def _query_is_valid(self, query: Any) -> bool:
        allowed = {"work_unit_id", "task_type", "status", "due_before", "limit"}
        if not isinstance(query, dict) or set(query) - allowed:
            return False
        for field in ("work_unit_id", "task_type", "status"):
            if field in query and (
                not isinstance(query[field], str) or not query[field]
            ):
                return False
        if "task_type" in query and query["task_type"] not in self._config.field_mappings[
            "task_type"
        ].options:
            return False
        due_before = query.get("due_before")
        if due_before is not None:
            if not isinstance(due_before, str):
                return False
            try:
                if date.fromisoformat(due_before).isoformat() != due_before:
                    return False
            except ValueError:
                return False
        limit = query.get("limit")
        if limit is not None and (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or not 1 <= limit <= 100
        ):
            return False
        return True

    def _call_provider(
        self,
        tool_name: str,
        arguments: Mapping[str, Any],
        *,
        stage: str,
    ) -> Dict[str, Any]:
        try:
            result = self._dispatch(tool_name, dict(arguments))
        except KeyError:
            raise _AdapterBlocker("tool_disabled", stage)
        except Exception:
            raise _AdapterBlocker("adapter_unavailable", stage)
        if not isinstance(result, str):
            raise _AdapterBlocker("adapter_unavailable", stage)
        try:
            envelope = json.loads(
                result,
                object_pairs_hook=_reject_duplicate_keys,
                parse_constant=_reject_non_json_constant,
            )
        except (TypeError, ValueError):
            raise _AdapterBlocker("adapter_unavailable", stage)
        if not isinstance(envelope, dict):
            raise _AdapterBlocker("adapter_unavailable", stage)

        envelope_keys = set(envelope)
        if envelope_keys == {"error"}:
            error_value = envelope["error"]
            code = self._public_error_code(error_value)
            raise _AdapterBlocker(
                code,
                stage,
                retryable=(
                    code == "rate_limited"
                    and self._is_explicit_no_write_error(error_value)
                ),
            )
        if envelope_keys not in ({"result"}, {"result", "structuredContent"}):
            raise _AdapterBlocker("adapter_unavailable", stage)

        provider_result = envelope["result"]
        if isinstance(provider_result, str):
            try:
                provider_result = json.loads(
                    provider_result,
                    object_pairs_hook=_reject_duplicate_keys,
                    parse_constant=_reject_non_json_constant,
                )
            except (TypeError, ValueError):
                raise _AdapterBlocker("adapter_unavailable", stage)
        if not isinstance(provider_result, dict):
            raise _AdapterBlocker("adapter_unavailable", stage)

        if "structuredContent" in envelope:
            structured_content = envelope["structuredContent"]
            if (
                not isinstance(structured_content, dict)
                or structured_content != provider_result
            ):
                raise _AdapterBlocker("adapter_unavailable", stage)
        return provider_result

    @staticmethod
    def _public_error_code(error: Any) -> str:
        if not isinstance(error, str) or not error.strip():
            return "adapter_unavailable"
        normalized = error.casefold()
        for patterns, code in _PUBLIC_ERROR_PATTERNS:
            if any(pattern in normalized for pattern in patterns):
                return code
        return "adapter_unavailable"

    @staticmethod
    def _is_explicit_no_write_error(error: Any) -> bool:
        if not isinstance(error, str):
            return False
        normalized = error.casefold()
        return (
            "rate limit" in normalized or "rate_limited" in normalized
        ) and (
            "write not executed" in normalized
            or "no write occurred" in normalized
        )

    @staticmethod
    def _validate_project_identity(result: Any, destination: Any) -> None:
        owner = result.get("owner") if isinstance(result, dict) else None
        owner_login = owner.get("login") if isinstance(owner, dict) else owner
        if (
            not isinstance(result, dict)
            or result.get("number") != destination.project_number
            or owner_login != destination.owner
        ):
            raise _AdapterBlocker("destination_unresolved", "project_lookup")

    @staticmethod
    def _blocked_result(
        operation: Mapping[str, Any],
        code: str,
        stage: str,
    ) -> Dict[str, Any]:
        messages = {
            "adapter_unavailable": "GitHub Projects adapter read access is unavailable.",
            "tool_disabled": "A required GitHub Projects read tool is disabled.",
            "auth_missing": "GitHub Projects authentication is unavailable.",
            "permission_failure": "GitHub Projects read permission is unavailable.",
            "rate_limited": "GitHub Projects read access is rate limited.",
            "destination_unresolved": "The configured GitHub Project is unavailable.",
            "required_field_missing": "A required GitHub Project field is unavailable.",
            "field_type_mismatch": "A GitHub Project field has an incompatible type.",
            "unsafe_delegation_exposure": "GitHub adapter delegation exposure is unsafe.",
            "capability_mismatch": "A required GitHub adapter capability is unavailable.",
        }
        return {
            "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
            "ok": False,
            "status": "blocked",
            "operation_type": operation["operation_type"],
            "backend_key": operation["backend_key"],
            "destination_ref": operation["destination_ref"],
            "readiness": {"ok": False, "checks": []},
            "expected_side_effects": [],
            "requires_human_confirmation": True,
            "error": {
                "error_type": "setup_blocker",
                "code": code,
                "message": messages[code],
                "stage": stage,
            },
        }

    def _list_project_fields(
        self,
        tool_name: str,
        *,
        owner: str,
        project_number: int,
    ) -> Dict[str, Any]:
        fields = []
        after = None
        seen_cursors = set()
        for _page_number in range(_MAX_PROVIDER_PAGES):
            arguments = {
                "method": "list_project_fields",
                "owner": owner,
                "project_number": project_number,
                "per_page": 50,
            }
            if after is not None:
                arguments["after"] = after
            result = self._call_provider(
                tool_name,
                arguments,
                stage="field_probe",
            )
            page_fields = result.get("fields") if isinstance(result, dict) else None
            page_info = result.get("pageInfo") if isinstance(result, dict) else None
            if not isinstance(page_fields, list) or not isinstance(page_info, dict):
                raise ValueError("Project field pagination is invalid.")
            fields.extend(page_fields)
            if page_info.get("hasNextPage") is not True:
                return {"fields": fields}
            after = page_info.get("nextCursor")
            if not isinstance(after, str) or not after or after in seen_cursors:
                raise ValueError("Project field pagination is invalid.")
            seen_cursors.add(after)
        raise ValueError("Project field pagination exceeded its bound.")

    def _validate_project_fields(self, raw_result: Any) -> None:
        fields = raw_result.get("fields") if isinstance(raw_result, dict) else None
        if not isinstance(fields, list):
            raise ValueError("Project fields are unavailable.")
        by_name = {
            field.get("name"): field
            for field in fields
            if isinstance(field, dict) and isinstance(field.get("name"), str)
        }
        for mapping in self._config.field_mappings.values():
            provider_field = by_name.get(mapping.field_name)
            if provider_field is None:
                if mapping.required:
                    raise _AdapterBlocker("required_field_missing", "field_probe")
                continue
            if provider_field.get("data_type") != _PROVIDER_FIELD_TYPES[mapping.field_type]:
                raise _AdapterBlocker("field_type_mismatch", "field_probe")

    @staticmethod
    def _requires_human_confirmation(operation: Mapping[str, Any]) -> bool:
        if operation["operation_type"] != "task.create":
            return False
        task = operation["payload"]["task"]
        return bool(
            task["approval_required"]
            or task.get("fields", {}).get("review_notes")
        )
