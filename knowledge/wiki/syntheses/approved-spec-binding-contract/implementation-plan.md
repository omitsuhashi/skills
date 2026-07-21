# Approved Spec Binding Artifact Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Group each Epic's durable planning artifacts under one tracked directory while keeping its instantiated execution context outside Git.

**Architecture:** Keep the sealed Input Packet as the tracked machine-readable approval lock beside the human-readable spec, ledger, and plans. Put Execution Envelope v4 and every downstream run artifact under the Git common runtime root. Enforce the ownership seam through Input Packet layout validation, skill instructions, repository tests, and a migrated current Epic fixture.

**Tech Stack:** Markdown skill contracts, Python 3 standard library, JSON Schema assets, `unittest`, Git.

## Global Constraints

- Preserve Input Packet v2 as the only machine-readable approval/execution-intent source of truth.
- Require `artifact_root` to end in the packet `epic_id`; keep spec, local issue sources, and sealed packet directly under that root.
- Keep Execution Envelope, runtime/event state, packets/reports, decisions, recovery, and delivery artifacts outside tracked worktrees.
- Keep schemas, templates, tests, and fixtures tracked as skill product assets.
- Preserve Codex/Hermes compatibility and current schema versions.
- Do not migrate unrelated historical flat artifacts.
- Push only `codex/approved-spec-binding-contract` and update Draft PR #32; do not ready, merge, release, or live-install.

---

### Task 1 / ASBC-007: Enforce the artifact ownership seam

**Files:**

- Modify: `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/approved_spec_binding.py`
- Modify: `skills/issue-implementation-loop/assets/templates/input-packet.json`
- Modify: `skills/issue-implementation-loop/tests/test_approved_spec_binding.py`
- Modify: `skills/issue-implementation-loop/tests/_helpers.py`
- Modify: `skills/grill-to-pr-loop/SKILL.md`
- Modify: `skills/grill-to-pr-loop/references/planning-contract.md`
- Modify: `skills/grill-to-pr-loop/references/execution-handoff.md`
- Modify: `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py`
- Modify: `skills/issue-implementation-loop/SKILL.md`
- Modify: `skills/issue-implementation-loop/references/execution-envelope.md`
- Modify: `skills/issue-implementation-loop/references/runtime-state.md`

**Interfaces:**

- Consumes: Input Packet v2 fields `epic_id`, `artifact_root`, `spec_binding.path`, `work_items[].source.path`.
- Produces: stable `ARTIFACT_LAYOUT_MISMATCH` with action `return_to_execution_plan_gate`; documented tracked/untracked artifact trees.

- [ ] **Step 1: Extend the public acceptance matrix and write failing layout tests**

Add ASB-31 through ASB-36 to `ASB_PUBLIC_ACCEPTANCE_MATRIX`. In `ApprovedSpecBindingTests`, use the existing temporary Git repository fixture and assert that these three mutations fail with `ARTIFACT_LAYOUT_MISMATCH`:

```python
cases = {
    "flat artifact root": {"artifact_root": "knowledge/wiki/syntheses"},
    "foreign epic root": {
        "artifact_root": "knowledge/wiki/syntheses/another-epic"
    },
    "ledger outside root": {
        "source_path": "knowledge/wiki/syntheses/shared/issues.md"
    },
}
```

Also assert that seal output outside `<artifact_root>` does not replace an existing sentinel file. Add a passing fixture rooted at `knowledge/wiki/syntheses/example/` with spec and issues directly inside it.

- [ ] **Step 2: Write the failing skill-contract test**

Add a test to `test_grill_to_pr_loop.py` that requires the combined planning/handoff/runtime guidance to contain:

```python
required = (
    "<durable-planning-root>/<epic-id>/",
    "spec.md",
    "issues.md",
    "implementation-plan.md",
    "input-packet.json",
    "$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/",
    "execution-envelope.json",
    "Do not commit instantiated execution artifacts",
)
```

The same test must assert that current guidance does not instruct planning to commit an Execution Envelope.

- [ ] **Step 3: Run RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_approved_spec_binding.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests -p 'test_grill_to_pr_loop.py'
```

Expected: layout cases are accepted or return the old `PATH_OUTSIDE_REPO`, the public matrix stops at ASB-30, and the planning guidance lacks the required per-Epic tree.

- [ ] **Step 4: Implement minimal fail-closed layout validation**

Add this stable action and a focused validator used by packet shape validation and seal/verify paths:

```python
DEFAULT_ACTIONS["ARTIFACT_LAYOUT_MISMATCH"] = "return_to_execution_plan_gate"


def _validate_artifact_layout(packet: Mapping[str, Any]) -> None:
    artifact_root = PurePosixPath(_parse_repo_path(packet["artifact_root"]))
    if artifact_root.name != packet["epic_id"]:
        raise BindingError("ARTIFACT_LAYOUT_MISMATCH", path=artifact_root.as_posix())
    paths = [packet["spec_binding"]["path"]]
    paths.extend(item["source"]["path"] for item in packet["work_items"])
    for value in paths:
        safe = PurePosixPath(_parse_repo_path(value))
        if safe.parent != artifact_root:
            raise BindingError("ARTIFACT_LAYOUT_MISMATCH", path=safe.as_posix())
```

Call `_validate_artifact_layout(packet)` after closed-shape work-item validation. Change the seal-output parent mismatch to `ARTIFACT_LAYOUT_MISMATCH`. During verified packet loading, require the pinned packet path's parent to equal `artifact_root` so a copied packet outside its Epic root cannot verify.

- [ ] **Step 5: Update reusable fixtures and templates**

Move current test fixture paths from flat examples to:

```text
knowledge/wiki/syntheses/example/spec.md
knowledge/wiki/syntheses/example/issues.md
knowledge/wiki/syntheses/example/input-packet.json
```

Update `assets/templates/input-packet.json` to the same generic per-Epic shape. Do not change schema versions or product-asset tracking.

- [ ] **Step 6: Update concise skill guidance**

In planning guidance, state the tracked tree once and link detailed lifecycle rules from the entrypoint. In execution guidance, state the untracked runtime tree once and include Envelope, runtime/events, reports/reviews, decisions/recovery, and delivery. Keep details in existing one-level references; do not add a new always-loaded reference.

- [ ] **Step 7: Run GREEN and commit ASBC-007**

Run the two focused suites from Step 3, then:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_*.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests -p 'test_*.py'
git diff --check
```

Expected: all commands exit 0. Commit message: `feat: separate durable and runtime epic artifacts`.

---

### Task 2 / ASBC-008: Migrate the active Epic and reseal it

**Files:**

- Keep: `knowledge/wiki/syntheses/approved-spec-binding-contract/spec.md`
- Keep: `knowledge/wiki/syntheses/approved-spec-binding-contract/issues.md`
- Keep: `knowledge/wiki/syntheses/approved-spec-binding-contract/initial-implementation-plan.md`
- Keep: `knowledge/wiki/syntheses/approved-spec-binding-contract/implementation-plan.md`
- Create after approval: `knowledge/wiki/syntheses/approved-spec-binding-contract/input-packet.json`
- Delete from current tree: `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-spec.md`
- Delete from current tree: `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-issues.md`
- Delete from current tree: `knowledge/wiki/syntheses/2026-07-21-loop-skill-approved-spec-binding-contract-implementation-plan.md`
- Delete from current tree: `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-input-packet.json`
- Delete from current tree: `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-execution-envelope.json`
- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`

**Interfaces:**

- Consumes: human-approved exact `spec.md` raw-byte SHA-256 and six-field approval scope.
- Produces: sealed Input Packet v2 under the Epic root, a gate commit containing exact spec/packet blobs, and no tracked instantiated Envelope.

- [ ] **Step 1: Verify the Written Spec Gate evidence before mutation**

Run `approved_spec_binding.py identify` against `knowledge/wiki/syntheses/approved-spec-binding-contract/spec.md`. Compare its digest byte-for-byte with the user-approved digest recorded in the append-only `knowledge/log.md` entry. Stop on any mismatch.

- [ ] **Step 2: Finalize the ledger and preserve initial history**

Keep ASBC-001 through ASBC-006 evidence intact in `issues.md` and `initial-implementation-plan.md`. Mark ASBC-007 runnable only after the approval record exists. Update the index to point current links at the nested tree; append a log entry for the layout gate without rewriting prior entries.

- [ ] **Step 3: Create the unsealed follow-up packet draft with `apply_patch`**

Create `/private/tmp/approved-spec-binding-contract-follow-up-draft.json` with exactly these top-level values before seal:

```json
{
  "artifact_root": "knowledge/wiki/syntheses/approved-spec-binding-contract",
  "delivery_intent": "per_action",
  "epic_id": "approved-spec-binding-contract",
  "schema_version": 2,
  "work_items": [
    {
      "acceptance_criteria": ["ASB-31〜ASB-36をpublic testsで検証する"],
      "dependencies": [],
      "id": "ASBC-007",
      "non_goals": ["historical flat artifact全件をmigrationしない"],
      "source": {"path": "knowledge/wiki/syntheses/approved-spec-binding-contract/issues.md", "type": "local"},
      "title": "Epic単位のdurable artifact layoutを契約化する",
      "verification": ["python3 -m unittest discover -s skills/issue-implementation-loop/tests", "python3 -m unittest discover -s skills/grill-to-pr-loop/tests"],
      "write_scope": ["path:skills/grill-to-pr-loop", "path:skills/issue-implementation-loop"]
    },
    {
      "acceptance_criteria": ["current durable artifactsがEpic directoryに集約されtracked Envelopeが消える"],
      "dependencies": ["ASBC-007"],
      "id": "ASBC-008",
      "non_goals": ["completed historical runtimeをresumeしない"],
      "source": {"path": "knowledge/wiki/syntheses/approved-spec-binding-contract/issues.md", "type": "local"},
      "title": "current Epicを新layoutへ移しruntime JSONをGit管理外にする",
      "verification": ["python3 skills/issue-implementation-loop/scripts/validate_input_packet.py knowledge/wiki/syntheses/approved-spec-binding-contract/input-packet.json"],
      "write_scope": ["path:knowledge/wiki/syntheses/approved-spec-binding-contract", "path:knowledge/index.md", "path:knowledge/log.md"]
    },
    {
      "acceptance_criteria": ["fresh-agent forward test、full verification、Draft PR #32更新を完了する"],
      "dependencies": ["ASBC-008"],
      "id": "ASBC-009",
      "non_goals": ["PR ready化、merge、release、live installを行わない"],
      "source": {"path": "knowledge/wiki/syntheses/approved-spec-binding-contract/issues.md", "type": "local"},
      "title": "forward test・全検証・Draft PR更新を完了する",
      "verification": ["python3 scripts/validate_skill_architecture.py --all", "python3 scripts/validate_skill_context.py --all", "python3 scripts/validate_dual_host_compatibility.py --all", "git diff --check"],
      "write_scope": ["path:knowledge/wiki/syntheses/approved-spec-binding-contract", "path:knowledge/index.md", "path:knowledge/log.md"]
    }
  ]
}
```

- [ ] **Step 4: Seal and validate the new packet**

Use the approved digest, `decision=approved`, `subject=spec_binding`, `actor_expression=session-user`, all six scope fields `true`, and `approved_at` from the approval log entry. Write only `knowledge/wiki/syntheses/approved-spec-binding-contract/input-packet.json`. Run the public packet validator and confirm the spec bytes did not change.

- [ ] **Step 5: Remove superseded flat current artifacts**

Delete the five old flat current files listed above with `apply_patch`. Do not delete unrelated historical packets/envelopes. Confirm `git ls-files` no longer contains the current instantiated Envelope and that the nested packet is tracked.

- [ ] **Step 6: Commit the new gate boundary**

Run `git diff --check`, stage only the ASBC-008 knowledge migration and packet, and commit with message `docs: group approved spec binding artifacts`. Record the full commit ID in the append-only log after the commit without editing `spec.md` or `input-packet.json`.

---

### Task 3 / ASBC-009: Forward-test, verify, and update Draft PR #32

**Files:**

- Modify: `knowledge/wiki/syntheses/approved-spec-binding-contract/issues.md`
- Modify: `knowledge/wiki/syntheses/approved-spec-binding-contract/implementation-plan.md`
- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`

**Interfaces:**

- Consumes: ASBC-007 implementation commit and ASBC-008 gate commit.
- Produces: fresh-agent evidence, full validation evidence, reviewed branch head, pushed Draft PR #32 update.

- [ ] **Step 1: Forward-test the updated skills**

Give three fresh read-only evaluators only the current skill entrypoints and hypothetical Epic names. Require exact artifact paths and Git tracking decisions. Pass only if all three group durable files by Epic and place instantiated Envelope/runtime artifacts under Git common runtime root.

- [ ] **Step 2: Run full verification**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_*.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests -p 'test_*.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_*.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts -p 'test_*.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json --strict
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --all
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
git diff --check
```

Expected: every command exits 0 and strict context warnings are empty.

- [ ] **Step 3: Review the final branch diff**

Review `origin/main...HEAD` for spec/implementation alignment, host-specific tracked paths, stale flat current links, accidental historical migration, schema/version drift, and remote-scope expansion. Fix any Critical or Important finding and rerun Step 2.

- [ ] **Step 4: Close durable evidence and commit**

Update ASBC-007 through ASBC-009 states, exact commit/review ranges, test counts, packet digest, and residual risks. Append the final verification event to `knowledge/log.md`. Commit with message `docs: close epic artifact lifecycle follow-up`.

- [ ] **Step 5: Push and update the existing Draft PR**

Push `codex/approved-spec-binding-contract` to `origin`. Update Draft PR #32 summary/checks to describe per-Epic durable roots, untracked runtime artifacts, the retained tracked Input Packet exception, and full verification evidence. Confirm the PR remains draft and do not merge or live-install.

## Self-Review

- Spec coverage: ASB-31 through ASB-36 map to Tasks 1 through 3.
- Placeholder scan: no deferred implementation marker is present; runtime approval values come from the exact approval log entry.
- Type consistency: `ARTIFACT_LAYOUT_MISMATCH`, `artifact_root`, `epic_id`, and the tracked/untracked trees use the same names in tests, implementation, docs, and migration steps.
