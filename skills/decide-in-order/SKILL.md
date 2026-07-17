---
name: decide-in-order
description: Use when a user needs to decide what to do before choosing methods or schedules, especially for prioritization, daily planning, research framing, continue/stop/defer/delegate choices, sunk-cost checks, uncertainty, or post-action review. Orders reasoning from purpose and protected criteria through acceptable loss, the core question, constraints, method, risk, and review while keeping clear execution requests lightweight.
---

# Decide In Order

Help the user decide in a stable order before optimizing execution. Keep the reasoning disciplined and the visible response proportional to the decision.

## References

- Read `references/core.md` before applying the method. It is the sole source of truth for the reasoning order and prohibited reversals.
- Read `references/modes.md` to select light, deep, or review handling and to adapt the method to prioritization, daily planning, research, continuation, discarding, and uncertainty.
- Read `references/decision-contracts.md` when deciding what to show or when preparing an optional durable `DecisionRecord` candidate.

## Default Flow

1. Distinguish a clear execution request from an unresolved decision.
2. Select light, deep, or review handling.
3. Infer safe context as assumptions; separate decision-changing unknowns.
4. Apply the canonical order from `references/core.md` only as far as the decision requires.
5. Ask at most one decision-changing question per turn.
6. Reduce options and separate what must be decided now from what may wait.
7. Return the central decision, the minimum next action, and the review condition in the smallest useful form.
8. Prepare a `DecisionRecord` candidate only when the materiality rules require one.

## Boundaries

- Do not own task storage, scheduling, backend routing, external writes, or approval gates.
- Do not turn every response into a form, YAML document, or checklist.
- Do not fabricate numeric probabilities when evidence is absent.
- Do not treat urgency, importance, invested effort, or anxiety as sufficient decision criteria.
- Stop for human approval or additional evidence when a decision can cause severe irreversible harm.
