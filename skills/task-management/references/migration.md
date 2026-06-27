# Migration Boundary

Backend migration means moving tasks from one backend to another and then switching the configured adapter. The caller's local system must not become the migration source of truth.

Allowed local migration artifacts:

- Export reports that identify backend task references.
- Mapping notes from old backend references to new backend references.
- Recommendation logs explaining why a backend switch is safe.

Disallowed local artifacts:

- A local task ledger that attempts to own status, due date, assignee, priority, body, or project fields.
- Raw provider payload archives that become de facto task state.
- Provider-specific IDs in application core contracts.
