import json
from copy import deepcopy
from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "task-management"
SKILL = SKILL_ROOT / "SKILL.md"
CORE = SKILL_ROOT / "references" / "core.md"
PROJECTS = SKILL_ROOT / "references" / "github-projects.md"
ISSUES = SKILL_ROOT / "references" / "issue-contract.md"
SAFETY = SKILL_ROOT / "references" / "safety-and-failures.md"
FIXTURES = SKILL_ROOT / "tests" / "fixtures"

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


def merge_observation(
    items: dict[str, dict[str, object]],
    observation: dict[str, object],
    item_identity_conflicts: set[str],
    reconciliation_conflicts: set[str],
) -> bool:
    item_id = str(observation["item_identity"])
    current = items.get(item_id)
    if current is None:
        initial = deepcopy(observation)
        explicit_clear = set(observation.get("explicit_clear", []))
        initial["_field_updated_at"] = {
            field: observation.get("updated_at")
            for field in ("status", "priority")
            if (
                field in observation
                and (
                    observation[field] is not None
                    or field in explicit_clear
                )
            )
        }
        items[item_id] = initial
        return False
    if current["task_identity"] != observation["task_identity"]:
        item_identity_conflicts.add(item_id)
        return True
    explicit_clear = set(observation.get("explicit_clear", []))
    field_updated_at = current.setdefault("_field_updated_at", {})
    for field in ("status", "priority"):
        if field in explicit_clear:
            current[field] = None
            field_updated_at[field] = observation.get("updated_at")
            continue
        if field not in observation:
            continue
        incoming = observation[field]
        existing = current.get(field)
        if incoming is None:
            continue
        old_time = field_updated_at.get(field)
        new_time = observation.get("updated_at")
        if incoming == existing:
            if (
                new_time is not None
                and (old_time is None or str(new_time) >= str(old_time))
            ):
                field_updated_at[field] = new_time
            continue
        if existing is None:
            current[field] = incoming
            field_updated_at[field] = new_time
            continue
        if old_time is not None and new_time is not None:
            if str(new_time) >= str(old_time):
                current[field] = incoming
                field_updated_at[field] = new_time
        else:
            reconciliation_conflicts.add(item_id)
    return True


def envelope(
    *,
    items: dict[str, dict[str, object]],
    first_seen: dict[str, int],
    raw_count: int,
    duplicate_count: int,
    item_identity_conflicts: set[str],
    reconciliation_conflicts: set[str],
    already_emitted: set[str],
    continuation: object,
    completeness: str,
    truncated: bool,
    stop_reason: str,
) -> dict[str, object]:
    task_memberships: dict[str, list[str]] = {}
    for item_id, item in items.items():
        if (
            item_id in item_identity_conflicts
            or item_id in reconciliation_conflicts
            or item.get("status") != "Ready"
        ):
            continue
        task_id = str(item["task_identity"])
        if task_id in already_emitted:
            continue
        task_memberships.setdefault(task_id, []).append(item_id)
    identity_conflicts = {
        task for task, memberships in task_memberships.items() if len(memberships) > 1
    }
    ordered = sorted(task_memberships, key=lambda task: first_seen[task])
    result_order: object = ordered
    if len(ordered) >= 49:
        result_order = {"first": ordered[0], "last": ordered[-1]}
    if reconciliation_conflicts:
        completeness = "partial"
        stop_reason = "reconciliation_conflict"
    elif item_identity_conflicts or identity_conflicts:
        completeness = "partial"
        stop_reason = "identity_conflict"
    return {
        "raw_observation_count": raw_count,
        "deduplicated_observation_count": duplicate_count,
        "identity_conflict_count": len(item_identity_conflicts) + len(identity_conflicts),
        "reconciliation_conflict_count": len(reconciliation_conflicts),
        "unique_task_count": len(ordered),
        "returned_count": len(ordered),
        "task_order": result_order,
        "completeness": completeness,
        "truncated": truncated,
        "continuation": continuation,
        "stop_reason": stop_reason,
        "_returned_task_identities": ordered,
    }


def reconcile_pages(case: dict[str, object]) -> dict[str, object]:
    items: dict[str, dict[str, object]] = {}
    first_seen: dict[str, int] = {}
    raw_count = 0
    duplicate_count = 0
    item_identity_conflicts: set[str] = set()
    reconciliation_conflicts: set[str] = set()
    already_emitted = set(case.get("already_emitted_task_identities", []))
    sequence = 0
    for page in case["pages"]:
        incoming = page.get("incoming_cursor")
        if "error" in page:
            return envelope(
                items=items,
                first_seen=first_seen,
                raw_count=raw_count,
                duplicate_count=duplicate_count,
                item_identity_conflicts=item_identity_conflicts,
                reconciliation_conflicts=reconciliation_conflicts,
                already_emitted=already_emitted,
                continuation=incoming,
                completeness="partial",
                truncated=False,
                stop_reason=str(page["error"]),
            )
        candidate_items = deepcopy(items)
        candidate_first_seen = dict(first_seen)
        candidate_identity_conflicts = set(item_identity_conflicts)
        candidate_conflicts = set(reconciliation_conflicts)
        candidate_raw = raw_count
        candidate_duplicates = duplicate_count
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
        valid_tasks = {
            str(item["task_identity"])
            for item_id, item in candidate_items.items()
            if (
                item_id not in candidate_identity_conflicts
                and item_id not in candidate_conflicts
                and item.get("status") == "Ready"
            )
        }
        for observation in observations:
            task_id = str(observation["task_identity"])
            if task_id in valid_tasks and task_id not in candidate_first_seen:
                candidate_first_seen[task_id] = sequence
                sequence += 1
        candidate = envelope(
            items=candidate_items,
            first_seen=candidate_first_seen,
            raw_count=candidate_raw,
            duplicate_count=candidate_duplicates,
            item_identity_conflicts=candidate_identity_conflicts,
            reconciliation_conflicts=candidate_conflicts,
            already_emitted=already_emitted,
            continuation=page.get("outgoing_cursor"),
            completeness="partial" if page.get("has_next") else "complete",
            truncated=bool(page.get("has_next")),
            stop_reason="unique_limit_reached" if page.get("has_next") else "source_exhausted",
        )
        if candidate["unique_task_count"] > 50:
            return envelope(
                items=items,
                first_seen=first_seen,
                raw_count=candidate_raw,
                duplicate_count=candidate_duplicates,
                item_identity_conflicts=item_identity_conflicts,
                reconciliation_conflicts=reconciliation_conflicts,
                already_emitted=already_emitted,
                continuation=incoming,
                completeness="partial",
                truncated=True,
                stop_reason="unique_limit_page_deferred",
            )
        items = candidate_items
        first_seen = candidate_first_seen
        item_identity_conflicts = candidate_identity_conflicts
        reconciliation_conflicts = candidate_conflicts
        raw_count = candidate_raw
        duplicate_count = candidate_duplicates
        if candidate["unique_task_count"] == 50 or not page.get("has_next"):
            return candidate
    raise AssertionError("fixture must terminate with exhaustion, limit, or error")


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


def parse_retry_side_matrix(text: str) -> dict[str, frozenset[str]]:
    return {
        row[0]: capability_cell(row[1])
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
        "read": {"duplicate_discovery", "target_repository_read", "target_project_read", "project_schema_read"},
        "write": {"issue_create", "project_item_add", "requested_field_update"},
    },
    "register_existing_issue": {
        "read": {"issue_read", "duplicate_membership_discovery", "target_project_read", "project_schema_read"},
        "write": {"project_item_add", "requested_field_update"},
    },
    "title_body_edit": {"read": {"issue_read"}, "write": {"issue_title_body_update"}},
    "comment": {"read": {"issue_read"}, "write": {"issue_comment_create"}},
    "status_priority_due_date": {
        "read": {"project_item_read", "requested_field_read"},
        "write": {"requested_field_update"},
    },
    "done_cancelled": {
        "read": {"issue_state_reason_read", "project_status_read"},
        "write": {"issue_close", "project_status_update"},
    },
    "reopen": {
        "read": {"issue_state_read", "project_status_read"},
        "write": {"issue_reopen", "project_status_update"},
    },
}


EXPECTED_RETRY_SIDES = {
    "issue_create": {"issue_create"},
    "project_item_add": {"project_item_add"},
    "requested_fields": {"requested_field_update"},
    "issue_terminal": {"issue_close"},
    "project_status": {"project_status_update"},
    "issue_reopen": {"issue_reopen"},
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
    if case["initial_issue"] != target_issue:
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
        and not bool(envelope_value.get("truncated", False))
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
        self.assertEqual([f"I-{number}" for number in range(1, 50)], first_identities)
        self.assertEqual(52, first["raw_observation_count"])
        self.assertEqual(49, first["unique_task_count"])
        self.assertEqual("partial", first["completeness"])
        self.assertEqual("cursor-2", first["continuation"])

        second_case = {
            "filter": "Ready",
            "already_emitted_task_identities": first_identities,
            "pages": [source["pages"][1]],
        }
        second = reconcile_pages(second_case)
        second_identities = second.pop("_returned_task_identities")
        self.assertEqual(["I-50", "I-51"], second_identities)
        self.assertEqual(
            {
                "raw_observation_count": 3,
                "deduplicated_observation_count": 0,
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
        text = read(CORE) + "\n" + read(PROJECTS)
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
            {name: set(values) for name, values in parse_retry_side_matrix(read(PROJECTS)).items()},
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
        self.assertEqual({"issue_read"}, set(matrix["comment"]["read"]))
        self.assertEqual({"issue_read"}, set(matrix["title_body_edit"]["read"]))
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
                        required.update(retry[side])
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
