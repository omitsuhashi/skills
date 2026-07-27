# SDD Implementation Phase 2 旧実装スキル削除計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `sdd-implementation` の実runとforward verificationを先に成立させたうえで、旧実装workflowである `grill-to-pr-loop` / `issue-implementation-loop` と専用runtime/context surfaceをcurrent treeから削除する。

**Architecture:** Task 1でrepository route、architecture policy、CIをSDD単独構成へ切り替え、SDD自身による実装・task reviewを削除前のforward evidenceとする。Task 1がreview cleanになった後だけTask 2へ進み、旧skill本体、専用test、context mapping、workflow complexity reportを削除する。historical wikiと旧baselineは証跡として保持し、current executable surfaceからだけ切り離す。

**Tech Stack:** Markdown、TOML、Python 3.9+ standard library、`unittest`、GitHub Actions YAML。

## Global Constraints

- Authority sourceは `knowledge/wiki/syntheses/sdd-implementation-skill-design.md` のPhase 2と、2026-07-27のsession userによる削除依頼である。
- `skills/grill-to-pr-loop/` と `skills/issue-implementation-loop/` のproduction filesを削除する。`grilling`、`tdd`、`llm-wiki`、`sdd-implementation`、その他の独立skillは削除しない。
- Task 1のSDD implementer report、fresh verification、独立task reviewが揃う前にTask 2を開始しない。
- `knowledge/raw/**` は不変とする。旧spec、issue ledger、plan、packet、envelope、events、`skill-repository-optimization-v4-context-baseline.json` はhistorical evidenceとして保持する。
- 旧runtime schema、template、script、test、context contract、workflow-complexity baselineをcurrent executable surfaceから除去する。compatibility layer、fallback、replacement schemaは追加しない。
- `planning_authority` と `forbidden_standalone_skill_names` はSDDでも有効なcurrent policyなので保持する。旧loop専用の`context_compaction` policyは除去する。
- `sdd-implementation` は `default_implementation_skill` かつ唯一の `user_facing_skills` entryとする。
- context toolingは現存する `context-contract.toml` だけを汎用的に検証・reportする。削除後のcurrent対象は `llm-wiki` であり、SDDへ新しいcontext contractを追加しない。
- historical wiki closeoutはSDDのKnowledge Closeout Workerが実装task完了後に行い、旧pathへのlive Markdown linkとcurrent/executable表現だけをhistorical/non-executableへ更新する。
- concrete model名、reasoning effort値、provider、agent ID、run-specific routing resultをdurable artifactへ保存しない。
- push、PR作成、merge、release、live installは行わない。

---

### Task 1: SDD単独routeを成立させ、削除前forward evidenceを作る

**Files:**
- Modify: `AGENTS.md`
- Modify: `skill-architecture.toml`
- Modify: `scripts/validate_skill_architecture.py`
- Modify: `scripts/test_validate_skill_architecture.py`
- Modify: `.github/workflows/skill-architecture.yml`
- Modify: `scripts/test_dual_host_ci_workflow.py`
- Test: `skills/sdd-implementation/tests/test_sdd_implementation.py`
- Test: `scripts/test_validate_skill_architecture.py`
- Test: `scripts/test_dual_host_ci_workflow.py`

**Interfaces:**
- Consumes: `skills/sdd-implementation/SKILL.md`、current `planning_authority` policy、current dual-host CI。
- Produces: `user_facing_skills = ["sdd-implementation"]`、`default_implementation_skill = "sdd-implementation"`、SDD contract testを実行するCI step、旧skillをrouteしないrepository router。

- [ ] **Step 1: architectureとCIの期待値を先にREDへ変更する**

`scripts/test_validate_skill_architecture.py` のlegacy route assertionsを、次のobservable contractへ置き換える。

```python
def test_sdd_is_the_only_user_facing_implementation_skill(self) -> None:
    family = repository_change_loop_family()
    self.assertEqual(["sdd-implementation"], family["user_facing_skills"])
    self.assertEqual("sdd-implementation", family["default_implementation_skill"])

def test_repository_router_uses_only_sdd_for_approved_plans(self) -> None:
    router = REPO_ROUTER.read_text(encoding="utf-8")
    self.assertIn("use `sdd-implementation` by default", router)
    self.assertNotIn("Use `grill-to-pr-loop`", router)
    self.assertNotIn("`issue-implementation-loop`", router)
```

同fileから`context_compaction`専用testを削除する。`scripts/test_dual_host_ci_workflow.py`には次を追加する。

```python
self.assertIn("Run sdd-implementation tests", text)
self.assertIn(
    "python3 -m unittest discover -s skills/sdd-implementation/tests",
    text,
)
self.assertNotIn("Run grill-to-pr-loop tests", text)
self.assertNotIn("Run issue-implementation-loop tests", text)
```

- [ ] **Step 2: focused testを実行して正しいREDを確認する**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-task1-pycache \
python3 -m unittest \
  scripts.test_validate_skill_architecture \
  scripts.test_dual_host_ci_workflow
```

Expected: FAIL because policy、router、CIがまだlegacy routeを含む。import errorやsyntax errorではないことを確認する。

- [ ] **Step 3: 最小のSDD単独routeへ更新する**

`AGENTS.md` は次のdefault routeだけを残す。

```markdown
## Default implementation route

- When a human-approved implementation plan is ready for local execution, use `sdd-implementation` by default.
```

`skill-architecture.toml` は `user_facing_skills = ["sdd-implementation"]` とし、`default_implementation_skill`、`forbidden_standalone_skill_names`、`internal_components`、`planning_authority`を保持する。`[families.repository-change-loop.context_compaction]` tableだけを削除する。

`scripts/validate_skill_architecture.py` は、user-facing skill数をexactly 1として検証し、`EXPECTED_CONTEXT_COMPACTION_POLICY`、`_validate_context_compaction_policy()`、その呼び出しを削除する。`planning_authority`検証は維持する。

`.github/workflows/skill-architecture.yml` は旧2 skillのtest stepを削除し、次を追加する。

```yaml
      - name: Run sdd-implementation tests
        run: PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests
```

- [ ] **Step 4: focused GREENとforward verificationを実行する**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-task1-pycache \
python3 -m unittest \
  scripts.test_validate_skill_architecture \
  scripts.test_dual_host_ci_workflow

PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-task1-pycache \
python3 -m unittest discover -s skills/sdd-implementation/tests

PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-task1-pycache \
python3 scripts/validate_skill_architecture.py --all
```

Expected: all commands exit 0。SDD implementer reportへcommands、test counts、output summaryを記録する。

- [ ] **Step 5: Task 1をcommitし、独立task reviewを通す**

```bash
git add AGENTS.md skill-architecture.toml \
  scripts/validate_skill_architecture.py \
  scripts/test_validate_skill_architecture.py \
  scripts/test_dual_host_ci_workflow.py \
  .github/workflows/skill-architecture.yml
git commit -m "refactor: make sdd the sole implementation route"
```

Task 1 reviewはrequirements fit、material simplicity、material current riskを確認する。review cleanとledgerの`Task 1: complete`が揃うまでTask 2を開始しない。

### Task 2: 旧loop skillと専用runtime/context surfaceを削除する

**Files:**
- Delete: `skills/grill-to-pr-loop/`
- Delete: `skills/issue-implementation-loop/`
- Delete: `scripts/test_loop_autonomous_gates_ledger.py`
- Delete: `scripts/test_loop_operational_simplicity_ledger.py`
- Delete: `scripts/test_loop_review_governance_ledger.py`
- Modify: `scripts/skill_context/contract.py`
- Modify: `scripts/report_skill_context.py`
- Modify: `scripts/test_report_skill_context.py`
- Modify: `.github/workflows/skill-architecture.yml`
- Preserve unchanged: `knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json`
- Test: `scripts/test_report_skill_context.py`
- Test: `scripts/test_validate_skill_architecture.py`

**Interfaces:**
- Consumes: Task 1のSDD-only architecture policyとreview-clean commit。
- Produces: legacy skill directoriesなし、現存context contractだけを扱うgeneric validator/reporter、legacy workflow complexity/session pressure surfaceなし、historical baselineのcurrent referenceなし。

- [ ] **Step 1: legacy absenceとgeneric context reportの期待値を先にREDへ固定する**

`scripts/test_validate_skill_architecture.py` に次を追加する。

```python
def test_legacy_implementation_skill_directories_are_absent(self) -> None:
    self.assertFalse((REPO_ROOT / "skills" / "grill-to-pr-loop").exists())
    self.assertFalse((REPO_ROOT / "skills" / "issue-implementation-loop").exists())
```

`scripts/test_report_skill_context.py` はlegacy workflow complexity、worker context、review cycle、session pressure、old baseline comparisonのtestを削除し、次を固定する。

```python
def test_all_context_contracts_are_discovered_without_architecture_coupling(self) -> None:
    result = run_script(REPORT_SKILL_CONTEXT, "--all", "--json")
    self.assertEqual(result.returncode, 0, result.stderr)
    payload = json.loads(result.stdout)
    self.assertEqual(["llm-wiki"], [skill["skill"] for skill in payload["skills"]])
    self.assertNotIn("workflow_complexity", payload)
    self.assertNotIn("session_context", payload)
    self.assertNotIn("baseline_path", payload)
```

- [ ] **Step 2: focused testを実行して正しいREDを確認する**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-task2-pycache \
python3 -m unittest \
  scripts.test_validate_skill_architecture \
  scripts.test_report_skill_context
```

Expected: FAIL becauselegacy directories、legacy report fields、architecture-coupled context discoveryがまだ存在する。

- [ ] **Step 3: legacy production filesと専用root testsを削除する**

`skills/grill-to-pr-loop/` のtracked filesすべて、`skills/issue-implementation-loop/` のtracked filesすべて、次のroot test filesを削除する。

```text
scripts/test_loop_autonomous_gates_ledger.py
scripts/test_loop_operational_simplicity_ledger.py
scripts/test_loop_review_governance_ledger.py
```

`knowledge/**` はこのstepで削除しない。

- [ ] **Step 4: context toolingを現存contractのgeneric reportへ縮小する**

`scripts/skill_context/contract.py` は `EXPECTED_PHASE_SKILL_MAPPINGS` とarchitecture policy dependencyを削除し、`all_skill_dirs()` を次のcontract discoveryへ変更する。

```python
def all_skill_dirs() -> List[Path]:
    return sorted(path.parent for path in SKILLS_ROOT.glob("*/context-contract.toml"))
```

phase skill mapping validationと旧2 skill固有のerror pathを削除し、schema v1/v2/v3のgeneric parser/validatorは維持する。

`scripts/report_skill_context.py` は `GATE_OPERATIONS`、runtime artifact discovery、`collect_workflow_complexity()`、`collect_session_context()`、session-pressure CLI、baseline comparison/emit/require CLIを削除する。出力は各current context contractのread-set metricsとwarningsだけを含める。

`.github/workflows/skill-architecture.yml` のcontext report commandから `--require-baseline` を削除し、`--all --json --fail-on-warning` を使用する。historical baseline fileは変更も削除もしない。

- [ ] **Step 5: focused GREENとlegacy surface absenceを確認する**

Run:

```bash
test ! -e skills/grill-to-pr-loop
test ! -e skills/issue-implementation-loop

PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-task2-pycache \
python3 -m unittest \
  scripts.test_validate_skill_architecture \
  scripts.test_report_skill_context

PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-task2-pycache \
python3 scripts/validate_skill_context.py --all

PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-task2-pycache \
python3 scripts/report_skill_context.py --all --json --fail-on-warning

git grep -n -E 'grill-to-pr-loop|issue-implementation-loop' -- \
  ':!knowledge/**'
```

Expected: existence checksとtests/validators/reportはexit 0。`git grep` はexit 1でmatchなし。`.git/**`、SDD scratch workspace、untracked reportは判定対象にしない。

- [ ] **Step 6: Task 2をcommitし、独立task reviewを通す**

```bash
git add -A
git commit -m "refactor: remove legacy implementation loops"
```

Review packageはTask 1 headをBASEとして作る。historical wikiの削除、unrelated skill削除、replacement runtime/schema追加、`planning_authority`削除があればblocking findingとする。

## SDD Knowledge Closeout And Final Verification

Task 1とTask 2のreview完了後、fresh Knowledge Closeout Workerが `llm-wiki` の `single-root.ingest` contractで次を行う。

- `knowledge/wiki/syntheses/sdd-implementation-skill-design.md` の状態とMigrationをPhase 2 local completeへ更新する。
- このplanに実run、Task 1/2 review、削除scope、残存historical evidence、未実施remote actionを追記する。
- `knowledge/index.md` で旧loop artifactのcurrent/executable/restart表現をhistorical/non-executableへ直し、このplanを発見可能にする。
- 削除済みproduction pathへのMarkdown linkをinline codeまたはhistorical commit referenceへ変換する。`knowledge/raw/**` は触らない。
- `knowledge/log.md` にPhase 2 closeoutをappendする。

Knowledge closeout後に次をfreshに実行する。

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-final-pycache \
python3 -m unittest discover -s skills/sdd-implementation/tests

PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-final-pycache \
python3 -m unittest discover -s skills/llm-wiki/tests

PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-final-pycache \
python3 -m unittest discover -s scripts

PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-final-pycache \
python3 scripts/validate_skill_architecture.py --all

PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-final-pycache \
python3 scripts/validate_skill_context.py --all

PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-final-pycache \
python3 scripts/report_skill_context.py --all --json --fail-on-warning

PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-final-pycache \
python3 scripts/validate_dual_host_compatibility.py --skill skills/sdd-implementation

PYTHONPYCACHEPREFIX=/private/tmp/sdd-phase2-final-pycache \
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/sdd-implementation

git diff --check "$(git merge-base main HEAD)..HEAD"
git status --short --branch
```

Final whole-branch reviewerはcode、tests、CI、architecture/context policy、knowledge closeoutを同じbranch rangeで確認する。`LOCAL_COMPLETE` は全task review、knowledge closeout、fresh verification、final reviewがapprovedの場合だけ返す。

## Phase 2 execution outcome and evidence

### Completed local implementation

- Task 1: `ce87b65`（`refactor: make sdd the sole implementation route`）とfix `4e4f532`（`fix: enforce the sdd-only implementation route`）。Task reviewはfix round 1後にreview cleanである。
- Task 2: `1def312405a1c1046366be749d85d3a493e5f887`（`refactor: remove legacy implementation loops`）。reviewはfindings 0でcleanである。
- current treeから`skills/grill-to-pr-loop/`、`skills/issue-implementation-loop/`、3件の旧loop ledger test、旧runtime/context report surfaceを削除した。historical wiki、`knowledge/raw/**`、`skill-repository-optimization-v4-context-baseline.json`は削除せず、非実行のevidenceとして保持した。

### Reported verification evidence

- Task 1 GREEN: architecture/CI focused suite 11 tests、`skills/sdd-implementation/tests` 9 tests、architecture validatorがpassした。
- Task 2 GREEN: architecture/context focused suite 12 tests、`scripts` discovery 42 tests、`skills/llm-wiki/tests` 5 tests、context validator、context report、architecture validator、dual-host CI workflow testsがpassした。旧directory absence checkはpassし、production surface grepはmatchなし（`git grep` exit 1）である。

### Remaining boundary

このcloseout時点では、Phase 2のfresh final verification、knowledge closeout後のfinal whole-branch review、`LOCAL_COMPLETE`判定は未実施である。push、PR作成、merge、release、live installも未実施であり、remote stateは変更していない。
