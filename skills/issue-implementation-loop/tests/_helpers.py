from __future__ import annotations

import importlib.util
import os
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL_FILE = SKILL_DIR / "SKILL.md"
SCRIPTS_DIR = SKILL_DIR / "scripts"
COMMON_SCRIPT = SCRIPTS_DIR / "_common.py"
ENVELOPE_SCHEMA_FILE = SKILL_DIR / "assets" / "schemas" / "execution-envelope.schema.json"
REPO_ROOT = SKILL_DIR.parents[1]
ASBC_GATE_COMMIT = "ad9adeab69bcafd761d8457e9c33d1b4c26096d5"
ASBC_PACKET_PATH = (
    "knowledge/wiki/syntheses/"
    "loop-skill-approved-spec-binding-contract-input-packet.json"
)
ASBC_PACKET_SHA256 = "3779e815b4be7438b36e9fb53073fa1d3ab20f07cd5ad1c531fa075c11b457e7"
BASE_SHA = "0123456789abcdef0123456789abcdef01234567"
HEAD_SHA = "89abcdef0123456789abcdef0123456789abcdef"
REVIEW_RANGE = f"{BASE_SHA}..{HEAD_SHA}"


def run_script(script_name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script_name), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def approved_spec_binding(
    *,
    path: str = ASBC_PACKET_PATH,
    sha256: str = ASBC_PACKET_SHA256,
    gate_commit: str = ASBC_GATE_COMMIT,
) -> dict[str, str]:
    return {"path": path, "sha256": sha256, "gate_commit": gate_commit}


def current_runtime(value: dict) -> dict:
    runtime = copy.deepcopy(value)
    runtime["schema_version"] = 2
    runtime.setdefault("approved_spec_binding", approved_spec_binding())
    for request in runtime.get("human_requests", []):
        if not isinstance(request, dict):
            continue
        request.setdefault("schema_version", 2)
        request.setdefault(
            "approved_spec_binding", copy.deepcopy(runtime["approved_spec_binding"])
        )
        request.setdefault("reason", "needs human decision")
    return runtime


def write_hardening_registry(path: Path, candidates: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(
        path,
        {
            "schema_version": 2,
            "approved_spec_binding": approved_spec_binding(),
            "epic_id": "issue-implementation-loop",
            "registry_path": str(path),
            "limits": {
                "hardening_candidate_summary_words_default": 80,
                "hardening_candidates_per_issue_default": 5,
            },
            "candidates": candidates,
        },
    )


def hardening_candidate(
    candidate_id: str,
    *,
    classification: str = "hardening_candidate",
    decision: str = "pending_decision",
    implementation_issue: str | None = None,
) -> dict:
    return {
        "candidate_id": candidate_id,
        "source_issue": "G2PR-001",
        "classification": classification,
        "summary": "Add a bounded delivery hardening guard.",
        "risk": "Low if deferred; source acceptance remains satisfied.",
        "estimated_scope": ["path:skills/issue-implementation-loop"],
        "decision": decision,
        "implementation_issue": implementation_issue,
        "delivery_blocker": classification == "safety_escalation",
    }


def load_common_module():
    spec = importlib.util.spec_from_file_location("issue_loop_common_under_test", COMMON_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def base_envelope() -> dict:
    return {
        "schema_version": 4,
        "epic_id": "issue-implementation-loop",
        "revision": 1,
        "approved_spec_binding": approved_spec_binding(),
        "epic_base": {
            "ref": "codex/approved-spec-binding-contract",
            "sha": git(REPO_ROOT, "rev-parse", "HEAD"),
        },
        "execution_policy": {
            "parallel_preferred": True,
            "serial_fallback_preapproved": True,
            "worker_context_required": True,
            "coordinator_may_implement": False,
            "serial_fallback_mode": "worker_context_only",
            "implementation_slots": 4,
            "review_slots": 2,
            "wave_is_barrier": False,
        },
        "review_policy": {
            "primary": "requesting-code-review",
            "fallbacks": ["manual"],
            "manual_fallback_preapproved": False,
            "max_review_cycles": 2,
            "max_fix_cycles": 2,
            "same_finding_limit": 2,
            "hardening_candidates": {
                "candidate_registry_path": "decisions/hardening-candidates.json",
                "max_candidates_per_issue": 5,
                "max_summary_words": 80,
                "issue_completion_blocking": False,
                "ready_or_merge_requires_decisions": True,
                "worker_packet_decision_state": "forbidden",
            },
        },
        "human_policy": {
            "default_scope": "issue",
            "epic_scope_requires_reason": True,
        },
        "context_policy": {
            "paths_first": True,
            "max_worker_packet_words": 450,
            "max_worker_report_words": 350,
            "include_full_spec_text": False,
            "include_full_ledger_text": False,
            "worker_packet_schema": "assets/schemas/worker-packet.schema.json",
            "worker_packet_template": "assets/templates/worker-packet.json",
            "worker_packet_validator": "scripts/validate_worker_packet.py",
            "session_compaction": {
                "soft_trigger_percent": 65,
                "hard_stop_percent": 75,
                "mandatory_handoff_compaction": 1,
                "mandatory_phase_transition_gc": True,
                "carry_forward_capsule_words_default": 400,
                "carry_forward_capsule_words_hard": 600,
                "inline_json_code_diff_lines_hard": 80,
            },
        },
        "phase_branch_policy": {
            "planning_artifacts_branch": "current_session_branch",
            "phase_approval_commit_required": True,
            "phase_transition_requires_clean_scope": True,
            "execution_coordinator_context": "fresh_or_compacted",
            "main_planning_session_may_implement": False,
            "worktree_per_issue": True,
            "branch_prefix": "codex",
            "epic_base_ref_pattern": "codex/<epic-id>/epic-base",
            "issue_branch_pattern": "codex/<epic-id>/<local-id>-<slug>",
            "epic_base_owner": "execution_coordinator",
            "issue_branch_owner": "worker",
            "integration_branch_policy": "approved_integration_work_item_only",
        },
        "remote_write_policy": {"mode": "local_only", "approved_actions": []},
        "work_items": {
            "G2PR-001": {
                "branch": "codex/issue-implementation-loop/G2PR-001-a",
                "worktree_path": "/tmp/skills/issue-implementation-loop/G2PR-001-a",
                "worktree_state": "create_on_run",
                "base_policy": {"type": "epic_base"},
                "write_scope": ["path:skills/a"],
                "dependencies": [],
            },
            "G2PR-002": {
                "branch": "codex/issue-implementation-loop/G2PR-002-b",
                "worktree_path": "/tmp/skills/issue-implementation-loop/G2PR-002-b",
                "worktree_state": "create_on_run",
                "base_policy": {"type": "epic_base"},
                "write_scope": ["path:skills/b"],
                "dependencies": [],
            },
            "G2PR-003": {
                "branch": "codex/issue-implementation-loop/G2PR-003-c",
                "worktree_path": "/tmp/skills/issue-implementation-loop/G2PR-003-c",
                "worktree_state": "reserved",
                "base_policy": {
                    "type": "blocker_head",
                    "issue": "G2PR-001",
                },
                "write_scope": ["path:skills/c"],
                "dependencies": [
                    {
                        "issue": "G2PR-001",
                        "strength": "hard",
                        "release_on": "review_approved",
                        "base_effect": "branch_from_blocker_head",
                    }
                ],
            },
        },
    }


def create_binding_repo(root: Path) -> tuple[Path, dict[str, str], str]:
    """Create a sealed packet/spec commit and return repo, binding, gate SHA."""

    repo = root / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test User")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "base")

    synthesis = repo / "knowledge/wiki/syntheses"
    synthesis.mkdir(parents=True)
    spec_path = synthesis / "spec.md"
    issues_path = synthesis / "issues.md"
    packet_path = synthesis / "input-packet.json"
    spec_path.write_text("approved spec\n", encoding="utf-8")
    issues_path.write_text("# Issues\n", encoding="utf-8")
    packet = current_input_packet(repo)
    write_json(packet_path, packet)
    packet_digest = hashlib.sha256(packet_path.read_bytes()).hexdigest()
    git(repo, "add", "knowledge")
    git(repo, "commit", "-q", "-m", "gate")
    gate_commit = git(repo, "rev-parse", "HEAD")
    binding = {
        "path": "knowledge/wiki/syntheses/input-packet.json",
        "sha256": packet_digest,
        "gate_commit": gate_commit,
    }
    return repo, binding, gate_commit


def binding_envelope(repo: Path, binding: dict[str, str], target: str | None = None) -> dict:
    envelope = base_envelope()
    envelope["epic_id"] = "approved-spec-binding"
    envelope["approved_spec_binding"] = copy.deepcopy(binding)
    envelope["epic_base"] = {
        "ref": git(repo, "branch", "--show-current") or "HEAD",
        "sha": target or git(repo, "rev-parse", "HEAD"),
    }
    envelope["work_items"] = {
        "ASBC-002": {
            "branch": "codex/approved-spec-binding/ASBC-002-workers",
            "worktree_path": str(repo),
            "worktree_state": "active",
            "base_policy": {"type": "epic_base"},
            "write_scope": ["path:skills/issue-implementation-loop"],
            "dependencies": [],
        }
    }
    return envelope


def write_binding_sources(
    repo: Path,
    binding: dict[str, str],
) -> tuple[Path, Path, Path]:
    envelope_path = repo / "execution-envelope.json"
    runtime_path = repo / "runtime-state.json"
    issue_source = repo / "knowledge/wiki/syntheses/issues.md"
    write_json(envelope_path, binding_envelope(repo, binding))
    write_json(
        runtime_path,
        {
            "schema_version": 2,
            "epic_id": "approved-spec-binding",
            "envelope_revision": 1,
            "approved_spec_binding": copy.deepcopy(binding),
            "issues": {},
            "human_requests": [],
        },
    )
    return envelope_path, runtime_path, issue_source


def current_worker_packet(
    repo: Path,
    binding: dict[str, str],
    *,
    task_kind: str = "implement",
) -> dict:
    envelope, runtime, issue_source = write_binding_sources(repo, binding)
    read_only = task_kind in {"review", "inspect"}
    return {
        "schema_version": 3,
        "packet_type": "issue_worker_dispatch",
        "task_kind": task_kind,
        "access_mode": "read_only" if read_only else "read_write",
        "source_revision": {
            "approved_spec_binding": copy.deepcopy(binding),
            "execution_envelope": {
                "path": str(envelope),
                "revision": 1,
                "sha256": hashlib.sha256(envelope.read_bytes()).hexdigest(),
            },
            "runtime_state": {
                "path": str(runtime),
                "envelope_revision": 1,
                "sha256": hashlib.sha256(runtime.read_bytes()).hexdigest(),
            },
            "issue_source": {
                "path": str(issue_source),
                "sha256": hashlib.sha256(issue_source.read_bytes()).hexdigest(),
            },
        },
        "epic_id": "approved-spec-binding",
        "issue_id": "ASBC-002",
        "issue_title": "Propagate binding through worker artifacts",
        "dispatch_id": f"dispatch-{task_kind}-001",
        "branch": "codex/approved-spec-binding/ASBC-002-workers",
        "worktree": str(repo),
        "write_scope": [] if read_only else ["path:skills/issue-implementation-loop"],
        "context_policy": {
            "paths_first": True,
            "max_packet_words": 450,
            "hard_max_packet_words": 800,
            "max_read_paths": 8,
            "max_inline_excerpt_words_per_file": 120,
            "max_inline_excerpt_words_total": 300,
            "include_full_spec_text": False,
            "include_full_ledger_text": False,
        },
        "read_paths": [
            {
                "path": "knowledge/wiki/syntheses/issues.md",
                "purpose": "issue-ledger",
            }
        ],
        "inline_context": [],
        "task": {
            "summary": "Propagate one approved binding.",
            "acceptance_criteria": ["Mismatched bindings are rejected."],
            "verification": ["python3 -m unittest"],
            "stop_conditions": ["Stop before remote writes."],
        },
        "report_contract": {
            "format": "worker-report.json",
            "validator": "skills/issue-implementation-loop/scripts/validate_worker_report.py",
        },
    }


def current_worker_report(
    repo: Path,
    binding: dict[str, str],
    packet: dict,
) -> dict:
    return {
        "schema_version": 2,
        "approved_spec_binding": copy.deepcopy(binding),
        "dispatch_id": packet["dispatch_id"],
        "epic_id": packet["epic_id"],
        "issue_id": packet["issue_id"],
        "branch": packet["branch"],
        "worktree": str(repo),
        "changed_files": ["skills/issue-implementation-loop/SKILL.md"],
        "verification": [{"command": "python3 -m unittest", "result": "passed"}],
        "base_sha": BASE_SHA,
        "head_sha": HEAD_SHA,
        "implementation_review": {"status": "approved", "range": REVIEW_RANGE},
        "status": "PR_READY",
        "residual_risks": [],
    }


def base_packet() -> dict:
    return {
        "schema_version": 1,
        "repo_root": "/tmp/repo",
        "epic_id": "issue-implementation-loop",
        "spec": {"path": "knowledge/wiki/syntheses/spec.md"},
        "work_items": [
            {
                "id": "G2PR-001",
                "title": "Example issue",
                "acceptance_criteria": ["observable behavior"],
                "verification": ["python3 -m unittest"],
                "write_scope": ["path:skills/example"],
                "dependencies": [],
            }
        ],
        "delivery_intent": "batch_issue_prs",
    }


def current_input_packet(repo: Path) -> dict:
    spec_path = "knowledge/wiki/syntheses/spec.md"
    digest = hashlib.sha256((repo / spec_path).read_bytes()).hexdigest()
    return {
        "schema_version": 2,
        "epic_id": "issue-implementation-loop",
        "artifact_root": "knowledge/wiki/syntheses",
        "spec_binding": {"path": spec_path, "sha256": digest},
        "approval_evidence": {
            "decision": "approved",
            "subject": "spec_binding",
            "actor_expression": "session-user",
            "approved_at": "2026-07-21T17:55:36+09:00",
            "scope": {
                "accepted_decisions": True,
                "non_goals": True,
                "acceptance_criteria": True,
                "verification": True,
                "remote_policy": True,
                "stop_conditions": True,
            },
        },
        "work_items": [
            {
                "id": "G2PR-001",
                "title": "Example issue",
                "source": {
                    "type": "local",
                    "path": "knowledge/wiki/syntheses/issues.md",
                },
                "acceptance_criteria": ["observable behavior"],
                "non_goals": ["remote write"],
                "verification": ["python3 -m unittest"],
                "write_scope": ["path:skills/example"],
                "dependencies": [],
            }
        ],
        "delivery_intent": "batch_issue_prs",
    }


def batch_issue_prs_envelope() -> dict:
    envelope = base_envelope()
    envelope["epic_base"]["ref"] = "codex/issue-implementation-loop/epic-base"
    envelope["epic_base"]["branch_state"] = "active"
    envelope["remote_write_policy"] = {
        "mode": "batch_issue_prs",
        "approved_actions": [],
        "issue_prs": {
            "base": "epic_base.ref",
            "merge": "agent_default_with_human_escalation",
        },
        "final_pr": {
            "head": "epic_base.ref",
            "base": "main",
            "merge": "human_only",
        },
    }
    return envelope


def merged_runtime_state(*, missing_merge: str | None = None) -> dict:
    issues = {}
    for issue_id in ("G2PR-001", "G2PR-002", "G2PR-003"):
        issues[issue_id] = {
            "status": "COMPLETE",
            "base_sha": BASE_SHA,
            "head_sha": HEAD_SHA,
            "review": {
                "status": "approved",
                "range": REVIEW_RANGE,
            },
            "pr": f"https://github.com/org/repo/pull/{issue_id.removeprefix('G2PR-')}",
            "pr_opened": True,
            "pr_merged": issue_id != missing_merge,
            "merge_commit": HEAD_SHA,
        }
    return {
        "schema_version": 2,
        "approved_spec_binding": approved_spec_binding(),
        "epic_id": "issue-implementation-loop",
        "envelope_revision": 1,
        "issues": issues,
        "human_requests": [],
    }


def current_execution_result(
    envelope: dict,
    runtime: dict,
    *,
    runtime_state_root: str = "/tmp/runtime-root",
) -> dict:
    issues = {}
    runtime_issues = runtime.get("issues", {})
    for issue_id in envelope.get("work_items", {}):
        record = copy.deepcopy(runtime_issues[issue_id])
        issues[issue_id] = {
            "status": record["status"],
            "branch": record.get("branch", envelope["work_items"][issue_id]["branch"]),
            "worktree": record.get(
                "worktree", envelope["work_items"][issue_id]["worktree_path"]
            ),
            "base_sha": record["base_sha"],
            "head_sha": record["head_sha"],
            "verification": "passed",
            "implementation_review": copy.deepcopy(record["review"]),
            "residual_risks": [],
        }
        for field in ("pr", "pr_opened", "pr_merged"):
            if field in record:
                issues[issue_id][field] = record[field]
    return {
        "schema_version": 2,
        "approved_spec_binding": copy.deepcopy(envelope["approved_spec_binding"]),
        "epic_id": envelope["epic_id"],
        "status": "local_complete",
        "envelope_revision": envelope["revision"],
        "epic_base": {
            "branch": envelope["epic_base"]["ref"],
            "initial_sha": envelope["epic_base"]["sha"],
            "current_sha": envelope["epic_base"]["sha"],
            "branch_exists": True,
        },
        "issues": issues,
        "pending_human_requests": copy.deepcopy(runtime.get("human_requests", [])),
        "delivery_candidates": list(envelope.get("work_items", {})),
        "runtime_state_root": runtime_state_root,
    }


def current_delivery_plan(
    envelope: dict,
    *,
    action: str = "final_pr",
    **fields: object,
) -> dict:
    plan = {
        "schema_version": 2,
        "approved_spec_binding": copy.deepcopy(envelope["approved_spec_binding"]),
        "action": action,
    }
    plan.update(fields)
    return plan
