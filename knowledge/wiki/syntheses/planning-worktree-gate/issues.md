# Planning Worktree Gate Issue 台帳

## Epic

- `Epic ID`: `planning-worktree-gate`
- `仕様`: [Planning Worktree Gate 仕様](spec.md)
- `リモート方針`: `local_only`
- `planning branch`: `codex/planning-worktree-gate/planning`
- `planning base SHA`: `b3b869b60dfb785b325f754292dccf675e47313b`

## 台帳

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| planning-worktree-gate | PWTG-001 | Planning Worktree Gate CLI と skill contract を追加する | 承認済み | 実行可能 | なし | PWTG-002, PWTG-004 | 未作成 | 未実施 | 未作成 |
| planning-worktree-gate | PWTG-002 | packet / runtime repository guard を追加する | 承認済み | ブロック中 | PWTG-001 | PWTG-003, PWTG-004 | 未作成 | 未実施 | 未作成 |
| planning-worktree-gate | PWTG-003 | PR_READY / delivery integrity guard を追加する | 承認済み | ブロック中 | PWTG-002 | PWTG-004 | 未作成 | 未実施 | 未作成 |
| planning-worktree-gate | PWTG-004 | wiki 同期と全体 verification / review を完了する | 承認済み | ブロック中 | PWTG-001, PWTG-002, PWTG-003 | なし | 未作成 | 未実施 | 未作成 |

## Blocker graph

```text
PWTG-001 -> PWTG-002 -> PWTG-003 -> PWTG-004
PWTG-001 ---------------------------> PWTG-004
PWTG-002 ---------------------------> PWTG-004
```

cycle はない。`PWTG-004` は統合 validation / review issue であり、複数 blocker head を worker が任意 merge する実装 issue ではない。

## PWTG-001 Planning Worktree Gate CLI と skill contract を追加する

- `実行状態`: `実行可能`
- `write scope`:
  - `skills/grill-to-pr-loop/SKILL.md`
  - `skills/grill-to-pr-loop/references/`
  - `skills/grill-to-pr-loop/scripts/`
  - `skills/grill-to-pr-loop/tests/`
- `受け入れ条件`:
  - clean `main` で `prepare` が `codex/<epic-id>/planning` と Epic-scoped worktree を作る。
  - 同じ branch の registered worktree があれば path を変えずに再利用する。
  - repeated Gate entry が同じ planning worktree identity を返す。
  - `git worktree add` failure 時に default checkout の tracked/untracked content、index、HEAD を変更しない。
  - pre-existing dirt の bytes と porcelain status を変更しない。
  - skill contract が default checkout write/stage/commit禁止、作成失敗時停止、worktree preference再確認不要、Gate間再利用を明記する。
- `非目標`:
  - generic worktree manager。
  - Gate ごとの worktree。
  - `.gitignore` の自動編集。
- `検証`:
  - `python3 -m unittest skills.grill-to-pr-loop.tests.test_planning_worktree_gate`
  - `python3 -m unittest discover -s skills/grill-to-pr-loop/tests`

## PWTG-002 packet / runtime repository guard を追加する

- `実行状態`: `ブロック中`
- `ブロック元`: `PWTG-001`
- `write scope`:
  - `skills/issue-implementation-loop/assets/`
  - `skills/issue-implementation-loop/references/`
  - `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/`
  - `skills/issue-implementation-loop/tests/`
- `受け入れ条件`:
  - new Input Packet v2 が `planning_branch` / `planning_base_sha` を表現し、pair 欠落、非canonical branch、短縮 SHA を拒否する。
  - existing sealed v2 packet bytes を変更せず読み取り互換を保つ。
  - Execution Envelope v4 の untracked `repository_guard` が planning worktree path と default checkout開始snapshotを保持する。
  - packet fields と runtime guard の branch/base mismatch を prepare が拒否する。
  - registered planning worktree / default checkout snapshot mismatch を prepare が拒否する。
  - Gate commit が `epic_base.sha` から到達不能なら `GATE_COMMIT_NOT_ANCESTOR` を返す。
- `非目標`:
  - host path の tracked packet 保存。
  - existing sealed packet の migration / reseal。
- `検証`:
  - `python3 -m unittest skills.issue-implementation-loop.tests.test_validation`
  - `python3 -m unittest skills.issue-implementation-loop.tests.test_approved_spec_binding`

## PWTG-003 PR_READY / delivery integrity guard を追加する

- `実行状態`: `ブロック中`
- `ブロック元`: `PWTG-002`
- `write scope`:
  - `skills/issue-implementation-loop/references/`
  - `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/`
  - `skills/issue-implementation-loop/tests/`
- `受け入れ条件`:
  - success status / completion validation が default checkout HEAD/status drift を拒否する。
  - pre-existing dirt が開始時 snapshot と同一なら許可する。
  - final PR head が approved Gate commit、`planning_base_sha`、全 delivery candidate `head_sha` を含まなければ delivery validation が失敗する。
  - `pr_merged: true` だけでは integration proof としない。
  - guard は default checkout の reset、clean、stash、file move、delete を行わない。
- `非目標`:
  - remote ref の mutation。
  - default checkout の自動復元。
- `検証`:
  - `python3 -m unittest skills.issue-implementation-loop.tests.test_delivery`
  - `python3 -m unittest discover -s skills/issue-implementation-loop/tests`

## PWTG-004 wiki 同期と全体 verification / review を完了する

- `実行状態`: `ブロック中`
- `ブロック元`: `PWTG-001`, `PWTG-002`, `PWTG-003`
- `write scope`:
  - `knowledge/wiki/syntheses/planning-worktree-gate/`
  - `knowledge/index.md`
  - `knowledge/log.md`
- `受け入れ条件`:
  - spec、Issue台帳、実装計画、実装結果の status / evidence が一致する。
  - dual-host / skill architecture / context validators と両 skill full suite が通る。
  - final PR candidate branch が全 planning / implementation commit を含む。
  - default checkout の HEAD/status が runtime start snapshot と一致する。
- `非目標`:
  - push、PR作成、merge。
- `検証`:
  - `python3 scripts/validate_skill_architecture.py --all`
  - `python3 scripts/validate_skill_context.py --all`
  - `python3 scripts/validate_dual_host_authoring.py --all`
  - `python3 -m unittest discover -s scripts`
  - `git diff --check`

## Issue Gate 判断

- `decision`: `approved`
- `actor`: `session-user`
- `scope`: user提示の方針、Acceptance Tests 1〜8、Non-goals を上記4 issueへ分解した dependency / write scope / criteria。
- `remote action`: なし。

## 関連ページ

- [Planning Worktree Gate 仕様](spec.md) は本台帳の scope と停止条件を定義する。
- [Grill To PR Loop Branch Policy Spec](../grill-to-pr-loop-branch-policy-spec.md) は execution issue branch / worktree ownership の既存契約である。

## 出典

- [Planning Worktree Gate 仕様](spec.md)
