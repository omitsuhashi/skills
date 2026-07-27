# Planning Authority Policy Issue 台帳

## Epic

- `Epic ID`: `planning-authority-policy`
- `仕様`: [Planning Authority Policy 仕様](spec.md)
- `仕様 SHA-256`: `6f4a952f35dd44fb930af98403ddfe5f0760af1d398722b338a18ef4493f8c68`
- `Spec Gate commit`: `ea0d1be65e75e1ed37930062f5ff213d416c349c`
- `リモート方針`: `local_only`
- `planning branch`: `codex/planning-authority-policy/planning`
- `planning base SHA`: `f5d151e34de5089d75be68249e09da8a2d14f282`

## 台帳

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| planning-authority-policy | PAP-001 | planning authority family policy と validator を追加する | 承認済み | 実行可能 | なし | PAP-002 | 未作成 | 未実施 | 未作成 |
| planning-authority-policy | PAP-002 | main planning / supporting agent の運用契約を追加する | 承認済み | ブロック中 | PAP-001 | PAP-003 | 未作成 | 未実施 | 未作成 |
| planning-authority-policy | PAP-003 | model非永続化と既存execution契約の回帰防止を追加する | 承認済み | ブロック中 | PAP-002 | PAP-004 | 未作成 | 未実施 | 未作成 |
| planning-authority-policy | PAP-004 | wiki同期と全体verificationを完了する | 承認済み | ブロック中 | PAP-003 | なし | 未作成 | 未実施 | 未作成 |

## Blocker graph

```text
PAP-001 -> PAP-002 -> PAP-003 -> PAP-004
```

cycle はない。Issue Gate 承認時点で実行可能なのは `PAP-001` だけとする。blocked issue は dependency を packet に保持し、blocker release 前にworkerへ渡さない。

## PAP-001 planning authority family policy と validator を追加する

- `実行状態`: `実行可能`
- `ブロック元`: `なし`
- `ブロック先`: `PAP-002`
- `write scope`:
  - `path:skill-architecture.toml`
  - `path:scripts/validate_skill_architecture.py`
  - `path:scripts/test_validate_skill_architecture.py`
- `受け入れ条件`:
  - `skill-architecture.toml` が `repository-change-loop.planning_authority` table と承認済み5項目を持つ。
  - validator がtable欠落、必須field欠落、未定義field、不正値を拒否する。
  - validator のsmall TOML parserは既存schema versionとPython 3.9互換を維持する。
  - existing `user_facing_skills`、`internal_components`、`context_compaction` validationを弱めない。
- `非目標`:
  - model name、reasoning level、host固有agent IDをpolicyへ追加しない。
  - standalone model router / skillを作らない。
- `検証`:
  - `python3 -m unittest discover -s scripts -p "test_validate_skill_architecture.py"`
  - `python3 scripts/validate_skill_architecture.py --all`
  - `git diff --check`

## PAP-002 main planning / supporting agent の運用契約を追加する

- `実行状態`: `ブロック中`
- `ブロック元`: `PAP-001`
- `ブロック先`: `PAP-003`
- `write scope`:
  - `path:skills/grill-to-pr-loop/SKILL.md`
  - `path:skills/grill-to-pr-loop/references/planning-contract.md`
  - `path:skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py`
- `受け入れ条件`:
  - entrypointが`main_planning_context`をintegration owner、supporting agentを`advisory_only`、Humanをdecision authorityとして短く示す。
  - planning contractがsupporting agentの`read_only` access、bounded question / read paths、evidence return、scope change禁止を説明する。
  - conflicting advisory resultを多数決にせず、main contextがevidenceを比較する。
  - unresolved authority-bearing ambiguityをHuman gateへ送る。
  - context compaction後のfresh primary contextへの明示的ownership transferをsupporting dispatchと区別する。
- `非目標`:
  - supporting agentへcanonical planning artifactのwrite権限を与えない。
  - supporting agentへspec approval、scope approval、packet sealを委譲しない。
- `検証`:
  - `python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
  - `python3 scripts/validate_skill_context.py --skill skills/grill-to-pr-loop`
  - `python3 scripts/report_skill_context.py --skill skills/grill-to-pr-loop --json`
  - `git diff --check`

## PAP-003 model非永続化と既存execution契約の回帰防止を追加する

- `実行状態`: `ブロック中`
- `ブロック元`: `PAP-002`
- `ブロック先`: `PAP-004`
- `write scope`:
  - `path:skills/grill-to-pr-loop/tests/test_planning_authority_policy.py`
- `受け入れ条件`:
  - focused regressionが`model_selection = "host_runtime"`と`model_persistence = "forbidden"`を固定する。
  - Input Packet、Execution Envelope、Worker Packetのclosed schemaが`model`、`model_name`、`model_reasoning_effort`、`reasoning_level`、`intelligence_level`を新規fieldとして受け入れないことを確認する。
  - user-selected model changeまたはmodel unavailableをspec / packet driftとして扱う文言がないことを確認する。
  - `issue-implementation-loop`のworker-only、fresh / compacted coordinator、`main_planning_session_may_implement=false`契約が不変である。
  - productionのInput Packet / Execution Envelope / Worker Packet schema、validator、schedulerは編集しない。
- `非目標`:
  - host runtimeの実効modelをtestから観測しない。
  - model availability、cost、latency、qualityをrepo testへ持ち込まない。
- `検証`:
  - `python3 -m unittest discover -s skills/grill-to-pr-loop/tests -p "test_planning_authority_policy.py"`
  - `python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
  - `python3 -m unittest discover -s skills/issue-implementation-loop/tests`
  - `git diff --check`

## PAP-004 wiki同期と全体verificationを完了する

- `実行状態`: `ブロック中`
- `ブロック元`: `PAP-003`
- `ブロック先`: `なし`
- `write scope`:
  - `path:knowledge/wiki/syntheses/planning-authority-policy`
  - `path:knowledge/index.md`
  - `path:knowledge/log.md`
- `受け入れ条件`:
  - spec、Issue台帳、Implementation Plan、Input Packet、実装結果のstatus / evidenceが一致する。
  - `knowledge/index.md`からcurrent canonical artifactを発見できる。
  - `knowledge/log.md`がSpec Gate、Issue Gate、Execution Plan Gate、implementation / review closeoutを追跡できる。
  - relevant regression、architecture / context / dual-host / skill validator、`git diff --check`が通る。
  - default checkoutのHEAD / statusがplanning開始時snapshotと一致する。
- `非目標`:
  - GitHub issue、push、PR、merge、release、live installを行わない。
- `検証`:
  - `python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
  - `python3 -m unittest discover -s skills/issue-implementation-loop/tests`
  - `python3 -m unittest discover -s skills/llm-wiki/tests`
  - `python3 -m unittest discover -s scripts`
  - `python3 scripts/validate_skill_architecture.py --all`
  - `python3 scripts/validate_skill_context.py --all`
  - `python3 scripts/report_skill_context.py --all --json`
  - `python3 scripts/validate_dual_host_compatibility.py --skill skills/grill-to-pr-loop`
  - `python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop`
  - `git diff --check`

## Issue Gate 判断

- `decision`: `approved`
- `actor`: `session-user`
- `approved at`: `2026-07-27T09:43:11+09:00`
- `scope`: PAP-001からPAP-004のdependency、write scope、acceptance criteria、non-goals、verification。
- `remote action`: なし。

## Execution Plan Gate

- `decision`: `auto-continue`
- `decided at`: `2026-07-27T09:50:50+09:00`
- `implementation plan`: [Planning Authority Policy 実装計画](implementation-plan.md)
- `normalized packet`: [Input Packet v2](input-packet.json)
- `packet SHA-256`: `90b22e13c1a91abcee126fd05345941d91d0671c60cb6ec03774005c5c90b9d5`
- `packet validation`: `ok: true`
- `capability preflight`: `ok: true`
- `scope / dependency`: Issue Gate承認内容から変更なし。`PAP-001 -> PAP-002 -> PAP-003 -> PAP-004`。
- `execution boundary`: fresh / compacted coordinatorとworker contextが必須。planning/grill sessionは実装しない。
- `remote policy`: `local_only`、remote actionなし。

## 関連ページ

- [Planning Authority Policy 仕様](spec.md)
- [Planning Authority Policy 実装計画](implementation-plan.md)
- [Input Packet v2](input-packet.json)
- [Loop Skill Codex 最適化仕様](../loop-skill-codex-optimization-spec.md)
- [Loop Skill Context Optimization Spec](../loop-skill-context-optimization-spec.md)
