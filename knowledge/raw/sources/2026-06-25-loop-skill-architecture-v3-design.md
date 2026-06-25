# ループ系スキル最適化・詳細設計

設計正本の推奨保存先は次です。

```text
knowledge/wiki/syntheses/loop-skill-architecture-v3-spec.md
```

このリポジトリでは、長い仕様や実装契約は `knowledge/wiki/syntheses/` に置き、実行プロンプトは参照先だけを持つ方針になっています。

## 1. 設計判断

ユーザーが直接呼ぶループ系スキルは、次の2つだけに固定します。

```text
grill-to-pr-loop
  設計対話
  → durable spec
  → Issue分解
  → Execution Packet
  → 実装へのhandoff
  → optional delivery coordination

issue-implementation-loop
  approved Execution Packet
  → Execution Envelope
  → Issue実装
  → 検証
  → Issue review/fix
  → PR_READY
  → optional remote delivery
```

次は独立スキルにしません。

```text
scheduler
execution-envelope
dependency-graph
runtime-state
worktree-lifecycle
review-gate
human-wait
remote-delivery
worker-contract
context-manager
```

これらは `issue-implementation-loop` 内の reference、schema、script、内部Python moduleとして実装します。

現在のリポジトリも、ユーザー向けスキルを2つに留め、schedulerやworktree管理を独立スキルにしない方針を採用しています。 添付論文が示す「手順型タスクでは外部LLMルーティングが文脈断絶と失敗点を増やす」という結果にも合致します。

## 2. スキルを分割する判定基準

今後、新しいuser-facing skillを追加するのは、次の条件をすべて満たす場合だけです。

| 条件          | 判定内容                          |
| ----------- | ----------------------------- |
| 独立起動        | 親スキルなしでユーザーから直接呼べる            |
| 独立完了        | 固有の完了条件を持つ                    |
| 安定I/O       | 入力・出力契約が独立している                |
| 再利用性        | 複数workflowから単独利用される           |
| discovery価値 | 独自のdescriptionによる発見が必要        |
| 文脈所有        | 独立したglobal contextを保持する合理性がある |

1つでも満たさない場合は、原則として以下にします。

```text
手順・判断ルール    → references/
状態形式            → assets/schemas/
初期値              → assets/templates/
検証・計算          → scripts/
Python内部責務      → scripts/lib/
長期設計・判断記録  → knowledge/wiki/syntheses/
```

## 3. 最終ディレクトリ構成

```text
scripts/
├── validate_loop_skill_context.py
└── inspect_loop_skill_context.py

skills/
├── grill-to-pr-loop/
│   ├── SKILL.md
│   ├── context-contract.toml
│   ├── agents/
│   │   └── openai.yaml
│   ├── references/
│   │   ├── core.md
│   │   ├── planning-contract.md
│   │   ├── local-issue-ledger.md
│   │   ├── execution-handoff.md
│   │   ├── delivery-coordination.md
│   │   ├── common-mistakes.md
│   │   └── workflow-contract.md        # 移行用の薄い互換shim
│   ├── scripts/
│   │   └── check_prereqs.py
│   └── tests/
│       ├── fixtures.py
│       ├── test_entrypoint_contract.py
│       ├── test_context_contract.py
│       ├── test_reference_ownership.py
│       └── test_prereqs.py
│
└── issue-implementation-loop/
    ├── SKILL.md
    ├── context-contract.toml
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
    │   │   ├── worker-packet.schema.json       # 追加
    │   │   ├── worker-report.schema.json
    │   │   └── execution-result.schema.json
    │   └── templates/
    │       ├── execution-envelope.json
    │       ├── worker-packet.json               # 追加
    │       ├── resume-brief.md                   # 追加
    │       └── execution-result.json
    ├── scripts/
    │   ├── _common.py                           # 一時的な互換re-export
    │   ├── select_operation.py                  # 追加
    │   ├── build_worker_packet.py               # 追加
    │   ├── build_resume_brief.py                # 追加
    │   ├── validate_worker_packet.py            # 追加
    │   ├── validate_input_packet.py
    │   ├── validate_execution_envelope.py
    │   ├── validate_runtime_state.py
    │   ├── validate_worker_report.py
    │   ├── validate_delivery_plan.py
    │   ├── compute_next_actions.py
    │   ├── rebuild_runtime_state.py
    │   ├── reconcile_git_state.py
    │   ├── check_capabilities.py
    │   └── lib/
    │       ├── __init__.py
    │       ├── contracts.py
    │       ├── validation.py
    │       ├── dependency_graph.py
    │       ├── scheduler.py
    │       ├── runtime.py
    │       ├── delivery.py
    │       ├── git_state.py
    │       ├── skill_discovery.py
    │       └── context.py
    └── tests/
        ├── fixtures.py
        ├── test_entrypoint_contract.py
        ├── test_context_contract.py
        ├── test_input_validation.py
        ├── test_envelope_validation.py
        ├── test_runtime_validation.py
        ├── test_worker_packet.py
        ├── test_worker_report.py
        ├── test_dependency_graph.py
        ├── test_scheduler.py
        ├── test_delivery.py
        ├── test_git_state.py
        ├── test_skill_discovery.py
        ├── test_resume_brief.py
        └── test_pressure_scenarios.py
```

## 4. コンテキストの3層モデル

ループ実行中の情報を、次の3層に分けます。

### Hot context

現在の判断に必ず必要な情報です。

```text
SKILL.md
context-contract.toml
references/core.md
現在のoperationに対応するreferences
短いruntime summary / resume brief
```

目標は、通常operationで合計3,000 words以下です。

### Warm context

必要になった時だけファイルから読みます。

```text
input packet
execution envelope
runtime state
現在のIssue brief
直近worker report
直近review report
local issue ledger
```

会話本文へ全文を貼りません。パスと短い要約を渡します。

### Cold context

原則としてコンテキストへ投入しません。

```text
full spec
full ADR
full glossary
full event log
過去の全worker report
無関係なIssue
無関係なsource code
過去の会話履歴
```

必要な部分だけ、durable pathから再読します。

現在もworker packetはpaths-firstとし、spec、ledger、ADR、glossaryの全文を貼らない契約になっています。

## 5. `context-contract.toml`

read setとbudgetを機械可読な1ファイルに集約します。

`SKILL.md` と複数referenceに同じrouting表を重複させません。

### `grill-to-pr-loop/context-contract.toml`

```toml
schema_version = 1
skill = "grill-to-pr-loop"
entrypoint = "SKILL.md"
base_references = ["references/core.md"]
max_reference_depth = 1

[budgets]
description_max_words = 28
default_prompt_max_words = 32
entrypoint_target_words = 600
entrypoint_max_words = 850
base_reference_max_words = 600

[operations.plan]
references = ["references/planning-contract.md"]
max_loaded_words = 2200
max_reference_files = 2

[operations.issues]
references = [
  "references/planning-contract.md",
  "references/local-issue-ledger.md",
]
max_loaded_words = 2800
max_reference_files = 3

[operations.handoff]
references = [
  "references/local-issue-ledger.md",
  "references/execution-handoff.md",
]
max_loaded_words = 3000
max_reference_files = 3

[operations.delivery]
references = [
  "references/local-issue-ledger.md",
  "references/delivery-coordination.md",
]
max_loaded_words = 2400
max_reference_files = 3

[operations.complete]
references = ["references/local-issue-ledger.md"]
max_loaded_words = 1800
max_reference_files = 2
```

### `issue-implementation-loop/context-contract.toml`

```toml
schema_version = 1
skill = "issue-implementation-loop"
entrypoint = "SKILL.md"
base_references = ["references/core.md"]
max_reference_depth = 1

[budgets]
description_max_words = 24
default_prompt_max_words = 32
entrypoint_target_words = 400
entrypoint_max_words = 520
base_reference_max_words = 600

[operations."prepare.envelope"]
references = [
  "references/execution-envelope.md",
  "references/dependency-contract.md",
]
max_loaded_words = 2800
max_reference_files = 3

[operations."prepare.reserve"]
references = ["references/worktree-lifecycle.md"]
max_loaded_words = 2200
max_reference_files = 2

[operations."execute.dispatch"]
references = [
  "references/scheduler.md",
  "references/worker-contract.md",
  "references/runtime-state.md",
]
max_loaded_words = 3000
max_reference_files = 4

[operations."execute.review"]
references = [
  "references/review-gate.md",
  "references/worker-contract.md",
  "references/runtime-state.md",
]
max_loaded_words = 3200
max_reference_files = 4

[operations."execute.fix"]
references = [
  "references/review-gate.md",
  "references/worker-contract.md",
]
max_loaded_words = 2800
max_reference_files = 3

[operations."execute.wait"]
references = [
  "references/human-wait.md",
  "references/runtime-state.md",
]
max_loaded_words = 2400
max_reference_files = 3

[operations."resume.reconcile"]
references = [
  "references/runtime-state.md",
  "references/recovery.md",
  "references/worktree-lifecycle.md",
]
max_loaded_words = 3200
max_reference_files = 4

[operations."status.snapshot"]
references = [
  "references/runtime-state.md",
  "references/scheduler.md",
]
max_loaded_words = 2400
max_reference_files = 3

[operations."deliver.issue-pr"]
references = ["references/remote-delivery.md"]
max_loaded_words = 2200
max_reference_files = 2

[operations."deliver.final-pr"]
references = [
  "references/remote-delivery.md",
  "references/runtime-state.md",
]
max_loaded_words = 2600
max_reference_files = 3
```

### 読み込み規則

`SKILL.md` には次だけを書きます。

```text
1. context-contract.toml を読む。
2. 現在のoperationを1つ選択する。
3. base_referencesと、そのoperationのreferencesだけを読む。
4. 複数operationのread setを無条件にunionしない。
5. 必要なspec、ledger、reportは本文ではなくdurable pathから読む。
```

referenceから別referenceを必須読込させることは禁止します。

```text
SKILL.md
  ↓
context-contract.toml
  ↓
base + operation references
```

必須referenceの深さは常に1です。

## 6. `core.md` が保持するグローバル文脈

referenceを分割しすぎると、モデルが現在ノードだけを見る問題が起きます。

それを防ぐため、各スキルの `core.md` は必ず読みます。

### `grill-to-pr-loop/references/core.md`

600 words以下で次を保持します。

```text
- workflow全体のライフサイクル
- planningとimplementationの責任境界
- durable artifactを正本とする原則
- Spec Gate / Issue Gate / Execution Plan Gate
- local-first原則
- remote write承認境界
- final responsibility
- operation選択原則
```

### `issue-implementation-loop/references/core.md`

現行の責任境界を維持します。

```text
- approved issueだけを実装する
- coordinatorがglobal stateを保持する
- coordinator自身は実装workerにならない
- workerはIssue単位のwrite scopeだけを持つ
- runtime stateはtracked issue branchへ置かない
- review済みcommit rangeを成功条件とする
- external writeはapproved policyが必要
- final PR mergeはhuman-only
```

現行 `core.md` でも、coordinator、worker、reviewerの所有境界と、generic orchestration frameworkを作らない方針が定義されています。

## 7. operation選択

`issue-implementation-loop` のoperationは、LLMの自由分類ではなく、構造化状態から決定します。

### `select_operation.py`

入力:

```bash
python3 skills/issue-implementation-loop/scripts/select_operation.py \
  --envelope <execution-envelope.json> \
  --runtime <runtime-state.json> \
  --requested-mode execute \
  --json
```

出力:

```json
{
  "operation": "execute.review",
  "reason": "reviewable issues exist",
  "issues": ["G2PR-003"],
  "read_set": [
    "SKILL.md",
    "context-contract.toml",
    "references/core.md",
    "references/review-gate.md",
    "references/worker-contract.md",
    "references/runtime-state.md"
  ],
  "estimated_words": 2140,
  "budget_words": 3200,
  "within_budget": true
}
```

### 判定優先順位

```text
1. 明示された status / deliver 要求
2. envelope未作成             → prepare.envelope
3. reservation未確定          → prepare.reserve
4. state/git不整合             → resume.reconcile
5. reviewable Issueあり        → execute.review
6. fixable Issueあり           → execute.fix
7. pending human requestあり   → execute.wait
8. runnable Issueあり          → execute.dispatch
9. 全Issue terminal            → status.snapshot
10. それ以外                   → resume.reconcile
```

これにより、mode routingのための追加LLM呼び出しは発生しません。

## 8. worker packetの正規化

現状のExecution Envelopeには、既に次のcontext policyがあります。

```json
{
  "paths_first": true,
  "max_worker_packet_words": 450,
  "max_worker_report_words": 350,
  "include_full_spec_text": false,
  "include_full_ledger_text": false
}
```

これを実際に強制するbuilderとschemaを追加します。

### `worker-packet.schema.json`

```json
{
  "schema_version": 1,
  "epic_id": "lower-kebab-case",
  "issue_id": "G2PR-001",
  "dispatch_id": "dispatch-001",
  "branch": "codex/<epic>/<issue>-<slug>",
  "worktree": "/absolute/path",
  "write_scope": ["path:skills/example"],
  "read_paths": [
    {
      "path": "knowledge/wiki/syntheses/spec.md",
      "purpose": "approved specification",
      "required": true
    }
  ],
  "required_behavior_summary": [],
  "acceptance_criteria": [],
  "verification": [],
  "stop_conditions": [],
  "report_path": "/absolute/path/report.json"
}
```

### 制約

```text
default packet: 450 words以下
hard limit:     800 words
read_paths:     8件以下
inline excerpt: 1ファイル120 words以下
inline合計:     300 words以下
full spec:      禁止
full ledger:    禁止
silent truncate:禁止
```

超過時は自動で切り落としません。

```text
PACKET_CONTEXT_BUDGET_EXCEEDED
```

として失敗させ、要約を短くするか、本文をartifactへ移します。

## 9. resume用コンテキスト

長時間実行後の再開で、会話履歴や全event logを読み直さないようにします。

### runtime構成

```text
<runtime-root>/
├── execution-envelope.json
├── runtime-state.json
├── events.jsonl
├── context/
│   ├── run-index.json
│   ├── resume-brief.md
│   └── issue-briefs/
│       ├── G2PR-001.md
│       └── G2PR-002.md
├── worker-reports/
├── review-reports/
└── execution-result.json
```

### `resume-brief.md`

600 words以下の派生artifactです。

```text
- Epic ID / envelope revision
- current overall status
- runnable
- active
- reviewable
- fixable
- waiting human
- pending remote action
- last verified commit ranges
- latest reportsへのpath
- recommended next operation
```

`resume-brief.md` は正本ではありません。

```text
execution-envelope
runtime-state
events.jsonl
```

からいつでも再生成できるcacheとして扱います。

`resume` は最初にbriefを読み、不整合がある場合だけevent logとgit stateを詳しく調べます。

## 10. referenceの所有境界

重複を防ぐため、ルールの正本を固定します。

| 契約                        | 正本                                                                  |
| ------------------------- | ------------------------------------------------------------------- |
| 全体ライフサイクル                 | 各スキルの `core.md`                                                     |
| planning artifact         | `grill-to-pr-loop/planning-contract.md`                             |
| local Issue ledger        | `grill-to-pr-loop/local-issue-ledger.md`                            |
| Execution Packet schema   | `issue-implementation-loop/assets/schemas/input-packet.schema.json` |
| handoff手順                 | `grill-to-pr-loop/execution-handoff.md`                             |
| branch/base/worktree      | `issue-implementation-loop/worktree-lifecycle.md`                   |
| dependency edge           | `issue-implementation-loop/dependency-contract.md`                  |
| runnable計算                | `issue-implementation-loop/scheduler.md`                            |
| worker packet/report      | `issue-implementation-loop/worker-contract.md`                      |
| implementation review     | `issue-implementation-loop/review-gate.md`                          |
| runtime / recovery        | `runtime-state.md`, `recovery.md`                                   |
| remote delivery mechanics | `issue-implementation-loop/remote-delivery.md`                      |
| GitHub mirrorとledger同期    | `grill-to-pr-loop/delivery-coordination.md`                         |

現在の `grill-to-pr-loop/execution-handoff.md` はbranch、base、commit、review cycleまで詳しく定義しています。 最適化後は、これらを `issue-implementation-loop` 側の正本へ移し、handoff側には次だけ残します。

```text
- packet path
- validation command
- approval gate
- selected delivery intent
- issue-implementation-loopの参照先
```

## 11. `SKILL.md` とdefault prompt

### `grill-to-pr-loop`

`SKILL.md` は目標600 words、上限850 wordsです。

残す内容:

```text
- Overview
- Immediate Guard
- responsibility boundary
- context-contract.tomlを読む指示
- operation概要
- approval stop conditions
- completion report
```

削る内容:

```text
- branch/base詳細
- packet field一覧
- remote delivery詳細
- local ledger詳細
- subskillの詳細手順
- schemaと同じ説明
```

### `issue-implementation-loop`

現在の520 words上限を維持します。現行entrypointもmode routerとして「必要なreferenceだけ読む」構造です。

### `agents/openai.yaml`

default promptにはbranch policyやreview policyを入れません。

```yaml
# grill-to-pr-loop
interface:
  display_name: "Grill to PR Loop"
  short_description: "設計から承認済み実行契約まで"
  default_prompt: "Use $grill-to-pr-loop for a repository change requiring approved design, issue decomposition, execution handoff, and optional delivery."

# issue-implementation-loop
interface:
  display_name: "Issue Implementation Loop"
  short_description: "承認済みIssueの実装ループ"
  default_prompt: "Use $issue-implementation-loop to execute an approved issue packet under its durable execution contract."
```

## 12. `_common.py` の内部分割

現在の `_common.py` には、JSON I/O、識別子、複数validation、dependency graph、scheduler、delivery、git、skill discoveryが同居しています。

次のように分離します。

| module                | 責務                                                |
| --------------------- | ------------------------------------------------- |
| `contracts.py`        | constants、regex、JSON I/O、primitive checks         |
| `validation.py`       | input、envelope、runtime、worker、delivery validation |
| `dependency_graph.py` | cycle、descendants、dependency release              |
| `scheduler.py`        | scope conflict、human block、next actions           |
| `runtime.py`          | issue record、event fold、resume brief              |
| `delivery.py`         | issue/final PR plan validation                    |
| `git_state.py`        | git command、branch/worktree reconcile             |
| `skill_discovery.py`  | repo-local優先のskill探索                              |
| `context.py`          | context-contract読込、budget計測、operation read set    |

CLIスクリプトは100 lines以下の薄いadapterにします。

```python
from lib.validation import validate_input_packet
from lib.contracts import load_json
```

`_common.py` は移行期間中のみre-exportします。

```python
from lib.contracts import *
from lib.validation import *
from lib.dependency_graph import *
from lib.scheduler import *
from lib.runtime import *
from lib.delivery import *
from lib.git_state import *
from lib.skill_discovery import *
from lib.context import *
```

目標は40 lines以下です。外部利用がないことを確認後に削除します。

## 13. context validator

### `validate_loop_skill_context.py`

```bash
python3 scripts/validate_loop_skill_context.py --all
python3 scripts/validate_loop_skill_context.py \
  --skill skills/issue-implementation-loop
```

検証内容:

```text
- context-contract.tomlがvalid TOML
- skill名とdirectory名が一致
- entrypointが存在
- description word budget
- default_prompt word budget
- SKILL.md word budget
- base reference budget
- operationごとの合計word budget
- operationごとの最大file数
- 未存在reference
- 未到達reference
- reference depth > 1
- 同じreferenceの重複登録
- routerとcontext-contractの矛盾
- full spec / ledgerをdefaultで許可していない
- forbidden standalone skill名
```

word数は実際にモデルが読む全文を数えます。

```text
operation_words =
  SKILL.md
  + context-contract.toml
  + base references
  + operation references
```

コードブロックも除外しません。

budgetを超えた場合、CIを失敗させます。

### inspection

```bash
python3 scripts/inspect_loop_skill_context.py \
  --skill skills/issue-implementation-loop \
  --operation execute.review \
  --json
```

出力:

```json
{
  "skill": "issue-implementation-loop",
  "operation": "execute.review",
  "files": [],
  "words": 2140,
  "max_words": 3200,
  "headroom_words": 1060
}
```

## 14. テスト分割

現状の大きな単一test fileは、機能単位へ分けます。既存specでも、テストが1ファイルへ集中している点が課題として記録されています。

分割原則:

```text
1 test file = 1 contract area
通常400 lines以下
共有fixtureはfixtures.py
pressure scenarioだけ統合testに残す
CLI testとpure function testを分ける
```

特に次を回帰テストにします。

```text
- repo-local skillがglobal installed copyより優先される
- context budget超過が失敗する
- operationから必要referenceだけが解決される
- standalone scheduler skillを追加していない
- worker packetがfull specを拒否する
- packet/report word budgetを超過できない
- resume briefが600 wordsを超えない
- remote delivery referenceが通常executeで読まれない
- planning referenceがIssue実装時に読まれない
- scheduler/refactor前後でnext actionsが同一
```

## 15. 実装スライス

### LSO-001: Context contract導入

```text
変更:
- 2つのcontext-contract.toml
- validate_loop_skill_context.py
- inspect_loop_skill_context.py
- context contract tests

完了条件:
- 現行read setを表現できる
- budgetがCIで検証される
- 実行挙動は変えない
```

### LSO-002: Entrypointとreference ownership整理

```text
変更:
- grill SKILL.md短縮
- default prompt短縮
- core.md追加
- execution-handoff薄型化
- delivery-coordinationへ改名
- workflow-contractを互換shim化

依存:
- LSO-001
```

### LSO-003: Worker packetとresume brief

```text
変更:
- worker-packet schema/template
- build/validate worker packet
- resume brief template/builder
- context_policy拡張

依存:
- LSO-001
```

### LSO-004: `_common.py` 分割

```text
変更:
- scripts/lib/*
- thin CLI adapters
- temporary _common re-export
- behavior parity tests

制約:
- scheduler semanticsを変更しない
- schema versionを変更しない
```

### LSO-005: テスト分割とCI統合

```text
変更:
- 単一test file分割
- context validationを通常CIへ追加
- existing pressure scenarios維持

依存:
- LSO-001〜004
```

## 16. 完了条件

最終的な受け入れ条件は次です。

```text
- user-facing loop skillは2つだけ
- issue-implementation-loop/SKILL.mdは520 words以下
- grill-to-pr-loop/SKILL.mdは850 words以下
- default_promptは各32 words以下
- 全operationがcontext budget内
- mandatory reference depthは1
- 未到達referenceがない
- worker packetはdefault 450 words以下
- worker reportはdefault 350 words以下
- resume briefは600 words以下
- full spec / ledgerをworker promptへ貼らない
- operation selectionに追加LLM routerを使わない
- scheduler / runtime / deliveryの挙動がrefactor前後で同一
- `_common.py` は互換re-exportだけ
- 既存CLI名と引数は維持
- 既存schema version 1との互換性を維持
- remote write / final merge policyを弱めない
```

検証コマンド:

```bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache \
python3 scripts/validate_loop_skill_context.py --all

PYTHONPYCACHEPREFIX=/tmp/skills-pycache \
python3 -m unittest discover -s skills/grill-to-pr-loop/tests

PYTHONPYCACHEPREFIX=/tmp/skills-pycache \
python3 -m unittest discover -s skills/issue-implementation-loop/tests

PYTHONPYCACHEPREFIX=/tmp/skills-pycache \
python3 skills/grill-to-pr-loop/scripts/check_prereqs.py \
  --phase execution \
  --json

PYTHONPYCACHEPREFIX=/tmp/skills-pycache \
python3 skills/issue-implementation-loop/scripts/check_capabilities.py \
  --json

PYTHONPYCACHEPREFIX=/tmp/skills-pycache \
python3 skills/issue-implementation-loop/scripts/validate_input_packet.py \
  knowledge/wiki/syntheses/loop-skill-context-optimization-input-packet.json

git diff --check
```

## 17. 停止条件

実装中に次の状態になった場合は、そのスライスを止めます。

```text
- budget削減のためにapproval / safety ruleが消える
- referenceを分けただけで、実際には全reference読込が必要になる
- context-contractとSKILL.mdが二重のsource of truthになる
- `_common.py` 分割でscheduler出力が変わる
- schema version 1の既存artifactを読めなくなる
- worker packetの短縮でacceptance criteriaが欠落する
- resume briefがcanonical stateとして扱われる
- repo-local skill discoveryの優先順位が下がる
- 新しい外部Python dependencyが必要になる
- remote writeまたは破壊的操作が必要になる
```

最終形は、**2つの大きな責任単位だけをskillとして公開し、global invariantsは常時in-context、局所手順はoperation単位でon-demand、状態と証跡はdurable artifactへ退避する構成**です。これにより、手順の全体像を失わず、通常ターンのコンテキスト量だけを抑えられます。
