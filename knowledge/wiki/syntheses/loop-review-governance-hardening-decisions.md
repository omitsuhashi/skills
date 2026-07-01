# Loop Review Governance Hardening Candidate Decisions

## 状態

Resolved for current draft PR。PR review comment で既存 4 件は current PR に取り込まず `deferred_follow_up` と判断した。

このファイルは `loop-review-governance` の draft final PR 上で、既存 `hardening_candidate` の扱いと、今後の review scope correction を記録する decision artifact です。

## Source

- Runtime registry: `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-review-governance/decisions/hardening-candidates.json`
- Human-readable source: この file と [loop-review-governance-issues.md](loop-review-governance-issues.md) の `Deferred Hardening Follow-ups`
- PR 上の確認面: draft PR [#27](https://github.com/omitsuhashi/skills/pull/27)

## Review Scope Correction

既存 4 件は current PR に取り込まず `deferred_follow_up` とする。

また、今回の 4 件のような「将来的にやった方がいいかも」という future-only hardening を通常レビュー観点から外す。Issue 実装レビューで自動確認する既定 scope は、Issue 意図適合、今回変更による regression、current PR delivery risk の 3 つに限定する。

`classification_needed` と `hardening_candidate` は完全には削除しない。ただし routine review で探させない。必要になった場合、または人間が明示した場合だけ扱う。

## 保存場所と読み方

人間が判断する入口はこの Markdown file です。JSON は runtime / validator が読む machine-readable registry として残し、判断時に直接読む前提にはしない。

- 人間向け判断 file: `knowledge/wiki/syntheses/loop-review-governance-hardening-decisions.md`
- 集約 ledger: `knowledge/wiki/syntheses/loop-review-governance-issues.md`
- machine-readable registry: `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-review-governance/decisions/hardening-candidates.json`

## 出典 / 指している箇所

| Candidate ID | 保存されている場所 | どこで出た指摘か | 何を指しているか |
| --- | --- | --- | --- |
| `HC-LRG-002-001` | runtime registry の `candidates[0]`、この file、issue ledger | `reviews/LRG-002/review-cycle-1.md` の Hardening Candidates | `skills/issue-implementation-loop/scripts/build_resume_brief.py`、`skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/resume_brief.py`、`skills/issue-implementation-loop/tests/test_resume_brief.py` |
| `HC-LRG-003-001` | runtime registry の `candidates[1]`、この file、issue ledger | `reviews/LRG-003/review-cycle-1.md` / `reviews/LRG-003/review-cycle-2.md` で既存 candidate として扱われた。primary details は runtime registry | `skills/issue-implementation-loop/scripts/check_capabilities.py`、worker packet validation 周辺、`skills/issue-implementation-loop/tests` |
| `HC-LRG-003-002` | runtime registry の `candidates[2]`、この file、issue ledger | `reviews/LRG-003/review-cycle-1.md` / `reviews/LRG-003/review-cycle-2.md` で既存 candidate として扱われた。primary details は runtime registry | `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/delivery.py`、`skills/issue-implementation-loop/scripts/validate_delivery_plan.py`、`skills/issue-implementation-loop/references/remote-delivery.md` |
| `HC-LRG-004-001` | runtime registry の `candidates[3]`、この file、issue ledger | `reviews/LRG-004/review-cycle-1.md` の Hardening Candidates | `skills/grill-to-pr-loop/references/execution-handoff.md`、`skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/validation/execution_envelope.py`、`skills/issue-implementation-loop/tests/test_validation.py` |

## 判断対象

| Candidate ID | 人間判断 | 判断理由 |
| --- | --- | --- |
| `HC-LRG-002-001` | `deferred_follow_up` | current PR の Issue 意図適合 / delivery correctness には不要。future-only hardening は通常レビューから外す。 |
| `HC-LRG-003-001` | `deferred_follow_up` | preflight hardening としてはあり得るが、今回 PR の scope では不要。future-only hardening は通常レビューから外す。 |
| `HC-LRG-003-002` | `deferred_follow_up` | local-only completion report validator は独立した後続設計。今回 PR の scope では不要。 |
| `HC-LRG-004-001` | `deferred_follow_up` | 今回の具体的 validator gap は修正済み。汎用 mismatch preflight は後続設計。 |

## PR / Ready / Merge 条件

この 4 件については `pending_decision` を解消済みとして扱う。current PR に追加実装しない。

ready-for-review、merge、force push、deploy、credential、permission、billing、production、destructive action は引き続き未承認。final PR merge は常に human-only。

## 今後のレビュー観点

Issue 実装レビューで reviewer に自動確認させるのは次だけにする。

- Issue 意図 / spec / acceptance criteria / non-goals / write scope / verification evidence が満たされているか
- 今回変更で既存挙動、契約、検証対象を壊していないか
- security、credential、permission、destructive、production、data loss など current PR delivery risk がないか

次は自動レビュー観点ではない。必要になった場合、またはユーザーが明示した場合だけ扱う。

- 分類不能な finding の `classification_needed` 判定
- future-only hardening、一般的な設計余裕、将来の追加検証、保守性改善
