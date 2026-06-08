# Repository Router

- This repository contains a persistent LLM-maintained wiki under `knowledge/`.
- When bootstrapping, ingesting, querying, or linting the wiki, read `knowledge/AGENTS.md` first and treat `knowledge/` as the knowledge root.
- When another workflow creates durable planning or decision documents, including roadmap, ADR, spec, design doc, implementation plan, or Goal command preparation, save them under `knowledge/wiki/...` according to `knowledge/AGENTS.md` instead of using repo-root `docs/` defaults.
- Keep repo-root guidance here short. Do not duplicate wiki-wide rules in this file.
