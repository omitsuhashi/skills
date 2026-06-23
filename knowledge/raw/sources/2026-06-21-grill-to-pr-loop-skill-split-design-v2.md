# Grill to PR Loop スキル分割・非停止実行 詳細設計 v2

- 対象Repository: `omitsuhashi/skills`
- 対象現行Skill: `skills/grill-to-pr-loop`
- 状態: Proposed
- 作成日: 2026-06-21
- 目的:
  - 人間待ちを局所化し、無関係な開発を止めない
  - 非停止型のIssue実装機構を他の開発ワークフローから再利用できるようにする
  - スキル分割による文脈断絶や過剰な外部オーケストレーションを避ける

---

## 1. 最終判断

現行の `grill-to-pr-loop` を次の2層に分割する。

```text
Composition Skill
  grill-to-pr-loop
    設計対話 → Spec/PRD → Issue分解 → Execution Plan → PR delivery

Reusable Execution Skill
  issue-implementation-loop
    承認済みIssue群 → 非停止型実装 → 検証 → Issueレビュー → PR-ready
```

新設するユーザー向けSkillは **`issue-implementation-loop` の1つだけ** とする。

以下は独立Skillにせず、`issue-implementation-loop` のreferenceまたは決定論的helperとして持つ。

```text
- Execution Envelope
- Worktree Reservation
- Typed Dependency Edge
- Event-driven Scheduler
- Scoped Human Wait
- Durable Resume
- Issue Implementation Review Gate
```

現時点では次を作らない。

```text
- execution-envelope skill
- worktree-manager skill
- scheduler skill
- human-gate-manager skill
- review-gate skill
- generic agent-orchestration framework
```

理由は、これらに単独の明確なユーザートリガーがなく、分離すると同じ手順を複数Skill間で往復することになり、全体文脈と責任主体が分散するためである。

---

## 2. 設計原則

### 2.1 Skill分割はsource organizationであり、runtime handoffではない

`grill-to-pr-loop` から `issue-implementation-loop` を使う際も、原則として同じparent coordinatorが全体文脈と最終責任を保持する。

```text
悪い構成:
  planning agent
    → scheduler agent
      → review agent
        → delivery agent

採用構成:
  one coordinator
    ├─ loads grill-to-pr-loop procedure
    ├─ loads issue-implementation-loop procedure
    ├─ dispatches isolated issue workers when useful
    └─ retains global state and final responsibility
```

Skillは手順モジュールであり、別人格へのhandoffではない。

### 2.2 外部stateは決定論的helperで守る

Git、worktree、SHA、lease、resource lock、event logは外部状態を持つため、検証と整合処理にはscriptを使う。

ただしscriptは次だけを行う。

- schema validation
- DAG cycle検出
- typed edgeの整合性検証
- write-scope conflict検出
- runnable候補計算
- illegal state transition検出
- snapshot/event reconciliation

scriptは次を行わない。

- LLMへのnode単位routing
- Issue内容の意味判断
- spec変更の自動決定
- risk acceptance
- 人間承認の代替

### 2.3 一つの責任主体を維持する

- coordinatorがapproved planとruntime stateを所有する
- workerは割り当てIssueだけを実装する
- reviewerはIssue packetに対する差分だけをレビューする
- worker/reviewerは中央stateを直接編集しない
- GitHub操作は既存GitHub skillへ委譲するが、coordinatorが承認境界と結果整合を保持する

### 2.4 抽象化は第2利用者が現れてから進める

`issue-implementation-loop` は複数のソフトウェア開発フローで再利用可能な粒度にする。

研究、知識整理、営業運用など非Gitワークフローにも共通化したくなった場合は、少なくとも第2の実利用者と共通schemaが確認できてから `non-blocking-workflow-core` の抽出を検討する。

現時点でGit/worktree/SHA/reviewを含む処理を抽象schedulerへ持ち上げない。

---

## 3. Skill責務

## 3.1 `grill-to-pr-loop`

### Trigger

```yaml
name: grill-to-pr-loop
description: >-
  Use when a user wants an end-to-end repository change beginning with
  design interrogation and durable design docs, followed by spec/PRD synthesis,
  issue decomposition, dependency-aware implementation, and PR delivery.
```

### Owns

- `grill-with-docs` を必須front doorとして使う
- design ambiguityの解消
- durable spec / ADR / glossary
- PRD/spec synthesis
- vertical-slice Issue分解
- acceptance criteriaとnon-goals
- local issue source of truth
- optional GitHub Issue mirrorの提案
- `issue-implementation-loop`への正規化済み入力作成
- 実装結果の最終報告
- 明示承認後のPR delivery調整

### Does not own

- worktree lifecycle
- Issue runtime state
- event-driven scheduling
- worker lease
- review/fix cycle
- scoped human wait
- resume reconciliation
- runnable計算

### End-to-end state

```text
Intake
  → Grill
  → Spec
  → Spec Gate
  → Issue decomposition
  → Execution Plan packet
  → Execution Plan Gate
  → issue-implementation-loop
  → optional PR delivery
  → Completion report
```

## 3.2 `issue-implementation-loop`

### Trigger

```yaml
name: issue-implementation-loop
description: >-
  Use when implementing one or more approved local or remote issues in a
  repository with dependency-aware scheduling, isolated git worktrees,
  verification and issue-scoped review, resumable state, and human escalation
  that must not block unrelated work. Do not use for initial design interrogation
  or issue decomposition.
```

### Owns

- approved work item packetのvalidation
- Execution Envelope
- all-issue branch/worktree reservation
- capability preflight
- typed dependency edges
- event-driven runnable recomputation
- implementation/review laneの並行管理
- TDD/verification contract
- Issue Implementation Review Gate
- bounded automatic remediation
- scoped human request
- worker attempts / leases / idempotency
- durable runtime state
- session resume/reconciliation
- PR-ready判定

### Does not own

- design interrogation
- PRD作成
- Issue内容の新規設計
- acceptance criteriaの無承認変更
- GitHubへの無承認write
- merge / deploy / destructive action

### Direct invocation

`grill-to-pr-loop` を経由せず、既に承認済みIssueがある場合にも直接使える。

```text
既存GitHub Issue群
  → local normalized work-item packet
  → Execution Envelope Gate
  → implementation loop
```

---

## 4. Composition構造

```text
user
  ↓
grill-to-pr-loop                         same coordinator
  ├─ grill-with-docs                     design interrogation
  ├─ to-prd                              spec synthesis
  ├─ to-issues                           issue draft/review
  ├─ issue-implementation-loop           reusable execution procedure
  │   ├─ tdd                             per-issue behavior change discipline
  │   └─ requesting-code-review          independent issue review when available
  └─ GitHub specialist skills            explicit remote delivery actions
```

`issue-implementation-loop` はworker agentではない。同じcoordinatorが読み込む手順である。

並列agent/threadを使うのは、write scopeが分離されたIssue実装・Issueレビューに限定する。

---

## 5. Gate再設計

人間の事前確認を減らし、実装開始後の停止を防ぐため、既存の多数のgateを次へ整理する。

### 5.1 Spec Gate

確認対象:

- problem / outcome
- accepted decisions
- non-goals
- acceptance criteria
- rollback / stop conditions
- Epic ID

### 5.2 Execution Plan Gate

従来のIssue Gate、Worktree Map Gate、Initial Verification Gate、review fallback選択を原則として一つのpacketへ統合する。

確認対象:

- 全Issueとacceptance criteria
- dependency graph
- typed release conditions
- 全branch/worktree reservation
- base policy
- write scope / resource lock
- baseline verification
- worker capability
- reviewer capabilityとfallback
- parallel/serial fallback policy
- retry budget
- human escalation policy
- optional GitHub Issue mirrorの具体的action
- optional draft PR batch policy

承認後、Envelope内の通常遷移では再承認しない。

### 5.3 Runtime Exception Gate

実装開始後に人間が必要なのは次に限定する。

- approved spec/acceptance criteriaの変更
- approved write scope外の変更
- unresolved Critical/Important findingのrisk acceptance
- collision等で予約済みbranch/pathを変更する必要
- envelope外のremote write
- credential / billing / production / destructive action
- state corruptionや全体共有baseの重大な不整合

Runtime Exception Gateは最小scopeへ局所化する。

---

## 6. Skill間Input Contract

`grill-to-pr-loop` は `issue-implementation-loop` に次のnormalized packetを渡す。

```json
{
  "schema_version": 1,
  "repo_root": "/abs/path/to/repo",
  "epic_id": "non-blocking-loop",
  "artifact_root": "knowledge/wiki/syntheses/non-blocking-loop",
  "spec": {
    "path": "knowledge/wiki/syntheses/non-blocking-loop-spec.md",
    "approved_revision": 3,
    "approved_hash": "sha256:..."
  },
  "work_items": [
    {
      "id": "G2PR-001",
      "title": "...",
      "source": {
        "type": "local",
        "path": "knowledge/wiki/syntheses/non-blocking-loop-issues.md"
      },
      "acceptance_criteria": ["..."],
      "non_goals": ["..."],
      "verification": ["python3 -m pytest ..."],
      "write_scope": ["path:skills/grill-to-pr-loop"],
      "dependencies": []
    }
  ],
  "delivery_intent": "local_only"
}
```

`issue-implementation-loop` はこのpacketからExecution Envelopeを作る。

GitHub、Jira等がsourceでも、実行前に同じlocal normalized packetへ変換する。

---

## 7. Skill間Output Contract

`issue-implementation-loop` は次を返す。

```json
{
  "schema_version": 1,
  "epic_id": "non-blocking-loop",
  "status": "local_complete",
  "envelope_revision": 1,
  "issues": {
    "G2PR-001": {
      "status": "PR_READY",
      "branch": "codex/non-blocking-loop/G2PR-001-...",
      "worktree": "/abs/...",
      "base_sha": "abc123",
      "head_sha": "def456",
      "verification": "passed",
      "implementation_review": "approved",
      "residual_risks": []
    }
  },
  "pending_human_requests": [],
  "delivery_candidates": ["G2PR-001"],
  "runtime_state_root": "/repo/.git/agent-runs/issue-implementation-loop/non-blocking-loop"
}
```

`grill-to-pr-loop` はこの結果を使って、完了報告または承認済みPR deliveryへ進む。

---

## 8. ArtifactとRuntime Stateの分離

前案の `runtime-state.json` をtracked docs directoryへ置く方式は修正する。

### 8.1 Durable planning artifacts

repoのinstructionに従う。fallback例:

```text
<artifact-root>/
├── spec.md
├── issues.md
├── execution-envelope.json
├── decisions.md
├── worktree-reservations.md
└── completion-summary.md
```

これらは人間向け・承認・監査用のdurable artifactである。

### 8.2 Mutable runtime state

中央の可変stateはworker branchに含めない。

既定:

```text
$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/
├── runtime-state.json
├── events.jsonl
├── reports/
├── reviews/
├── decisions/
├── locks/
└── recovery/
```

理由:

- 全worktreeから共有可能
- issue branchのdiffを汚さない
- coordinator-owned fileのmerge conflictを避ける
- workerがledgerを並行編集しない

repo/local policyが別state rootを指定する場合はそれを優先する。

### 8.3 Runtime update rule

中央stateを書けるのはcoordinatorだけ。

```text
worker result message
  → coordinator validates attempt/report ID
  → append event
  → atomic snapshot update
  → render human summary when necessary
```

workerがshared `runtime-state.json` やlocal issue ledgerを直接更新してはならない。

---

## 9. `issue-implementation-loop` Directory設計

```text
skills/issue-implementation-loop/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── core.md
│   ├── execution-envelope.md
│   ├── dependency-contract.md
│   ├── worktree-lifecycle.md
│   ├── scheduler.md
│   ├── worker-contract.md
│   ├── review-gate.md
│   ├── human-wait.md
│   ├── runtime-state.md
│   ├── recovery.md
│   └── remote-delivery.md
├── assets/
│   ├── schemas/
│   │   ├── input-packet.schema.json
│   │   ├── execution-envelope.schema.json
│   │   ├── runtime-state.schema.json
│   │   ├── event.schema.json
│   │   ├── worker-report.schema.json
│   │   └── human-request.schema.json
│   └── templates/
│       ├── execution-envelope.json
│       ├── decisions.md
│       └── completion-summary.md
├── scripts/
│   ├── check_capabilities.py
│   ├── validate_input_packet.py
│   ├── validate_execution_envelope.py
│   ├── compute_next_actions.py
│   ├── validate_runtime_state.py
│   ├── rebuild_runtime_state.py
│   └── reconcile_git_state.py
└── tests/
    ├── test_validate_execution_envelope.py
    ├── test_compute_next_actions.py
    ├── test_validate_runtime_state.py
    └── fixtures/
```

---

## 10. Selective Reference Loading

`SKILL.md` を巨大な単一契約にせず、modeごとに必要なreferenceだけ読む。

### Modes

```text
prepare
  input packetを検証し、Execution Envelopeを作る

execute
  approved Envelopeから実装・review loopを動かす

resume
  session中断後にstateとgitをreconcileする

status
  現在状態、待機集合、critical pathを報告する

deliver
  PR-ready branchを明示承認されたremote actionへ渡す
```

### Read set

```text
Always:
  references/core.md

prepare:
  execution-envelope.md
  dependency-contract.md
  worktree-lifecycle.md

execute:
  scheduler.md
  worker-contract.md
  review-gate.md
  human-wait.md
  runtime-state.md

resume:
  runtime-state.md
  recovery.md

status:
  runtime-state.md
  scheduler.md

deliver:
  remote-delivery.md
```

全referenceを毎回ロードしない。

---

## 11. Execution Envelope

全Issueを開始前に予約・承認する。

```json
{
  "schema_version": 1,
  "epic_id": "non-blocking-loop",
  "revision": 1,
  "epic_base": {
    "ref": "main",
    "sha": "<immutable-sha>"
  },
  "execution_policy": {
    "parallel_preferred": true,
    "serial_fallback_preapproved": true,
    "implementation_slots": 4,
    "review_slots": 2,
    "wave_is_barrier": false
  },
  "review_policy": {
    "primary": "requesting-code-review",
    "fallbacks": ["equivalent-independent-reviewer"],
    "manual_fallback_preapproved": false,
    "max_fix_cycles": 3,
    "same_finding_limit": 2
  },
  "human_policy": {
    "default_scope": "issue",
    "epic_scope_requires_reason": true
  },
  "remote_write_policy": {
    "mode": "local_only",
    "approved_actions": []
  },
  "work_items": {
    "G2PR-001": {
      "branch": "codex/non-blocking-loop/G2PR-001-...",
      "worktree_path": "/abs/.../G2PR-001-...",
      "worktree_state": "create_on_run",
      "base_policy": {"type": "epic_base"},
      "write_scope": ["path:skills/grill-to-pr-loop"],
      "dependencies": []
    },
    "G2PR-002": {
      "branch": "codex/non-blocking-loop/G2PR-002-...",
      "worktree_path": "/abs/.../G2PR-002-...",
      "worktree_state": "reserved",
      "base_policy": {
        "type": "blocker_head",
        "issue": "G2PR-001"
      },
      "write_scope": ["path:skills/grill-to-pr-loop/scripts"],
      "dependencies": [
        {
          "issue": "G2PR-001",
          "strength": "hard",
          "release_on": "review_approved",
          "base_effect": "branch_from_blocker_head"
        }
      ]
    }
  }
}
```

### Envelope内で自動実行可能

- blocker release
- reserved worktree activation
- local branch creation
- TDD/implementation
- local commit
- targeted/final verification
- issue-scoped review
- in-scope findingのbounded fix
- reverify / rereview
- downstream release
- approved serial fallback

### Envelope revisionが必要

- branch/path reservation変更
- acceptance criteria変更
- dependency edge変更
- write scope拡張
- base strategy変更
- unapproved remote action追加
- retry/risk policy変更

---

## 12. Capability Preflight

実装後に能力不足が発覚して止まることを避ける。

Execution Plan Gate前に次を確認する。

- git repository / common git dir
- dirty stateとplanned scopeの衝突
- existing branch/worktree/path collision
- required commands
- test/verification availability
- independent worker capability
- serial fallback policy
- reviewer skill availability
- independent reviewer execution capability
- equivalent reviewer
- manual fallback policy
- GitHub remote/auth（remote deliveryを予定する場合のみ）

`parallel_preferred=true` かつ `serial_fallback_preapproved=true` なら、parallel workerを起動できない場合でも追加確認なしにserialで継続する。

parallelが絶対要件なら、runtime中ではなくExecution Plan Gate前に停止する。

---

## 13. Event-driven Scheduler

Waveはlaunch cohortであり、completion barrierではない。

```text
W1: A, B
A → C

A review approved
  → C runnable
  → slotとlockがあれば即時起動

Bはそのまま継続
```

### Parent loop

```text
reconcile external state
  → ingest new reports
  → apply human decisions
  → expire/recover stale leases
  → evaluate edge release conditions
  → recompute runnable/reviewable/fixable
  → dispatch available work
  → persist events/snapshot
  → repeat after every event
```

外部LLM routerを作らず、parent coordinatorが手順全体を保持する。

---

## 14. Typed Dependency Edge

```text
strength:
  hard | soft

release_on:
  artifact_ready
  review_approved
  integrated
  pr_opened
  pr_merged
  human_decision
  external_condition

base_effect:
  none
  branch_from_blocker_head
  branch_from_integration_head
```

Issue Gateでは各hard edgeについて確認する。

1. downstreamが今開始できない具体的理由
2. 解除を観測するevent
3. blocker codeをbaseへ含める必要
4. human decisionをcritical pathへ置く必要

複数blocker headをdownstream workerが任意mergeしてはならない。専用integration work itemまたは承認済みintegration branchを使う。

---

## 15. Human Wait Scope

```text
issue
  対象Issueだけ停止

descendants
  対象Issueと未解除hard descendantsを停止

resource
  同じresource lockを必要とするIssueを停止

epic
  全Issueを停止
```

既定は `issue`。

Epic全体停止は次に限定する。

- approved Envelopeの破損
- DAG cycle / runtime state corruption
- user workを壊す共有base問題
- credential/security incident
- 全Issueへ影響する外部契約変更

人間待ち中も、無関係なrunnable work item、review lane、local verification、remote lane以外の処理を継続する。

---

## 16. Review Pipeline

### 16.1 Review scope

reviewerが指摘できるのは次に対する未達だけ。

- approved issue
- requirements/spec
- acceptance criteria
- non-goals
- write scope
- verification evidence

一般的な理想論やscope外refactorはfindingにしない。

### 16.2 Bounded remediation

```text
review
  → Critical/Important in-scope finding
  → fix attempt
  → targeted verification
  → fresh final verification
  → update local commit
  → rereview
```

`max_fix_cycles` または `same_finding_limit` を超えた場合だけ `WAITING_HUMAN(scope=issue)`。

### 16.3 Lane separation

```text
implementation_slots: 4
review_slots: 2
integration_slots: 1
```

Issue Aのreview待ちがIssue B/Cのimplementationを止めない。

---

## 17. ResumeとRecovery

再開時に比較する。

- approved Envelope hash/revision
- runtime snapshot
- event log
- `git worktree list`
- branch/head/base SHA
- dirty state
- worker/reviewer result
- active lease
- GitHub Issue/PR state（権限と必要性がある場合）

### Recovery rule

- snapshotとevent logの差分はeventから再構築
- `RUNNING`だがworker不在ならworktreeをinspection
- valid commit/reportがあれば次stateへ進める
- incompleteなら同じattemptまたは新attemptで再dispatch
- stale reportはattempt ID/generationで無視
- retry budget超過時だけ人間へ上げる

---

## 18. Remote Delivery Boundary

`issue-implementation-loop` の既定終端は `PR_READY`。

Remote write modes:

```text
local_only
per_action
batch_draft_prs
```

Batch approvalに含められるもの:

- exact branchのpush
- exact targetへのdraft PR作成
- exact GitHub Issue linkage

常に別承認:

- merge
- force push
- ready-for-review変更
- production deploy
- billing/permission/credential操作
- destructive remote action

Remote laneが失敗してもlocal implementation/reviewは継続する。

---

## 19. 現行ファイルからの移動表

| 現行内容 | 移動先 |
| --- | --- |
| Grill / Spec / PRD | `grill-to-pr-loop` |
| Local Issue decomposition | `grill-to-pr-loop` |
| GitHub Issue mirror planning | `grill-to-pr-loop` |
| Worktree Map / reservation | `issue-implementation-loop` |
| Initial execution verification | `issue-implementation-loop` |
| Parallel Goal Loop Scheduler | `issue-implementation-loop` |
| Issue Implementation Review Gate | `issue-implementation-loop` |
| Goal worker contract | `issue-implementation-loop` |
| blocker release | `issue-implementation-loop` |
| human wait scope | `issue-implementation-loop` |
| runtime state / events / leases | `issue-implementation-loop` |
| PR-ready result | `issue-implementation-loop` |
| GitHub push/PR coordination | `grill-to-pr-loop` + GitHub specialist |
| final end-to-end report | `grill-to-pr-loop` |

---

## 20. Prerequisite分離

### `grill-to-pr-loop/scripts/check_prereqs.py`

```text
Required for design phase:
  grill-with-docs

Optional/planning accelerators:
  to-prd
  to-issues

Required before execution phase:
  issue-implementation-loop
```

実装skillが未導入でも、ユーザーがplanning-onlyを求めている場合はSpec/Issue artifactsまで進められる。

### `issue-implementation-loop/scripts/check_capabilities.py`

```text
Required:
  git
  valid repository
  approved normalized input packet

Conditional:
  tdd skill or equivalent discipline
  requesting-code-review or approved equivalent/fallback
  independent worker/thread support
  GitHub access for remote delivery only
```

---

## 21. Pressure Scenario / Test設計

### Scheduler

1. A/Bが同時実行、A→C。A review pass後にBを待たずCを起動
2. issue-scoped human waitが無関係なD/Eを止めない
3. descendant scopeがhard descendantsだけを止める
4. resource scopeが同じlock利用者だけを止める
5. epic scopeが全体を止める

### Reservation

6. blocked itemのbranch/pathは承認済みだがworktree未作成
7. dependency release後に追加承認なしでworktree activation
8. activation時collisionは当該Issueだけhuman wait
9. approved reservation外pathは拒否

### Capability

10. parallel unavailable + serial fallback preapprovedなら継続
11. parallel requiredならExecution Plan Gate前に検出
12. reviewer unavailable + approved fallbackなら実装後に止まらない

### Review

13. Important findingを自動修正して再review pass
14. retry budget超過でissue scope human request
15. out-of-scope observationをfindingとして記録しない

### State/Recovery

16. duplicate worker reportをidempotently無視
17. stale attempt reportを無視
18. session interruption後にworktree/SHA/eventから再開
19. dirty worktreeを勝手にresetしない
20. snapshot破損時にevent logから再構築

### Remote

21. remote auth失敗でもlocal lane継続
22. batch envelope外branchのpushを拒否
23. merge/force-pushはbatch approvalに含めない

---

## 22. Rollout Plan

### Phase 0: Design canonicalization

- 本設計を `knowledge/wiki/syntheses/` に保存
- `knowledge/index.md` と `knowledge/log.md` を更新
- skill名と責務を承認

### Phase 1: Safe extraction without behavior change

- `issue-implementation-loop` skeleton作成
- 現行のworktree/scheduler/review contractを移動
- `grill-to-pr-loop` は新skillへのcompositionを明記
- 現行behaviorをpressure testsで保持

### Phase 2: Gate consolidation

- Spec Gate + Execution Plan Gateへ整理
- all-issue reservation
- capability preflight
- serial/reviewer fallback事前選択

### Phase 3: Non-blocking scheduler

- wave barrier廃止
- event-driven runnable recompute
- scoped human wait
- implementation/review lane separation

### Phase 4: Durable runtime

- git-common-dir state root
- event log / snapshot
- attempts / leases / idempotency
- resume/reconciliation scripts

### Phase 5: Delivery policy

- `PR_READY` output contract
- local-only / per-action / batch draft PR policy
- GitHub skill integration

### Phase 6: Operational validation

- real repositoryでsmall DAG test
- slow sibling scenario
- human wait scenario
- interruption/resume scenario
- metrics review

---

## 23. Metrics

```text
- total lead time
- runnable-to-start latency
- human wait time
- critical-path human idle ratio
- unrelated continuation rate
- review queue latency
- automatic remediation success rate
- epic-wide stop count
- resume recovery count
- duplicate/stale report count
- capability failure discovered after start
```

最重要:

```text
Unrelated continuation rate
  = human wait中に実行可能だった無関係Issueのうち、継続できた割合

Late capability discovery count
  = 実装開始後に初めて判明したworker/reviewer/tool不足の件数
```

目標:

```text
Unrelated continuation rate = 100%
Late capability discovery count = 0
```

---

## 24. Future Extraction Criteria

将来 `non-blocking-workflow-core` を抽出するのは、次をすべて満たした場合だけ。

1. `issue-implementation-loop` 以外に実利用者が2つ以上ある
2. Git/worktree/SHAを除いた共通state machineが安定している
3. 共通schemaが全体の70%以上を占める
4. 抽出後も一つのcoordinatorがprocedure全体をin-contextで保持できる
5. skill routingが増えてもユーザートリガーが曖昧にならない
6. 外部LLM node routerを必要としない

候補利用者:

- research work-item execution
- knowledge proposal review queue
- document migration batch
- data quality remediation queue

これらが現れるまでは、generic coreを先に作らない。

---

## 25. Acceptance Criteria

- `grill-to-pr-loop` がplanning/composition責務に縮小されている
- `issue-implementation-loop` が既存Issueから直接利用できる
- 同じcoordinatorが全体文脈と最終責任を保持する
- Execution Plan Gate後の通常遷移で再承認を要求しない
- blocked Issueを含む全Issueのbranch/worktreeが予約される
- blocked Issueの物理worktreeは解除前に作られない
- Issue eventごとにrunnableを再計算する
- Wave全体完了を待たない
- human waitは既定でissue scope
- unrelated workはhuman wait中も継続する
- reviewer/parallel fallbackは開始前に確定する
- runtime stateはissue branchのtracked fileに置かない
- worker/reviewerは中央stateを直接更新しない
- session中断後にstate/git/reportをreconcileできる
- remote failureはlocal laneを止めない
- merge/force-push/deploy/destructive actionは引き続き明示承認
- standalone scheduler/approval/worktree skillを過早に増やしていない

---

## 26. 推奨名称

```text
Existing composition skill:
  grill-to-pr-loop

New reusable skill:
  issue-implementation-loop

Display name:
  Issue Implementation Loop

Japanese summary:
  依存関係対応・非停止型Issue実装ループ
```

`orchestrator`、`agent graph`、`scheduler framework` をSkill名に使わない。

---

## 27. まとめ

最適な分割は、現行Skillを細かな機能別Skillへ分解することではない。

```text
上流の設計・Issue作成:
  grill-to-pr-loop

再利用可能な実装実行:
  issue-implementation-loop
```

この2層にすることで、次を両立できる。

- end-to-end user experienceを維持
- approved Issueからの直接実行を可能にする
- 人間待ちの局所化
- worktree/review/recovery機構の再利用
- 一つのcoordinatorによる全体文脈保持
- 過剰な外部オーケストレーションの回避
