# Target Authorization

The caller supplies the authority facts for one mutation: the exact source profile,
the exact active profile snapshot, the declared task operation, the exact Work Unit ID
and Work Unit repository binding when an Issue repository is involved, the approved
repository owner set, and the Project owner policy. This skill does not invent, widen,
or persist those facts.

After duplicate and read resolution, run the generic target guard immediately before
the first GitHub MCP mutation. The guard must confirm that the source profile is active
in that snapshot, the declared operation is granted to that profile, and the target has
the exact operation-specific shape:

- create / register requires one repository, its exact Work Unit ID and repository
  binding, and one Project;
- comment requires one repository and its exact Work Unit binding;
- project-only field update requires one Project and an explicit project-only
  declaration, with no repository;
- issue edit / complete requires one repository and its exact Work Unit binding;
- any optional repository or Project target supplied for an operation is still
  validated.

Validate `OWNER/REPOSITORY` syntax, exact equality with the Work Unit repository
binding, membership of the owner in the approved repository owner set, and the Project
URL kind, owner, and positive number against the caller's Project owner policy. Never
infer authority from the current directory, a Git remote, Project title, recent use, or
the authenticated account alone.

An inactive source profile, ungranted operation, absent authority fact, malformed Project URL,
repository binding mismatch, conflicting target, multiple repositories,
multiple Projects, or bulk mutation returns `confirmation-needed` or `blocked` with
zero writes. Do not invoke a mutation capability after a blocked guard. Capability
readiness is checked only for the declared operation; an unrelated missing capability
does not change this target decision.

The allowed decision authorizes only the named operation and target for this invocation.
The skill then calls the available official GitHub MCP capability directly and performs
the operation's normal remote readback.
