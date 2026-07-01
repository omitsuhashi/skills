# Human Wait Scope

Default scope is `issue`.

## Scopes

- `issue`: stop only the target issue.
- `descendants`: stop target issue's unreleased hard descendants.
- `resource`: stop issues requiring the same resource/write lock.
- `epic`: stop all issues.

Use `epic` only for envelope corruption, DAG/runtime corruption, shared-base safety issues, credential/security incidents, or external contract changes affecting all issues.

## Runtime Rule

While waiting, continue unrelated runnable implementation work, review work, fix work, local verification, and recovery. Do not turn a narrow question into a global pause.

## Review Governance Waits

`safety_escalation` findings and encountered `classification_needed` cases open a
`human_request_opened` event at the smallest affected scope. Do not auto-fix
them and do not widen the wait just because the finding appeared during a
review.

- Use `issue` when the decision affects only the source issue.
- Use `descendants` when unreleased hard descendants would inherit the risk or
  classification.
- Use `resource` when the same write lock, credential, delivery surface, or
  shared artifact is affected.
- Use `epic` only for the existing epic-wide reasons above.

Routine future-only hardening suggestions are not review findings and do not
open a human wait. A `hardening_candidate` is recorded in
`<runtime-root>/decisions/hardening-candidates.json` only when the human
explicitly requested hardening review or the candidate is tied to current PR
delivery risk. It still does not open an issue execution wait by itself.

Do not open a classification wait just because classification is a possible
review category. Open it only when an actual finding cannot be classified from
available evidence or the human explicitly requested a classification pass.
