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
5. Use `superpowers:requesting-code-review` when available, or an approved equivalent/manual fallback.
6. Send the exact issue review packet and narrow review intent.
7. Fix Critical and Important in-scope findings.
8. Rerun targeted verification and fresh final verification after fixes.
9. Rerun review until approved, retry budget is exhausted, or human accepts risk.
10. Coordinator records review range, verdict, fixed findings, and residual risks.

Manual fallback must be approved before use. PR review, CI checks, later GitHub comments, and uncommitted `working-tree` review ranges do not replace this gate.
