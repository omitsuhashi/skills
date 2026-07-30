+---
title: SDD first-write worktree migration Implementation Plan
date: 2026-07-30
tags:
  - sdd-implementation
  - worktree
  - first-write
  - implementation-plan
status: promoted
lifecycle_state: promoted
review_state: closed
canonical_target: "[[wiki/syntheses/sdd-first-write-worktree-migration-implementation-plan|SDD first-write worktree migration 実装計画]]"
owner_decision: promote
decision_actor: Human / repository maintainer
decision_date: 2026-07-30
decision_reason: Human が implementation plan として明示承認したため
---


# SDD first-write worktree migration Implementation Plan

## Draft Review Decision

- status: `promoted`
- owner decision: `promote`
- decision authority: Human / repository maintainer（Canonical Owner）
- decision date: 2026-07-30
- destination: [[wiki/syntheses/sdd-first-write-worktree-migration-implementation-plan|SDD first-write worktree migration 実装計画]]
- evidence: Human の明示承認

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Require `sdd-implementation` to bind the first repository content/artifact write to a captured-SHA Epic planning worktree, while preserving sequential SDD and offering a thin parallel adapter only for later opt-in Epics.

**Architecture:** This migration is a bootstrap exception: execute it sequentially in the already-existing Epic planning worktree, using current canonical SDD, without a new execution worktree or its own not-yet-implemented adapter. The product is portable Markdown plus Python contract tests; it adds no scheduler, lock, event schema, runtime state/snapshot, pre-plan reservation, compatibility bridge, or resume record.

**Tech Stack:** Markdown, Python 3.9 `unittest`, `tempfile`, `subprocess`, Git worktrees, existing validators.

## Global Constraints

- Bootstrap only in `/Users/omitsuhashi/repos/omitsuhashi/skills/.worktrees/sdd-first-write-worktree-migration-planning` on `codex/sdd-first-write-worktree-migration/planning`; no new issue/execution worktree and no adapter for this migration.
- `starting_branch` is the PR base only; `integration_branch` is integration destination and PR head only. Create it from immutable `starting_head_sha` captured at chat start.
- Pre-plan tuple `(original path, starting branch, starting SHA, starting status, integration branch, planning-worktree identity)` exists only in Stage Capsule/control context. Loss is `BLOCKED` plus Human restart/confirmation; never reconstruct it or persist a pre-plan record.
- Every planning root/CWD/writable path resolves inside planning worktree. Detached HEAD, dirty original content needed as source, collision, ambiguity, path escape, or original-checkout drift stops before write.
- Issue SDD remains sequential. Later parallel mode needs explicit Human opt-in and Human-approved independent plans; one issue owns one branch/worktree/session/plan/artifact workspace and one writer.
- Adapter authority is readiness/dependency/conflict verdict, allocation/wait/result routing, actual-result revalidation, and serialized single-writer integration only.
- Unknown/conflicting dependency, overlap, semantic/resource, ancestry, target-drift, or integration facts fail closed. Every required task commit remains reachable from `integration_branch`.
- Commit Plan Gate and implementation-closeout knowledge before fresh final verification and the one canonical whole-branch review. No repository write follows final review. Remote publication is separate authorization.

---

## File Structure

| Path | Responsibility |
| --- | --- |
| `skills/sdd-implementation/SKILL.md` | Gate before Planning Controller; later-Epic adapter; integration and final gate. |
| `skills/sdd-implementation/references/planning-context.md` | Tuple lifetime, recovery, path proof, Research/Spec/Review/Plan Author handoff, adapter authority. |
| `skills/sdd-implementation/references/research-stage.md` | First transient report containment. |
| `skills/sdd-implementation/prompts/{repository-researcher,spec-synthesizer,spec-reviewer}.md` | Bound root/CWD/artifact input and write containment. |
| `skills/sdd-implementation/tests/test_skill_contract.py` | Entrypoint, adapter, integration/final assertions. |
| `skills/sdd-implementation/tests/test_preimplementation_context.py` | Tuple and prompt handoff assertions. |
| `skills/sdd-implementation/tests/test_first_write_worktree_contract.py` | Static acceptance matrix and isolated Git fixture. |
| `knowledge/wiki/syntheses/sdd-first-write-worktree-migration-implementation-plan.md` | Canonical approved plan, created before implementation. |
| `knowledge/index.md`, `knowledge/log.md` | Plan Gate sync, then separate closeout event. |

Existing architecture/context validators and CI discovery are validation authorities; do not add validator/configuration/runtime files.

## Acceptance Coverage Matrix

Portable instructions have no host controller implementation; each policy case is verified by a static contract test against the repository-owned portable documents, which is the spec's equivalent isolated test. The native Git primitive is also exercised in a temporary repository.

| Required scenario | Named executable test | Mode |
| --- | --- | --- |
| clean named default branch captured-SHA allocation, original branch/HEAD/index/tracked/untracked/status fingerprint preservation, isolated first report | `NativeWorktreeContractTests.test_clean_default_branch_allocation_is_isolated` | temporary Git fixture |
| non-default allocation and full original fingerprint preservation, including staged index, staged/unstaged tracked diffs, untracked bytes, branch/HEAD/status | `NativeWorktreeContractTests.test_dirty_named_branch_preserves_all_status_categories` | temporary Git fixture |
| failed Git allocation preserves branch/HEAD/index/staged+unstaged tracked diffs/status and discovered non-empty untracked identity+bytes; creates no report/fallback write | `NativeWorktreeContractTests.test_failed_allocation_preserves_original_and_creates_no_report` | temporary Git fixture |
| detached, dirty-source, collision/no-fallback policy | `FirstWriteContractTests.test_all_first_write_stop_cases` | scoped static contract |
| continuing reuse, competing allocators, independent/stale/unattributable reuse, pre/post transfer compaction | `FirstWriteContractTests.test_reuse_compaction_and_ownership_cases` | static |
| relative/absolute/stale/escaping path and Research/Spec/Review/Plan Author planning handoffs | `PreImplementationContextContractTests.test_bound_paths_and_first_report_are_required` and `PreImplementationContextContractTests.test_plan_author_uses_only_bound_planning_paths` | scoped static contract |
| issue-internal task waits for review/fix and never has concurrent implementers | `SddImplementationSkillContractTests.test_parallel_adapter_leaves_issue_sdd_sequential` | scoped static contract |
| no opt-in/unapproved plan; dependency/overlap/resource/unknown; isolated units | `SddImplementationSkillContractTests.test_parallel_eligibility_is_fail_closed` | scoped static contract |
| actual changed path, semantic/resource, sibling ancestry rechecks | `SddImplementationSkillContractTests.test_actual_result_revalidation_is_required` | scoped static contract |
| blocked/unreviewed rejection, issue-tip-only, squash/cherry-pick task loss | `SddImplementationSkillContractTests.test_every_task_commit_reachability_is_required` | scoped static contract |
| serialized integration, conflict/partial stop, unchanged/advance/rewrite target | `SddImplementationSkillContractTests.test_serialized_integration_and_target_drift_are_required` | scoped static contract |
| combined verification, one whole-branch review/fixer/rereview | `SddImplementationSkillContractTests.test_combined_gate_is_canonical_and_single_pass` | static |
| original completion preservation and separate publication authorization | `SddImplementationSkillContractTests.test_completion_and_publication_boundary` | static |

### Task 0: Complete Plan Gate before execution

**Files:** Create `knowledge/wiki/syntheses/sdd-first-write-worktree-migration-implementation-plan.md`; modify `knowledge/index.md`, `knowledge/log.md`.

**Interfaces:** Consumes this approved draft and accepted spec; produces repository-approved canonical plan before Implementation Stage.

- [ ] **Step 1: Gate on approval**

  If plan approval or canonical-owner authority is missing, return `BLOCKED`; do not change canonical knowledge or begin implementation.

- [ ] **Step 2: Promote and synchronize**

  Copy the approved draft verbatim to the stated canonical synthesis. Add one Japanese index entry and one append-only Japanese Plan Gate log event naming accepted spec, canonical plan, approval, and no remote publication. Do not record transient output, agent IDs, or runtime state.

- [ ] **Step 3: Verify and commit Plan Gate**

Run: `git diff --check`

Expected: no output, exit 0.

```bash
git add knowledge/wiki/syntheses/sdd-first-write-worktree-migration-implementation-plan.md knowledge/index.md knowledge/log.md
git commit -m "docs: approve SDD worktree migration plan"
```

### Task 1: Write all red tests before contract prose

**Files:** Modify `skills/sdd-implementation/tests/test_skill_contract.py`, `skills/sdd-implementation/tests/test_preimplementation_context.py`; create `skills/sdd-implementation/tests/test_first_write_worktree_contract.py`.

**Interfaces:** Consumes the six current portable documents; produces the tests named in the matrix and no production helper/schema.

- [ ] **Step 1: Add these methods to `SddImplementationSkillContractTests`**

```python
    def test_first_write_gate_precedes_controller(self) -> None:
        self.assertLess(self.skill_text.index("## First-Write Worktree Gate"), self.skill_text.index("## Planning Controller"))
        gate = self.skill_text.split("## First-Write Worktree Gate", 1)[1].split("## Planning Controller", 1)[0]
        for value in ("read-only discovery", "detached HEAD", "default-branch inference", "`starting_branch`", "`starting_head_sha`", "`integration_branch`", "shared Git metadata", "zero content/artifact write", "original checkout fallback"):
            self.assertIn(value, gate)

    def test_parallel_adapter_leaves_issue_sdd_sequential(self) -> None:
        section = self.skill_text.split("## Epic Parallel Issue Adapter", 1)[1].split("## Runtime Model", 1)[0]
        for value in ("Within an issue, never dispatch concurrent implementers.", "Do not advance to the next task until its task review and any canonical fix are complete.", "Each issue execution unit has exactly one writer.", "does not schedule issue-internal tasks"):
            self.assertIn(value, section)

    def test_parallel_eligibility_is_fail_closed(self) -> None:
        section = self.skill_text.split("## Epic Parallel Issue Adapter", 1)[1].split("## Runtime Model", 1)[0]
        for value in ("explicit Human opt-in", "Human-approved issue plan", "one branch/worktree/session/plan/artifact workspace", "expected write overlap", "shared mutable resource", "pinned-base ancestry", "unknown", "sequential handling or Human decision"):
            self.assertIn(value, section)

    def test_actual_result_revalidation_is_required(self) -> None:
        section = self.skill_text.split("## Epic Parallel Issue Adapter", 1)[1].split("## Runtime Model", 1)[0]
        for value in ("actual commit range", "actual changed paths", "semantic/resource assumptions", "before integration-ready", "before every serialized integration", "sibling results"):
            self.assertIn(value, section)

    def test_every_task_commit_reachability_is_required(self) -> None:
        section = self.skill_text.split("## Epic Parallel Issue Adapter", 1)[1].split("## Runtime Model", 1)[0]
        for value in ("blocked or unreviewed result is not integration-ready", "every required issue/task commit", "reachable", "issue tip", "squash", "selected cherry-pick"):
            self.assertIn(value, section)

    def test_serialized_integration_and_target_drift_are_required(self) -> None:
        section = self.skill_text.split("## Epic Parallel Issue Adapter", 1)[1].split("## Runtime Model", 1)[0]
        for value in ("target head is unchanged", "single-writer serialized integration", "one ready issue at a time", "partial integrated state", "descendant advance", "non-descendant rewrite", "silently retarget"):
            self.assertIn(value, section)

    def test_combined_gate_is_canonical_and_single_pass(self) -> None:
        for value in ("fresh combined verification", "whole-branch review", "one fixer", "exactly one scoped re-review", "second fix wave", "repeated whole-branch review"):
            self.assertIn(value, self.skill_text)

    def test_completion_and_publication_boundary(self) -> None:
        for value in ("original-checkout preservation", "`LOCAL_COMPLETE`", "separate explicit authorization", "PR base", "PR head", "valid remote PR base"):
            self.assertIn(value, self.skill_text)
```

- [ ] **Step 2: Add these methods to `PreImplementationContextContractTests`**

```python
    def test_binding_tuple_lifetime_and_recovery_are_required(self) -> None:
        section = self.planning_text.split("## Stage Capsule", 1)[1].split("## Spec Synthesis And Review", 1)[0]
        for value in ("original checkout path", "`starting_branch`", "`starting_head_sha`", "captured starting status", "`integration_branch`", "Stage Capsule/control context", "plan-owned workspace/progress ledger", "Human restart/confirmation", "`BLOCKED`"):
            self.assertIn(value, section)
        for value in ("reconstruct", "compatibility bridge", "pre-plan reservation", "resume record"):
            self.assertIn(value, section)

    def test_bound_paths_and_first_report_are_required(self) -> None:
        for text in (self.researcher_text, self.synthesizer_text, self.reviewer_text):
            for value in ("resolved planning worktree root", "CWD", "writable artifact path", "original checkout"):
                self.assertIn(value, text)
            self.assertNotIn("- repository root;", text)
        for value in ("first transient Research Report", "relative", "absolute", "stale path", "escape"):
            self.assertIn(value, self.research_text)
        for value in ("original checkout metadata (read-only)", "baseline commit", "epic ID and current research question", "applicable repository and knowledge constraints", "current spec path when one exists"):
            self.assertIn(value, self.research_text)
        self.assertNotIn("- repository root and current baseline commit;", self.research_text)

    def test_plan_author_uses_only_bound_planning_paths(self) -> None:
        section = self.planning_text.split("## Plan Authoring", 1)[1].split("## Failure Boundary", 1)[0]
        for value in ("resolved planning worktree root", "bound CWD", "writable plan artifact path", "original checkout metadata (read-only)", "Plan Author Worker"):
            self.assertIn(value, section)
        self.assertNotIn("repository root, baseline commit", section)
```

- [ ] **Step 3: Create the complete new test module**

```python
from __future__ import annotations
from pathlib import Path
import subprocess
import tempfile
import unittest

SKILL_DIR = Path(__file__).resolve().parents[1]
DOCUMENTS = tuple(SKILL_DIR / name for name in ("SKILL.md", "references/planning-context.md", "references/research-stage.md", "prompts/repository-researcher.md", "prompts/spec-synthesizer.md", "prompts/spec-reviewer.md"))

def run_git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout

def fingerprint(root: Path) -> tuple[str, str, str, str, str, str, tuple[tuple[str, bytes], ...]]:
    untracked = tuple(name for name in run_git(root, "ls-files", "--others", "--exclude-standard", "-z").split("\0") if name)
    return (
        run_git(root, "branch", "--show-current").strip(),
        run_git(root, "rev-parse", "HEAD").strip(),
        run_git(root, "ls-files", "--stage", "-z"),
        run_git(root, "diff", "--cached", "--binary"),
        run_git(root, "diff", "--binary"),
        run_git(root, "status", "--porcelain=v1", "--untracked-files=all"),
        tuple((name, (root / name).read_bytes()) for name in untracked),
    )

class FirstWriteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = DOCUMENTS[0].read_text(encoding="utf-8")
        cls.planning_text = DOCUMENTS[1].read_text(encoding="utf-8")
        cls.contract = "\n".join(path.read_text(encoding="utf-8") for path in DOCUMENTS)

    def test_all_first_write_stop_cases(self) -> None:
        gate = self.skill_text.split("## First-Write Worktree Gate", 1)[1].split("## Planning Controller", 1)[0]
        for value in ("default-branch inference", "detached HEAD", "task-relevant uncommitted original content", "branch collision", "path collision", "allocation failure", "zero content/artifact write", "original checkout fallback", "switch/reset/stash/clean/add/commit"):
            self.assertIn(value, gate)

    def test_reuse_compaction_and_ownership_cases(self) -> None:
        gate = self.skill_text.split("## First-Write Worktree Gate", 1)[1].split("## Planning Controller", 1)[0]
        capsule = self.planning_text.split("## Stage Capsule", 1)[1].split("## Spec Synthesis And Review", 1)[0]
        for value in ("continuing controller/chat", "atomic allocation", "two allocators", "loser", "independent chat", "stale/foreign state", "HEAD/index/tracked/untracked"):
            self.assertIn(value, gate)
        for value in ("pre-plan compaction", "post-transfer", "canonical plan ledger tuple", "do not reconstruct"):
            self.assertIn(value, capsule)

class NativeWorktreeContractTests(unittest.TestCase):
    def make_repository(self, root: Path) -> None:
        run_git(root, "init", "-b", "main")
        run_git(root, "config", "user.name", "Test User")
        run_git(root, "config", "user.email", "test@example.invalid")
        (root / "tracked.txt").write_text("base\n", encoding="utf-8")
        run_git(root, "add", "tracked.txt")
        run_git(root, "commit", "-m", "base")

    def test_clean_default_branch_allocation_is_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            original, planning = Path(directory) / "original", Path(directory) / "planning"
            original.mkdir(); self.make_repository(original)
            branch, sha = run_git(original, "branch", "--show-current").strip(), run_git(original, "rev-parse", "HEAD").strip()
            self.assertEqual("main", branch)
            before = fingerprint(original)
            self.assertEqual("", before[5])
            run_git(original, "worktree", "add", "-b", "integration/default", str(planning), sha)
            report = planning / ".superpowers/research/default/report.md"; report.parent.mkdir(parents=True); report.write_text("report\n", encoding="utf-8")
            self.assertEqual(sha, run_git(planning, "rev-parse", "HEAD").strip())
            self.assertEqual(before, fingerprint(original))
            self.assertFalse((original / ".superpowers/research/default/report.md").exists())

    def test_dirty_named_branch_preserves_all_status_categories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            original, planning = Path(directory) / "original", Path(directory) / "planning"
            original.mkdir(); self.make_repository(original)
            run_git(original, "switch", "-c", "feature/start")
            (original / "unstaged.txt").write_text("committed\n", encoding="utf-8"); run_git(original, "add", "unstaged.txt"); run_git(original, "commit", "-m", "second tracked file")
            (original / "tracked.txt").write_text("staged\n", encoding="utf-8"); run_git(original, "add", "tracked.txt")
            (original / "unstaged.txt").write_text("unstaged\n", encoding="utf-8"); (original / "untracked.txt").write_text("untracked\n", encoding="utf-8")
            branch, sha = run_git(original, "branch", "--show-current").strip(), run_git(original, "rev-parse", "HEAD").strip()
            before = fingerprint(original)
            self.assertTrue(before[3]); self.assertTrue(before[4]); self.assertIn("?? untracked.txt", before[5])
            run_git(original, "worktree", "add", "-b", "integration/epic-42", str(planning), sha)
            report = planning / ".superpowers/research/epic-42/report.md"; report.parent.mkdir(parents=True); report.write_text("report\n", encoding="utf-8")
            self.assertEqual("feature/start", branch); self.assertEqual(sha, run_git(planning, "rev-parse", "HEAD").strip())
            self.assertEqual(before, fingerprint(original))
            self.assertTrue(report.is_relative_to(planning)); self.assertFalse((original / ".superpowers/research/epic-42/report.md").exists())

    def test_failed_allocation_preserves_original_and_creates_no_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            original, first, failed = Path(directory) / "original", Path(directory) / "first", Path(directory) / "failed"
            original.mkdir(); self.make_repository(original)
            (original / "unstaged.txt").write_text("committed\n", encoding="utf-8"); run_git(original, "add", "unstaged.txt"); run_git(original, "commit", "-m", "second tracked file")
            (original / "tracked.txt").write_text("staged\n", encoding="utf-8"); run_git(original, "add", "tracked.txt")
            (original / "unstaged.txt").write_text("unstaged\n", encoding="utf-8")
            (original / "failed-untracked.txt").write_bytes(b"failed-allocation-untracked\n")
            sha = run_git(original, "rev-parse", "HEAD").strip()
            before = fingerprint(original)
            self.assertTrue(before[3]); self.assertTrue(before[4])
            self.assertEqual((("failed-untracked.txt", b"failed-allocation-untracked\n"),), before[6])
            run_git(original, "worktree", "add", "-b", "integration/existing", str(first), sha)
            result = subprocess.run(["git", "worktree", "add", "-b", "integration/existing", str(failed), sha], cwd=original, capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(before, fingerprint(original))
            self.assertFalse((failed / ".superpowers/research/failed/report.md").exists())
            self.assertFalse((original / ".superpowers/research/failed/report.md").exists())

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Prove red state**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests -p 'test_skill_contract.py'`

Expected: FAIL on missing gate/adapter/final terms.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests -p 'test_preimplementation_context.py'`

Expected: FAIL on missing tuple/bound-path terms.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests -p 'test_first_write_worktree_contract.py'`

Expected: FAIL on the two missing static contract cases; the three native fixture cases pass independently, including the failed-allocation case with staged, unstaged, and deterministic non-empty untracked baseline.

- [ ] **Step 5: Commit red tests**

```bash
git add skills/sdd-implementation/tests/test_skill_contract.py skills/sdd-implementation/tests/test_preimplementation_context.py skills/sdd-implementation/tests/test_first_write_worktree_contract.py
git commit -m "test: specify SDD worktree migration contract"
```

### Task 2: Implement contract prose and turn the same tests green

**Files:** Modify `skills/sdd-implementation/SKILL.md`, both `references/*.md`, and all three `prompts/*.md` listed in File Structure.

**Interfaces:** Consumes the trusted tuple; produces `resolved planning worktree root`, `CWD`, and a contained writable artifact path for Research, Spec Synthesis, Spec Review, and Plan Author while retaining the four-field Control Return.

- [ ] **Step 1: Add `## First-Write Worktree Gate` before `## Planning Controller`**

  Insert this exact section immediately before `## Planning Controller`:

```markdown
## First-Write Worktree Gate

Before any content or artifact write, perform read-only discovery and capture the original checkout canonical path, named `starting_branch`, immutable `starting_head_sha`, distinguishable staged/unstaged/untracked starting status, Git common directory/worktree registration, and Epic branch/path. Detached HEAD, default-branch inference, task-relevant uncommitted original content, branch collision, path collision, allocation failure, or ownership ambiguity is fail closed: return `BLOCKED` with zero content/artifact write and no original checkout fallback.

Create the planning worktree atomically from `starting_head_sha`; only the continuing controller/chat that won atomic allocation may reuse it. If two allocators select the same Epic, the loser must not attach to the existing worktree and returns `BLOCKED`. An independent chat, stale/foreign state, or HEAD/index/tracked/untracked state not attributable to the trusted tuple is `BLOCKED`. Allocation may change shared Git metadata only; never perform original checkout switch/reset/stash/clean/add/commit or content write.

Before the first writable dispatch, prove planning registration/common directory/branch/path, captured-SHA base, original branch/HEAD/status preservation, and that repository root, CWD, every relative or absolute writable artifact path, and the first transient Research Report resolve inside the planning worktree. Reject stale path or escape path. The original checkout must not remain in a writable root, fallback root, CWD, or artifact destination.
```

- [ ] **Step 2: Add tuple, recovery, and prompt containment**

  Append this exact paragraph to `## Stage Capsule` in `references/planning-context.md`, without changing its existing five carried fields or controller read boundary:

```markdown
Before approved-plan entry, the compact tuple is held only in current Stage Capsule/control context: original checkout path, `starting_branch`, `starting_head_sha`, captured starting status, `integration_branch`, and planning-worktree identity. After pre-plan compaction, if that tuple is not trusted, return `BLOCKED` and request Human restart/confirmation; do not reconstruct from Git or conversation and do not create a compatibility bridge, pre-plan reservation, snapshot, runtime state, scheduler, lock, event schema, or resume record. On normal approved-plan SDD entry transfer the trusted tuple to the ordinary plan-owned workspace/progress ledger. Post-transfer recovery compares the canonical plan ledger tuple with current Git facts.
```

  Replace only the generic path input in `references/research-stage.md` and preserve every non-path input with this exact full input list (retain existing four-field Control Return):

```markdown
- resolved planning worktree root;
- bound CWD;
- writable artifact path under that root: `.superpowers/research/<epic-id>/`.
- original checkout metadata (read-only): canonical path, `starting_branch`, `starting_head_sha`, and captured starting status;
- baseline commit;
- epic ID and current research question;
- applicable repository and knowledge constraints;
- current spec path when one exists.

The first transient Research Report must resolve under the resolved planning worktree root. Before report creation, reject a relative, absolute, stale path, or escape path that resolves outside it, including the original checkout or any sibling worktree, and return `BLOCKED`.
```

  In each prompt, replace the current `- repository root;` input with these three inputs, retaining all other existing non-path inputs in their current order: `- resolved planning worktree root;`, `- bound CWD;`, and `- writable artifact path;`. Then add this exact `## Write Binding` section before `## Direct Return`, replacing only `<artifact>` with `Research Report`, `spec draft`, and `review artifact` respectively:

```markdown
## Write Binding

Inputs include `resolved planning worktree root`, `CWD`, and `writable artifact path`. Resolve the <artifact> under that writable artifact path before writing. If the resolved destination is the original checkout, a planning sibling, an issue sibling, or escapes the resolved planning worktree root, return `BLOCKED` without writing. Keep advisory-only authority and the existing four-field Direct Return unchanged.
```

  Replace the Plan Author input sentence in `## Plan Authoring` of `references/planning-context.md` with this exact sentence, retaining its existing fresh-worker, `writing-plans`, self-review, and Control Return rules:

```markdown
Pass the resolved planning worktree root, bound CWD, writable plan artifact path contained by that root, original checkout metadata (read-only), baseline commit, approved spec path, applicable repository rules, and current `superpowers:writing-plans` skill path to a fresh Plan Author Worker. Reject a stale, sibling, original-checkout, or escaping writable plan artifact path before authoring.
```

- [ ] **Step 3: Add later-Epic adapter, integration, final, and publication rules**

  Insert this exact section after `## Implementation Stage` and before `## Runtime Model` in `SKILL.md`:

```markdown
## Epic Parallel Issue Adapter

Default execution remains sequential canonical SDD. This migration itself runs sequentially in its existing Epic planning worktree; the adapter is available only to a later Epic with explicit Human opt-in and a Human-approved issue plan. Each issue execution unit has exactly one branch/worktree/session/plan/artifact workspace and exactly one writer. Within an issue, never dispatch concurrent implementers. Do not advance to the next task until its task review and any canonical fix are complete.

The adapter owns readiness/dependency/conflict verdicts, allocation/wait/result routing, actual-result revalidation, and single-writer serialized integration; it does not schedule issue-internal tasks or alter canonical task/review/fix/ledger/recovery authority. Unknown expected write overlap, dependency, shared mutable resource, pinned-base ancestry, or integration assumption returns to sequential handling or Human decision.

Before integration-ready and before every serialized integration, derive actual commit range, actual changed paths, semantic/resource assumptions, and every required issue/task commit from existing Superpowers ledger and Git history; revalidate them against sibling results and current target. A blocked or unreviewed result is not integration-ready. Reject an issue tip that cannot prove every required issue/task commit reachable, including squash or selected cherry-pick loss. Integrate one ready issue at a time; clean textual merge is insufficient and partial integrated state is not completion.

`starting_branch` is PR base and `integration_branch` is PR head and integration target. If target head is unchanged, retain captured ancestry. On descendant advance, revalidate against the same named branch and refresh integration ancestry and combined verification. On non-descendant rewrite, material divergence, or unknown, return `BLOCKED`; never silently retarget. After every required issue/task commit is reachable, run fresh combined verification and exactly one canonical whole-branch review for `starting_branch...integration_branch`. A finding follows one fixer, exactly one scoped re-review, and adjudication/stop; no second fix wave or repeated whole-branch review. Return `LOCAL_COMPLETE` only after original-checkout preservation. Remote publication needs separate explicit authorization and a valid remote PR base.
```

- [ ] **Step 4: Run the same focused green commands**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests -p 'test_skill_contract.py'`

Expected: PASS.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests -p 'test_preimplementation_context.py'`

Expected: PASS.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests -p 'test_first_write_worktree_contract.py'`

Expected: PASS, including all three native fixtures and discovered untracked identity-plus-byte comparison after failed allocation.

- [ ] **Step 5: Commit green contract**

```bash
git add skills/sdd-implementation/SKILL.md skills/sdd-implementation/references/planning-context.md skills/sdd-implementation/references/research-stage.md skills/sdd-implementation/prompts/repository-researcher.md skills/sdd-implementation/prompts/spec-synthesizer.md skills/sdd-implementation/prompts/spec-reviewer.md
git commit -m "feat: bind SDD writes to Epic worktrees"
```

### Task 3: Run verified repository closeout validators

**Files:** Test only existing files and the runtime-discovered skill-creator validator.

- [ ] **Step 1: Run full regression**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests`

Expected: PASS.

- [ ] **Step 2: Run verified validators**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`

Expected: `OK: validated skill architecture policy (repository-change-loop)`.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`

Expected: `OK: validated 1 skill context contract(s)`.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest scripts.test_validate_skill_architecture`

Expected: `Ran 11 tests` and `OK`.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest scripts.test_skill_ci_workflow`

Expected: `Ran 3 tests` and `OK`.

- [ ] **Step 3: Run required skill-creator validation**

  Use active-runtime discovery for the skill-creator validator. Current runtime command:

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sdd-implementation`

Expected: `Skill is valid!`; if no runtime-discovered equivalent exists, return `BLOCKED` rather than substitute an unrelated tool.

- [ ] **Step 4: Check diff and commit test edits if not already committed in Task 1**

Run: `git diff --check`

Expected: no output, exit 0.

```bash
git add skills/sdd-implementation/tests/test_skill_contract.py skills/sdd-implementation/tests/test_preimplementation_context.py skills/sdd-implementation/tests/test_first_write_worktree_contract.py
git commit -m "test: cover SDD worktree migration gates"
```

Expected: create this commit only when those changes were not included in Task 1's red-test commit; never make an empty commit.

### Task 4: Commit implementation closeout, then final gate

**Files:** Modify `knowledge/log.md`.

- [ ] **Step 1: Append implementation-closeout event**

  Add one Japanese append-only event naming accepted spec/canonical plan, completed portable contract, passed local validation classes, original-checkout comparison, and no remote publication. Exclude raw output, transient files, agent IDs, and runtime state.

- [ ] **Step 2: Commit closeout before final review**

```bash
git add knowledge/log.md
git commit -m "docs: close out SDD worktree migration"
```

- [ ] **Step 3: Verify final committed branch and invoke canonical review once**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests`

Expected: PASS on final committed branch.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`

Expected: architecture validator PASS on final committed branch.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`

Expected: context validator PASS on final committed branch.

Run: `git diff --check`

Expected: no output, exit 0.

  Invoke canonical Superpowers final whole-branch review exactly once. A material finding follows its one fixer/exactly one scoped re-review/adjudication flow; after that permitted fix commit, rerun fresh verification and only its scoped re-review. Do not start another full review.

- [ ] **Step 4: Verify branch and original-checkout invariants**

  Confirm current planning branch contains Plan Gate, all task, and closeout commits; every task commit is reachable; original branch/HEAD/status equals captured trusted tuple/ledger tuple. On mismatch stop and preserve evidence; never reset, checkout, stash, clean, or delete worktrees. Do not push, create PR, merge, or publish without separate explicit authorization.

## Self-Review

All approved acceptance criteria map to a named executable test in the matrix. Native fixtures discover the untracked identity set and compare its bytes together with original branch, HEAD, index, staged/unstaged tracked diffs, and status. The failed-allocation fixture establishes a deterministic non-empty untracked file plus staged and unstaged tracked changes before its baseline and compares that complete fingerprint after failure. Every contract assertion is written before prose and executed red, then the exact same command executes green. Canonical plan is committed before implementation; closeout is committed before final verification/review; bootstrap location and no-adapter rule are explicit. Research, synthesis, review, and Plan Author each receive bound root/CWD/contained path, while original checkout metadata remains read-only. No custom runtime infrastructure or undefined implementation step is introduced.

## Execution Handoff

After Plan Gate approval, implement sequentially in the existing planning worktree and branch above. The adapter is unavailable to this migration and may be selected only by a later independently approved, explicitly opted-in Epic. Remote publication is out of scope.
