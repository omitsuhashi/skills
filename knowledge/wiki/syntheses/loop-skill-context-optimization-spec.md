# Loop Skill Context Optimization Spec

## 目的

`grill-to-pr-loop` と `issue-implementation-loop` を、長い repository change を扱うための 2 つの user-facing skill として維持しつつ、読み込む文脈量と stale skill 誤検出を減らす。

この spec は、現在の到達点から「ベストな状態」へ寄せるための全体方針と、今回の実装スライスを分けて定義する。

## Epic ID

`loop-skill-context-optimization`

## 現状

- `grill-to-pr-loop` は planning / composition skill へ縮小済みだが、`SKILL.md` が 1253 words、`references/workflow-contract.md` が 1711 words あり、実行時に読む reference がまだ太い。
- `issue-implementation-loop` は `SKILL.md` が 507 words で mode router を持ち、entrypoint は十分に薄い。
- `issue-implementation-loop/scripts/_common.py` は 874 lines で、input / envelope / runtime / worker / delivery validation、DAG、scheduler、git helper、skill discovery が混在している。
- `issue-implementation-loop/tests/test_issue_implementation_loop.py` は 1355 lines で、実行契約の圧力テストが 1 file に集中している。
- preflight / capability check の skill discovery は global install を repo-local `skills/` より先に拾う場合があり、skill 開発中に stale installed copy を検証してしまうリスクがある。

## ベストな状態

- User-facing skill は `grill-to-pr-loop` と `issue-implementation-loop` の 2 つに留める。
- `execution-envelope`, scheduler, runtime state, worktree lifecycle, review gate, remote delivery は独立 skill にしない。`issue-implementation-loop` の reference / schema / helper として保持する。
- `grill-to-pr-loop/SKILL.md` は state machine と gate の入口だけを持ち、詳細は one-level reference に逃がす。
- `grill-to-pr-loop/references/workflow-contract.md` は backward-compatible router とし、planning, ledger, handoff, delivery, mistakes を分割 reference に委譲する。
- `issue-implementation-loop/SKILL.md` は 520 words 以下を維持する。
- `issue-implementation-loop/scripts/_common.py` は後続 slice で `lib/validation.py`, `lib/dependency_graph.py`, `lib/scheduler.py`, `lib/runtime.py`, `lib/delivery.py`, `lib/git_state.py`, `lib/skill_discovery.py` に分ける。
- `issue-implementation-loop/tests/` は後続 slice で validation / runtime / delivery / scheduler / git reconcile / skill discovery に分ける。
- repo-local skill roots は global install roots より優先される。JSON output は selected root と checked roots を見て stale copy を判別できる。

## 今回の実装範囲

今回は次だけを行う。

1. この spec、local issue ledger、normalized input packet を `knowledge/wiki/syntheses/` に追加する。
2. `grill-to-pr-loop/references/workflow-contract.md` を router 化し、以下の one-level references を追加する。
   - `planning-contract.md`
   - `local-issue-ledger.md`
   - `execution-handoff.md`
   - `remote-delivery.md`
   - `common-mistakes.md`
3. `grill-to-pr-loop/SKILL.md` の reference routing を更新する。
4. `grill-to-pr-loop/scripts/check_prereqs.py` と `issue-implementation-loop/scripts/_common.py` の skill root 順序を repo-local 優先へ変更する。
5. `skills/grill-to-pr-loop/tests/` を追加し、reference routing と root ordering の回帰テストを置く。
6. `skills/issue-implementation-loop/tests/test_issue_implementation_loop.py` に repo-local root ordering の最小回帰テストを追加する。
7. `knowledge/index.md` と `knowledge/log.md` を更新する。

## 今回やらないこと

- `_common.py` の大規模 lib 分割。
- `test_issue_implementation_loop.py` の大規模 test file 分割。
- 新しい user-facing skill の追加。
- GitHub issue / PR 作成、push、merge、remote write。
- subagent / user-owned Codex thread の自動作成。

## 受け入れた判断

- 今の最大の context 効率改善は `grill-to-pr-loop` の太い workflow reference を split router にすること。
- `issue-implementation-loop` の mode-specific reference は現時点では維持する。実際の重さは `_common.py` と tests の責務混在の方が大きい。
- helper library 分割は behavior-preserving refactor だが影響範囲が大きいため、今回の slice では仕様に残して次回対応にする。
- preflight が global installed skill を先に拾う問題は、今回の slice で直す。skill 開発 repo では repo-local copy が最も信頼できるため。
- remote write は未承認かつ GitHub auth も optional failure なので、今回の delivery intent は `local_only` とする。

## Acceptance Criteria

- `grill-to-pr-loop/SKILL.md` が分割 reference の routing を説明している。
- `workflow-contract.md` が full contract ではなく router として振る舞い、詳細を one-level references へ委譲している。
- 新規 reference files が `workflow-contract.md` から直接発見できる。
- `planning-contract.md` が artifact/spec/gate を持つ。
- `local-issue-ledger.md` が日本語 local-first ledger と blocker graph contract を持つ。
- `execution-handoff.md` が normalized packet と `issue-implementation-loop` handoff を持つ。
- `remote-delivery.md` が GitHub mirror / issue PR / final PR / approval policy を持つ。
- `common-mistakes.md` が既存 mistakes を保持する。
- `check_prereqs.py` と `_common.py` が `Path.cwd()/skills` を global install roots より先に探す。
- 回帰テストが repo-local root ordering と reference routing を検証する。
- 既存 `issue-implementation-loop` tests が通る。
- `git diff --check` が通る。

## 検証コマンド

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase execution --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/check_capabilities.py --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_input_packet.py knowledge/wiki/syntheses/loop-skill-context-optimization-input-packet.json
git diff --check
```

`quick_validate.py` は `PyYAML` が必要なため、環境に dependency cache がない場合は `uv --with PyYAML==6.0.2` で確認する。ネットワークが閉じている場合は未検証として記録する。

## Stop Conditions

- `workflow-contract.md` の router 化で、既存の mandatory gate や stop condition が新 references から発見できなくなる。
- skill root ordering の変更で explicit `--skills-root` の優先度が下がる。
- repo-local root を優先した結果、plugin-provided optional skill detection が消える。
- tests が既存 branch/base/commit policy または delivery policy を壊す。
- remote write が必要になる。

## 関連ページ

- [Grill To PR Loop Skill Split V2 Spec](grill-to-pr-loop-skill-split-v2-spec.md) は user-facing skill を 2 つに分けた既存契約。
- [Issue Implementation Loop Context Policy Spec](issue-implementation-loop-context-policy-spec.md) は `issue-implementation-loop` の context policy 契約。
- [Grill To PR Loop Branch Policy Spec](grill-to-pr-loop-branch-policy-spec.md) は branch / worktree / commit policy 契約。
- [Grill To PR Loop Epic Base Lifecycle Hardening Spec](grill-to-pr-loop-epic-base-lifecycle-hardening-spec.md) は `epic_base` lifecycle hardening 契約。

## 出典

- [skills/grill-to-pr-loop/SKILL.md](../../../skills/grill-to-pr-loop/SKILL.md)
- [skills/grill-to-pr-loop/references/workflow-contract.md](../../../skills/grill-to-pr-loop/references/workflow-contract.md)
- [skills/grill-to-pr-loop/scripts/check_prereqs.py](../../../skills/grill-to-pr-loop/scripts/check_prereqs.py)
- [skills/issue-implementation-loop/SKILL.md](../../../skills/issue-implementation-loop/SKILL.md)
- [skills/issue-implementation-loop/scripts/_common.py](../../../skills/issue-implementation-loop/scripts/_common.py)
- [skills/issue-implementation-loop/tests/test_issue_implementation_loop.py](../../../skills/issue-implementation-loop/tests/test_issue_implementation_loop.py)
