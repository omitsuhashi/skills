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

Specs/PRDs use Japanese headings/labels/prose. Preserve IDs, paths, commands, code symbols, schema keys, branches, errors, external refs.

The spec must contain:

- 問題設定 / 成功条件。
- Stable `Epic ID`。
- 採用した判断。
- 非目標。
- Issue 分解方針。
- 受け入れ条件。
- 検証方針 / コマンド。
- リモート書き込み方針。
- 人間レビューゲート。
- 停止条件 / 既知のリスク。

Self-review the spec for placeholders, contradictions, ambiguous criteria, stale paths, hidden implementation assumptions, and English prose that should be Japanese.

## Gates

### Spec Gate

Present spec path, `Epic ID`, 採用した判断, 非目標, 受け入れ条件, 検証コマンド, remote policy, and stop conditions. Wait for approval before issue decomposition unless the user already provided an approved spec and requested direct implementation.

After Spec Gate approval, commit the approved spec and ledger/log updates before issue decomposition.

### Issue Gate

Present local issues with `Epic ID`, blocker graph, dependency order, `実行可能/ブロック中` status, and acceptance criteria. Wait for approval before GitHub mirroring or execution planning.

After Issue Gate approval, commit the approved local issue ledger and ledger/log updates before GitHub mirroring or execution packet work.

### GitHub Mirror Gate Preparation

Optional. If the user wants GitHub issue mirroring after Issue Gate, stop planning work and load `remote-delivery.md`.

Do not create GitHub issues from this planning reference alone. The remote reference owns the remote/auth checks, exact publication set, explicit approval, write action, and local ledger update invariant.
