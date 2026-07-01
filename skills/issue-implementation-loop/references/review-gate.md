# Issue Implementation Review Gate

Run after fresh final verification, before issue completion, blocker release, or PR readiness.

## Scope

**Automatic review checks**:

1. **Issue intent fit**: approved issue/spec, acceptance, non-goals, write scope, and verification evidence are satisfied.
2. **Implementation regression**: branch does not break behavior, contract, data shape, or verification.
3. **Current PR delivery risk**: no security, credential, permission, destructive, production, data-loss, or high-risk delivery concern exists.

Ignore quality/architecture/style/performance/refactor/docs suggestions unless they prove a source artifact is unmet.

## Finding Taxonomy

Classify before a finding enters a fix loop:

- `intent_gap`: approved artifact is unmet; blocking finding.
- `implementation_regression`: branch breaks behavior/contract/data/verification; blocking finding when in scope/caused here.
- `hardening_candidate`: human-requested hardening or current-PR delivery-risk decision; candidate only; do not auto-fix.
- `safety_escalation`: security, credential, permission, destructive, production, data-loss, or high-risk delivery concern; human decision; do not auto-fix.
- `classification_needed`: evidence is insufficient to classify; coordinator or human decision; do not auto-fix.

`intent_gap / implementation_regression` use the existing fix loop: fix Critical/Important in-scope findings, rerun verification, refresh the scoped commit, and re-review within two cycles.

hardening_candidate is not a fix request. Do not spend a fix cycle on it or auto-fix it unless approved scope expands.

## Non-automatic handling

classification_needed is not an automatic review viewpoint. Use only for unclassifiable automatic-check findings or an explicit human classification pass.

Hardening is not an automatic review viewpoint. Future-only hardening suggestions are out of review scope by default. Do not ask the reviewer to enumerate general hardening ideas such as "this could be more robust later". Record `hardening_candidate` only when explicitly requested by the human or tied to current PR delivery risk; otherwise omit it.

classification_needed stops the issue until coordinator or human decision. Do not guess.

## Reviewer Packet Contract

Use `superpowers:requesting-code-review` as the first candidate. If unavailable, use only an approved equivalent/manual fallback; do not skip the gate.

Review committed changes only. Set `BASE_SHA` / `HEAD_SHA`, request `BASE_SHA..HEAD_SHA` committed range review. Uncommitted `working-tree` review does not satisfy this gate.

Keep the packet paths-first: issue/spec/ledger, worker report, changed files, and verification evidence paths with short excerpts only. Do not paste full spec. Do not paste full ledger, full diff, or transcript. Use default 600 words, hard 900 words.

Use this narrow reviewer output:

1. **Issue intent fit**: unmet approved artifacts are `intent_gap`.
2. **Implementation regression**: caused regressions are `implementation_regression`.
3. **Current PR delivery risk**: delivery risks are `safety_escalation`.

Include `classification_needed` only when those checks need more evidence or the human requested classification. Include `hardening_candidate` only when hardening was explicitly requested by the human or tied to current PR delivery risk. These are not blocker findings or fix requests; do not auto-fix during this cycle.

## Procedure

Confirm approval/worktree; create scoped commit; set `BASE_SHA`/`HEAD_SHA`; validate worker report; request review; send paths-first packet. Fix in-scope Critical/Important findings, verify, update commit, and re-review until approved, two cycles are exhausted, or human accepts risk. Record range, verdict, fixed findings, and residual risks.

After the second cycle, remaining Critical/Important findings require human decision.

Manual fallback must be approved before use. PR review, CI checks, later GitHub comments, and uncommitted `working-tree` ranges do not replace this gate.
