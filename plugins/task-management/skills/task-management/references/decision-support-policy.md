# Decision Support Policy

Use `$decide-in-order` as an optional companion when it is discoverable. This reference selects intensity and handoff behavior only; it does not restate the decision method.

## Operation Matrix

| Operation | Intensity |
| --- | --- |
| Task snapshot read or search | none |
| Backend or destination routing | none |
| Adapter preflight or dispatch preview | none |
| Clear execution task intake | light |
| Ambiguous task intake | deep |
| Research task framing | light, then deep when the decision question or stop signal is missing |
| Prioritization or daily planning | deep |
| Continue, stop, defer, or delegate | deep |
| Periodic or post-action review | review |
| Simple status update or maintenance | none |

Light handling is normally invisible. Do not add a decision form when the task is already ready for execution.

## Intake Gate

Before composing a new TaskDraft, check:

1. Is this ready for execution or is a decision unresolved?
2. Are conditions or deadlines overriding the stated purpose?
3. Is there a core question that must be answered first?

If all three checks are clear, continue without displaying decision scaffolding.

Use deep handling when purpose changes the choice, protected criteria conflict, acceptable loss must be chosen, options remain excessive, sunk cost drives continuation, research has no stop signal, or the choice has material irreversible or trust effects.

## Existing TaskDraft Handoff

Do not create a new handoff schema.

- Map the decided direction to TaskDraft title and outcome.
- Map the minimum next action to the body.
- Map evidence of progress or completion to acceptance text.
- Map assumptions and unresolved facts to review notes.
- Map an existing durable decision record only as a sanitized source reference.

Adapter Dispatch Review remains required. Decision support does not approve a backend destination or state-changing adapter operation.

## Companion Unavailable

- Mechanical reads, routing, and clear task intake continue.
- Do not claim that decision support ran.
- State that the companion is unavailable when deep handling is required.
- Stop before ordinary TaskDraft creation for severe irreversible harm.
- Do not copy a shortened version of the canonical method into this plugin.
