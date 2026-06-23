# Grill To PR Loop Skill Split V2 Spec

## 目的

`grill-to-pr-loop` を設計・Issue分解・PR delivery の composition skill に戻し、承認済み Issue 群の非停止型実装を `issue-implementation-loop` として再利用できるようにする。

## Epic ID

`issue-implementation-loop`

## 受け入れた判断

- 新設するユーザー向け skill は `issue-implementation-loop` のみ。
- `execution-envelope`、worktree reservation、typed dependency edge、event-driven scheduler、scoped human wait、durable resume、review gate は個別 skill に分けず、`issue-implementation-loop` の reference / script / schema に閉じる。
- coordinator は同じ parent session が保持し、skill split は source organization として扱う。skill 間 handoff や外部 LLM router は作らない。
- mutable runtime state は tracked issue branch に置かず、git common dir 配下を既定にする。
- Execution Plan Gate 後の通常遷移では再承認を求めず、Runtime Exception Gate は issue / descendants / resource / epic scope へ局所化する。
- GitHub issue / push / PR / merge / deploy / destructive / credential / billing / permission 操作は引き続き明示承認が必要。

## 実装範囲

- `skills/issue-implementation-loop/` を追加する。
- `SKILL.md` は mode router と最小運用契約だけを持ち、詳細は `references/` に分ける。
- `assets/schemas/` に input packet、execution envelope、runtime state、event、worker report、human request の JSON schema を置く。
- `assets/templates/` に execution envelope、decisions、completion summary の雛形を置く。
- `scripts/` に capability check、input / envelope / runtime validation、next action 計算、event log rebuild、git state reconcile を置く。
- `tests/` に pressure scenario を確認する unittest を置く。
- `skills/grill-to-pr-loop/` は `issue-implementation-loop` への normalized packet 作成と optional PR delivery coordination を明記する。
- `grill-to-pr-loop/scripts/check_prereqs.py` は planning phase と execution phase の前提を分ける。

## 非目標

- standalone scheduler skill、approval skill、worktree manager skill、generic agent orchestration framework は作らない。
- GitHub issue / PR を自動作成しない。
- merge、force-push、deploy、production、billing、credential、permission 操作は実装しない。
- 実 worker / reviewer の外部並列実行プラットフォームをこの repo に作り込まない。

## ローカルIssue分解

詳細は [Grill To PR Loop Skill Split V2 Issues](grill-to-pr-loop-skill-split-v2-issues.md) を参照する。

## Acceptance Criteria

- `grill-to-pr-loop` が planning/composition 責務に縮小されている。
- `issue-implementation-loop` が既存 Issue から直接利用できる。
- 同じ coordinator が全体文脈と最終責任を保持する契約になっている。
- Execution Plan Gate 後の通常遷移で再承認を要求しない。
- blocked Issue を含む全 Issue の branch/worktree reservation を envelope で表現できる。
- blocked Issue の物理 worktree は解除前に作らない契約になっている。
- Issue event ごとに runnable を再計算でき、Wave 全体完了を待たない。
- human wait は既定で issue scope であり、unrelated work は継続できる。
- reviewer / parallel fallback は開始前に capability preflight / envelope policy で確定する。
- runtime state は issue branch の tracked file に置かない。
- worker / reviewer は中央 state を直接更新しない。
- session 中断後に state / git / report を reconcile できる。
- remote failure は local lane を止めない。
- merge / force-push / deploy / destructive action は引き続き明示承認が必要。
- standalone scheduler / approval / worktree skill を増やしていない。

## 検証コマンド

```bash
python3 -m unittest discover -s skills/issue-implementation-loop/tests
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase execution --json
python3 skills/issue-implementation-loop/scripts/check_capabilities.py --input knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-input-packet.json --json
python3 skills/issue-implementation-loop/scripts/validate_input_packet.py knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-input-packet.json
python3 skills/issue-implementation-loop/scripts/validate_execution_envelope.py knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-execution-envelope.json
python3 skills/issue-implementation-loop/scripts/compute_next_actions.py knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-execution-envelope.json knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-runtime-state.json
python3 skills/issue-implementation-loop/scripts/validate_runtime_state.py knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-runtime-state.json
python3 skills/issue-implementation-loop/scripts/rebuild_runtime_state.py knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-events.jsonl
python3 skills/issue-implementation-loop/scripts/reconcile_git_state.py knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-execution-envelope.json --json
```

## Stop Conditions

- `grill-with-docs` がない。
- `issue-implementation-loop` が execution phase 前提として見つからない。
- proposed branch / worktree reservation が衝突している。
- blocker graph に cycle がある。
- approved envelope 外の write scope / remote action / destructive action が必要になる。
- Critical / Important な in-scope review finding が未修正で、人間の明示 risk acceptance もない。
- runtime snapshot と event log / git state を reconcile できない。

## 関連ページ

- [Grill To PR Loop スキル分割・非停止実行 詳細設計 v2](../sources/2026-06-21-grill-to-pr-loop-skill-split-design-v2.md) は元設計の source summary。
- [Grill To PR Loop Issue Implementation Review Gate Plan](grill-to-pr-loop-issue-implementation-review-gate-plan.md) は review gate の先行設計。

## 出典

- [raw/sources/2026-06-21-grill-to-pr-loop-skill-split-design-v2.md](../../raw/sources/2026-06-21-grill-to-pr-loop-skill-split-design-v2.md)
- [skills/grill-to-pr-loop/SKILL.md](../../../skills/grill-to-pr-loop/SKILL.md)
- [skills/grill-to-pr-loop/references/workflow-contract.md](../../../skills/grill-to-pr-loop/references/workflow-contract.md)
