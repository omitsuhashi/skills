# Skill authoring contract

- Skills in this directory must be readable by both Codex and Hermes Agent.
- Use `<skill-name>/SKILL.md` as the shared entrypoint. Its frontmatter must contain a non-empty `name` and `description`, and the directory name must equal `name`.
- Hermes discovery does not require a separate description file; must not create `description.md` as a discovery requirement.
- `agents/openai.yaml` is Codex UI metadata and does not make a skill discoverable in Hermes.
- Keep host-specific tool assumptions conditional and document a capability check, alternative, or platform boundary.
- Document one Hermes discovery route: GitHub install or tap, `~/.hermes/skills/`, or `skills.external_dirs`.
- Repository compatibility is not live availability. For approved live verification, confirm the skill in `hermes skills list`.
- Run the repository dual-host validator and skill-creator validator before handoff.
