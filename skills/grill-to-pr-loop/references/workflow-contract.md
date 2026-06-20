# Grill to PR Loop Workflow Contract

Use this reference for execution details after loading `grill-to-pr-loop`.

## Sub-Skill Contract

This workflow coordinates existing skills instead of replacing them.

- Use `grill-with-docs` to interrogate design choices and produce durable ADR/glossary/design context.
- Use `to-prd` after Grill with Docs when the next artifact should be a PRD, spec packet, or product requirement summary. Keep its result local-first unless the current gate explicitly approves publishing.
- Use `to-issues` after the spec is approved to draft vertical slices and quiz the user about granularity and dependencies. Do not allow its publish phase to create remote issues until the GitHub Mirror Gate passes.
- Use `tdd` inside each implementation Goal loop for features, bug fixes, refactors, or behavior changes.
- Use `superpowers:requesting-code-review` when available after each issue's fresh final verification and scoped local commit. The review must check only for gaps against the approved local issue, requirements, spec, acceptance criteria, write scope, and verification evidence before local completion, blocker release, or PR creation.

When a sub-skill's default workflow assumes remote issue tracker writes, this workflow's local-first and explicit-approval gates override it.

## Local Ledger Update Invariant

The local issue ledger is the source of truth for workflow state. Remote writes and implementation completion must be reflected locally in the same step.

Update the local ledger immediately after:

- Creating a GitHub issue: record the GitHub issue URL or number.
- Creating a PR: record the PR URL, PR state, and whether it uses `Closes` or `Refs`.
- Passing issue implementation review: record `実装レビュー`, `レビュー範囲`, `レビュー結果`, reviewer used or manual fallback, in-scope findings, and any human risk acceptance.
- Completing an issue implementation: update completion state, verification result, commit SHA, implementation review result, and any blocker changes.
- Closing or merging a PR when known: update PR state and issue completion/closure state.

Do not report a GitHub issue or PR as done if the local ledger still says `未作成` for that remote object or otherwise contradicts remote reality. Do not report a local issue implementation, blocker release, or PR-ready branch as complete if the local ledger still says `未完了`, `実装レビュー: 未実施`, `実装レビュー: 依頼済み`, `実装レビュー: 指摘対応中`, or otherwise contradicts the worktree/review reality. If the ledger update fails, stop and report the remote action plus the failed local update as an unresolved consistency problem.

## Artifact Contract

Prefer repo-local conventions. If none exist, use:

- Spec or PRD: `docs/grill-to-pr-loop/<topic>-spec.md`
- Local issue ledger: `docs/grill-to-pr-loop/<topic>-issues.md`
- Worktree map: `docs/grill-to-pr-loop/<topic>-worktrees.md`
- Goal prompt snippets: `docs/grill-to-pr-loop/goals/<issue-slug>.md`

For repos with a knowledge wiki or Goal convention, keep the short prompt separate from the detailed contract. Put durable detail in the repo's canonical spec/synthesis location and link to it from the prompt.

## Spec / PRD Minimum

The spec or PRD must contain:

- Problem statement and success criteria.
- Stable `Epic ID` for branch, worktree, ledger, and Goal prompt namespacing.
- User stories or user-facing behaviors when relevant.
- Accepted decisions from Grill with Docs.
- Non-goals.
- Issue decomposition strategy.
- Acceptance criteria.
- Testing decisions and test seams.
- Verification commands.
- Human review gates.
- Stop conditions and known risks.

Self-review the spec for placeholders, contradictory decisions, ambiguous acceptance criteria, stale paths, and hidden implementation assumptions.

## Local-First Issue Policy

Local issues are the source of truth for decomposition. Write local issue titles, headings, field labels, status values, ledger labels, blocker summaries, and prose in Japanese. Keep stable IDs, file paths, commands, code symbols, API names, branch names, error messages, and external issue/PR references in their original form.

GitHub issues are optional mirrors for collaboration and PR traceability. When creating GitHub issues, write titles, headings, labels, status values, and prose in Japanese using the same local issue contract.

Do not use English display labels such as `Ready`, `Blocked`, `Blocked by`, `Blocks`, `None`, or `Not created` in generated issues or ledgers. Use `実行可能`, `ブロック中`, `ブロック元`, `ブロック先`, `なし`, and `未作成` instead. Only keep English when it is a command, path, identifier, product name, API name, branch name, URL, or copied external error text.

Local ledgers must use these `レビュー状態` values: `下書き`, `承認済み`, `差し戻し`, `未解決`. Do not use `approved`, `rejected`, `draft`, or `unresolved` as generated review state values.

Local ledgers that track implementation progress must use these `実装レビュー` values: `未実施`, `依頼済み`, `指摘対応中`, `承認済み`, `手動レビュー済み`, `差し戻し`. Do not overload `レビュー状態`; it is for human review of the local issue draft, not implementation review of completed code.

Every local ledger must record one stable `Epic ID` for the workflow. The `Epic ID` must be lower-kebab-case ASCII, unique among active epics in the repo's worktree namespace, and stable for the lifetime of the local issue ledger. Derive it from the approved spec topic when the user does not provide one, then present it for approval before worktree planning. Do not reuse the same `Epic ID` for unrelated epics even if their issue IDs differ.

Use local-only mode by default when:

- The user has not explicitly approved remote issue creation.
- GitHub access, authentication, or permissions are unavailable.
- The repo has no GitHub remote.
- The issue split is still under review.

Use GitHub mirror mode only after local issue approval. Record the relationship in the local ledger:

```markdown
| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <epic-id> | G2PR-001 | <日本語タイトル> | 承認済み | 実行可能 | なし | G2PR-002 | https://github.com/<org>/<repo>/issues/<n> | 未実施 | 未作成 |
```

If GitHub publication fails, keep the approved local ledger intact and ask whether to continue local-only.

After GitHub publication succeeds, update the local ledger before doing any worktree or PR action. The update must include the remote issue URL or issue number for every created issue.

## ブロッカーグラフ

Build a blocker graph before the Issue Gate. Treat each blocker edge as `blocked issue -> required prerequisite`.

Rules:

- Every local issue must declare `ブロック元`.
- Every local issue should declare `ブロック先` when known.
- `実行可能` means `ブロック元` is `なし` or all blockers are completed.
- `ブロック中` means at least one blocker is not completed.
- Parallel work may start only for `実行可能` issues with no dependency edge between them.
- Worktree creation and Goal loops are allowed only for `実行可能` issues unless the user explicitly overrides the blocker.
- Detect cycles. If a cycle exists, stop and ask the user to revise the issue split or blocker graph.
- When a blocker completes, update dependent issues from `ブロック中` to `実行可能` before proposing new worktrees.

Use this compact graph summary in the local ledger:

```markdown
## ブロッカーグラフ

- G2PR-001: 実行可能; ブロック先 G2PR-002, G2PR-003
- G2PR-002: ブロック中; ブロック元 G2PR-001
- G2PR-003: ブロック中; ブロック元 G2PR-001
```

## ローカルIssueテンプレート

Use vertical slices. Each issue should be independently verifiable. Write the title, headings, labels, status values, and prose in Japanese.

```markdown
## ローカルID

G2PR-<number>

## Epic ID

<lower-kebab-case-epic-id>

## タイトル

<日本語の短いタイトル>

## 作るもの

<このスライスで実現する一連の振る舞い。>

## 受け入れ条件

- [ ] <観測可能な条件>
- [ ] <検証またはレビュー条件>

## ブロッカー

- 実行状態: <実行可能 または ブロック中>
- ブロック元: <ローカルIssue ID または なし>
- ブロック先: <ローカルIssue ID または なし>

## 必要な文脈

- 仕様: <path>
- ADR / 用語集 / 関連ドキュメント: <paths または なし>

## 検証

- <command>

## 実装レビュー

- 状態: <未実施 | 依頼済み | 指摘対応中 | 承認済み | 手動レビュー済み | 差し戻し>
- レビュー範囲: <base sha>..<head sha> または 未実施
- レビュー結果: <verdict / findings summary / risk acceptance または 未実施>

## リモート追跡

- GitHub Issue: <URL または 未作成>
- PR: <URL または 未作成>
```

Avoid brittle file-path instructions unless a path is the stable public surface being changed.

## Optional GitHub Mirror Gate

Before creating GitHub issues:

1. Confirm the repo remote points to GitHub.
2. Confirm a GitHub app, MCP tool, or `gh` CLI is available and authenticated.
3. Present the exact local issues to publish, including `実行可能/ブロック中` status and blocker edges.
4. Ask for explicit approval to create remote issues.
5. Create one GitHub issue per approved local issue.
6. Update the local ledger with remote issue URLs before continuing.

Do not create GitHub issues for `差し戻し`, `下書き`, or `未解決` local issues. Local issues with `レビュー状態: 承認済み` and `実行状態: ブロック中` may be mirrored only when the GitHub Mirror Gate explicitly includes blocked tracking issues and the user approves them.

Remote issue bodies should preserve the Japanese local issue contract, blocker fields, and spec path. Use the repo's normal labels/milestones only when they are discoverable from repo docs or approved by the user.

If using `to-issues`, use only its context gathering, draft vertical-slice breakdown, and quiz/review phases until this gate passes. Do not let `to-issues` publish remote issues as a side effect before explicit GitHub mirror approval.

## Epic-Scoped Branch And Worktree Naming

Use epic-scoped names so two epics can run in parallel even when they both have `G2PR-001` or the same issue slug.

Rules:

- `Epic ID` format: lower-kebab-case ASCII; no `/`, spaces, shell metacharacters, or path traversal.
- Default branch naming: `codex/<epic-id>/<issue-id>-<issue-slug>`.
- Default worktree placement: `<worktree-root>/<repo-name>/<epic-id>/<issue-id>-<issue-slug>`.
- `issue-id` stays stable (`G2PR-001` etc.); `issue-slug` is lower-kebab-case and should describe the vertical slice.
- If the repo has a documented branch/worktree convention, adapt only the prefix/root; keep the `Epic ID` namespace.
- Do not silently add `-2`, timestamps, or random suffixes to resolve collisions. Present the collision and ask the user to approve a revised `Epic ID` or issue slug.

Before the Worktree Map Gate, check:

```bash
git worktree list
git branch --format='%(refname:short)'
```

Also check that every proposed filesystem path does not already exist unless it is the exact approved worktree for the same Epic ID and local issue. Stop if the `Epic ID` or proposed path collides with another active epic.

## Worktree Map

Propose this table before creating worktrees, and record it after approval:

```markdown
| Wave | Epic ID | ローカルIssue | GitHub Issue | ブランチ | 作業ツリー | Owner/Agent | Write Scope | ベース | 実行状態 | 準備状態 | 検証 | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W1 | <epic-id> | G2PR-001 | #123 または ローカルのみ | codex/<epic-id>/G2PR-001-<issue-slug> | <worktree-root>/<repo-name>/<epic-id>/G2PR-001-<issue-slug> | <agent/thread id または 未割当> | <paths/modules> | <sha> | 実行可能 | 準備済み | <commands> | 未実施 | 未作成 |
```

Use the repo's documented branch prefix or worktree root if it differs, but do not remove the `Epic ID` namespace.

Do not include `ブロック中` issues in the proposed worktree map unless the user explicitly overrides the blocker. Do not run `git worktree add` until the user approves the proposed map.

## Approval Gates

Run these gates in order:

1. **Spec Gate**: Present the spec path, Epic ID, accepted decisions, non-goals, acceptance criteria, verification commands, and stop conditions. Wait for explicit approval before local issue decomposition.
2. **Issue Gate**: Present Japanese local issues with Epic ID, blocker graph, dependency order, `実行可能/ブロック中` status, and acceptance criteria. Wait for explicit approval before GitHub mirroring or worktree planning.
3. **GitHub Mirror Gate**: Optional. If the user wants remote tracking, present the exact local issues to publish, including blocked tracking issues if any, and wait for explicit approval before creating GitHub issues.
4. **Worktree Map Gate**: Present Epic ID, proposed branch/worktree paths, collision-check evidence, base commit, and dependency constraints. Wait for explicit approval before creating worktrees.
5. **Initial Verification Gate**: Run lightweight verification, summarize current artifacts, and wait for explicit approval before starting Goal loops.

Approval must be specific to the current gate packet. Vague approval from an earlier gate does not authorize later remote writes, worktree creation, pushes, or PR creation.

## Parallelization Rules

- Parallelize only `実行可能` issues with no dependency edge between them.
- Assign exactly one worktree per agent/thread.
- Do not let two agents edit the same worktree.
- Do not let two active epics share the same branch namespace or worktree path namespace.
- Do not put issues with overlapping write scopes in the same wave.
- Keep shared docs changes in a parent/prep issue when possible; otherwise serialize them.
- Treat the local issue ledger, wave state, and shared worktree map as coordinator-owned unless a specific issue explicitly owns them.
- Rebase or merge only after checking the repo's contribution policy.
- Do not start a dependent branch until its blocker is complete unless the user explicitly approves stacked/dependent PR work.

## Parallel Goal Loop Scheduler

After the Initial Verification Gate, run implementation by parallel wave rather than by a single serial loop.

Definitions:

- **Runnable issue**: `レビュー状態: 承認済み`, `実行状態: 実行可能`, no incomplete blockers, and no unresolved stop condition.
- **Parallel wave**: a set of runnable issues with no dependency edge between them and no overlapping write scope.
- **Coordinator-owned state**: local issue ledger, worktree map, wave status, shared progress docs, and any other file used to coordinate multiple workers.

Scheduler steps:

1. Recompute runnable issues from the approved local ledger.
2. Exclude any issue whose write scope overlaps with another candidate; put the lower-priority or dependent issue into a later wave.
3. Assign a wave ID such as `W1`, `W2`, and exactly one epic-scoped branch/worktree/owner per issue.
4. Display a launch packet in the parent session before dispatch:

```markdown
## Parallel Wave Launch

| Wave | Epic ID | ローカルIssue | Branch | Worktree Path | Owner/Agent | Write Scope |
| --- | --- | --- | --- | --- | --- | --- |
| W1 | <epic-id> | G2PR-001 | codex/<epic-id>/G2PR-001-<issue-slug> | /abs/path/to/<repo-name>/<epic-id>/G2PR-001-<issue-slug> | <agent/thread id> | <paths/modules> |
```

5. Dispatch every issue in the wave in parallel when the platform supports parallel agents or background threads.
6. Give each worker only its issue, branch, worktree path, write scope, source docs, verification commands, and stop conditions.
7. Tell each worker it is not alone in the codebase, must not revert other workers' changes, and must not edit coordinator-owned state unless explicitly assigned.
8. If the platform cannot create independent agents/threads, stop and ask whether to run serially or switch to a parallel-capable surface.
9. When a worker reports implementation complete, inspect its result, run or record required verification, and run the Issue Implementation Review Gate before updating issue completion or releasing blockers from the parent session.
10. After all workers in the wave finish, update blocker status, recompute runnable issues, and start the next wave.

Worker completion reports must include:

- Local issue ID and title.
- Epic ID.
- Worktree path and branch.
- Changed files.
- Verification commands and results.
- Commit SHA when committed.
- Issue implementation review state, review range, reviewer or manual fallback, verdict, fixed Critical/Important findings, and accepted residual risks.
- PR readiness and known risks.
- Blockers released or new blockers discovered.

## Review Gate Packet

Before Goal loops, present:

- Spec path and summary of accepted decisions.
- Issue list with blocker graph, `実行可能/ブロック中` status, and dependency order.
- Worktree map with Epic ID, wave ID, owner/agent, write scope, and absolute worktree path for every task.
- Collision-check evidence from `git worktree list`, branch names, and proposed filesystem paths.
- Verification already run.
- Exact question: whether the user approves starting implementation loops.

Do not proceed on vague approval. Require approval of the current packet.

## Issue Implementation Review Gate

Run this gate after a worker's fresh final verification and before local issue completion, blocker release, or PR creation. This is separate from PR review and later check monitoring.

Review scope is intentionally narrow. The reviewer may report only findings that show the implementation is missing, contradicts, or does not sufficiently prove something from the approved local issue, requirements, spec, acceptance criteria, non-goals, or write scope. Do not request general code quality, architecture, style, performance, refactor, documentation, or "ideal implementation" changes unless the concern directly proves one of those source artifacts is unmet. If a broader observation is not tied to an explicit source artifact, omit it from the findings.

Default path:

1. Confirm the local issue is still `レビュー状態: 承認済み` and `実行状態: 実行可能`, or that the user explicitly approved an override.
2. Confirm the worktree contains only the issue's scoped changes and no unassigned coordinator-owned state changes.
3. Create or update a scoped local commit for the issue. This local commit is not a remote write.
4. Set `BASE_SHA` to the worktree map's `ベース` commit and `HEAD_SHA` to the current issue head.
5. Use `superpowers:requesting-code-review` when available. If it is unavailable or no independent reviewer/subagent can run, stop and ask whether to install/enable it or approve a manual review fallback.
6. Send the reviewer a packet that includes:
   - local issue ID/title and GitHub issue URL or `ローカルのみ`
   - spec / PRD / ADR / glossary paths
   - acceptance criteria, non-goals, and write scope
   - verification commands and results
   - `BASE_SHA` and `HEAD_SHA`
   - exact review intent: `<local issue id> の実装について、issue / 要件 / 仕様 / 受け入れ条件 / write scope から漏れている、逸脱している、または検証証跡が不足している点だけを指摘してください。一般的な code quality、architecture、style、performance、refactor、documentation、理想実装の提案は、明示された source artifact の未達を示す場合だけ指摘してください。`
7. Record the ledger state as `実装レビュー: 依頼済み`.
8. Fix every Critical and Important in-scope finding, or stop for explicit human risk acceptance. After fixes, rerun targeted verification and fresh final verification, update the local commit, and rerun review with the same base and new head.
9. Minor in-scope findings may remain only when they are recorded in `レビュー結果` with a reason. Out-of-scope observations must not be recorded as findings.
10. Mark `実装レビュー: 承認済み` for reviewer approval, or `手動レビュー済み` only when the user approved manual fallback and the same packet was reviewed manually.
11. Record `レビュー範囲`, `レビュー結果`, reviewer or fallback, fixed in-scope findings, and any risk acceptance before marking the issue complete or releasing blockers.

Manual fallback is not a silent downgrade. If the user does not explicitly approve it, stop. PR review, CI checks, or a later GitHub review do not replace this gate.

## Goal Loop Definition

For each approved issue assigned to a worker:

1. Confirm the worktree path and branch.
2. Confirm the assigned Epic ID, wave ID, and exclusive write scope.
3. Re-read the issue and spec.
4. Confirm the issue is `実行可能`. If it is `ブロック中`, stop unless the user explicitly approved an override.
5. Do not edit coordinator-owned state such as the local issue ledger unless this issue explicitly owns that file.
6. Use `tdd` when the issue changes behavior, fixes bugs, refactors behavior-bearing code, or adds tests.
7. Write or update tests first when behavior changes.
8. Implement the narrowest change that satisfies the issue.
9. Run targeted verification.
10. Update issue-owned docs/progress required by the repo.
11. Run fresh final verification.
12. Commit only the issue's scoped changes locally so the review has a base/head range.
13. Run the Issue Implementation Review Gate.
14. Fix actionable in-scope findings; for Critical or Important in-scope findings, rerun targeted verification, fresh final verification, update the local commit, and repeat review or get explicit human risk acceptance.
15. Report completion data to the coordinator; the coordinator updates the local ledger with completion state, verification result, commit SHA, implementation review result, and remaining risk.
16. The coordinator marks completed blockers and updates dependent issues from `ブロック中` to `実行可能` only after implementation review passes.

If the platform has a native Goal command, use it with the short prompt and linked docs. If not, execute the same loop manually and report that no native Goal runner was available.

## PR Review Definition

Create PRs only after final verification, Issue Implementation Review Gate completion for every issue in the PR scope, and review fixes. Prefer draft PRs when multiple dependent branches remain in flight. Include:

- What changed.
- Spec, local issue, and remote issue links when available.
- ブロッカー状態と、必要な場合は stacked/dependent PR の関係.
- Verification results.
- Known risks.
- Dependency/stacking notes.

If a GitHub issue exists, link the PR with the repo's preferred closing syntax:

- Use `Closes #<n>` when merging the PR should close the issue.
- Use `Refs #<n>` when the PR is partial, stacked, exploratory, or should not auto-close the issue.

If no GitHub issue exists, include the local issue ID and ledger path instead. Do not create a remote issue during PR creation unless the user explicitly approves that remote write.

Push and PR creation are remote writes. Use the relevant GitHub/PR skill or repo convention only after explicit user approval for the current branch/issue. After PR creation succeeds, update the local ledger with the PR URL, PR state, issue linkage syntax, and any stacked/dependent PR relationship before reporting success. For blocked or dependent work, prefer stacked draft PRs only when the user explicitly approves stacked/dependent PR work and the blocker PR relationship is documented. After PR creation, inspect checks and actionable review comments. Fix only scoped feedback in the same worktree/branch. For broad redesign requests, return to Grill with Docs or spec update.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Skipping Grill with Docs because the design seems obvious | Run it or stop if unavailable. |
| Creating horizontal layer issues | Rewrite as vertical slices that are independently verifiable. |
| Writing issues in English by habit | Write issue titles, headings, labels, status values, and prose in Japanese; keep technical identifiers unchanged. |
| Leaving English labels in issue templates | Replace `Ready`, `Blocked`, `Blocked by`, `Blocks`, `None`, and `Not created` with `実行可能`, `ブロック中`, `ブロック元`, `ブロック先`, `なし`, and `未作成`; replace review values with `下書き`, `承認済み`, `差し戻し`, or `未解決`. |
| Treating blockers as notes only | Maintain `ブロック元`, `ブロック先`, and `実行可能/ブロック中` status in the local ledger. |
| Treating GitHub as the default issue source | Keep local issues canonical; mirror only after approval. |
| Letting `to-prd` or `to-issues` publish remotely before this workflow's gate | Use those skills for synthesis and review first; remote publication waits for explicit approval. |
| Creating GitHub issues or PRs without updating local issue state | Update the local ledger immediately; stop if local state cannot be reconciled. |
| Running same-wave issues serially by habit | Dispatch all runnable non-conflicting issues in the wave in parallel when the platform supports it. |
| Hiding worktree paths inside worker prompts | Display every wave member's absolute worktree path in the parent session before dispatch. |
| Letting workers update the shared local ledger concurrently | Keep coordinator-owned state in the parent session unless a specific issue owns that file. |
| Starting Goal loops before human review | Stop at the review packet and wait for approval. |
| Starting Goal loops for blocked issues | Wait until blockers complete or get explicit override for stacked/dependent work. |
| Treating PR review, CI checks, or GitHub review comments as a substitute for issue implementation review | Run the Issue Implementation Review Gate before local completion, blocker release, or PR creation. |
| Letting issue implementation review become a general code quality review | Limit findings to gaps against the approved issue, requirements, spec, acceptance criteria, write scope, or verification evidence. |
| Releasing blockers while Critical or Important in-scope implementation review findings remain unresolved | Fix the findings or record explicit human risk acceptance before completion. |
| Reusing one worktree for multiple parallel issues | Create isolated worktrees and branches. |
| Putting full specs into Goal prompts | Keep prompts short and link durable docs. |
| Treating PR creation as implicit | Get explicit approval first, then use the repo's PR skill/convention. |
