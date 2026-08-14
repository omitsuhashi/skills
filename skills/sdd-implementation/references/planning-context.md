# Planning Context

Load this reference only after input maturity selects a pre-implementation
decision, synthesis, review, or plan-authoring stage.

Apply the `SKILL.md` Common Runtime Capability Guard before every worker
dispatch and affected mutation. This reference adds only planning-stage inputs,
routing, and results; it does not redefine capability, model, path, worktree, or
failure checks.

## Controller Ownership

The Planning Controller owns Human dialogue, the current material decision,
small updates to the Decision Record, approval state, stage routing, Control
Return evaluation, and the next Stage Capsule. It does not own repository
exploration, full artifact synthesis, review, or implementation.

## Read Boundary

Allowed direct reads:

- applicable skill instructions and repository `AGENTS.md`;
- repository root, branch, worktree, and status metadata;
- writer ownership and original preservation evidence;
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

## Spec Synthesis And Review

After all material decisions are confirmed, dispatch a fresh Spec Synthesis
Worker with research report paths, the `Confirmed Decisions` and `Open
Decisions` excerpts, the current spec draft path, and applicable authoring
rules. Do not inherit the parent conversation.

Then dispatch a separate fresh Spec Reviewer with the durable spec path,
repository-external Research Report paths, Decision Record excerpts, and a raw
review artifact path using the repository-external task/session temporary
route. The reviewer is advisory-only. Integrate only its durable verdict
summary into the canonical specification. The Human must approve the Written
Spec before Plan Stage.

## Plan Authoring

For a Human-approved current specification, dispatch a fresh Plan Author Worker.
Apply the `SKILL.md` Common Runtime Capability Guard before authoring.
Do not inherit the parent conversation. In addition to the Common Runtime
Capability Guard inputs, pass only the writable plan artifact path, baseline
commit, approved spec path, applicable repository rules, current
`superpowers:writing-plans` skill path, and local overlay path
`references/plan-contract.md`.

The worker maps current files and tests, writes an executable TDD plan, performs
the upstream author self-review, and returns only a Control Return. After that
return, dispatch a fresh independent Plan Reviewer using
`prompts/plan-reviewer.md`; do not inherit the author context. Pass the approved
spec path, trusted bounded paths, a raw review path using the repository-external
task/session temporary route, local overlay path, authored plan path, Plan
Author result, and current-tree evidence required for buildability review.
Apply the Common Runtime Capability Guard and Keep Implementation Simple Wiring.
Integrate only the durable verdict summary into the reviewed implementation
plan; do not copy the raw review artifact or transcript.

Local override: skip the upstream `superpowers:writing-plans`
`## Execution Handoff`. Do not offer Subagent-Driven or Inline Execution. Do
not ask the Human which execution approach to use. After independent review,
reviewed `ready` deterministically enters the Implementation Stage through
`superpowers:subagent-driven-development`.

The Planning Controller evaluates only the Plan Author Control Return, Plan
Reviewer verdict and disposition, plan path, spec binding, and readiness
disposition. A review verdict of `ready` maps to the existing Control Return `status: complete`
and permits Implementation Stage entry. Classify `issues_found`
deterministically: `needs_repair` for agent-repairable plan deficiencies,
`needs_decision` only for an evidenced material spec conflict, and `blocked` for
a non-decision capability, trust, path, or evidence blocker.
It does not repeat repository file mapping or code exploration.

`needs_repair` remains inside the agent-owned Plan Stage: dispatch a fresh Plan
Author with the review artifact and then a fresh independent Plan Reviewer.
Return only an evidenced material spec conflict as one Human decision request.
Do not make missing remote publication authorization a plan blocker; remote
authorization is evaluated only when the later remote action is requested.

## Failure Boundary

Apply the Common Runtime Capability Guard and its four-field blocked diagnosis
before affected work. A failure performs no authoring and does not move work to
the Planning Controller, another workspace, or another workflow. Do not add a
fallback matrix, retry scheduler, runtime state, packet schema, context
telemetry, manual compaction, or strict word-count enforcement.
