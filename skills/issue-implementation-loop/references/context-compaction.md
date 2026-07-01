# Execution Context Compaction

This contract keeps execution resumable without carrying raw transcript or bulky worker artifacts across phase boundaries. It does not change scheduler, runtime-state, event ordering, delivery, review, or worker semantics.

## Policy Source

`Execution Envelope.context_policy.session_compaction` is the session-level policy. It is required for schema version `2` envelopes. Legacy schema version `1` envelopes may omit it when they predate this contract. When present, it must contain:

- `soft_trigger_percent: 65`
- `hard_stop_percent: 75`
- `mandatory_handoff_compaction: 1`
- `mandatory_phase_transition_gc: true`
- `carry_forward_capsule_words_default: 400`
- `carry_forward_capsule_words_hard: 600`
- `inline_json_code_diff_lines_hard: 80`

At 65% session pressure, start a checkpoint even before the next natural boundary. At 75%, do not enter a new phase, dispatch a worker, start a review/fix cycle, resume from cache, or open a remote gate until a carry-forward capsule exists or a fresh coordinator is started.

## Artifact Boundaries

- Execution Envelope: approved execution policy, source revisions, reservations, budgets, and remote-write boundary.
- Runtime state and events: canonical execution status, issue state, attempt/report/review events, human waits, and delivery state.
- Resume brief: bounded cache rebuilt from runtime sources; never canonical.
- Worker packet: paths-first issue dispatch. Its strict `context_policy` is packet-local only and must not include `session_compaction` or other session-level fields.
- Worker report and review report: evidence artifacts. Carry forward their paths, commit ranges, verdicts, and unresolved findings instead of full text.

## Phase Exit GC

At every `prepare`, `execute`, `review`, `resume`, and `deliver` exit, create a carry-forward capsule before moving on. The capsule may include only:

- current phase result and next operation
- canonical paths and revision/digest metadata
- affected issue IDs, branch/worktree, base/head SHA, and review range
- approval state, remote-write policy, human waits, blockers, and residual risks
- verification command/result summary and evidence paths
- `Pending hardening decisions: N` and `<runtime-root>/decisions/hardening-candidates.json` when unresolved candidates exist

Drop raw worker JSON, full worker report text, full review text, candidate full text, command output dumps, diff/patch text, stale drafts, rejected alternatives, and local implementation trial-and-error from carry-forward context after the phase exit. If needed later, reload the bounded source artifact by path and digest.

## Candidate Registry Carry-Forward

Hardening candidate state is carried by path, not by copied proposal text.
Carry forward only:

```text
Pending hardening decisions: N
Candidate registry: <runtime-root>/decisions/hardening-candidates.json
```

Do not paste candidate full text, rationale, suggested change, or decision
history into phase carry-forward capsules, resume briefs, worker packets, or
review packets. Reload `hardening-candidates.json` by path when the coordinator
needs the full decision surface.

## Required Phase Outcomes

- `prepare`: carry forward envelope path/revision/hash, runtime root, event log path, branch/worktree reservation summary, and unresolved envelope validation issues.
- `execute`: carry forward worker packet path, worker report path, changed file summary, commit SHA, verification result, and any scoped blocker.
- `review`: carry forward review range, verdict, Critical/Important findings, fix status, accepted residual risk, candidate count, and candidate registry path only.
- `resume`: validate or rebuild the resume brief, then carry forward runtime state, event log, freshness metadata, dirty-state summary, selected next operation, `Pending hardening decisions: N`, and candidate registry path.
- `deliver`: carry forward PR-ready branches, approved remote action set, skipped remote actions, final PR human-only boundary, and delivery evidence path.

## Worker Packet Strictness

Do not move this session policy into worker packets. `validate_worker_packet.py` must continue rejecting unknown `context_policy` fields such as `session_compaction`; worker packets keep only packet budget, read-path, and inline-excerpt controls.
