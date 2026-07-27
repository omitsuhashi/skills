# SDD Implementation Superpowers-first Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Status:** 2026-07-27にHumanがExecution Plan Gateとして承認し、Subagent-Driven executionを選択した。Task 1〜3の実装、review、fresh verificationの進行状態はplan固有のSDD ledgerと末尾のcloseout記録で追跡する。

**Goal:** `sdd-implementation`を、Superpowersの標準lifecycleを主系とし、spec stageの`Grill with Docs`、durable knowledge lifecycleの`llm-wiki`、host固有のmodel resolutionとoptional reasoning effortだけを薄く統合するrepository change entrypointへ更新する。

**Architecture:** 単一の共有`SKILL.md`が入力成熟度を判定し、`brainstorming -> writing-plans -> subagent-driven-development`を順に呼ぶ。Superpowersがspec、plan、TDD、dispatch、review、model tierを所有し、repo-local contractはGrill / LLM Wiki compositionとCodex / Hermes host adapterだけを追加する。既存のcontract tests、repository router、architecture policy、Codex UI metadataを同じpublic contractへ揃え、新しいscript、schema、runtime stateは作らない。

**Tech Stack:** Markdown Skill instructions、YAML `agents/openai.yaml`、Python 3.9+ `unittest` contract tests、TOML architecture policy、Superpowers v6.2.0、`grill-with-docs`、`llm-wiki`。

## Global Constraints

- 承認済みWritten Specは`knowledge/wiki/syntheses/sdd-implementation-skill-design.md`とする。
- 実装開始時に`superpowers:writing-skills`と`superpowers:test-driven-development`を読み、skill pressure / contract testをREDから始める。
- Superpowersをlifecycle、Human approval、plan structure、TDD、worker dispatch、review、fix loop、worktree、branch finishing、per-dispatch model tierの正本とする。
- repo-local skillはSuperpowersをfork、vendor、要約再実装せず、別のrole-to-model policy tableを持たない。
- Human-approved current specまたはcurrent specへbinding済みのapproved planがある場合、完了済みstageを再実行しない。
- Human-approved Written Specがない、またはmaterial ambiguityが残る場合は`Grill with Docs`を必須とし、利用不能ならad hoc質問へsilent fallbackせず`BLOCKED`とする。
- `llm-wiki`はrelevant knowledge queryと、approved spec、repository-approved plan、implementation closeoutのdurable syncを所有する。
- `CONTEXT.md`やrepo-root `docs/adr/`という並行正本を作らず、repositoryの`knowledge/AGENTS.md` write boundaryを優先する。
- runtime ledger、worker report、review transcript、diff、test log、agent IDはwikiへ保存しない。
- upstream model tierはhostのconcrete modelへruntime resolutionし、全dispatchでmodelを明示する。
- reasoning effortは`low` / `medium` / `high`のruntime-only overlayとし、user overrideを優先する。
- independent effort controlがないhostは`not_supported`としてmodel selectionだけで継続し、isolated model dispatch自体がない場合だけ`BLOCKED`とする。
- concrete model、effort、provider、availability、agent ID、run-specific resolutionをspec、plan、wiki、ledger、schemaへ保存しない。
- CodexとHermes Agentの両方で読める共有`SKILL.md`を維持し、host固有tool名やmodel catalogを固定しない。
- reviewはrequirements fit、material simplicity、material current riskに限定し、mechanical validationとrequired testsは弱めない。
- old loop skill、custom scheduler、queue、event store、runtime snapshot、worker packet、resume cacheをfallbackまたは新規依存として追加しない。
- push、PR作成、merge、release、live installはこのplanのscope外とする。

## File Map

- `skills/sdd-implementation/SKILL.md`: 入力成熟度、Superpowers lifecycle、Grill / LLM Wiki composition、model / effort / host boundary、closeoutを定義する唯一のshared runtime contract。
- `skills/sdd-implementation/tests/test_skill_contract.py`: shared skillのobservable contractと、旧model policyの再導入防止を検証する。
- `skills/sdd-implementation/agents/openai.yaml`: Codex UIで新しいend-to-end entrypointを説明するmetadata。
- `AGENTS.md`: repository changeのdefault routeを、approved-plan-onlyからSuperpowers-first lifecycleへ更新するthin router。
- `skill-architecture.toml`: repository-change-loop familyの説明をrequirements-to-local-completionへ合わせる。既存planning authority fieldsは変更しない。
- `scripts/test_validate_skill_architecture.py`: routerとarchitecture descriptionのregression contract。
- `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`: implementation完了状態とverification evidenceのcanonical spec。
- `knowledge/wiki/syntheses/sdd-implementation-superpowers-first-implementation-plan.md`: 本planのgate / execution / completion状態。
- `knowledge/wiki/syntheses/sdd-implementation-skill-implementation-plan.md`: Phase 1 historical plan。内容を実行契約として再利用しない。
- `knowledge/index.md` / `knowledge/log.md`: discoverability、Spec Gate、Execution Plan Gate、implementation closeout。

---

### Task 1: Replace the approved-plan-only skill contract with the Superpowers-first lifecycle

**Files:**
- Modify: `skills/sdd-implementation/tests/test_skill_contract.py`
- Modify: `skills/sdd-implementation/SKILL.md`

**Interfaces:**
- Consumes: change request、Human-approved Written Spec、またはcurrent specへbindingされたapproved implementation plan。
- Produces: `brainstorming -> writing-plans -> subagent-driven-development -> llm-wiki closeout -> final review` routeと、`LOCAL_COMPLETE | BLOCKED`。
- Preserves: isolated implementer / reviewer、main-session orchestration、material review threshold、local-only remote boundary。

- [ ] **Step 1: Read the required implementation skills**

Read completely:

```text
/Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.2.0/skills/writing-skills/SKILL.md
/Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.2.0/skills/test-driven-development/SKILL.md
```

Use their pressure-test and RED-GREEN requirements for this skill edit.

- [ ] **Step 2: Replace the old contract assertions with failing lifecycle assertions**

Keep `read_or_empty`, resource-shape coverage, review coverage, and local-only coverage. Replace the trigger, routing, and closeout assertions and add the following tests:

```python
def test_frontmatter_triggers_for_the_full_repository_change_lifecycle(self) -> None:
    frontmatter = self.skill_text.split("---", 2)[1] if "---" in self.skill_text else ""
    self.assertIn("name: sdd-implementation", frontmatter)
    self.assertIn(
        "description: Use when a repository change needs specification, planning, "
        "or local implementation through the Superpowers development lifecycle.",
        frontmatter,
    )

def test_superpowers_owns_the_ordered_lifecycle(self) -> None:
    brainstorming = self.skill_text.index("superpowers:brainstorming")
    writing_plans = self.skill_text.index("superpowers:writing-plans")
    sdd = self.skill_text.index("superpowers:subagent-driven-development")
    self.assertLess(brainstorming, writing_plans)
    self.assertLess(writing_plans, sdd)
    self.assertIn("Superpowers is the authoritative development methodology.", self.skill_text)
    for forbidden in ("custom scheduler", "worker packet schema", "runtime snapshot"):
        self.assertIn(forbidden, self.skill_text)

def test_entry_maturity_skips_completed_stages(self) -> None:
    for state in (
        "Change request or incomplete specification",
        "Human-approved current specification",
        "Approved plan bound to the current specification",
    ):
        self.assertIn(state, self.skill_text)
    self.assertIn("Do not repeat a completed stage.", self.skill_text)

def test_grill_with_docs_is_required_for_spec_authoring_and_refinement(self) -> None:
    self.assertIn("REQUIRED SUB-SKILL: Use grill-with-docs", self.skill_text)
    for trigger in (
        "no Human-approved written specification exists",
        "material ambiguity remains",
        "repository evidence conflicts with the proposed specification",
    ):
        self.assertIn(trigger, self.skill_text)
    self.assertIn("Ask one decision question at a time.", self.skill_text)
    self.assertIn("Do not silently replace Grill with Docs with ad hoc questioning.", self.skill_text)
    self.assertIn("not_needed", self.skill_text)

def test_llm_wiki_owns_query_and_three_durable_checkpoints(self) -> None:
    self.assertIn("REQUIRED SUB-SKILL: Use llm-wiki", self.skill_text)
    for checkpoint in (
        "Human-approved written specification",
        "Repository-approved implementation plan",
        "Implementation closeout",
    ):
        self.assertIn(checkpoint, self.skill_text)
    self.assertIn("knowledge/index.md", self.skill_text)
    self.assertIn("knowledge/log.md", self.skill_text)
    self.assertIn("Do not create parallel `CONTEXT.md` or `docs/adr/` stores.", self.skill_text)
    self.assertIn("not_applicable", self.skill_text)

def test_upstream_owns_model_tiers_and_local_contract_only_adds_effort(self) -> None:
    self.assertIn("Follow the current Superpowers SDD Model Selection contract.", self.skill_text)
    self.assertIn("Every subagent dispatch must state its model.", self.skill_text)
    self.assertIn("| Mechanical task or small scoped re-review | `low` |", self.skill_text)
    self.assertIn("| Multi-file integration, normal debugging, or task review | `medium` |", self.skill_text)
    self.assertIn("| Architecture-sensitive or high-risk task, or final review | `high` |", self.skill_text)
    self.assertIn("Honor an explicit user runtime override.", self.skill_text)
    self.assertIn("`not_supported`", self.skill_text)
    self.assertNotIn("| orchestrator |", self.skill_text)
    self.assertNotIn("economical balanced", self.skill_text)
    self.assertNotRegex(self.skill_text, re.compile(r"\bgpt-[0-9]"))

def test_host_boundary_distinguishes_optional_effort_from_required_dispatch(self) -> None:
    self.assertIn(
        "Lack of independent effort control does not block the flow.",
        self.skill_text,
    )
    self.assertIn(
        "Lack of isolated dispatch with an explicit model is `BLOCKED`.",
        self.skill_text,
    )
    self.assertIn("Codex", self.skill_text)
    self.assertIn("Hermes Agent", self.skill_text)
    self.assertIn("skills.external_dirs", self.skill_text)
```

Update `test_knowledge_closeout_precedes_final_review` so it locates the checkpoint list occurrence of `Implementation closeout` and the later `Final Whole-Branch Review` heading, rather than the first mention in the overview:

```python
def test_knowledge_closeout_precedes_final_review(self) -> None:
    task_review = self.skill_text.index("All implementation tasks and task reviews")
    closeout = self.skill_text.index("## Implementation Closeout")
    final_review = self.skill_text.index("## Final Whole-Branch Review")
    self.assertLess(task_review, closeout)
    self.assertLess(closeout, final_review)
```

- [ ] **Step 3: Run the focused tests and verify RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-t1-red \
python3 -m unittest discover -s skills/sdd-implementation/tests -p "test_skill_contract.py"
```

Expected: FAIL because the current skill only accepts a Human-approved plan, does not name `brainstorming`, `writing-plans`, or `grill-with-docs`, and still contains the duplicate role/capability table.

- [ ] **Step 4: Rewrite `SKILL.md` with the minimal shared contract**

Use this exact section structure and contract text. Preserve concise prose; do not add scripts, references, schema, or runtime artifacts.

```markdown
---
name: sdd-implementation
description: Use when a repository change needs specification, planning, or local implementation through the Superpowers development lifecycle.
---

# SDD Implementation

Superpowers is the authoritative development methodology. Compose its current
skills; do not copy their process into a custom scheduler, worker packet schema,
runtime snapshot, event log, or resume protocol.

## Route By Input Maturity

Do not repeat a completed stage.

- **Change request or incomplete specification:** use
  `superpowers:brainstorming`, the Spec Stage below, and Human written-spec
  approval before planning.
- **Human-approved current specification:** verify authority, applicability,
  requirements, and acceptance criteria, then use `superpowers:writing-plans`.
  Return to the Spec Stage only for a material conflict.
- **Approved plan bound to the current specification:** verify its binding,
  current-tree compatibility, and verification scope, then use
  `superpowers:subagent-driven-development`.

## Spec Stage

**REQUIRED SUB-SKILL: Use superpowers:brainstorming.**

When a knowledge root exists and prior decisions, terminology, architecture, or
implementation can materially affect the specification, query it first.
Do not force a ceremonial query when no relevant knowledge exists.

**REQUIRED SUB-SKILL: Use grill-with-docs** when no Human-approved written
specification exists, material ambiguity remains, or repository evidence
conflicts with the proposed specification.

Ask one decision question at a time. Investigate repository facts instead of
asking the Human. Confirm shared understanding for each material decision.
Do not silently replace Grill with Docs with ad hoc questioning. If Grill with
Docs is required but unavailable, return `BLOCKED`. For a complete,
Human-approved current specification, record the stage as `not_needed`.

Create and self-review the written specification using the current Superpowers
brainstorming contract. Require Human approval before planning.

## Durable Knowledge

**REQUIRED SUB-SKILL: Use llm-wiki** when a knowledge root exists.

Use the repository topology and write boundary for these checkpoints:

1. Human-approved written specification.
2. Repository-approved implementation plan.
3. Implementation closeout.

Keep canonical pages, `knowledge/index.md`, and `knowledge/log.md` synchronized.
Do not create parallel `CONTEXT.md` or `docs/adr/` stores. Keep runtime ledgers,
worker reports, review transcripts, diffs, test logs, agent IDs, and concrete
runtime routing outside the wiki.

No knowledge root is `not_applicable`; do not bootstrap one implicitly. An
existing knowledge root with unresolved authority, target, write boundary,
index/log sync, or validation is `BLOCKED`.

## Plan Stage

**REQUIRED SUB-SKILL: Use superpowers:writing-plans.**

Create an executable plan from the approved specification. Apply any
repository-required plan review or Human approval. Persist the approved plan
through the Durable Knowledge contract. Do not dispatch implementation from an
unapproved plan.

## Implementation Stage

**REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.**

Main session is the orchestrator. It retains state, paths, routing, waits, and
short verdicts. Never implement production code, perform task review, or author
wiki content in the main session.

Use fresh implementers and independent reviewers. Do not inherit the parent
conversation. On Codex, use `fork_turns="none"`; on Hermes Agent, use the
equivalent fresh context. Pass durable paths and missing task-local facts only.

Run SDD sequentially. Review only requirements fit, material simplicity, and
material current risk. A blocking finding needs evidence of a requirement gap,
scope excess, observable regression, or concrete current risk. Do not block on
style, formatting, future-only concerns, scope-external hardening, or equivalent
preferences. Do not reduce mechanical validation or required test coverage.

All implementation tasks and task reviews must be complete before closeout.

## Runtime Model And Effort

Follow the current Superpowers SDD Model Selection contract. Every subagent
dispatch must state its model. Let Superpowers choose the relative tier for the
task and resolve that tier to a concrete model available in the current host.
Do not maintain a second role-to-model table.

Apply reasoning effort as an independent runtime-only overlay when supported:

| Superpowers task class | Reasoning effort |
| --- | --- |
| Mechanical task or small scoped re-review | `low` |
| Multi-file integration, normal debugging, or task review | `medium` |
| Architecture-sensitive or high-risk task, or final review | `high` |

Honor an explicit user runtime override. For a stuck fix, raise effort one
available step before following Superpowers model escalation.

When a host has no independent effort control, record `not_supported` and
continue with Superpowers model selection. Lack of independent effort control
does not block the flow. Lack of isolated dispatch with an explicit model is
`BLOCKED`.

Persist no concrete model, effort, provider, availability, agent ID, or
run-specific resolution in the specification, plan, wiki, ledger, or schema.

## Host Boundary

Codex maps isolated dispatch, explicit model, optional effort, wait, and resume
to current host capabilities. Hermes Agent is not assumed to have an upstream
adapter; detect and map fresh worker/reviewer, model selector, optional effort,
and resume capabilities. Keep `skills.external_dirs` as the documented Hermes
discovery route.

Do not hard-code host tool names or model catalogs. Do not silently fall back to
main-session implementation or an old loop skill when required SDD capability
is absent.

## Implementation Closeout

Dispatch a fresh knowledge worker and use the Durable Knowledge contract.
Validate the wiki before final review.

## Final Whole-Branch Review

After closeout, run the Superpowers final whole-branch review over code, tests,
the approved specification and plan, and knowledge artifacts. Return
`LOCAL_COMPLETE` only after reviewed tasks, fresh verification, scoped commits,
applicable closeout, and final approval.

Do not push, create a PR, merge, release, or install live without separate
explicit authorization. Report blockers, residual material risk, and
unperformed remote actions briefly.
```

- [ ] **Step 5: Run focused tests and skill validators**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-t1-green \
python3 -m unittest discover -s skills/sdd-implementation/tests -p "test_skill_contract.py"

python3 scripts/validate_dual_host_compatibility.py \
  --skill skills/sdd-implementation

python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/sdd-implementation
```

Expected: all contract tests pass; dual-host validator prints `OK: dual-host repository compatibility`; quick validator prints `Skill is valid!`.

- [ ] **Step 6: Commit Task 1**

```bash
git add skills/sdd-implementation/SKILL.md \
  skills/sdd-implementation/tests/test_skill_contract.py
git commit -m "feat: make SDD implementation Superpowers-first"
```

---

### Task 2: Align repository routing, architecture policy, and Codex metadata

**Files:**
- Modify: `scripts/test_validate_skill_architecture.py`
- Modify: `skills/sdd-implementation/tests/test_skill_contract.py`
- Modify: `AGENTS.md`
- Modify: `skill-architecture.toml`
- Modify: `skills/sdd-implementation/agents/openai.yaml`

**Interfaces:**
- Consumes: Task 1 shared lifecycle contract.
- Produces: repository default routing and Codex UI copy that accept change requests, specs, and plans without changing `default_implementation_skill = "sdd-implementation"` or planning authority fields.

- [ ] **Step 1: Write failing router, policy, and metadata assertions**

Replace `test_repository_router_uses_old_loops_only_when_explicit` with:

```python
def test_repository_router_uses_sdd_for_the_full_change_lifecycle(self) -> None:
    router = REPO_ROUTER.read_text(encoding="utf-8")
    self.assertIn(
        "For repository changes, use `sdd-implementation` by default.",
        router,
    )
    self.assertIn(
        "Superpowers lifecycle, `grill-with-docs`, and `llm-wiki`",
        router,
    )
    self.assertIn(
        "Use `grill-to-pr-loop` or `issue-implementation-loop` only when "
        "the user explicitly names one",
        router,
    )

def test_repository_change_family_describes_requirements_to_completion(self) -> None:
    family = repository_change_loop_family()
    self.assertEqual(
        "Repository change workflow skills that move work from requirements "
        "through specification, planning, and local implementation.",
        family["description"],
    )
```

Update `test_openai_metadata_matches_the_skill` in the skill contract tests:

```python
def test_openai_metadata_matches_the_skill(self) -> None:
    self.assertIn('display_name: "SDD Implementation"', self.openai_text)
    self.assertIn(
        'short_description: "Develop changes with Superpowers, Grill, and LLM Wiki."',
        self.openai_text,
    )
    self.assertIn(
        'default_prompt: "Use $sdd-implementation to take this repository change '
        'through specification, planning, implementation, and local completion."',
        self.openai_text,
    )
```

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-t2-red \
python3 -m unittest discover -s skills/sdd-implementation/tests -p "test_skill_contract.py"

PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-t2-red \
python3 -m unittest discover -s scripts -p "test_validate_skill_architecture.py"
```

Expected: FAIL on the old approved-plan-only router, old family description, and old Codex UI copy.

- [ ] **Step 3: Apply the minimal router, policy, and metadata changes**

Replace the first bullet under `## Default implementation route` in `AGENTS.md` with:

```markdown
- For repository changes, use `sdd-implementation` by default. It composes the Superpowers lifecycle, `grill-with-docs`, and `llm-wiki`, and skips specification or planning stages that are already Human-approved and current.
```

Keep the explicit-only old-loop bullet unchanged.

Set the family description in `skill-architecture.toml` to:

```toml
description = "Repository change workflow skills that move work from requirements through specification, planning, and local implementation."
```

Do not change `default_implementation_skill`, `planning_authority`, context compaction, or the old `user_facing_skills` compatibility list.

Replace `skills/sdd-implementation/agents/openai.yaml` with:

```yaml
interface:
  display_name: "SDD Implementation"
  short_description: "Develop changes with Superpowers, Grill, and LLM Wiki."
  default_prompt: "Use $sdd-implementation to take this repository change through specification, planning, implementation, and local completion."
```

- [ ] **Step 4: Run focused tests and architecture validation**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-t2-green \
python3 -m unittest discover -s skills/sdd-implementation/tests -p "test_skill_contract.py"

PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-t2-green \
python3 -m unittest discover -s scripts -p "test_validate_skill_architecture.py"

python3 scripts/validate_skill_architecture.py --all
```

Expected: focused suites pass and architecture validator prints `OK: validated skill architecture policy (repository-change-loop)`.

- [ ] **Step 5: Commit Task 2**

```bash
git add AGENTS.md \
  skill-architecture.toml \
  scripts/test_validate_skill_architecture.py \
  skills/sdd-implementation/agents/openai.yaml \
  skills/sdd-implementation/tests/test_skill_contract.py
git commit -m "docs: route repository changes through Superpowers"
```

---

### Task 3: Perform LLM Wiki closeout and full verification

**Files:**
- Modify: `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`
- Modify: `knowledge/wiki/syntheses/sdd-implementation-superpowers-first-implementation-plan.md`
- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`

**Interfaces:**
- Consumes: reviewed Task 1 and Task 2 commits plus their fresh verification.
- Produces: current implementation status, discoverable canonical pages, durable verification evidence, and a clean branch ready for final whole-branch review.

- [ ] **Step 1: Run `llm-wiki` in `single-root.ingest` mode**

Read repository and knowledge-root instructions, then use `llm-wiki` with:

```text
topology = single-root
operation = ingest
knowledge_root = knowledge
write_boundary = owned
```

Do not edit `knowledge/raw/`.

- [ ] **Step 2: Synchronize canonical status**

Update the design `## 状態` to say that the Superpowers-first revision implementation and task reviews are complete and that final whole-branch review is pending. Do not claim `LOCAL_COMPLETE` yet.

Keep this plan’s status immediately after the required sub-skill header:

```markdown
> **Status:** 2026-07-27にHumanがExecution Plan Gateとして承認し、Subagent-Driven executionを選択した。Task 1〜3の実装、review、fresh verificationの進行状態はplan固有のSDD ledgerと末尾のcloseout記録で追跡する。
```

Append a `## Closeout Candidate` section containing:

- Task 1 and Task 2 commit SHAs obtained from `git log --oneline --reverse 8c18ef0..HEAD` and identified by the exact Task 1 / Task 2 commit subjects in this plan.
- task implementation review verdicts.
- every fresh verification command from Step 4 and its actual result.
- remote actions not performed.

Update `knowledge/index.md` descriptions so the design is implemented but awaiting final review and this plan is the current successor plan; keep the Phase 1 plan explicitly historical.

Add a `knowledge/log.md` `final-review-candidate` entry with the task commits and fresh verification. Do not add `local-complete` before final review approval.

- [ ] **Step 3: Run knowledge validation**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-t3-wiki \
python3 -m unittest discover -s skills/llm-wiki/tests

git diff --check
```

Expected: 6 LLM Wiki tests pass and diff check reports no errors.

- [ ] **Step 4: Run the full scoped verification bundle**

Run from repository root:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-final \
python3 -m unittest discover -s skills/sdd-implementation/tests

PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-final \
python3 -m unittest discover -s scripts

python3 scripts/validate_skill_architecture.py --all

python3 scripts/validate_skill_context.py --all

python3 scripts/validate_dual_host_compatibility.py \
  --skill skills/sdd-implementation

python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/sdd-implementation

PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-final \
python3 -m unittest discover -s skills/llm-wiki/tests

git diff --check
```

Expected: all unit suites pass; architecture and context validators print `OK`; scoped dual-host validator prints `OK: dual-host repository compatibility`; quick validator prints `Skill is valid!`; diff check reports no errors.

- [ ] **Step 5: Commit the knowledge closeout candidate**

```bash
git add knowledge/wiki/syntheses/sdd-implementation-skill-design.md \
  knowledge/wiki/syntheses/sdd-implementation-superpowers-first-implementation-plan.md \
  knowledge/index.md \
  knowledge/log.md
git commit -m "docs: prepare Superpowers-first SDD final review"
```

- [ ] **Step 6: Run final whole-branch review**

Use Superpowers final whole-branch review over the approved Written Spec, this plan, all commits after the Spec Gate commit, tests, and knowledge artifacts.

If there is a blocking requirements-fit, material-simplicity, or material-current-risk finding, run one bounded fix and the required scoped re-review before continuing.

- [ ] **Step 7: Record final approval and commit the completion evidence**

Only after final whole-branch review approves:

- change the design status from final-review-pending to locally complete;
- rename the plan section from `## Closeout Candidate` to `## Closeout`;
- record the final review verdict and any bounded fix / re-review commit;
- update the index descriptions from final-review-pending to current/implemented;
- add one `knowledge/log.md` `local-complete` entry containing task commit SHAs, fresh verification, final review verdict, residual material risk, and unperformed remote actions.

Commit:

```bash
git add knowledge/wiki/syntheses/sdd-implementation-skill-design.md \
  knowledge/wiki/syntheses/sdd-implementation-superpowers-first-implementation-plan.md \
  knowledge/index.md \
  knowledge/log.md
git commit -m "docs: close out Superpowers-first SDD revision"
```

- [ ] **Step 8: Re-verify and re-review the final evidence-only commit**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-final-docs \
python3 -m unittest discover -s skills/llm-wiki/tests

git diff --check 8c18ef0..HEAD
```

Perform one scoped review of the final evidence-only commit against the approved Written Spec and Step 7 requirements. Return `LOCAL_COMPLETE` only when the tests pass, diff check is clean, and the scoped re-review has no blocking finding.

Do not push, create a PR, merge, release, or install live.

## Closeout Candidate

2026-07-27時点で、Task 1〜3 の実装、Task 1〜2 の task review、fresh verification を final whole-branch review に渡せる状態へ同期した。この section は final review の候補証跡であり、`LOCAL_COMPLETE` や final approval を主張しない。

### Task commits と task review

- Task 1: `65abafa` `feat: make SDD implementation Superpowers-first`。review fix は`6fa0f4f` `test: cover SDD review and remote boundaries`であり、Task 1 review fix round 1 は approved（open material finding なし）。
- Task 2: `693e1aa` `docs: route repository changes through Superpowers`。Task 2 review は approved（material finding なし）。

上記SHAとsubjectは`git log --oneline --reverse 8c18ef0..HEAD`から確認した。Task 1 の初期実装とreview fix、Task 2 のrouter / architecture / metadata同期は、いずれもこのcloseout candidateの親コミットに含まれる。

### Fresh verification

Step 3:

- `PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-t3-wiki python3 -m unittest discover -s skills/llm-wiki/tests` — 6 tests、`OK`。
- `git diff --check` — 出力なし、成功。

Step 4:

- `PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-final python3 -m unittest discover -s skills/sdd-implementation/tests` — 12 tests、`OK`。
- `PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-final python3 -m unittest discover -s scripts` — 68 tests、`OK`。
- `python3 scripts/validate_skill_architecture.py --all` — `OK: validated skill architecture policy (repository-change-loop)`。
- `python3 scripts/validate_skill_context.py --all` — `OK: validated 3 skill context contract(s)`。
- `python3 scripts/validate_dual_host_compatibility.py --skill skills/sdd-implementation` — `OK: dual-host repository compatibility`。
- `python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sdd-implementation` — `Skill is valid!`。
- `PYTHONPYCACHEPREFIX=/private/tmp/sdd-superpowers-final python3 -m unittest discover -s skills/llm-wiki/tests` — 6 tests、`OK`。
- `git diff --check` — 出力なし、成功。

### 未実施 remote action

push、PR作成、merge、release、live install は実施していない。最終 whole-branch review も未実施であり、その承認後まで completion status は変更しない。
