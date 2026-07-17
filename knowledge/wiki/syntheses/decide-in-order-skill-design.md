---
kind: synthesis
created: 2026-07-17
updated: 2026-07-17
source_files:
  - ../../raw/sources/2026-07-17-decide-in-order-source-brief.md
---

# Decide In Order Skill 設計

## 状態

実装完了・local verification済み。`decide-in-order` standalone skill、standalone forward test、task-management integration policy、plugin regression verificationまで完了。marketplace、cachebuster、live install、外部writeは未実施。

## 目的

`decide-in-order` は、タスク管理の有無にかかわらず、条件、期限、不安、既投入工数より先に目的と判断基準を整え、何を進め、何を捨て、いつ見直すかを決めるための独立 skill とする。

成果量や TODO 消化量ではなく、全体の進行を支配する中心決定を一つ前進させる。一般的な task store、priority score、schedule engine は作らない。

## 採用した設計

- 正本は独立した `skills/decide-in-order/` とする。
- skill は state-free とし、保存先や外部書き込みを所有しない。
- 判断プロセスは厳密、内部の作業状態は疎、ユーザー表示は適応的、永続化境界だけ型付きにする。
- `task-management` は思想を複製せず、動作別に不使用、軽量、深い判断、review を使い分ける。
- 初期実装で新しい plugin は作らない。既存 task-management plugin には integration policy だけを追加する。
- skill が利用できない場合も task read、routing、明確な task 登録は壊さない。高影響な未解決判断は通常 task として暗黙に登録しない。

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
- TaskDraft の最終生成。
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

## Task-management Integration Policy

task-management 側には `plugins/task-management/skills/task-management/references/decision-support-policy.md` を追加し、既存 `SKILL.md` から条件付きで参照する。思想本文や `DecisionFrame` は複製しない。

| Task-management の動作 | 利用強度 |
| --- | --- |
| task snapshot read / search | 不使用 |
| backend / destination routing | 不使用 |
| adapter preflight / dispatch preview | 不使用 |
| 明確な実行 task の新規登録 | 軽量、通常は不可視 |
| 目的が曖昧な task 化 | 深い判断 |
| 調査 task | 問いと終了条件だけ軽量確認、必要時は深い判断 |
| 優先順位 / 日次計画 | 深い判断 |
| 継続 / 中止 / 延期 / 委任 | 深い判断 |
| 定期見直し / 実行後 review | review 手順 |
| 単純な status 更新 / maintenance | 原則不使用 |

新規 TaskDraft 前に確認するのは、実行準備済みか未解決の意思決定か、目的と条件が矛盾していないか、先に決める核心が残っていないかの 3 点とする。問題がなければ追加表示しない。

新しい handoff schema は作らない。判断結果は既存 TaskDraft へ必要部分だけ反映する。

- 決まった方向: title / outcome。
- 最小行動: body。
- 完了の証拠: acceptance。
- 仮定と未確認事項: review notes。
- durable な判断記録: sanitized `source_ref`。

`decide-in-order` が利用できない場合、read、routing、明確な task 登録は継続する。深い判断が必要な場合は companion skill が利用できないことを明示する。高影響で不可逆な判断は通常 TaskDraft へ押し込まず停止する。task-management 側に簡易版の思想を複製しない。

## Plugin 方針

初期実装で `decide-in-order` 用の新規 plugin scaffold や marketplace entry は作らない。実行 tool、MCP、設定、credential を束ねる必要がなく、単一 skill に plugin 配布層を追加する利点がないためである。

既存 task-management plugin を更新した後は `plugin-creator` validator を通す。repo 内変更だけでは marketplace、cachebuster、live install を変更しない。実際に既存 local plugin を再導入する場合だけ `update_plugin_cachebuster.py` と正式な reinstall flow を使い、marketplace を手編集しない。

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
- task-management は思想を複製せず、動作別 integration policy だけを持つ。
- task read、routing、adapter approval gate、既存 TaskDraft contract が変わらない。
- `decide-in-order` が利用できなくても機械的な task 操作は継続できる。
- 高影響な未解決判断を通常 task として暗黙に登録しない。
- skill / plugin validators、既存 task-management tests、forward test が通る。

## 検証方針

静的検証は `skill-creator` の `quick_validate.py`、`plugin-creator` の `validate_plugin.py`、既存 task-management test suite、`git diff --check`、未確定記述 / 不要 resource 確認を行う。

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
- task-management integration contract tests: 6 passed; full plugin suite: 89 passed.
- task-management skill validation and plugin validation: passed.
- llm-wiki tests: 6 passed.
- repository skill architecture and 3 context contracts: validated.
- Task 3 review fix `4475668` strengthened integration tests after independent review.
- The baseline contained no existing `goals/**/*.json`; ignored, untracked, and tracked counts were all zero, so no goal JSON was created solely for tracking verification.
- No new plugin, marketplace edit, cachebuster, live install, backend call, or external write was performed.

## リスクと対策

- 構造化しすぎて対話が重くなる: 内部状態を疎にし、通常表示を schema 化しない。
- 構造を弱めすぎて思想が失われる: 9 段階の判断順序を処理契約として固定する。
- task-management と責務が重複する: integration policy だけを置き、新しい handoff schema を作らない。
- companion skill がない環境で挙動が曖昧になる: 機械操作は継続し、深い判断の欠落は明示する。
- exact-output test が表現を硬直化する: forward test は行動特性で評価する。
- 大きな判断だけという閾値が曖昧になる: 影響期間、撤回コスト、関係者、説明責任、明示要求を判定基準にする。

## 関連ページ

- [Decide In Order Skill 原案](../sources/2026-07-17-decide-in-order-source-brief.md) — 判断順序、利用場面、品質基準の一次資料。
- [Portfolio OS Task Backend Plugin Skill Spec](portfolio-os-task-backend-plugin-skill-spec.md) — task-management 側の既存責務、TaskDraft、routing、adapter approval 境界。
- [Loop Skill 運用単純化仕様](loop-skill-operational-simplicity-spec.md) — ユーザー向け skill 数と内部機構を分け、露出複雑性を抑える関連設計。

## 出典

- [Decide In Order 原案](../../raw/sources/2026-07-17-decide-in-order-source-brief.md)
- [task-management SKILL.md](../../../plugins/task-management/skills/task-management/SKILL.md)
- [task draft contract](../../../plugins/task-management/skills/task-management/references/task-draft-contract.md)
- [task contracts](../../../plugins/task-management/skills/task-management/references/task-contracts.md)
- `skill-creator:/Users/omitsuhashi/.codex/skills/.system/skill-creator/SKILL.md`
- `plugin-creator:/Users/omitsuhashi/.codex/skills/.system/plugin-creator/SKILL.md`
