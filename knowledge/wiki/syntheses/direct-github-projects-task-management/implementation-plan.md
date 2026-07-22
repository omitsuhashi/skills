# GitHub Projects Direct Task Management Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the backend-neutral task-management plugin with a host-neutral standalone skill that operates GitHub Issues and one caller-selected GitHub Project directly through GitHub MCP.

**Architecture:** Keep task state entirely in GitHub: Issue content belongs to the selected repository, while Project membership and workflow fields belong to the caller-selected Project. The skill contains only Markdown operating contracts and standard-library contract tests; it owns no runtime facade, adapter, provider client, credentials, or task state.

**Tech Stack:** Markdown `SKILL.md` and references, Python 3.9 / 3.12 standard-library `unittest`, GitHub MCP semantic capabilities, Git, repository validators.

## Global Constraints

- Use approved spec path `knowledge/wiki/syntheses/direct-github-projects-task-management/spec.md` with raw-byte SHA-256 `9200996f2ed046ecb351fad96930c6e4e9a1580fdde14472ecc8b68b98f36c94`.
- Use approved Issue ledger `knowledge/wiki/syntheses/direct-github-projects-task-management/issues.md`; do not change Issue IDs, dependencies, acceptance criteria, non-goals, or write scopes during execution.
- Keep `delivery_intent=local_only`; do not push, create or update a PR, mirror GitHub Issues, mutate a live GitHub Project, install a skill, release, or merge.
- Do not modify, delete, or stage the unrelated untracked file `skills/llm-wiki/DESCRIPTION.md`.
- Do not edit approved `spec.md` or sealed `input-packet.json` during implementation.
- Create no production Python, plugin manifest, backend config, provider adapter, local task state, or credential file under `skills/task-management/`.
- Keep `skills/task-management/**` user-facing prose free of named agent hosts, dedicated host toolsets, host-specific install commands, and host profile paths.
- Use GitHub MCP directly; do not add `gh`, REST, GraphQL, browser automation, or local backend fallbacks.
- Each caller normally provides one canonical default `project_url`; invocation override is explicit and never becomes multi-Project routing.
- Treat the Issue repository as the work-unit boundary; do not create a duplicate work-unit Project field.
- Load `superpowers:test-driven-development` before each production implementation task. Show RED before GREEN, run focused verification, commit the reviewed task, then release its dependent.

---

## File responsibility map

- `skills/task-management/SKILL.md`: trigger, reference router, direct-MCP boundaries, concise default flow.
- `skills/task-management/references/core.md`: caller input contract plus Project and repository resolution order.
- `skills/task-management/references/github-projects.md`: Project item model, semantic capabilities, fields, terminal transitions, setup boundary.
- `skills/task-management/references/issue-contract.md`: Issue title/body/content rules and duplicate handling.
- `skills/task-management/references/safety-and-failures.md`: automatic versus confirmed mutations, fail-closed errors, partial-success continuation.
- `skills/task-management/tests/test_task_management_contract.py`: executable static contract for all standalone skill behavior and prohibited architecture.
- `.github/workflows/skill-architecture.yml`: Python 3.9 / 3.12 CI invocation for the standalone tests.
- `scripts/test_dual_host_ci_workflow.py`: repository test that pins the new CI command without requiring host-specific task-management prose.
- `scripts/test_loop_autonomous_gates_ledger.py`: repository test that maps autonomous-gate evidence to the new approval/capability contract rather than deleted adapter tests.
- `plugins/task-management/`: delete the entire former plugin implementation after the replacement skill passes focused validation.
- `knowledge/index.md`, `knowledge/log.md`, `knowledge/wiki/syntheses/direct-github-projects-task-management/issues.md`: active-contract discovery and append-only implementation evidence.

---

### Task 1 / DGPTM-001: Scaffold and pin the standalone skill contract

**Files:**

- Create: `skills/task-management/SKILL.md`
- Create: `skills/task-management/references/core.md`
- Create: `skills/task-management/tests/test_task_management_contract.py`
- Delete after scaffold: `skills/task-management/agents/openai.yaml`

**Interfaces:**

- Consumes: caller logical inputs `project_url` and optional `inbox_repository` from the approved spec.
- Produces: standalone `task-management` skill root and the shared `TaskManagementContractTests` test surface used by DGPTM-002 and DGPTM-003.

- [ ] **Step 1: Run the required skill-creator scaffold**

Run from the repository root:

```bash
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  task-management \
  --path skills \
  --resources references \
  --interface 'display_name=Task Management' \
  --interface 'short_description=Manage GitHub Project tasks through GitHub MCP' \
  --interface 'default_prompt=Use $task-management to manage this task in the configured GitHub Project.'
mkdir -p skills/task-management/tests
```

Expected: `skills/task-management/` is created once. If the directory already exists, stop and inspect it instead of overwriting it.

Delete the generated `skills/task-management/agents/openai.yaml` with `apply_patch`, then run `rmdir skills/task-management/agents` after confirming the directory is empty. This approved skill has no host-specific metadata. Do not create `description.md` or `DESCRIPTION.md`.

- [ ] **Step 2: Write the initial failing contract test**

Replace `skills/task-management/tests/test_task_management_contract.py` with:

```python
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "task-management"
SKILL = SKILL_ROOT / "SKILL.md"
CORE = SKILL_ROOT / "references" / "core.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TaskManagementContractTests(unittest.TestCase):
    def test_standalone_structure_and_frontmatter(self) -> None:
        self.assertTrue(SKILL.is_file())
        self.assertTrue(CORE.is_file())
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/task-management/tests
```

Expected: FAIL because the scaffold has no completed `references/core.md` contract and its generated `SKILL.md` does not contain the approved caller/Issue model.

- [ ] **Step 4: Write the minimum standalone entrypoint**

Replace `skills/task-management/SKILL.md` with:

```markdown
---
name: task-management
description: Use when creating, finding, updating, prioritizing, or completing GitHub Issue-backed tasks collected in one caller-selected GitHub Project through GitHub MCP.
---

# Task Management

Manage task content as GitHub Issues and portfolio state as Project items. Use GitHub MCP directly.

## References

- Read `references/core.md` before resolving the caller's Project or the Issue repository.

## Required boundary

- Accept `project_url` from the invocation, caller default, or established session context.
- Accept optional `inbox_repository` only for repository-independent or unclassified tasks.
- Each caller normally supplies one canonical default Project. An explicit invocation override applies only to that operation.
- Store each task as a GitHub Issue. The Issue repository is the work unit boundary.
- Stop when the target cannot be resolved confidently. Do not invent a destination.
```

Create `skills/task-management/references/core.md` with:

```markdown
# Core Contract

## Caller input

- `project_url`: URL of the one canonical default Project selected by the caller, or an explicit invocation override.
- `inbox_repository`: optional `OWNER/REPOSITORY` used only when the task is genuinely repository-independent or unclassified.

The skill stores neither value. Caller-owned configuration, invocation context, and established session context supply them.

## Task identity

- A task is a GitHub Issue added to the selected Project through GitHub MCP.
- The repository is the work unit boundary and remains the source of repository ownership.
- Project membership and Project fields remain the source of portfolio workflow state.
- Do not create Project-native draft tasks or duplicate repository identity in a custom field.
```

- [ ] **Step 5: Run GREEN and validate the skill**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-management
rg -n --glob '!**/tests/**' "Hermes|Codex|task-management-read|task_adapter__|work_unit_id" skills/task-management
git diff --check
```

Expected: unittest and validator exit 0; both `rg` and `git diff --check` emit no findings.

- [ ] **Step 6: Commit DGPTM-001**

Stage only `skills/task-management/`, confirm `skills/llm-wiki/DESCRIPTION.md` is absent from the index, and commit:

```bash
git add skills/task-management
git diff --cached --check
git commit -m "feat: add standalone task management skill contract"
```

Expected: one scoped local commit; no remote write.

---

### Task 2 / DGPTM-002: Implement the direct GitHub MCP workflow and safety contract

**Files:**

- Modify: `skills/task-management/SKILL.md`
- Modify: `skills/task-management/references/core.md`
- Create: `skills/task-management/references/github-projects.md`
- Create: `skills/task-management/references/issue-contract.md`
- Create: `skills/task-management/references/safety-and-failures.md`
- Modify: `skills/task-management/tests/test_task_management_contract.py`

**Interfaces:**

- Consumes: DGPTM-001 `SKILL.md`, caller input names, Issue-backed identity, repository work-unit boundary.
- Produces: ordered target/repository resolution, Issue/Project field contract, approval policy, semantic capability check, and idempotent partial-failure continuation.

- [ ] **Step 1: Add failing behavior-contract tests**

Add these constants below `CORE` in `test_task_management_contract.py`:

```python
PROJECTS = SKILL_ROOT / "references" / "github-projects.md"
ISSUES = SKILL_ROOT / "references" / "issue-contract.md"
SAFETY = SKILL_ROOT / "references" / "safety-and-failures.md"
```

Add these methods to `TaskManagementContractTests`:

```python
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
        for steps in (project_steps, repository_steps):
            positions = [text.index(step) for step in steps]
            self.assertEqual(sorted(positions), positions)
        self.assertIn("Never use inbox as an ambiguity fallback", text)

    def test_issue_and_project_fields_are_exact(self) -> None:
        project_text = read(PROJECTS)
        issue_text = read(ISSUES)
        for status in (
            "Inbox",
            "Backlog",
            "Ready",
            "In progress",
            "Blocked",
            "Done",
            "Cancelled",
        ):
            self.assertIn(f"`{status}`", project_text)
        for priority in ("P0", "P1", "P2", "P3"):
            self.assertIn(f"`{priority}`", project_text)
        self.assertIn("`Due date`", project_text)
        self.assertIn("close reason `completed`", project_text)
        self.assertIn("close reason `not planned`", project_text)
        for heading in (
            "## Outcome",
            "## Context",
            "## Acceptance criteria",
            "## References",
        ):
            self.assertIn(heading, issue_text)

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
            "Issue read, search, create, update, and comment",
            "Project read, item add, and field update",
            "Do not fall back to a CLI, direct API client, browser automation, or local backend",
            "Do not delete the created Issue",
            "Continue only the unfinished steps",
            "Do not create a duplicate Issue",
        ):
            self.assertIn(required, text)
```

- [ ] **Step 2: Run RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/task-management/tests
```

Expected: FAIL because three references and their ordered behavior are absent.

- [ ] **Step 3: Replace the entrypoint with the final router**

Replace `skills/task-management/SKILL.md` with:

```markdown
---
name: task-management
description: Use when creating, finding, updating, prioritizing, commenting on, or completing GitHub Issue-backed tasks collected in one caller-selected GitHub Project through GitHub MCP.
---

# Task Management

Manage task content as GitHub Issues and portfolio state as Project items. Use available GitHub MCP capabilities directly.

## References

- Read `references/core.md` before resolving the caller's Project or Issue repository.
- Read `references/github-projects.md` before adding an Issue to the Project, changing fields, completing a task, or checking capabilities.
- Read `references/issue-contract.md` before creating an Issue or deciding whether an existing Issue is the same task.
- Read `references/safety-and-failures.md` before any write, destructive operation, bulk change, or recovery from a partial failure.

## Boundaries

- Accept `project_url` from the invocation, caller default, or established session context. Do not store a user-specific default in this skill.
- Accept optional `inbox_repository` only for repository-independent or unclassified tasks.
- Keep one canonical default Project per caller. An explicit invocation override applies only to that operation.
- Store every task as a GitHub Issue. The Issue repository is the work unit boundary.
- Use GitHub MCP directly. Do not route through a facade, adapter, provider-neutral schema, CLI, direct API client, browser automation, or local backend.
- Do not own credentials, MCP registration, Project creation, repository creation, or normal-operation schema repair.

## Default flow

1. Determine the requested outcome and observable acceptance criteria.
2. Resolve the Project and Issue repository using `references/core.md`.
3. Check the semantic GitHub MCP capabilities required for the operation.
4. Search read-only for an obvious existing Issue before creating a task.
5. Create or reuse the Issue according to `references/issue-contract.md`.
6. Add the Issue to the selected Project and set the requested fields; otherwise use `Status=Inbox`, `Priority=P2`, and no due date.
7. Apply `references/safety-and-failures.md` before mutation and after any partial success.
8. Return the Issue URL, repository, Project URL, completed steps, and unfinished steps.

Stop before writing when the Project, repository, task outcome, acceptance criteria, capability, authentication, permission, or schema is not reliable enough to proceed.
```

- [ ] **Step 4: Write the ordered resolution contract**

Replace `skills/task-management/references/core.md` with:

```markdown
# Core Contract

## Caller input

- `project_url`: URL of the one canonical default Project selected by the caller, or an explicit invocation override.
- `inbox_repository`: optional `OWNER/REPOSITORY` used only when the task is genuinely repository-independent or unclassified.

The skill stores neither value. Caller-owned configuration, invocation context, and established session context supply them. An invocation override never changes the caller default and never enables automatic routing across multiple Projects.

## Project resolution order

1. Invocation `project_url`.
2. Caller default `project_url`.
3. Session-established Project.
4. Unique open Project discovery through a read-only GitHub MCP capability, only when no owner, visibility, closed-state, or template conflict exists.
5. Ask the user when more than one candidate remains or the authenticated owner is unclear.

Accept personal `/users/<owner>/projects/<number>` and organization `/orgs/<owner>/projects/<number>` URLs. Interpret the owner-scoped number only when an MCP operation requires it. Never select a state-changing target from title or recency alone, and never substitute another Project after an invalid URL or permission failure.

## Repository resolution order

1. Explicit repository from the user.
2. Current repository when the task directly concerns that repository.
3. Unique referenced repository derived from one Issue, PR, durable specification, or code target.
4. Configured inbox when the task is repository-independent or deliberately unclassified.
5. Ask the user when repositories conflict or attribution remains uncertain.

Never use inbox as an ambiguity fallback. The repository is the work unit boundary. GitHub's repository metadata is the grouping key; do not duplicate it in a custom Project field.

## Read and write identity

- A task is a GitHub Issue added to the selected Project through GitHub MCP.
- Issue title and body are the source of task content.
- Project membership, Status, Priority, and Due date are the source of portfolio workflow state.
- One operation targets one resolved Project and one resolved Issue repository.
```

- [ ] **Step 5: Write the Project and capability contract**

Create `skills/task-management/references/github-projects.md` with:

```markdown
# GitHub Projects Contract

## Semantic capability check

Before a write, confirm these available GitHub MCP operations and target permissions:

- Issue read, search, create, update, and comment.
- Project read, item add, and field update.
- Access to the resolved owner, repository, Project, and relevant private content.

Tool names may differ by host integration. Match semantic capabilities, but use only GitHub MCP. Do not fall back to a CLI, direct API client, browser automation, or local backend.

## Project item model

- Create or reuse a GitHub Issue before adding it to the Project.
- Do not use a Project-native draft item as the task source of truth.
- Keep completed and cancelled items in the Project for history.
- Do not create a Project, repository, field, option, view, or workflow as a side effect of normal task operations.

## Fields

`Status` options:

- `Inbox`: untriaged.
- `Backlog`: accepted but unscheduled.
- `Ready`: actionable.
- `In progress`: active work.
- `Blocked`: waiting on an external condition.
- `Done`: completed.
- `Cancelled`: intentionally not completed.

`Priority` options:

- `P0`: immediate.
- `P1`: high.
- `P2`: normal and the default when unspecified.
- `P3`: low.

`Due date` is optional. Leave it empty when no reliable deadline exists. Use GitHub-native repository, assignee, label, milestone, Issue type, and parent/sub-issue information instead of duplicate custom fields.

## Terminal transitions

- `Done` maps to Issue close reason `completed`.
- `Cancelled` maps to Issue close reason `not planned`.
- Treat the Project Status and Issue close as one logical transition.
- Keep the item in the Project; do not remove or archive it.
- When an externally closed Issue has a reliable close reason, reconcile the Project Status as a safe non-destructive update.
- If only one side succeeds, report the mismatch and continue only the unfinished side after applying the safety contract.

## Setup boundary

If fields or options are missing, stop normal task writing and report the exact schema difference. Create or repair schema only in a separately requested setup operation with confirmed GitHub MCP capability and permission. Never silently remap a field by a similar name.
```

- [ ] **Step 6: Write the Issue contract**

Create `skills/task-management/references/issue-contract.md` with:

````markdown
# Issue Contract

## Title

Write the observable result, not an internal activity label. Keep the title concise enough to scan in Project views.

## Body

```markdown
## Outcome
The result this Issue must achieve.

## Context
Why the work is needed and the confirmed decision context.

## Acceptance criteria
- [ ] An observable completion condition.

## References
Related Issues, PRs, durable specifications, files, or confirmed external references.
```

Do not store raw conversation transcripts, internal prompts, hidden reasoning, credentials, or agent names. Prefer durable repository references for implementation work. Use existing repository labels and Issue types rather than imposing a global taxonomy.

## Creation gate

Do not create the Issue when the outcome or acceptance criteria cannot support an observable completion decision. Ask one decision-changing question and then resume.

## Duplicate handling

Search open Issues and current Project items read-only before creation. Reuse an Issue only when repository, outcome, and references make identity high-confidence. Similar titles alone are not sufficient. After a partial failure, resume from the returned Issue URL and never create a second Issue for the same operation.
````

- [ ] **Step 7: Write the approval and failure contract**

Create `skills/task-management/references/safety-and-failures.md` with:

```markdown
# Safety And Failures

## Approval policy

- High-confidence safe single-item writes run automatically.
- Uncertain target or content requires confirmation.
- Destructive or bulk mutation requires confirmation.
- An explicit user instruction is the approval for that exact operation. Do not ask twice.

Safe automatic operations include reads, searches, capability checks, a high-confidence single Issue create/edit/comment, adding that Issue to the resolved Project, non-terminal field updates, and repair of Project Status after an already closed Issue with a reliable reason.

Confirmation is required for ambiguous Project or repository selection, unclear outcome or acceptance criteria, inferred close/transfer/delete, Project item removal/archive, destructive body replacement, Project schema or visibility change, private-content exposure, and multi-Issue mutation. If an explicit instruction reveals a different target, unexpected permission identity, or unexpectedly large item count, stop and reconfirm.

## Fail closed

- Missing MCP: name GitHub MCP as unavailable.
- Missing capability: list the absent Issue or Projects operation.
- Authentication or permission failure: name the target and rejected operation without requesting or storing a credential.
- Schema mismatch: list missing fields or options and route to separate setup.
- Ambiguous result: show candidates without writing.

Do not fall back to a CLI, direct API client, browser automation, or local backend.

## Partial success

If Issue creation succeeds but Project add or field update fails, do not delete the created Issue. Return its URL, successful steps, unfinished steps, and the safe resume action. On retry, continue only the unfinished steps and do not create a duplicate Issue.

If Issue close and terminal Project Status diverge, do not roll back the successful side automatically. Report the mismatch and complete only the missing side after the applicable confirmation rule.
```

- [ ] **Step 8: Run GREEN, static checks, and validator**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --skill skills/task-management
rg -n --glob '!**/tests/**' "Hermes|Codex|task-management-read|task_adapter__|mcp__<server>__task_query|work_unit_id" skills/task-management
find skills/task-management -path '*/tests/*' -prune -o -name '*.py' -print
git diff --check
```

Expected: Python commands exit 0; `rg`, `find`, and `git diff --check` emit no findings.

- [ ] **Step 9: Commit DGPTM-002**

```bash
git add skills/task-management
git diff --cached --check
git commit -m "feat: define direct GitHub Projects task workflow"
```

Expected: one scoped local commit based on reviewed DGPTM-001; no remote write.

---

### Task 3 / DGPTM-003: Remove the plugin and migrate CI contracts

**Files:**

- Delete: every tracked file under `plugins/task-management/`
- Modify: `.github/workflows/skill-architecture.yml:70-74`
- Replace: `scripts/test_dual_host_ci_workflow.py:1-50`
- Modify: `scripts/test_loop_autonomous_gates_ledger.py:12-40`
- Verify: `skills/task-management/tests/test_task_management_contract.py`

**Interfaces:**

- Consumes: passing standalone contract from DGPTM-002.
- Produces: repository CI and regression checks that depend only on `skills/task-management/`; removes all runtime plugin surfaces.

- [ ] **Step 1: Resolve the exact destructive target**

Run:

```bash
git ls-files plugins/task-management
git status --short plugins/task-management
```

Expected: the tracked list matches the current plugin tree and the second command is empty. If untracked or modified user files appear under the target, stop instead of deleting them.

The deletion set is exactly:

```text
plugins/task-management/.codex-plugin/plugin.json
plugins/task-management/README.md
plugins/task-management/__init__.py
plugins/task-management/config/task-backends.example.toml
plugins/task-management/examples/.gitkeep
plugins/task-management/examples/hermes-github-mcp-enable.example.md
plugins/task-management/examples/task-create-preview.example.md
plugins/task-management/plugin.yaml
plugins/task-management/scripts/smoke_test_hermes_read.py
plugins/task-management/skills/task-management/SKILL.md
plugins/task-management/skills/task-management/agents/openai.yaml
plugins/task-management/skills/task-management/references/adapter-dispatch.md
plugins/task-management/skills/task-management/references/backend-routing.md
plugins/task-management/skills/task-management/references/decision-support-policy.md
plugins/task-management/skills/task-management/references/github-mcp-projects.md
plugins/task-management/skills/task-management/references/hermes-mcp-governance.md
plugins/task-management/skills/task-management/references/routing-flow.md
plugins/task-management/skills/task-management/references/task-contracts.md
plugins/task-management/skills/task-management/references/task-draft-contract.md
plugins/task-management/skills/task-management/references/task-read-adapter.md
plugins/task-management/task_management/__init__.py
plugins/task-management/task_management/provider_adapters/__init__.py
plugins/task-management/task_management/provider_adapters/external_tool.py
plugins/task-management/task_management/provider_adapters/local_json.py
plugins/task-management/task_management/read_adapter.py
plugins/task-management/task_management/route_config.py
plugins/task-management/tests/.gitkeep
plugins/task-management/tests/fixtures/backend-destination.example.json
plugins/task-management/tests/fixtures/backend-route.example.json
plugins/task-management/tests/fixtures/github_mcp_route/adapter-results.json
plugins/task-management/tests/fixtures/github_mcp_route/preflight-results.json
plugins/task-management/tests/fixtures/local_tasks.json
plugins/task-management/tests/fixtures/task-draft.example.json
plugins/task-management/tests/fixtures/task-query.example.json
plugins/task-management/tests/fixtures/task-ref.example.json
plugins/task-management/tests/fixtures/task-snapshot.example.json
plugins/task-management/tests/fixtures/task-write-result.example.json
plugins/task-management/tests/test_adapter_dispatch.py
plugins/task-management/tests/test_backend_routing.py
plugins/task-management/tests/test_decision_support_policy.py
plugins/task-management/tests/test_github_mcp_route.py
plugins/task-management/tests/test_hermes_plugin_manifest.py
plugins/task-management/tests/test_task_contracts.py
plugins/task-management/tests/test_task_draft_examples.py
plugins/task-management/tests/test_task_read_adapter.py
plugins/task-management/tests/test_task_read_routes.py
plugins/task-management/tests/test_work_unit_preview.py
```

- [ ] **Step 2: Rewrite the CI test first**

Replace `scripts/test_dual_host_ci_workflow.py` with:

```python
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "skill-architecture.yml"
TASK_MANAGEMENT_TEST = (
    REPO_ROOT
    / "skills"
    / "task-management"
    / "tests"
    / "test_task_management_contract.py"
)


class DualHostCiWorkflowTests(unittest.TestCase):
    def test_python_matrix_runs_standalone_skill_contracts(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('python-version:\n          - "3.9"\n          - "3.12"', text)
        self.assertIn("Run decide-in-order tests", text)
        self.assertIn(
            "python3 -m unittest discover -s skills/decide-in-order/tests", text
        )
        self.assertIn("Run task-management tests", text)
        self.assertIn(
            "python3 -m unittest discover -s skills/task-management/tests", text
        )
        self.assertNotIn("plugins/task-management", text)

    def test_task_management_contract_is_host_neutral(self) -> None:
        text = TASK_MANAGEMENT_TEST.read_text(encoding="utf-8")
        self.assertIn("test_skill_has_no_host_specific_or_runtime_surface", text)
        self.assertIn("test_capability_and_partial_failures_are_fail_closed", text)


if __name__ == "__main__":
    unittest.main()
```

In `scripts/test_loop_autonomous_gates_ledger.py`, replace lines 7-40 with this exact block and keep the remaining ledger tests unchanged:

```python
REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "knowledge/wiki/syntheses/loop-skill-autonomous-gates-issues.md"
INDEX = REPO_ROOT / "knowledge/index.md"
LOG = REPO_ROOT / "knowledge/log.md"
GRILL_TESTS = REPO_ROOT / "skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py"
TASK_CONTRACT_TESTS = (
    REPO_ROOT
    / "skills"
    / "task-management"
    / "tests"
    / "test_task_management_contract.py"
)
DELIVERY_TESTS = REPO_ROOT / "skills/issue-implementation-loop/tests/test_delivery.py"


class LoopAutonomousGatesLedgerTests(unittest.TestCase):
    def test_regression_tests_pin_all_autonomous_gate_contracts(self) -> None:
        grill_text = GRILL_TESTS.read_text(encoding="utf-8")
        task_text = TASK_CONTRACT_TESTS.read_text(encoding="utf-8")
        delivery_text = DELIVERY_TESTS.read_text(encoding="utf-8")

        for required in (
            "test_gate_taxonomy_separates_human_preflight_and_remote_boundaries",
            "test_execution_plan_gate_auto_continue_keeps_evidence_and_stop_conditions",
        ):
            self.assertIn(required, grill_text)

        for required in (
            "test_approval_policy_distinguishes_safe_uncertain_and_destructive",
            "test_capability_and_partial_failures_are_fail_closed",
        ):
            self.assertIn(required, task_text)

        self.assertIn(
            "test_validate_delivery_plan_requires_approved_final_pr_actions",
            delivery_text,
        )
        self.assertIn(
            "test_validate_delivery_plan_rejects_ready_final_pr_creation",
            delivery_text,
        )
```

Remove the two deleted plugin test constants and their reads.

- [ ] **Step 3: Run RED against the current workflow**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/test_dual_host_ci_workflow.py
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/test_loop_autonomous_gates_ledger.py
```

Expected: the CI workflow test fails because `.github/workflows/skill-architecture.yml` still invokes the plugin tests. The autonomous-gates test passes against the DGPTM-002 contract test.

- [ ] **Step 4: Replace the workflow steps**

Replace `.github/workflows/skill-architecture.yml:70-74` with:

```yaml
      - name: Run task-management tests
        run: PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/task-management/tests
```

- [ ] **Step 5: Delete the resolved plugin tree with apply_patch**

Delete only the files listed in Step 1. Do not use a broad recursive target and do not touch `plugins/AGENTS.md` or another plugin. Confirm afterward:

```bash
test ! -e plugins/task-management
git status --short
```

Expected: the former tracked plugin files are deleted, the new standalone skill remains, and `skills/llm-wiki/DESCRIPTION.md` remains untracked and unstaged.

- [ ] **Step 6: Run GREEN and repository-focused regression**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/test_dual_host_ci_workflow.py
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/test_loop_autonomous_gates_ledger.py
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/decide-in-order/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --skill skills/task-management
rg -n "plugins/task-management|task-management-read" .github/workflows skills/task-management --glob '!**/tests/**'
git diff --check
```

Expected: Python commands exit 0; `test ! -e`, `rg`, and `git diff --check` report no issue.

- [ ] **Step 7: Commit DGPTM-003**

Stage exactly the resolved plugin deletions, workflow, two repository tests, and any DGPTM-003 test assertion change:

```bash
git add plugins/task-management .github/workflows/skill-architecture.yml scripts/test_dual_host_ci_workflow.py scripts/test_loop_autonomous_gates_ledger.py skills/task-management/tests
git diff --cached --check
git commit -m "refactor: replace task management plugin with skill"
```

Expected: one scoped local migration commit; no remote write.

---

### Task 4 / DGPTM-004: Switch active knowledge and complete integration verification

**Files:**

- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`
- Modify: `knowledge/wiki/syntheses/direct-github-projects-task-management/issues.md`

**Interfaces:**

- Consumes: reviewed DGPTM-001 through DGPTM-003 commits, approved planning artifacts, standalone skill tests.
- Produces: current knowledge discovery, fresh forward-test evidence, repository-wide validation evidence, and local implementation closeout.

- [ ] **Step 1: Demonstrate stale active discovery before editing it**

Run:

```bash
rg -n "Portfolio OS Task Backend Plugin Skill|Task Management Provider Adapters|POTASK-011" knowledge/index.md
```

Expected: current index entries still present the former plugin spec, ledger, packet, adapter plan, or execution artifacts as active pages.

- [ ] **Step 2: Update current knowledge without altering historical artifacts**

In `knowledge/index.md`:

- Keep the four current Epic entries for `spec.md`, `issues.md`, `implementation-plan.md`, and `input-packet.json`.
- Remove active catalog entries for the former Portfolio OS task backend source summary, plugin spec, plugin Issue ledger, plugin Input Packet, provider-adapter implementation plan, POTASK-011 Input Packet, and POTASK-011 Execution Envelope.
- Keep `decide-in-order` as a standalone current skill, but change its two index summaries so the former plugin integration is explicitly historical and the skill itself owns no task storage.

The two current `decide-in-order` entries must read:

```markdown
- [Decide In Order Skill 設計](wiki/syntheses/decide-in-order-skill-design.md) — 独立state-free skillの判断順序、適応的表示、DecisionRecordを記録する設計。旧task-management plugin integrationはhistoricalであり、current skillはtask storageを所有しない。
  検索語: decide-in-order, decision support, DecisionFrame, DecisionRecord, light, deep, review, standalone skill, 決める順番, 意思決定支援, 日次計画, 継続判断, 調査方針, 許容損失
- [Decide In Order Skill 実装計画](wiki/syntheses/2026-07-17-decide-in-order-implementation-plan.md) — standalone decision skillのtest-first実装とforward testを記録するhistorical plan。旧task-management plugin integrationはcurrent task contractではない。
  検索語: decide-in-order, implementation plan, skill-creator, forward test, contract test, TDD, standalone skill, 実装計画, 意思決定支援, 回帰検証
```

Do not edit the old spec, ledger, plan, Input Packet, Execution Envelope, or source summary bytes. The approved new spec already links them as historical evidence.

- [ ] **Step 3: Forward-test with fresh read-only evaluators**

Use fresh subagents only as evaluation surfaces. Give them the current `skills/task-management/SKILL.md` path and no design transcript or expected answer. Do not permit live MCP calls or file writes.

Evaluator A receives these requests:

```text
1. 既定Projectと現在のrepositoryが分かっている状態で、新しい実装taskを登録したい。
2. 今回だけ既定とは別のProject URLを指定してtaskを登録したい。
3. 参照可能なProjectが複数あるが、どれを使うか指定していない。
4. 1件のIssue作成には成功したが、Project追加が失敗した。再実行したい。
```

Evaluator B receives these requests:

```text
1. 2つのrepositoryにまたがる内容で、保存先を決める根拠がないtaskを登録したい。
2. repositoryに属さない事務taskをconfigured inboxへ登録したい。
3. ユーザーが明示的にtask完了を指示した。
4. checklistが埋まっているので、agentの推定だけでtaskを完了扱いにしたい。
```

Controller evaluation criteria:

- Project and repository resolution follow the documented order.
- Clear safe writes proceed without an extra confirmation.
- Ambiguous targets and inferred terminal changes stop for one confirmation.
- Explicit terminal instruction is not confirmed twice.
- Inbox is used only for repository-independent/unclassified work.
- Partial failure resumes from the existing Issue and never deletes or duplicates it.
- No response invents a live result or proposes a non-MCP fallback.

Require all eight scenarios to pass. If any fails, return to the owning Issue, add a failing contract test, fix the skill, rerun focused tests, and re-evaluate the failed scenario before final verification. Store only a concise pass/fail summary in the ledger; do not commit raw evaluator transcripts.

- [ ] **Step 4: Run complete local verification**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/decide-in-order/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts -p 'test_*.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --skill skills/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-management
test ! -e plugins/task-management
rg -n --glob '!**/tests/**' "Hermes|Codex|task-management-read|task_adapter__|mcp__<server>__task_query|work_unit_id" skills/task-management
rg -n "Portfolio OS Task Backend Plugin Skill|Task Management Provider Adapters|POTASK-011" knowledge/index.md
git diff --check
```

Expected: all Python commands exit 0; `test ! -e` succeeds; both `rg` commands and `git diff --check` emit no findings. Repository-wide `--all` compatibility may still report the pre-existing unrelated `skills/llm-wiki/DESCRIPTION.md`; the scoped `--skill skills/task-management` result is the acceptance gate and the unrelated file remains untouched.

- [ ] **Step 5: Record observed evidence and close the local ledger**

Update the Issue table in `issues.md` in dependency order:

- DGPTM-001 through DGPTM-004: Gate `承認済み`, execution `完了`.
- Record each reviewed local commit and review result in a new `最終実装証跡` section.
- Record the eight-scenario forward-test pass count, exact verification commands, pass/fail results, remaining risk, and `local_only` remote state.

Append one `implementation-closeout` entry to `knowledge/log.md` naming the four Issue IDs, final reviewed commit, validation result, historical-artifact preservation, and unmodified unrelated file. Do not rewrite earlier gate entries.

- [ ] **Step 6: Commit DGPTM-004**

```bash
git add knowledge/index.md knowledge/log.md knowledge/wiki/syntheses/direct-github-projects-task-management/issues.md
git diff --cached --check
git commit -m "docs: close direct GitHub task management migration"
```

Expected: local branch contains four reviewed implementation commits plus planning gate commits; no push, PR, live GitHub mutation, install, release, or merge.

---

## Spec coverage map

| Approved spec responsibility | Implementing task |
|---|---|
| standalone skill、caller-owned target、Issue-backed identity、repository work-unit boundary | DGPTM-001 |
| Project / repository resolution、Issue contract、fields、terminal mapping | DGPTM-002 |
| high-confidence automation、confirmation boundaries、capability / partial-failure contract | DGPTM-002 |
| plugin facade / adapter / host-specific runtime removal、CI migration | DGPTM-003 |
| historical supersession、fresh evaluation、repository-wide verification | DGPTM-004 |
| no runtime fallback、no credential ownership、no live / remote mutation | Global Constraints and all four task verifications |

---

## Execution handoff

- Execution is serial because all four Issues form one dependency chain and DGPTM-001 / DGPTM-002 overlap `skills/task-management/`.
- Reserve epic base `codex/direct-github-projects-task-management/epic-base`; its immutable initial SHA is the Execution Plan Gate commit containing exact `spec.md` and sealed `input-packet.json` blobs.
- Reserve issue branches and base policies exactly as follows:

| Issue | Branch | Base policy |
|---|---|---|
| DGPTM-001 | `codex/direct-github-projects-task-management/dgptm-001-standalone-contract` | `epic_base` |
| DGPTM-002 | `codex/direct-github-projects-task-management/dgptm-002-direct-github-mcp` | `blocker_head: DGPTM-001` |
| DGPTM-003 | `codex/direct-github-projects-task-management/dgptm-003-plugin-removal` | `blocker_head: DGPTM-002` |
| DGPTM-004 | `codex/direct-github-projects-task-management/dgptm-004-integration-closeout` | `blocker_head: DGPTM-003` |

- Set `max_parallel=1`, `wave_is_barrier=true`, `worker_context_required=true`, `coordinator_may_implement=false`, and `serial_fallback_mode=worker_context_only`.
- Use `superpowers:requesting-code-review` as the primary task reviewer, repository `code-review` as fallback, and human review only when both are unavailable. Allow at most two review/fix cycles per Issue.
- Use `remote_write_policy.mode=local_only`; do not configure issue PRs or final PR actions in this execution.
- Keep the planning branch and approved planning artifacts read-only in issue worktrees.
- Review each committed Issue range before releasing the next dependency.
- Stop on approved spec / packet drift, overlapping unrelated changes, missing worker context, failed capability preflight, or any required remote/live mutation.
- After local closeout, report the branch and commits. Do not publish until a separate remote-delivery request.

## Related pages

- [Approved specification](spec.md)
- [Approved Issue ledger](issues.md)
- [Approved Spec Binding Contract](../approved-spec-binding-contract/spec.md)

## 出典

- [GitHub Projects 直接接続型 Task Management Skill 仕様](spec.md)
- [GitHub Projects 直接接続型 Task Management Skill Issue 台帳](issues.md)
