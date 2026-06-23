# Grill To PR Loop Branch Policy Spec

## 目的

`grill-to-pr-loop` と `issue-implementation-loop` に、branch / worktree / commit の推奨運用を明確な契約として追加する。

この変更では「開発メインブランチへ各 worktree を順次 merge する」運用を既定にしない。実行の正本は Execution Envelope の immutable `epic_base` とし、issue ごとの branch / worktree reservation、typed dependency edge、scoped local commit、local `PR_READY` を標準の終端にする。

## Epic ID

`grill-to-pr-branch-policy`

## 受け入れた判断

- planning 用 branch は任意。実行契約上の親は mutable branch ではなく `epic_base.ref` + `epic_base.sha`。
- `epic_base.sha` は full 40/64-character hex SHA として契約検証し、Git object の実在確認は git state reconciliation に分離する。
- issue branch は `codex/<epic-id>/<local-id>-<slug>` を基本形にする。
- approved issue は 1 issue につき 1 branch / worktree reservation を持つ。
- blocked issue は branch / path を予約できるが、物理 worktree は release まで作らない。
- downstream が前段の code を必要とする場合は、merge ではなく dependency edge の `base_effect` と work item の `base_policy` で表現する。
- 複数 blocker head を downstream worker が任意 merge してはならない。必要な場合は integration work item / integration branch を明示的に作る。
- issue 完了、blocker release、PR readiness の前に、fresh verification 後の scoped local commit を作り、`BASE_SHA..HEAD_SHA` を review range として記録する。
- `PR_READY` / `COMPLETE` / `DONE` は committed `BASE_SHA..HEAD_SHA` review range を必須にし、`working-tree` や欠落 range は拒否する。
- remote push / GitHub issue / PR / merge は引き続き明示承認が必要。

## 実装範囲

- `skills/grill-to-pr-loop/SKILL.md` に branch/base/commit policy の要点を追加する。
- `skills/grill-to-pr-loop/references/workflow-contract.md` に具体運用を追加する。
- `skills/issue-implementation-loop/references/execution-envelope.md` と `dependency-contract.md` に `base_policy` と integration branch の扱いを明記する。
- `skills/issue-implementation-loop/scripts/_common.py` に envelope / runtime validation を追加する。
- `skills/issue-implementation-loop/tests/test_issue_implementation_loop.py` に回帰テストを追加する。
- `skills/issue-implementation-loop/assets/schemas/execution-envelope.schema.json` と template を更新する。

## 非目標

- GitHub issue、push、PR、merge を実行しない。
- generic scheduler skill、standalone worktree manager skill、approval skill を増やさない。
- 既存の skill split v2 実行履歴を新しい commit range に書き換えない。
- `main` へ merge しない。

## Acceptance Criteria

- `grill-to-pr-loop` が「開発メインブランチ」ではなく `epic_base` を実行契約の中心として説明している。
- issue branch naming、worktree reservation、blocked issue の physical worktree delay が明示されている。
- scoped local commit の順序が `fresh verification -> scoped local commit -> issue review -> fixes/re-review -> PR_READY` として明示されている。
- `epic_base.ref` / `epic_base.sha` の欠落または短縮 SHA を envelope validation が拒否する。
- `issue-implementation-loop` の envelope validation が `base_policy` type を検証する。
- `branch_from_blocker_head` を複数 blocker へ同時に使う envelope を拒否する。
- `branch_from_integration_head` を複数 integration head へ同時に使う envelope を拒否する。
- `branch_from_integration_head` を使う dependency が integration base policy と一致しない envelope を拒否する。
- `PR_READY` / `COMPLETE` / `DONE` issue の review range 欠落または `working-tree` が明示された runtime state を拒否する。
- 既存の `issue-implementation-loop` テストと skill validation が通る。

## 検証コマンド

```bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase execution --json
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_input_packet.py knowledge/wiki/syntheses/grill-to-pr-loop-branch-policy-input-packet.json
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_execution_envelope.py knowledge/wiki/syntheses/grill-to-pr-loop-branch-policy-execution-envelope.json
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/reconcile_git_state.py knowledge/wiki/syntheses/grill-to-pr-loop-branch-policy-execution-envelope.json --json
```

## Stop Conditions

- dirty repo changes overlap with the planned write scope.
- proposed branch / worktree reservation collides.
- envelope validation が `base_policy` / dependency edge の不整合を検出する。
- scoped commit range を作れず、manual fallback も明示承認されていない。
- Critical / Important な in-scope review finding が未修正で、人間の明示 risk acceptance もない。
- external write が必要になる。

## 関連ページ

- [Grill To PR Loop Skill Split V2 Spec](grill-to-pr-loop-skill-split-v2-spec.md) は `grill-to-pr-loop` と `issue-implementation-loop` の責務分割を定義している。
- [Grill To PR Loop Issue Implementation Review Gate Plan](grill-to-pr-loop-issue-implementation-review-gate-plan.md) は scoped local commit と issue review gate の先行設計。

## 出典

- `../../../skills/grill-to-pr-loop/SKILL.md`
- `../../../skills/grill-to-pr-loop/references/workflow-contract.md`
- `../../../skills/issue-implementation-loop/SKILL.md`
- `../../../skills/issue-implementation-loop/references/execution-envelope.md`
- `../../../skills/issue-implementation-loop/references/dependency-contract.md`
