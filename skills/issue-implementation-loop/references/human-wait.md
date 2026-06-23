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
