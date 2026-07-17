# Decision Outputs

## Sparse DecisionFrame

Use `DecisionFrame` as internal vocabulary, not as a required input or output schema. Populate only decision-relevant fields such as purpose, protected criteria, acceptable loss, core question, decide-now, decide-later, constraints, method, risk, next action, review, assumptions, and unresolved facts.

- Do not serialize it by default.
- Do not emit empty arrays or null-valued fields to appear complete.
- Keep inferred content in `assumptions`.
- Keep only decision-changing unknowns in `unresolved`.

## Adaptive Guidance

DecisionGuidance is a rendering rule, not a second schema.

- For an unresolved decision, begin with a one-sentence purpose statement or visible purpose assumption before showing a recommendation, constraints, method, or risk analysis; naming `purpose` as an abstract criterion is not enough.
- For clear execution, show no special structure.
- For light correction, show the central decision, minimum next action, and review trigger in two to four lines.
- For deep handling, show only the relevant purpose, protected criteria, acceptable loss, decide-now, decide-later, next action, evidence, risk, assumptions, and review information.
- For review, show the result, changed assumption, reasoning-order issue, adjustment, and next review when useful.

## DecisionRecord Candidate

Prepare a typed candidate only when the decision has long-lived effects, high reversal cost, multi-person or trust impact, a stop or withdrawal choice, an accountability requirement, or an explicit request to record it.

Required fields:

```yaml
DecisionRecord:
  schema_version: 1
  title:
  decision_status: provisional | confirmed | superseded
  purpose:
  core_question:
  decision:
  must_protect:
  acceptable_loss:
  next_action:
  review:
```

Add only when relevant:

```yaml
  decide_later:
  constraints:
  alternatives_rejected:
  risk:
  sunk_cost_check:
  assumptions:
  evidence:
  source_ref:
```

The caller owns identifiers, timestamps, storage, and writes. Returning a candidate does not prove that any durable record was saved.
