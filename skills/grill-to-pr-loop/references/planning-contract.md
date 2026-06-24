# Planning Contract

Use this reference for intake, Grill with Docs, spec/PRD synthesis, Spec Gate, Issue Gate, and GitHub Mirror Gate preparation.

## Artifact Contract

Prefer repo-local conventions. In this repo:

- long specs, ADRs, implementation plans, and Goal contracts: `knowledge/wiki/syntheses/`
- raw source material: `knowledge/raw/sources/`
- source summaries: `knowledge/wiki/sources/`
- active catalog and timeline: `knowledge/index.md`, `knowledge/log.md`

For repos without a knowledge wiki, fallback paths are:

- Spec or PRD: `docs/grill-to-pr-loop/<topic>-spec.md`
- Local issue ledger: `docs/grill-to-pr-loop/<topic>-issues.md`
- Execution packet: `docs/grill-to-pr-loop/<topic>-input-packet.json`
- Completion summary: `docs/grill-to-pr-loop/<topic>-completion.md`

## Spec / PRD Minimum

The spec must contain:

- Problem statement and success criteria.
- Stable `Epic ID`.
- Accepted decisions from Grill with Docs.
- Non-goals.
- Issue decomposition strategy.
- Acceptance criteria.
- Testing decisions and verification commands.
- Remote-write policy.
- Human review gates.
- Stop conditions and known risks.

Self-review the spec for placeholders, contradictory decisions, ambiguous acceptance criteria, stale paths, and hidden implementation assumptions.

## Gates

### Spec Gate

Present spec path, `Epic ID`, accepted decisions, non-goals, acceptance criteria, verification commands, remote policy, and stop conditions. Wait for approval before issue decomposition unless the user already provided an approved spec and requested direct implementation.

### Issue Gate

Present local issues with `Epic ID`, blocker graph, dependency order, `実行可能/ブロック中` status, and acceptance criteria. Wait for approval before GitHub mirroring or execution planning.

### GitHub Mirror Gate Preparation

Optional. If the user wants GitHub issue mirroring after Issue Gate, stop planning work and load `remote-delivery.md`.

Do not create GitHub issues from this planning reference alone. The remote reference owns the remote/auth checks, exact publication set, explicit approval, write action, and local ledger update invariant.
