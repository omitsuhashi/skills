from __future__ import annotations

import re


EPIC_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ISSUE_RE = re.compile(r"^[A-Z0-9]+-[0-9]+$")
FULL_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$", re.IGNORECASE)
COMMIT_RANGE_RE = re.compile(
    r"^(?:[0-9a-f]{40}|[0-9a-f]{64})\.\.(?:[0-9a-f]{40}|[0-9a-f]{64})$",
    re.IGNORECASE,
)

EDGE_STRENGTHS = {"hard", "soft"}
RELEASE_ON = {
    "artifact_ready",
    "review_approved",
    "integrated",
    "pr_opened",
    "pr_merged",
    "human_decision",
    "external_condition",
}
BASE_EFFECTS = {"none", "branch_from_blocker_head", "branch_from_integration_head"}
BASE_POLICY_TYPES = {"epic_base", "blocker_head", "integration_head"}
WORKTREE_STATES = {"reserved", "create_on_run", "active", "missing"}
REMOTE_MODES = {"local_only", "per_action", "batch_draft_prs", "batch_issue_prs"}
DELIVERY_INTENTS = REMOTE_MODES
ISSUE_PR_BASES = {"epic_base.ref"}
ISSUE_PR_MERGE_POLICIES = {"agent_default_with_human_escalation"}
FINAL_PR_HEADS = {"epic_base.ref"}
FINAL_PR_MERGE_POLICIES = {"human_only"}
MAX_REVIEW_CYCLES = 2
APPROVED_REVIEW_STATUSES = {"approved", "承認済み"}

ACTIVE_STATUSES = {"RUNNING", "FIXING"}
TERMINAL_STATUSES = {"PR_READY", "COMPLETE", "DONE", "FAILED", "CANCELLED"}
SUCCESS_STATUSES = {"PR_READY", "COMPLETE", "DONE"}
REVIEWABLE_STATUSES = {"IMPLEMENTED", "VERIFICATION_PASSED"}
WAITING_STATUSES = {"WAITING_HUMAN"}
