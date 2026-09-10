---
summary: 旧loop familyの過去runに関するbounded handoff brief。
knowledge_status: historical
---
# Loop Skill Context Compaction Handoff Brief

## 適用範囲と履歴

旧 grill-to-pr-loop / issue-implementation-loop の設計・実行証跡。[[wiki/syntheses/sdd-implementation-phase2-removal-plan|旧 loop skill の除去記録]] により executable surface / restart entrypoint ではない。本文の current 表現や packet / envelope / baseline は当時の範囲に限り、再実行には新しい承認と run を必要とする。現行の作業境界は repository root の `AGENTS.md` を参照する。

## Purpose

`loop-skill-context-compaction` の Execution Plan Gate 後に、planning session の raw discussion や full output に依存せず `issue-implementation-loop` を再開するための bounded handoff brief。正本は spec、issue ledger、input packet、Execution Envelope、runtime state、events であり、この brief は cache として扱う。

## Canonical Artifacts

- Spec: `knowledge/wiki/syntheses/loop-skill-context-compaction-spec.md`
- Issue ledger: `knowledge/wiki/syntheses/loop-skill-context-compaction-issues.md`
- Input packet: `knowledge/wiki/syntheses/loop-skill-context-compaction-input-packet.json`
- Execution Envelope: `knowledge/wiki/syntheses/loop-skill-context-compaction-execution-envelope.json`
- Runtime root: `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-skill-context-compaction`
- Worker packet for current issue: `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-skill-context-compaction/worker-packets/LSCC-005-dispatch-001.json`

## Carry-Forward Capsule

- Gate state: Spec Gate、Issue Gate、Execution Plan Gate は承認済み。remote policy は `local_only`。
- Execution policy: `worker_context_required=true`、`coordinator_may_implement=false`、`serial_fallback_mode=worker_context_only`。
- Context policy: paths-first、full spec/ledger paste 禁止、session compaction は soft 65% / hard 75% / mandatory handoff compaction `1` / phase transition GC required。
- Verified ranges:
  - LSCC-001: `54cb7a85d1a5882b194e217e6ce5bbc12473f7fb..61f59973bca2eb13417eef05961ef0ecf7215194`, review approved。
  - LSCC-002: `61f59973bca2eb13417eef05961ef0ecf7215194..90f4813f7458dbc0bbbc8712a69d85c78d33ef0d`, review approved。
  - LSCC-003: `90f4813f7458dbc0bbbc8712a69d85c78d33ef0d..b788964b44a575ed554b0a4e05f3317075cd27b4`, review approved。
  - LSCC-004: `b788964b44a575ed554b0a4e05f3317075cd27b4..20f0628c70a1bddef618725ba93f09e9be184fb9`, review approved。
- Current work: LSCC-005 syncs ledger, normalized packet, Execution Envelope, handoff brief, index, and log. It does not perform remote writes.
- Next operation: coordinator-side implementation review for LSCC-005, then blocker/release or local delivery decision under `local_only`.

## Do Not Carry Forward

Do not rely on raw chat, full command output, full worker reports, full review reports, diff text, or local implementation trial-and-error. Reload by the paths above when exact evidence is needed.

## 切替前の補足情報

2026-09-10 の探索方式切替時に旧目録から回収した当時の説明（現行判定は上記の適用範囲を優先する）：

旧loop familyの過去runに関するbounded handoff brief。historical / non-executableであり、再開には使わない。
