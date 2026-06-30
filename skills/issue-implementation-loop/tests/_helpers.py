from __future__ import annotations

import importlib.util
import os
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


def load_common_module():
    spec = importlib.util.spec_from_file_location("issue_loop_common_under_test", COMMON_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def base_envelope() -> dict:
    return {
        "schema_version": 2,
        "epic_id": "issue-implementation-loop",
        "revision": 1,
        "epic_base": {"ref": "main", "sha": BASE_SHA},
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
        "schema_version": 1,
        "epic_id": "issue-implementation-loop",
        "envelope_revision": 1,
        "issues": issues,
        "human_requests": [],
    }
