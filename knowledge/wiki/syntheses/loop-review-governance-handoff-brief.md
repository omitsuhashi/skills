# Loop Review Governance Handoff Brief

## Purpose

`loop-review-governance` の Execution Plan Gate 後に、planning session の raw discussion や full output に依存せず `issue-implementation-loop` を開始するための bounded handoff brief。正本は spec、issue ledger、input packet、Execution Envelope、runtime state、events であり、この brief は cache として扱う。

## Canonical Artifacts

- Spec: `knowledge/wiki/syntheses/loop-review-governance-spec.md`
- Issue ledger: `knowledge/wiki/syntheses/loop-review-governance-issues.md`
- Input packet: `knowledge/wiki/syntheses/loop-review-governance-input-packet.json`
- Execution Envelope: `knowledge/wiki/syntheses/loop-review-governance-execution-envelope.json`
- Runtime root: `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-review-governance`

## Carry-Forward Capsule

- Gate state: Spec Gate、Issue Gate、Execution Plan Gate は承認済み。draft final PR 作成のみ承認済み。
- Execution policy: `worker_context_required=true`、`coordinator_may_implement=false`、`serial_fallback_mode=worker_context_only`。
- Review policy: `requesting-code-review` を第一候補とし、`max_review_cycles=2`。自動レビュー観点は Issue 意図適合、今回変更による regression、current PR delivery risk の 3 つだけ。`classification_needed` / `hardening_candidate` は必要になった場合または人間が明示した場合だけ扱い、自動修正しない。
- Context policy: paths-first、full spec/ledger paste 禁止、worker packet default 600 words、session compaction は soft 65% / hard 75% / mandatory handoff compaction `1` / phase transition GC required。
- Dependency order: LRG-001 -> LRG-002 -> LRG-003。LRG-004 は LRG-001 / LRG-002 後、LRG-005 は LRG-001 から LRG-004 後。
- Runnable first issue: LRG-001。LRG-002 / LRG-003 / LRG-004 / LRG-005 は blocker release まで reserved。
- Remote actions: branch push と draft final PR 作成のみ承認済み。GitHub issue mirror、ready-for-review、merge、force push、deploy、credential、permission、billing、production、destructive action は未承認。

## Next Operation

Run `issue-implementation-loop prepare` / `execute` from the normalized packet and Execution Envelope. The coordinator may create runtime state and worker packets, but must not implement issue work directly. If worker contexts are unavailable, stop before implementation.

## Do Not Carry Forward

Do not rely on raw chat, full command output, full worker reports, full review reports, diff text, or local implementation trial-and-error. Reload by the paths above when exact evidence is needed.
