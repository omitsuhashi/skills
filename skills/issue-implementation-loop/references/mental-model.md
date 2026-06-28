# Role Boundary Mental Model

Use this page before executing an approved issue packet when the coordinator, worker, reviewer, state, ledger, and delivery boundaries are not already clear. It is an orientation page, not an operation read-set file.

## One-Line Flow

`grill-to-pr-loop` creates the approved spec, local ledger, and execution packet. `issue-implementation-loop` turns that packet into local `PR_READY` results by coordinating workers, reviewers, runtime state, and optional remote delivery without letting the coordinator implement issue work.

## Responsibility Boundaries

- **coordinator** owns the approved packet, Execution Envelope, runnable-work decisions, blocker release, human waits, review decisions, status, and final report. It writes coordinator-owned runtime state and shared ledger updates only when the issue contract assigns that responsibility.
- **worker** owns one bounded issue at a time: assigned branch/worktree, write scope, implementation, issue-local tests, verification evidence, and a scoped local commit. A worker must not edit outside its packet or update global runtime state unless explicitly assigned.
- **reviewer** owns implementation review for the assigned issue packet and commit range. It reports Critical, Important, Minor, and residual-risk findings; it does not rewrite scope, perform delivery, or become the worker.
- **runtime state** is coordinator-owned operational memory: event log, mutable snapshot, reservations, human requests, blocker state, review-cycle state, and delivery candidates. Keep it outside tracked issue branches under the configured runtime root.
- **local ledger** is the canonical human-readable issue record. It records approved scope, blocker status, implementation evidence, review outcome, PR-ready state, and any local-only exceptions. Remote systems are mirrors, not the planning source of truth.
- **remote delivery** is optional and gated. Pushes, GitHub issue creation, PR creation, issue PR merge, final PR merge, deployment, destructive actions, credential changes, billing, and permission changes require explicit current approval for the exact action set.

## Operating Rules

- If the coordinator would need to implement, stop or use an approved worker-context fallback.
- If scope changes, return to the approved spec or issue ledger instead of adjusting execution in place.
- If a reviewer finds in-scope Critical or Important issues, fix them in the worker context before blocker release or PR readiness; after the allowed review cycles, ask for human risk acceptance.
- If remote delivery is not approved, finish with local branches, local commits, ledger evidence, and delivery candidates only.
