# Issue Implementation Loop Common Lib Split Spec

## 目的

`issue-implementation-loop` の実行契約を変えずに、`scripts/_common.py` と単一巨大 test file に集まった責務を internal common lib へ分割する。目的は、後続の実装・レビュー時に必要な文脈を mode / domain ごとに小さく読み込めるようにし、検証対象の境界を明確にすること。

この spec は、[Loop Skill Context Optimization Spec](loop-skill-context-optimization-spec.md) で「後続 slice」とされた `_common.py` lib 分割と tests 分割を、実装可能なローカル issue 群へ落とすための draft である。

## Epic ID

`issue-implementation-loop-common-lib-split`

## 現状

- `grill-to-pr-loop` は router 化済みで、`SKILL.md` は 134 lines、`references/workflow-contract.md` は 45 lines まで縮小されている。
- `issue-implementation-loop/SKILL.md` は mode router と required rules に絞られている。
- `issue-implementation-loop/scripts/_common.py` は 876 lines で、以下が混在している。
  - JSON I/O、ID / SHA / branch utility、review approval 判定
  - input packet / execution envelope / runtime state / worker report / delivery plan validation
  - dependency graph、human wait、write-scope conflict、scheduler
  - git helper、skill discovery
- `issue-implementation-loop/tests/test_issue_implementation_loop.py` は 1396 lines で、entrypoint budget、skill discovery、validation、runtime rebuild、git reconcile、delivery、scheduler の tests が 1 file に集中している。
- 既存 CLI は `from _common import ...` に依存しているため、一気に import surface を変えると検証 blast radius が大きい。

## ベストな状態

- User-facing skill は引き続き `grill-to-pr-loop` と `issue-implementation-loop` の 2 つだけにする。
- 新しい user-facing skill、`execution-envelope` skill、standalone scheduler skill は作らない。
- Internal library を `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/` に置く。
- `_common.py` は backward-compatible facade として残し、既存 CLI と tests の import を壊さない。最終状態では `_common.py` は re-export と import bootstrap だけを持ち、実装本体を持たない。
- Module boundaries は次を基本形にする。
  - `constants.py`: enum-like constants と regex
  - `io.py`: `load_json`, `dump_json`
  - `identifiers.py`: epic / issue / SHA / commit range / canonical branch utilities
  - `review.py`: review approval / human risk acceptance 判定
  - `validation/input_packet.py`
  - `validation/execution_envelope.py`
  - `validation/runtime_state.py`
  - `validation/worker_report.py`
  - `validation/delivery_plan.py`
  - `graph.py`: dependency cycle / descendants / dependency satisfaction
  - `scheduler.py`: next-actions, human wait, write-scope conflict
  - `git_state.py`: local git helper
  - `skill_discovery.py`: repo-local-first skill root discovery
- Tests は behavior domain ごとに分ける。
  - `test_entrypoint.py`
  - `test_skill_discovery.py`
  - `test_validation.py`
  - `test_runtime_state.py`
  - `test_delivery.py`
  - `test_scheduler.py`
  - `test_git_reconcile.py`
- Public scripts の CLI output、exit code、schema compatibility は変えない。

## 受け入れた判断

- これは behavior-preserving refactor として扱う。validator / scheduler / delivery の仕様変更は入れない。
- `_common.py` は削除しない。既存 script import を守る facade として残す。
- Internal package は `scripts/lib/issue_implementation_loop/` に置く。repo 外 installable package にはしない。
- Test split は lib split と同じ epic で行う。実装本体だけを分けて tests を単一 file に残すと、次回以降の context 最適化効果が小さいため。
- 実装は TDD で進める。各 slice は先に import compatibility / CLI compatibility / behavior regression test を赤にしてから、最小移動で通す。
- `knowledge/wiki/syntheses/loop-skill-context-optimization-*` は過去の first slice evidence として残し、この follow-up は新 Epic ID で扱う。
- 2026-06-25 に spec / issue / packet は user approval 済み。実装は `local_only` で行い、GitHub issue / PR / push / merge は行わない。

## 実装範囲

1. `scripts/lib/issue_implementation_loop/` を作り、package import と `_common.py` facade の互換性を確立する。
2. validation 系関数を domain module へ移す。
3. dependency graph / scheduler / human wait / write-scope conflict を domain module へ移す。
4. delivery / runtime-facing helper / git / skill discovery を domain module へ移し、CLI compatibility を維持する。
5. tests を behavior domain ごとに分割し、旧 monolithic test file を縮小または廃止する。
6. `knowledge/index.md` / `knowledge/log.md` / local ledger に implementation state と検証結果を反映する。

## 今回やらないこと

- 新しい user-facing skill の追加。
- `issue-implementation-loop` の execution semantics、scheduler semantics、runtime schema、delivery policy の変更。
- GitHub issue 作成、push、PR 作成、merge、remote write。
- package install metadata、PyPI 化、外部 dependency 追加。
- `grill-to-pr-loop` の再分割。ただし関連 docs の参照更新は必要に応じて行う。

## Issue 分割方針

- G2PR-001: lib package と `_common.py` facade を作り、import / skill discovery / git helper の互換性を固定する。
- G2PR-002: input / envelope / runtime / worker / delivery validation を module 化する。
- G2PR-003: dependency graph / scheduler / human wait / write-scope conflict を module 化する。
- G2PR-004: delivery-facing helper、runtime / reconcile script の import surface、CLI compatibility を仕上げる。
- G2PR-005: tests を behavior domain ごとに分割し、wiki ledger と verification evidence を更新する。

G2PR-001 を最初に置く。G2PR-002 以降は `_common.py` facade と tests に触るため、原則 sequential に実行する。

## Acceptance Criteria

- `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/` が存在し、domain module へ責務が分割されている。
- `_common.py` は backward-compatible facade として残り、既存 public scripts が同じ CLI で動く。
- `_common.py` は validation / scheduler / delivery の実装本体を持たない。
- 既存 public scripts の出力 contract が変わらない。
- `validate_input_packet.py`, `validate_execution_envelope.py`, `validate_runtime_state.py`, `validate_worker_report.py`, `validate_delivery_plan.py`, `compute_next_actions.py`, `check_capabilities.py`, `reconcile_git_state.py`, `rebuild_runtime_state.py` の regression tests が通る。
- tests が behavior domain ごとの file に分かれ、単一 test file に全契約が集中しない。
- repo-local skill root 優先の regression が維持される。
- `issue-implementation-loop/SKILL.md` の entrypoint budget と trigger-only description contract が維持される。
- `git diff --check` が通る。

## 検証コマンド

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_input_packet.py knowledge/wiki/syntheses/issue-implementation-loop-common-lib-split-input-packet.json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/check_capabilities.py --input knowledge/wiki/syntheses/issue-implementation-loop-common-lib-split-input-packet.json --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase execution --json
git diff --check
```

`quick_validate.py` は PyYAML が必要なため、dependency cache がない環境では未検証として記録する。使用できる場合は以下も実行する。

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
```

## Remote Write Policy

`local_only`。GitHub issue / PR / push / merge は未承認であり、現在の `gh` auth も optional failure なので実行しない。

## Human Review Gates

- Spec Gate: この spec の承認。
- Issue Gate: [Issue Ledger](issue-implementation-loop-common-lib-split-issues.md) の粒度・依存関係・acceptance criteria の承認。
- Execution Plan Gate: [Input Packet](issue-implementation-loop-common-lib-split-input-packet.json) と remote policy の承認。
- Implementation Review Gate: 各 issue completion / blocker release / PR_READY の前に issue-scoped implementation review を実施する。

## Stop Conditions

- `_common.py` facade を維持できず、既存 CLI import を破る必要が出た場合。
- validator / scheduler / delivery behavior を変更しないと tests が通らない場合。
- module split によって circular import が生じ、境界の再設計が必要になった場合。
- repo-local skill root 優先が失われる場合。
- test split が既存 coverage を落とす場合。
- remote write が必要になった場合。

## リスク

- `_common.py` が多責務なため、単純移動だけでも import cycle を作りやすい。
- `scripts/lib` は public script 実行時の `sys.path` に自動では入らないため、facade または bootstrap の設計を固定する必要がある。
- tests 分割を後回しにすると、lib split の context 最適化効果が小さくなる。
- behavior-preserving refactor 中に既存仕様のバグを見つけた場合、同じ epic で直すか別 follow-up に切るかの判断が必要になる。

## 関連ページ

- [Loop Skill Context Optimization Spec](loop-skill-context-optimization-spec.md)
- [Issue Implementation Loop Context Policy Spec](issue-implementation-loop-context-policy-spec.md)
- [Grill To PR Loop Skill Split V2 Spec](grill-to-pr-loop-skill-split-v2-spec.md)
- [Grill To PR Loop Branch Policy Spec](grill-to-pr-loop-branch-policy-spec.md)
- [Grill To PR Loop Epic Base Delivery Policy Spec](grill-to-pr-loop-epic-base-delivery-policy-spec.md)

## 出典

- [skills/issue-implementation-loop/SKILL.md](../../../skills/issue-implementation-loop/SKILL.md)
- [skills/issue-implementation-loop/scripts/_common.py](../../../skills/issue-implementation-loop/scripts/_common.py)
- [skills/issue-implementation-loop/tests/test_issue_implementation_loop.py](../../../skills/issue-implementation-loop/tests/test_issue_implementation_loop.py)
- [skills/issue-implementation-loop/scripts/check_capabilities.py](../../../skills/issue-implementation-loop/scripts/check_capabilities.py)
- [skills/issue-implementation-loop/scripts/compute_next_actions.py](../../../skills/issue-implementation-loop/scripts/compute_next_actions.py)
- [skills/issue-implementation-loop/scripts/validate_delivery_plan.py](../../../skills/issue-implementation-loop/scripts/validate_delivery_plan.py)
