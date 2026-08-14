# SDD Plan Ownership Alignment Approved Residual Fix Report

## Status

- Result: `APPROVED_RESIDUAL_FIX_COMPLETE`.
- Branch: `codex/sdd-plan-ownership-alignment-planning`.
- Pre-fix tip: `235957b600a4fd8cb3950dd12ad257f05b387121`.
- Scoped behavioral / durable fix commit: `b806631` (`fix: close SDD plan validation residuals`).
- Scope: only the three Human-approved residual Important findings were changed.
- Completion boundary: this report records the fix and verification evidence for controller adjudication; it does not authorize or perform remote publication or live mutation.

## Resolved Findings

### 1. Semantic plan readiness validation

The Plan Contract Overlay, representative ready-plan fixture, canonical implementation plan, and executable validator now use closed semantic states instead of accepting arbitrary non-empty readiness prose:

- `Current-tree compatibility: compatible`;
- `Independent review verdict: ready`;
- `Repository checks: passed`;
- `Readiness evidence state: current`;
- `Plan readiness disposition: ready`;
- `Control Return status: complete`;
- `Implementation Stage entry: allowed`.

The validator rejects non-empty but non-ready values including `incompatible`, `issues_found`, absent repository checks, stale evidence, and `needs_repair`. Existing approval-snapshot validation, baseline ancestry validation, Human-only North Star / Written Spec approval, agent-owned plan readiness / execution, and separate remote authorization remain unchanged.

### 2. Prospective-body false negatives

The executable plan validator now rejects structural, unfenced prospective bodies for:

- multiline and one-line Python production functions;
- multiline JavaScript functions and one-line arrow-function production code;
- shell `if ...; then ... fi` bodies even when the body is not indented;
- `python3 -m unittest` execution commands;
- command-shaped `echo` lines.

Detection uses multiline body structure or line-anchored command syntax rather than keyword presence. Intent-only prose may still name Python / JavaScript syntax, shell-if bodies, unittest, or echo; the regression control includes a prose line beginning with `echo is` and remains accepted.

### 3. Append-only authority evidence correction

`knowledge/log.md` received one append-only `authority-evidence-correction` event. It supersedes, without rewriting, the current-topic `implementation-closeout-candidate` and `final-review-correction` statements that claimed `knowledge/AGENTS.md` declared `Read: allowed`.

The correction records only evidence actually present in `knowledge/AGENTS.md`: the `knowledge/` root, repository maintainer or maintainer-delegated Canonical Owner, `owned` Write Boundary with owner-only direct verified updates, and `obsidian` authoring profile. The undeclared read state is not inferred. The approved product boundary, canonical identities, active index effect, agent-owned plan lifecycle, and remote authorization boundary are unchanged.

## TDD Evidence

### RED

The first new focused run exercised semantic readiness mutations plus the initial production/shell/command probes. It failed for the expected missing behavior:

- the fixture lacked machine-checkable readiness states;
- Python and JavaScript production bodies were accepted;
- a shell-if body was accepted;
- `python3 -m unittest` and `echo` commands were accepted.

The intent-only narrative control passed in that same RED run.

A second adversarial RED cycle added one-line Python, one-line JavaScript arrow syntax, an unindented shell-if body, and prose beginning with `echo is`. It failed in exactly four expected places: three false negatives and one echo-prose false positive.

### GREEN

- The initial five-test behavior group passed after adding semantic states and structural detection.
- The second two-test adversarial group passed after extending one-line / unindented structural handling and narrowing echo detection to command-shaped lines.
- Final focused plan/public contract suite: 48 tests passed; 0 failures; 0 errors.

## Required Combined Verification

The complete required combined gate was run once after the finished five-file behavioral / durable change set.

| Gate | Result |
|---|---|
| SDD implementation suite | 76 tests passed; 0 failures; 0 errors |
| Repository script suite | 19 tests passed; 0 failures; 0 errors |
| LLM Wiki suite | 21 tests passed; 0 failures; 0 errors |
| Skill architecture validator | exit 0; repository-change-loop policy validated |
| Skill context validator | exit 0; 1 contract validated |
| Skill context report | exit 0; 1 skill, 12 operations, warnings `[]` |
| Skill-creator validator | exit 0; `Skill is valid!` |
| Working-tree whitespace gate | exit 0 |
| Staged whitespace gate | exit 0 before the scoped fix commit |

All Python verification used isolated `/private/tmp/sdd-poa-residual-*` bytecode cache roots.

## Changed Scope

The scoped fix commit changed exactly five files:

- `skills/sdd-implementation/tests/test_plan_contract.py`;
- `skills/sdd-implementation/references/plan-contract.md`;
- `skills/sdd-implementation/tests/fixtures/plan-contract/ready-plan.md`;
- `knowledge/wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan.md`;
- `knowledge/log.md`.

No approved Written Spec requirement, `knowledge/index.md`, `knowledge/raw/**`, runtime implementation, remote state, or live installation was changed.

## Concerns And Boundaries

- Open material concern within the approved residual scope: none identified.
- Authority note: `knowledge/AGENTS.md` still does not declare a read state. This fix deliberately corrects the unsupported historical claim without inferring or adding that policy field.
- Remote action: none. No push, PR, merge, release, live install, issue, comment, project write, or other remote mutation was performed.
- Original-checkout preservation is verified separately after the report commit so the final evidence covers the complete local result.

## Approved Residual Fix Loop Round 1

### Status And Commit

- Result: `ROUND_1_FIX_COMPLETE`.
- Independent re-review findings addressed: exactly 2 Important findings.
- Scoped fix commit: `261df06` (`fix: harden SDD plan validator round one`).
- Changed set: executable plan validator/tests, Plan Contract Overlay, and one append-only `knowledge/log.md` review-fix event.

### Singleton Readiness Hardening

The validator now enforces cardinality one for every North Star identity, Written Spec identity, Plan Binding, and closed Readiness Result field. It rejects contradictory duplicates even when the first occurrence is valid. Adversarial regressions cover:

- `Independent review verdict: ready` followed by `issues_found`;
- `Readiness evidence state: current` followed by `stale`;
- `Plan readiness disposition: ready` followed by `issues_found`.

This closes the first-match bypass while retaining the existing exact-value, approval snapshot, contained-path, and baseline-ancestry checks.

### Prospective-Body Hardening

The validator now rejects these remaining production/command structures:

- a Python function whose executable body follows a docstring;
- a one-line JavaScript function body;
- a one-line shell `if ...; then ...; fi` body;
- plain `echo ready`.

Python executable statements use token boundaries, so `return` is not inferred from the prose word `returns`. The exact interface description `def build_plan(spec): returns a normalized plan in the proposed interface.` remains allowed, as do the prior intent-only prose controls.

### TDD Evidence

RED ran three focused tests. The narrative control passed, while seven subcases failed for the expected gaps: three contradictory duplicate declarations and four previously missed body/command forms.

GREEN results:

- targeted representative/canonical/adversarial group: 5 tests passed;
- final focused plan/public contract suite: 50 tests passed, 0 failures, 0 errors;
- full SDD implementation suite: 78 tests passed, 0 failures, 0 errors;
- repository script suite: 19 tests passed;
- LLM Wiki suite: 21 tests passed;
- skill architecture and context validators: exit 0;
- context report: 1 skill, 12 operations, warnings `[]`;
- skill-creator validator: exit 0, `Skill is valid!`;
- working and staged whitespace gates: exit 0.

The required combined gate was run once after the complete round-1 behavioral/durable set. Python commands used isolated `/private/tmp/sdd-poa-round1-*` bytecode cache roots.

### Boundaries And Concerns

- `knowledge/log.md` authority-evidence correction was not modified; the new event records only this fix wave.
- Human-only North Star / Written Spec approval, agent-owned plan readiness/execution, and separate remote authorization remain unchanged.
- No remote publication or live mutation was performed.
- Open material concern within round-1 scope: none identified by the implemented regressions and fresh verification.

## Approved Residual Fix Loop Round 2

### Status And Commit

- Result: `ROUND_2_FIX_COMPLETE`.
- Independent re-review findings addressed: exactly 2 Important findings.
- Scoped fix commit: `adf2038` (`fix: close SDD validator round two gaps`).

### All-Section Singleton Validation

The plan validator no longer obtains singleton authority/readiness data from only the first matching section. It collects every matching `Approved North Star Identity`, `Approved Written Spec Identity`, `Plan Binding`, and `Readiness Result` section, requires exactly one section, then validates all field declarations within that collected content.

The new adversarial cases reject:

- an empty `Repository checks` declaration;
- a second `Plan Binding` section containing `incompatible`, `issues_found`, `failed`, and `stale` evidence;
- a second `Readiness Result` section containing `issues_found`, `blocked`, and forbidden entry.

This preserves the exact singleton-value checks from round 1 while closing the duplicate-section first-match bypass.

### Remaining Structural Bodies

The Python docstring detector now permits blank lines between the closing docstring and the indented executable statement before recognizing the production body. The one-line shell-if detector now recognizes a non-empty command sequence through the final `; fi`, including multiple commands separated by internal semicolons.

Both checks remain anchored to complete language structures. Existing narrative controls—including the `def build_plan(spec): returns ...` interface prose—remain accepted.

### TDD And Verification Evidence

RED ran two new behavioral tests plus the existing prose control. Four subcases failed for the intended gaps: duplicate `Plan Binding`, duplicate `Readiness Result`, blank-line docstring body, and multi-command inline shell-if. The empty-field case and prose control already passed, proving the existing boundary rather than inventing a new expectation.

GREEN results:

- targeted representative/canonical/adversarial group: 5 tests passed;
- final focused plan/public contract suite: 52 tests passed, 0 failures, 0 errors;
- full SDD implementation suite: 80 tests passed, 0 failures, 0 errors;
- repository script suite: 19 tests passed;
- LLM Wiki suite: 21 tests passed;
- skill architecture and context validators: exit 0;
- context report: 1 skill, 12 operations, warnings `[]`;
- skill-creator validator: exit 0, `Skill is valid!`;
- working and staged whitespace gates: exit 0.

The required combined gate was run once after the complete round-2 behavioral/durable set. Python commands used isolated `/private/tmp/sdd-poa-round2-*` bytecode cache roots.

### Boundaries And Concerns

- Only the validator/tests, Plan Contract Overlay, and one append-only round-2 log event changed.
- Approved North Star / Written Spec authority, agent-owned plan readiness/execution, separate remote authorization, and the prior authority-evidence correction remain unchanged.
- No remote publication or live mutation was performed.
- Open material concern within round-2 scope: none identified by the regression set and fresh verification.

## Approved Residual Fix Loop Round 3

### Status And Commit

- Result: `ROUND_3_FIX_COMPLETE`.
- Remaining independent-review finding addressed: exactly 1 Important finding; round-2 finding 1 was not reopened.
- Scoped fix commit: `8a2aa4b` (`fix: parse prospective Python plan bodies`).

### Parser-Backed Python Body Detection

The Python prospective-body path no longer maintains a list of executable statement prefixes. It extracts line-anchored `def` and `async def` candidates together with their indented suite, then uses Python's parser to decide whether the candidate is an actual function body.

The new RED regressions prove that a valid body after optional docstrings, comments, and blank lines is rejected for all requested forms:

- `import json`;
- `await normalize(spec)` in an async function;
- `self.normalize(spec)`;
- `self.plan = spec`.

The exact prose interface control `def build_plan(spec): returns a normalized plan in the proposed interface.` remains allowed because it is not a valid parsed Python function body. Prior multiline, one-line, docstring, and allowed narrative regressions remain green. Shell detection was not changed.

### TDD And Verification Evidence

RED ran the new four-subcase Python test with the existing prose control. All four valid Python bodies failed for the expected whitelist gap; the prose control passed.

GREEN results:

- targeted Python/prose regression group: 5 tests passed;
- final focused plan/public contract suite: 53 tests passed, 0 failures, 0 errors;
- full SDD implementation suite: 81 tests passed, 0 failures, 0 errors;
- repository script suite: 19 tests passed;
- LLM Wiki suite: 21 tests passed;
- skill architecture and context validators: exit 0;
- context report: 1 skill, 12 operations, warnings `[]`;
- skill-creator validator: exit 0, `Skill is valid!`;
- working and staged whitespace gates: exit 0.

The required combined gate was run once after the complete round-3 behavioral/durable set. Python commands used isolated `/private/tmp/sdd-poa-round3-*` bytecode cache roots.

### Boundaries And Concerns

- Changed scope is limited to the Python validator/tests, Plan Contract Overlay, and one append-only round-3 log event.
- Shell logic, singleton validation, approved North Star / Written Spec authority, agent-owned plan readiness/execution, separate remote authorization, and prior authority evidence remain unchanged.
- No remote publication or live mutation was performed.
- Open material concern within round-3 scope: none identified by the parser-backed regressions and fresh verification.

## Approved Residual Fix Loop Round 4

### Status And Commit

- Result: `ROUND_4_FIX_COMPLETE`.
- Remaining independent-review finding addressed: exactly 1 Important finding.
- Scoped fix commit: `126646a` (`fix: parse complete prospective Python functions`).

### Complete Parser Candidate Detection

The Python prospective-body path now treats a line-anchored `def` or `async def` only as a candidate start. From that start, it expands candidate prefixes and asks Python's parser whether a complete function definition exists. It no longer requires a single-line signature and no longer stops candidate collection at a comment or other line whose indentation is not deeper than the header.

The new RED regressions close both reported bypasses:

- a valid function with an unindented comment between its header and indented body;
- a valid function with a multiline signature and indented body.

The same adversarial group retains the prior `import`, `await`, `self.normalize(...)`, `self.plan = ...`, and docstring / comment / blank-line cases. The exact prose interface `def build_plan(spec): returns a normalized plan in the proposed interface.` and existing normal plan prose remain accepted because they do not parse as complete Python function definitions. JavaScript, shell, command, singleton, authority, readiness, and coverage validation were not changed.

### TDD And Verification Evidence

RED ran the expanded Python adversarial test. Exactly the two new subcases failed for the reported bypasses; the prior parser-backed cases remained green.

GREEN results:

- targeted Python / docstring / prose regression group: 5 tests passed;
- focused Plan Contract suite: 23 tests passed, 0 failures, 0 errors;
- full SDD implementation suite: 81 tests passed, 0 failures, 0 errors;
- repository script suite: 19 tests passed, 0 failures, 0 errors;
- LLM Wiki suite: 21 tests passed, 0 failures, 0 errors;
- skill architecture validator: exit 0;
- skill context validator: exit 0, 1 contract validated;
- context report: exit 0, 1 skill, 12 operations, warnings `[]`;
- skill-creator validator: exit 0, `Skill is valid!`;
- working and staged whitespace gates: exit 0.

The full required verification used isolated `/private/tmp/sdd-poa-round4-*` bytecode cache roots.

### Boundaries And Concerns

- Changed behavioral scope is limited to the Python candidate collector, its adversarial tests, and the Plan Contract Overlay; this report is the only closeout artifact change.
- The parser remains the authority for whether a candidate is an actual Python function definition; no executable-statement whitelist was added.
- No remote publication or live mutation was performed.
- Open material concern within round-4 scope: none identified by the adversarial and full regression sets.
