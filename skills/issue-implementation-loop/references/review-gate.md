# Issue Implementation Review Gate

Run after fresh final verification and before issue completion, blocker release, or PR readiness.

## Scope

Review only for gaps against:

- approved local/remote issue
- requirements/spec
- acceptance criteria
- non-goals
- write scope
- verification evidence

Ignore general code quality, architecture, style, performance, refactor, or documentation suggestions unless they prove a source artifact is unmet.

## Finding Taxonomy

Classify every finding before deciding whether it enters a fix loop:

| Classification | Meaning | Action |
| --- | --- | --- |
| `intent_gap` | Approved issue/spec/acceptance/non-goals/write scope/verification is unmet. | blocking finding |
| `implementation_regression` | The issue branch breaks existing behavior, contract, data shape, or verification. | blocking finding when in scope or caused by the branch |
| `hardening_candidate` | Source artifacts are already satisfied, but defense, validation, maintainability, or design margin could improve. | candidate only; do not auto-fix |
| `safety_escalation` | Security, credential, permission, destructive, production, data-loss, or high-risk delivery concern. | human decision; do not auto-fix |
| `classification_needed` | Evidence is insufficient to classify. | coordinator or human classification decision; do not auto-fix |

`intent_gap / implementation_regression` are blocking finding results and use the existing fix loop: fix Critical and Important in-scope findings, rerun verification, refresh the local scoped commit, and re-review within the two-cycle limit.

hardening_candidate is not a fix request. Do not spend an issue fix cycle on it or auto-fix it in the worker branch unless a later approved issue or envelope revision expands scope.

classification_needed stops the issue until the coordinator or human classification decision is recorded. Do not guess or convert ambiguity into an automatic fix request.

## Reviewer Packet Contract

Use `superpowers:requesting-code-review` as the first candidate for Issue implementation review. If unavailable, use only an approved equivalent/manual fallback; do not silently skip the gate.

Review committed changes only. Set `BASE_SHA` / `HEAD_SHA` from the envelope/worktree map and current issue head, then request a `BASE_SHA..HEAD_SHA` committed range review. Uncommitted `working-tree` review does not satisfy this gate.

Keep the packet paths-first. Include durable paths for issue/spec/ledger section, worker report, changed files, and verification evidence; use short excerpts only. Do not paste full spec. Do not paste full ledger. Do not paste full diff or transcript. Keep the packet near default 600 words with hard 900 words as the ceiling.

Separate the reviewer output into two lanes:

1. **Issue intent review lane**: required lane. Review only approved issue, spec, acceptance, non-goals, write scope, and verification evidence. Classify gaps as `intent_gap`, `implementation_regression`, or `classification_needed`.
2. **Hardening candidate lane**: optional lane. When source artifacts are already satisfied, list bounded proposals as `hardening_candidate`. These are not blocker findings or fix requests; do not auto-fix during this review/fix cycle.

## Procedure

1. Confirm issue is approved and runnable, or that an override is recorded.
2. Confirm worktree contains only scoped changes.
3. Create/update a local scoped commit.
4. Set `BASE_SHA` from the envelope/worktree map and `HEAD_SHA` from current issue head.
5. Validate the worker report before review when one exists.
6. Use `superpowers:requesting-code-review` when available, or an approved equivalent/manual fallback.
7. Send the exact paths-first issue review packet and narrow review intent.
8. Fix Critical and Important in-scope findings.
9. Rerun targeted verification and fresh final verification after fixes.
10. Create/update the local scoped commit after fixes and refresh `HEAD_SHA`.
11. Rerun review until approved, two review cycles are exhausted, or human accepts risk.
12. Coordinator records matching `base_sha`, `head_sha`, review range, verdict, fixed findings, and residual risks.

If the second review cycle still has Critical or Important in-scope findings, stop and ask the human for a decision instead of starting a third review/fix loop.

Manual fallback must be approved before use. PR review, CI checks, later GitHub comments, and uncommitted `working-tree` review ranges do not replace this gate.

Use:

```bash
python3 <skill-dir>/scripts/validate_worker_report.py <worker-report.json>
```
