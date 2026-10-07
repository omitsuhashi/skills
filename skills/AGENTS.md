# Skill authoring contract

- Skills in this directory use the standard `<skill-name>/SKILL.md`.
  Its frontmatter must contain a non-empty `name` and `description`, and the
  directory name must equal `name`.
- Define a skill's inputs, outputs, and required capabilities without naming a
  target runtime. Use the active runtime's skill discovery to resolve applicable
  dependencies and capabilities.
- Do not make `description.md` a discovery requirement; must not create `description.md`
  for that purpose.
- Keep optional metadata isolated from the portable contract. For example,
  `agents/openai.yaml` may provide optional UI metadata. It must not determine
  skill discovery or behavior, except to enforce explicit-only invocation
  requested by the user. Declare that restriction in `SKILL.md` as well and
  use the runtime's invocation policy (for example,
  `policy.allow_implicit_invocation: false`) to prevent implicit loading.
- Keep runtime-specific tool assumptions conditional and document a capability
  check, alternative, or `BLOCKED` boundary.
- Run `scripts/validate_skill_architecture.py --all` and the skill-creator
  validator before handoff.

## Instruction design

- State the outcome, decision criteria, and non-obvious domain constraints.
  Use fixed sequences only where order protects correctness or authorization.
- Treat defaults and examples as guidance; explicit user choices govern the
  requested scope. Keep source integrity and authorization boundaries explicit.
- Ask only for missing information that materially changes the result and cannot
  be reasonably inferred. Continue independent authorized work while waiting.
  If a skill requires stopping, cite its exact rule and affected operation.
- Keep shared essentials in `SKILL.md`; load branch-specific references only
  when their stated condition applies. Avoid repeating host-level instructions.
- Define completion and verification proportional to the change. Passing a
  structural validator is not evidence of behavior on a real task; distinguish
  observed outcomes from untested expectations.
