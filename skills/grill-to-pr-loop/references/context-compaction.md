# Context Compaction

Use this reference only when session context pressure reaches `65%`, at a phase transition, or when preparing an implementation handoff. It is a conditional overlay for the current operation, not a replacement operation. Keep the current operation read-set loaded, then add this reference to decide what to carry forward.

`context-contract.toml` remains the operation read-set source of truth. Do not add this file to normal operation references, and do not treat read-set budget metrics as session pressure.

## Owner Boundary

`grill-to-pr-loop` owns planning context: user requirements, accepted decisions, non-goals, `Epic ID`, spec path, issue ledger path, gate approvals, blocker graph, remote policy, and the bounded handoff brief.

`issue-implementation-loop` owns execution context after handoff: normalized packet, Execution Envelope, runtime state, worker packets, worker reports, review ranges, verification, delivery candidates, and resume briefs.

Both owners must preserve approval and safety state for external writes, push, PR creation, merge, credentials, permissions, billing, destructive actions, and human-only final merge.

## 忘れてはいけないこと

Carry these forward in a durable artifact or a bounded capsule:

- Final user requirements, accepted decisions, explicit non-goals, and unresolved questions.
- `Epic ID`, spec path, issue ledger path, packet path, envelope path, runtime root, and source revision or digest.
- Gate approval state, approval target, approval time when known, and any user-approved commit delay.
- Remote policy, unapproved actions, final merge boundary, and other approval constraints.
- Issue ID, acceptance criteria, write scope, blocker graph, dependency order, and stop conditions.
- Branch/worktree reservations, base policy, dirty-overlap decisions, and protected user changes.
- Verification commands and result summary. Long output belongs in a report path, not chat carry-forward.

## 忘れてもいいこと

Drop or summarize these after the decision, result, or path is durable:

- Rejected exploration threads, old wording drafts, stale branch name candidates, and duplicated rationale.
- Full `rg`, `sed`, validator, test, or tool output. Keep only meaningful failures, command names, and result.
- Full spec, full issue ledger, full JSON/TOML/YAML, and full source excerpts when a path and relevant section are enough.
- Diff or patch bodies, resolved review discussion, and local implementation trial-and-error.
- Repeated preflight output when the final command and status are recorded.

## 圧縮してはいけないこと

Do not compress away or omit:

- Open design questions, pending human waits, or risk acceptance requests.
- Acceptance criteria, write scope, dependencies, stop conditions, or blocker release conditions.
- Approval boundaries for remote write, merge, credentials, permissions, billing, destructive actions, and production operations.
- Review finding severity, scope, required fix, unresolved status, or accepted residual risk.
- Source revision, digest, branch, commit, path, command, and runtime event ordering.
- Secrets or personal data. Redact values if needed, but keep the approval state and required handling boundary.

## Phase Transition Context GC

Run this GC at every phase exit, even below `65%`. This is an operational discard rule, not a promise that the host deletes transcript text.

1. Confirm the phase result is saved in a canonical artifact: spec, issue ledger, normalized packet, Execution Envelope, runtime state, event log, worker report, review report, resume brief, or completion report.
2. Create a carry-forward capsule containing only current phase result, next phase entrypoint, canonical paths, revision or digest, open decisions, approval state, pending risk, and verification summary.
3. Keep the capsule under 400 words by default and 600 words hard maximum. Inline JSON, code, or diff snippets must stay under 80 total lines.
4. Drop raw discussion, raw JSON, full command output, full diff or patch, rejected branches, stale drafts, and local implementation attempts.
5. Resume the next phase from the capsule plus canonical paths. Re-read durable artifacts by path and digest instead of relying on chat memory.

## Phase 別圧縮 matrix

| Phase | Trigger | Allowed compaction | Canonical carry-forward |
| --- | --- | --- | --- |
| Intake / Applicability | `>=65%` or unclear loop fit | Summarize user need, assumptions, and open questions; exit loop if the task is small | spec draft or short chat summary |
| Grill / Design | `>=65%` or several unresolved choices | Split Q&A into accepted decisions, rejected alternatives, and open questions | spec `採用した判断`, `非目標`, `停止条件` |
| Spec Gate | before gate presentation or `>=65%` | Present path, `Epic ID`, key decisions, AC, verification, and remote policy | spec path, digest, index/log |
| Issue Gate | before gate presentation or `>=65%` | Compress rationale into issue acceptance, non-goals, and blocker graph | local issue ledger |
| Execution Plan Gate | always before handoff | Use normalized packet plus bounded handoff brief; do not paste full spec or ledger | packet, handoff brief, ledger/log |
| Completion Report | before reporting | Summarize status, verification, review, remote actions, and residual risks | completion report, ledger, index/log |
| Delivery / Remote Gate | before external write | Present exact action set and approval state only | local ledger and delivery record |

At `65%`, add this reference as a conditional overlay to the current operation. The current operation's required references stay in context; this file only decides what can be compacted before continuing.
