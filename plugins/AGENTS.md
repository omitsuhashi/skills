# Plugin authoring contract

- Plugins in this directory must be loadable by both Codex and Hermes Agent.
- Keep `.codex-plugin/plugin.json` and `plugin.yaml`; keep their `name`, `version`, and non-empty descriptions coherent.
- A Hermes plugin must have importable `__init__.py` with `register(ctx)`. Register bundled skills with `ctx.register_skill(...)`.
- Keep manifest tool declarations aligned with runtime registration through plugin-specific tests.
- Treat a standalone companion skill as a separate install prerequisite. Do not copy its source into the plugin. Document behavior when unavailable.
- Repository compatibility is not live availability. For approved live verification, confirm enablement and version with `hermes plugins list`, then run the plugin smoke.
- Do not mutate a live Hermes profile, marketplace, credential, or install state during ordinary validation.
- Run `scripts/validate_repository_compatibility.py` and the plugin-creator validator before handoff.
