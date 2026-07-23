---
kind: synthesis
created: 2026-07-17
updated: 2026-07-23
source_files:
  - ../../raw/sources/2026-07-17-decide-in-order-source-brief.md
---

# Decide In Order Skill 設計

## 状態

実装完了・local verification済み。`decide-in-order`はstandalone / state-freeで、task storage、task routing、外部writeを所有しない。2026-07-17のtask-management plugin integration、TaskDraft、adapter、plugin validator、deleted pathに関する記述はhistorical / supersededであり、current `skills/task-management/`から本skillへのdependencyはない。live installと外部writeは未実施。

## 目的

`decide-in-order` は、タスク管理の有無にかかわらず、条件、期限、不安、既投入工数より先に目的と判断基準を整え、何を進め、何を捨て、いつ見直すかを決めるための独立 skill とする。

成果量や TODO 消化量ではなく、全体の進行を支配する中心決定を一つ前進させる。一般的な task store、priority score、schedule engine は作らない。

## 採用した設計

- 正本は独立した `skills/decide-in-order/` とする。
- skill は state-free とし、保存先や外部書き込みを所有しない。
- 判断プロセスは厳密、内部の作業状態は疎、ユーザー表示は適応的、永続化境界だけ型付きにする。
- current task-management skillへdependencyやintegration policyを追加しない。必要な依頼でcallerが両skillを明示的に組み合わせる場合も、責務とstateは分離する。
- 初期実装で新しいpluginを作らず、このstandalone境界を維持する。
- 本skillが利用できないことはtask storageや機械的task operationのavailabilityを左右しない。

## Skill の配置と構成

skill 名は `skill-creator` の verb-led naming に合わせて `decide-in-order` とする。

```text
skills/decide-in-order/
├── SKILL.md
├── agents/openai.yaml
└── references/
    ├── core.md
    ├── modes.md
    └── decision-contracts.md
```

- `SKILL.md`: trigger、mode 選択、共通フロー、reference routing だけを置く。
- `core.md`: 判断順序、不変原則、禁止パターンを置く。
- `modes.md`: 軽量適用、深い対話、review 手順、エスカレーション条件を置く。
- `decision-contracts.md`: 適応的な表示規約と `DecisionRecord` 契約を置く。
- `agents/openai.yaml`: skill 本文から `skill-creator` generator で生成する。

初期版には runtime code、独自 state store、scripts、assets、README を追加しない。skill scaffold は `skill-creator` の `init_skill.py` を使い、手作業で独自 scaffold を作らない。

## 責務境界

`decide-in-order` が所有するもの:

- 目的から見直しまでの判断順序。
- 文脈からの仮説補完と最小限の質問。
- サンクコスト、選択肢過多、期限先行、情報収集先行、不安とリスクの混同の検出。
- 中心決定、最小行動、見直し条件の導出。
- 必要時の `DecisionRecord` 候補生成。

所有しないもの:

- タスク状態の永続保存。
- backend / destination routing。
- 外部 system への書き込み。
- schedule への配置。
- TaskDraftの最終生成（2026-07-17旧plugin contractのhistorical concept）。
- human approval gate の代替。

## 判断順序

次の順序を skill の処理契約とする。

1. `purpose`: 何のためか。
2. `must_protect`: 目的のために絶対に守るものは何か。
3. `acceptable_loss`: そのために意図的に捨ててよいものは何か。
4. `core_question`: 今ここで答える核心の問いは何か。
5. `decision_order`: 先に決めることと後でよいことは何か。
6. `constraints`: 時間、予算、人、環境などの条件は何か。
7. `method`: 条件内でどの手段を選ぶか。
8. `risk`: 起こりうる結果、起こりやすさ、被害、備え、撤退条件は何か。
9. `review`: いつ、何を基準に見直すか。

全項目を常に埋める必要はない。ただし、後段を扱う前に前段を飛ばしてよいかを確認する。

次の順序は避ける。

- 期限だけで優先順位を決める。
- 重要度だけで全 task を並べる。
- 既投入工数を続行理由にする。
- 問いを決める前に情報を集める。
- 全選択肢を残したまま方法比較を続ける。
- 一度の決定を永久決定として扱う。
- 不安の強さをリスクの大きさとみなす。

## 動作モード

### 軽量適用

新しい依頼、明確な実行 task、軽い迷いへ使う。文脈から安全に推定し、問題がなければ skill 固有の構造を表示しない。期限先行や未解決の核心を検出した場合だけ短く補正する。

### 深い対話

優先順位、日次計画、調査方針、継続、中止、延期、委任、重要な選択へ使う。結論を大きく変える不明点だけを一度に一問確認し、選択肢と後回し項目を減らす。

### Review

実行後、定期見直し、方針再評価へ使う。結果だけでなく、目的から判断できたか、順序を逆転させなかったか、どの前提が変わったかを確認する。

## 構造化の方針

構造化するか否かを一律に決めず、層ごとに強度を変える。

| 層 | 方針 |
| --- | --- |
| 判断プロセス | 順序を厳密に保つ |
| 内部作業状態 | 必要な項目だけ持つ疎な `DecisionFrame` |
| ユーザー表示 | 状況に応じた自然文または短い Markdown |
| 永続記録 | 大きな判断だけ型付き `DecisionRecord` 候補 |

`DecisionFrame` は共通語彙であり、厳密な入出力 schema にはしない。空配列や `null` を並べず、通常は serialize しない。推定事項は `assumptions`、判断を変えうる不明点は `unresolved` として区別する。

`DecisionGuidance` は別のデータ型にしない。単純な依頼では不可視、軽量補正では中心決定、最小行動、見直しを短く示し、深い判断では必要な項目だけを表示する。

## DecisionRecord

長期間影響する、撤回コストが高い、複数人や信頼へ影響する、中止や撤退を含む、説明責任がある、または明示的に記録を求められた場合だけ候補を返す。

必須項目:

```yaml
schema_version:
title:
decision_status: provisional | confirmed | superseded
purpose:
core_question:
decision:
must_protect:
acceptable_loss:
next_action:
review:
```

必要時だけ追加する項目:

```yaml
decide_later:
constraints:
alternatives_rejected:
risk:
sunk_cost_check:
assumptions:
evidence:
source_ref:
```

`decision_id`、作成日時、保存先、実保存は呼び出し元が所有する。

## 不明点と安全性

- 文脈から安全に推定できる場合は仮説として補完する。
- 結論を変えない不明点は質問しない。
- 結論を大きく変える不明点だけ、一度に一問確認する。
- 確率の根拠がない場合は数値を作らず、`unknown` または定性的評価にする。
- 核心の問いが未確定なまま方法比較へ進まない。
- 重大で不可逆な損害がありうる場合は、人間承認、追加調査、停止を優先する。
- 単純な実行依頼へ過剰な意思決定対話を挟まない。

## Current task-management boundary

`decide-in-order`と`skills/task-management/`は独立したstandalone skillsである。current task-management skillは、本skillを参照せず、task create / read / updateのためのdependencyにもしていない。

- `decide-in-order`は目的、判断順序、最小行動、見直し条件を導く。
- `task-management`はGitHub Issue / Project上のtask operationだけを扱う。
- どちらも相手のstateや保存先を所有しない。
- callerが両方を明示的に使う場合も、判断結果の保存形式やhandoff schemaをこの設計から強制しない。

## Historical task-management plugin integration（superseded）

2026-07-17実装では、旧`plugins/task-management/`にdecision-support policyを置き、TaskDraft、adapter preflight、dispatch preview、plugin validatorと組み合わせた。このintegration、TaskDraft mapping、companion fallback、plugin再導入手順、deleted pathは2026-07-23 standalone task-management migrationでsupersedeされたhistorical evidenceであり、current implementation instructionではない。

## Plugin 方針

`decide-in-order`用のplugin scaffoldやmarketplace entryは作らない。実行tool、MCP、設定、credential、task storageを束ねる必要がなく、standalone skillにplugin配布層を追加する理由がない。旧task-management pluginのvalidator / cachebuster / reinstall記録はhistoricalであり、current task-management surfaceへ復元しない。

## 非目標

- 一般的な TODO store、calendar、schedule engine を作ること。
- task-management backend contract を置き換えること。
- priority score だけで task を並べること。
- 全判断を YAML として表示または保存すること。
- すべての task 操作を判断対話で止めること。
- provider API、MCP server、credential、外部 write を追加すること。
- 初期実装で新しい plugin や marketplace entry を作ること。

## 受け入れ条件

- `skills/decide-in-order/` が独立 skill として存在し、task-management なしで利用できる。
- `SKILL.md` の frontmatter description が、迷い、優先順位、日次計画、継続判断、調査方針、リスク、review の trigger を表現する。
- 判断順序と禁止パターンの正本が `core.md` に一度だけ存在する。
- 軽量適用は明確な実行依頼を不必要に重くしない。
- 深い対話は一度に一問だけ確認する。
- `DecisionFrame` は疎な内部語彙であり、通常出力 schema にならない。
- `DecisionRecord` は大きな判断だけに生成され、保存は caller が所有する。
- current task-management skillは本skillへのdependency、思想の複製、handoff schemaを持たない。
- task storage、task routing、Project / Issue mutationは`decide-in-order`の責務外である。
- `decide-in-order`が利用できなくても機械的なtask操作は継続できる。
- 高影響な未解決判断を通常 task として暗黙に登録しない。
- standalone skill validator、current task-management tests、forward testが通る。

## 検証方針

current静的検証は`skill-creator`の`quick_validate.py`、standalone task-management test suite、`git diff --check`、未確定記述 / 不要resource確認を行う。2026-07-17のplugin-creator validationはhistorical evidenceとしてのみ保持する。

forward test は期待回答を渡さない新しい subagent へ skill と生の依頼だけを渡し、live backend や外部 write を使わずに行う。

最低限、明確な実行依頼、期限が迫る複数 task、サンクコスト継続、終了条件のない調査、不安が強く確率不明な判断、不可逆な選択、日次計画、実行後 review、task-management integration を試す。

評価は文面一致ではなく、判断順序、質問数、推定の区別、表示量、選択肢削減、最小行動、見直し条件、DecisionRecord 閾値、task-management 責務境界で行う。

## Standalone Forward-test Evidence

- 8 scenarios passed: clear execution, competing deadlines, sunk cost, bounded research, anxiety without probability evidence, irreversible risk, daily planning, and post-action review.
- Evaluation used behavior invariants rather than exact-output matching.
- Fresh agents received only the skill path and raw user request; no expected answer or live backend was provided.
- Final behavior kept clear execution lightweight, asked at most one material question, and limited `DecisionRecord` candidates to material decisions.

## Implementation Evidence

- `decide-in-order` contract tests: 6 passed.
- `decide-in-order` skill validation: passed.
- Standalone forward tests: 8 scenarios passed using fresh agents and behavior-based evaluation.
- Historical 2026-07-17 task-management integration contract tests: 6 passed; old plugin suite: 89 passed。いずれもcurrent task-management verificationではない。
- Historical integration forward tests: final 2/2 passed, covering mechanical read exclusion and decision-sensitive intake。旧plugin integrationの証跡であり、current dependencyを意味しない。
- Historical task-management skill / plugin validation: passed。2026-07-23に旧pluginは削除済み。
- llm-wiki tests: 6 passed.
- repository skill architecture and 3 context contracts: validated.
- Task 3 review fix `4475668` strengthened integration tests after independent review.
- The baseline contained no existing `goals/**/*.json`; ignored, untracked, and tracked counts were all zero, so no goal JSON was created solely for tracking verification.
- No new plugin, marketplace edit, cachebuster, live install, backend call, or external write was performed.
- 2026-07-23 current boundary確認: `decide-in-order`はstandalone / state-free、current `skills/task-management/SKILL.md`は本skillを参照せず、task storageを所有しない。

## リスクと対策

- 構造化しすぎて対話が重くなる: 内部状態を疎にし、通常表示を schema 化しない。
- 構造を弱めすぎて思想が失われる: 9 段階の判断順序を処理契約として固定する。
- task-managementと責務が重複する: current skills間にdependencyやintegration policyを置かず、callerが明示した場合だけ独立に組み合わせる。
- skill availabilityがtask operationへ波及する: task storage / mutationを所有しないことを固定し、機械操作から分離する。
- exact-output test が表現を硬直化する: forward test は行動特性で評価する。
- 大きな判断だけという閾値が曖昧になる: 影響期間、撤回コスト、関係者、説明責任、明示要求を判定基準にする。

## 関連ページ

- [Decide In Order Skill 原案](../sources/2026-07-17-decide-in-order-source-brief.md) — 判断順序、利用場面、品質基準の一次資料。
- [GitHub Projects 直接接続型 Task Management Skill 仕様](direct-github-projects-task-management/spec.md) — current standalone task-management contractと責務境界。
- [Portfolio OS Task Backend Plugin Skill Spec](portfolio-os-task-backend-plugin-skill-spec.md) — TaskDraft / adapter / plugin integrationを記録するhistorical / superseded evidence。
- [Loop Skill 運用単純化仕様](loop-skill-operational-simplicity-spec.md) — ユーザー向け skill 数と内部機構を分け、露出複雑性を抑える関連設計。

## 出典

- [Decide In Order 原案](../../raw/sources/2026-07-17-decide-in-order-source-brief.md)
- [current task-management SKILL.md](../../../skills/task-management/SKILL.md)
- [current task-management spec](direct-github-projects-task-management/spec.md)
- [historical Portfolio OS Task Backend Plugin Skill Spec](portfolio-os-task-backend-plugin-skill-spec.md)
- `skill-creator:/Users/omitsuhashi/.codex/skills/.system/skill-creator/SKILL.md`
