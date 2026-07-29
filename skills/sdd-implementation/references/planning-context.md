# Planning Context

Load this reference only after input maturity selects a pre-implementation
decision, synthesis, review, or plan-authoring stage.

## Controller Ownership

The Planning Controller owns Human dialogue, the current material decision,
small updates to the Decision Record, approval state, stage routing, Control
Return evaluation, and the next Stage Capsule. It does not own repository
exploration, full artifact synthesis, review, or implementation.

## Read Boundary

Allowed direct reads:

- applicable skill instructions and repository `AGENTS.md`;
- repository root, branch, worktree, and status metadata;
- Control Return and Stage Capsule;
- a worker-provided short excerpt for the current decision;
- approval state and canonical artifact paths.

Forbidden direct reads:

- source code;
- broad wiki or documentation pages;
- full specification or full implementation plan;
- git diff, test output, or raw command output;
- multi-file repository exploration.

Pass paths to the responsible fresh worker instead of integrating these sources
inside the Planning Controller.

## Decision Record

Use the planning-worktree specification draft sections `Confirmed Decisions`
and `Open Decisions` as the only Decision Record. Do not create a separate ledger, `CONTEXT.md`, or repo-root `docs/adr/`.

Before asking the Human, read only the worker-provided Decision Record excerpt
for the current question. Do not ask a confirmed question again. Reopen a
confirmed decision only when new repository evidence creates a material
conflict. Present the previous decision, conflicting evidence, and decision
impact together. Ask one material decision at a time through `grill-with-docs`;
workers remain advisory and never approve scope or risk.

## Control Return

Every Pre-Implementation Worker returns exactly these semantic fields:

- `status`: `complete`, `needs_decision`, or `blocked`;
- `artifact_path`: canonical or transient detail path, or `none`;
- `decision_requests`: one material Human decision or `none`;
- `material_risks`: current material conflict, blocker, or `none`.

Keep detailed findings in the artifact. Aim for about 200 words; do not add a word-count validator.

## Stage Capsule

At each stage transition carry only:

- current result;
- canonical paths;
- open decisions;
- approval state;
- material risks.

Aim for about 400 words; do not copy raw discussion or tool output.

## Spec Synthesis And Review

After all material decisions are confirmed, dispatch a fresh Spec Synthesis
Worker with research report paths, the `Confirmed Decisions` and `Open
Decisions` excerpts, the current spec draft path, and applicable authoring
rules. Do not inherit the parent conversation.

Then dispatch a separate fresh Spec Reviewer with the spec path, research paths,
Decision Record excerpts, and review artifact path. The reviewer is
advisory-only. The Human must approve the Written Spec before Plan Stage.

## Plan Authoring

For a Human-approved current specification, dispatch a fresh Plan Author Worker.
Do not inherit the parent conversation. Pass the repository root, baseline
commit, approved spec path, required plan path, applicable repository rules, and
the current `superpowers:writing-plans` skill path. The worker maps current files
and tests, writes an executable TDD plan, performs the upstream plan
self-review, and returns only a Control Return.

The Planning Controller evaluates only the Control Return, plan path, spec
binding, and repository-required approval. It does not repeat repository file
mapping or code exploration. Do not begin Implementation Stage until the plan
is repository-approved.

## Failure Boundary

If isolated fresh-context dispatch is unavailable, return `BLOCKED`. Do not fall back to Planning Controller exploration or artifact authoring. Do not add a
fallback matrix, retry scheduler, runtime state, packet schema, context
telemetry, manual compaction, or strict word-count enforcement.
