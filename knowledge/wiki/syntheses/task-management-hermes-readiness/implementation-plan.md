# Task Management Hermes Schedule Secretary Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Status:** `Human-approved / current`。2026-07-31にHumanがExecution Plan Gateとして承認した。Skills implementationとterminal cross-repository handoffが承認対象であり、Companies production変更とlive mutationは引き続き別承認を要する。

**Goal:** `skills/task-management/` の portable task semantics を fixture-backed TDD で完成させ、Companies / Portfolio OS と live Hermes / GitHub MCP の未実施 work を、current-main evidence Gate と別承認を失わない durable handoffへ引き渡す。

**Architecture:** Skills repository は operation-scoped capability matrix、canonical identity、page reconciliation、lossless unique-50 pagination、complete/partial result、Done / Cancelled / reopen、resume-only partial failure、GitHub-native metadata preservationを Markdown contract と standard-library behavioral testsで所有する。本 plan の executable scope は Skills implementation と cross-repository handoffまでとし、Companies production interface、hash/install mechanism、live runbook commandは事前に固定しない。Companies は clean current `main` から別の Written Spec / Issue / Execution Plan Gateを通り、その後に live read-only / setup / task-writeを別 authorization Gateで計画する。

**Tech Stack:** Markdown、Obsidian wikilinks、JSON fixtures、Python 3.9 / 3.12 standard-library `unittest`、Git。

## Global Constraints

- Binding source は [[spec|Task Management Hermes Schedule Secretary Readiness 仕様]]、raw-byte SHA-256 は `338e0c1e192949c352a1fdd6deec1231ad495f19b68729e2aff3f330356ced4f`、Human approval commit は `088b91669813649363ddda28ea3d45387b92dbc3`。
- approved spec、[[../direct-github-projects-task-management/spec|current direct GitHub Projects spec]]、[[../direct-github-projects-task-management/issues|current ledger]] は変更しない。
- Skills Issue Gate と Execution Plan Gateを通過するまで実装を開始しない。
- `skills/task-management/` は portable contractだけを所有する。Hermes、Codex、profile path、exact live tool name、credential、permission ID、schema ID、caller default valueを hard-codeしない。
- GitHub MCP以外のCLI、REST、GraphQL、browser、local backend、provider adapterへ fallbackしない。
- assignee、label、milestone、Issue type、parent / sub-issueのwriteを追加しない。supported mutationは既存値を保持する。
- provider paginationのopaque continuation tokenは許可する。禁止対象はcredential / secret / authentication tokenの値の保存・出力であり、`token`という語そのものではない。
- credential value、secret value、authentication token value、agent ID、transcript、raw profile dump、concrete live run evidenceをrepository artifactへ保存しない。
- 各production taskは`superpowers:test-driven-development`を読み、RED -> minimal GREEN -> focused verification -> independent review -> scoped commitの順で行う。
- Companies変更、managed-native install、live MCP configuration、permission/schema mutation、Issue / Project mutation、push、PR、merge、releaseは本planでは実行しない。

## Dependency sequence

1. Task 1: operation-scoped capability matrixとcurrent validator drift。
2. Task 2: canonical identity、page reconciliation、lossless unique-50 pagination。
3. Task 3: Status normalization、complete/partial envelope、duplicate discovery stop。
4. Task 4: Done / Cancelled / reopenのcomplete state machineとresume-only retry。
5. Task 5: native metadata preservation、portable negative boundary、Skills closeout。
6. Task 6: exact cross-repository handoff。これが本planのterminal deliverableである。

Companies implementationはTask 6では開始しない。Task 6が要求するCompanies-local spec / Issue / planがHuman-approvedになった後、fresh current-main evidenceだけで別の executable planを作る。live runbook / execution planはさらにそのCompanies approvalとrepository delivery後に作る。

## File responsibility map

- `skills/task-management/SKILL.md`: operation routing、status-filtered list、reopen entrypoint、supported mutation boundary。
- `skills/task-management/references/core.md`: caller inputs、canonical Issue / Project / Project-item identity、target resolution。
- `skills/task-management/references/github-projects.md`: operation capability matrix、retry-side matrix、Status normalization、page reconciliation、pagination/result envelope、terminal/reopen semantics。
- `skills/task-management/references/issue-contract.md`: completeness-required duplicate discoveryとcreate stop condition。
- `skills/task-management/references/safety-and-failures.md`: honest complete/partial、readback-first resume、no rollback、no fallback。
- `skills/task-management/tests/fixtures/operation-capability-cases.json`: every approved operation row、unrelated-capability negative cases、remaining-side retry cases。
- `skills/task-management/tests/fixtures/pagination-cases.json`: 50/51 unique boundary、repeated/updated/conflicting observations、failures、exact envelopes。
- `skills/task-management/tests/fixtures/transition-cases.json`: Done / Cancelled / reopen complete/partial/retry state machines。
- `skills/task-management/tests/fixtures/native-metadata-cases.json`: per-operation before/change/after metadata preservation。
- `skills/task-management/tests/test_task_management_contract.py`: Markdown table parsers、test-local behavioral oracles、fixture assertions。
- `scripts/test_skill_ci_workflow.py`: strengthened task-management suiteのCI discoverability。
- `knowledge/wiki/syntheses/task-management-hermes-readiness/cross-repo-handoff.md`: Companies/live未実施workのexact durable handoff。
- `knowledge/index.md`, `knowledge/log.md`: plan / handoff / closeout discoverability。

---

### Task 1: Replace profile-wide write validation with a parsed operation-scoped matrix

**Files:**

- Modify: `skills/task-management/SKILL.md:26-82`
- Modify: `skills/task-management/references/github-projects.md:3-15`
- Create: `skills/task-management/tests/fixtures/operation-capability-cases.json`
- Modify: `skills/task-management/tests/test_task_management_contract.py:14-21,179-263,287-297`

**Interfaces:**

- `parse_capability_matrix(markdown: str) -> dict[str, dict[str, frozenset[str]]]`
- `parse_retry_side_matrix(markdown: str) -> dict[str, frozenset[str]]`
- Operation keys: `read`, `search`, `status_filtered_list`, `create`, `register_existing_issue`, `title_body_edit`, `comment`, `status_priority_due_date`, `done_cancelled`, `reopen`.
- Retry-side keys: `issue_create`, `project_item_add`, `requested_fields`, `issue_terminal`, `project_status`, `issue_reopen`.
- The fixture never supplies its own `required` set. Tests derive requirements from the parsed Markdown tables.

- [ ] **Step 1: Add the first fixture path to the exact structure contract**

Add this member to `EXPECTED_FILES` in `test_task_management_contract.py`:

```python
"tests/fixtures/operation-capability-cases.json",
```

At Task 1 GREEN, the complete expected set is the six current files plus this one fixture. Later tasks add their fixture path in the same task that creates it.

- [ ] **Step 2: Create cases covering every approved matrix row**

Create `operation-capability-cases.json`:

```json
{
  "cases": [
    {"operation": "read", "available": ["target_issue_or_project_item_read"], "remaining_sides": [], "expected_missing": []},
    {"operation": "search", "available": ["issue_search", "project_item_read", "project_item_list"], "remaining_sides": [], "expected_missing": []},
    {"operation": "status_filtered_list", "available": ["project_item_read", "project_item_list", "status_field_read"], "remaining_sides": [], "expected_missing": []},
    {"operation": "create", "available": ["duplicate_discovery", "target_repository_read", "target_project_read", "project_schema_read", "issue_create", "project_item_add", "requested_field_update"], "remaining_sides": [], "expected_missing": []},
    {"operation": "register_existing_issue", "available": ["issue_read", "duplicate_membership_discovery", "target_project_read", "project_schema_read", "project_item_add", "requested_field_update"], "remaining_sides": [], "expected_missing": []},
    {"operation": "title_body_edit", "available": ["issue_read", "issue_title_body_update"], "remaining_sides": [], "expected_missing": []},
    {"operation": "comment", "available": ["issue_read", "issue_comment_create"], "remaining_sides": [], "expected_missing": []},
    {"operation": "status_priority_due_date", "available": ["project_item_read", "requested_field_read", "requested_field_update"], "remaining_sides": [], "expected_missing": []},
    {"operation": "done_cancelled", "available": ["issue_state_reason_read", "project_status_read", "issue_close", "project_status_update"], "remaining_sides": [], "expected_missing": []},
    {"operation": "reopen", "available": ["issue_state_read", "project_status_read", "issue_reopen", "project_status_update"], "remaining_sides": [], "expected_missing": []},
    {"operation": "comment", "available": ["issue_read", "issue_comment_create"], "remaining_sides": [], "expected_missing": []},
    {"operation": "comment", "available": ["issue_read"], "remaining_sides": [], "expected_missing": ["issue_comment_create"]},
    {"operation": "register_existing_issue", "available": ["issue_read", "duplicate_membership_discovery", "target_project_read", "project_schema_read", "project_item_add", "requested_field_update"], "remaining_sides": [], "expected_missing": []},
    {"operation": "reopen", "available": ["issue_state_read", "project_status_read", "project_status_update"], "remaining_sides": ["project_status"], "expected_missing": []},
    {"operation": "done_cancelled", "available": ["issue_state_reason_read", "project_status_read"], "remaining_sides": ["issue_terminal"], "expected_missing": ["issue_close"]}
  ]
}
```

The duplicate comment case proves missing create / Project-write capabilities do not block comment. The register case proves Issue-create is irrelevant. Retry cases derive only the named remaining-side write capabilities plus the operation’s readback capabilities.

- [ ] **Step 3: Add runnable Markdown parsers and exact expected rows**

Add to `test_task_management_contract.py`:

```python
import json

FIXTURES = SKILL_ROOT / "tests" / "fixtures"


def fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


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
```

Add these methods inside `TaskManagementContractTests`:

```python
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
```

- [ ] **Step 4: Run RED**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 skills/task-management/tests/test_task_management_contract.py \
  TaskManagementContractTests.test_operation_capability_matrix_matches_every_approved_row \
  TaskManagementContractTests.test_operation_scoped_cases_derive_requirements_from_markdown \
  -v
```

Expected: FAIL because current Markdown requires one complete write set and has neither approved matrix.

- [ ] **Step 5: Write the exact two Markdown tables**

Replace the current complete-write-set prose with the two tables whose keys and semantic capability code spans exactly match `EXPECTED_CAPABILITIES` and `EXPECTED_RETRY_SIDES`. Replace every “full write preflight” route in `SKILL.md` with operation-scoped preflight. State that retry exact-reads current sides, then checks only the read set plus remaining-side writes. Tool names remain runtime-resolved.

- [ ] **Step 6: Run GREEN and commit**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 -m unittest discover -s skills/task-management/tests -v
rg -n "Every write route requires|full write preflight|Do not narrow the write preflight" \
  skills/task-management
git diff --check
git add \
  skills/task-management/SKILL.md \
  skills/task-management/references/github-projects.md \
  skills/task-management/tests/fixtures/operation-capability-cases.json \
  skills/task-management/tests/test_task_management_contract.py
git commit -m "fix: scope task capabilities by operation"
```

Expected: tests pass; negative `rg` has no output; diff check passes; one scoped commit.

---

### Task 2: Implement canonical reconciliation and lossless unique-50 pagination contract

**Files:**

- Modify: `skills/task-management/references/core.md:30-35`
- Modify: `skills/task-management/references/github-projects.md:17-45`
- Create: `skills/task-management/tests/fixtures/pagination-cases.json`
- Modify: `skills/task-management/tests/test_task_management_contract.py`

**Interfaces:**

- `canonical_task_identity`: stable Issue ID -> canonical Issue URL -> normalized `owner/repository#number`.
- `canonical_project_item_identity`: stable item ID -> `(canonical_project_url, canonical_task_identity)`.
- `reconcile_pages(case: dict[str, object]) -> dict[str, object]` is test-only acceptance oracle.
- Envelope fields: `raw_observation_count`, `deduplicated_observation_count`, `identity_conflict_count`, `reconciliation_conflict_count`, `unique_task_count`, `returned_count`, `task_order`, `completeness`, `truncated`, `continuation`, `stop_reason`.
- `ContinuationState` contains the unchanged opaque `provider_cursor` plus exact `already_emitted_task_identities`; the identity set is resume state, not a synthesized provider cursor.
- `raw_observation_count` counts every raw observation fetched and inspected during that call, including an overshoot page that is deferred from reconciliation state.
- Lossless unique-50 rule: process raw pages atomically. If accepting a page would exceed 50 unique matches, do not commit it; return the page’s provider-supplied incoming cursor and prior reconciliation state, even when that returns fewer than 50. The next call supplies the unchanged cursor and prior emitted identities, suppresses repeats, and may complete from the deferred page. Do not synthesize an intra-page offset or identity. This MVP does not use provider intra-page resume because later observations in the same page may revise earlier ones.

- [ ] **Step 1: Extend `EXPECTED_FILES` for the pagination fixture**

Add:

```python
"tests/fixtures/pagination-cases.json",
```

- [ ] **Step 2: Create concrete compact fixtures with exact envelopes**

Create `pagination-cases.json`. `generated_unique` expands deterministic observations `I-<n>` / `PVTI-<n>`:

```json
{
  "cases": [
    {
      "name": "exact_50_after_duplicate",
      "filter": "Ready",
      "pages": [
        {"incoming_cursor": null, "outgoing_cursor": "cursor-2", "has_next": true, "generated_unique": {"start": 1, "count": 48}},
        {"incoming_cursor": "cursor-2", "outgoing_cursor": "cursor-3", "has_next": true, "items": [
          {"item_identity": "PVTI-1", "task_identity": "I-1", "status": "Ready", "updated_at": "2026-07-31T00:00:00Z"},
          {"item_identity": "PVTI-49", "task_identity": "I-49", "status": "Ready", "updated_at": "2026-07-31T00:00:00Z"},
          {"item_identity": "PVTI-50", "task_identity": "I-50", "status": "Ready", "updated_at": "2026-07-31T00:00:00Z"}
        ]}
      ],
      "expected": {"raw_observation_count": 51, "deduplicated_observation_count": 1, "identity_conflict_count": 0, "reconciliation_conflict_count": 0, "unique_task_count": 50, "returned_count": 50, "task_order": {"first": "I-1", "last": "I-50"}, "completeness": "partial", "truncated": true, "continuation": "cursor-3", "stop_reason": "unique_limit_reached"}
    },
    {
      "name": "page_would_create_51",
      "filter": "Ready",
      "pages": [
        {"incoming_cursor": null, "outgoing_cursor": "cursor-2", "has_next": true, "generated_unique": {"start": 1, "count": 49}},
        {"incoming_cursor": "cursor-2", "outgoing_cursor": null, "has_next": false, "items": [
          {"item_identity": "PVTI-1", "task_identity": "I-1", "status": "Ready", "updated_at": "2026-07-31T00:00:00Z"},
          {"item_identity": "PVTI-50", "task_identity": "I-50", "status": "Ready", "updated_at": "2026-07-31T00:00:00Z"},
          {"item_identity": "PVTI-51", "task_identity": "I-51", "status": "Ready", "updated_at": "2026-07-31T00:00:00Z"}
        ]}
      ],
      "expected": {"raw_observation_count": 52, "deduplicated_observation_count": 1, "identity_conflict_count": 0, "reconciliation_conflict_count": 0, "unique_task_count": 49, "returned_count": 49, "task_order": {"first": "I-1", "last": "I-49"}, "completeness": "partial", "truncated": true, "continuation": "cursor-2", "stop_reason": "unique_limit_page_deferred"}
    },
    {
      "name": "repeated_and_updated_across_pages",
      "filter": "Ready",
      "pages": [
        {"incoming_cursor": null, "outgoing_cursor": "cursor-b", "has_next": true, "items": [
          {"item_identity": "PVTI-A", "task_identity": "I-A", "status": "Backlog", "updated_at": "2026-07-30T00:00:00Z"},
          {"item_identity": "PVTI-B", "task_identity": "I-B", "status": "Ready", "updated_at": "2026-07-30T00:00:00Z"}
        ]},
        {"incoming_cursor": "cursor-b", "outgoing_cursor": null, "has_next": false, "items": [
          {"item_identity": "PVTI-A", "task_identity": "I-A", "status": "Ready", "updated_at": "2026-07-31T00:00:00Z"},
          {"item_identity": "PVTI-B", "task_identity": "I-B", "status": null, "updated_at": "2026-07-31T00:00:00Z"}
        ]}
      ],
      "expected": {"raw_observation_count": 4, "deduplicated_observation_count": 2, "identity_conflict_count": 0, "reconciliation_conflict_count": 0, "unique_task_count": 2, "returned_count": 2, "task_order": ["I-B", "I-A"], "completeness": "complete", "truncated": false, "continuation": null, "stop_reason": "source_exhausted"}
    },
    {
      "name": "same_task_multiple_items",
      "filter": "Ready",
      "pages": [
        {"incoming_cursor": null, "outgoing_cursor": null, "has_next": false, "items": [
          {"item_identity": "PVTI-X", "task_identity": "I-X", "status": "Ready", "updated_at": null},
          {"item_identity": "PVTI-Y", "task_identity": "I-X", "status": "Ready", "updated_at": null}
        ]}
      ],
      "expected": {"raw_observation_count": 2, "deduplicated_observation_count": 0, "identity_conflict_count": 1, "reconciliation_conflict_count": 0, "unique_task_count": 1, "returned_count": 1, "task_order": ["I-X"], "completeness": "partial", "truncated": false, "continuation": null, "stop_reason": "identity_conflict"}
    },
    {
      "name": "irreconcilable_same_item",
      "filter": "Ready",
      "pages": [
        {"incoming_cursor": null, "outgoing_cursor": null, "has_next": false, "items": [
          {"item_identity": "PVTI-Z", "task_identity": "I-Z", "status": "Ready", "priority": "P1", "updated_at": null},
          {"item_identity": "PVTI-Z", "task_identity": "I-Z", "status": "Ready", "priority": "P2", "updated_at": null}
        ]}
      ],
      "expected": {"raw_observation_count": 2, "deduplicated_observation_count": 1, "identity_conflict_count": 0, "reconciliation_conflict_count": 1, "unique_task_count": 0, "returned_count": 0, "task_order": [], "completeness": "partial", "truncated": false, "continuation": null, "stop_reason": "reconciliation_conflict"}
    },
    {
      "name": "missing_preserves_then_explicit_clear_removes",
      "filter": "Ready",
      "pages": [
        {"incoming_cursor": null, "outgoing_cursor": "cursor-clear", "has_next": true, "items": [
          {"item_identity": "PVTI-C", "task_identity": "I-C", "status": "Ready", "priority": "P1", "updated_at": "2026-07-29T00:00:00Z"}
        ]},
        {"incoming_cursor": "cursor-clear", "outgoing_cursor": null, "has_next": false, "items": [
          {"item_identity": "PVTI-C", "task_identity": "I-C", "status": null, "updated_at": "2026-07-30T00:00:00Z"},
          {"item_identity": "PVTI-C", "task_identity": "I-C", "status": null, "priority": null, "explicit_clear": ["priority"], "updated_at": "2026-07-31T00:00:00Z"}
        ]}
      ],
      "expected_item_state": {"PVTI-C": {"task_identity": "I-C", "status": "Ready", "priority": null}},
      "expected": {"raw_observation_count": 3, "deduplicated_observation_count": 2, "identity_conflict_count": 0, "reconciliation_conflict_count": 0, "unique_task_count": 1, "returned_count": 1, "task_order": ["I-C"], "completeness": "complete", "truncated": false, "continuation": null, "stop_reason": "source_exhausted"}
    },
    {
      "name": "same_item_different_task_identity",
      "filter": "Ready",
      "pages": [
        {"incoming_cursor": null, "outgoing_cursor": null, "has_next": false, "items": [
          {"item_identity": "PVTI-Q", "task_identity": "I-Q1", "status": "Ready", "updated_at": null},
          {"item_identity": "PVTI-Q", "task_identity": "I-Q2", "status": "Ready", "updated_at": null}
        ]}
      ],
      "expected": {"raw_observation_count": 2, "deduplicated_observation_count": 1, "identity_conflict_count": 1, "reconciliation_conflict_count": 0, "unique_task_count": 0, "returned_count": 0, "task_order": [], "completeness": "partial", "truncated": false, "continuation": null, "stop_reason": "identity_conflict"}
    },
    {
      "name": "permission_failure_preserves_results",
      "filter": "Ready",
      "pages": [
        {"incoming_cursor": null, "outgoing_cursor": "cursor-f", "has_next": true, "generated_unique": {"start": 1, "count": 3}},
        {"incoming_cursor": "cursor-f", "error": "permission_failure"}
      ],
      "expected": {"raw_observation_count": 3, "deduplicated_observation_count": 0, "identity_conflict_count": 0, "reconciliation_conflict_count": 0, "unique_task_count": 3, "returned_count": 3, "task_order": ["I-1", "I-2", "I-3"], "completeness": "partial", "truncated": false, "continuation": "cursor-f", "stop_reason": "permission_failure"}
    }
  ]
}
```

- [ ] **Step 3: Add the complete runnable reconciliation oracle**

Add to `test_task_management_contract.py`:

```python
from copy import deepcopy


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
        items[item_id] = deepcopy(observation)
        return False
    if current["task_identity"] != observation["task_identity"]:
        item_identity_conflicts.add(item_id)
        return True
    explicit_clear = set(observation.get("explicit_clear", []))
    for field in ("status", "priority"):
        if field in explicit_clear:
            current[field] = None
            if observation.get("updated_at") is not None:
                current["updated_at"] = observation["updated_at"]
            continue
        if field not in observation:
            continue
        incoming = observation[field]
        existing = current.get(field)
        if incoming is None:
            continue
        if existing is None or incoming == existing:
            current[field] = incoming
            continue
        old_time = current.get("updated_at")
        new_time = observation.get("updated_at")
        if old_time is not None and new_time is not None:
            if str(new_time) >= str(old_time):
                current[field] = incoming
                current["updated_at"] = new_time
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
```

Add these methods inside `TaskManagementContractTests`:

```python
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
```

- [ ] **Step 4: Run RED**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 skills/task-management/tests/test_task_management_contract.py \
  TaskManagementContractTests.test_pagination_fixtures_match_exact_counts_conflicts_and_continuation \
  TaskManagementContractTests.test_unique_51_two_call_continuation_is_lossless \
  TaskManagementContractTests.test_identity_and_lossless_page_boundary_are_explicit \
  -v
```

Expected: fixture oracle passes internally, but contract test FAILS because current Markdown lacks identity/reconciliation/lossless continuation rules. If the oracle itself fails, fix the fixture/oracle before editing production Markdown.

- [ ] **Step 5: Write minimal identity, merge, and unique-50 contract**

Add exact identity precedence and URL normalization to `core.md`. Add field merge, timestamp ordering, ordinary missing/null preservation, provider-declared explicit clear, same-item/different-task identity-conflict isolation, same-task/multiple-membership partial result, stable first-valid order, whole-page atomicity, and the lossless page-defer rule to `github-projects.md`. A fetched overshoot page contributes to the call’s `raw_observation_count` but is not committed to matching state. Return its unchanged incoming provider cursor plus `already_emitted_task_identities`; the resumed call suppresses those identities and emits each canonical task once.

- [ ] **Step 6: Run GREEN and commit**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 -m unittest discover -s skills/task-management/tests -v
git diff --check
git add \
  skills/task-management/references/core.md \
  skills/task-management/references/github-projects.md \
  skills/task-management/tests/fixtures/pagination-cases.json \
  skills/task-management/tests/test_task_management_contract.py
git commit -m "feat: define lossless task page reconciliation"
```

---

### Task 3: Normalize Status and make completeness / duplicate discovery honest

**Files:**

- Modify: `skills/task-management/SKILL.md:34-52`
- Modify: `skills/task-management/references/github-projects.md`
- Modify: `skills/task-management/references/issue-contract.md:29-33`
- Modify: `skills/task-management/references/safety-and-failures.md:14-28`
- Modify: `skills/task-management/tests/test_task_management_contract.py`

**Interfaces:**

- Canonical Status: `Inbox`, `Backlog`, `Ready`, `In progress`, `Blocked`, `Done`, `Cancelled`.
- Result envelope is the Task 2 envelope. `complete` requires source exhaustion; limit, deferred page, permission failure, page failure, schema ambiguity, or tool hard limit is `partial`.
- Duplicate discovery is completeness-required. `partial` or truncated discovery returns `create_allowed=false`.

- [ ] **Step 1: Add failing normalization and duplicate-decision helpers**

Add the helper at module scope and the methods inside `TaskManagementContractTests`:

```python
STATUS_WORDING = {
    "Inbox": {"Inbox", "受信箱", "未整理"},
    "Backlog": {"Backlog", "バックログ", "実施候補"},
    "Ready": {"Ready", "着手可能", "準備完了"},
    "In progress": {"In progress", "進行中", "着手中", "対応中"},
    "Blocked": {"Blocked", "ブロック中", "停止中"},
    "Done": {"Done", "完了", "終了"},
    "Cancelled": {"Cancelled", "Canceled", "中止", "キャンセル"},
}


def duplicate_decision(envelope_value: dict[str, object], unique_match: bool) -> dict[str, object]:
    complete = envelope_value["completeness"] == "complete"
    return {
        "no_duplicate_claim": complete and not unique_match,
        "create_allowed": complete and not unique_match,
    }


    def test_status_wording_and_schema_ambiguity_contract(self) -> None:
        text = read(PROJECTS)
        for canonical, wording in STATUS_WORDING.items():
            self.assertIn(canonical, text)
            for value in wording:
                self.assertIn(value, text)
        self.assertIn("schema ambiguity", text)
        self.assertIn("stop", text)

    def test_duplicate_discovery_requires_complete_exhaustion(self) -> None:
        partial = {"completeness": "partial"}
        complete = {"completeness": "complete"}
        self.assertEqual(
            {"no_duplicate_claim": False, "create_allowed": False},
            duplicate_decision(partial, unique_match=False),
        )
        self.assertEqual(
            {"no_duplicate_claim": True, "create_allowed": True},
            duplicate_decision(complete, unique_match=False),
        )
        self.assertEqual(
            {"no_duplicate_claim": False, "create_allowed": False},
            duplicate_decision(complete, unique_match=True),
        )
        duplicate_text = section(read(ISSUES), "## Duplicate handling")
        self.assertIn("completeness-required", duplicate_text)
        self.assertIn("create_allowed=false", duplicate_text)
```

- [ ] **Step 2: Run RED**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 skills/task-management/tests/test_task_management_contract.py \
  TaskManagementContractTests.test_status_wording_and_schema_ambiguity_contract \
  TaskManagementContractTests.test_duplicate_discovery_requires_complete_exhaustion \
  -v
```

Expected: FAIL because current contract lacks wording normalization, honest envelope, and partial duplicate stop.

- [ ] **Step 3: Write minimal completeness contract**

Add the exact Status wording table, ambiguity stop, result envelope field definitions, exhaustion-only `complete`, opaque provider continuation preservation, failure stop reasons, and duplicate-discovery decision. Keep display limit separate from investigation extent. Do not prohibit the term continuation token.

- [ ] **Step 4: Run GREEN and commit**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 -m unittest discover -s skills/task-management/tests -v
git diff --check
git add \
  skills/task-management/SKILL.md \
  skills/task-management/references/github-projects.md \
  skills/task-management/references/issue-contract.md \
  skills/task-management/references/safety-and-failures.md \
  skills/task-management/tests/test_task_management_contract.py
git commit -m "feat: make task query completeness explicit"
```

---

### Task 4: Execute Done, Cancelled, and reopen state-machine fixtures

**Files:**

- Modify: `skills/task-management/SKILL.md:75-82`
- Modify: `skills/task-management/references/github-projects.md:47-58`
- Modify: `skills/task-management/references/safety-and-failures.md:24-28`
- Create: `skills/task-management/tests/fixtures/transition-cases.json`
- Modify: `skills/task-management/tests/test_task_management_contract.py`

**Interfaces:**

- `run_transition(case: dict[str, object]) -> dict[str, object]` is a test-only state machine.
- Side names: `issue`, `project_status`.
- Result fields: `target_issue_state`, `target_close_reason`, `target_status`, `first_attempted_sides`, `first_result`, `first_remaining_sides`, `retry_attempted_sides`, `final_result`, `final_remaining_sides`.
- Bare reopen target is `Backlog`; explicit terminal target for reopen is blocked.

- [ ] **Step 1: Extend `EXPECTED_FILES`**

Add:

```python
"tests/fixtures/transition-cases.json",
```

- [ ] **Step 2: Create complete transition fixtures**

Create `transition-cases.json`:

```json
{
  "cases": [
    {"name": "done_complete", "operation": "done", "initial_issue": "open", "initial_status": "In progress", "requested_status": null, "first_success": ["issue", "project_status"], "retry_success": [], "expected": {"target_issue_state": "closed", "target_close_reason": "completed", "target_status": "Done", "first_attempted_sides": ["issue", "project_status"], "first_result": "complete", "first_remaining_sides": [], "retry_attempted_sides": [], "final_result": "complete", "final_remaining_sides": []}},
    {"name": "done_issue_first_partial", "operation": "done", "initial_issue": "open", "initial_status": "In progress", "requested_status": null, "first_success": ["issue"], "retry_success": ["project_status"], "expected": {"target_issue_state": "closed", "target_close_reason": "completed", "target_status": "Done", "first_attempted_sides": ["issue", "project_status"], "first_result": "partial", "first_remaining_sides": ["project_status"], "retry_attempted_sides": ["project_status"], "final_result": "complete", "final_remaining_sides": []}},
    {"name": "done_status_first_partial", "operation": "done", "initial_issue": "open", "initial_status": "In progress", "requested_status": null, "first_success": ["project_status"], "retry_success": ["issue"], "expected": {"target_issue_state": "closed", "target_close_reason": "completed", "target_status": "Done", "first_attempted_sides": ["issue", "project_status"], "first_result": "partial", "first_remaining_sides": ["issue"], "retry_attempted_sides": ["issue"], "final_result": "complete", "final_remaining_sides": []}},
    {"name": "cancelled_issue_first_partial", "operation": "cancelled", "initial_issue": "open", "initial_status": "Blocked", "requested_status": null, "first_success": ["issue"], "retry_success": ["project_status"], "expected": {"target_issue_state": "closed", "target_close_reason": "not planned", "target_status": "Cancelled", "first_attempted_sides": ["issue", "project_status"], "first_result": "partial", "first_remaining_sides": ["project_status"], "retry_attempted_sides": ["project_status"], "final_result": "complete", "final_remaining_sides": []}},
    {"name": "cancelled_status_first_partial", "operation": "cancelled", "initial_issue": "open", "initial_status": "Blocked", "requested_status": null, "first_success": ["project_status"], "retry_success": ["issue"], "expected": {"target_issue_state": "closed", "target_close_reason": "not planned", "target_status": "Cancelled", "first_attempted_sides": ["issue", "project_status"], "first_result": "partial", "first_remaining_sides": ["issue"], "retry_attempted_sides": ["issue"], "final_result": "complete", "final_remaining_sides": []}},
    {"name": "bare_reopen_issue_first", "operation": "reopen", "initial_issue": "closed", "initial_status": "Done", "requested_status": null, "first_success": ["issue"], "retry_success": ["project_status"], "expected": {"target_issue_state": "open", "target_close_reason": null, "target_status": "Backlog", "first_attempted_sides": ["issue", "project_status"], "first_result": "partial", "first_remaining_sides": ["project_status"], "retry_attempted_sides": ["project_status"], "final_result": "complete", "final_remaining_sides": []}},
    {"name": "explicit_reopen_status_first", "operation": "reopen", "initial_issue": "closed", "initial_status": "Cancelled", "requested_status": "Ready", "first_success": ["project_status"], "retry_success": ["issue"], "expected": {"target_issue_state": "open", "target_close_reason": null, "target_status": "Ready", "first_attempted_sides": ["issue", "project_status"], "first_result": "partial", "first_remaining_sides": ["issue"], "retry_attempted_sides": ["issue"], "final_result": "complete", "final_remaining_sides": []}},
    {"name": "reopen_readback_resumes_status_only", "operation": "reopen", "initial_issue": "open", "initial_status": "Done", "requested_status": null, "first_success": ["project_status"], "retry_success": [], "expected": {"target_issue_state": "open", "target_close_reason": null, "target_status": "Backlog", "first_attempted_sides": ["project_status"], "first_result": "complete", "first_remaining_sides": [], "retry_attempted_sides": [], "final_result": "complete", "final_remaining_sides": []}},
    {"name": "invalid_terminal_reopen", "operation": "reopen", "initial_issue": "closed", "initial_status": "Done", "requested_status": "Cancelled", "first_success": [], "retry_success": [], "expected": {"target_issue_state": null, "target_close_reason": null, "target_status": null, "first_attempted_sides": [], "first_result": "blocked", "first_remaining_sides": [], "retry_attempted_sides": [], "final_result": "blocked", "final_remaining_sides": []}},
    {"name": "invalid_done_reopen", "operation": "reopen", "initial_issue": "closed", "initial_status": "Cancelled", "requested_status": "Done", "first_success": [], "retry_success": [], "expected": {"target_issue_state": null, "target_close_reason": null, "target_status": null, "first_attempted_sides": [], "first_result": "blocked", "first_remaining_sides": [], "retry_attempted_sides": [], "final_result": "blocked", "final_remaining_sides": []}},
    {"name": "unknown_reopen_target", "operation": "reopen", "initial_issue": "closed", "initial_status": "Done", "requested_status": "Later", "first_success": [], "retry_success": [], "expected": {"target_issue_state": null, "target_close_reason": null, "target_status": null, "first_attempted_sides": [], "first_result": "blocked", "first_remaining_sides": [], "retry_attempted_sides": [], "final_result": "blocked", "final_remaining_sides": []}}
  ]
}
```

- [ ] **Step 3: Add the runnable state machine**

```python
NON_TERMINAL_REOPEN_STATUSES = frozenset(
    {"Inbox", "Backlog", "Ready", "In progress", "Blocked"}
)


def transition_targets(case: dict[str, object]) -> tuple[object, object, object]:
    operation = case["operation"]
    if operation == "done":
        return "closed", "completed", "Done"
    if operation == "cancelled":
        return "closed", "not planned", "Cancelled"
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
```

- [ ] **Step 4: Run RED**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 skills/task-management/tests/test_task_management_contract.py \
  TaskManagementContractTests.test_transition_fixtures_execute_complete_partial_and_retry \
  TaskManagementContractTests.test_reopen_target_allowlist_blocks_terminal_and_unknown_values \
  TaskManagementContractTests.test_terminal_and_reopen_contract_names_state_machine_outputs \
  -v
```

Expected: state-machine fixture test passes; contract test FAILS because current Markdown lacks reopen and exact output/resume terms.

- [ ] **Step 5: Write minimal transition contract**

Add `### Reopen` to `SKILL.md`; add terminal and reopen state machine prose to `github-projects.md`; add readback-first/no-rollback/remaining-only recovery to `safety-and-failures.md`. The exact explicit reopen target allowlist is `Inbox`, `Backlog`, `Ready`, `In progress`, and `Blocked`; bare reopen remains `Backlog`. Block `Done`, `Cancelled`, every unknown or non-normalizable value, and schema-ambiguous targets before either side is attempted. Explicit terminal instructions retain no-double-confirmation; inferred terminal transition retains confirmation.

- [ ] **Step 6: Run GREEN and commit**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 -m unittest discover -s skills/task-management/tests -v
git diff --check
git add \
  skills/task-management/SKILL.md \
  skills/task-management/references/github-projects.md \
  skills/task-management/references/safety-and-failures.md \
  skills/task-management/tests/fixtures/transition-cases.json \
  skills/task-management/tests/test_task_management_contract.py
git commit -m "feat: add resumable terminal task transitions"
```

---

### Task 5: Prove native metadata preservation and close the Skills implementation

**Files:**

- Modify: `skills/task-management/SKILL.md`
- Modify: `skills/task-management/references/github-projects.md`
- Modify: `skills/task-management/references/issue-contract.md`
- Modify: `skills/task-management/references/safety-and-failures.md`
- Create: `skills/task-management/tests/fixtures/native-metadata-cases.json`
- Modify: `skills/task-management/tests/test_task_management_contract.py`
- Modify: `scripts/test_skill_ci_workflow.py:39-42`
- Modify: Skills Issue ledger created by Issue Gate
- Modify: `knowledge/index.md`
- Append only: `knowledge/log.md`

**Interfaces:**

- Protected keys: `assignees`, `labels`, `milestone`, `issue_type`, `parent_issue`, `sub_issues`.
- `apply_requested_change(before, requested_change) -> after` is test-only.
- Each fixture case owns explicit `before`, `requested_change`, and `after`; tests compare the full result and protected equality.

- [ ] **Step 1: Extend `EXPECTED_FILES`**

Add:

```python
"tests/fixtures/native-metadata-cases.json",
```

The final exact `EXPECTED_FILES` is:

```python
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
```

- [ ] **Step 2: Create per-operation before/change/after fixtures**

Create `native-metadata-cases.json`. Every case repeats the protected values intentionally so a changed after-state fails:

```json
{
  "cases": [
    {"operation": "register_existing_issue", "before": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"project_membership": false, "status": null, "priority": null, "due_date": null}}, "requested_change": {"project_membership": true, "status": "Inbox", "priority": "P2", "due_date": null}, "after": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"project_membership": true, "status": "Inbox", "priority": "P2", "due_date": null}}},
    {"operation": "edit_title", "before": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"title": "old"}}, "requested_change": {"title": "new"}, "after": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"title": "new"}}},
    {"operation": "edit_body", "before": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"body": "old"}}, "requested_change": {"body": "new"}, "after": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"body": "new"}}},
    {"operation": "comment", "before": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"comments": []}}, "requested_change": {"comments": ["note"]}, "after": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"comments": ["note"]}}},
    {"operation": "status", "before": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"status": "Backlog"}}, "requested_change": {"status": "Ready"}, "after": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"status": "Ready"}}},
    {"operation": "priority", "before": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"priority": "P2"}}, "requested_change": {"priority": "P1"}, "after": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"priority": "P1"}}},
    {"operation": "due_date", "before": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"due_date": null}}, "requested_change": {"due_date": "2026-08-01"}, "after": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"due_date": "2026-08-01"}}},
    {"operation": "done", "before": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"issue_state": "open", "close_reason": null, "status": "In progress"}}, "requested_change": {"issue_state": "closed", "close_reason": "completed", "status": "Done"}, "after": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"issue_state": "closed", "close_reason": "completed", "status": "Done"}}},
    {"operation": "cancelled", "before": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"issue_state": "open", "close_reason": null, "status": "Blocked"}}, "requested_change": {"issue_state": "closed", "close_reason": "not planned", "status": "Cancelled"}, "after": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"issue_state": "closed", "close_reason": "not planned", "status": "Cancelled"}}},
    {"operation": "reopen", "before": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"issue_state": "closed", "close_reason": "completed", "status": "Done"}}, "requested_change": {"issue_state": "open", "close_reason": null, "status": "Backlog"}, "after": {"protected": {"assignees": ["octo"], "labels": ["planning"], "milestone": "M1", "issue_type": "Task", "parent_issue": "R#10", "sub_issues": ["R#12"]}, "mutable": {"issue_state": "open", "close_reason": null, "status": "Backlog"}}}
  ]
}
```

- [ ] **Step 3: Add runnable equality tests and secret-specific negative checks**

```python
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


    def test_every_supported_mutation_preserves_native_metadata(self) -> None:
        expected_operations = {
            "register_existing_issue", "edit_title", "edit_body", "comment",
            "status", "priority", "due_date", "done", "cancelled", "reopen",
        }
        observed = set()
        for case in fixture("native-metadata-cases.json")["cases"]:
            observed.add(case["operation"])
            with self.subTest(operation=case["operation"]):
                actual = apply_requested_change(case["before"], case["requested_change"])
                self.assertEqual(case["after"], actual)
                self.assertEqual(
                    case["before"]["protected"],
                    actual["protected"],
                )
                self.assertEqual(
                    case["after"]["protected"],
                    actual["protected"],
                )
        self.assertEqual(expected_operations, observed)

    def test_portable_contract_forbids_secret_values_not_pagination_terms(self) -> None:
        production = "\n".join(
            read(path) for path in [SKILL, *sorted((SKILL_ROOT / "references").glob("*.md"))]
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
```

Update `scripts/test_skill_ci_workflow.py` to require:

```python
self.assertIn("test_operation_capability_matrix_matches_every_approved_row", text)
self.assertIn("test_pagination_fixtures_match_exact_counts_conflicts_and_continuation", text)
self.assertIn("test_unique_51_two_call_continuation_is_lossless", text)
self.assertIn("test_transition_fixtures_execute_complete_partial_and_retry", text)
self.assertIn("test_reopen_target_allowlist_blocks_terminal_and_unknown_values", text)
self.assertIn("test_every_supported_mutation_preserves_native_metadata", text)
```

- [ ] **Step 4: Run RED**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 skills/task-management/tests/test_task_management_contract.py \
  TaskManagementContractTests.test_every_supported_mutation_preserves_native_metadata \
  TaskManagementContractTests.test_portable_contract_forbids_secret_values_not_pagination_terms \
  -v
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 scripts/test_skill_ci_workflow.py -v
```

Expected: fixture equality test passes; contract/CI tests FAIL for missing exact preservation/continuation and strengthened method names.

- [ ] **Step 5: Write minimal preservation and secret boundary**

State that native metadata may be read but no MVP operation writes it, including when registering an existing Issue into the Project and initializing requested Project fields. Require requested-field and protected-metadata exact readback for `register_existing_issue` and every other supported mutation; unavailable readback yields `partial`. Permit provider opaque continuation tokens. Add the exact sentence `Do not store or return credential, secret, or authentication token values.`

- [ ] **Step 6: Run complete fresh Skills verification**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 -m unittest discover -s skills/task-management/tests -v
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 scripts/test_skill_ci_workflow.py -v
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 -m unittest discover -s scripts -p 'test_*.py' -v
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache \
  python3 scripts/validate_skill_architecture.py --all
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/task-management
rg -n --glob '!**/tests/**' \
  "Hermes|Codex|task-management-read|task_adapter__|work_unit_id|credential_value|secret_value|authentication_token_value|raw_profile_dump" \
  skills/task-management
git diff --check
```

Expected: tests/validators pass; negative `rg` has no output; `git diff --check` passes. The `rg` deliberately does not reject `continuation token`.

- [ ] **Step 7: Update Skills closeout and commit**

Map every portable acceptance criterion to named tests in the approved Issue ledger. Update `knowledge/index.md` and append `knowledge/log.md` with exact commits and verification counts. State explicitly that Companies delivery, install, live readiness, and mutation remain unperformed.

```bash
git add \
  skills/task-management \
  scripts/test_skill_ci_workflow.py \
  knowledge/index.md \
  knowledge/log.md \
  knowledge/wiki/syntheses/task-management-hermes-readiness
git diff --cached --check
git commit -m "feat: complete portable task management readiness"
```

---

### Task 6: Publish the exact cross-repository handoff and stop

**Files:**

- Create: `knowledge/wiki/syntheses/task-management-hermes-readiness/cross-repo-handoff.md`
- Modify: `knowledge/index.md`
- Append only: `knowledge/log.md`

**Interfaces:**

- Consumes: merged Skills commit, full 40-character revision, exact installed-bundle bytes/hash evidence when later resolved by the owning runtime, approved spec path/hash/commit, Skills verification summary.
- Produces: Companies evidence-resolution packet, required Companies durable artifacts, required live durable artifacts, acceptance evidence, authorization Gates, dependency order, and stop conditions.
- Does not define Companies production paths, Python types, hash algorithm, install command, CLI integration, or live tool names.

- [ ] **Step 1: Prove the Skills revision is merged before handoff**

```bash
git fetch --prune origin main
SKILLS_REVISION="$(git rev-parse HEAD)"
git merge-base --is-ancestor "$SKILLS_REVISION" origin/main
git show --no-patch --format='%H %cI %s' "$SKILLS_REVISION"
```

Expected: ancestry exits `0` and prints one exact commit. If not merged, stop `BLOCKED: Companies must not pin a local-only Skills revision`.

- [ ] **Step 2: Write the handoff’s known external facts and clean-baseline commands**

`cross-repo-handoff.md` must bind:

- Skills spec `knowledge/wiki/syntheses/task-management-hermes-readiness/spec.md`;
- spec SHA-256 `338e0c1e192949c352a1fdd6deec1231ad495f19b68729e2aff3f330356ced4f`;
- approval commit `088b91669813649363ddda28ea3d45387b92dbc3`;
- exact merged `SKILLS_REVISION`;
- exact Skills verification commands/counts;
- observed, explicitly stale-until-rechecked Companies evidence:
  - dirty default checkout `/Users/omitsuhashi/repos/the3-inc/companies`;
  - observed branch `codex/github-task-live-readiness` / `190fcdb27f622884e3eaefee1a2654ac8c5c40e5`;
  - observed `main` / `origin/main` `42e9f0600f2fbec66f7fe05f9023f3a6328292d7`;
  - overlapping divergent worktree `/private/tmp/github-mcp-operation-scoped-actions-worktrees/companies` / `c5359467dd1346f3d2ec8ff4649aaad74fedf017`.

Include these exact read-only/current-main commands:

```bash
git -C /Users/omitsuhashi/repos/the3-inc/companies status --short --branch
git -C /Users/omitsuhashi/repos/the3-inc/companies rev-parse HEAD
git -C /Users/omitsuhashi/repos/the3-inc/companies worktree list --porcelain
git -C /Users/omitsuhashi/repos/the3-inc/companies fetch --prune origin main
git -C /Users/omitsuhashi/repos/the3-inc/companies rev-parse refs/remotes/origin/main
git -C /Users/omitsuhashi/repos/the3-inc/companies log -1 \
  --format='%H %cI %s' refs/remotes/origin/main
```

Stop if fetch/current-main verification fails. Do not stash, switch, pull, clean, reset, or edit the dirty default checkout.

- [ ] **Step 3: Require one clean Companies planning worktree and overlap reconciliation**

The handoff requires:

```bash
COMPANIES_PLAN_PARENT="$(mktemp -d /private/tmp/task-management-hermes-readiness-companies.XXXXXX)"
COMPANIES_PLAN_WORKTREE="${COMPANIES_PLAN_PARENT}/companies"
git -C /Users/omitsuhashi/repos/the3-inc/companies worktree add \
  -b codex/task-management-hermes-readiness-planning \
  "$COMPANIES_PLAN_WORKTREE" \
  refs/remotes/origin/main
git -C "$COMPANIES_PLAN_WORKTREE" status --short --branch
sed -n '1,240p' "$COMPANIES_PLAN_WORKTREE/AGENTS.md"
sed -n '1,320p' "$COMPANIES_PLAN_WORKTREE/knowledge/AGENTS.md"
git -C "$COMPANIES_PLAN_WORKTREE" merge-base \
  refs/remotes/origin/main \
  c5359467dd1346f3d2ec8ff4649aaad74fedf017
git -C "$COMPANIES_PLAN_WORKTREE" diff --name-status \
  refs/remotes/origin/main...c5359467dd1346f3d2ec8ff4649aaad74fedf017
git -C "$COMPANIES_PLAN_WORKTREE" log --oneline \
  refs/remotes/origin/main..c5359467dd1346f3d2ec8ff4649aaad74fedf017
```

If the branch already exists, reuse only after proving its base/scope; do not delete it. The overlapping branch is evidence only, never default cherry-pick/merge input. Classify each overlap `reuse_semantics`, `superseded_by_current_main`, `conflicts_with_approved_scope`, or `not_applicable`.

- [ ] **Step 4: Require separate Companies Written Spec / Issue / Plan Gates**

The handoff must require the Companies owner to create and approve, from verified current `main`:

- `knowledge/wiki/syntheses/task-management-hermes-readiness/spec.md`;
- `knowledge/wiki/syntheses/task-management-hermes-readiness/issues.md`;
- `knowledge/wiki/syntheses/task-management-hermes-readiness/implementation-plan.md`;
- Companies `knowledge/index.md` and append-only `knowledge/log.md` synchronization.

The Companies spec must reconcile the current Hermes-sole-owner boundary before any production change. It must preserve these approved requirements without preselecting implementation:

1. Schedule Secretary-only source selection, exact source revision/hash evidence, install/discovery, and caller `project_url` / optional `inbox_repository` readiness.
2. Portable semantics are consumed from the pinned Skills revision and never copied into Companies.
3. Atomic reason codes and deterministic `blocked > partial > ready`, with `not_applicable` excluded and operation scope preserved.
4. Managed-native checks: expected hash missing, installed hash current/stale/unknown, discovery ready/unknown/blocked, default current/missing/overridden.
5. Live checks: semantic tool present/missing/unknown, permission confirmed/unknown/rejected, target access, applicable schema current/unknown/mismatch, pagination/continuation behavior, non-mutating write readiness ceiling.
6. Official `dry-run -> separately authorized apply -> status -> readback`, with apply log, backup manifest, rollback bundle, completed/remaining steps.
7. No credential values/secrets, no direct profile filesystem or `jobs.json` edits, no fallback transport.

Stop after Companies planning artifacts and Human approvals. A fresh Plan Author must map current exact files, interfaces, runnable TDD snippets, official hash/install/update behavior, validators, and commits. This Skills plan does not approve that implementation.

- [ ] **Step 5: Require a subsequent live runbook / execution plan**

Only after Companies approval and repository delivery, require Companies owning repo durable artifacts:

- `knowledge/wiki/goals/task-management-hermes-readiness/managed-native-runbook.md`;
- `knowledge/wiki/goals/task-management-hermes-readiness/live-github-mcp-runbook.md`;
- `knowledge/wiki/goals/task-management-hermes-readiness/readiness-receipt-template.md`;
- `knowledge/wiki/goals/task-management-hermes-readiness/operator-handoff.md`.

The live plan must have three authorization Gates:

1. **Read-only Inventory Gate:** Schedule Secretary identity, native skill discovery, installed revision/hash evidence, caller defaults, MCP registration, exact tools and advertised JSON schema hashes, authenticated identity category, authoritative permission evidence if available, target/schema readback, pagination/continuation, `mutation_performed=false`. Unknown write permission remains `partial`; do not write as a probe.
2. **Live Setup Gate:** separate exact-target approval; dry-run when supported, otherwise exact proposed before/after categories; apply; status; exact readback; partial-success remaining-only resume; rollback evidence.
3. **Live Task Write Gate:** another separate approval for one exact Issue/Project operation, target, residual/cleanup policy, and partial-failure handling. Never compensating-delete a successful side.

Repository completion, installed/discovered state, read-only live readiness, setup verification, and task-write verification remain independent completion states.

- [ ] **Step 6: Validate handoff discoverability and commit**

```bash
rg -n \
  "338e0c1e192949c352a1fdd6deec1231ad495f19b68729e2aff3f330356ced4f|088b91669813649363ddda28ea3d45387b92dbc3|Companies Written Spec Gate|Read-only Inventory Gate|Live Setup Gate|Live Task Write Gate|mutation_performed=false" \
  knowledge/wiki/syntheses/task-management-hermes-readiness/cross-repo-handoff.md
git diff --check
git add \
  knowledge/wiki/syntheses/task-management-hermes-readiness/cross-repo-handoff.md \
  knowledge/index.md \
  knowledge/log.md
git commit -m "docs: hand off task readiness delivery"
```

Expected: every required binding/Gate is found, diff check passes, and the commit changes only the handoff/index/log. Return with Companies implementation and live work explicitly unperformed.

---

## Writing-plans self-review

### Spec coverage

- Every approved operation capability row and retry-side preflight: Task 1 parsed tables and all-row fixture.
- Canonical identity, page merge, ordinary missing/null preservation, provider explicit clear, repeated/updated/conflicting observation, same-item/different-task isolation, deterministic order: Task 2 oracle and fixtures.
- 50/51 unique boundary and lossless continuation: Task 2 exact envelopes; the fetched overshoot page contributes to raw count, is deferred using its unchanged incoming cursor, and a second call returns all 51 canonical identities exactly once.
- Status wording, source exhaustion, complete/partial, duplicate create stop: Task 3.
- Done / Cancelled, both partial orders, explicit/bare reopen, exact five-status non-terminal allowlist, terminal/unknown blocked targets, remaining-only retry: Task 4.
- Per-operation native metadata before/change/after preservation, including existing-Issue registration, and secret-specific boundary: Task 5.
- Companies source/hash/install/discovery/default/readiness, official receipts, live inventory/setup/task-write requirements remain discoverable without pre-approval implementation: Task 6 handoff.

### Placeholder and interface review

- Executable Skills snippets define every helper they invoke.
- Fixture tests derive capability requirements from Markdown, compute reconciliation envelopes, execute transitions, and compare full metadata states.
- `EXPECTED_FILES` is updated with each created fixture and shown as a complete final set.
- No Companies production interface, hash algorithm, command, or live tool name is invented before its own Gates.
- No unresolved implementation marker or abbreviated function body remains.

### Scope review

This executable plan ends at Skills portable implementation plus cross-repository handoff. It does not implement or approve Companies production changes, managed-native apply, live configuration/permission/schema changes, or GitHub task writes.
