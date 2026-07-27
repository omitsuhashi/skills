# Skill authoring contract

- Skills in this directory are portable through their shared `<skill-name>/SKILL.md`.
  Its frontmatter must contain a non-empty `name` and `description`, and the
  directory name must equal `name`.
- Define a skill's inputs, outputs, and required capabilities without naming a
  target runtime. Use the active runtime's skill discovery to resolve applicable
  dependencies and capabilities.
- Do not make `description.md` a discovery requirement; must not create `description.md`
  for that purpose.
- Keep optional metadata isolated from the portable contract. For example,
  `agents/openai.yaml` may provide optional UI metadata but must not determine
  skill discovery or behavior.
- Keep runtime-specific tool assumptions conditional and document a capability
  check, alternative, or `BLOCKED` boundary.
- Repository compatibility is not live availability. Run the repository
  compatibility validator and skill-creator validator before handoff.
