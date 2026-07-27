# Target Authorization

The invocation supplies the exact source profile, declared task operation, and typed
target identity. The local gate resolves a fresh resolver-issued profile inventory
snapshot itself and derives the active profile set, runtime root, approved repository
owner set, and Project owner policy from that installed instance. The caller cannot
supply or override those authority facts.

After duplicate and read resolution, run `portfolio-os task-preflight` immediately
before the bounded operation's first direct GitHub MCP write. The local read-only gate must confirm that the
source profile is active in the fresh resolver-issued profile inventory snapshot, the
declared operation is granted to that profile, the entire canonical Work Unit registry
is valid, and the target has the exact operation-specific shape:

- `task_create` requires one repository, exact Work Unit ID and Work Unit repository binding,
  one Project, and a deterministic pre-Issue idempotency identity. It authorizes the
  bounded Issue creation and initial Project registration in one invocation;
- `task_project_register` requires one exact existing Issue identity, one Project,
  and the explicit partial-resume state, and is reserved for retry or resume rather
  than the normal successful `task_create` flow;
- `task_update` requires one exact Issue identity plus `mutation_kind=issue` and one
  exact Issue property, `title` or `body`, or
  that same Issue identity plus `mutation_kind=project_field`, exact Project URL,
  Project item ID, and one allowed field;
- `task_comment` requires one exact Issue identity;
- `task_complete` requires the exact remaining Issue and/or Project item identity,
  `requested_field=Status` for the Project side, and `resume_state=normal`,
  `issue_only`, or `project_only`.

Validate `OWNER/REPOSITORY` syntax, exact equality with the Work Unit repository
binding, membership of the owner in the approved repository owner set, and the Project
URL kind, owner, and positive number against the caller's Project owner policy. Never
infer authority from the current directory, a Git remote, Project title, recent use, or
the authenticated account alone.

An untrusted, stale, or cross-instance inventory, inactive source profile, ungranted operation,
absent authority fact, malformed Project URL, repository binding mismatch,
missing or conflicting identity, repository-wide or Project-wide authority, multiple repositories,
multiple Projects, or bulk mutation returns `confirmation-needed` or `blocked` with
zero writes. Do not invoke a mutation capability after a blocked guard. Capability
readiness is not part of the local command.

The allowed decision authorizes only the named operation and target for this invocation.
Next perform a separate direct GitHub MCP capability and access check only for the
declared operation. Then call the available official GitHub MCP capability directly
and perform the operation's normal remote readback. The local gate never invokes MCP,
reads credentials or tokens, accesses the network, mutates local or remote state, or
acts as a facade, wrapper, executor, or transport adapter.
