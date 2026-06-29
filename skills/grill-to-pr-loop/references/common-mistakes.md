# Common Mistakes

Use this reference when behavior is ambiguous, an agent tries to skip a gate, or a run looks like it is drifting from the workflow contract.

| Mistake | Correction |
| --- | --- |
| Skipping Grill with Docs because the design seems obvious | Run it or stop if unavailable. |
| Keeping execution mechanics in this skill | Move worktree/scheduler/runtime/recovery/review loop details to `issue-implementation-loop`. |
| Implementing issue code in the planning/grill session | Stop and hand off to an execution coordinator with worker contexts. |
| Creating horizontal layer issues | Rewrite as vertical slices that are independently verifiable. |
| English spec/PRD | Use Japanese; preserve IDs/paths/schema keys. |
| Writing generated issue labels in English | Use Japanese labels/status values; keep code symbols and paths unchanged. |
| Treating GitHub as the default issue source | Keep local issues canonical; mirror only after approval. |
| Letting `to-prd` or `to-issues` publish remotely before the gate | Use them for local synthesis/review first. |
| Creating GitHub issues or PRs without updating the ledger | Update the local ledger immediately. |
| Moving to the next phase without committing an approved gate | Commit the approved local artifacts and ledger/log updates after Spec Gate, Issue Gate, and Execution Plan Gate approval. |
| Starting execution without a validated input packet | Validate and present the Execution Plan Gate first. |
| Treating a planning branch as the execution source of truth | Pin `epic_base` in the envelope and reserve issue branches/worktrees. |
| Merging multiple blocker heads inside a downstream worker | Create an approved integration work item or integration branch. |
| Marking an issue PR-ready from an uncommitted diff | Create/update a scoped local commit and review `BASE_SHA..HEAD_SHA`. |
| Treating PR review as issue implementation review | Let `issue-implementation-loop` run the issue-scoped review gate before PR readiness. |
| Treating PR creation as implicit | Get explicit approval first. |
| Merging final PRs automatically | Create the final PR, then leave final merge to the human. |
