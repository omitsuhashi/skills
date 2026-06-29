# Core Workflow Context

Load this reference immediately after `grill-to-pr-loop/SKILL.md`. It owns the global context that every operation needs; phase details stay in the other references.

## Lifecycle

Run the workflow as: intake, Grill with Docs, spec/PRD synthesis, Spec Gate, local issue decomposition, Issue Gate, execution packet, Execution Plan Gate, `issue-implementation-loop`, optional remote delivery, completion report. If the user provides an already-approved spec or issue ledger, verify the artifact and continue from the matching gate instead of restarting the lifecycle.

## Responsibilities

`grill-to-pr-loop` owns design interrogation, durable planning artifacts, spec synthesis, Japanese local issue ledger, stable `Epic ID`, normalized execution packet, and final coordination report. `issue-implementation-loop` owns execution envelope, branch/worktree reservation, scheduling, runtime state, worker dispatch, scoped waits, implementation review, recovery, and `PR_READY` results.

Reference ownership is strict: `planning-contract.md` owns artifact and spec minimums, `local-issue-ledger.md` owns ledger format and update invariants, `execution-handoff.md` owns branch/base/packet handoff, `remote-delivery.md` owns GitHub mirror and PR delivery policy, and `common-mistakes.md` owns ambiguity corrections.

## Gates

Use explicit gates before expanding scope: Spec Gate, Issue Gate, Execution Plan Gate, Implementation Review Gate inside `issue-implementation-loop`, and Remote Gate before external writes. Present paths, decisions, acceptance criteria, verification, stop conditions, write scope, dependency order, fallback policy, and local/remote policy as applicable.

After each Spec Gate, Issue Gate, or Execution Plan Gate approval, commit the approved artifacts and ledger/log updates before starting the next phase. Record any user-approved delayed commit as an explicit exception.

Stop if required skills are missing, dirty changes overlap planned write scope, `Epic ID` or blocker graph is ambiguous, approved scope would change, worker contexts are unavailable for implementation, or unresolved Critical/Important findings lack human risk acceptance.

## Local-first

Local durable artifacts are canonical. In this repository, long specs and Goal contracts live under `knowledge/wiki/syntheses/`. Specs/PRDs/ledgers use Japanese headings/labels/status/prose; preserve code symbols, schema keys, paths, commands, branches, IDs, external refs. GitHub issues and PRs are mirrors or delivery records, not the planning source of truth.

Update the local ledger whenever issue publication, implementation review, PR-ready state, PR creation, merge/close state, or completion state changes. Do not report completion while the ledger contradicts execution or remote state.

## Remote approval

Remote writes are optional and require explicit current approval. This includes GitHub issue creation, push, PR creation, ready-for-review changes, issue PR merge, force push, deployment, destructive action, credential, permission, billing, or production changes. GitHub authentication is optional until a Remote Gate is approved. If remote access is unavailable, ask whether to continue local-only. Final PR merge is always human-only.
