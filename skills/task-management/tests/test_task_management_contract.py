import json
import hashlib
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "task-management"
SKILL = SKILL_ROOT / "SKILL.md"
CORE = SKILL_ROOT / "references" / "core.md"
PROJECTS = SKILL_ROOT / "references" / "github-projects.md"
ISSUES = SKILL_ROOT / "references" / "issue-contract.md"
SAFETY = SKILL_ROOT / "references" / "safety-and-failures.md"
FIXTURES = SKILL_ROOT / "tests" / "fixtures"
HERMES_READINESS_LEDGER = (
    REPO_ROOT
    / "knowledge"
    / "wiki"
    / "syntheses"
    / "task-management-hermes-readiness"
    / "issues.md"
)

EXPECTED_FILES = {
    "SKILL.md",
    "references/core.md",
    "references/github-projects.md",
    "references/issue-contract.md",
    "references/safety-and-failures.md",
    "tests/fixtures/native-metadata-cases.json",
    "tests/fixtures/operation-capability-cases.json",
    "tests/fixtures/pagination-cases.json",
    "tests/fixtures/transition-cases.json",
    "tests/test_task_management_contract.py",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def apply_requested_change(
    before: dict[str, object],
    requested_change: dict[str, object],
) -> dict[str, object]:
    result = deepcopy(before)
    mutable = result["mutable"]
    if not isinstance(mutable, dict):
        raise AssertionError("mutable fixture state must be an object")
    mutable.update(requested_change)
    return result


def expand_page(page: dict[str, object]) -> list[dict[str, object]]:
    generated = page.get("generated_unique")
    items = list(page.get("items", []))
    if isinstance(generated, dict):
        start = int(generated["start"])
        count = int(generated["count"])
        items = [
            {
                "item_identity": f"PVTI-{number}",
                "task_identity": f"I-{number}",
                "status": "Ready",
                "updated_at": "2026-07-30T00:00:00Z",
            }
            for number in range(start, start + count)
        ] + items
    return items


RECONCILED_FIELDS = ("status", "priority", "due_date")
CANONICAL_STATUSES = {
    "Inbox",
    "Backlog",
    "Ready",
    "In progress",
    "Blocked",
    "Done",
    "Cancelled",
}
CANONICAL_PRIORITIES = {"P0", "P1", "P2", "P3"}
TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
DUE_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
INVALID_VALUE = object()


def normalized_identity(value: object) -> object:
    if (
        type(value) is str
        and value
        and not any(ord(character) < 32 for character in value)
    ):
        return value
    return None


def normalized_timestamp(value: object) -> object:
    if value is None:
        return None
    if type(value) is str and TIMESTAMP_PATTERN.fullmatch(value):
        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            return INVALID_VALUE
        return value
    return INVALID_VALUE


def normalized_field_value(field: str, value: object) -> object:
    if value is None:
        return None
    if field == "status" and type(value) is str and value in CANONICAL_STATUSES:
        return value
    if field == "priority" and type(value) is str and value in CANONICAL_PRIORITIES:
        return value
    if field == "due_date" and type(value) is str and DUE_DATE_PATTERN.fullmatch(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return INVALID_VALUE
        return value
    return INVALID_VALUE


def normalized_explicit_clear(value: object) -> object:
    if type(value) is not list:
        return None
    if any(type(field) is not str or field not in RECONCILED_FIELDS for field in value):
        return None
    if len(value) != len(set(value)):
        return None
    return set(value)


def merge_observation(
    items: dict[str, dict[str, object]],
    observation: dict[str, object],
    item_identity_conflicts: set[str],
    reconciliation_conflicts: set[str],
) -> bool:
    item_id = normalized_identity(observation.get("item_identity"))
    if item_id is None:
        item_identity_conflicts.add("malformed-item-identity")
        return False
    task_id = normalized_identity(observation.get("task_identity"))
    if task_id is None:
        item_identity_conflicts.add(item_id)
        task_id = "malformed-task-identity"
    explicit_clear = normalized_explicit_clear(
        observation.get("explicit_clear", [])
    )
    if explicit_clear is None:
        explicit_clear = set()
        reconciliation_conflicts.add(item_id)
    new_time = normalized_timestamp(observation.get("updated_at"))
    timestamp_is_valid = new_time is not INVALID_VALUE
    if not timestamp_is_valid:
        new_time = None
        reconciliation_conflicts.add(item_id)
    current = items.get(item_id)
    if current is None:
        normalized_fields: dict[str, object] = {}
        for field in RECONCILED_FIELDS:
            value = normalized_field_value(field, observation.get(field))
            if value is INVALID_VALUE:
                reconciliation_conflicts.add(item_id)
                value = None
            normalized_fields[field] = (
                None if field in explicit_clear else value
            )
        initial = {
            "item_identity": item_id,
            "task_identity": task_id,
            **normalized_fields,
        }
        initial["_field_updated_at"] = {
            field: new_time
            for field in RECONCILED_FIELDS
            if (
                timestamp_is_valid
                and
                field in observation
                and (
                    normalized_fields[field] is not None
                    or field in explicit_clear
                )
            )
        }
        initial["_field_tombstones"] = {
            field: new_time
            for field in explicit_clear
            if field in RECONCILED_FIELDS
        }
        items[item_id] = initial
        return False
    if current["task_identity"] != task_id:
        item_identity_conflicts.add(item_id)
        return True
    if not timestamp_is_valid:
        return True
    field_updated_at = current.setdefault("_field_updated_at", {})
    field_tombstones = current.setdefault("_field_tombstones", {})
    for field in RECONCILED_FIELDS:
        old_time = field_updated_at.get(field)
        if field in explicit_clear:
            if (
                old_time is not None
                and new_time is not None
                and str(new_time) < str(old_time)
            ):
                continue
            current[field] = None
            field_updated_at[field] = new_time
            field_tombstones[field] = new_time
            continue
        if field not in observation:
            continue
        incoming = normalized_field_value(field, observation[field])
        if incoming is INVALID_VALUE:
            reconciliation_conflicts.add(item_id)
            continue
        existing = current.get(field)
        if incoming is None:
            continue
        if field in field_tombstones:
            tombstone_time = field_tombstones[field]
            if tombstone_time is None or new_time is None:
                reconciliation_conflicts.add(item_id)
                continue
            if str(new_time) < str(tombstone_time):
                continue
        if (
            old_time is not None
            and new_time is not None
            and str(new_time) < str(old_time)
        ):
            continue
        if incoming == existing:
            if (
                new_time is not None
                and (old_time is None or str(new_time) >= str(old_time))
            ):
                field_updated_at[field] = new_time
            field_tombstones.pop(field, None)
            continue
        if existing is None:
            if old_time is not None and new_time is None:
                reconciliation_conflicts.add(item_id)
                continue
            current[field] = incoming
            field_updated_at[field] = new_time
            field_tombstones.pop(field, None)
            continue
        if old_time is not None and new_time is not None:
            if str(new_time) >= str(old_time):
                current[field] = incoming
                field_updated_at[field] = new_time
                field_tombstones.pop(field, None)
        else:
            reconciliation_conflicts.add(item_id)
    return True


def matching_state(
    *,
    items: dict[str, dict[str, object]],
    first_seen: dict[str, int],
    item_identity_conflicts: set[str],
    reconciliation_conflicts: set[str],
    requested_filter: object,
) -> tuple[dict[str, list[str]], dict[str, list[str]], list[str]]:
    task_memberships: dict[str, list[str]] = {}
    for item_id, item in items.items():
        if (
            item_id in item_identity_conflicts
            or item_id in reconciliation_conflicts
            or (
                requested_filter is not None
                and item.get("status") != requested_filter
            )
        ):
            continue
        task_id = str(item["task_identity"])
        task_memberships.setdefault(task_id, []).append(item_id)
    membership_conflicts = {
        task_id: sorted(memberships)
        for task_id, memberships in task_memberships.items()
        if len(memberships) > 1
    }
    ordered = sorted(
        task_memberships,
        key=lambda task_id: first_seen.get(task_id, len(first_seen)),
    )
    return task_memberships, membership_conflicts, ordered


def envelope(
    *,
    items: dict[str, dict[str, object]],
    first_seen: dict[str, int],
    raw_count: int,
    duplicate_count: int,
    item_identity_conflicts: set[str],
    reconciliation_conflicts: set[str],
    already_emitted: set[str],
    requested_filter: object,
    query_mode: str,
    continuation: object,
    completeness: str,
    truncated: bool,
    stop_reason: str,
) -> dict[str, object]:
    _, membership_conflicts, all_matching = matching_state(
        items=items,
        first_seen=first_seen,
        item_identity_conflicts=item_identity_conflicts,
        reconciliation_conflicts=reconciliation_conflicts,
        requested_filter=requested_filter,
    )
    if query_mode == "completeness_required":
        ordered = all_matching
    else:
        ordered = [
            task_id
            for task_id in all_matching
            if task_id not in already_emitted
        ]
    returned = ordered[:50]
    result_order: object = returned
    if len(returned) >= 49:
        result_order = {"first": returned[0], "last": returned[-1]}
    if reconciliation_conflicts:
        completeness = "partial"
        stop_reason = "reconciliation_conflict"
    elif item_identity_conflicts or membership_conflicts:
        completeness = "partial"
        stop_reason = "identity_conflict"
    result = {
        "raw_observation_count": raw_count,
        "deduplicated_observation_count": duplicate_count,
        "identity_conflict_count": (
            len(item_identity_conflicts) + len(membership_conflicts)
        ),
        "reconciliation_conflict_count": len(reconciliation_conflicts),
        "unique_task_count": len(ordered),
        "returned_count": len(returned),
        "task_order": result_order,
        "completeness": completeness,
        "truncated": truncated or len(ordered) > len(returned),
        "continuation": continuation,
        "stop_reason": stop_reason,
        "_returned_task_identities": returned,
    }
    invalidated = sorted(already_emitted - set(all_matching))
    if invalidated:
        result["invalidated_task_identities"] = invalidated
    return result


def checkpoint_for(
    *,
    items: dict[str, dict[str, object]],
    first_seen: dict[str, int],
    item_identity_conflicts: set[str],
    reconciliation_conflicts: set[str],
    already_emitted: set[str],
    raw_count: int,
    duplicate_count: int,
    requested_filter: object,
    query_mode: str,
) -> dict[str, object]:
    serialized_items: dict[str, dict[str, object]] = {}
    field_freshness: dict[str, dict[str, object]] = {}
    field_tombstones: dict[str, dict[str, object]] = {}
    for item_id, item in items.items():
        if normalized_identity(item_id) != item_id:
            raise AssertionError("checkpoint item identity is malformed")
        task_id = normalized_identity(item.get("task_identity"))
        if task_id is None:
            raise AssertionError("checkpoint task identity is malformed")
        safe_fields: dict[str, object] = {}
        for field in RECONCILED_FIELDS:
            value = normalized_field_value(field, item.get(field))
            if value is INVALID_VALUE:
                raise AssertionError(
                    f"checkpoint {field} is not a permitted scalar"
                )
            safe_fields[field] = value
        serialized_items[item_id] = {
            "item_identity": item_id,
            "task_identity": task_id,
            **safe_fields,
        }
        field_freshness[item_id] = {}
        field_tombstones[item_id] = {}
        for map_name, target in (
            ("_field_updated_at", field_freshness[item_id]),
            ("_field_tombstones", field_tombstones[item_id]),
        ):
            values = item.get(map_name, {})
            if type(values) is not dict or not set(values).issubset(
                RECONCILED_FIELDS
            ):
                raise AssertionError(
                    f"checkpoint {map_name} has an invalid field schema"
                )
            for field, timestamp in values.items():
                normalized = normalized_timestamp(timestamp)
                if normalized is INVALID_VALUE:
                    raise AssertionError(
                        f"checkpoint {map_name} timestamp is malformed"
                    )
                target[field] = normalized
    _, membership_conflicts, matching = matching_state(
        items=items,
        first_seen=first_seen,
        item_identity_conflicts=item_identity_conflicts,
        reconciliation_conflicts=reconciliation_conflicts,
        requested_filter=requested_filter,
    )
    invalidated = sorted(already_emitted - set(matching))
    checkpoint = {
        "items": serialized_items,
        "field_freshness": field_freshness,
        "field_tombstones": field_tombstones,
        "first_seen": dict(first_seen),
        "item_identity_conflicts": sorted(item_identity_conflicts),
        "reconciliation_conflicts": sorted(reconciliation_conflicts),
        "membership_conflicts": membership_conflicts,
        "already_emitted_task_identities": sorted(already_emitted),
        "raw_observation_count": raw_count,
        "deduplicated_observation_count": duplicate_count,
        "normalized_filter": requested_filter,
        "query_mode": query_mode,
        "matching_task_identities": matching,
        "unique_matching_count": len(matching),
        "display_task_identities": matching[:50],
        "invalidated_task_identities": invalidated,
    }
    validate_checkpoint(checkpoint)
    return checkpoint


CHECKPOINT_KEYS = {
    "items",
    "field_freshness",
    "field_tombstones",
    "first_seen",
    "item_identity_conflicts",
    "reconciliation_conflicts",
    "membership_conflicts",
    "already_emitted_task_identities",
    "raw_observation_count",
    "deduplicated_observation_count",
    "normalized_filter",
    "query_mode",
    "matching_task_identities",
    "unique_matching_count",
    "display_task_identities",
    "invalidated_task_identities",
}
CHECKPOINT_ITEM_KEYS = {
    "item_identity",
    "task_identity",
    "status",
    "priority",
    "due_date",
}


def require_normalized_string_list(value: object, label: str) -> list[str]:
    if type(value) is not list:
        raise AssertionError(f"checkpoint {label} must be a list")
    normalized: list[str] = []
    for entry in value:
        identity = normalized_identity(entry)
        if identity is None:
            raise AssertionError(
                f"checkpoint {label} must contain normalized strings"
            )
        normalized.append(identity)
    if len(normalized) != len(set(normalized)):
        raise AssertionError(f"checkpoint {label} must not contain duplicates")
    return normalized


def validate_checkpoint(checkpoint: object) -> None:
    if type(checkpoint) is not dict or set(checkpoint) != CHECKPOINT_KEYS:
        raise AssertionError("checkpoint must have the exact safe schema")
    items = checkpoint["items"]
    if type(items) is not dict:
        raise AssertionError("checkpoint items must be an object")
    for item_id, item in items.items():
        if normalized_identity(item_id) != item_id:
            raise AssertionError("checkpoint item keys must be normalized strings")
        if type(item) is not dict or set(item) != CHECKPOINT_ITEM_KEYS:
            raise AssertionError("checkpoint item must have the exact safe schema")
        if item["item_identity"] != item_id:
            raise AssertionError("checkpoint item identity must match its key")
        if normalized_identity(item["task_identity"]) is None:
            raise AssertionError("checkpoint task identity must be a string")
        for field in RECONCILED_FIELDS:
            if normalized_field_value(field, item[field]) is INVALID_VALUE:
                raise AssertionError(
                    f"checkpoint {field} must be a permitted scalar"
                )

    for map_name in ("field_freshness", "field_tombstones"):
        field_map = checkpoint[map_name]
        if type(field_map) is not dict or set(field_map) != set(items):
            raise AssertionError(
                f"checkpoint {map_name} must map every exact item"
            )
        for item_id, values in field_map.items():
            if type(values) is not dict or not set(values).issubset(
                RECONCILED_FIELDS
            ):
                raise AssertionError(
                    f"checkpoint {map_name} has an invalid field schema"
                )
            for timestamp in values.values():
                if normalized_timestamp(timestamp) is INVALID_VALUE:
                    raise AssertionError(
                        f"checkpoint {map_name} timestamps must be scalar"
                    )

    first_seen = checkpoint["first_seen"]
    if type(first_seen) is not dict:
        raise AssertionError("checkpoint first_seen must be an object")
    for task_id, ordinal in first_seen.items():
        if normalized_identity(task_id) != task_id:
            raise AssertionError("checkpoint first_seen keys must be strings")
        if type(ordinal) is not int or ordinal < 0:
            raise AssertionError(
                "checkpoint first_seen ordinals must be non-negative integers"
            )

    for collection_name in (
        "item_identity_conflicts",
        "reconciliation_conflicts",
        "already_emitted_task_identities",
        "matching_task_identities",
        "display_task_identities",
        "invalidated_task_identities",
    ):
        require_normalized_string_list(
            checkpoint[collection_name],
            collection_name,
        )

    membership_conflicts = checkpoint["membership_conflicts"]
    if type(membership_conflicts) is not dict:
        raise AssertionError("checkpoint membership_conflicts must be an object")
    for task_id, memberships in membership_conflicts.items():
        if normalized_identity(task_id) != task_id:
            raise AssertionError(
                "checkpoint membership conflict keys must be strings"
            )
        require_normalized_string_list(
            memberships,
            "membership conflict memberships",
        )

    for count_name in (
        "raw_observation_count",
        "deduplicated_observation_count",
        "unique_matching_count",
    ):
        value = checkpoint[count_name]
        if type(value) is not int or value < 0:
            raise AssertionError(
                f"checkpoint {count_name} must be a non-negative integer"
            )
    normalized_filter = checkpoint["normalized_filter"]
    if not (
        normalized_filter is None
        or (
            type(normalized_filter) is str
            and normalized_filter in CANONICAL_STATUSES
        )
    ):
        raise AssertionError("checkpoint normalized_filter must be canonical")
    query_mode = checkpoint["query_mode"]
    if type(query_mode) is not str or query_mode not in {
        "standard_display",
        "completeness_required",
    }:
        raise AssertionError("checkpoint query_mode is invalid")
    matching = checkpoint["matching_task_identities"]
    if checkpoint["unique_matching_count"] != len(matching):
        raise AssertionError("checkpoint unique count must match identities")
    if checkpoint["display_task_identities"] != matching[:50]:
        raise AssertionError("checkpoint display must be the first 50 matches")


def continuation_association(
    provider_continuation: object,
    checkpoint: dict[str, object],
) -> str:
    if provider_continuation is not None and type(provider_continuation) is not str:
        raise AssertionError("provider continuation must be an opaque string")
    validate_checkpoint(checkpoint)
    payload = json.dumps(
        {
            "provider_continuation": provider_continuation,
            "checkpoint": checkpoint,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def continuation_state_for(
    provider_continuation: object,
    checkpoint: dict[str, object],
) -> dict[str, object]:
    return {
        "provider_continuation": provider_continuation,
        "checkpoint": checkpoint,
        "association": continuation_association(
            provider_continuation,
            checkpoint,
        ),
    }


def result_checkpoint(result: dict[str, object]) -> dict[str, object]:
    return result["continuation_state"]["checkpoint"]


def attach_checkpoint(
    result: dict[str, object],
    *,
    items: dict[str, dict[str, object]],
    first_seen: dict[str, int],
    item_identity_conflicts: set[str],
    reconciliation_conflicts: set[str],
    already_emitted: set[str],
    raw_count: int,
    duplicate_count: int,
    requested_filter: object,
    query_mode: str,
) -> dict[str, object]:
    emitted = set(already_emitted)
    emitted.update(result["_returned_task_identities"])
    checkpoint = checkpoint_for(
        items=items,
        first_seen=first_seen,
        item_identity_conflicts=item_identity_conflicts,
        reconciliation_conflicts=reconciliation_conflicts,
        already_emitted=emitted,
        raw_count=raw_count,
        duplicate_count=duplicate_count,
        requested_filter=requested_filter,
        query_mode=query_mode,
    )
    result["continuation_state"] = continuation_state_for(
        result["continuation"],
        checkpoint,
    )
    return result


def reconcile_pages(case: dict[str, object]) -> dict[str, object]:
    requested_filter = normalize_status(str(case["filter"])) if case.get("filter") else None
    if case.get("filter") and requested_filter is None:
        raise ValueError("unknown Status filter")
    query_mode = (
        "completeness_required"
        if case.get("mode") == "completeness_required"
        else "standard_display"
    )
    if (
        "resume_checkpoint" in case
        or "resume_provider_continuation" in case
    ):
        raise AssertionError(
            "resume requires one indivisible ContinuationState"
        )
    resume_state = case.get("resume_continuation_state")
    expected_resume_cursor = None
    if resume_state is None:
        resume: dict[str, object] = {}
    else:
        if (
            type(resume_state) is not dict
            or set(resume_state)
            != {"provider_continuation", "checkpoint", "association"}
        ):
            raise AssertionError(
                "resume requires one indivisible ContinuationState"
            )
        resume_checkpoint = resume_state["checkpoint"]
        if type(resume_checkpoint) is not dict:
            raise AssertionError("ContinuationState checkpoint is invalid")
        expected_association = continuation_association(
            resume_state["provider_continuation"],
            resume_checkpoint,
        )
        if resume_state["association"] != expected_association:
            raise AssertionError(
                "ContinuationState association does not match cursor/checkpoint"
            )
        expected_resume_cursor = resume_state["provider_continuation"]
        resume = resume_checkpoint
    if resume:
        validate_checkpoint(resume)
        if resume.get("normalized_filter") != requested_filter:
            raise AssertionError(
                "resume checkpoint normalized Status filter does not match"
            )
        if resume.get("query_mode") != query_mode:
            raise AssertionError("resume checkpoint query mode does not match")
    items = {
        item_id: {
            "item_identity": item["item_identity"],
            "task_identity": item["task_identity"],
            **{
                field: item[field]
                for field in RECONCILED_FIELDS
            },
        }
        for item_id, item in dict(resume.get("items", {})).items()
    }
    freshness = resume.get("field_freshness", {})
    tombstones = resume.get("field_tombstones", {})
    for item_id, item in items.items():
        item["_field_updated_at"] = {
            field: timestamp
            for field, timestamp in freshness.get(item_id, {}).items()
        }
        item["_field_tombstones"] = {
            field: timestamp
            for field, timestamp in tombstones.get(item_id, {}).items()
        }
    first_seen = {
        task_id: ordinal
        for task_id, ordinal in dict(resume.get("first_seen", {})).items()
    }
    raw_count = resume.get("raw_observation_count", 0)
    duplicate_count = resume.get("deduplicated_observation_count", 0)
    call_start_raw = raw_count
    call_start_duplicates = duplicate_count
    item_identity_conflicts = set(resume.get("item_identity_conflicts", []))
    reconciliation_conflicts = set(resume.get("reconciliation_conflicts", []))
    already_emitted = set(resume.get("already_emitted_task_identities", []))
    already_emitted.update(
        require_normalized_string_list(
            case.get("already_emitted_task_identities", []),
            "already_emitted_task_identities input",
        )
    )
    completeness_required = query_mode == "completeness_required"

    def output_counts(
        cumulative_raw: int,
        cumulative_duplicates: int,
    ) -> tuple[int, int]:
        if completeness_required:
            return cumulative_raw, cumulative_duplicates
        return (
            cumulative_raw - call_start_raw,
            cumulative_duplicates - call_start_duplicates,
        )

    for page_index, page in enumerate(case["pages"]):
        incoming = page.get("incoming_cursor")
        if (
            page_index == 0
            and resume_state is not None
            and incoming != expected_resume_cursor
        ):
            raise AssertionError(
                "ContinuationState association cursor must be consumed unchanged"
            )
        if "error" in page:
            output_raw, output_duplicates = output_counts(
                raw_count,
                duplicate_count,
            )
            result = envelope(
                items=items,
                first_seen=first_seen,
                raw_count=output_raw,
                duplicate_count=output_duplicates,
                item_identity_conflicts=item_identity_conflicts,
                reconciliation_conflicts=reconciliation_conflicts,
                already_emitted=already_emitted,
                requested_filter=requested_filter,
                query_mode=query_mode,
                continuation=incoming,
                completeness="partial",
                truncated=False,
                stop_reason=str(page["error"]),
            )
            return attach_checkpoint(
                result,
                items=items,
                first_seen=first_seen,
                item_identity_conflicts=item_identity_conflicts,
                reconciliation_conflicts=reconciliation_conflicts,
                already_emitted=already_emitted,
                raw_count=raw_count,
                duplicate_count=duplicate_count,
                requested_filter=requested_filter,
                query_mode=query_mode,
            )
        candidate_items = deepcopy(items)
        candidate_first_seen = dict(first_seen)
        candidate_identity_conflicts = set(item_identity_conflicts)
        candidate_conflicts = set(reconciliation_conflicts)
        candidate_raw = raw_count
        candidate_duplicates = duplicate_count
        candidate_sequence = max(
            candidate_first_seen.values(),
            default=-1,
        ) + 1
        observations = expand_page(page)
        for observation in observations:
            candidate_raw += 1
            if merge_observation(
                candidate_items,
                observation,
                candidate_identity_conflicts,
                candidate_conflicts,
            ):
                candidate_duplicates += 1
            item_id = normalized_identity(observation.get("item_identity"))
            task_id = normalized_identity(observation.get("task_identity"))
            if item_id is None or task_id is None or item_id not in candidate_items:
                continue
            item = candidate_items[item_id]
            if (
                item_id not in candidate_identity_conflicts
                and item_id not in candidate_conflicts
                and (
                    requested_filter is None
                    or item.get("status") == requested_filter
                )
                and task_id not in candidate_first_seen
            ):
                candidate_first_seen[task_id] = candidate_sequence
                candidate_sequence += 1
        output_raw, output_duplicates = output_counts(
            candidate_raw,
            candidate_duplicates,
        )
        candidate = envelope(
            items=candidate_items,
            first_seen=candidate_first_seen,
            raw_count=output_raw,
            duplicate_count=output_duplicates,
            item_identity_conflicts=candidate_identity_conflicts,
            reconciliation_conflicts=candidate_conflicts,
            already_emitted=already_emitted,
            requested_filter=requested_filter,
            query_mode=query_mode,
            continuation=page.get("outgoing_cursor"),
            completeness="partial" if page.get("has_next") else "complete",
            truncated=bool(page.get("has_next")),
            stop_reason="unique_limit_reached" if page.get("has_next") else "source_exhausted",
        )
        _, _, candidate_matching = matching_state(
            items=candidate_items,
            first_seen=candidate_first_seen,
            item_identity_conflicts=candidate_identity_conflicts,
            reconciliation_conflicts=candidate_conflicts,
            requested_filter=requested_filter,
        )
        candidate_deliverable = [
            task_id
            for task_id in candidate_matching
            if task_id not in already_emitted
        ]
        if not completeness_required and len(candidate_deliverable) > 50:
            output_raw, output_duplicates = output_counts(
                candidate_raw,
                candidate_duplicates,
            )
            result = envelope(
                items=items,
                first_seen=first_seen,
                raw_count=output_raw,
                duplicate_count=output_duplicates,
                item_identity_conflicts=item_identity_conflicts,
                reconciliation_conflicts=reconciliation_conflicts,
                already_emitted=already_emitted,
                requested_filter=requested_filter,
                query_mode=query_mode,
                continuation=incoming,
                completeness="partial",
                truncated=True,
                stop_reason="unique_limit_page_deferred",
            )
            return attach_checkpoint(
                result,
                items=items,
                first_seen=first_seen,
                item_identity_conflicts=item_identity_conflicts,
                reconciliation_conflicts=reconciliation_conflicts,
                already_emitted=already_emitted,
                raw_count=candidate_raw,
                duplicate_count=candidate_duplicates,
                requested_filter=requested_filter,
                query_mode=query_mode,
            )
        items = candidate_items
        first_seen = candidate_first_seen
        item_identity_conflicts = candidate_identity_conflicts
        reconciliation_conflicts = candidate_conflicts
        raw_count = candidate_raw
        duplicate_count = candidate_duplicates
        if (
            not completeness_required
            and len(candidate_deliverable) == 50
        ) or not page.get("has_next"):
            return attach_checkpoint(
                candidate,
                items=items,
                first_seen=first_seen,
                item_identity_conflicts=item_identity_conflicts,
                reconciliation_conflicts=reconciliation_conflicts,
                already_emitted=already_emitted,
                raw_count=raw_count,
                duplicate_count=duplicate_count,
                requested_filter=requested_filter,
                query_mode=query_mode,
            )
    output_raw, output_duplicates = output_counts(raw_count, duplicate_count)
    result = envelope(
        items=items,
        first_seen=first_seen,
        raw_count=output_raw,
        duplicate_count=output_duplicates,
        item_identity_conflicts=item_identity_conflicts,
        reconciliation_conflicts=reconciliation_conflicts,
        already_emitted=already_emitted,
        requested_filter=requested_filter,
        query_mode=query_mode,
        continuation=case["pages"][-1].get("outgoing_cursor"),
        completeness="partial",
        truncated=False,
        stop_reason="page_input_incomplete",
    )
    return attach_checkpoint(
        result,
        items=items,
        first_seen=first_seen,
        item_identity_conflicts=item_identity_conflicts,
        reconciliation_conflicts=reconciliation_conflicts,
        already_emitted=already_emitted,
        raw_count=raw_count,
        duplicate_count=duplicate_count,
        requested_filter=requested_filter,
        query_mode=query_mode,
    )


def reconcile_fixture_item_state(case: dict[str, object]) -> dict[str, object]:
    items: dict[str, dict[str, object]] = {}
    item_identity_conflicts: set[str] = set()
    reconciliation_conflicts: set[str] = set()
    for page in case["pages"]:
        if "error" in page:
            break
        for observation in expand_page(page):
            merge_observation(
                items,
                observation,
                item_identity_conflicts,
                reconciliation_conflicts,
            )
    expected = case.get("expected_item_state", {})
    return {
        item_id: {
            field: items[item_id].get(field)
            for field in fields
        }
        for item_id, fields in expected.items()
    }


def section(text: str, heading: str) -> str:
    """Return one Markdown section, excluding peer and parent headings."""
    match = re.search(
        rf"(?ms)^{re.escape(heading)}\n(.*?)(?=^#{{1,{heading.count('#')}}} |\Z)",
        text,
    )
    if match is None:
        raise AssertionError(f"missing section: {heading}")
    return match.group(1)


def parse_table(text: str, heading: str) -> list[list[str]]:
    block = section(text, heading)
    lines = [line for line in block.splitlines() if line.startswith("|")]
    if len(lines) < 3:
        raise AssertionError(f"missing Markdown table: {heading}")
    return [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in lines[2:]
    ]


def capability_cell(cell: str) -> frozenset[str]:
    if cell == "none":
        return frozenset()
    return frozenset(re.findall(r"`([a-z_]+)`", cell))


def parse_capability_matrix(text: str) -> dict[str, dict[str, frozenset[str]]]:
    rows = parse_table(text, "## Operation capability matrix")
    return {
        row[0]: {
            "read": capability_cell(row[1]),
            "write": capability_cell(row[2]),
        }
        for row in rows
    }


def parse_retry_side_matrix(
    text: str,
) -> dict[str, dict[str, frozenset[str]]]:
    return {
        row[0]: {
            "read": capability_cell(row[1]),
            "write": capability_cell(row[2]),
        }
        for row in parse_table(text, "## Retry side capability matrix")
    }


EXPECTED_CAPABILITIES = {
    "read": {"read": {"target_issue_or_project_item_read"}, "write": set()},
    "search": {
        "read": {"issue_search", "project_item_read", "project_item_list"},
        "write": set(),
    },
    "status_filtered_list": {
        "read": {"project_item_read", "project_item_list", "status_field_read"},
        "write": set(),
    },
    "create": {
        "read": {"duplicate_discovery", "target_repository_read", "target_project_read", "project_schema_read", "protected_native_metadata_read"},
        "write": {"issue_create", "project_item_add", "requested_field_update"},
    },
    "register_existing_issue": {
        "read": {"issue_read", "duplicate_membership_discovery", "target_project_read", "project_schema_read", "protected_native_metadata_read"},
        "write": {"project_item_add", "requested_field_update"},
    },
    "title_body_edit": {
        "read": {"issue_read", "protected_native_metadata_read"},
        "write": {"issue_title_body_update"},
    },
    "comment": {
        "read": {"issue_read", "protected_native_metadata_read"},
        "write": {"issue_comment_create"},
    },
    "status_priority_due_date": {
        "read": {"project_item_read", "requested_field_read", "protected_native_metadata_read"},
        "write": {"requested_field_update"},
    },
    "done_cancelled": {
        "read": {"issue_state_reason_read", "project_status_read", "protected_native_metadata_read"},
        "write": {"issue_close", "project_status_update"},
    },
    "reopen": {
        "read": {"issue_state_reason_read", "project_status_read", "protected_native_metadata_read"},
        "write": {"issue_reopen", "project_status_update"},
    },
}


EXPECTED_RETRY_SIDES = {
    "issue_create": {
        "read": {"protected_native_metadata_read"},
        "write": {"issue_create"},
    },
    "project_item_add": {
        "read": {"protected_native_metadata_read"},
        "write": {"project_item_add"},
    },
    "requested_fields": {
        "read": {"protected_native_metadata_read"},
        "write": {"requested_field_update"},
    },
    "issue_terminal": {
        "read": {"protected_native_metadata_read"},
        "write": {"issue_close"},
    },
    "project_status": {
        "read": {"protected_native_metadata_read"},
        "write": {"project_status_update"},
    },
    "issue_reopen": {
        "read": {"protected_native_metadata_read"},
        "write": {"issue_reopen"},
    },
}

STATUS_WORDING = {
    "Inbox": {"Inbox", "受信箱", "未整理"},
    "Backlog": {"Backlog", "バックログ", "実施候補"},
    "Ready": {"Ready", "着手可能", "準備完了"},
    "In progress": {"In progress", "進行中", "着手中", "対応中"},
    "Blocked": {"Blocked", "ブロック中", "停止中"},
    "Done": {"Done", "完了", "終了"},
    "Cancelled": {"Cancelled", "Canceled", "中止", "キャンセル"},
}

NON_TERMINAL_REOPEN_STATUSES = frozenset(
    {"Inbox", "Backlog", "Ready", "In progress", "Blocked"}
)


def transition_targets(case: dict[str, object]) -> tuple[object, object, object]:
    operation = case["operation"]
    if operation == "done":
        return "closed", "completed", "Done"
    if operation == "cancelled":
        return "closed", "not planned", "Cancelled"
    if operation != "reopen":
        raise ValueError(f"unknown transition operation: {operation}")
    requested = case["requested_status"]
    if requested is not None and requested not in NON_TERMINAL_REOPEN_STATUSES:
        return None, None, None
    return "open", None, requested or "Backlog"


def run_transition(case: dict[str, object]) -> dict[str, object]:
    target_issue, target_reason, target_status = transition_targets(case)
    if target_issue is None:
        return {
            "target_issue_state": None,
            "target_close_reason": None,
            "target_status": None,
            "first_attempted_sides": [],
            "first_result": "blocked",
            "first_remaining_sides": [],
            "retry_attempted_sides": [],
            "final_result": "blocked",
            "final_remaining_sides": [],
        }
    sides = []
    if (
        case["initial_issue"] != target_issue
        or case.get("initial_close_reason") != target_reason
    ):
        sides.append("issue")
    if case["initial_status"] != target_status:
        sides.append("project_status")
    first_success = set(case["first_success"])
    if not first_success <= set(sides):
        raise AssertionError("first_success must be a subset of readback-derived sides")
    first_remaining = [side for side in sides if side not in first_success]
    retry_attempted = list(first_remaining)
    retry_success = set(case["retry_success"])
    if not retry_success <= set(first_remaining):
        raise AssertionError(
            "retry_success must be a subset of first_remaining"
        )
    final_remaining = [side for side in first_remaining if side not in retry_success]
    return {
        "target_issue_state": target_issue,
        "target_close_reason": target_reason,
        "target_status": target_status,
        "first_attempted_sides": sides,
        "first_result": "complete" if not first_remaining else "partial",
        "first_remaining_sides": first_remaining,
        "retry_attempted_sides": retry_attempted,
        "final_result": "complete" if not final_remaining else "partial",
        "final_remaining_sides": final_remaining,
    }


def duplicate_decision(
    envelope_value: dict[str, object],
    discovery_outcome: str,
) -> dict[str, object]:
    complete = (
        envelope_value["completeness"] == "complete"
        and envelope_value.get("stop_reason") == "source_exhausted"
    )
    if discovery_outcome not in {
        "none",
        "unique_high_confidence",
        "ambiguous_or_multiple",
    }:
        raise ValueError(f"unknown discovery outcome: {discovery_outcome}")
    return {
        "no_duplicate_claim": complete and discovery_outcome == "none",
        "create_allowed": complete and discovery_outcome == "none",
        "reuse_existing": complete and discovery_outcome == "unique_high_confidence",
        "stop": not complete or discovery_outcome == "ambiguous_or_multiple",
    }


def completeness_required_decision(
    *,
    source_exhausted: bool,
    unique_match_count: int,
    hard_stop: bool = False,
) -> dict[str, object]:
    returned_count = min(unique_match_count, 50)
    complete = source_exhausted and not hard_stop
    return {
        "returned_count": returned_count,
        "continue_investigation": not source_exhausted and not hard_stop,
        "completeness": "complete" if complete else "partial",
    }


def status_schema_decision(schema_match_count: int) -> str:
    return "proceed" if schema_match_count == 1 else "stop_schema_ambiguity"


def normalize_status(value: str) -> object:
    for canonical, wording in STATUS_WORDING.items():
        if value in wording:
            return canonical
    return None


def canonical_issue_identity(observation: dict[str, object]) -> object:
    stable_id = observation.get("stable_issue_id")
    if stable_id:
        return str(stable_id)

    issue_url = observation.get("issue_url")
    if issue_url:
        parsed = urlsplit(str(issue_url))
        match = re.fullmatch(
            r"/([^/]+)/([^/]+)/issues/([0-9]+)/?",
            parsed.path,
            flags=re.IGNORECASE,
        )
        if parsed.scheme != "https" or parsed.netloc.casefold() != "github.com":
            return None
        if match is None:
            return None
        owner, repository, number_text = match.groups()
        number = int(number_text)
        if number < 1:
            return None
        return (
            "https://github.com/"
            f"{owner.casefold()}/{repository.casefold()}/issues/{number}"
        )

    owner = observation.get("owner")
    repository = observation.get("repository")
    number_value = observation.get("number")
    if not isinstance(owner, str) or not owner.strip():
        return None
    if not isinstance(repository, str) or not repository.strip():
        return None
    if isinstance(number_value, bool):
        return None
    try:
        number = int(str(number_value))
    except (TypeError, ValueError):
        return None
    if number < 1 or str(number_value).strip().lstrip("0") not in {
        str(number),
        "",
    }:
        return None
    return f"{owner.casefold()}/{repository.casefold()}#{number}"


def write_target_decision(memberships: list[str]) -> dict[str, object]:
    unique_memberships = list(dict.fromkeys(memberships))
    if len(unique_memberships) != 1:
        return {
            "decision": "blocked",
            "canonical_project_item_identity": None,
            "conflict_memberships": unique_memberships,
        }
    return {
        "decision": "proceed",
        "canonical_project_item_identity": unique_memberships[0],
        "conflict_memberships": [],
    }


def completeness_required_traversal(case: dict[str, object]) -> dict[str, object]:
    return reconcile_pages(case)


def field_options(text: str, field: str) -> list[str]:
    """Parse the backtick option names in one Project field subsection."""
    next_field = {
        "Status": r"^`Priority` options:",
        "Priority": r"^`Due date`",
    }[field]
    match = re.search(
        rf"(?ms)^`{re.escape(field)}` options:\n(.*?)(?={next_field})",
        text,
    )
    if match is None:
        raise AssertionError(f"missing field option block: {field}")
    field_text = match.group(1)
    return re.findall(r"(?m)^- `([^`]+)`: ", field_text)


class TaskManagementContractTests(unittest.TestCase):
    def test_checkpoint_recursively_rejects_nested_secret_and_malformed_values(
        self,
    ) -> None:
        result = reconcile_pages(
            {
                "filter": "Ready",
                "pages": [
                    {
                        "incoming_cursor": None,
                        "outgoing_cursor": None,
                        "has_next": False,
                        "items": [
                            {
                                "item_identity": "PVTI-NESTED",
                                "task_identity": "I-NESTED",
                                "status": "Ready",
                                "priority": {
                                    "authentication_token": "NESTED-SECRET",
                                },
                                "due_date": "2026-08-10",
                                "updated_at": [
                                    "malformed",
                                    {
                                        "raw_provider_session": "NESTED-SESSION",
                                    },
                                ],
                                "raw_provider_session": {
                                    "nested": {
                                        "authentication_token": "NESTED-SESSION",
                                    }
                                },
                            }
                        ],
                    }
                ],
            }
        )
        self.assertEqual("partial", result["completeness"])
        self.assertEqual(
            "reconciliation_conflict",
            result["stop_reason"],
        )
        self.assertEqual(1, result["reconciliation_conflict_count"])
        checkpoint = result["continuation_state"]["checkpoint"]
        serialized = json.dumps(checkpoint, sort_keys=True)
        for forbidden in (
            "NESTED-SECRET",
            "NESTED-SESSION",
            "authentication_token",
            "raw_provider_session",
            "malformed",
        ):
            self.assertNotIn(forbidden, serialized)
        self.assertIsNone(checkpoint["items"]["PVTI-NESTED"]["priority"])
        self.assertEqual(
            {},
            checkpoint["field_freshness"]["PVTI-NESTED"],
        )
        malformed_checkpoint = deepcopy(checkpoint)
        malformed_checkpoint["items"]["PVTI-NESTED"]["priority"] = {
            "authentication_token": "NESTED-RESUME-SECRET",
        }
        with self.assertRaisesRegex(AssertionError, "permitted scalar"):
            validate_checkpoint(malformed_checkpoint)

        negative_count = deepcopy(checkpoint)
        negative_count["raw_observation_count"] = -1
        with self.assertRaisesRegex(AssertionError, "non-negative integer"):
            validate_checkpoint(negative_count)

        nested_collection = deepcopy(checkpoint)
        nested_collection["matching_task_identities"] = [
            {"raw_provider_session": "NESTED-COLLECTION-SECRET"}
        ]
        with self.assertRaisesRegex(AssertionError, "normalized strings"):
            validate_checkpoint(nested_collection)
        self.assertIn(
            "recursively type-check",
            read(PROJECTS),
        )

    def test_timestamp_less_clear_blocks_unordered_resurrection(self) -> None:
        for field, initial in (
            ("status", "Ready"),
            ("priority", "P1"),
            ("due_date", "2026-08-10"),
        ):
            with self.subTest(field=field):
                items: dict[str, dict[str, object]] = {}
                identity_conflicts: set[str] = set()
                reconciliation_conflicts: set[str] = set()
                merge_observation(
                    items,
                    {
                        "item_identity": f"PVTI-NO-TIME-{field}",
                        "task_identity": f"I-NO-TIME-{field}",
                        field: initial,
                        "updated_at": "2026-07-31T00:00:00Z",
                    },
                    identity_conflicts,
                    reconciliation_conflicts,
                )
                merge_observation(
                    items,
                    {
                        "item_identity": f"PVTI-NO-TIME-{field}",
                        "task_identity": f"I-NO-TIME-{field}",
                        field: None,
                        "explicit_clear": [field],
                        "updated_at": None,
                    },
                    identity_conflicts,
                    reconciliation_conflicts,
                )
                merge_observation(
                    items,
                    {
                        "item_identity": f"PVTI-NO-TIME-{field}",
                        "task_identity": f"I-NO-TIME-{field}",
                        field: initial,
                        "updated_at": "2026-08-01T00:00:00Z",
                    },
                    identity_conflicts,
                    reconciliation_conflicts,
                )
                item = items[f"PVTI-NO-TIME-{field}"]
                self.assertIsNone(item[field])
                self.assertIn(field, item["_field_tombstones"])
                self.assertIsNone(item["_field_tombstones"][field])
                self.assertIn(
                    f"PVTI-NO-TIME-{field}",
                    reconciliation_conflicts,
                )
        self.assertIn("timestamp-less tombstone", read(PROJECTS))

    def test_continuation_state_is_indivisible_and_cursor_bound(self) -> None:
        source = next(
            case
            for case in fixture("pagination-cases.json")["cases"]
            if case["name"] == "completeness_required_post_50_hard_stop"
        )
        first = completeness_required_traversal(source)
        state = first["continuation_state"]
        self.assertEqual(first["continuation"], state["provider_continuation"])
        self.assertNotIn(
            "provider_cursor",
            json.dumps(state["checkpoint"], sort_keys=True),
        )

        exact = completeness_required_traversal(
            {
                "mode": "completeness_required",
                "filter": "Ready",
                "resume_continuation_state": deepcopy(state),
                "pages": [
                    {
                        "incoming_cursor": state["provider_continuation"],
                        "outgoing_cursor": None,
                        "has_next": False,
                        "generated_unique": {"start": 56, "count": 5},
                    }
                ],
            }
        )
        self.assertEqual("complete", exact["completeness"])
        self.assertTrue(duplicate_decision(exact, "none")["create_allowed"])

        with self.assertRaisesRegex(
            AssertionError,
            "indivisible ContinuationState",
        ):
            completeness_required_traversal(
                {
                    "mode": "completeness_required",
                    "filter": "Ready",
                    "resume_checkpoint": state["checkpoint"],
                    "pages": [
                        {
                            "incoming_cursor": state["provider_continuation"],
                            "outgoing_cursor": None,
                            "has_next": False,
                            "generated_unique": {"start": 56, "count": 5},
                        }
                    ],
                }
            )

        mixed = deepcopy(state)
        mixed["provider_continuation"] = "cursor-WRONG"
        with self.assertRaisesRegex(AssertionError, "association"):
            completeness_required_traversal(
                {
                    "mode": "completeness_required",
                    "filter": "Ready",
                    "resume_continuation_state": mixed,
                    "pages": [
                        {
                            "incoming_cursor": "cursor-WRONG",
                            "outgoing_cursor": None,
                            "has_next": False,
                            "generated_unique": {"start": 56, "count": 5},
                        }
                    ],
                }
            )
        self.assertIn("resume_continuation_state", read(SKILL))
        self.assertIn("must not decompose", read(PROJECTS))

    def test_checkpoint_serialization_is_explicit_and_secret_safe(self) -> None:
        result = reconcile_pages(
            {
                "filter": "Ready",
                "pages": [
                    {
                        "incoming_cursor": None,
                        "outgoing_cursor": None,
                        "has_next": False,
                        "items": [
                            {
                                "item_identity": "PVTI-SAFE",
                                "task_identity": "I-SAFE",
                                "status": "Ready",
                                "priority": "P1",
                                "due_date": "2026-08-10",
                                "updated_at": "2026-07-31T00:00:00Z",
                                "authentication_token_value": "never-copy-token",
                                "raw_provider_session": {
                                    "session": "never-copy-session",
                                },
                                "provider_payload": {
                                    "nested": ["never-copy-payload"],
                                },
                            }
                        ],
                    }
                ],
            }
        )
        checkpoint = result_checkpoint(result)
        serialized = json.dumps(checkpoint, sort_keys=True)
        for forbidden in (
            "authentication_token_value",
            "never-copy-token",
            "raw_provider_session",
            "never-copy-session",
            "provider_payload",
            "never-copy-payload",
            "provider_cursor",
        ):
            self.assertNotIn(forbidden, serialized)
        self.assertEqual(
            {
                "items",
                "field_freshness",
                "field_tombstones",
                "first_seen",
                "item_identity_conflicts",
                "reconciliation_conflicts",
                "membership_conflicts",
                "already_emitted_task_identities",
                "raw_observation_count",
                "deduplicated_observation_count",
                "normalized_filter",
                "query_mode",
                "matching_task_identities",
                "unique_matching_count",
                "display_task_identities",
                "invalidated_task_identities",
            },
            set(checkpoint),
        )
        self.assertEqual(
            {
                "item_identity",
                "task_identity",
                "status",
                "priority",
                "due_date",
            },
            set(checkpoint["items"]["PVTI-SAFE"]),
        )

    def test_explicit_clear_tombstone_prevents_stale_resurrection(self) -> None:
        for field, initial in (
            ("status", "Ready"),
            ("priority", "P1"),
            ("due_date", "2026-08-10"),
        ):
            with self.subTest(field=field):
                items: dict[str, dict[str, object]] = {}
                identity_conflicts: set[str] = set()
                reconciliation_conflicts: set[str] = set()
                merge_observation(
                    items,
                    {
                        "item_identity": f"PVTI-{field}",
                        "task_identity": f"I-{field}",
                        field: initial,
                        "updated_at": "2026-07-31T00:00:00Z",
                    },
                    identity_conflicts,
                    reconciliation_conflicts,
                )
                merge_observation(
                    items,
                    {
                        "item_identity": f"PVTI-{field}",
                        "task_identity": f"I-{field}",
                        field: None,
                        "explicit_clear": [field],
                        "updated_at": "2026-07-31T02:00:00Z",
                    },
                    identity_conflicts,
                    reconciliation_conflicts,
                )
                merge_observation(
                    items,
                    {
                        "item_identity": f"PVTI-{field}",
                        "task_identity": f"I-{field}",
                        field: initial,
                        "updated_at": "2026-07-31T01:00:00Z",
                    },
                    identity_conflicts,
                    reconciliation_conflicts,
                )
                item = items[f"PVTI-{field}"]
                self.assertIsNone(item[field])
                self.assertEqual(
                    "2026-07-31T02:00:00Z",
                    item["_field_updated_at"][field],
                )
                self.assertEqual(
                    "2026-07-31T02:00:00Z",
                    item["_field_tombstones"][field],
                )

    def test_cross_call_membership_conflict_precedes_delivery_suppression(self) -> None:
        first = reconcile_pages(
            {
                "filter": "Ready",
                "pages": [
                    {
                        "incoming_cursor": None,
                        "outgoing_cursor": "cursor-membership",
                        "has_next": True,
                        "generated_unique": {"start": 2, "count": 49},
                        "items": [
                            {
                                "item_identity": "PVTI-X-A",
                                "task_identity": "I-X",
                                "status": "Ready",
                                "updated_at": "2026-07-31T00:00:00Z",
                            }
                        ],
                    }
                ],
            }
        )
        self.assertIn("I-X", first["_returned_task_identities"])
        resumed = reconcile_pages(
            {
                "filter": "Ready",
                "resume_continuation_state": first["continuation_state"],
                "pages": [
                    {
                        "incoming_cursor": first["continuation"],
                        "outgoing_cursor": None,
                        "has_next": False,
                        "items": [
                            {
                                "item_identity": "PVTI-X-B",
                                "task_identity": "I-X",
                                "status": "Ready",
                                "updated_at": "2026-08-01T00:00:00Z",
                            }
                        ],
                    }
                ],
            }
        )
        self.assertEqual("partial", resumed["completeness"])
        self.assertEqual("identity_conflict", resumed["stop_reason"])
        self.assertEqual(1, resumed["identity_conflict_count"])
        self.assertEqual(
            ["PVTI-X-A", "PVTI-X-B"],
            result_checkpoint(resumed)["membership_conflicts"]["I-X"],
        )
        self.assertEqual(
            "blocked",
            write_target_decision(
                result_checkpoint(resumed)["membership_conflicts"]["I-X"]
            )["decision"],
        )

    def test_completeness_required_resume_preserves_aggregate_state(self) -> None:
        source = next(
            case
            for case in fixture("pagination-cases.json")["cases"]
            if case["name"] == "completeness_required_post_50_hard_stop"
        )
        first = completeness_required_traversal(source)
        resumed = completeness_required_traversal(
            {
                "mode": "completeness_required",
                "filter": "Ready",
                "resume_continuation_state": first["continuation_state"],
                "pages": [
                    {
                        "incoming_cursor": first["continuation"],
                        "outgoing_cursor": None,
                        "has_next": False,
                        "generated_unique": {"start": 56, "count": 5},
                    }
                ],
            }
        )
        self.assertEqual(60, resumed["raw_observation_count"])
        self.assertEqual(0, resumed["deduplicated_observation_count"])
        self.assertEqual(60, resumed["unique_task_count"])
        self.assertEqual(50, resumed["returned_count"])
        self.assertEqual(
            [f"I-{number}" for number in range(1, 51)],
            resumed["_returned_task_identities"],
        )
        self.assertEqual("complete", resumed["completeness"])
        self.assertTrue(resumed["truncated"])
        self.assertIsNone(resumed["continuation"])
        self.assertEqual("source_exhausted", resumed["stop_reason"])
        self.assertTrue(
            duplicate_decision(resumed, "none")["create_allowed"]
        )
        self.assertEqual(
            60,
            result_checkpoint(resumed)["raw_observation_count"],
        )
        self.assertEqual(
            60,
            result_checkpoint(resumed)["unique_matching_count"],
        )

    def test_resume_binds_filter_and_reports_invalidated_tasks(self) -> None:
        first = reconcile_pages(
            {
                "filter": "Ready",
                "pages": [
                    {
                        "incoming_cursor": None,
                        "outgoing_cursor": "cursor-invalidate",
                        "has_next": True,
                        "generated_unique": {"start": 2, "count": 49},
                        "items": [
                            {
                                "item_identity": "PVTI-INVALIDATE",
                                "task_identity": "I-INVALIDATE",
                                "status": "Ready",
                                "updated_at": "2026-07-31T00:00:00Z",
                            }
                        ],
                    }
                ],
            }
        )
        self.assertEqual(
            "Ready",
            result_checkpoint(first)["normalized_filter"],
        )
        self.assertEqual(
            "standard_display",
            result_checkpoint(first)["query_mode"],
        )
        with self.assertRaisesRegex(
            AssertionError,
            "normalized Status filter",
        ):
            reconcile_pages(
                {
                    "filter": "Backlog",
                    "resume_continuation_state": first["continuation_state"],
                    "pages": [
                        {
                            "incoming_cursor": first["continuation"],
                            "outgoing_cursor": None,
                            "has_next": False,
                            "items": [],
                        }
                    ],
                }
            )
        with self.assertRaisesRegex(AssertionError, "query mode"):
            reconcile_pages(
                {
                    "mode": "completeness_required",
                    "filter": "Ready",
                    "resume_continuation_state": first["continuation_state"],
                    "pages": [
                        {
                            "incoming_cursor": first["continuation"],
                            "outgoing_cursor": None,
                            "has_next": False,
                            "items": [],
                        }
                    ],
                }
            )

        resumed = reconcile_pages(
            {
                "filter": "Ready",
                "resume_continuation_state": first["continuation_state"],
                "pages": [
                    {
                        "incoming_cursor": first["continuation"],
                        "outgoing_cursor": None,
                        "has_next": False,
                        "items": [
                            {
                                "item_identity": "PVTI-INVALIDATE",
                                "task_identity": "I-INVALIDATE",
                                "status": "Backlog",
                                "updated_at": "2026-08-01T00:00:00Z",
                            }
                        ],
                    }
                ],
            }
        )
        self.assertEqual(
            ["I-INVALIDATE"],
            resumed["invalidated_task_identities"],
        )
        self.assertEqual(
            49,
            result_checkpoint(resumed)["unique_matching_count"],
        )
        self.assertNotIn(
            "I-INVALIDATE",
            result_checkpoint(resumed)["display_task_identities"],
        )

    def test_first_valid_order_uses_first_matching_observation(self) -> None:
        result = reconcile_pages(
            {
                "filter": "Ready",
                "pages": [
                    {
                        "incoming_cursor": None,
                        "outgoing_cursor": None,
                        "has_next": False,
                        "items": [
                            {
                                "item_identity": "PVTI-A",
                                "task_identity": "I-A",
                                "status": "Backlog",
                                "updated_at": "2026-07-31T00:00:00Z",
                            },
                            {
                                "item_identity": "PVTI-B",
                                "task_identity": "I-B",
                                "status": "Ready",
                                "updated_at": "2026-07-31T00:01:00Z",
                            },
                            {
                                "item_identity": "PVTI-A",
                                "task_identity": "I-A",
                                "status": "Ready",
                                "updated_at": "2026-07-31T00:02:00Z",
                            },
                        ],
                    }
                ],
            }
        )
        self.assertEqual(
            ["I-B", "I-A"],
            result["_returned_task_identities"],
        )

    def test_index_keeps_distinct_plan_and_ledger_search_terms(self) -> None:
        lines = read(REPO_ROOT / "knowledge" / "index.md").splitlines()
        plan_index = next(
            index
            for index, line in enumerate(lines)
            if "task-management-hermes-readiness/implementation-plan|" in line
        )
        ledger_index = next(
            index
            for index, line in enumerate(lines)
            if "task-management-hermes-readiness/issues|" in line
        )
        self.assertTrue(lines[plan_index + 1].startswith("  検索語:"))
        self.assertTrue(lines[ledger_index + 1].startswith("  検索語:"))
        self.assertIn("implementation plan", lines[plan_index + 1])
        self.assertIn("Issue ledger", lines[ledger_index + 1])

    def test_requested_status_filter_controls_reconciled_matches(self) -> None:
        cases = {
            case["name"]: case
            for case in fixture("pagination-cases.json")["cases"]
        }
        backlog = reconcile_pages(
            cases["status_and_priority_freshness_are_independent"]
        )
        self.assertEqual(["I-FIELDS"], backlog["_returned_task_identities"])
        self.assertEqual(1, backlog["unique_task_count"])

        ready_then_backlog = {
            "filter": "Ready",
            "pages": [
                {
                    "incoming_cursor": None,
                    "outgoing_cursor": None,
                    "has_next": False,
                    "items": [
                        {
                            "item_identity": "PVTI-STATUS",
                            "task_identity": "I-STATUS",
                            "status": "Ready",
                            "updated_at": "2026-07-31T00:00:00Z",
                        },
                        {
                            "item_identity": "PVTI-STATUS",
                            "task_identity": "I-STATUS",
                            "status": "Backlog",
                            "updated_at": "2026-07-31T01:00:00Z",
                        },
                    ],
                }
            ],
        }
        self.assertEqual(
            [],
            reconcile_pages(ready_then_backlog)["_returned_task_identities"],
        )

    def test_resume_checkpoint_is_lossless_across_identity_and_field_changes(self) -> None:
        source = next(
            case
            for case in fixture("pagination-cases.json")["cases"]
            if case["name"] == "page_would_create_51"
        )
        first = reconcile_pages(source)
        self.assertIn("continuation_state", first)
        checkpoint = result_checkpoint(first)
        self.assertIsInstance(checkpoint, dict)
        self.assertIn("items", checkpoint)
        self.assertIn("field_freshness", checkpoint)
        self.assertIn("already_emitted_task_identities", checkpoint)

        resumed_identity_change = {
            "filter": "Ready",
            "resume_continuation_state": first["continuation_state"],
            "pages": [
                {
                    "incoming_cursor": first["continuation"],
                    "outgoing_cursor": None,
                    "has_next": False,
                    "items": [
                        {
                            "item_identity": "PVTI-1",
                            "task_identity": "I-NEW",
                            "status": "Ready",
                            "updated_at": "2026-08-01T00:00:00Z",
                        }
                    ],
                }
            ],
        }
        identity_result = reconcile_pages(resumed_identity_change)
        self.assertEqual("partial", identity_result["completeness"])
        self.assertEqual(1, identity_result["identity_conflict_count"])
        self.assertNotIn(
            "I-NEW",
            identity_result["_returned_task_identities"],
        )

        field_source = {
            "filter": "Ready",
            "pages": [
                {
                    "incoming_cursor": None,
                    "outgoing_cursor": "cursor-field",
                    "has_next": True,
                    "items": [
                        {
                            "item_identity": "PVTI-FIELD-RESUME",
                            "task_identity": "I-FIELD-RESUME",
                            "status": "Ready",
                            "priority": "P2",
                            "due_date": "2026-08-10",
                            "updated_at": "2026-07-31T00:00:00Z",
                        }
                    ],
                },
                {
                    "incoming_cursor": "cursor-field",
                    "outgoing_cursor": "cursor-after-field",
                    "has_next": True,
                    "generated_unique": {"start": 100, "count": 50},
                },
            ],
        }
        field_first = reconcile_pages(field_source)
        field_resume = {
            "filter": "Ready",
            "resume_continuation_state": field_first["continuation_state"],
            "pages": [
                {
                    "incoming_cursor": field_first["continuation"],
                    "outgoing_cursor": None,
                    "has_next": False,
                    "items": [
                        {
                            "item_identity": "PVTI-FIELD-RESUME",
                            "task_identity": "I-FIELD-RESUME",
                            "status": None,
                            "priority": "P1",
                            "due_date": None,
                            "explicit_clear": ["due_date"],
                            "updated_at": "2026-08-01T00:00:00Z",
                        }
                    ],
                }
            ],
        }
        field_result = reconcile_pages(field_resume)
        resumed_item = result_checkpoint(field_result)["items"][
            "PVTI-FIELD-RESUME"
        ]
        self.assertEqual("Ready", resumed_item["status"])
        self.assertEqual("P1", resumed_item["priority"])
        self.assertIsNone(resumed_item["due_date"])

    def test_due_date_reconciliation_is_independent_and_lossless(self) -> None:
        cases = {
            case["name"]: case
            for case in fixture("pagination-cases.json")["cases"]
        }
        self.assertEqual(
            {
                "PVTI-DUE": {
                    "task_identity": "I-DUE",
                    "status": "Ready",
                    "priority": "P2",
                    "due_date": None,
                }
            },
            reconcile_fixture_item_state(cases["due_date_update_preserve_clear"]),
        )
        due_conflict = reconcile_pages(cases["due_date_unorderable_conflict"])
        self.assertEqual("partial", due_conflict["completeness"])
        self.assertEqual(1, due_conflict["reconciliation_conflict_count"])
        self.assertEqual(0, due_conflict["unique_task_count"])

    def test_ambiguous_project_membership_blocks_project_writes(self) -> None:
        decision = write_target_decision(["PVTI-A", "PVTI-B"])
        self.assertEqual("blocked", decision["decision"])
        self.assertIsNone(decision["canonical_project_item_identity"])
        self.assertEqual(
            ["PVTI-A", "PVTI-B"],
            decision["conflict_memberships"],
        )
        operative = (
            section(read(SKILL), "## Operation routing")
            + section(read(PROJECTS), "## Project item model")
        )
        for operation in ("field", "terminal", "reopen"):
            self.assertIn(operation, operative.lower())
        self.assertIn(
            "all Project field, terminal, and reopen writes stop",
            " ".join(operative.split()),
        )

    def test_completeness_required_traversal_executes_all_pages(self) -> None:
        cases = {
            case["name"]: case
            for case in fixture("pagination-cases.json")["cases"]
        }
        for name in (
            "completeness_required_over_50_exhausted",
            "completeness_required_post_50_hard_stop",
        ):
            with self.subTest(case=name):
                case = cases[name]
                actual = completeness_required_traversal(case)
                returned = actual.pop("_returned_task_identities")
                continuation_state = actual.pop("continuation_state")
                checkpoint = continuation_state["checkpoint"]
                self.assertEqual(case["expected"], actual)
                self.assertEqual(
                    case["expected_returned"],
                    {"first": returned[0], "last": returned[-1]},
                )
                self.assertLessEqual(len(returned), 50)
                self.assertEqual(
                    case["expected_create_allowed"],
                    duplicate_decision(actual, "none")["create_allowed"],
                )
                self.assertEqual(
                    case["expected_checkpoint_cursor"],
                    actual["continuation"],
                )
                self.assertNotIn("provider_cursor", checkpoint)

    def test_skill_declares_portable_inputs_outputs_and_capabilities(self) -> None:
        text = read(SKILL)
        inputs = section(text, "## Inputs")
        outputs = section(text, "## Outputs")
        capabilities = section(text, "## Required Capabilities")
        for required in (
            "project_url",
            "inbox_repository",
            "operation",
            "Status filter",
            "continuation",
            "checkpoint",
        ):
            self.assertIn(required, inputs)
        for required in (
            "`complete`",
            "`partial`",
            "`blocked`",
            "remaining",
            "recovery",
        ):
            self.assertIn(required, outputs)
        for required in (
            "operation-scoped",
            "semantic",
            "exact readback",
            "protected native metadata",
        ):
            self.assertIn(required, capabilities)

    def test_execution_ledger_exists_and_is_discoverable(self) -> None:
        self.assertTrue(HERMES_READINESS_LEDGER.is_file())
        ledger = read(HERMES_READINESS_LEDGER)
        for required in (
            "338e0c1e192949c352a1fdd6deec1231ad495f19b68729e2aff3f330356ced4f",
            "088b91669813649363ddda28ea3d45387b92dbc3",
            "Execution Plan Gate",
            "whole-branch",
            "Task 6",
            "merged revision",
            "push",
            "PR",
            "Companies",
            "live",
        ):
            self.assertIn(required, ledger)
        self.assertIn(
            "task-management-hermes-readiness/issues",
            read(REPO_ROOT / "knowledge" / "index.md"),
        )

    def test_canonical_issue_identity_normalizes_case_and_decimal_number(self) -> None:
        self.assertEqual(
            "https://github.com/octocat/tasks/issues/7",
            canonical_issue_identity(
                {
                    "issue_url": (
                        "https://github.com/OctoCat/Tasks/issues/0007/"
                        "?notification=1#discussion"
                    )
                }
            ),
        )
        self.assertEqual(
            "octocat/tasks#7",
            canonical_issue_identity(
                {
                    "owner": "OctoCat",
                    "repository": "TASKS",
                    "number": "0007",
                }
            ),
        )
        self.assertEqual(
            "ISSUE_kwDOStable",
            canonical_issue_identity(
                {
                    "stable_issue_id": "ISSUE_kwDOStable",
                    "issue_url": "https://github.com/other/repo/issues/2",
                }
            ),
        )
        for incomplete in (
            {"owner": "octocat", "number": 7},
            {"repository": "tasks", "number": 7},
            {"owner": "octocat", "repository": "tasks", "number": "seven"},
            {"issue_url": "https://example.com/octocat/tasks/issues/7"},
            {"title": "mutable display identity"},
        ):
            with self.subTest(incomplete=incomplete):
                self.assertIsNone(canonical_issue_identity(incomplete))

        contract = " ".join(
            section(read(CORE), "## Canonical identity").lower().split()
        )
        for required in (
            "casefold",
            "decimal integer representation",
            "partial",
            "do not deduplicate",
            "do not write",
            "title",
            "mutable display",
        ):
            self.assertIn(required.lower(), contract)

    def test_every_supported_mutation_preserves_native_metadata(self) -> None:
        expected_operations = {
            "register_existing_issue",
            "edit_title",
            "edit_body",
            "comment",
            "status",
            "priority",
            "due_date",
            "done",
            "cancelled",
            "reopen",
        }
        protected_keys = {
            "assignees",
            "labels",
            "milestone",
            "issue_type",
            "parent_issue",
            "sub_issues",
        }
        observed = set()
        for case in fixture("native-metadata-cases.json")["cases"]:
            observed.add(case["operation"])
            with self.subTest(operation=case["operation"]):
                actual = apply_requested_change(
                    case["before"],
                    case["requested_change"],
                )
                self.assertEqual(case["after"], actual)
                self.assertEqual(
                    case["before"]["protected"],
                    actual["protected"],
                )
                self.assertEqual(
                    case["after"]["protected"],
                    actual["protected"],
                )
                self.assertEqual(protected_keys, set(actual["protected"]))
        self.assertEqual(expected_operations, observed)

        operative = "\n".join(
            (
                section(read(SKILL), "## Boundaries"),
                section(read(SKILL), "## Operation routing"),
                section(read(PROJECTS), "## Project item model"),
                section(read(PROJECTS), "## Fields"),
                section(read(PROJECTS), "## Terminal transitions"),
                section(read(PROJECTS), "## Reopen"),
                section(read(ISSUES), "## Duplicate handling"),
                section(read(SAFETY), "## Partial success"),
            )
        )
        for operation in expected_operations:
            self.assertIn(f"`{operation}`", operative)
        for protected_key in protected_keys:
            self.assertIn(f"`{protected_key}`", operative)
        self.assertIn(
            "Every supported mutation requires exact readback of the requested "
            "fields and all protected native metadata",
            " ".join(operative.split()),
        )
        self.assertIn(
            "If protected native metadata readback is unavailable, return "
            "`partial`; never report the mutation as `complete`",
            " ".join(operative.split()),
        )

    def test_portable_contract_forbids_secret_values_not_pagination_terms(self) -> None:
        production = "\n".join(
            read(path)
            for path in [SKILL, *sorted((SKILL_ROOT / "references").glob("*.md"))]
        )
        self.assertIn("continuation token", production)
        self.assertIn(
            "Do not store or return credential, secret, or authentication token values",
            production,
        )
        for prohibited in (
            "credential_value",
            "secret_value",
            "authentication_token_value",
            "raw_profile_dump",
        ):
            self.assertNotIn(prohibited, production)
        self.assertIn("Do not fall back to a CLI", production)

    def test_transition_fixtures_execute_complete_partial_and_retry(self) -> None:
        for case in fixture("transition-cases.json")["cases"]:
            with self.subTest(case=case["name"]):
                self.assertEqual(case["expected"], run_transition(case))

    def test_reopen_target_allowlist_blocks_terminal_and_unknown_values(self) -> None:
        self.assertEqual(
            {"Inbox", "Backlog", "Ready", "In progress", "Blocked"},
            set(NON_TERMINAL_REOPEN_STATUSES),
        )
        cases = fixture("transition-cases.json")["cases"]
        blocked = {
            case["name"]: run_transition(case)
            for case in cases
            if case["name"] in {
                "invalid_terminal_reopen",
                "invalid_done_reopen",
                "unknown_reopen_target",
            }
        }
        self.assertEqual(
            {
                "invalid_terminal_reopen",
                "invalid_done_reopen",
                "unknown_reopen_target",
            },
            set(blocked),
        )
        for result in blocked.values():
            self.assertEqual("blocked", result["first_result"])
            self.assertEqual([], result["first_attempted_sides"])
            self.assertEqual([], result["retry_attempted_sides"])

    def test_transition_rejects_invalid_operation_and_retry_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown transition operation"):
            transition_targets(
                {
                    "operation": "reopne",
                    "requested_status": "Ready",
                }
            )

        with self.assertRaisesRegex(
            AssertionError,
            "retry_success must be a subset of first_remaining",
        ):
            run_transition(
                {
                    "operation": "done",
                    "initial_issue": "open",
                    "initial_status": "In progress",
                    "requested_status": None,
                    "first_success": ["issue"],
                    "retry_success": ["issue"],
                }
            )

    def test_terminal_and_reopen_contract_names_state_machine_outputs(self) -> None:
        text = read(SKILL) + "\n" + read(PROJECTS) + "\n" + read(SAFETY)
        for required in (
            "bare reopen",
            "`Backlog`",
            "completed",
            "not planned",
            "first_remaining_sides",
            "retry_attempted_sides",
            "remaining side only",
            "exact readback",
            "do not roll back",
        ):
            self.assertIn(required, text)

        terminal = section(read(PROJECTS), "## Terminal transitions")
        self.assertIn("`Done` maps to Issue close reason `completed`", terminal)
        self.assertIn("`Cancelled` maps to Issue close reason `not planned`", terminal)
        self.assertIn(
            "Per-side result and exact readback identify completed work",
            terminal,
        )
        self.assertIn(
            "`first_remaining_sides` contains unfinished sides only",
            terminal,
        )
        self.assertNotIn("`Done` maps to Issue close reason `not planned`", terminal)
        self.assertNotIn("`Cancelled` maps to Issue close reason `completed`", terminal)

        reopen = section(read(PROJECTS), "## Reopen")
        self.assertEqual(
            ["Backlog"],
            re.findall(r"bare reopen defaults to `([^`]+)`", reopen),
        )
        for required in (
            "Issue state and Project Status are two sides of one logical operation",
            "bare reopen",
            "`Backlog`",
            "`Inbox`, `Backlog`, `Ready`, `In progress`, and `Blocked`",
            "before either side is attempted",
            "first_remaining_sides",
            "retry_attempted_sides",
            "remaining side only",
            "exact readback",
            "do not roll back",
        ):
            self.assertIn(required, reopen)
        for contradiction in (
            "bare reopen defaults to `Inbox`",
            "retry both sides",
            "roll back the successful side",
            "partial success is complete",
        ):
            self.assertNotIn(contradiction, reopen)

        partial = section(read(SAFETY), "## Partial success")
        self.assertIn(
            "Per-side result and exact readback identify completed work",
            partial,
        )
        self.assertIn(
            "`first_remaining_sides` contains unfinished sides only",
            partial,
        )
        contradiction = re.compile(
            r"(?im)^(?:-\s*)?(?:retry both sides|"
            r"roll back the successful side|"
            r"(?:a |two-side )?partial success is complete)\b"
        )
        for operative in (terminal, reopen, partial):
            self.assertIsNone(contradiction.search(operative))

    def test_pagination_fixtures_match_exact_counts_conflicts_and_continuation(self) -> None:
        for case in fixture("pagination-cases.json")["cases"]:
            with self.subTest(case=case["name"]):
                actual = reconcile_pages(case)
                actual.pop("_returned_task_identities")
                actual.pop("continuation_state")
                self.assertEqual(case["expected"], actual)
                if "expected_item_state" in case:
                    self.assertEqual(
                        case["expected_item_state"],
                        reconcile_fixture_item_state(case),
                    )

    def test_reconciliation_tracks_freshness_per_field(self) -> None:
        cases = {
            case["name"]: case
            for case in fixture("pagination-cases.json")["cases"]
        }
        self.assertEqual(
            {
                "PVTI-FRESH": {
                    "task_identity": "I-FRESH",
                    "status": "Ready",
                }
            },
            reconcile_fixture_item_state(
                cases["same_value_advances_field_freshness"]
            ),
        )
        self.assertEqual(
            {
                "PVTI-FIELDS": {
                    "task_identity": "I-FIELDS",
                    "status": "Backlog",
                    "priority": "P2",
                }
            },
            reconcile_fixture_item_state(
                cases["status_and_priority_freshness_are_independent"]
            ),
        )

    def test_unique_51_two_call_continuation_is_lossless(self) -> None:
        source = next(
            case
            for case in fixture("pagination-cases.json")["cases"]
            if case["name"] == "page_would_create_51"
        )
        first = reconcile_pages(source)
        first_identities = first.pop("_returned_task_identities")
        continuation_state = first.pop("continuation_state")
        self.assertEqual([f"I-{number}" for number in range(1, 50)], first_identities)
        self.assertEqual(52, first["raw_observation_count"])
        self.assertEqual(49, first["unique_task_count"])
        self.assertEqual("partial", first["completeness"])
        self.assertEqual("cursor-2", first["continuation"])

        second_case = {
            "filter": "Ready",
            "resume_continuation_state": continuation_state,
            "pages": [source["pages"][1]],
        }
        second = reconcile_pages(second_case)
        second_identities = second.pop("_returned_task_identities")
        second.pop("continuation_state")
        self.assertEqual(["I-50", "I-51"], second_identities)
        self.assertEqual(
            {
                "raw_observation_count": 3,
                "deduplicated_observation_count": 1,
                "identity_conflict_count": 0,
                "reconciliation_conflict_count": 0,
                "unique_task_count": 2,
                "returned_count": 2,
                "task_order": ["I-50", "I-51"],
                "completeness": "complete",
                "truncated": False,
                "continuation": None,
                "stop_reason": "source_exhausted",
            },
            second,
        )
        combined = first_identities + second_identities
        self.assertEqual([f"I-{number}" for number in range(1, 52)], combined)
        self.assertEqual(51, len(set(combined)))
        self.assertEqual(1, combined.count("I-1"))

    def test_identity_and_lossless_page_boundary_are_explicit(self) -> None:
        text = " ".join((read(CORE) + "\n" + read(PROJECTS)).split())
        for required in (
            "canonical_task_identity",
            "canonical_project_item_identity",
            "stable Issue ID",
            "canonical Issue URL",
            "owner/repository#number",
            "whole page",
            "incoming cursor",
            "do not consume",
            "unique_limit_page_deferred",
            "must not synthesize an intra-page offset",
            "already_emitted_task_identities",
            "raw observations fetched and inspected",
        ):
            self.assertIn(required, text)

    def test_status_wording_and_schema_ambiguity_contract(self) -> None:
        status_text = section(read(PROJECTS), "## Status normalization")
        rows = parse_table(read(PROJECTS), "## Status normalization")
        actual = {
            row[0].strip("`"): {
                value.strip().strip("`")
                for value in row[1].split(",")
            }
            for row in rows
        }
        self.assertEqual(STATUS_WORDING, actual)
        self.assertEqual("stop_schema_ambiguity", status_schema_decision(0))
        self.assertEqual("proceed", status_schema_decision(1))
        self.assertEqual("stop_schema_ambiguity", status_schema_decision(2))
        self.assertIn(
            "A missing option, duplicate option, or other schema ambiguity "
            "must stop the operation",
            " ".join(status_text.split()),
        )
        for contradiction in (
            "may choose the closest",
            "may continue on schema ambiguity",
            "schema ambiguity does not stop",
        ):
            self.assertNotIn(contradiction, status_text.lower())

    def test_duplicate_discovery_requires_complete_exhaustion(self) -> None:
        partial = {"completeness": "partial", "stop_reason": "permission_failure"}
        complete = {"completeness": "complete", "stop_reason": "source_exhausted"}
        expected = {
            ("partial", "none"): {
                "no_duplicate_claim": False,
                "create_allowed": False,
                "reuse_existing": False,
                "stop": True,
            },
            ("complete", "none"): {
                "no_duplicate_claim": True,
                "create_allowed": True,
                "reuse_existing": False,
                "stop": False,
            },
            ("complete", "unique_high_confidence"): {
                "no_duplicate_claim": False,
                "create_allowed": False,
                "reuse_existing": True,
                "stop": False,
            },
            ("complete", "ambiguous_or_multiple"): {
                "no_duplicate_claim": False,
                "create_allowed": False,
                "reuse_existing": False,
                "stop": True,
            },
        }
        self.assertEqual(expected[("partial", "none")], duplicate_decision(partial, "none"))
        for outcome in ("none", "unique_high_confidence", "ambiguous_or_multiple"):
            self.assertEqual(
                expected[("complete", outcome)],
                duplicate_decision(complete, outcome),
            )
        for outcome in ("none", "unique_high_confidence", "ambiguous_or_multiple"):
            decision = duplicate_decision(
                {
                    "completeness": "complete",
                    "truncated": True,
                    "stop_reason": "unique_limit_reached",
                },
                outcome,
            )
            self.assertFalse(decision["create_allowed"])
            self.assertTrue(decision["stop"])
        with self.assertRaises(ValueError):
            duplicate_decision(complete, "zero_or_more")

        duplicate_text = section(read(ISSUES), "## Duplicate handling")
        decision_rows = parse_table(
            read(ISSUES),
            "### Duplicate discovery decision matrix",
        )
        self.assertEqual(
            [
                ["`complete` / `source_exhausted`", "`none`", "true", "true", "false", "proceed to create"],
                ["`complete` / `source_exhausted`", "`unique_high_confidence`", "false", "false", "true", "reuse existing"],
                ["`complete` / `source_exhausted`", "`ambiguous_or_multiple`", "false", "false", "false", "stop"],
                ["`partial` or `truncated`", "any", "false", "false", "false", "stop"],
            ],
            decision_rows,
        )
        for contradiction in (
            "partial discovery may create",
            "truncated discovery may create",
            "multiple matches may create",
            "ambiguous discovery may create",
        ):
            self.assertNotIn(contradiction, duplicate_text.lower())

        pagination_text = section(read(PROJECTS), "## Completeness envelope")
        mode_rows = parse_table(
            read(PROJECTS),
            "### Query mode decision matrix",
        )
        self.assertEqual(
            [
                ["standard display", "50 unique matches before exhaustion", "stop the call", "`partial`", "at most 50"],
                ["completeness-required", "50 unique matches before exhaustion", "continue investigation", "`partial`", "at most 50"],
                ["completeness-required", "provider continuation available", "follow the opaque continuation", "`partial`", "at most 50"],
                ["any", "raw source exhausted without conflicts", "stop", "`complete`", "at most 50"],
                ["any", "hard stop or conflict", "stop and preserve results", "`partial`", "at most 50"],
            ],
            mode_rows,
        )
        self.assertEqual(
            {
                "returned_count": 50,
                "continue_investigation": True,
                "completeness": "partial",
            },
            completeness_required_decision(
                source_exhausted=False,
                unique_match_count=50,
            ),
        )
        self.assertEqual(
            {
                "returned_count": 50,
                "continue_investigation": True,
                "completeness": "partial",
            },
            completeness_required_decision(
                source_exhausted=False,
                unique_match_count=73,
            ),
        )
        self.assertEqual(
            {
                "returned_count": 50,
                "continue_investigation": False,
                "completeness": "complete",
            },
            completeness_required_decision(
                source_exhausted=True,
                unique_match_count=73,
            ),
        )
        self.assertEqual(
            {
                "returned_count": 50,
                "continue_investigation": False,
                "completeness": "partial",
            },
            completeness_required_decision(
                source_exhausted=False,
                unique_match_count=73,
                hard_stop=True,
            ),
        )
        for contradiction in (
            "50 unique matches proves complete",
            "50 results means complete",
            "stop the investigation at 50",
            "duplicate discovery may stop at 50",
        ):
            self.assertNotIn(contradiction, pagination_text.lower())

    def test_standalone_structure_and_frontmatter(self) -> None:
        actual_files = {
            path.relative_to(SKILL_ROOT).as_posix()
            for path in SKILL_ROOT.rglob("*")
            if path.is_file()
        }
        self.assertEqual(EXPECTED_FILES, actual_files)
        self.assertFalse((REPO_ROOT / "plugins" / "task-management").exists())
        text = read(SKILL)
        self.assertTrue(text.startswith("---\nname: task-management\n"))
        self.assertIn("description:", text.split("---", 2)[1])

    def test_core_is_caller_owned_and_issue_backed(self) -> None:
        text = read(SKILL) + "\n" + read(CORE)
        for required in (
            "project_url",
            "inbox_repository",
            "one canonical default Project",
            "GitHub Issue",
            "repository is the work unit boundary",
            "GitHub MCP",
        ):
            self.assertIn(required, text)

    def test_skill_has_no_host_specific_or_runtime_surface(self) -> None:
        production = [
            SKILL,
            *sorted((SKILL_ROOT / "references").glob("*.md")),
        ]
        text = "\n".join(read(path) for path in production)
        for prohibited in (
            "Hermes",
            "Codex",
            "task-management-read",
            "task_adapter__",
            "work_unit_id",
        ):
            self.assertNotIn(prohibited, text)
        self.assertFalse((SKILL_ROOT / "agents").exists())
        self.assertFalse((SKILL_ROOT / "plugin.yaml").exists())
        self.assertFalse((SKILL_ROOT / ".codex-plugin").exists())
        production_python = [
            path
            for path in SKILL_ROOT.rglob("*.py")
            if "tests" not in path.parts
        ]
        self.assertEqual([], production_python)

    def test_reference_router_is_complete(self) -> None:
        skill_text = read(SKILL)
        for name in (
            "core.md",
            "github-projects.md",
            "issue-contract.md",
            "safety-and-failures.md",
        ):
            self.assertIn(f"references/{name}", skill_text)
            self.assertTrue((SKILL_ROOT / "references" / name).is_file())

    def test_target_resolution_is_ordered_and_ambiguity_stops(self) -> None:
        text = read(CORE)
        project_section = text.split("## Project resolution order", 1)[1].split(
            "## Repository resolution order", 1
        )[0]
        repository_section = text.split("## Repository resolution order", 1)[1].split(
            "## Read and write identity", 1
        )[0]
        project_steps = (
            "Invocation `project_url`",
            "Caller default `project_url`",
            "Session-established Project",
            "Unique open Project discovery",
            "Ask the user",
        )
        repository_steps = (
            "Explicit repository",
            "Current repository",
            "Unique referenced repository",
            "Configured inbox",
            "Ask the user",
        )
        for section, steps in (
            (project_section, project_steps),
            (repository_section, repository_steps),
        ):
            positions = [section.index(step) for step in steps]
            self.assertEqual(sorted(positions), positions)
        self.assertIn("Never use inbox as an ambiguity fallback", text)

    def test_issue_and_project_fields_are_exact(self) -> None:
        project_text = read(PROJECTS)
        issue_text = read(ISSUES)
        self.assertEqual(
            [
                "Inbox",
                "Backlog",
                "Ready",
                "In progress",
                "Blocked",
                "Done",
                "Cancelled",
            ],
            field_options(project_text, "Status"),
        )
        self.assertEqual(
            ["P0", "P1", "P2", "P3"],
            field_options(project_text, "Priority"),
        )
        self.assertIn("`Due date` is optional.", project_text)
        due_date = project_text.split("`Due date` is optional.", 1)[1].split(
            "## Terminal transitions", 1
        )[0]
        self.assertIn("Leave it empty", due_date)
        self.assertIn("close reason `completed`", project_text)
        self.assertIn("close reason `not planned`", project_text)
        for heading in (
            "## Outcome",
            "## Context",
            "## Acceptance criteria",
            "## References",
        ):
            self.assertIn(heading, issue_text)

    def test_operation_routing_is_classified_before_capabilities(self) -> None:
        text = read(SKILL)
        routing = section(text, "## Operation routing")
        self.assertIn("For every operation", routing)
        self.assertLess(
            routing.index("Classify the requested operation"),
            routing.index("For every operation"),
        )

        read_flow = section(text, "### Read, search, and list")
        for prohibited_write in (
            "create or edit an Issue",
            "add a comment",
            "close an Issue",
            "add an Issue to a Project",
            "update a Project field",
        ):
            self.assertIn(prohibited_write, read_flow)
        self.assertIn("Resolve only the query scope needed to answer", read_flow)
        self.assertIn("Return only read results", read_flow)

        create_flow = section(text, "### Create and register")
        self.assertIn("Only this operation uses the new-task flow", create_flow)
        self.assertIn("newly created Project item", create_flow)
        self.assertIn("Status=Inbox", create_flow)
        self.assertIn("Priority=P2", create_flow)
        self.assertIn("no due date", create_flow)

        edit_flow = section(text, "### Edit")
        self.assertIn("only the explicitly requested Issue properties", edit_flow)
        self.assertIn("Do not add Project membership", edit_flow)
        self.assertIn("Do not apply creation defaults", edit_flow)

        comment_flow = section(text, "### Comment")
        self.assertIn("only the requested comment", comment_flow)
        self.assertIn("Do not add Project membership", comment_flow)
        self.assertIn("Do not apply creation defaults", comment_flow)

        field_flow = section(text, "### Non-terminal field update")
        self.assertIn("only the explicitly requested field values", field_flow)
        self.assertIn("Do not change any unrequested field", field_flow)

        terminal_flow = section(text, "### Terminal update")
        self.assertIn("explicit terminal instruction", terminal_flow)
        self.assertIn("Do not ask twice", terminal_flow)
        self.assertIn("inferred terminal transition", terminal_flow)
        self.assertIn("confirmation", terminal_flow)

    def test_operation_capability_matrix_matches_every_approved_row(self) -> None:
        actual = parse_capability_matrix(read(PROJECTS))
        normalized = {
            operation: {name: set(values) for name, values in groups.items()}
            for operation, groups in actual.items()
        }
        self.assertEqual(EXPECTED_CAPABILITIES, normalized)
        self.assertEqual(
            EXPECTED_RETRY_SIDES,
            {
                side: {
                    group: set(values)
                    for group, values in requirements.items()
                }
                for side, requirements in parse_retry_side_matrix(
                    read(PROJECTS)
                ).items()
            },
        )

    def test_issue_only_operations_require_only_their_resolved_targets(self) -> None:
        capability_check = section(read(PROJECTS), "## Semantic capability check")
        matrix = parse_capability_matrix(read(PROJECTS))
        self.assertNotIn(
            "access to the resolved owner, repository, Project",
            capability_check,
        )
        self.assertIn(
            "Require access only to the targets resolved by that operation.",
            capability_check,
        )
        self.assertEqual(
            {"issue_read", "protected_native_metadata_read"},
            set(matrix["comment"]["read"]),
        )
        self.assertEqual(
            {"issue_read", "protected_native_metadata_read"},
            set(matrix["title_body_edit"]["read"]),
        )
        self.assertIn("project_item_read", matrix["status_priority_due_date"]["read"])
        self.assertIn("target_project_read", matrix["create"]["read"])

    def test_operation_scoped_cases_derive_requirements_from_markdown(self) -> None:
        matrix = parse_capability_matrix(read(PROJECTS))
        retry = parse_retry_side_matrix(read(PROJECTS))
        for case in fixture("operation-capability-cases.json")["cases"]:
            with self.subTest(operation=case["operation"], sides=case["remaining_sides"]):
                operation = matrix[case["operation"]]
                required = set(operation["read"])
                if case["remaining_sides"]:
                    for side in case["remaining_sides"]:
                        required.update(retry[side]["read"])
                        required.update(retry[side]["write"])
                else:
                    required.update(operation["write"])
                missing = sorted(required - set(case["available"]))
                self.assertEqual(case["expected_missing"], missing)

    def test_reuse_and_partial_failure_preserve_existing_state(self) -> None:
        issue_text = section(read(ISSUES), "## Duplicate handling")
        self.assertIn("never create a second Issue", issue_text)
        self.assertIn("Preserve its current fields", issue_text)
        self.assertIn("requested operation", issue_text)
        self.assertIn("documented unfinished partial-failure step", issue_text)

        partial_failure = section(read(SAFETY), "## Partial success")
        self.assertIn("continue only the unfinished steps", partial_failure.lower())
        self.assertIn("Do not reset completed or current fields", partial_failure)
        self.assertIn("Do not create a duplicate Issue", partial_failure)

    def test_approval_policy_distinguishes_safe_uncertain_and_destructive(self) -> None:
        text = read(SAFETY)
        for required in (
            "High-confidence safe single-item writes run automatically",
            "Uncertain target or content requires confirmation",
            "Destructive or bulk mutation requires confirmation",
            "An explicit user instruction is the approval for that exact operation",
            "Do not ask twice",
        ):
            self.assertIn(required, text)

    def test_capability_and_partial_failures_are_fail_closed(self) -> None:
        text = read(PROJECTS) + "\n" + read(SAFETY)
        for required in (
            "## Operation capability matrix",
            "## Retry side capability matrix",
            "Do not fall back to a CLI, direct API client, browser automation, or local backend",
            "Do not delete the created Issue",
            "Continue only the unfinished steps",
            "Do not create a duplicate Issue",
        ):
            self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
