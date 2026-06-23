# Core Contract

Use this skill only after issues and acceptance criteria are approved. The parent coordinator owns:

- input packet and approved Execution Envelope
- append-only event log and mutable runtime snapshot
- blocker release and human request routing
- issue completion and PR-ready decisions
- final report and remote-write approval boundary

Workers own only their assigned issue worktree, branch, write scope, and verification evidence. Reviewers own only review findings for the issue packet they receive.

## Input Packet

Normalize local or remote issues before execution:

```json
{
  "schema_version": 1,
  "repo_root": "/abs/path/to/repo",
  "epic_id": "issue-implementation-loop",
  "artifact_root": "knowledge/wiki/syntheses/issue-implementation-loop",
  "spec": {
    "path": "knowledge/wiki/syntheses/spec.md",
    "approved_revision": 1,
    "approved_hash": "sha256:..."
  },
  "work_items": [
    {
      "id": "G2PR-001",
      "title": "短い日本語タイトル",
      "source": {"type": "local", "path": "knowledge/wiki/syntheses/issues.md"},
      "acceptance_criteria": ["observable condition"],
      "non_goals": ["excluded behavior"],
      "verification": ["python3 -m unittest discover -s tests"],
      "write_scope": ["path:skills/example"],
      "dependencies": []
    }
  ],
  "delivery_intent": "local_only"
}
```

Validate with:

```bash
python3 <skill-dir>/scripts/validate_input_packet.py <packet.json>
```

## Output Contract

Return a local execution result:

```json
{
  "schema_version": 1,
  "epic_id": "issue-implementation-loop",
  "status": "local_complete",
  "envelope_revision": 1,
  "issues": {
    "G2PR-001": {
      "status": "PR_READY",
      "branch": "codex/issue-implementation-loop/G2PR-001-example",
      "worktree": "/abs/worktree",
      "base_sha": "abc123",
      "head_sha": "def456",
      "verification": "passed",
      "implementation_review": "approved",
      "residual_risks": []
    }
  },
  "pending_human_requests": [],
  "delivery_candidates": ["G2PR-001"],
  "runtime_state_root": "/repo/.git/agent-runs/issue-implementation-loop/issue-implementation-loop"
}
```

## Non-Goals

- Do not create or redesign issues.
- Do not create a generic workflow framework.
- Do not route work through a separate LLM node scheduler.
- Do not perform remote writes unless the envelope and the human both approve the exact action.
