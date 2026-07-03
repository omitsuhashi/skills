# Task Management Plugin

`task-management` is a thin Hermes / Codex workflow package for reviewed task
intake and backend-neutral task routing. The package ships one primary skill at
`skills/task-management/SKILL.md` and does not register MCP servers, configure
credentials, edit Hermes profiles, or perform GitHub writes during install.

## Hermes Install

Install the plugin subdirectory from this repository:

```bash
hermes plugins install git@github.com:omitsuhashi/skills.git#plugins/task-management
hermes plugins enable task-management
```

Hermes will discover `plugin.yaml` and load `__init__.py` when the plugin is
enabled. The entrypoint registers the bundled skill as
`task-management:task-management` through `ctx.register_skill`.

## Update Caveat

Current Hermes installs a subdirectory plugin by cloning the repository to a
temporary directory and moving only the selected subdirectory into
`~/.hermes/plugins/task-management`. That installed directory usually does not
retain `.git`, so:

```bash
hermes plugins update task-management
```

may fail with "not a git checkout". Until Hermes records source metadata for
subdirectory plugins or this plugin is published as a standalone repository,
refresh it with a forced reinstall:

```bash
hermes plugins install --force git@github.com:omitsuhashi/skills.git#plugins/task-management
hermes plugins enable task-management
```
