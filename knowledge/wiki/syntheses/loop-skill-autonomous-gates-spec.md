# Loop Skill 自動継続 Gate 仕様

## 状態

Spec Gate / Issue Gate 承認済み。Execution Plan Gate は agent preflight + commit boundary として自動通過済み。承認済み local issue ledger は [Loop Skill 自動継続 Gate Issue 台帳](loop-skill-autonomous-gates-issues.md)、normalized input packet は [Loop Skill 自動継続 Gate Input Packet](loop-skill-autonomous-gates-input-packet.json) に置く。2026-06-30 のユーザー承認により、`Execution Plan Gate` と `Live Root Gate` は都度の人間レビュー対象にせず、agent preflight と commit boundary として扱う。実装完了後の final PR 作成も、承認済み delivery policy 内では追加承認なしに自動実行する。final PR merge は引き続き human-only。

## 問題設定

`grill-to-pr-loop` / `issue-implementation-loop` は、Spec Gate、Issue Gate、Execution Plan Gate、Remote Gate、Implementation Review Gate を使って、長い repository change を監査可能に進める。ただし `Execution Plan Gate` と live root readiness 系の gate は、提示される情報が packet path、capability preflight、write scope、dependency graph、root / adapter readiness であり、人間が都度判断するには低レベルすぎる。

現在の摩擦は次の通り。

- Spec / Issue 承認後でも、Execution Plan Gate が人間待ちになり、承認済み scope の実装開始が止まる。
- live root / adapter availability の確認が human approval gate のように見えると、実際には人間が判断できない readiness check までユーザー判断に戻る。
- 実装完了後の final PR 作成も別承認を求めるため、local `PR_READY` 後の配送で不要な wait が発生する。
- 一方で、remote write、credential、permission、destructive action、production action、final merge まで自動化すると安全境界が崩れる。

この仕様は、人間が判断すべき gate と agent が機械的に処理すべき gate を分離し、承認済み scope 内では自動継続する契約へ更新する。

## Epic ID

`loop-skill-autonomous-gates`

## 現在の前提

- `python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase planning` は通過済み。
- `gh` auth は現時点では unavailable。これは設計時点の remote 実行不可であり、自動 PR 作成方針そのものの否定ではない。
- current checkout には `Live Root Gate` という literal な名称は存在しない。既存の近い契約は `Adapter Availability Gate` と live root / adapter readiness preflight である。この仕様では `Live Root Gate` を「live root または external adapter が承認済み operation を受け取れるかを確認する readiness gate」として扱う。
- `remote_write_policy.approved_actions` は既に Execution Envelope の schema に存在するが、現在は final PR 自動作成の action name / semantics が固定されていない。
- `batch_issue_prs` の final PR は `epic_base.ref` から `main` へ作成し、final PR merge は `human_only` として検証される。

## 採用する判断

- **Spec Gate と Issue Gate は人間レビューを維持する。** 仕様、非目標、issue 粒度、依存関係、acceptance criteria は人間が判断すべき対象である。
- **Execution Plan Gate は auto-continue gate に変更する。** normalized input packet、capability preflight、write scope、dependency graph、fallback policy、local / remote policy を agent が検証し、承認済み artifact と ledger / log を commit してから自動的に `issue-implementation-loop prepare` へ進む。
- **Execution Plan Gate は削除しない。** 人間承認を求めないだけで、packet validation、preflight evidence、commit boundary、stop condition は維持する。
- **Live Root Gate は readiness check として自動継続する。** live root path、repo root、worktree root、adapter availability、destination / connection reference、auth availability、delegation boundary などを agent / host が検証し、pass なら継続、fail なら setup blocker として停止する。
- **Live Root Gate は write approval ではない。** live root readiness が pass しても、未承認の remote write、credential、permission、destructive action、production action は許可しない。
- **final PR 作成は承認済み delivery policy 内で自動化する。** 仕様または Issue Gate / Execution Envelope が `final_pr_push_head` と `final_pr_create_draft` を approved action として持つ場合、全 issue が対象 scope で完了し、`epic_base.ref` が active で、delivery plan validation が `ok: true` のとき、agent は追加承認なしに branch push と draft final PR 作成を実行してよい。
- **final PR merge は常に human-only。** ready-for-review 化、merge、force push、deploy、billing、credential、permission、production、destructive remote action は自動化対象外とする。
- **GitHub issue mirror はこの仕様では自動化しない。** final PR 作成の自動化は GitHub issue 作成や task backend mutation の自動承認を意味しない。
- **既存 skill は concise に保つ。** `SKILL.md` は trigger / invariant / stop condition を中心にし、詳細は references、schema、validator、tests に置く。

## 非目標

- Spec Gate / Issue Gate の自動承認。
- final PR merge の agent 実行。
- ready-for-review 化の自動実行。
- GitHub issue mirror、GitHub Projects mutation、task backend write の包括的な自動承認。
- credential / permission / production / billing / destructive action の自動承認。
- `grill-to-pr-loop` を実装 worker にすること。
- `issue-implementation-loop` の worker-only execution boundary を弱めること。
- live root setup、Hermes profile 編集、MCP server 登録、credential 設定を repository skill install の副作用にすること。

## Issue 分解方針

Spec Gate 承認後に、日本語 local-first ledger として次の blocker order で issue 化する。

1. **LSAG-001: Gate taxonomy と自動継続 policy を定義する**
   - `grill-to-pr-loop` の gate 説明を、human decision gate、agent preflight gate、remote action gate に分ける。
   - `Execution Plan Gate` を auto-continue gate として説明し、commit boundary と stop condition を維持する。
   - `common-mistakes.md` の「PR creation は常に個別承認」のような古い表現を、approved remote policy 内の自動作成と矛盾しない形へ更新する。

2. **LSAG-002: Execution Plan Gate の自動継続を実行契約に反映する**
   - `execution-handoff.md` を更新し、承認済み Spec / Issue scope 内で packet validation と capability preflight が通る場合は、追加承認なしに approval record commit から `issue-implementation-loop prepare` へ進むと明記する。
   - `validate_input_packet.py`、`check_capabilities.py --input`、write scope / dependency graph / remote policy summary を evidence として残す。
   - scope change、dirty overlap、capability failure、worker context unavailable、remote policy mismatch は停止条件として維持する。

3. **LSAG-003: Live Root Gate / Adapter Availability Gate を readiness gate として整理する**
   - current checkout に literal `Live Root Gate` がないため、既存 `Adapter Availability Gate` と live root readiness の用語を整理する。
   - pass / fail の意味を「承認」ではなく「実行可能性」に限定する。
   - auth missing、destination unresolved、delegation boundary unsafe、root mismatch は setup blocker として報告し、人間判断ではなく環境修正待ちにする。
   - task-management plugin の adapter dispatch approval と混同しないよう、readiness gate は state-changing operation approval ではないと明記する。

4. **LSAG-004: final PR 自動作成 policy を Execution Envelope / delivery に固定する**
   - `remote_write_policy.approved_actions` に `final_pr_push_head` と `final_pr_create_draft` を定義する。
   - `batch_issue_prs` では `epic_base.ref` active、対象 issue の `pr_merged: true` または承認済み ledger-equivalent integration record、delivery plan `ok: true` を final PR 作成条件にする。
   - draft final PR 作成後は local ledger、runtime state、completion report に PR URL と residual risk を同期する。
   - final PR merge、ready-for-review、force push は常に別の human action / approval として残す。

5. **LSAG-005: regression tests と wiki discoverability を追加する**
   - gate taxonomy、Execution Plan Gate auto-continue、Live Root / Adapter Availability readiness semantics、final PR auto-create approved action を tests で固定する。
   - `knowledge/index.md` と `knowledge/log.md` から仕様、issue ledger、execution packet、delivery evidence を辿れるようにする。

## 受け入れ条件

- `grill-to-pr-loop` は、Spec Gate / Issue Gate を human decision gate、Execution Plan Gate を agent preflight + commit boundary、Remote Gate を remote action policy gate として説明している。
- Execution Plan Gate は、承認済み scope 内で `validate_input_packet.py` と capability preflight が通り、外部 / 高リスク action を含まない場合、人間承認待ちせずに `issue-implementation-loop prepare` へ進める。
- Execution Plan Gate の auto-continue 後も、承認済み artifacts と `knowledge/log.md` / local ledger 更新は commit される。
- `Live Root Gate` / `Adapter Availability Gate` は readiness check であり、write approval ではないと明記される。
- live root / adapter readiness failure は、承認待ちではなく setup blocker として報告される。
- `remote_write_policy.approved_actions` が `final_pr_push_head` と `final_pr_create_draft` を表現できる。
- final PR 自動作成は、delivery plan validation `ok: true`、`epic_base.ref` active、対象 issue の統合済み状態、approved remote policy を満たす場合だけ実行される。
- 自動作成される final PR は既定で draft。ready-for-review 化は別承認または明示 approved action がある場合だけ許可される。
- final PR merge は常に human-only として schema、validator、docs、tests に残る。
- GitHub issue mirror、task backend mutation、credential / permission / billing / production / destructive action はこの仕様の自動化対象に含まれない。
- `SKILL.md` は肥大化させず、詳細 contract は references、schema、validator、tests に置く。

## 検証方針 / コマンド

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_delivery_plan.py <execution-envelope.json> <runtime-state.json> <delivery-plan.json> --json
rg -n "Execution Plan Gate|Live Root Gate|Adapter Availability Gate|final_pr_create_draft|final PR merge" skills plugins scripts knowledge/wiki/syntheses
git diff --check
```

`plugins/task-management/tests` が存在しない checkout では、その command は skip して理由を completion report に残す。

## リモート書き込み方針

この仕様自体の実装は local-first で進める。実装完了後の final PR 作成については、ユーザーの 2026-06-30 方針により、承認済み delivery policy に `final_pr_push_head` と `final_pr_create_draft` が含まれる場合、追加の Remote Gate 承認を求めず自動作成してよい。

自動化対象:

- final PR head branch の push。
- draft final PR の作成。
- PR URL / state の local ledger、runtime state、completion report への同期。

自動化対象外:

- final PR merge。
- ready-for-review 化。
- force push。
- deploy。
- credential / permission / billing / production / destructive action。
- GitHub issue mirror。
- task backend state-changing adapter dispatch。

GitHub auth、network、permission、branch protection、conflict、failed checks、delivery plan validation failure がある場合、approval 待ちではなく実行不能または human action required として停止する。

## 人間レビューゲート

- **Spec Gate**: この仕様の Epic ID、採用する判断、非目標、受け入れ条件、検証、remote policy、停止条件を承認する。
- **Issue Gate**: 日本語 local-first issue ledger の粒度、blocker graph、依存順、acceptance criteria を承認する。
- **Execution Plan Gate**: human approval gate ではなく、agent preflight + commit boundary として実行する。stop condition がなければ自動継続する。
- **Live Root Gate / Adapter Availability Gate**: human approval gate ではなく、readiness gate として実行する。pass なら継続、fail なら setup blocker として停止する。
- **Implementation Review Gate**: 各 issue completion / blocker release / PR_READY 前に issue-scoped implementation review を実施する。
- **Remote Gate**: approved remote policy に含まれない外部 write が必要になった場合だけ exact action set を提示し、明示承認を待つ。

## 停止条件

- Spec Gate または Issue Gate の承認がない。
- Execution Plan Gate の auto-continue が approved scope を変更する必要がある。
- normalized input packet、capability preflight、write scope、dependency graph、remote policy の検証に失敗する。
- dirty changes が planned write scope と重なる。
- worker context が利用できず、coordinator-direct implementation が必要になる。
- live root / adapter availability が root mismatch、auth missing、destination unresolved、unsafe delegation boundary を返す。
- delivery plan validation が `ok: true` にならない。
- final PR head が `epic_base.ref` ではない、または `epic_base.ref` が active ではない。
- 対象 issue が final PR scope に統合済みであることを runtime state または承認済み ledger-equivalent record で確認できない。
- final PR 作成以外の remote write、ready-for-review、merge、force push、deploy、credential、permission、billing、production、destructive action が必要になる。
- 2 回目の implementation review 後も Critical / Important な in-scope finding が残り、人間の risk acceptance が必要になる。

## 既知のリスク

- `Live Root Gate` という名称が current checkout にはないため、実装時に既存 `Adapter Availability Gate` と新しい live root terminology の対応を誤る可能性がある。
- draft final PR 自動作成を ready PR 作成と混同すると、ready-for-review gate が弱まる。
- `approved_actions` の action name を自由文字列のまま増やすと validator が弱くなるため、実装時は enum 化または dedicated validator を追加する必要がある。
- GitHub auth unavailable は承認問題ではなく実行環境問題なので、auto policy だけでは解決しない。
- 自動継続を強めすぎると、Spec / Issue scope drift まで機械的に進む危険がある。scope drift は必ず stop condition として残す。

## 関連ページ

- [Loop Skill 運用単純化仕様](loop-skill-operational-simplicity-spec.md)
- [Grill To PR Loop Epic Base Delivery Policy Spec](grill-to-pr-loop-epic-base-delivery-policy-spec.md)
- [Loop Skill Architecture V3 Spec](loop-skill-architecture-v3-spec.md)
- [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- [Portfolio OS Task Backend Plugin Skill Spec](portfolio-os-task-backend-plugin-skill-spec.md)

## 出典

- [skills/grill-to-pr-loop/SKILL.md](../../../skills/grill-to-pr-loop/SKILL.md)
- [skills/grill-to-pr-loop/references/core.md](../../../skills/grill-to-pr-loop/references/core.md)
- [skills/grill-to-pr-loop/references/execution-handoff.md](../../../skills/grill-to-pr-loop/references/execution-handoff.md)
- [skills/grill-to-pr-loop/references/remote-delivery.md](../../../skills/grill-to-pr-loop/references/remote-delivery.md)
- [skills/issue-implementation-loop/SKILL.md](../../../skills/issue-implementation-loop/SKILL.md)
- [skills/issue-implementation-loop/references/execution-envelope.md](../../../skills/issue-implementation-loop/references/execution-envelope.md)
- [skills/issue-implementation-loop/references/remote-delivery.md](../../../skills/issue-implementation-loop/references/remote-delivery.md)
- [plugins/task-management/skills/task-management/references/github-mcp-projects.md](../../../plugins/task-management/skills/task-management/references/github-mcp-projects.md)
- [knowledge/AGENTS.md](../../AGENTS.md)
