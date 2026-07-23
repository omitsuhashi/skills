# Execution Handoff

Use this reference when preparing the normalized input packet, presenting the Execution Plan Gate, or handing approved issue work to `issue-implementation-loop`.

## Branch / Base / Commit Policy

Use an optional planning branch, immutable `epic_base.sha`, one reservation per issue, typed dependencies, and local `PR_READY`. Issue PRs target `epic_base.ref`; final PR targets `main` and merge is human-only.

The tracked/runtime identity boundary is strict: planning artifacts/gate commits are tracked; Git-common-dir `planning-worktree.json` is host-specific and untracked. Keep `epic_base`, issues, reservations, and execution runtime separate.

Issue branches use `codex/<epic-id>/<local-id>-<slug>`; blocked worktrees remain uncreated until release.

Codex phase branch policy: gate planning artifacts on the current planning branch; workers inherit but do not author them. Envelope v4 carries `approved_spec_binding` and `phase_branch_policy`; a fresh/compacted coordinator owns execution resources.

Base policies: `epic_base` branches from `codex/<epic-id>/epic-base`, `blocker_head` from exactly one prerequisite issue head, and `integration_head` from an approved integration work item. Do not let a downstream worker merge multiple blocker heads; add an integration work item.

Commit policy:

Run targeted and fresh final verification. Create or update a scoped local commit before issue implementation review. Review committed `BASE_SHA..HEAD_SHA`, not `working-tree`. After fixes, rerun verification and update the commit/head before re-review. Run at most two issue implementation review cycles; if the second still has in-scope findings, stop and ask the human.

## Normalized Execution Packet

Build an Input Packet v2 file for `issue-implementation-loop`; use a file instead of prompt paste. The unsealed draft contains:

- `schema_version: 2`, `epic_id`, and repo-relative `artifact_root`
- `work_items[]` with ID, title, source, acceptance criteria, non-goals, verification, write scope, and dependencies
- `delivery_intent`

`work_items[].title`、`acceptance_criteria`、`non_goals` などの user-facing packet string は日本語をベースにする。schema key、path、command、ID、外部参照は維持する。

Use the prerequisite-derived `<issue-implementation-loop-skill-dir>` from the planning contract. Seal with the exact approved revision and approval record:

```bash
python3 <issue-implementation-loop-skill-dir>/scripts/approved_spec_binding.py seal \
  --repo-root <repo-root> \
  --draft-packet <repo-relative-draft-packet> \
  --output-packet <repo-relative-sealed-packet> \
  --spec-path <repo-relative-spec-path> \
  --spec-sha256 <approved-raw-byte-sha256> \
  --decision approved \
  --subject spec_binding \
  --actor-expression <actor-expression> \
  --approved-at <timezone-qualified-rfc3339> \
  --approve-scope accepted_decisions \
  --approve-scope non_goals \
  --approve-scope acceptance_criteria \
  --approve-scope verification \
  --approve-scope remote_policy \
  --approve-scope stop_conditions
```

Seal re-reads the spec, atomically writes `spec_binding` and `approval_evidence`, and never edits the spec. Never hand off an invalid sealed output.

Packet drift has three outcomes. Exact restoration of unintended packet byte drift plus fresh validation retains the existing approved binding, Envelope revision, and runtime epoch. An intended non-spec packet byte change goes through the Execution Plan Gate for reconciliation and revalidation, a new reseal, and a new Envelope revision and runtime epoch, without a new human Spec Gate approval. A change to spec bytes, `spec_binding`, or `approval_evidence` goes through the human Spec Gate for a new approval and seal, then a new Envelope revision and runtime epoch. The non-spec route is exhaustive: execution-intent-only packet drift—issue scope, dependencies, write scope, or delivery intent—is only an example; any other sealed packet byte drift while `spec_binding` and `approval_evidence` remain exact follows it, including other packet fields and serialization or whitespace-only drift. On that route, reseal only when the changed bytes are intended; exact restoration reuses the seal. Old downstream artifacts do not cross either new-seal epoch.

Commit the four durable planning files. Then create the untracked Execution Envelope v4, pinning the packet digest and full gate commit; execution owns its lifecycle.

## Implementation Context Handoff

Before handoff, compact planning or use a fresh execution coordinator; never implement from expanded planning context. Start from the normalized packet, a bounded handoff brief (scope, dependencies, write scopes, verification, stops, policy), and durable spec/ledger paths. The brief is cache; reconcile conflicts to packet, ledger, and envelope.

## Review Governance Handoff

The Envelope carries `review_policy.hardening_candidates`: registry `decisions/hardening-candidates.json`, max `5` candidates/issue and `80` summary words, `issue_completion_blocking=false`, `ready_or_merge_requires_decisions=true`, `worker_packet_decision_state=forbidden`. Runtime owns records/decisions; worker packet text may name paths but no candidate decision state. Routine review checks intent fit, regression, and current PR risk; the planning/grill session must not become an implementation worker.

## Execution Plan Gate

Present packet path, capability preflight, issue list, write scopes, dependencies, delivery intent, `epic_base`, branch/worktree reservations, base policies, reviewer/fallback policy, parallel/serial fallback, remote-write policy, issue PR policy, and final PR human-only merge policy.

Leave durable evidence before auto-continuation: normalized packet path and validation result, capability preflight, approved write scope, dependency graph, `phase_branch_policy`, and remote policy summary.

Validate with:

```bash
python3 <issue-implementation-loop-skill-dir>/scripts/validate_input_packet.py <packet.json>
python3 <issue-implementation-loop-skill-dir>/scripts/check_capabilities.py --input <packet.json> --json
```

When Spec Gate and Issue Gate already approved scope, auto-continue without another human approval if `validate_input_packet.py` and capability preflight pass, scope stays approved, and remote policy has no unapproved external write or high-risk action.

After Execution Plan Gate approval or auto-continue, commit durable artifacts, packet/evidence, ledger, and `knowledge/log.md`. Then run `issue-implementation-loop prepare` from a fresh or compacted coordinator context; exclude its instantiated artifacts.

Stop instead of auto-continuing if the approved scope would change, dirty changes overlap planned write scope, capability preflight fails, worker context is unavailable, or the observed remote policy does not match the approved remote policy.

## Execution Coordinator

After the gate, load `issue-implementation-loop`: `prepare` validates envelope/reservations; `execute` schedules work/review/fix; `resume` reconciles; `status` reports; `deliver` prepares approved remote delivery. A fresh/compacted coordinator owns these operations and ledger consistency; planning/grill never implements. Without worker contexts, stop.
