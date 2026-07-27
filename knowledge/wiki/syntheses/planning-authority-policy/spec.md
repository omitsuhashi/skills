# Planning Authority Policy 仕様

## 問題設定 / 成功条件

`grill-to-pr-loop` は planning と implementation を分離しているが、planning 中に supporting agent を使う場合の権限境界は機械可読な family policy として固定されていない。Codex はメインコンテキストと subagent で異なる model / reasoning 設定を選べるため、model routing を repository 契約へ持ち込むと、Codex / Hermes 共通 skill が一時的な host 設定へ依存する。一方、権限境界を明示しないまま delegation すると、supporting agent が spec 統合、scope 変更、approval candidate 確定を事実上所有する余地が残る。

成功条件は次のとおり。

- planning の統合責任を `main_planning_context` に固定する。
- supporting agent の権限を `advisory_only`、planning artifact への access を `read_only` とする。
- Spec Gate / Issue Gate の最終 decision authority を Human に残す。
- model / reasoning の選択を host runtime に任せ、repository artifact へ永続化しない。
- `issue-implementation-loop` の worker-only 契約、Execution Envelope、Worker Packet、scheduler を変更しない。
- Codex / Hermes の dual-host authoring 契約を維持する。

## Epic ID

`planning-authority-policy`

## 用語

- `main_planning_context`: 現在の planning authority を所有し、設計判断、spec、Issue 台帳、Input Packet、Human gate への approval candidate を統合する primary context。
- `supporting_planning_agent`: codebase 探索、一次情報調査、設計批評、criteria gap 確認を行い、根拠付き advisory result を返す read-only agent。
- `planning authority`: planning artifact の canonical 内容を統合し、Human gate へ提示する approval candidate を確定する権限。Human の decision authority は含まない。
- `host_runtime`: Codex の選択画面、Hermes profile、または各 host の runtime 設定。model / reasoning の具体値を所有する。
- `ownership transfer`: context compaction または fresh context 移行時に、durable artifact と bounded brief を使って `main_planning_context` の役割を新しい primary context へ明示的に移すこと。supporting agent への delegation とは区別する。

## 採用した判断

### Machine-readable family policy

`skill-architecture.toml` に次の小さな interface を追加する。

```toml
[families.repository-change-loop.planning_authority]
integration_owner = "main_planning_context"
supporting_agent_authority = "advisory_only"
decision_authority = "human"
model_selection = "host_runtime"
model_persistence = "forbidden"
```

この interface は権限と ownership だけを表す。model name、reasoning level、intelligence level、host 固有の agent ID は表さない。

### Human-readable planning contract

`grill-to-pr-loop` の entrypoint と planning contract は次を要求する。

- `main_planning_context` が spec、Issue 台帳、Input Packet、approval candidate を統合する。
- `supporting_planning_agent` は単一の問い、bounded read paths、停止条件を受け取り、根拠・findings・disagreements・uncertainties・recommendation を返す。
- supporting agent は canonical planning artifact を編集せず、scope 変更、Human approval、packet seal を行わない。
- supporting agent の出力は advisory であり、多数決で planning decision を決めない。
- main context は conflicting evidence を解決し、解決できない authority-bearing ambiguity を Human gate へ提示する。

### Model selection

- planning に使う model / reasoning は host runtime で選ぶ。Codex ではメインコンテキストに対して選択画面の設定を使う。
- supporting agent、execution coordinator、worker、reviewer の model routing は host に任せる。
- model が利用できない、model 名が変わる、user が途中で設定を変える、という事象は spec / packet drift と扱わない。
- `model`、`model_name`、`model_reasoning_effort`、`reasoning_level`、`intelligence_level` を durable planning / execution artifact に追加しない。

## 責任フロー

```text
host runtime でメイン model / reasoning を選ぶ
        ↓
main_planning_context
  - intake / Grill with Docs
  - 設計判断の統合
  - spec / Issue 台帳 / Input Packet の作成
  - approval candidate の確定
        │
        ├─ supporting_planning_agent: codebase 探索
        ├─ supporting_planning_agent: 一次情報調査
        └─ supporting_planning_agent: 設計批評
             - advisory_only
             - read_only
             - model routing は host に委譲
        ↓
Human Spec Gate / Issue Gate
        ↓
fresh または compacted execution coordinator
        ├─ worker
        └─ reviewer
             - model routing は host に委譲
        ↓
Human final merge decision
```

## 失敗時の扱い

- supporting agent が canonical planning artifact を編集した場合、その変更を authority-bearing update として採用しない。main context が根拠を再確認し、必要な内容だけを自ら反映する。
- advisory result に根拠がない場合、不完全な result として planning decision に使用しない。
- agent 間の意見が衝突した場合、多数決にせず、main context が evidence を比較する。approved scope に影響する未解決点は Human gate へ送る。
- supporting agent が scope 変更を提案した場合、自動反映しない。main context が spec change として扱い、承認後の spec byte を変えるなら新しい Spec Gate を要求する。
- host が特定 model / reasoning level を提供しない場合、repository validation failure にしない。host が利用可能な routing を選ぶ。
- planning context が context pressure threshold に達した場合、既存の compaction policyを使う。fresh context へ移る場合は明示的な ownership transfer とし、supporting agent dispatch と混同しない。
- user が host runtime の model / reasoning 設定を変えても、spec binding、approval evidence、Input Packet、Execution Envelope の revision を変更しない。

## 変更対象

- `skill-architecture.toml`
- `scripts/validate_skill_architecture.py`
- `scripts/test_validate_skill_architecture.py`
- `skills/grill-to-pr-loop/SKILL.md`
- `skills/grill-to-pr-loop/references/planning-contract.md`
- `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py`
- `knowledge/wiki/syntheses/planning-authority-policy/`
- `knowledge/index.md`
- `knowledge/log.md`

## 変更しない対象

- `.codex/config.toml`
- `.codex/agents/*.toml`
- `skills/grill-to-pr-loop/context-contract.toml`
- Input Packet schema / template / validator
- Execution Envelope schema / template / validator
- Worker Packet schema / template / validator
- `issue-implementation-loop` scheduler / runtime / worker lifecycle
- Codex / Hermes 固有の model 名や reasoning level

## 非目標

- すべての subagent を同一 model / reasoning へ固定しない。
- model availability、price、latency、quality tier を repository で管理しない。
- host runtime の実効 model を repository validator から検査しない。
- supporting agent に planning authority または Human decision authority を与えない。
- planning context を implementation worker にしない。
- 新しい standalone skill、scheduler、model router、provider adapter を追加しない。
- historical spec、Input Packet、Execution Envelope を書き換えない。
- GitHub issue、push、PR、merge、release、live install を実行しない。

## Issue 分解方針

実装時は次の serial dependency で分解する。

1. family policy と architecture validator を test-first で追加する。
2. `grill-to-pr-loop` entrypoint / planning contract と docs test を policy に同期する。
3. model persistence forbidden invariant と existing execution contract non-regression を検証する。
4. wiki、index、log、full verification evidence を同期する。

`issue-implementation-loop` の production implementation は変更しない。

## 受け入れ条件

- `skill-architecture.toml` が `planning_authority` の5項目を正本として持つ。
- architecture validator が5項目の欠落、未知値、未定義field、table 欠落を拒否する。
- `grill-to-pr-loop/SKILL.md` が planning integration owner、supporting agent authority、Human decision authorityを短い required rule として示す。
- `planning-contract.md` が advisory/read-only dispatch、evidence return、conflict handling、ownership transfer を説明する。
- supporting agent が canonical planning artifact、scope approval、packet seal を所有しない。
- durable planning / execution artifact が model / reasoning field を新たに受け入れない。
- `issue-implementation-loop` の worker-only、fresh / compacted coordinator、main planning session non-implementation 契約が不変である。
- model unavailable または user-selected model change が repository drift / gate reset を起こさない。
- scoped dual-host validation と対象 skill validator が成功する。
- repository の relevant regression suites と `git diff --check` が成功する。

## 検証方針 / コマンド

```bash
python3 -m unittest discover -s scripts -p "test_validate_skill_architecture.py"
python3 -m unittest discover -s skills/grill-to-pr-loop/tests
python3 -m unittest discover -s skills/issue-implementation-loop/tests
python3 -m unittest discover -s scripts
python3 scripts/validate_skill_architecture.py --all
python3 scripts/validate_skill_context.py --all
python3 scripts/report_skill_context.py --all --json
python3 scripts/validate_dual_host_compatibility.py --skill skills/grill-to-pr-loop
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
git diff --check
```

追加する focused regression は、少なくとも次を含む。

- `planning_authority` table 欠落を拒否する。
- 5項目の各不正値を拒否する。
- `planning_authority` の未定義fieldを拒否する。
- supporting agent が `advisory_only` / `read_only` である。
- Human が decision authority である。
- model selection が `host_runtime`、persistence が `forbidden` である。
- Input Packet、Execution Envelope、Worker Packet の既存 closed schema が model / reasoning field を受け入れない。

## リモート書き込み方針

`local_only`。GitHub issue mirror、push、PR 作成、ready-for-review、merge、release、live install、その他の外部書き込みは承認対象外とする。

## 人間レビューゲート

- Spec Gate は本specのexact path、raw-byte SHA-256、採用した判断、非目標、受け入れ条件、検証方針、remote policy、停止条件を対象にHumanが判断する。
- Issue Gate はlocal-first Issue台帳、依存順、write scope、acceptance criteriaを対象にHumanが判断する。
- Execution Plan Gate はapproved scope内のpreflight / commit boundaryであり、scopeを変えない限り追加Human approvalを要求しない。
- final merge decision はHuman-onlyを維持する。

## 停止条件 / 既知のリスク

- `main_planning_context` と supporting agent のauthorityを一意に区別できない。
- model / reasoningの具体値をdurable artifactへ保存しないと実装できない。
- `issue-implementation-loop` のschemaまたはscheduler変更が必要になる。
- Human gateまたはworker-only policyを弱める必要が生じる。
- current architecture validatorのsmall TOML parserでは閉じたpolicyを安全に検証できない。
- context budgetがbaselineから10%を超えて増加する。
- planned write scopeと競合するdirty changeが見つかる。
- scoped dual-host validationまたはrelevant regressionが失敗する。

## 関連ページ

- [Loop Skill Codex 最適化仕様](../loop-skill-codex-optimization-spec.md)
- [Loop Skill Context Optimization Spec](../loop-skill-context-optimization-spec.md)
- [Loop Skill 運用単純化仕様](../loop-skill-operational-simplicity-spec.md)
- [Planning Worktree Gate 仕様](../planning-worktree-gate/spec.md)
