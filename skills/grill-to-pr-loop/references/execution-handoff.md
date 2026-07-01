# Execution Handoff

Use this reference when preparing the normalized input packet, presenting the Execution Plan Gate, or handing approved issue work to `issue-implementation-loop`.

## Branch / Base / Commit Policy

Do not model the run as a mutable development main branch. Use optional planning branch, per-epic `epic_base.ref` (`codex/<epic-id>/epic-base`) with immutable `epic_base.sha` and delivery `branch_state`, one branch/worktree reservation per issue, typed dependencies, and local `PR_READY` until remote delivery is approved. Issue PRs target `epic_base.ref`; final PR targets `main` and final merge is human-only.

Use branch names like `codex/<epic-id>/<local-id>-<slug>`. Blocked issues may reserve names/paths, but physical worktrees stay absent until release.

Base policies:

- `epic_base`: branch from `codex/<epic-id>/epic-base` at the recorded base head.
- `blocker_head`: branch from exactly one prerequisite issue head.
- `integration_head`: branch from an approved integration work item / branch.

Do not let a downstream worker merge multiple blocker heads; add an integration work item instead.

Commit policy:

- Run targeted verification and fresh final verification.
- Create or update a scoped local commit before issue implementation review.
- Review committed `BASE_SHA..HEAD_SHA`; do not use `working-tree` as the new PR-ready review head.
- After fixes, rerun verification and update the commit/head before re-review.
- Run at most two issue implementation review cycles; if the second review still has in-scope findings, stop and ask the human.

## Normalized Execution Packet

Build a normalized input packet file for `issue-implementation-loop`; use a file instead of prompt paste. Include:

- `schema_version`, `repo_root`, `epic_id`, optional `artifact_root`
- `spec.path`, plus approved revision/hash when available
- `work_items[]` with ID, title, source, acceptance criteria, non-goals, verification, write scope, and dependencies
- `delivery_intent`

`work_items[].title`、`acceptance_criteria`、`non_goals` などの user-facing packet string は日本語をベースにする。schema key、path、command、ID、外部参照は維持する。

Use the input-packet template/schema and validate through `issue-implementation-loop/scripts/validate_input_packet.py`.

## Implementation Context Handoff

Do not begin implementation from the expanded main planning context. Before handoff, compact the planning session or switch to a fresh execution coordinator.

The execution side starts from:

- the normalized packet path
- a compressed handoff brief with approved scope, dependency order, write scopes, verification, stop conditions, and local/remote policy
- durable spec and ledger paths, not pasted full source text

The handoff brief is cache, not canonical state. If it conflicts with packet, ledger, or envelope, reconcile durable artifacts first.

## Review Governance Handoff

The Execution Envelope carries minimal `review_policy.hardening_candidates`: registry path `decisions/hardening-candidates.json`, max `5` candidates per issue, max `80` summary words, `issue_completion_blocking=false`, `ready_or_merge_requires_decisions=true`, and `worker_packet_decision_state=forbidden`.

This is policy only. Runtime owns candidate records and decisions; worker packets may name paths/instructions but not candidate decision state. Routine review packets ask for only three automatic checks: issue intent fit, implementation regression, and current PR delivery risk. Do not solicit future-only hardening or classification-only passes. Record `hardening_candidate` or `classification_needed` only when needed by an encountered finding or explicitly requested by the human. The planning/grill session must not become an implementation worker; it hands off to `issue-implementation-loop`.

## Execution Plan Gate

Present packet path, capability preflight, issue list, write scopes, dependencies, delivery intent, `epic_base`, branch/worktree reservations, base policies, reviewer/fallback policy, parallel/serial fallback, remote-write policy, issue PR policy, and final PR human-only merge policy.

Leave durable evidence before auto-continuation: normalized packet path and validation result, capability preflight, approved write scope, dependency graph, and remote policy summary.

Validate with:

```bash
python3 skills/issue-implementation-loop/scripts/validate_input_packet.py <packet.json>
python3 skills/issue-implementation-loop/scripts/check_capabilities.py --input <packet.json> --json
```

When Spec Gate and Issue Gate already approved scope, auto-continue without another human approval if `validate_input_packet.py` and capability preflight pass, scope stays approved, and remote policy has no unapproved external write or high-risk action.

After Execution Plan Gate approval or auto-continue, commit approved artifacts, packet/evidence boundary, local ledger, and `knowledge/log.md`. Then run `issue-implementation-loop prepare`.

Stop instead of auto-continuing if the approved scope would change, dirty changes overlap planned write scope, capability preflight fails, worker context is unavailable, or the observed remote policy does not match the approved remote policy.

## Execution Coordinator

After the Execution Plan Gate, load `issue-implementation-loop`: `prepare` validates envelope/reservations; `execute` schedules implementation/review/fix; `resume` reconciles; `status` reports; `deliver` prepares approved remote delivery.

Recommended context split:

1. The planning/grill session creates the approved packet and envelope, then stops doing implementation work.
2. An execution coordinator runs `prepare`, `execute`, `resume`, and `status`, dispatching bounded workers/reviewers.
3. PR delivery runs in `deliver` mode from the coordinator or fresh delivery context using completion artifact and runtime summary.

The workflow keeps final responsibility for ledger consistency, but the main planning/grill session must not become an implementation worker. If worker contexts are unavailable, stop before implementation.
