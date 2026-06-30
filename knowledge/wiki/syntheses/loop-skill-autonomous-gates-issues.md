# Loop Skill 自動継続 Gate Issue 台帳

## 状態

Spec Gate / Issue Gate 承認済み。Execution Plan Gate は agent preflight + commit boundary として自動通過済み。LSAG-001 から LSAG-005 は未実装。GitHub issue mirror、push、PR 作成、merge はまだ行っていない。承認済み仕様は [Loop Skill 自動継続 Gate 仕様](loop-skill-autonomous-gates-spec.md)、normalized input packet は [Loop Skill 自動継続 Gate Input Packet](loop-skill-autonomous-gates-input-packet.json)。

## 台帳

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loop-skill-autonomous-gates | LSAG-001 | Gate taxonomy と自動継続 policy を定義する | 承認済み | 実行可能 | なし | LSAG-002, LSAG-003, LSAG-004 | 未作成 | 未実施 | 未作成 |
| loop-skill-autonomous-gates | LSAG-002 | Execution Plan Gate の自動継続を実行契約に反映する | 承認済み | ブロック中 | LSAG-001 | LSAG-005 | 未作成 | 未実施 | 未作成 |
| loop-skill-autonomous-gates | LSAG-003 | Live Root Gate / Adapter Availability Gate を readiness gate として整理する | 承認済み | ブロック中 | LSAG-001 | LSAG-005 | 未作成 | 未実施 | 未作成 |
| loop-skill-autonomous-gates | LSAG-004 | final PR 自動作成 policy を Execution Envelope / delivery に固定する | 承認済み | ブロック中 | LSAG-001 | LSAG-005 | 未作成 | 未実施 | 未作成 |
| loop-skill-autonomous-gates | LSAG-005 | regression tests と wiki discoverability を追加する | 承認済み | ブロック中 | LSAG-002, LSAG-003, LSAG-004 | なし | 未作成 | 未実施 | 未作成 |

## ブロッカーグラフ

- LSAG-001: 実行可能。ブロック元 なし。LSAG-002、LSAG-003、LSAG-004 の共通前提。
- LSAG-002: ブロック中。LSAG-001 の gate taxonomy 確定後に、Execution Plan Gate の実行契約を更新する。
- LSAG-003: ブロック中。LSAG-001 の gate taxonomy 確定後に、Live Root / Adapter Availability readiness semantics を整理する。
- LSAG-004: ブロック中。LSAG-001 の gate taxonomy 確定後に、final PR 自動作成の approved action と delivery validation を固定する。
- LSAG-005: ブロック中。LSAG-002、LSAG-003、LSAG-004 の実装後に regression と wiki discoverability を集約する。

循環依存はない。Issue Gate 承認済みのため、全 issue の `レビュー状態` は `承認済み` とする。

## LSAG-001

### Epic ID

`loop-skill-autonomous-gates`

### タイトル

Gate taxonomy と自動継続 policy を定義する

### 作るもの

`grill-to-pr-loop` の gate 説明を、human decision gate、agent preflight gate、remote action gate に分ける。`Execution Plan Gate` は削除せず、agent preflight と commit boundary として残す。`common-mistakes.md` の PR creation 承認表現を、approved remote policy 内の自動作成と矛盾しない形へ更新する。

### 受け入れ条件

- [ ] `skills/grill-to-pr-loop/SKILL.md` または operation-owned reference が、Spec Gate / Issue Gate を human decision gate として説明している。
- [ ] `Execution Plan Gate` は human approval gate ではなく、agent preflight + commit boundary として説明されている。
- [ ] Remote Gate は approved remote policy 外の external write にだけ明示承認を求める gate として説明されている。
- [ ] `common-mistakes.md` は、approved remote policy 内の draft final PR 自動作成を「PR creation は常に個別承認」と誤読させない。
- [ ] final PR merge は常に human-only として残っている。

### 非目標

- Spec Gate / Issue Gate の自動承認。
- final PR merge、ready-for-review、force push、deploy、credential / permission / billing / production / destructive action の自動化。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: なし
- ブロック先: LSAG-002, LSAG-003, LSAG-004

### 想定 write scope

- `path:skills/grill-to-pr-loop/SKILL.md`
- `path:skills/grill-to-pr-loop/references/core.md`
- `path:skills/grill-to-pr-loop/references/common-mistakes.md`
- `path:skills/grill-to-pr-loop/tests`
- `path:knowledge/wiki/syntheses/loop-skill-autonomous-gates-issues.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `rg -n "agent preflight|commit boundary|human-only|Remote Gate" skills/grill-to-pr-loop`
- `git diff --check`

## LSAG-002

### Epic ID

`loop-skill-autonomous-gates`

### タイトル

Execution Plan Gate の自動継続を実行契約に反映する

### 作るもの

`execution-handoff.md` を更新し、承認済み Spec / Issue scope 内で normalized input packet validation と capability preflight が通る場合は、追加承認なしに approval record commit から `issue-implementation-loop prepare` へ進むと明記する。scope change、dirty overlap、capability failure、worker context unavailable、remote policy mismatch は停止条件として維持する。

### 受け入れ条件

- [ ] `Execution Plan Gate` は、承認済み scope 内で `validate_input_packet.py` と capability preflight が通る場合、自動継続できると明記されている。
- [ ] 自動継続前に normalized packet、preflight evidence、write scope、dependency graph、remote policy summary を durable evidence として残す。
- [ ] 自動継続後も承認済み artifacts と `knowledge/log.md` / local ledger 更新を commit してから `issue-implementation-loop prepare` へ進む。
- [ ] scope change、dirty overlap、capability failure、worker context unavailable、remote policy mismatch は停止条件として残っている。
- [ ] planning/grill session が issue work を直接実装しない境界は弱まっていない。

### 非目標

- `issue-implementation-loop` の worker-only policy を弱めること。
- coordinator-direct implementation の許可。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: LSAG-001
- ブロック先: LSAG-005

### 想定 write scope

- `path:skills/grill-to-pr-loop/references/execution-handoff.md`
- `path:skills/grill-to-pr-loop/references/core.md`
- `path:skills/grill-to-pr-loop/tests`
- `path:knowledge/wiki/syntheses/loop-skill-autonomous-gates-issues.md`
- `path:knowledge/log.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `rg -n "Execution Plan Gate|validate_input_packet|capability preflight|issue-implementation-loop prepare" skills/grill-to-pr-loop/references/execution-handoff.md`
- `git diff --check`

## LSAG-003

### Epic ID

`loop-skill-autonomous-gates`

### タイトル

Live Root Gate / Adapter Availability Gate を readiness gate として整理する

### 作るもの

current checkout に literal `Live Root Gate` がないため、既存 `Adapter Availability Gate` と live root readiness の用語を整理する。pass / fail の意味を「承認」ではなく「実行可能性」に限定し、auth missing、destination unresolved、delegation boundary unsafe、root mismatch は setup blocker として扱う。

### 受け入れ条件

- [ ] `Live Root Gate` / `Adapter Availability Gate` は readiness check であり、write approval ではないと明記されている。
- [ ] pass 時は承認済み operation が実行可能であることだけを意味し、未承認 remote write を許可しない。
- [ ] root mismatch、auth missing、destination unresolved、unsafe delegation boundary は setup blocker として表現される。
- [ ] task-management plugin の adapter dispatch approval と readiness gate が混同されない。
- [ ] plugin install が Hermes profile 編集、MCP server 登録、credential 設定を副作用として行わない境界は維持される。

### 非目標

- Hermes profile 編集、MCP server 登録、credential 設定の自動化。
- GitHub Projects mutation や task backend write の自動承認。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: LSAG-001
- ブロック先: LSAG-005

### 想定 write scope

- `path:plugins/task-management/skills/task-management/references/github-mcp-projects.md`
- `path:plugins/task-management/skills/task-management/references/hermes-mcp-governance.md`
- `path:plugins/task-management/skills/task-management/references/adapter-dispatch.md`
- `path:plugins/task-management/tests`
- `path:knowledge/wiki/syntheses/loop-skill-autonomous-gates-issues.md`
- `path:knowledge/log.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests`
- `rg -n "Adapter Availability Gate|readiness|approval|credential|delegation" plugins/task-management`
- `git diff --check`

## LSAG-004

### Epic ID

`loop-skill-autonomous-gates`

### タイトル

final PR 自動作成 policy を Execution Envelope / delivery に固定する

### 作るもの

`remote_write_policy.approved_actions` に `final_pr_push_head` と `final_pr_create_draft` を定義し、`batch_issue_prs` の final PR 作成条件を validator / docs / tests で固定する。draft final PR 作成後は local ledger、runtime state、completion report に PR URL と residual risk を同期する。

### 受け入れ条件

- [ ] `remote_write_policy.approved_actions` が `final_pr_push_head` と `final_pr_create_draft` を表現できる。
- [ ] final PR 自動作成は、delivery plan validation `ok: true`、`epic_base.ref` active、対象 issue の統合済み状態、approved remote policy を満たす場合だけ許可される。
- [ ] final PR head が `epic_base.ref` ではない場合は停止する。
- [ ] 自動作成される final PR は既定で draft。
- [ ] ready-for-review 化、final PR merge、force push は別の human action / approval として残る。
- [ ] draft final PR 作成後に ledger / runtime state / completion report を更新する契約がある。

### 非目標

- final PR merge の agent 実行。
- ready-for-review 化の自動実行。
- GitHub issue mirror の自動作成。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: LSAG-001
- ブロック先: LSAG-005

### 想定 write scope

- `path:skills/issue-implementation-loop/references/remote-delivery.md`
- `path:skills/issue-implementation-loop/references/execution-envelope.md`
- `path:skills/issue-implementation-loop/assets/schemas/execution-envelope.schema.json`
- `path:skills/issue-implementation-loop/assets/templates/execution-envelope.json`
- `path:skills/issue-implementation-loop/assets/templates/delivery-plan.json`
- `path:skills/issue-implementation-loop/scripts`
- `path:skills/issue-implementation-loop/tests`
- `path:knowledge/wiki/syntheses/loop-skill-autonomous-gates-issues.md`
- `path:knowledge/log.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_delivery_plan.py <execution-envelope.json> <runtime-state.json> <delivery-plan.json> --json`
- `rg -n "final_pr_push_head|final_pr_create_draft|human_only|draft" skills/issue-implementation-loop`
- `git diff --check`

## LSAG-005

### Epic ID

`loop-skill-autonomous-gates`

### タイトル

regression tests と wiki discoverability を追加する

### 作るもの

LSAG-001 から LSAG-004 の契約を regression tests と wiki navigation で固定する。`knowledge/index.md` と `knowledge/log.md` から仕様、issue ledger、execution packet、delivery evidence を辿れるようにし、最終実装 evidence を台帳に集約する。

### 受け入れ条件

- [ ] gate taxonomy、Execution Plan Gate auto-continue、Live Root / Adapter Availability readiness semantics、final PR auto-create approved action が tests で固定されている。
- [ ] `knowledge/index.md` が仕様と issue ledger を discoverable にしている。
- [ ] `knowledge/log.md` が Issue Gate、Execution Plan Gate、実装完了、delivery state を追える。
- [ ] final ledger に LSAG-001 から LSAG-005 の implementation evidence、review result、verification result が集約される。
- [ ] full verification が通る。

### 非目標

- 実装本体をこの issue に集約すること。
- GitHub issue mirror、ready-for-review、final PR merge の実行。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: LSAG-002, LSAG-003, LSAG-004
- ブロック先: なし

### 想定 write scope

- `path:scripts`
- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/tests`
- `path:plugins/task-management/tests`
- `path:knowledge/index.md`
- `path:knowledge/log.md`
- `path:knowledge/wiki/syntheses/loop-skill-autonomous-gates-issues.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts`
- `git diff --check`

## リモート方針

Issue Gate 時点では GitHub issue mirror、push、PR 作成、merge は行わない。Execution Envelope で `final_pr_push_head` と `final_pr_create_draft` が approved action として固定された後、実装完了時の draft final PR 作成は追加承認なしに自動実行する。final PR merge、ready-for-review、force push、deploy、credential / permission / billing / production / destructive action は常に自動化対象外とする。
