# Repository Router

- This repository contains a persistent LLM-maintained wiki under `<knowledge-root>/`.
- When bootstrapping, ingesting, querying, reviewing drafts, canonicalizing pages, or linting the wiki, read `<knowledge-root>/AGENTS.md` first and treat that directory as the knowledge root.
- When another workflow creates durable planning or decision documents, including superpowers outputs such as roadmap, ADR, spec, design doc, or implementation plan, save them under `<knowledge-root>/wiki/...` according to `<knowledge-root>/AGENTS.md` instead of using repo-root `docs/` defaults.
- For single-root topology, do not create a root registry; the knowledge-root `AGENTS.md` is the authority source for owner, write boundary, and draft target.
- For multi-root topology, the knowledge-root `AGENTS.md` must point to the system-specific root registry adapter.
- Multi-root adapters must resolve `Root ID`, `Root URI/Path`, `Scope`, `Canonical Owner`, `Read`, `Write`, and `Draft Target`; proposed notes require `Read: allowed`, `Write: owned|propose`, and a resolved in-root `Draft Target`.
- If adapter resolution returns `Read: restricted`, `Read: no-access`, `Write: closed`, or an unresolved `Draft Target`, do not write verified claims or proposed notes; ask the session user or local governance.
- Keep repo-root guidance here short. Do not duplicate wiki-wide rules in this file.
