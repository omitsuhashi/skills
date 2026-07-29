# Research Stage

Load this reference only for a change request, incomplete specification, or a
material conflict that requires repository evidence.

## Dispatch

Create an isolated fresh-context Research Worker using
`prompts/repository-researcher.md`. Do not inherit the parent conversation. Pass
only:

- repository root and current baseline commit;
- epic ID and current research question;
- applicable repository and knowledge constraints;
- current spec path when one exists;
- report path under `.superpowers/research/<epic-id>/`.

Required isolated dispatch and explicit-model capability are fail-closed. If
they are unavailable, return `BLOCKED`. Do not fall back to Planning Controller
exploration or artifact authoring.

## Worker Scope

The Research Worker may inspect the minimum relevant repository structure,
source code, documentation, tests, validators, git history, and existing
knowledge. When a relevant knowledge root exists, it follows the `llm-wiki`
query contract. It separates confirmed facts, material conflicts, and unknowns,
and cites repository-relative paths and line ranges.

The worker does not make design decisions, approve scope, accept risk, or decide
the final Human question.

## Research Report

Write detailed evidence to the supplied path under
`.superpowers/research/<epic-id>/`. This directory is gitignored transient
evidence. Do not add the report to the wiki, Git, `knowledge/index.md`, or
`knowledge/log.md`.

Return only the Control Return defined in `planning-context.md`. The Planning
Controller reads the Control Return, not the report body. For a current material
decision, the worker may provide a short evidence excerpt or a dedicated excerpt
path.

## Decision Handoff

The Planning Controller compares the current Decision Record excerpt with the
Control Return. It asks the Human one unresolved material decision through
`grill-with-docs`. A confirmed decision remains closed unless new repository
evidence creates a material conflict.
