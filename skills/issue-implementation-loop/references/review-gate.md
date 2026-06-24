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

## Procedure

1. Confirm issue is approved and runnable, or that an override is recorded.
2. Confirm worktree contains only scoped changes.
3. Create/update a local scoped commit.
4. Set `BASE_SHA` from the envelope/worktree map and `HEAD_SHA` from current issue head.
5. Validate the worker report before review when one exists.
6. Use `superpowers:requesting-code-review` when available, or an approved equivalent/manual fallback.
7. Send the exact issue review packet and narrow review intent.
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
