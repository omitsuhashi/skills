# Repository Router

- This repository contains a persistent LLM-maintained wiki under `knowledge/`.
- When bootstrapping, ingesting, querying, reviewing drafts, canonicalizing pages, or linting the wiki, read `knowledge/AGENTS.md` first and treat `knowledge/` as the knowledge root.
- When another workflow creates durable planning or decision documents, including roadmap, ADR, spec, design doc, implementation plan, or Goal command preparation, save them under `knowledge/wiki/...` according to `knowledge/AGENTS.md` instead of using repo-root `docs/` defaults.
- Keep repo-root guidance here short. Do not duplicate wiki-wide rules in this file.

## Dual-host authoring

- Skills and plugins created or changed in this repository must target both Codex and Hermes Agent.
- For skill requirements, follow `skills/AGENTS.md`.
- For plugin requirements, follow `plugins/AGENTS.md`.

## Task Worktree Policy

- Default branch checkout is read-only for task work.
- Before the first repository write after discovery or grilling, create or enter one Epic-scoped planning worktree.
- Reuse that worktree through Written Spec, Spec Gate, Issue Gate, Execution Plan Gate, and planning documentation sync.
- Do not create a new worktree for every Gate.
- Additional issue worktrees are used only when execution isolation or parallel worker review requires them.
- If required worktree creation fails, stop before writing; do not continue in the default checkout.
- Before delivery, verify that the PR branch contains every task commit.
- Before completion, verify that the default checkout matches its starting HEAD/status. Never alter pre-existing unrelated changes without explicit approval.

