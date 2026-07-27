# Planning Contract

Use this reference for intake, Grill with Docs, spec/PRD synthesis, Spec Gate, Issue Gate, and GitHub Mirror Gate preparation.

## Planning Worktree Gate

Before Written Spec or any planning write, run:

```bash
python3 <skill-dir>/scripts/planning_worktree.py prepare --repo-root <absolute> --epic-id <lower-kebab> --json
```

It canonicalizes the repo, reads the registered default checkout, and creates/reuses one Epic-scoped planning worktree, `codex/<epic-id>/planning`. Reuse it through Written Spec, Spec Gate, Issue Gate, Execution Plan Gate, and planning sync. The project-local root must be ignored; sandbox/preparation failure stops before writes, never using default checkout. No repeated consent follows an existing preference. Its untracked runtime identity is `$(git rev-parse --git-common-dir)/agent-runs/grill-to-pr-loop/<epic-id>/planning-worktree.json`, with host paths and exact starting HEAD/status.

## Artifact Contract

Track this tree for every current Epic:

```text
<durable-planning-root>/<epic-id>/
├── spec.md
├── issues.md
├── implementation-plan.md
└── input-packet.json
```

Here `<durable-planning-root>` is `knowledge/wiki/syntheses`; without a wiki use `docs/grill-to-pr-loop`. `artifact_root` is the exact Epic directory; spec, local issue sources, and sealed packet are direct children. Keep `knowledge/index.md` and `knowledge/log.md` current. Commit this tree; execution artifacts use the untracked lifecycle.

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

Self-review in this order:

1. **Requirements**: the approved problem, decisions, non-goals, acceptance criteria, verification, remote policy, and stop conditions are complete and consistent.
2. **Material simplicity**: no concrete simpler alternative meets the same requirements and risk boundary with materially fewer mechanisms, branches, layers, duplication, or abstractions.
3. **Material risk**: placeholders, contradictions, ambiguous criteria, stale paths, hidden implementation assumptions, and English prose that should be Japanese do not create material risk.

Report only `Critical` / `Important` findings. Do not report `Minor`, nit, preference, or optional improvement. A material simplicity finding must include a concrete simpler alternative and is blocking as `intent_gap` / `Important`; otherwise approve without inventing a finding.

## Gates

### Spec Gate

Before any binding command, run `python3 <skill-dir>/scripts/check_prereqs.py --phase execution --json`. Derive `<issue-implementation-loop-skill-dir>` as the parent directory of the `SKILL.md` path in `required["issue-implementation-loop"]`; never assume the target repository contains a source checkout of the skill.

Finalize the spec before approval. Identify its repo-relative spec path and exact raw-byte SHA-256 with:

```bash
python3 <issue-implementation-loop-skill-dir>/scripts/approved_spec_binding.py identify \
  --repo-root <repo-root> --spec-path <repo-relative-spec-path>
```

Present that path and digest with `Epic ID`, 採用した判断, 非目標, 受け入れ条件, 検証コマンド, remote policy, and stop conditions. Record one Spec Gate approval whose scope contains all six fields: `accepted_decisions`, `non_goals`, `acceptance_criteria`, `verification`, `remote_policy`, and `stop_conditions`. Wait for approval before issue decomposition unless the user already supplied approval for that exact revision and scope.

Any spec byte change requires re-approval and a new seal. Never infer approval, update the expected digest, or edit the spec while sealing.

After Spec Gate approval, commit the approved spec and ledger/log updates before issue decomposition.

### Issue Gate

Present local issues with `Epic ID`, blocker graph, dependency order, `実行可能/ブロック中` status, and acceptance criteria. Wait for approval before GitHub mirroring or execution planning.

After Issue Gate approval, commit the approved local issue ledger and ledger/log updates before GitHub mirroring or execution packet work.

### GitHub Mirror Gate Preparation

Optional. If the user wants GitHub issue mirroring after Issue Gate, stop planning work and load `remote-delivery.md`.

Do not create GitHub issues from this planning reference alone. The remote reference owns the remote/auth checks, exact publication set, explicit approval, write action, and local ledger update invariant.
