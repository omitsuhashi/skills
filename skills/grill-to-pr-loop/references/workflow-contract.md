# Grill to PR Loop Workflow Router

Use this reference after loading `grill-to-pr-loop`. This file is a routing layer. Load only the detail references required by the current phase.

Keep execution mechanics delegated to `issue-implementation-loop`; do not duplicate its scheduler, runtime state, recovery, or review/fix loop. End-to-end coordination does not authorize same-session issue implementation.

## Detail References

- Planning, durable artifacts, spec minimum, and approval gates: `planning-contract.md`
- Japanese local issue ledger, blocker graph, and ledger update invariant: `local-issue-ledger.md`
- Execution packet, branch/base/commit policy, and `issue-implementation-loop` handoff: `execution-handoff.md`
- GitHub mirror, issue PRs, final PR, and remote approval policy: `remote-delivery.md`
- Known failure modes and corrections: `common-mistakes.md`

## Read Sets

- `intake`, `grill`, or `spec`: read `planning-contract.md`.
- `local issues` or `issue gate`: read `planning-contract.md` and `local-issue-ledger.md`.
- `execution plan packet` or `execution plan gate`: read `planning-contract.md`, `local-issue-ledger.md`, and `execution-handoff.md`.
- `resume` or `completion report`: read `local-issue-ledger.md` and `execution-handoff.md`; add `remote-delivery.md` only if remote actions were approved or attempted.
- `GitHub mirror`, `issue PR`, `final PR`, or delivery: read `remote-delivery.md`.
- When behavior looks ambiguous, read `common-mistakes.md` before proceeding.

## Sub-Skill Contract

- Use `grill-with-docs` for design interrogation and durable design context.
- Use `to-prd` when the approved conversation/docs should become a PRD or spec packet. Keep local-first unless remote publication is approved.
- Use `to-issues` only for draft vertical-slice breakdown and quiz/review until the GitHub Mirror Gate passes.
- Use `issue-implementation-loop` after local issues and the normalized execution packet are approved.
- Use GitHub/PR specialist workflows only after explicit remote-write approval.

When sub-skills assume remote tracker writes, this workflow's local-first and explicit-approval gates override them.

## Stop If

- `grill-with-docs` is missing.
- `issue-implementation-loop` is missing before execution.
- Dirty repo changes overlap with planned issue write scopes.
- The `Epic ID` is missing, ambiguous, unapproved, or collides with another active epic namespace.
- The local issue blocker graph is cyclic or ambiguous.
- Execution requires changing approved spec, acceptance criteria, issue scope, or write scope.
- Worker contexts are unavailable for implementation; do not degrade into main-session implementation.
- Any external write, credential, permission, billing, production, destructive, push, PR, or merge action is required without approved remote policy.

Final PR merge always requires current human action.
