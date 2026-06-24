# Grill To PR Loop Epic Base Delivery Policy Spec

## 目的

`grill-to-pr-loop` / `issue-implementation-loop` の remote delivery を、issue PR は epic base branch へ集約し、final PR は `main` へ出す運用へ更新する。

## Epic ID

`grill-to-pr-epic-base-delivery`

## 受け入れた判断

- epic base branch は `codex/<epic-id>/epic-base` とする。
- `epic_base.ref` は issue PR の base branch、`epic_base.sha` は epic 開始時点の immutable initial SHA とする。
- issue branch は `codex/<epic-id>/<local-id>-<slug>` を維持する。
- issue PR は issue branch から `epic_base.ref` へ作成する。
- issue PR merge は、scope / review / CI / mergeability / permission が明確な場合は agent が既定で実行してよい。
- 判断がぶれる場合、仕様確認が必要な場合、scope drift、CI 失敗、conflict、未解決 review、permission 不明がある場合は human decision へ切り替える。
- issue implementation review は最大 2 回までとする。2 回目でも Critical / Important な in-scope finding が残る場合は human decision へ切り替える。
- final PR は `epic_base.ref` から `main` へ作成する。
- final PR merge は必ず人間が行う。

## 実装範囲

- `skills/grill-to-pr-loop/SKILL.md` と `references/workflow-contract.md` に epic base delivery policy を追加する。
- `skills/issue-implementation-loop/SKILL.md` と `references/{core,execution-envelope,remote-delivery,review-gate}.md` に issue PR / final PR / review cycle policy を追加する。
- `skills/issue-implementation-loop/assets/schemas/{input-packet,execution-envelope,event,runtime-state}.schema.json` と templates を更新する。
- `skills/issue-implementation-loop/scripts/_common.py` に `batch_issue_prs`、`codex/<epic-id>/epic-base`、final PR human-only、review cycle 上限の validation を追加する。
- `skills/issue-implementation-loop/tests/test_issue_implementation_loop.py` に回帰テストを追加する。

## 非目標

- GitHub remote write をこの実装作業内で実行しない。
- issue PR / final PR の実作成や merge をこの作業内で行わない。
- final PR merge を agent に許可しない。
- global `dev` branch を導入しない。

## Acceptance Criteria

- Execution Envelope が `batch_issue_prs` remote mode を受け入れる。
- `batch_issue_prs` では `epic_base.ref` が `codex/<epic-id>/epic-base` でなければ validation が失敗する。
- `batch_issue_prs` では issue PR base が `epic_base.ref`、issue PR merge policy が `agent_default_with_human_escalation` として検証される。
- `batch_issue_prs` では final PR head が `epic_base.ref`、base が `main`、merge policy が `human_only` として検証される。
- `review_policy.max_review_cycles` は 1 以上 2 以下でなければ validation が失敗する。
- docs / templates / agent metadata が `codex/<epic-id>/epic-base` と final PR human-only を説明している。
- 既存の `issue-implementation-loop` tests と skill validation が通る。

## 検証コマンド

```bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest skills.issue-implementation-loop.tests.test_issue_implementation_loop
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
```

## Stop Conditions

- final PR merge を agent に許可する必要が出た場合。
- issue PR merge の判断に scope / spec / CI / conflict / permission ambiguity がある場合。
- 2 回目の issue implementation review 後も Critical / Important な in-scope finding が残る場合。
- `epic_base.ref` naming が既存 branch と衝突する場合。
- remote write が必要になり、approved remote policy がない場合。

## 関連ページ

- [Grill To PR Loop Branch Policy Spec](grill-to-pr-loop-branch-policy-spec.md) は branch / worktree / commit policy の先行契約。
- [Grill To PR Loop Skill Split V2 Spec](grill-to-pr-loop-skill-split-v2-spec.md) は `grill-to-pr-loop` と `issue-implementation-loop` の責務分割。
- [Issue Implementation Loop Context Policy Spec](issue-implementation-loop-context-policy-spec.md) は worker packet / context policy の直近契約。

## 出典

- `../../../skills/grill-to-pr-loop/SKILL.md`
- `../../../skills/grill-to-pr-loop/references/workflow-contract.md`
- `../../../skills/issue-implementation-loop/SKILL.md`
- `../../../skills/issue-implementation-loop/references/execution-envelope.md`
- `../../../skills/issue-implementation-loop/references/remote-delivery.md`
