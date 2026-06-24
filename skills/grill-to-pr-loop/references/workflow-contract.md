# Grill to PR Loop Workflow Contract

Use this reference after loading `grill-to-pr-loop`. Keep execution mechanics delegated to `issue-implementation-loop`; do not duplicate its scheduler, runtime state, recovery, or review/fix loop. End-to-end coordination does not authorize same-session issue implementation.

## Sub-Skill Contract

- Use `grill-with-docs` for design interrogation and durable design context.
- Use `to-prd` when the approved conversation/docs should become a PRD or spec packet. Keep local-first unless remote publication is approved.
- Use `to-issues` only for draft vertical-slice breakdown and quiz/review until the GitHub Mirror Gate passes.
- Use `issue-implementation-loop` after local issues and the normalized execution packet are approved.
- Use GitHub/PR specialist workflows only after explicit remote-write approval.

When sub-skills assume remote tracker writes, this workflow's local-first and explicit-approval gates override them.

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

## Local Issue Policy

Local issues are the canonical planning source. Write local issue titles, headings, field labels, status values, ledger labels, blocker summaries, and prose in Japanese. Keep stable IDs, file paths, commands, code symbols, API names, branch names, error messages, and external issue/PR references unchanged.

Use these values:

- `レビュー状態`: `下書き`, `承認済み`, `差し戻し`, `未解決`
- `実行状態`: `実行可能`, `ブロック中`
- `実装レビュー`: `未実施`, `依頼済み`, `指摘対応中`, `承認済み`, `手動レビュー済み`, `差し戻し`
- no blocker / no remote: `なし`, `未作成`

Ledger table:

```markdown
| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <epic-id> | G2PR-001 | <日本語タイトル> | 承認済み | 実行可能 | なし | G2PR-002 | 未作成 | 未実施 | 未作成 |
```

## Blocker Graph

Build a blocker graph before execution planning:

- Every local issue declares `ブロック元`.
- Every local issue should declare `ブロック先` when known.
- `実行可能` means blockers are `なし` or complete.
- `ブロック中` means at least one blocker is not complete.
- Detect cycles before producing the normalized execution packet.
- Do not hand blocked issues to execution as runnable work. Put dependencies in the packet and let `issue-implementation-loop` reserve them.

## Branch / Base / Commit Policy

Do not model the run as a shared mutable development main branch that receives ad hoc merges from issue branches. Model it as:

1. Optional planning branch for workspace isolation.
2. Per-epic `epic_base.ref` branch named `codex/<epic-id>/epic-base`, plus immutable initial `epic_base.sha` and delivery `branch_state` in the Execution Envelope.
3. One branch/worktree reservation per approved issue.
4. Typed dependency edge plus work item `base_policy` when downstream code needs upstream code.
5. Local `PR_READY` as the implementation terminal state until remote delivery is explicitly approved.
6. Issue PRs from issue branches to `epic_base.ref`, with guarded agent merge when the remote policy allows it.
7. A final PR from `epic_base.ref` to `main`; final PR merge is human-only.

Use branch names like `codex/<epic-id>/<local-id>-<slug>`. Blocked issues may reserve names and paths, but their physical worktrees stay absent until release.

Base policies:

- `epic_base`: branch from `codex/<epic-id>/epic-base` at the recorded base head.
- `blocker_head`: branch from exactly one prerequisite issue head.
- `integration_head`: branch from an approved integration work item / branch.

Do not let a downstream worker merge multiple blocker heads. Add an integration work item when multiple prerequisite heads must be combined.

Commit policy:

- Run targeted verification and fresh final verification.
- Create or update a scoped local commit before issue implementation review.
- Review committed `BASE_SHA..HEAD_SHA`; do not use `working-tree` as the new PR-ready review head.
- After fixes, rerun verification and update the commit/head before re-review.
- Run at most two issue implementation review cycles; if the second review still has in-scope findings, stop and ask the human.

## Gates

### Spec Gate

Present spec path, `Epic ID`, accepted decisions, non-goals, acceptance criteria, verification commands, remote policy, and stop conditions. Wait for approval before issue decomposition unless the user already provided an approved spec and requested direct implementation.

### Issue Gate

Present local issues with `Epic ID`, blocker graph, dependency order, `実行可能/ブロック中` status, and acceptance criteria. Wait for approval before GitHub mirroring or execution planning.

### GitHub Mirror Gate

Optional. Before creating GitHub issues:

1. Confirm the remote points to GitHub.
2. Confirm GitHub tool/CLI auth.
3. Present exact local issues to publish.
4. Ask for explicit approval.
5. Create one issue per approved local issue.
6. Update local ledger before continuing.

If publication fails, keep the local ledger intact and ask whether to continue local-only.

### Execution Plan Gate

Build and present:

- normalized input packet path
- `issue-implementation-loop` capability preflight result
- issue list, write scopes, dependencies, and delivery intent
- `epic_base`, branch/worktree reservations, and base policies
- reviewer capability and approved fallback policy
- parallel/serial fallback policy
- remote-write policy
- issue PR base/merge policy and final PR human-only merge policy

Validate with:

```bash
python3 skills/issue-implementation-loop/scripts/validate_input_packet.py <packet.json>
```

Wait for explicit approval before execution unless the user has already authorized local implementation and no external write or high-risk action is included.

## Execution Handoff

After the Execution Plan Gate, load `issue-implementation-loop` and follow its mode router:

- `prepare`: create/validate Execution Envelope and branch/worktree reservations.
- `execute`: schedule implementation/review/fix lanes.
- `resume`: reconcile state after interruption.
- `status`: report current execution state.
- `deliver`: prepare PR-ready branches for approved remote delivery.

Recommended context split:

1. The planning/grill session creates the approved packet and envelope, then stops doing implementation work.
2. An execution coordinator context runs `prepare`, `execute`, `resume`, and `status`, dispatching bounded workers/reviewers.
3. PR delivery runs in `deliver` mode from the execution coordinator or a fresh delivery context that reads the completion artifact and runtime summary.

The workflow keeps final responsibility for ledger consistency, but the main planning/grill session must not become an implementation worker. If worker contexts are unavailable, stop before implementation.

## Local Ledger Update Invariant

Update the local ledger immediately after:

- GitHub issue creation.
- Execution returns issue implementation review result.
- Execution marks an issue `PR_READY` or complete.
- PR creation.
- PR closure/merge when known.

Do not report remote or local completion when the ledger contradicts reality. If ledger update fails after a remote action, stop and report the consistency problem.

## PR Delivery

Create issue PRs only after `issue-implementation-loop` returns `PR_READY` for every issue in the PR scope and after explicit remote-write approval.

For `batch_issue_prs`:

- `epic_base.ref` must be `codex/<epic-id>/epic-base`.
- Issue PRs use head `codex/<epic-id>/<local-id>-<slug>` and base `epic_base.ref`.
- The agent may merge issue PRs when checks/review/mergeability pass and the approved policy says `agent_default_with_human_escalation`.
- Escalate to the human for scope drift, spec ambiguity, failed checks, conflicts, unresolved review, missing permissions, or any uncertain judgment.
- After every issue PR creation or merge, update the local ledger and runtime state before continuing.
- Before every issue PR or final PR, validate the exact delivery plan with `issue-implementation-loop/scripts/validate_delivery_plan.py`.
- After all issue PRs are merged and `epic_base.ref` reconciles as an existing branch, create the final PR from `epic_base.ref` to `main`.
- If a final PR plan uses an issue branch (`codex/<epic-id>/<local-id>-<slug>`) as the head, stop; do not reinterpret the last issue branch as the integration branch.
- Final PR merge is human-only.

Include:

- what changed
- spec/local issue/remote issue links
- blocker or stacked PR relationship
- verification results
- implementation review summary
- known risks

Use `Closes #<n>` only when merge should close the issue. Use `Refs #<n>` for partial, stacked, exploratory, or non-closing PRs.

Push, GitHub issue creation, PR creation, ready-for-review, issue PR merge, force push, deploy, credential, permission, billing, production, and destructive actions require approved remote policy. Final PR merge always requires current human action.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Skipping Grill with Docs because the design seems obvious | Run it or stop if unavailable. |
| Keeping execution mechanics in this skill | Move worktree/scheduler/runtime/recovery/review loop details to `issue-implementation-loop`. |
| Implementing issue code in the planning/grill session | Stop and hand off to an execution coordinator with worker contexts. |
| Creating horizontal layer issues | Rewrite as vertical slices that are independently verifiable. |
| Writing generated issue labels in English | Use Japanese labels/status values; keep code symbols and paths unchanged. |
| Treating GitHub as the default issue source | Keep local issues canonical; mirror only after approval. |
| Letting `to-prd` or `to-issues` publish remotely before the gate | Use them for local synthesis/review first. |
| Creating GitHub issues or PRs without updating the ledger | Update the local ledger immediately. |
| Starting execution without a validated input packet | Validate and present the Execution Plan Gate first. |
| Treating a planning branch as the execution source of truth | Pin `epic_base` in the envelope and reserve issue branches/worktrees. |
| Merging multiple blocker heads inside a downstream worker | Create an approved integration work item or integration branch. |
| Marking an issue PR-ready from an uncommitted diff | Create/update a scoped local commit and review `BASE_SHA..HEAD_SHA`. |
| Treating PR review as issue implementation review | Let `issue-implementation-loop` run the issue-scoped review gate before PR readiness. |
| Treating PR creation as implicit | Get explicit approval first. |
| Merging final PRs automatically | Create the final PR, then leave final merge to the human. |
