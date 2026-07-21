"""Executable GitHub Projects adapter through an injected public dispatch seam."""

from __future__ import annotations

import json
from datetime import date
from typing import Any, Callable, Dict, Mapping

from .config import ConfigError, GithubProjectsConfig
from .contracts import ADAPTER_CONTRACT_VERSION, validate_operation_envelope
from .normalization import NormalizationError, matches_query, normalize_project_item
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
_PUBLIC_ERROR_PATTERNS = (
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
    def __init__(self, code: str, stage: str):
        super().__init__(code)
        self.code = code
        self.stage = stage


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
            raise _AdapterBlocker(
                self._public_error_code(envelope["error"]),
                stage,
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
