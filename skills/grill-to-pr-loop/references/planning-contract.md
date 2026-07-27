# Planning Contract

Use this reference for intake, Grill with Docs, spec/PRD synthesis, Spec Gate, Issue Gate, and GitHub Mirror Gate preparation.

## Planning Worktree Gate

Before Written Spec or any planning write, run:

```bash
python3 <skill-dir>/scripts/planning_worktree.py prepare --repo-root <absolute> --epic-id <lower-kebab> --json
```

From the registered default checkout, create/reuse one Epic-scoped planning worktree, `codex/<epic-id>/planning`, through planning sync. Ignore project-local roots; failure stops before writes or default-checkout use. Reuse existing consent. Store host paths and starting HEAD/status at untracked `$(git rev-parse --git-common-dir)/agent-runs/grill-to-pr-loop/<epic-id>/planning-worktree.json`.

## Artifact Contract

Track this tree for every current Epic:

```text
<durable-planning-root>/<epic-id>/
├── spec.md
├── issues.md
├── implementation-plan.md
└── input-packet.json
```

`<durable-planning-root>` is `knowledge/wiki/syntheses`, or `docs/grill-to-pr-loop` without a wiki. `artifact_root` is that Epic directory; shown files are direct children. Commit it, maintain `knowledge/index.md` / `knowledge/log.md`, and leave execution artifacts untracked.

## Planning Authority / Supporting Agent Dispatch

The main planning context is the integration owner; supporting agents are advisory-only and read-only; Human is the decision authority. Dispatch one bounded question, minimum repo-relative read paths, and stop conditions. Return evidence, source paths, critique, disagreements, uncertainties, and a recommendation.

Supporting agents must not write canonical planning artifacts, approve a spec or scope, or seal an Input Packet. The main context compares evidence when advice conflicts and never uses a vote or majority. Send authority-bearing ambiguity to a Human gate.

After compaction, a fresh primary context inherits integration ownership only by explicit ownership transfer, not a supporting dispatch.

A user-selected model change or host model unavailability is host runtime state, not spec or packet drift.

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

Self-review for placeholders, contradictions, ambiguous criteria, stale paths, hidden assumptions, and English prose requiring Japanese.

## Gates

### Spec Gate

Before binding, run `python3 <skill-dir>/scripts/check_prereqs.py --phase execution --json`. Set `<issue-implementation-loop-skill-dir>` to the parent of the `SKILL.md` path in `required["issue-implementation-loop"]`; do not assume a repo-local checkout.

Finalize the spec, then identify its repo-relative spec path and exact raw-byte SHA-256:

```bash
python3 <issue-implementation-loop-skill-dir>/scripts/approved_spec_binding.py identify \
  --repo-root <repo-root> --spec-path <repo-relative-spec-path>
```

Present the path/digest, `Epic ID`, and six fields: `accepted_decisions`, `non_goals`, `acceptance_criteria`, `verification`, `remote_policy`, `stop_conditions`. Record one Spec Gate approval and wait before issue decomposition unless that exact revision and scope are already approved.

Any spec byte change requires re-approval and a new seal. Never infer approval, alter its digest, or edit while sealing. After Spec Gate approval, commit the spec and ledger/log before issue decomposition.

### Issue Gate

Present local issues with `Epic ID`, blockers, order, `実行可能/ブロック中`, and criteria. Wait for approval. After Issue Gate approval, commit the local ledger and ledger/log before mirroring or execution planning.

### GitHub Mirror Gate Preparation

For optional GitHub issue mirroring after Issue Gate, stop planning and load `remote-delivery.md`; this reference alone never authorizes creation. The remote reference owns auth checks, publication set, approval, writes, and local ledger updates.
