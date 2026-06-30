# Loop Skill Context Compaction Issues

## 状態

Issue Gate 承認済み。Spec Gate も承認済み。Execution Plan Gate、実装、GitHub issue mirror、push、PR 作成、merge は未承認。

## Source

- Epic ID: `loop-skill-context-compaction`
- 承認済み spec: [loop-skill-context-compaction-spec.md](loop-skill-context-compaction-spec.md)
- Spec Gate approval commit: `fb731232a37092d8f49f5cd10bdbd7fe28717da9`
- Spec digest: `sha256:a152fb5cc58a6174687980c71727373646254808d7b8aa87e5862b1e638bf426`
- Issue Gate approval: 2026-06-30 user approved this local issue ledger.
- Remote policy: `local_only`

## Phase Transition Capsule

- Current phase result: Issue Gate 承認済み。LSCC-001 から LSCC-005 の粒度、blocker graph、dependency order、acceptance criteria は承認済み。
- Next phase entrypoint: Execution Plan Gate preparation。
- Canonical paths: spec は `knowledge/wiki/syntheses/loop-skill-context-compaction-spec.md`、issue ledger はこの file。
- Open decisions: normalized input packet、write scope、execution dependency graph、fallback policy、remote policy の Execution Plan Gate 承認。
- Pending risk: host transcript の物理削除は保証できず、skill-level operational discard として扱う。

## Local Issue Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loop-skill-context-compaction | LSCC-001 | family-level context compaction policy を追加する | 承認済み | 実行可能 | なし | LSCC-002, LSCC-003, LSCC-004 | 未作成 | 未実施 | 未作成 |
| loop-skill-context-compaction | LSCC-002 | `grill-to-pr-loop` の context compaction contract を追加する | 承認済み | ブロック中 | LSCC-001 | LSCC-004 | 未作成 | 未実施 | 未作成 |
| loop-skill-context-compaction | LSCC-003 | `issue-implementation-loop` の execution compaction contract を追加する | 承認済み | 実装済み | LSCC-001 | LSCC-004 | 未作成 | 未実施 | 未作成 |
| loop-skill-context-compaction | LSCC-004 | session pressure advisory と regression を追加する | 承認済み | ブロック中 | LSCC-001, LSCC-002, LSCC-003 | LSCC-005 | 未作成 | 未実施 | 未作成 |
| loop-skill-context-compaction | LSCC-005 | wiki ledger / packet / verification を仕上げる | 承認済み | ブロック中 | LSCC-004 | なし | 未作成 | 未実施 | 未作成 |

## Blocker Graph

```text
LSCC-001
  -> LSCC-002
  -> LSCC-003
  -> LSCC-004
LSCC-002 -> LSCC-004
LSCC-003 -> LSCC-004
LSCC-004 -> LSCC-005
```

- 実行可能: LSCC-001。
- 実装済み: LSCC-003。実装レビューと blocker release は未実施。
- ブロック中: LSCC-002、LSCC-004、LSCC-005。
- Cyclic blocker: なし。

## LSCC-001: family-level context compaction policy を追加する

### 目的

`repository-change-loop` family に session context compaction policy を追加し、loop family 全体の 65% / 75% / mandatory handoff compaction 契約を machine-readable にする。

### Scope

- `skill-architecture.toml`
- `scripts/validate_skill_architecture.py`
- `scripts/report_skill_context.py`
- scripts tests

### Acceptance Criteria

- `skill-architecture.toml` が `soft_trigger_percent = 65` を持つ。
- `skill-architecture.toml` が `hard_stop_percent = 75` を正確に持つ。
- `mandatory_handoff_compaction = 1` を integer flag として持つ。または boolean 採用時は parser / validator / regression が boolean を明示的に扱う。
- 新しい standalone skill を作らないことが regression で固定される。
- architecture validator が repository-change-loop family の context compaction policy を検証する。

### Non-goals

- user-facing skill の追加。
- session pressure を read-set estimated token count から推定すること。

## LSCC-002: `grill-to-pr-loop` の context compaction contract を追加する

### 目的

Planning / gate owner である `grill-to-pr-loop` に、65% trigger、conditional overlay、keep/drop taxonomy、phase transition GC、planning phase matrix を追加する。

### Scope

- `skills/grill-to-pr-loop/SKILL.md`
- `skills/grill-to-pr-loop/references/context-compaction.md`
- `skills/grill-to-pr-loop/context-contract.toml`
- `skills/grill-to-pr-loop/tests/`

### Acceptance Criteria

- entrypoint から 65% trigger と context compaction reference を発見できる。
- `references/context-compaction.md` が owner 境界つきで「忘れてはいけないこと」「忘れてもいいこと」「圧縮してはいけないこと」を明示する。
- 同 reference が phase transition GC rule と phase 別圧縮 matrix を持つ。
- `context-compaction` operation は current operation の conditional overlay としてだけ使われ、通常 operation read-set には常時含まれない。
- 65% trigger 時も current operation の required references を落とさない。

### Non-goals

- 通常 operation read-set を肥大化させること。
- planning session が issue implementation worker になること。

## LSCC-003: `issue-implementation-loop` の execution compaction contract を追加する

### 目的

Execution owner である `issue-implementation-loop` に、Execution Envelope、runtime state、resume brief、worker packet の compaction 境界と phase transition GC を追加する。

### Scope

- `skills/issue-implementation-loop/SKILL.md`
- `skills/issue-implementation-loop/references/`
- Execution Envelope schema / template / validator
- worker packet validator / tests

### Acceptance Criteria

- `issue-implementation-loop` が Execution Envelope、runtime state、resume brief、worker packet の圧縮境界を明示する。
- `Execution Envelope.context_policy.session_compaction` が schema / template / validator で検証される。
- `context_policy.session_compaction.soft_trigger_percent` は `65` でなければならない。
- `context_policy.session_compaction.hard_stop_percent` は `75` でなければならない。
- prepare / execute / review / resume / deliver の phase exit で carry-forward capsule を作る契約を持つ。
- raw worker JSON、full report、diff 全文、実装試行錯誤は phase exit 後の carry-forward context へ残らない。
- worker packet の strict `context_policy` は session-level field を拒否し続ける。

### Non-goals

- worker packet schema に session-level policy を混ぜること。
- runtime state / scheduler / delivery semantics の意味論を変更すること。

### Implementation Evidence

- 2026-06-30 worker 実装で `skills/issue-implementation-loop/references/context-compaction.md`、entrypoint pointer、`context-contract.toml` の `context-compaction` overlay operation を追加。
- `Execution Envelope.context_policy.session_compaction` を schema / template / Python validator に追加し、`soft_trigger_percent=65`、`hard_stop_percent=75`、handoff compaction、phase transition GC、carry-forward capsule 上限を固定。
- worker packet 側は schema / validator に session-level field を追加せず、`context_policy.session_compaction` を unknown field として拒否する regression を追加。
- Verification: issue-implementation-loop tests、source-revision Execution Envelope validation、worker packet validation、skill context validation、`git diff --check` は OK。
- Packet 記載の relative envelope validation は、この worker worktree に `knowledge/wiki/syntheses/loop-skill-context-compaction-execution-envelope.json` が存在しないため `FileNotFoundError`。当該 artifact は LSCC-005 write scope 側であり、LSCC-003 では編集していない。

## LSCC-004: session pressure advisory と regression を追加する

### 目的

Operator-supplied session pressure advisory と regression tests を追加し、65% trigger、75% hard stop、conditional overlay、phase transition GC が文書だけで終わらないようにする。

### Scope

- `scripts/report_skill_context.py`
- `scripts/test_report_skill_context.py` または関連 scripts tests
- `scripts/validate_skill_context.py` regression
- loop skill entrypoint / context tests

### Acceptance Criteria

- `report_skill_context.py --all --json --session-pressure-percent 65` が `session_context.compaction_required=true` を返す。
- `report_skill_context.py --all --session-pressure-percent 65` の text output は短い advisory 行だけを追加する。
- `report_skill_context.py --all --session-pressure-percent 75 --fail-on-warning` が hard-stop warning と fail-on-warning 挙動を固定する。
- advisory は phase checkpoint / conditional overlay の代替ではないことを regression または contract test で確認できる。
- `validate_skill_context.py --all` は session pressure を扱わず、read-set budget validator のまま通る。
- existing context budget は、通常 operation read-set の headroom minimum を下回らない。

### Non-goals

- `validate_skill_context.py` を session pressure validator にすること。
- non-loop skill に session pressure advisory を広げること。

## LSCC-005: wiki ledger / packet / verification を仕上げる

### 目的

Issue Gate 承認後の execution handoff に向け、local ledger、input packet、Execution Envelope、index/log、verification evidence を整合させる。

### Scope

- この issue ledger
- `knowledge/index.md`
- `knowledge/log.md`
- normalized input packet
- Execution Envelope
- final verification summary

### Acceptance Criteria

- Issue ledger が implementation evidence、review result、verification result を issue ごとに持つ。
- normalized input packet が approved spec / approved ledger / write scope / remote policy を参照する。
- Execution Envelope が `local_only`、worker-only、context compaction policy を含む。
- full verification と implementation review evidence が ledger / log に同期される。
- Spec / Issue / Execution Plan Gate 承認後の commit boundary が維持される。

### Non-goals

- GitHub issue mirror、push、PR 作成、PR ready 化、merge。
- final PR merge。

## Issue Gate 承認対象

- Approval: 2026-06-30 user approved Issue Gate。
- Local issue count: 5。
- Dependency order: LSCC-001 -> LSCC-002 / LSCC-003 -> LSCC-004 -> LSCC-005。
- First runnable issue: LSCC-001。
- Remote policy: `local_only`。
- GitHub issue mirror、push、PR 作成、merge は未承認。

## Verification Plan

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json --session-pressure-percent 65
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --session-pressure-percent 75 --fail-on-warning
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts
git diff --check
```
