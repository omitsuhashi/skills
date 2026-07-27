# Planning Authority Policy 実装計画

> **For agentic workers:** 実装は `issue-implementation-loop` の worker context だけで行う。各 Issue は TDD、fresh verification、scoped commit、別 worker による implementation review を完了してから次の blocker を release する。

**Goal:** planning の最終統合を main planning context、人間の判断権限を Human、supporting agent を advisory/read-only として固定し、model / reasoning の具体値を durable artifact へ保存しない family policy と回帰テストを追加する。

**Architecture:** `skill-architecture.toml` を repository-change-loop family の機械可読な authority 正本とし、`scripts/validate_skill_architecture.py` が exact-value / closed-field contract を検証する。`grill-to-pr-loop` の短い entrypoint と planning reference は人間が読める運用契約を所有する。focused regression はその policy、closed execution schemas、既存 worker-only phase policy を横断して、planning authority の変更が execution protocol や host model routingへ広がらないことを固定する。

**Tech Stack:** Python 3.9-compatible standard library、`unittest`、repository-local small TOML parser、Markdown、TOML、JSON Schema。

---

## 実行前の固定条件

- Approved spec: `knowledge/wiki/syntheses/planning-authority-policy/spec.md`
- Approved spec SHA-256: `6f4a952f35dd44fb930af98403ddfe5f0760af1d398722b338a18ef4493f8c68`
- Spec Gate commit: `ea0d1be65e75e1ed37930062f5ff213d416c349c`
- Issue Gate commit: `5f5bdff`
- Planning branch: `codex/planning-authority-policy/planning`
- Planning base SHA: `f5d151e34de5089d75be68249e09da8a2d14f282`
- Dependency order: `PAP-001 -> PAP-002 -> PAP-003 -> PAP-004`
- Delivery intent: `local_only`
- Production implementation は planning/grill session で行わない。
- `skills/issue-implementation-loop/assets/schemas/`、その validator、scheduler、runtime、Worker Packet builder は変更しない。
- model name、reasoning level、host固有agent ID、cost、latency、availability は durable policy / packet / ledgerへ追加しない。
- approved spec bytes、`spec_binding`、`approval_evidence` が変わったら即停止し、Human Spec Gateへ戻す。
- Issue scope、dependency、write scope、delivery intent が変わる場合は実装を止め、Execution Plan Gateを再構成する。

## Execution Plan Gate evidence

- `decision`: `auto-continue`
- `decided at`: `2026-07-27T09:50:50+09:00`
- `normalized packet`: `knowledge/wiki/syntheses/planning-authority-policy/input-packet.json`
- `packet SHA-256`: `90b22e13c1a91abcee126fd05345941d91d0671c60cb6ec03774005c5c90b9d5`
- `validate_input_packet.py`: `ok: true`、errorsなし。
- `check_capabilities.py`: `ok: true`。approved-spec seal、`issue-implementation-loop`、TDD、independent reviewが利用可能。
- `fresh planning verification`: grill-to-pr-loop 58 tests、llm-wiki 6 testsがpass。`git diff --check`がpass。
- `default checkout`: `HEAD=f5d151e34de5089d75be68249e09da8a2d14f282`、`## main...origin/main`で開始時snapshotと一致。
- `scope reconciliation`: PAP-001〜PAP-004のacceptance criteria、non-goals、write scope、verificationはIssue Gate承認範囲内で変更なし。
- `dependency graph`: `PAP-001 -> PAP-002 -> PAP-003 -> PAP-004`、cycleなし。Gate時点でrunnableなのはPAP-001だけ。
- `phase_branch_policy`: planning artifactはcurrent planning branchでGate commitまで固定し、executionはfresh / compacted coordinatorへ移す。`main_planning_session_may_implement=false`、issue branch ownerはworker。
- `epic_base`: execution coordinatorが `codex/planning-authority-policy/epic-base` をExecution Plan Gate commitにpinして予約する。Gate前にissue worktreeは作らない。
- `reservations`: PAP-001だけを `create_on_run` 候補とし、PAP-002〜PAP-004のbranch / worktreeはblocker releaseまで作らない。
- `execution fallback`: parallel availabilityはplatform-dependent。serial fallbackはworker contextだけで許可し、worker contextがなければ停止する。
- `review policy`: primaryは`requesting-code-review`、fallbackはequivalent independent reviewer、manual fallbackはpre-approvedではない。implementation / fix reviewは最大2 cycle。
- `remote policy`: `local_only`。push、GitHub Issue、PR、merge、release、live installは非承認。将来remote policyが変更されても最終mergeはHuman-only。
- `auto-continue basis`: Spec GateとIssue Gateが承認済み、packet / capability preflightがpass、scope不変、unapproved external / high-risk actionなし。

## Task 1: PAP-001 planning authority family policy と validator

**Files:**

- Modify: `skill-architecture.toml` の `[families.repository-change-loop.context_compaction]` 直前
- Modify: `scripts/validate_skill_architecture.py` の policy constants と `validate_policy`
- Test: `scripts/test_validate_skill_architecture.py`

### 1.1 Failing tests を追加する

- [x] `scripts/test_validate_skill_architecture.py` で `validate_policy` を import し、default policy を深い copy にして直接 mutate できる helper を追加する。
- [x] 次のstructural 4ケースとinvalid-value 5 subcasesを `SkillArchitecturePolicyTests` に追加する。
  - canonical policy が次の exact dict と一致する。
  - `planning_authority` table 全体の欠落を拒否する。
  - 必須 field 1件の欠落を拒否する。
  - 未定義 field `model_name` を拒否する。
  - `integration_owner`、`supporting_agent_authority`、`decision_authority`、`model_selection`、`model_persistence`の各不正値をsubtestで拒否する。

期待する正本:

```python
{
    "integration_owner": "main_planning_context",
    "supporting_agent_authority": "advisory_only",
    "decision_authority": "human",
    "model_selection": "host_runtime",
    "model_persistence": "forbidden",
}
```

- [x] failing test を実行する。

```bash
python3 -m unittest discover -s scripts -p "test_validate_skill_architecture.py"
```

Expected: `planning_authority` が未実装で、新規 test が failure になる。

### 1.2 最小の family policy を追加する

- [x] `skill-architecture.toml` に次の table だけを追加する。

```toml
[families.repository-change-loop.planning_authority]
integration_owner = "main_planning_context"
supporting_agent_authority = "advisory_only"
decision_authority = "human"
model_selection = "host_runtime"
model_persistence = "forbidden"
```

- [x] model / reasoning の具体値、agent ID、routing rule は追加しない。

### 1.3 closed exact-value validator を実装する

- [x] `scripts/validate_skill_architecture.py` に `EXPECTED_PLANNING_AUTHORITY_POLICY` を追加する。
- [x] `_validate_planning_authority_policy(family, errors)` を追加し、次を順に検証する。
  1. `repository-change-loop.planning_authority` が dict である。
  2. `set(policy) == set(EXPECTED_PLANNING_AUTHORITY_POLICY)` である。missing / unknown field は field 名を含む error にする。
  3. 各 field の値が expected string と完全一致する。
- [x] `validate_policy` 末尾で、既存 `_validate_context_compaction_policy` と並べて新 helper を呼ぶ。
- [x] small TOML parser、`schema_version = 1`、既存3 policy group の検証は変更しない。

実装形:

```python
EXPECTED_PLANNING_AUTHORITY_POLICY = {
    "integration_owner": "main_planning_context",
    "supporting_agent_authority": "advisory_only",
    "decision_authority": "human",
    "model_selection": "host_runtime",
    "model_persistence": "forbidden",
}


def _validate_planning_authority_policy(
    family: Dict[str, object], errors: List[str]
) -> None:
    policy = family.get("planning_authority")
    if not isinstance(policy, dict):
        errors.append("repository-change-loop.planning_authority must be a table")
        return
    # Report missing and unknown fields, then exact-value drift.
```

### 1.4 Targeted verification と commit

- [x] targeted tests を pass させる。

```bash
python3 -m unittest discover -s scripts -p "test_validate_skill_architecture.py"
python3 scripts/validate_skill_architecture.py --all
git diff --check
```

- [x] production files が PAP-001 write scope 内だけであることを確認する。
- [x] scoped commit を作成する。

```bash
git add skill-architecture.toml scripts/validate_skill_architecture.py scripts/test_validate_skill_architecture.py
git commit -m "feat: define planning authority policy"
```

#### Spec alignment fix evidence

- PAP-004 spec alignment review cycle 1は、production validatorの挙動ではなく、5 fieldすべてに対する恒久的なper-field invalid-value regression coverage不足をImportant 1件として検出した。
- PAP-001 fix commit `40a4459a8a5ab9b6f6afff0bd3e6505821d049bf`で5 fieldをparameterized subtestsへ固定した。
- focused architecture suite 8件（invalid-value 5 subcases）、scripts 63件、architecture validator、committed-range `git diff --check`がpassした。
- PAP-001 fix review cycle 2はCritical 0 / Important 0 / Minor 0で`approved`。merge commit `11477585f1d0c77c842a1b654d3aaf0f182bda63`でPAP-004 final branchへ統合した。

## Task 2: PAP-002 main planning / supporting agent 運用契約

**Depends on:** `PAP-001`

**Files:**

- Modify: `skills/grill-to-pr-loop/SKILL.md` の `Required Rules`
- Modify: `skills/grill-to-pr-loop/references/planning-contract.md` の `Artifact Contract` 後
- Test: `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py`

### 2.1 Failing documentation contract test を追加する

- [x] `GrillToPrLoopTests` に `test_planning_authority_contract_separates_integration_advice_and_decision` を追加する。
- [x] entrypoint と planning contract の連結 text に、次の意味を持つ exact token / sentence があることを assert する。
  - `main planning context` と `integration owner`
  - `supporting agent` と `advisory-only` / `read-only`
  - `Human` と `decision authority`
  - `bounded question`、`read paths`、`evidence`
  - canonical planning artifact の write / approval / packet seal を supporting agentへ渡さない
  - conflicting advice は vote ではなく evidence 比較で統合する
  - authority-bearing ambiguity は Human gateへ送る
  - fresh primary context の `explicit ownership transfer` は supporting dispatch ではない
- [x] entrypoint word budget `<= 950` の既存 test を維持する。

Expected: 新しい契約文がないため failure になる。hyphenを含むskill directoryはmodule pathとしてimportせず、discoverで実行する。

```bash
python3 -m unittest discover -s skills/grill-to-pr-loop/tests -p "test_grill_to_pr_loop.py"
```

### 2.2 Entrypoint に authority summary を追加する

- [x] `Required Rules` に次の3 owner を短く追加する。
  - main planning context: canonical spec / issue / plan / packet の integration owner
  - supporting agents: advisory-only、read-only
  - Human: Spec / Issue scope と unresolved authority decision の decision authority
- [x] host runtime がmodel / reasoningを選び、repo artifactは具体値を保存しないことを1文で明示する。
- [x] entrypoint へ dispatch手順や長い例を持ち込まない。

### 2.3 Planning reference に dispatch contract を追加する

- [x] `planning-contract.md` に `## Planning Authority / Supporting Agent Dispatch` を追加する。
- [x] supporting dispatch を次で限定する。
  1. coordinator が bounded question と必要最小の repo-relative read paths を指定する。
  2. supporting agent の access は read-only。
  3. return は evidence、source paths、critique、uncertainty に限定する。
  4. canonical artifact write、scope change、Human approval、packet sealは禁止する。
  5. 複数助言が衝突したら main context が evidence を比較し、vote / majority で決めない。
  6. authority-bearing ambiguity が残れば Human gateへ送る。
  7. compaction 後の fresh primary context は explicit ownership transfer がある場合だけ integration owner を引き継ぐ。これは supporting dispatch と区別する。
- [x] 次の runtime boundary を明示する。

```text
A user-selected model change or host model unavailability is host runtime state, not spec or packet drift.
```

### 2.4 Targeted verification と commit

- [x] grill tests、context validators、budget reportを実行する。

```bash
python3 -m unittest discover -s skills/grill-to-pr-loop/tests
python3 scripts/validate_skill_context.py --skill skills/grill-to-pr-loop
python3 scripts/report_skill_context.py --skill skills/grill-to-pr-loop --json
git diff --check
```

- [x] report が hard limit を越える場合、entrypointではなく planning reference の重複を削る。authorityを別 skill / referenceへ分裂させない。
- [x] scoped commit を作成する。

```bash
git add skills/grill-to-pr-loop/SKILL.md skills/grill-to-pr-loop/references/planning-contract.md skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py
git commit -m "docs: define planning agent authority"
```

## Task 3: PAP-003 model非永続化 / execution non-regression

**Depends on:** `PAP-002`

**Files:**

- Create: `skills/grill-to-pr-loop/tests/test_planning_authority_policy.py`
- Read only:
  - `skill-architecture.toml`
  - `skills/grill-to-pr-loop/SKILL.md`
  - `skills/grill-to-pr-loop/references/planning-contract.md`
  - `skills/issue-implementation-loop/assets/schemas/input-packet.schema.json`
  - `skills/issue-implementation-loop/assets/schemas/execution-envelope.schema.json`
  - `skills/issue-implementation-loop/assets/schemas/worker-packet.schema.json`
  - `skills/issue-implementation-loop/assets/templates/execution-envelope.json`

### 3.1 Focused regression test を作る

- [x] new test file は `Path(__file__).resolve()` から repo root を求め、`scripts` を `sys.path` へ追加して repository small TOML parserを再利用する。TOML parserを複製しない。
- [x] `PlanningAuthorityPolicyTests` に次の4 test を追加する。

1. `test_planning_authority_delegates_model_selection_to_host_runtime`
   - `planning_authority` が approved 5-field dict と完全一致する。
   - forbidden concrete-routing keys が policy に存在しない。
2. `test_closed_execution_schemas_reject_model_routing_fields`
   - Input Packet、Execution Envelope、Worker Packet のroot schemaで `additionalProperties` が `false`。
   - root `properties` に次の field がない。
3. `test_model_runtime_change_is_not_spec_or_packet_drift`
   - planning contract の runtime boundary sentence を固定する。
4. `test_existing_worker_only_phase_policy_is_unchanged`
   - Execution Envelope schema と template の `execution_coordinator_context = "fresh_or_compacted"`。
   - `main_planning_session_may_implement = false`。
   - `issue_branch_owner = "worker"`。

禁止field set:

```python
FORBIDDEN_MODEL_FIELDS = {
    "model",
    "model_name",
    "model_reasoning_effort",
    "reasoning_level",
    "intelligence_level",
}
```

- [x] focused test を実行する。PAP-001 / PAP-002 が正しく統合済みなら初回から pass してよい。この Issue のTDD対象は「新しい回帰テスト自体が既存契約を観測できること」であり、production schemaへ故意の変更は加えない。

```bash
python3 -m unittest discover -s skills/grill-to-pr-loop/tests -p "test_planning_authority_policy.py"
```

### 3.2 Negative-control を確認する

- [x] test file の作業中だけ policy payloadのlocal copyへ `model_name` を追加し、assert helper が failすることを確認する。production fileは変更しない。
- [x] negative-control を戻し、focused test を再実行して pass させる。
- [x] `git diff -- skills/issue-implementation-loop/assets skills/issue-implementation-loop/scripts` が空であることを確認する。

### 3.3 Cross-loop verification と commit

- [x] full grill / execution tests を実行する。

```bash
python3 -m unittest discover -s skills/grill-to-pr-loop/tests
python3 -m unittest discover -s skills/issue-implementation-loop/tests
git diff --check
```

- [x] scoped commit を作成する。

```bash
git add skills/grill-to-pr-loop/tests/test_planning_authority_policy.py
git commit -m "test: guard planning model non-persistence"
```

## Task 4: PAP-004 wiki同期 / full verification closeout

**Depends on:** `PAP-003`

**Files:**

- Modify: `knowledge/wiki/syntheses/planning-authority-policy/issues.md`
- Modify: `knowledge/wiki/syntheses/planning-authority-policy/implementation-plan.md`
- Verify, do not hand-edit after seal: `knowledge/wiki/syntheses/planning-authority-policy/input-packet.json`
- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`

### 4.1 Durable status と evidence を同期する

- [x] `issues.md` の各 Issue に implementation commit、verification、review verdictを記録し、dependency release順と最終状態を同期する。
- [x] `implementation-plan.md` の完了 checkbox と実際の結果が一致するよう更新する。未実行項目を完了扱いしない。
- [x] `knowledge/index.md` の Planning Authority Policy entry から spec、Issue台帳、実装計画、sealed Input Packetを発見可能にする。
- [x] `knowledge/log.md` に implementation / review closeout を append-only で追加する。
- [x] spec bytes と sealed Input Packet bytes は変更しない。変更が必要なら実装を止め、該当Gateへ戻す。

### 4.2 Full verification を fresh に実行する

- [x] 次の順で実行し、command / result / failure修正を closeout evidenceへ残す。

```bash
python3 -m unittest discover -s skills/grill-to-pr-loop/tests
python3 -m unittest discover -s skills/issue-implementation-loop/tests
python3 -m unittest discover -s skills/llm-wiki/tests
python3 -m unittest discover -s scripts
python3 scripts/validate_skill_architecture.py --all
python3 scripts/validate_skill_context.py --all
python3 scripts/report_skill_context.py --all --json
python3 scripts/validate_dual_host_compatibility.py --skill skills/grill-to-pr-loop
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
git diff --check
```

- [x] default checkout `/Users/omitsuhashi/repos/omitsuhashi/skills` が planning開始時の `HEAD=f5d151e34de5089d75be68249e09da8a2d14f282` と開始時statusを維持していることをread-onlyで確認する。
- [x] production diff が approved write scope 内で、execution schemas / validator / scheduler / runtimeに変更がないことを確認する。

#### 実行結果

- unit suites: grill-to-pr-loop 63件、issue-implementation-loop 284件、llm-wiki 6件、scripts 63件がpass。
- focused spec fix: architecture suite 8件と5-field invalid-value subcasesがpass。
- validators: skill architecture、3 context contracts、scoped dual-host compatibility、grill-to-pr-loop quick validatorがpass。
- context report: warningsなし。grill-to-pr-loop execution-planは推定8778 / 11000 tokens、headroom 20%、baseline growth 9.89%。
- immutable artifacts: spec SHA-256 `6f4a952f35dd44fb930af98403ddfe5f0760af1d398722b338a18ef4493f8c68`、sealed packet SHA-256 `90b22e13c1a91abcee126fd05345941d91d0671c60cb6ec03774005c5c90b9d5`。
- scope / checkout: approved write scope外のPAP-004 diffなし。execution schemas / validator / scheduler / runtimeのproduction diffはゼロ。default checkoutは開始時HEAD / statusと一致。
- remote action: 0。

### 4.3 Closeout commit と review

- [x] scoped closeout commit を作成する。

```bash
git add knowledge/wiki/syntheses/planning-authority-policy/issues.md knowledge/wiki/syntheses/planning-authority-policy/implementation-plan.md knowledge/index.md knowledge/log.md
git commit -m "docs: close planning authority policy implementation"
```

- [x] initial closeout range `681dfb723be171b81502540ded0458c186f6f036..4bc6fe52e4bdd062a10766b96446b325a57c540a`のimplementation review cycle 1を実施し、findings 0で`approved`を得た。
- [x] spec alignment review cycle 1を実施し、PAP-001のper-field regression coverage不足をImportant 1件として受けた。
- [x] PAP-001 fix、fresh verification、fix review cycle 2承認、final branch integrationを完了した。
- [ ] fix同期commitを含むfinal rangeに対するimplementation review cycle 2とspec alignment review cycle 2を別 reviewer contextで実施する。
- [ ] cycle 2でin-scope Critical / Important findingがあれば、上限内でworkerが修正し、fresh verification、commit更新、再reviewを行う。
- [ ] review承認後に local `PR_READY` とする。`local_only` なので push、GitHub Issue、PR、merge、release、live installは行わない。

## Completion criteria

- [ ] `PAP-001 -> PAP-002 -> PAP-003 -> PAP-004` が順に release / complete されている。
- [x] approved 5-field policyがmachine-readable正本とhuman-readable contractで一致する。
- [x] supporting agents は advisory/read-onlyで、Human decision authorityが維持される。
- [x] model / reasoning の具体値が新規 durable artifact fieldとして存在しない。
- [x] execution schema / runtime implementationにproduction diffがない。
- [x] worker-only / fresh-or-compacted coordinator contractが回帰していない。
- [ ] 全verificationと2種類のreviewが承認済みである。
- [x] default checkoutが開始時snapshotから不変である。
- [x] remote actionがゼロである。
