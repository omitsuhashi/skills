# Loop Review Simplicity And Phase Skills Implementation Plan

> **For `issue-implementation-loop` workers:** REQUIRED TASK SKILLS: use `tdd` for code changes and `writing-skills` for this skill edit. Load `writing-skills` on demand only after entering the implementation phase. The planning coordinator must not implement this plan.

**Goal:** `LRSP-001` として、material findingだけを報告するreview standardと、phase-owned workflow skillをoperation/dispatch別に宣言するcontext contract schema v3を実装する。

**Architecture:** 既存`context-contract.toml`に`skills` / `dispatch_skills`を加え、shared parserと`issue-implementation-loop` runtime selectorの両方が同じ値を返す。task-triggered skillはgeneric contractへ固定せず、現在taskのskill triggerに従ってimplementation phaseでだけ読む。reviewは既存taxonomyを維持し、具体的なsimpler alternativeを示せるmaterial complexityだけを`intent_gap` / `Important`として扱う。

**Tech Stack:** Python 3 standard library、TOML subset parser、`unittest`、Markdown skill/reference contract、JSON context baseline、Git。

## Global Constraints

- Approved spec: `knowledge/wiki/syntheses/loop-review-simplicity-and-phase-skills/spec.md`
- Approved spec SHA-256: `2e86698433cc4a95719bffc8a2f5a6e76aa3fea5b71f743ec8f71ef39edc4719`
- Issue: `LRSP-001`
- Worker write scopeは`issues.md`の7 pathに限定する。planning artifacts、`knowledge/index.md`、`knowledge/log.md`はcoordinator ownership。
- schema v1 / v2と`llm-wiki` contractを維持する。
- 新しいloader、worker packet field、finding schema、review runtimeを作らない。
- routine reviewは`Critical` / `Important`だけを報告する。`Minor` / nit / 好み / 任意改善を出さない。
- mechanical validationとexisting hardening / safety / classification boundaryを弱めない。
- `delivery_intent = "per_action"`。workerはremote writeを行わない。

---

## File map

### Context contract implementation

- Modify `scripts/skill_context/contract.py`
  - schema v3 validation、phase skill list extraction、generic inspector payloadを所有する。
- Modify `scripts/inspect_skill_context.py`
  - text outputへ`skills` / `dispatch_skills`を追加する。
- Modify `scripts/report_skill_context.py`
  - JSON operation payloadを継承し、text reportへnon-empty skill boundaryを短く表示し、metric sourceをschema v3対応へ更新する。
- Modify `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/context_contract.py`
  - runtime operation read-setへ同じschema v3 semanticsを追加する。
- Modify `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/operation_selection.py`
  - selected operation resultのtop-levelへ`skills` / `dispatch_skills`を返す。
- Modify `skills/issue-implementation-loop/scripts/select_operation.py`
  - non-JSON outputへselected phase skill boundaryを表示する。

### Operation contracts and review policy

- Modify `skills/grill-to-pr-loop/context-contract.toml`
  - schema v3、approved phase mapping、`final-review` operation。
- Modify `skills/issue-implementation-loop/context-contract.toml`
  - schema v3、approved phase mapping。
- Modify `skills/grill-to-pr-loop/SKILL.md`
  - current operation read rule、task-triggered current-phase rule、material review policy。
- Modify `skills/grill-to-pr-loop/references/planning-contract.md`
  - spec self-reviewへmaterial review thresholdを適用する。
- Modify `skills/grill-to-pr-loop/references/remote-delivery.md`
  - final spec alignment reviewを独立`final-review` operationへrouteし、3観点とmaterial finding outputを要求する。
- Modify `skills/issue-implementation-loop/SKILL.md`
  - current operation skill boundaryとmaterial implementation reviewを短く明記する。
- Modify `skills/issue-implementation-loop/references/review-gate.md`
  - review order、reporting threshold、simpler alternative contractをcanonicalにする。
- Modify `skills/issue-implementation-loop/references/mental-model.md`
  - reviewer outputから`Minor`を除く。

### Tests and baseline

- Modify `skills/grill-to-pr-loop/tests/test_context_contract.py`
- Modify `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py`
- Modify `skills/issue-implementation-loop/tests/test_context_contract.py`
- Modify `skills/issue-implementation-loop/tests/test_operation_selection.py`
- Modify `skills/issue-implementation-loop/tests/test_review_gate.py`
- Modify `skills/issue-implementation-loop/tests/test_entrypoint.py`
- Modify `scripts/test_report_skill_context.py`
- Regenerate `knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json`

---

### Task 1: Baseline pressure scenarios

**Files:**

- Read: `skills/grill-to-pr-loop/context-contract.toml`
- Read: `skills/issue-implementation-loop/references/review-gate.md`
- Read: `skills/issue-implementation-loop/references/mental-model.md`
- Evidence target: worker report summary。raw transcriptはcommitしない。

**Interfaces:**

- Consumes: current committed planning head and approved `LRSP-001`。
- Produces: three scored baseline observations with exact behavior/rationalization snippets for the worker report。review policyとphase loadingで少なくとも1件ずつREDを確認する。既にGREENの観点はfailureを捏造せずregression targetとして保持する。

- [x] **Step 1: Run the nit-pressure control**

Fresh read-only evaluatorへ、1つのmaterial requirement gapと複数のnaming/formatting nitsを含むsynthetic committed-diff summaryを渡す。current review contractだけを使わせる。

Fail score:

```text
Minor/nitをfindingとして報告する、またはmaterial gapより先に列挙する。
```

既存contractだけでGREENの場合はその結果を記録し、nit-specific failureを作るためにscenarioや許可taxonomyを歪めない。post-changeでも同じ結果を要求するregression targetとする。

- [x] **Step 2: Run the simplicity control**

Fresh read-only evaluatorへ、acceptance criteriaは満たすが同じvalidationを2層で重複実装したsynthetic changeを渡す。

Fail score:

```text
approvedにする、または具体的なsimpler alternativeなしの任意refactorとして扱う。
```

- [x] **Step 3: Run the phase-loading control**

Fresh read-only evaluatorへ`intake` operation開始時にどのskill instructionsを読むか判断させる。

Fail score:

```text
current contractに境界がないため、tddまたはrequesting-code-reviewを先読みする。
```

- [x] **Step 4: Record baseline evidence**

Worker reportへscenario、verdict、exact behavior/rationalization、fresh-context制約を各80 words以内で記録する。simplicityとphase loadingのREDを確認できない場合、またはfresh evaluator capacityが不足した場合は過去outputを再利用せず停止する。nit controlが既にGREENなら、明示的review output contractのregression evidenceとして記録する。

### Task 2: Schema v3 phase skill contract

**Files:**

- Modify: `scripts/skill_context/contract.py`
- Modify: `scripts/inspect_skill_context.py`
- Modify: `scripts/report_skill_context.py`
- Modify: `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/context_contract.py`
- Modify: `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/operation_selection.py`
- Modify: `skills/issue-implementation-loop/scripts/select_operation.py`
- Modify: both `context-contract.toml`
- Test: both `tests/test_context_contract.py`
- Test: `skills/issue-implementation-loop/tests/test_operation_selection.py`
- Test: `scripts/test_report_skill_context.py`

**Interfaces:**

- Produces generic inspector operation payload:

```python
{
    "schema_version": 3,
    "skill": str,
    "operation": str,
    "files": list[str],
    "skills": list[str],
    "dispatch_skills": list[str],
    # existing metrics unchanged
}
```

- Produces runtime selector top-level fields:

```python
{
    "operation": str,
    "read_set": list[str],
    "skills": list[str],
    "dispatch_skills": list[str],
    "word_budget_result": dict,
}
```

- [x] **Step 1: Add failing generic schema v3 tests**

`skills/issue-implementation-loop/tests/test_context_contract.py`のtemporary skill fixtureで次を固定する。

```python
def test_generic_v3_requires_phase_skill_fields_for_every_operation():
    # missing skills -> operations.test.skills must be an array
    # missing dispatch_skills -> operations.test.dispatch_skills must be an array

def test_generic_v3_rejects_empty_or_duplicate_phase_skill_names():
    # [""] and ["tdd", "tdd"] are invalid

def test_generic_v3_inspector_returns_phase_skill_boundaries():
    # skills == ["requesting-code-review"]
    # dispatch_skills == []

def test_generic_validator_preserves_v1_v2_compatibility():
    # existing fixtures continue to return code 0
```

- [x] **Step 2: Verify generic tests are RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest \
  discover -s skills/issue-implementation-loop/tests -p 'test_context_contract.py'
```

Expected: schema v3 is rejected as unsupported or expected phase skill validation/output is missing。

- [x] **Step 3: Add failing runtime selector tests**

`test_context_contract.py`と`test_operation_selection.py`に次を追加する。

```python
self.assertEqual(payload["skills"], ["requesting-code-review"])
self.assertEqual(payload["dispatch_skills"], [])

self.assertEqual(dispatch_payload["skills"], [])
self.assertEqual(dispatch_payload["dispatch_skills"], ["tdd"])
```

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest \
  discover -s skills/issue-implementation-loop/tests -p 'test_operation_selection.py'
```

Expected: selected payloadに両fieldがなくRED。

- [x] **Step 4: Implement shared schema v3 validation**

`scripts/skill_context/contract.py`で:

```python
def _schema_version(contract, errors):
    # accept 1, 2, 3

def _operation_skills(raw_config, operation, schema, errors):
    # v1/v2 -> ([], [])
    # v3 -> require string arrays, reject empty values and duplicates
    # return (skills, dispatch_skills)
```

`inspect_operation()`はvalidated listsをpayloadに追加する。reference file metricsへskill instruction本文を加えない。

- [x] **Step 5: Implement runtime schema v3 projection**

runtime `context_contract.operation_read_set()`でschema v3を受理し、generic validatorと同じfield/type/empty/duplicate semanticsを適用する。return dictへ`skills` / `dispatch_skills`を追加し、`operation_selection._result()`のtop-levelへprojectionする。

- [x] **Step 6: Update CLI/report rendering**

`inspect_skill_context.py`と`select_operation.py`は次を表示する。

```text
skills: requesting-code-review
dispatch_skills: none
```

`report_skill_context.py`はoperation JSON payloadをそのまま保持し、text reportではnon-empty listだけを短いsuffixとして表示する。`metric_source`は`schema v1/v2/v3`とする。

- [x] **Step 7: Apply exact phase mappings**

両contractをschema v3へ上げ、approved spec tableどおり全operationに2 fieldを明示する。`grill-to-pr-loop`へ:

```toml
[operations."final-review"]
references = ["references/remote-delivery.md"]
skills = ["requesting-code-review"]
dispatch_skills = []
```

を追加する。`delivery`は両fieldを空に保つ。

- [x] **Step 8: Run focused GREEN tests**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_context_contract.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_operation_selection.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts -p 'test_report_skill_context.py'
```

Expected: all pass。

### Task 3: Material review contract

**Files:**

- Modify: both `SKILL.md`
- Modify: `skills/grill-to-pr-loop/references/planning-contract.md`
- Modify: `skills/grill-to-pr-loop/references/remote-delivery.md`
- Modify: `skills/issue-implementation-loop/references/review-gate.md`
- Modify: `skills/issue-implementation-loop/references/mental-model.md`
- Test: `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py`
- Test: `skills/issue-implementation-loop/tests/test_review_gate.py`
- Test: `skills/issue-implementation-loop/tests/test_entrypoint.py`

**Interfaces:**

- Review order: requirements → material simplicity → material risk。
- Reportable severity: `Critical` / `Important` only。
- Simplicity finding required fields: evidence、material impact、required fix、concrete simpler alternative。

- [x] **Step 1: Add failing review wording tests**

Testsは少なくとも次のphrases/absenceを固定する。

```python
for required in (
    "material simplicity",
    "concrete simpler alternative",
    "`Critical` / `Important`",
    "`intent_gap`",
):
    self.assertIn(required, combined_text)

self.assertNotIn("Critical, Important, Minor", mental_model_text)
self.assertIn("Do not report `Minor`, nit", review_gate_text)
```

final review testは`final-review` routing、要件過不足、material simplicity、material riskを要求する。

- [x] **Step 2: Verify review tests are RED**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests -p 'test_grill_to_pr_loop.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_review_gate.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_entrypoint.py'
```

Expected: current wordingにmaterial simplicity / no-Minor contractがなくRED。

- [x] **Step 3: Implement minimal review wording**

`review-gate.md`をcanonical ownerとし、automatic checksの順序をrequirements、material simplicity、material riskへする。material simplicityは具体案がある場合だけ`intent_gap` / `Important`。`Minor` / nit / 好み / 任意改善を報告せず、findingがなければ補充せずapproveする。

両`SKILL.md`は短いrouting ruleだけを追加する。planning self-reviewとfinal review promptも同じ3観点へ揃える。existing hardening / safety / classification sectionsは削らない。

- [x] **Step 4: Run review GREEN tests**

Step 2と同じcommandを実行し、all passを確認する。

### Task 4: Baseline refresh and full verification

**Files:**

- Regenerate: `knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json`
- No worker edits to Epic planning artifacts。

- [x] **Step 1: Regenerate context baseline**

```bash
python3 scripts/report_skill_context.py --all --emit-baseline --json \
  --output knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json
```

baselineは両loop schema v3と`final-review` operationを含む。`llm-wiki` schema v2は維持する。

- [x] **Step 2: Re-run pressure scenarios with changed skill**

Task 1と同じ3 scenarioをfresh read-only evaluatorで実行する。

Pass score:

```text
nitをfindingとして報告しない。
material requirement gapを先に扱う。
具体的simpler alternative付きのImportantを返す。
intakeでfuture-phase workflow skillを先読みしない。
```

raw transcriptはcommitせず、worker reportへ各80 words以内のscore/evidenceを記録する。

- [x] **Step 3: Run full verification**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
python3 scripts/validate_skill_architecture.py --all
python3 scripts/validate_skill_context.py --all
python3 scripts/report_skill_context.py --all --json --require-baseline --fail-on-warning
python3 scripts/validate_dual_host_compatibility.py --skill skills/grill-to-pr-loop
python3 scripts/validate_dual_host_compatibility.py --skill skills/issue-implementation-loop
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
git diff --check
```

- [x] **Step 4: Commit the scoped implementation**

Review `git status --short` and confirm every changed file is inside worker write scope。

```bash
git add \
  skills/grill-to-pr-loop \
  skills/issue-implementation-loop \
  scripts/skill_context \
  scripts/inspect_skill_context.py \
  scripts/report_skill_context.py \
  scripts/test_report_skill_context.py \
  knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json
git commit -m "feat(loop): scope skills and material reviews by phase"
```

- [x] **Step 5: Produce worker report**

Worker reportはchanged files、RED/GREEN evidence、full verification、commit SHA、residual risksを含む。remote write、planning artifact update、ledger updateは行わない。

## Coordinator review and closeout

1. coordinatorはfresh binding verification後、committed `BASE_SHA..HEAD_SHA`を`execute.review`へ送る。
2. reviewerは`Critical` / `Important`だけを返す。material simplicity findingにはconcrete simpler alternativeを必須にする。
3. blocking findingがあればworker-context fixを最大2 cycle実行し、fresh verification後に再reviewする。
4. approved後、coordinatorが`issues.md`、`implementation-plan.md`、`knowledge/index.md`、`knowledge/log.md`へevidenceを同期し、local `PR_READY`を記録する。
5. pushとdraft PRはRemote Gateでexact actionを再提示するまで実行しない。

### Closeout evidence

- Implementation: `10c3cf49d846585cbd5a51ae18e1141ded113572`
- Review fix: `fbaaeeda0e1808d25ab4e029e12eaf0eac19fd1d`
- Approved range: `9653fe8441104e71d0380f0da2913d9a66f05913..fbaaeeda0e1808d25ab4e029e12eaf0eac19fd1d`
- Tests: grill 60 + issue loop 292 + scripts 59 + llm-wiki 6 = 417 pass。
- Validators: architecture、context、strict report `warnings=[]`、dual-host 2件、quick validator 2件、`git diff --check`がpass。
- Review: cycle 1 Important 2件をclose。cycle 2は`Critical` / `Important`なし、material residual riskなし。
- Runtime: `LRSP-001`はlocal `PR_READY`。remote writeは未実施。

## 関連ページ

- [仕様](spec.md)
- [Issue 台帳](issues.md)
- [Loop Review Governance Spec](../loop-review-governance-spec.md)
- [Loop Skill 運用単純化仕様](../loop-skill-operational-simplicity-spec.md)
