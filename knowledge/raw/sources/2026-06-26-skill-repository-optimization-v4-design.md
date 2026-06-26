# Skill Repository Optimization V4 — 詳細設計

## 最終判断

現在の `main` は、PR #19でループ系V3最適化がマージ済みです。context contract、構造化operation selection、bounded worker packet、resume briefまで実装されています。

したがって次の設計では、ループ系スキルをさらに分割しません。

```text
user-facing skill
├── grill-to-pr-loop
│   └── 設計、仕様、Issue分解、Execution Plan、delivery調整
└── issue-implementation-loop
    └── 承認済みIssueの実装、レビュー、依存解除、PR_READY化
```

`scheduler`、`runtime-state`、`review-gate`、`worker-contract`、`context-manager` などは、引き続きreference / schema / script / internal libraryとして保持します。V3でも「user-facing loop skillは2つ」「内部実行機構を独立skillにしない」が採用されています。

狙うべきV4は、次の4点です。

```text
1. context-contract.toml をread-setの唯一の正本にする
2. word countから、文字数＋推定token数によるbudgetへ移行する
3. worker / reviewer / resumeの文脈をrevision付きartifactとして管理する
4. 粒度とcontext regressionをCIで固定する
```

---

## 1. 現状の主要課題

### 1.1 read-setが三重管理されている

`grill-to-pr-loop` のoperationとreference対応は、現在以下の3か所にあります。

```text
SKILL.md
references/workflow-contract.md
context-contract.toml
```

`SKILL.md` がmode別referenceを列挙し、 `workflow-contract.md` も同じ対応を持ち、 `context-contract.toml` も機械可読な同一対応を持っています。

この状態では、片方だけ変更されると、モデルが読むreferenceとvalidatorが想定するreferenceがずれます。

### 1.2 `issue-implementation-loop` ではすでにずれがある

`SKILL.md` は `execute` で以下すべてを読むよう指示しています。

```text
scheduler
worker-contract
review-gate
human-wait
runtime-state
```

一方、`context-contract.toml` は以下のように分離されています。

```text
execute.dispatch:
  scheduler
  worker-contract
  human-wait
  runtime-state

execute.review:
  review-gate
  worker-contract
  runtime-state
```

機械可読contractに従えばreview時にschedulerやhuman-waitは不要ですが、`SKILL.md`だけを読むと余計なreferenceをロードします。

### 1.3 現在のword countは日本語contextを正確に表さない

現在のvalidatorは正規表現によるword countを使っています。

この実装では、連続した日本語文字列を少数の「word」と数える可能性があります。これはコードからの推論ですが、日本語中心のreferenceではtoken量を過小評価するリスクがあります。

### 1.4 resume briefの鮮度を判定できない

`build_resume_brief.py` はruntime rootからMarkdownを生成しますが、生成元のenvelope revision、runtime revision、event sequenceなどを成果物へ保持していません。

そのため、古いbriefを再利用しているかを機械的に判断できません。

---

## 2. 目標アーキテクチャ

```text
User request
    │
    ▼
SKILL.md
  trigger / immediate guard / global invariantだけ
    │
    ▼
deterministic operation resolver
  requested mode + durable state
    │
    ▼
context-contract.toml
  exact read-set + budget
    │
    ├── references/core.md
    │     全体state machine・責任・安全境界
    │
    └── operation-specific references
          現在のoperationに必要な詳細だけ
    │
    ▼
durable artifacts
  spec / ledger / packet / envelope / runtime / reports
    │
    ├── bounded worker packet
    ├── bounded review packet
    └── regenerable resume brief
```

重要なのは、**global procedureを失わないこと**です。

`core.md` にはライフサイクル全体、状態遷移、責任主体、gate、安全境界を残します。operation-specific referenceには、その時点で必要な詳細だけを置きます。

これは「ノードごとに別LLMへ細切れhandoffする」設計ではありません。同じcoordinatorが全体責任を持ち、外部状態の判定だけをdeterministic scriptへ寄せます。手順型タスクでは全体手順を保持した単一モデルが外部LLM orchestrationより一貫して良かった、という添付研究とも整合します。

---

# 3. スキル粒度の正式ルール

## 3.1 新しいuser-facing skillを作る条件

新規skillは、次の必須条件をすべて満たす場合だけ作ります。

| 条件                                  | 判定 |
| ----------------------------------- | -- |
| ユーザーが自然言語で独立して呼び分けられる               | 必須 |
| 独立した開始条件と完了条件を持つ                    | 必須 |
| 親skillのmutable stateなしで開始できる        | 必須 |
| 独立した成果物契約を持つ                        | 必須 |
| 他の2つ以上のworkflowから再利用される             | 加点 |
| 権限・安全境界が親skillと異なる                  | 加点 |
| skill分割後もhandoff量を含めcontextが30%以上減る | 加点 |

次に該当するものはskillにしません。

```text
- 同じloopの内部phase
- state machineの1状態
- 単に長いreference
- 単に大きいPython module
- schemaやvalidator
- worker packetの一種
- reviewやhuman waitのような内部制御
```

### 現在のloop判定

```text
grill-to-pr-loop:
  独立trigger      = yes
  独立成果物       = spec / issue ledger / execution packet
  独立完了条件     = Execution Plan Gateまたはdelivery
  execution state不要

issue-implementation-loop:
  独立trigger      = approved packet
  独立成果物       = commits / reports / PR_READY branches
  独立完了条件     = terminal states / PR_READY
  planning conversation不要
```

この2つは分ける価値があります。

一方、schedulerやreview gateは実装loopのmutable stateを共有するため、独立skillにはしません。

---

## 3.2 機械可読なfamily policy

追加ファイル:

```text
skill-architecture.toml
```

```toml
schema_version = 1

[[families]]
id = "repository-change-loop"
user_facing_skills = [
  "grill-to-pr-loop",
  "issue-implementation-loop",
]
max_user_facing_skills = 2

forbidden_standalone_skills = [
  "context-manager",
  "dependency-graph",
  "execution-envelope",
  "human-wait",
  "remote-delivery",
  "review-gate",
  "runtime-state",
  "scheduler",
  "worker-contract",
  "worktree-lifecycle",
]
```

既存validatorにも禁止skill名はありますが、現在はPythonコード内にハードコードされています。
V4ではpolicy fileを正本にします。

---

# 4. Context Contract V2

## 4.1 正本ルール

```text
context-contract.toml:
  operation → exact read-set の唯一の正本

SKILL.md:
  operation-specific filenameを列挙しない

references/workflow-contract.md:
  default read-setから外す
  移行期間だけdeprecated shimとして残す
```

`SKILL.md` は次だけを持ちます。

```text
- trigger
- immediate guard
- global responsibility
- operation resolverの使い方
- required invariants
- stop conditions
```

## 4.2 Contract例

```toml
schema_version = 2
skill = "issue-implementation-loop"
entrypoint = "SKILL.md"
base_references = ["references/core.md"]

max_file_count = 6
max_context_chars = 16000
max_estimated_tokens = 2400
minimum_headroom_percent = 15

[operations.prepare]
references = [
  "references/execution-envelope.md",
  "references/dependency-contract.md",
  "references/worktree-lifecycle.md",
]
max_file_count = 5

[operations."execute.dispatch"]
references = [
  "references/scheduler.md",
  "references/worker-contract.md",
  "references/runtime-state.md",
]
max_file_count = 5

[operations."execute.review"]
references = [
  "references/review-gate.md",
  "references/worker-contract.md",
  "references/runtime-state.md",
]
max_file_count = 5

[operations."execute.wait"]
references = [
  "references/human-wait.md",
  "references/runtime-state.md",
]
max_file_count = 4

[operations.resume]
references = [
  "references/runtime-state.md",
  "references/recovery.md",
]

[operations.status]
references = [
  "references/runtime-state.md",
  "references/scheduler.md",
]

[operations.deliver]
references = ["references/remote-delivery.md"]
```

### `execute.wait` を新設する理由

現在は `waiting_human` も `execute.dispatch` にroutingされます。

変更後:

```python
reviewable     -> execute.review
fixable        -> execute.dispatch
waiting_human  -> execute.wait
runnable       -> execute.dispatch
```

human wait中にworker-contractやscheduler全体を読む必要がなくなります。

---

## 4.3 `grill-to-pr-loop` operation

```text
intake
grill
spec
issue-gate
execution-plan
resume.local
resume.remote
completion-report.local
completion-report.remote
delivery
ambiguity-check
```

`resume` と `completion-report` をlocal / remoteで分けることで、「remote actionがあった場合だけremote-deliveryを追加する」という自然言語条件を消します。

現在はこの条件が`SKILL.md`にだけ存在し、contractには表現されていません。

### 基本read-set

```text
base:
  SKILL.md
  references/core.md

intake / grill / spec:
  planning-contract.md

issue-gate:
  planning-contract.md
  local-issue-ledger.md

execution-plan:
  planning-contract.md
  local-issue-ledger.md
  execution-handoff.md

resume.local:
  local-issue-ledger.md
  execution-handoff.md

resume.remote:
  local-issue-ledger.md
  execution-handoff.md
  remote-delivery.md

delivery:
  remote-delivery.md
```

`workflow-contract.md`をbaseから外すことで、現在のexecution-plan read-setからrouter 1ファイル分を削減できます。現在のテストはrouterを含む6ファイルを期待しています。

---

# 5. Context budgetの計測方法

## 5.1 word countは参考値へ降格

以下を計測します。

```text
character_count
non_whitespace_character_count
estimated_token_count
file_count
headroom_percent
```

推定tokenは外部dependencyなしで算出します。

```python
estimated_tokens =
    ceil(ascii_alphanumeric_chars / 4)
  + cjk_hiragana_katakana_hangul_chars
  + ceil(other_non_whitespace_chars / 2)
```

これはモデル固有tokenizerの正確な値ではありませんが、日本語を1wordとして扱うより安全です。

## 5.2 budget決定ルール

各operationの初期budgetは次で決めます。

```text
budget = 現在のestimated token数 × 1.20
```

100token単位で切り上げ、最低15%のheadroomを要求します。

```text
hard failure:
  actual > max_estimated_tokens
  actual chars > max_context_chars
  file_count > max_file_count
  headroom < 0

warning:
  headroom < 15%
  main比較でcontextが10%以上増加
```

## 5.3 Entrypoint目標

| ファイル                                 |      target | hard max |
| ------------------------------------ | ----------: | -------: |
| `grill-to-pr-loop/SKILL.md`          | 400 words以下 |      500 |
| `issue-implementation-loop/SKILL.md` | 350 words以下 |      420 |
| 各`references/core.md`                | 450 words以下 |      550 |
| agent default prompt                 |  24 words以下 |       32 |

現在はV3で `grill=551 words`, `issue=507 words` まで圧縮済みです。

---

# 6. Worker Packet V2

現在のpacketはpaths-first、最大8 path、default 450 words、hard 800 words、全文spec/ledger禁止まで実装されています。

V2では次を追加します。

```json
{
  "schema_version": 2,
  "packet_type": "issue_worker_dispatch",
  "task_kind": "implement",
  "access_mode": "read_write",
  "source_revision": {
    "envelope_revision": 3,
    "runtime_revision": 18,
    "issue_revision": 2
  },
  "read_paths": [
    {
      "path": "knowledge/wiki/syntheses/example-spec.md",
      "purpose": "Approved acceptance criteria"
    }
  ],
  "write_scope": [
    "path:skills/example/"
  ]
}
```

## 契約

| `task_kind` | `access_mode` | write_scope |
| ----------- | ------------- | ----------- |
| `implement` | `read_write`  | 必須          |
| `fix`       | `read_write`  | 必須          |
| `review`    | `read_only`   | 空配列         |
| `inspect`   | `read_only`   | 空配列         |

変更点:

```text
- read_paths.purposeを必須化
- path traversalを拒否
- worktree外のpathは明示許可rootだけ許可
- packetのrevisionとexecution envelopeを照合
- stale packetは実行前に拒否
- review workerも同じpacket familyで扱う
- reviewer専用の新skillは作らない
```

現在のvalidatorはpathを「空でない文字列」として確認していますが、root境界までは検証していません。

---

# 7. Resume Brief V2

出力:

```text
<runtime-root>/
├── resume-brief.md
└── resume-brief.meta.json
```

`resume-brief.meta.json`:

```json
{
  "schema_version": 2,
  "epic_id": "example-epic",
  "generated_at": "2026-06-25T18:00:00+09:00",
  "envelope_revision": 3,
  "runtime_revision": 18,
  "last_event_sequence": 91,
  "source_digest": "sha256:...",
  "word_count": 438,
  "max_words": 600
}
```

再開時:

```text
1. metaと現在のruntime/envelopeを比較
2. 一致すればresume-brief.mdを読む
3. 不一致ならbriefを再生成
4. canonical判断にはruntime-state.jsonとevents.jsonlを使う
```

brief本文は以下だけに限定します。

```text
- Epic ID
- status count
- active issue
- reviewable / runnable / waiting set
- unresolved human request
- next deterministic operation
- pending remote action
- residual risk
```

過去の全eventや全worker reportは埋め込みません。

---

# 8. Repository全体への適用

## Contract必須条件

次のいずれかを満たすskillは`context-contract.toml`必須とします。

```text
- operation / modeが2つ以上
- referencesが2ファイル以上
- SKILL.mdが400 wordsを超える
- workerやsub-workflowへcontextを渡す
```

### 適用対象

```text
必須:
  grill-to-pr-loop
  issue-implementation-loop
  llm-wiki

推奨:
  tailwindplus-elements

不要:
  python-setup-with-uv
  単一SKILL.mdで完結するatomic skill
```

`llm-wiki` はすでに「core + topology 1つ + mode 1つだけ読む」と明確にroutingしています。
これを機械可読contractへ移す価値があります。

---

# 9. ファイル構成

```text
skill-architecture.toml

scripts/
├── skill_context/
│   ├── __init__.py
│   ├── contract.py
│   ├── metrics.py
│   ├── inspection.py
│   └── validation.py
├── validate_skill_architecture.py
├── validate_skill_context.py
├── inspect_skill_context.py
├── report_skill_context.py
├── validate_loop_skill_context.py     # compatibility wrapper
└── inspect_loop_skill_context.py      # compatibility wrapper

skills/
├── grill-to-pr-loop/
│   ├── SKILL.md
│   ├── context-contract.toml
│   └── references/
│       ├── core.md
│       └── workflow-contract.md       # deprecated shim
├── issue-implementation-loop/
│   ├── SKILL.md
│   ├── context-contract.toml
│   ├── assets/schemas/
│   │   ├── worker-packet-v1.schema.json
│   │   └── worker-packet.schema.json
│   └── scripts/
│       ├── select_operation.py
│       ├── build_worker_packet.py
│       ├── validate_worker_packet.py
│       ├── build_resume_brief.py
│       └── validate_resume_brief.py
└── llm-wiki/
    └── context-contract.toml

.github/workflows/
└── skill-architecture.yml

knowledge/wiki/syntheses/
├── skill-repository-optimization-v4-spec.md
├── skill-repository-optimization-v4-issues.md
└── skill-repository-optimization-v4-input-packet.json
```

Durable設計文書を`knowledge/wiki/syntheses/`に置く方針は、repository routerとknowledge root contractにも一致します。

---

# 10. 実装Issue分解

## 依存関係

```text
SRO4-001
  ├─> SRO4-002 ─> SRO4-003 ─┐
  │                           ├─> SRO4-005 ─> SRO4-006
  └────────────> SRO4-004 ───┘
```

| ID       | 内容                                  | 主なwrite scope                                          |
| -------- | ----------------------------------- | ------------------------------------------------------ |
| SRO4-001 | 粒度policy・baseline・詳細spec            | `skill-architecture.toml`, `knowledge/wiki/syntheses/` |
| SRO4-002 | Context Contract V2と共通validator     | `scripts/skill_context/`, validator scripts            |
| SRO4-003 | 2 loop skillのsingle-source routing化 | 両`SKILL.md`, context contract, references              |
| SRO4-004 | Worker Packet V2 / Resume Brief V2  | issue loop schemas, scripts, tests                     |
| SRO4-005 | `llm-wiki`適用とCI追加                   | llm-wiki contract, `.github/workflows/`                |
| SRO4-006 | 統合検証、移行shim、wiki ledger更新           | tests, index, log, compatibility wrappers              |

## SRO4-001 Acceptance

```text
- 新規skill判定ルールが文書化されている
- repository-change-loop familyが機械可読
- user-facing loop skillが2つに固定される
- 現在の全operation context量がbaseline JSONに保存される
```

## SRO4-002 Acceptance

```text
- schema_version=1と2を読める
- chars / estimated tokens / filesを検証できる
- operationごとのbudget overrideを読める
- v1はwarning付きで互換維持
- Python 3.9で外部dependencyなし
```

## SRO4-003 Acceptance

```text
- SKILL.mdがoperation-specific reference名を列挙しない
- workflow-contract.mdがbase read-setから外れる
- execute.waitが追加される
- waiting_humanがexecute.waitへroutingされる
- global lifecycleとsafety invariantはcore.mdに残る
```

## SRO4-004 Acceptance

```text
- implement / fix / review / inspect packetを表現できる
- review packetはread-only
- stale revisionを拒否する
- read path purposeが必須
- resume brief freshnessを検証できる
- v1 packetは既存runのresume用に読める
```

## SRO4-005 Acceptance

```text
- llm-wikiのtopology × mode read-setが機械検証される
- PRごとにcontext reportが生成される
- budget超過でCIが失敗する
- context増加率がreportに出る
```

---

# 11. CI設計

```yaml
name: skill-architecture

on:
  pull_request:
  push:
    branches: [main]

jobs:
  validate:
    strategy:
      matrix:
        python-version: ["3.9", "3.12"]

    steps:
      - checkout
      - setup-python
      - run: python3 scripts/validate_skill_architecture.py --all
      - run: python3 scripts/validate_skill_context.py --all
      - run: python3 scripts/report_skill_context.py --all --json > skill-context-report.json
      - run: python3 -m unittest discover -s skills/grill-to-pr-loop/tests
      - run: python3 -m unittest discover -s skills/issue-implementation-loop/tests
      - run: git diff --check
```

CI failure条件:

```text
- forbidden standalone skill追加
- missing / duplicate reference
- entrypointにoperation mappingを重複記述
- context budget超過
- max file count超過
- packet / resume schema不整合
- v1 compatibility破壊
```

---

# 12. 移行方針

```text
Step 1:
  V1 contractを読み続ける
  V2を新規defaultにする

Step 2:
  workflow-contract.mdをdeprecated shimにする
  base read-setからのみ外す

Step 3:
  SKILL.mdのmanual reference mapを削除

Step 4:
  worker packet builderはV2を生成
  validatorはV1/V2両方を読む

Step 5:
  古いresume briefは最初のresume時に再生成

Step 6:
  1回の安定運用後にV1生成とworkflow shimを削除
```

---

# 13. Stop Conditions

以下が発生した場合は実装を止めます。

```text
- context削減によりglobal lifecycleを読めなくなる
- safety / approval / remote boundaryがSKILLとcoreの両方から消える
- worker packetからacceptance criteriaまたはstop conditionが欠落する
- operation selectionに追加LLM routerが必要になる
- schedulerやruntime semanticsを変更しないと実装できない
- v1 artifactのresumeが不可能になる
- context削減後にworker/reviewerの再質問や誤実装が増える
```

## 到達状態

```text
粒度:
  user-facing loop skillは2つ
  内部機構はreference / artifact / script / lib

context:
  global procedure skeletonは常時保持
  operation詳細は必要時だけ読む
  worker packetはpaths-first
  resumeはfreshness検証済みbriefから開始

品質保証:
  read-setはcontext-contractだけが正本
  budgetは文字数＋推定tokenで計測
  context regressionはCIで検出
```

実装開始点は **SRO4-001: 粒度policy・現状baseline・V4 specの正本化** です。
