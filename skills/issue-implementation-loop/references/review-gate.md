# Issue Implementation Review Gate

Run after fresh final verification, before issue completion, blocker release, or PR readiness.

## Scope

Review only approved issue, spec/requirements, acceptance criteria, non-goals, write scope, and verification evidence.

Ignore quality/architecture/style/performance/refactor/docs suggestions unless they prove a source artifact is unmet.

## Finding Taxonomy

Classify before deciding whether a finding enters a fix loop:

| Classification | Meaning | Action |
| --- | --- | --- |
| `intent_gap` | Approved source artifact is unmet. | blocking finding |
| `implementation_regression` | Branch breaks existing behavior, contract, data shape, or verification. | blocking finding when in scope/caused here |
| `hardening_candidate` | Explicit human-requested hardening or current-PR delivery-risk decision. | candidate only; do not auto-fix |
| `safety_escalation` | Security, credential, permission, destructive, production, data-loss, or high-risk delivery concern. | human decision; do not auto-fix |
| `classification_needed` | Evidence is insufficient to classify. | coordinator or human classification decision; do not auto-fix |

`intent_gap / implementation_regression` use the existing fix loop: fix Critical/Important in-scope findings, rerun verification, refresh the scoped commit, and re-review within two cycles.

hardening_candidate is not a fix request. Do not spend a fix cycle on it or auto-fix it unless approved scope expands.

Future-only hardening suggestions are out of review scope by default. Do not ask the reviewer to enumerate general hardening ideas such as "this could be more robust later" when the approved issue is already satisfied. Record a `hardening_candidate` only when explicitly requested by the human or tied to current PR delivery risk; otherwise omit it from the review report and registry.

classification_needed stops the issue until the coordinator or human classification decision is recorded. Do not guess.

## Reviewer Packet Contract

Use `superpowers:requesting-code-review` as the first candidate. If unavailable, use only an approved equivalent/manual fallback; do not skip the gate.

Review committed changes only. Set `BASE_SHA` / `HEAD_SHA` from envelope/worktree map and issue head, then request a `BASE_SHA..HEAD_SHA` committed range review. Uncommitted `working-tree` review does not satisfy this gate.

Keep the packet paths-first. Include durable paths for issue/spec/ledger, worker report, changed files, and verification evidence; use short excerpts only. Do not paste full spec. Do not paste full ledger. Do not paste full diff or transcript. Keep near default 600 words with hard 900 words ceiling.

Use this narrow reviewer output:

1. **Issue intent review lane**: required lane. Review approved issue, spec, acceptance, non-goals, write scope, and verification evidence. Classify gaps as `intent_gap`, `implementation_regression`, or `classification_needed`.
2. **Escalations**: include only `safety_escalation`, unresolved `classification_needed`, or human-requested/current-delivery `hardening_candidate`. These are not blocker findings or fix requests; do not auto-fix during this cycle.

## Procedure

1. Confirm issue approval/runnable state and scoped worktree.
2. Create/update a scoped commit; set `BASE_SHA` and `HEAD_SHA`.
3. Validate the worker report when present.
4. Use `superpowers:requesting-code-review` or approved fallback.
5. Send the paths-first packet and narrow review intent.
6. Fix Critical/Important in-scope findings, rerun verification, update commit, and re-review until approved, two cycles are exhausted, or human accepts risk.
7. Record `base_sha`, `head_sha`, range, verdict, fixed findings, and residual risks.

If the second review cycle still has Critical or Important in-scope findings, stop and ask the human for a decision instead of starting a third review/fix loop.

Manual fallback must be approved before use. PR review, CI checks, later GitHub comments, and uncommitted `working-tree` ranges do not replace this gate.
