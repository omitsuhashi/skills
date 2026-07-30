# Structure And Routing

Read this reference only when resolving knowledge-root layout, page type, durable-document routing, or filename identity. Do not read it for a routine query.

## Default Layout

Mixed repository:

```text
repo-root/
├── AGENTS.md
└── <knowledge-root>/
    ├── raw/
    │   ├── sources/
    │   └── assets/
    ├── wiki/
    │   ├── sources/
    │   ├── entities/
    │   ├── concepts/
    │   ├── syntheses/
    │   ├── queries/
    │   └── drafts/
    ├── index.md
    ├── log.md
    └── AGENTS.md
```

Dedicated wiki repository:

```text
repo-root/
├── raw/
│   ├── sources/
│   └── assets/
├── wiki/
│   ├── sources/
│   ├── entities/
│   ├── concepts/
│   ├── syntheses/
│   ├── queries/
│   └── drafts/
├── index.md
├── log.md
└── AGENTS.md
```

## Page Types

- `wiki/sources/`: source summaries that preserve claims, significance, open questions, provenance, and relations to affected knowledge.
- `wiki/entities/`: named people, organizations, products, places, characters, or other durable things.
- `wiki/concepts/`: themes, methods, arguments, frameworks, and recurring ideas that span sources.
- `wiki/syntheses/`: comparisons, theses, timelines, due-diligence notes, briefings, reports, roadmaps, ADRs, specifications, design documents, implementation plans, and implementation progress ledgers.
- `wiki/queries/`: reusable answers, comparison notes, decision material, and short reports that originate from a question.
- `wiki/drafts/`: non-owner proposals awaiting an owner decision.

## Durable Document Routing

Keep durable outputs from other workflows inside the knowledge root.

- Route roadmaps, ADRs, specifications, design documents, implementation plans, briefings, and comparison notes to `wiki/syntheses/`.
- Route an implementation progress ledger that tracks multiple slices, remaining scope, evidence, and review conditions to `wiki/syntheses/`.
- Route short decision or comparison notes that originate from a question to `wiki/queries/`.
- Declare any project-specific subordinate routing as a local override in the knowledge-root contract.

An implementation progress ledger does not replace its specifications, plans, progress records, or issue tracking. It is the discovery surface for their status, remaining scope, evidence, next trigger, and review conditions. Keep an active ledger discoverable through the index and record each lifecycle update in the log. Do not require a validator, scheduler, database view, viewer plugin, or issue tracker integration.

## Filename Identity

- Use a lower-kebab-case ASCII slug as the default durable filename identity.
- Preserve the formal or localized title as semantic content and discovery metadata instead of packing search terms into the filename.
- Keep one durable topic per file.
- Preserve raw-source filenames.
- Use a date prefix when chronology is part of a source summary or query note's identity.

Examples of structural path identity:

- `wiki/sources/2026-04-12-article-title.md`
- `wiki/entities/vannevar-bush.md`
- `wiki/concepts/persistent-knowledge-base.md`
- `wiki/syntheses/llm-wiki-architecture.md`
- `wiki/syntheses/checkout-api-phase-1-spec.md`
- `wiki/syntheses/checkout-implementation-progress-ledger.md`
- `wiki/queries/2026-04-12-compare-rag-and-llm-wiki.md`
- `wiki/drafts/2026-04-12-proposed-update-to-checkout-claims.md`
