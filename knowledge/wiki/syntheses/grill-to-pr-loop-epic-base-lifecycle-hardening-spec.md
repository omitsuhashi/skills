# Grill To PR Loop Epic Base Lifecycle Hardening Spec

## 目的

`grill-to-pr-loop` / `issue-implementation-loop` の final PR 経路で、`codex/<epic-id>/epic-base` を名前だけの policy ではなく、検証可能な delivery/integration branch resource として統制する。

## Epic ID

`grill-to-pr-epic-base-lifecycle`

## 受け入れた判断

- `epic_base` は issue work item ではなく、top-level の delivery/integration branch resource として扱う。
- `epic_base.ref` は `batch_issue_prs` では `codex/<epic-id>/epic-base` に固定する。
- `epic_base.sha` は epic 開始時点の immutable initial SHA として維持する。
- `epic_base` は `branch_state` を持ち、`reserved`, `create_on_run`, `active`, `missing` の lifecycle に載せる。
- `epic_base.worktree_path` は任意とする。delivery/reconciliation で物理 worktree を管理する場合だけ絶対 path を記録する。
- `reconcile_git_state.py` は issue reservations に加え、`epic_base` の branch existence / worktree path collision / registered branch を報告する。
- `pr_created` / `pr_merged` event は runtime state に反映し、issue PR merge の事実を durable state に残す。
- final PR readiness は、全 delivery candidate issue が `pr_merged: true` で、`epic_base.ref` が統合済み head として存在することを前提にする。

## 実装範囲

- `skills/issue-implementation-loop/assets/schemas/execution-envelope.schema.json` と template に `epic_base.branch_state` / optional `epic_base.worktree_path` を追加する。
- `skills/issue-implementation-loop/scripts/_common.py` の envelope validation に `epic_base.branch_state` と optional absolute `worktree_path` validation を追加する。
- `skills/issue-implementation-loop/scripts/reconcile_git_state.py` に `epic_base` reconciliation を追加する。
- `skills/issue-implementation-loop/scripts/rebuild_runtime_state.py` に `pr_created` / `pr_merged` event 反映を追加する。
- `skills/issue-implementation-loop/references/{execution-envelope,worktree-lifecycle,remote-delivery,runtime-state}.md` と `skills/grill-to-pr-loop/references/workflow-contract.md` を更新する。
- `skills/issue-implementation-loop/tests/test_issue_implementation_loop.py` に回帰テストを追加する。

## 非目標

- GitHub issue、push、PR 作成、PR merge は実行しない。
- final PR merge を agent に許可しない。
- `epic_base` を通常の issue work item として `work_items` に混ぜない。
- 既存の local-only execution envelope を `batch_issue_prs` へ暗黙変換しない。

## Acceptance Criteria

- `batch_issue_prs` envelope では `epic_base.branch_state` が必須で、許可値以外なら validation が失敗する。
- `epic_base.worktree_path` がある場合は絶対 path でなければ validation が失敗する。
- `reconcile_git_state.py --json` が `epic_base` の branch existence と optional worktree registration を返す。
- 存在しない `epic_base.ref` を指定した `batch_issue_prs` envelope は reconcile で `ok: false` になる。
- `pr_created` event rebuild 後に issue record の `pr` と `pr_opened` が保持される。
- `pr_merged` event rebuild 後に issue record の `pr_merged` と `merge_commit` が保持される。
- docs / templates が `epic_base` を branch lifecycle 管理対象として説明する。
- 既存の `issue-implementation-loop` tests と skill validation が通る。

## 検証コマンド

```bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
git diff --check
```

## Stop Conditions

- `epic_base` を issue work item として扱わないと表現できない要件が出た場合。
- remote branch 作成、push、PR 作成、merge が必要になった場合。
- `epic_base.ref` の既存 branch collision が発生し、人間の判断なしに解消できない場合。
- final PR merge を agent に許可する必要が出た場合。

## 関連ページ

- [Grill To PR Loop Branch Policy Spec](grill-to-pr-loop-branch-policy-spec.md) は branch / worktree / commit policy の先行契約。
- [Grill To PR Loop Epic Base Delivery Policy Spec](grill-to-pr-loop-epic-base-delivery-policy-spec.md) は issue PR / final PR delivery policy の先行契約。

## 出典

- `../../../skills/issue-implementation-loop/scripts/_common.py`
- `../../../skills/issue-implementation-loop/scripts/reconcile_git_state.py`
- `../../../skills/issue-implementation-loop/scripts/rebuild_runtime_state.py`
- `../../../skills/issue-implementation-loop/references/execution-envelope.md`
- `../../../skills/grill-to-pr-loop/references/workflow-contract.md`
