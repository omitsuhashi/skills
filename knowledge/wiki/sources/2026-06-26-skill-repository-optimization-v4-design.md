# Skill Repository Optimization V4 Design

## 概要

この source は、PR #19 で loop skill V3 最適化が `main` に入った後の後続設計である。新しい user-facing loop skill は増やさず、`grill-to-pr-loop` と `issue-implementation-loop` の 2 skill 体制を維持したまま、read-set の正本化、context budget の計測精度、worker / reviewer / resume artifact の鮮度管理、CI による context regression 固定へ進める。

## 主要 claim

- `scheduler`、`runtime-state`、`review-gate`、`worker-contract`、`context-manager` は standalone skill にせず、reference / schema / script / internal library として保持する。
- V4 の中心は `context-contract.toml` を operation read-set の唯一の正本にし、`SKILL.md` と `workflow-contract.md` から operation-specific filename の重複管理を外すこと。
- 現在の word count は日本語 context を過小評価し得るため、文字数、非空白文字数、推定 token 数、file count、headroom を併用する budget に移行する。
- `issue-implementation-loop` は `execute.wait` を追加し、`waiting_human` 時に scheduler / worker contract を不要にする。
- Worker Packet V2 は `task_kind`、`access_mode`、`source_revision`、`read_paths.purpose`、root 境界検証、stale packet 拒否を持つ。
- Resume Brief V2 は本文と `resume-brief.meta.json` を分け、envelope revision、runtime revision、last event sequence、source digest で鮮度を判定する。
- `llm-wiki` も複数 mode / references を持つため、機械可読 `context-contract.toml` の適用対象に含める。

## 設計上の境界

- global lifecycle、gate、安全境界は `core.md` に残し、context 削減によって approval / remote policy / stop condition を消さない。
- `workflow-contract.md` は移行期間の deprecated shim として残すが、base read-set から外す。
- reviewer 専用 skill は作らず、worker packet family の `task_kind=review` と `access_mode=read_only` で扱う。
- V1 artifact は resume のために互換維持し、V2 を新規 default にする。

## 実装開始点

source は `SRO4-001: 粒度policy・現状baseline・V4 specの正本化` を開始点として指定している。後続は `SRO4-002` から `SRO4-006` までの dependency graph に沿って進める。

## 関連ページ

- [Skill Repository Optimization V4 Spec](../syntheses/skill-repository-optimization-v4-spec.md) — この source を current checkout に合わせて Spec Gate draft 化した実装契約。
- [Skill Repository Optimization V4 Issues](../syntheses/skill-repository-optimization-v4-issues.md) — V4 実装候補の日本語 local-first issue ledger。
- [Loop Skill Architecture V3 Spec](../syntheses/loop-skill-architecture-v3-spec.md) — PR #19 の前提となる V3 実装契約。
- [Loop Skill Architecture V3 Issues](../syntheses/loop-skill-architecture-v3-issues.md) — V3 実装結果と PR #19 の evidence。

## Open Questions

- `context-contract.toml` V2 の schema を TOML subset parser で維持するか、Python 3.11+ の `tomllib` availability に合わせて分岐するか。
- `skill-architecture.toml` と context contract validator の責務境界をどこで切るか。
- `llm-wiki` の topology × mode contract をどこまで V4 初回 PR に含めるか。

## 出典

- [raw/sources/2026-06-26-skill-repository-optimization-v4-design.md](../../raw/sources/2026-06-26-skill-repository-optimization-v4-design.md)
