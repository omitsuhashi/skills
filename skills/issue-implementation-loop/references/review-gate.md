# Issue Implementation Review Gate

Run after fresh final verification, before issue completion, blocker release, or PR readiness.

## Scope

**Automatic review checks**:

1. **Issue intent fit**: approved issue/spec, acceptance, non-goals, write scope, and verification evidence.
2. **Implementation regression**: caused behavior, contract, data-shape, or verification breakage.
3. **Current PR delivery risk**: security, credential, permission, destructive, production, data-loss, or high-risk delivery concerns.

## Finding Taxonomy

- `intent_gap`: approved artifact is unmet; blocking finding.
- `implementation_regression`: this branch causes a regression; blocking finding when in scope.
- `hardening_candidate`: explicitly requested hardening or current-PR risk decision; candidate only.
- `safety_escalation`: security, permission, destructive, production, data-loss, or high-risk concern; human decision.
- `classification_needed`: evidence is insufficient; coordinator or human decision.

`intent_gap / implementation_regression` use the existing fix loop: fix in-scope Critical/Important findings, verify, refresh the commit, and re-review within two cycles.

hardening_candidate is not a fix request. Do not spend a fix cycle or auto-fix unless approved scope expands.

## Non-automatic handling

classification_needed is not an automatic review viewpoint. classification_needed stops the issue until coordinator or human decision; do not guess.

Hardening is not an automatic review viewpoint. Future-only hardening suggestions are out of review scope by default. Do not ask the reviewer to enumerate general hardening ideas. Record one only when explicitly requested by the human or tied to Current PR delivery risk; otherwise omit it and do not auto-fix.

## Reviewer Packet Contract

Use `superpowers:requesting-code-review` as the first candidate. If unavailable, use only an approved equivalent/manual fallback; never skip the gate.

Review committed changes only. Set `BASE_SHA` / `HEAD_SHA` and request committed range review of `BASE_SHA..HEAD_SHA`; `working-tree` does not satisfy the gate.

Before dispatch and approval intake, require fresh envelope -> packet -> spec verification in the reviewer worktree. Packet, report, Runtime State, and checkout must carry the active `approved_spec_binding`. Approval is valid only for that binding and `BASE_SHA..HEAD_SHA`; reseal, source drift, or a new head invalidates it.

Keep the packet paths-first: issue/spec/ledger, worker report, changed files, and verification evidence paths with short excerpts. Do not paste full spec. Do not paste full ledger, diff, or transcript. Use default 600 words, hard 900 words.

Include `classification_needed` only for insufficient evidence or an explicit classification pass. Include `hardening_candidate` only for explicit human hardening or current-PR risk. Neither is an automatic fix request.

## Procedure

Confirm binding/worktree; commit; set the range; validate the worker report; dispatch a paths-first reviewer packet; validate the review report against the active binding and `BASE_SHA..HEAD_SHA`; then record approval. Fix blocking findings and re-review until approved, two cycles are exhausted, or the human accepts risk. Record range, verdict, fixes, and residual risks.

After cycle two, remaining Critical/Important findings require human decision. Manual fallback must be approved. PR review, CI, GitHub comments, and `working-tree` ranges do not replace this gate.
