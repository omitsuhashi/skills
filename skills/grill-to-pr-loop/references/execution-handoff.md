# Execution Handoff

Use this reference when preparing the normalized input packet, presenting the Execution Plan Gate, or handing approved issue work to `issue-implementation-loop`.

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

## Normalized Execution Packet

Build a normalized input packet file for `issue-implementation-loop`; do not paste the packet body into the prompt when a file can hold it. Include:

- `schema_version`, `repo_root`, `epic_id`, optional `artifact_root`
- `spec.path`, plus approved revision/hash when available
- `work_items[]` with ID, title, source, acceptance criteria, non-goals, verification, write scope, and dependencies
- `delivery_intent`

`work_items[].title`、`acceptance_criteria`、`non_goals` などの user-facing packet string は日本語をベースにする。schema key、path、command、ID、外部参照は維持する。

Use `issue-implementation-loop/assets/templates/input-packet.json` for the concrete shape and `issue-implementation-loop/assets/schemas/input-packet.schema.json` for the field contract. Validate it through `issue-implementation-loop/scripts/validate_input_packet.py` before execution.

## Implementation Context Handoff

Do not begin implementation from the expanded main planning context. Before approved implementation handoff, either perform context 圧縮 of the main planning session or switch to a fresh execution coordinator.

The execution side starts from:

- the normalized packet path
- a compressed handoff brief with approved scope, dependency order, write scopes, verification, stop conditions, and local/remote policy
- durable spec and ledger paths, not pasted full source text

The handoff brief is a bounded bridge, not canonical state. If it conflicts with the normalized packet, approved ledger, or Execution Envelope, stop and reconcile those durable artifacts first.

## Execution Plan Gate

Build and present:

- normalized input packet path
- `issue-implementation-loop` capability preflight result
- issue list, write scopes, dependencies, and delivery intent
- `epic_base`, branch/worktree reservations, and base policies
- reviewer capability and approved fallback policy
- parallel/serial fallback policy
- remote-write policy
- issue PR base/merge policy and final PR human-only merge policy

Leave durable evidence before auto-continuation:

- normalized packet path and validation result
- capability preflight evidence
- approved write scope
- dependency graph
- remote policy summary

Validate with:

```bash
python3 skills/issue-implementation-loop/scripts/validate_input_packet.py <packet.json>
python3 skills/issue-implementation-loop/scripts/check_capabilities.py --input <packet.json> --json
```

When Spec Gate and Issue Gate already approved the scope, auto-continue without another human approval if `validate_input_packet.py` and capability preflight pass, the run stays inside the approved write scope, and the remote policy summary contains no unapproved external write or high-risk action.

After Execution Plan Gate approval or auto-continue decision, commit the approved artifacts, normalized packet/evidence boundary, local ledger, and `knowledge/log.md` updates. Then run `issue-implementation-loop prepare`.

Stop instead of auto-continuing if the approved scope would change, dirty changes overlap planned write scope, capability preflight fails, worker context is unavailable, or the observed remote policy does not match the approved remote policy.

## Execution Coordinator

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
