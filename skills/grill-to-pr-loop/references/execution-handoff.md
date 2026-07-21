# Execution Handoff

Use this reference when preparing the normalized input packet, presenting the Execution Plan Gate, or handing approved issue work to `issue-implementation-loop`.

## Branch / Base / Commit Policy

Do not model the run as a mutable development main branch. Use an optional planning branch, per-epic `epic_base.ref` with immutable `epic_base.sha`, one branch/worktree reservation per issue, typed dependencies, and local `PR_READY` until remote delivery is approved. Issue PRs target `epic_base.ref`; final PR targets `main` and final merge is human-only.

Use branch names like `codex/<epic-id>/<local-id>-<slug>`. Blocked issues may reserve names/paths, but physical worktrees stay absent until release.

Codex phase branch policy: keep planning artifacts on the current planning branch through gate commits; issue workers inherit but do not author them; create an Execution Envelope v4 with `approved_spec_binding` and `phase_branch_policy`; hand execution to a fresh or compacted coordinator context; let `issue-implementation-loop` own `epic_base.ref`, reservations, and integration work items.

Base policies: `epic_base` branches from `codex/<epic-id>/epic-base`, `blocker_head` from exactly one prerequisite issue head, and `integration_head` from an approved integration work item. Do not let a downstream worker merge multiple blocker heads; add an integration work item.

Commit policy:

Run targeted and fresh final verification. Create or update a scoped local commit before issue implementation review. Review committed `BASE_SHA..HEAD_SHA`, not `working-tree`. After fixes, rerun verification and update the commit/head before re-review. Run at most two issue implementation review cycles; if the second still has in-scope findings, stop and ask the human.

## Normalized Execution Packet

Build an Input Packet v2 file for `issue-implementation-loop`; use a file instead of prompt paste. The unsealed draft contains:

- `schema_version: 2`, `epic_id`, and repo-relative `artifact_root`
- `work_items[]` with ID, title, source, acceptance criteria, non-goals, verification, write scope, and dependencies
- `delivery_intent`

`work_items[].title`、`acceptance_criteria`、`non_goals` などの user-facing packet string は日本語をベースにする。schema key、path、command、ID、外部参照は維持する。

Seal the draft with `approved_spec_binding.py seal`, passing the approved repo-relative path, exact raw-byte SHA-256, actor expression/time, and all six `--approve-scope` values. Seal re-reads the spec, atomically writes required `spec_binding` and `approval_evidence`, and does not edit the spec. Then run `validate_input_packet.py`; never hand off an unsealed or invalid packet.

Commit the sealed packet and exact spec, then create an Execution Envelope v4 whose `approved_spec_binding` pins the packet digest and full gate commit. Any spec or packet byte drift requires human re-approval and a new seal/envelope/runtime epoch; old reviews and results do not carry forward.

## Implementation Context Handoff

Do not begin implementation from the expanded main planning context. Before handoff, compact the planning session or switch to a fresh execution coordinator.

The execution side starts from the normalized packet path, a compressed handoff brief with approved scope / dependency order / write scopes / verification / stop conditions / policy, and durable spec / ledger paths instead of pasted full source text.

The handoff brief is cache, not canonical state. If it conflicts with packet, ledger, or envelope, reconcile durable artifacts first.

## Review Governance Handoff

The Execution Envelope carries minimal `review_policy.hardening_candidates`: registry path `decisions/hardening-candidates.json`, max `5` candidates per issue, max `80` summary words, `issue_completion_blocking=false`, `ready_or_merge_requires_decisions=true`, and `worker_packet_decision_state=forbidden`.

This is policy only. Runtime owns records and decisions; worker packet text may name paths but not candidate decision state. Routine review checks issue intent fit, regression, and current PR delivery risk. The planning/grill session must not become an implementation worker.

## Execution Plan Gate

Present packet path, capability preflight, issue list, write scopes, dependencies, delivery intent, `epic_base`, branch/worktree reservations, base policies, reviewer/fallback policy, parallel/serial fallback, remote-write policy, issue PR policy, and final PR human-only merge policy.

Leave durable evidence before auto-continuation: normalized packet path and validation result, capability preflight, approved write scope, dependency graph, `phase_branch_policy`, and remote policy summary.

Validate with:

```bash
python3 skills/issue-implementation-loop/scripts/validate_input_packet.py <packet.json>
python3 skills/issue-implementation-loop/scripts/check_capabilities.py --input <packet.json> --json
```

When Spec Gate and Issue Gate already approved scope, auto-continue without another human approval if `validate_input_packet.py` and capability preflight pass, scope stays approved, and remote policy has no unapproved external write or high-risk action.

After Execution Plan Gate approval or auto-continue, commit approved artifacts, packet/evidence boundary, local ledger, and `knowledge/log.md`. Then run `issue-implementation-loop prepare` from a fresh or compacted coordinator context.

Stop instead of auto-continuing if the approved scope would change, dirty changes overlap planned write scope, capability preflight fails, worker context is unavailable, or the observed remote policy does not match the approved remote policy.

## Execution Coordinator

After the Execution Plan Gate, load `issue-implementation-loop`: `prepare` validates envelope/reservations; `execute` schedules implementation/review/fix; `resume` reconciles; `status` reports; `deliver` prepares approved remote delivery.

Context split: the planning/grill session creates the approved packet and envelope, then stops implementation work; an execution coordinator runs `prepare`, `execute`, `resume`, and `status`; PR delivery runs in `deliver` mode from the coordinator or fresh delivery context.

The workflow keeps final responsibility for ledger consistency, but the main planning/grill session must not become an implementation worker. If worker contexts are unavailable, stop before implementation.
