from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .constants import ACTIVE_STATUSES, REVIEWABLE_STATUSES, SUCCESS_STATUSES
from .io import load_json
from .review import review_approved_or_accepted
from .scheduler import compute_next_actions
from .validation.execution_envelope import validate_execution_envelope
from .validation.runtime_state import validate_runtime_state


DEFAULT_MAX_WORDS = 600
DEFAULT_OUTPUT_NAME = "resume-brief.md"
MISSING_ENVELOPE = "unavailable - execution envelope missing"


class ResumeBriefError(Exception):
    """Base error for resume brief generation."""


class ResumeBriefBudgetError(ResumeBriefError):
    def __init__(self, word_count: int, max_words: int) -> None:
        self.word_count = word_count
        self.max_words = max_words
        super().__init__(
            f"RESUME_BRIEF_WORD_BUDGET_EXCEEDED: {word_count} words exceeds {max_words}"
        )


class ResumeBriefInputError(ResumeBriefError):
    pass


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _copy_issue_metadata(record: dict[str, Any], event: dict[str, Any]) -> None:
    for field in ("branch", "worktree", "base_sha", "head_sha"):
        value = event.get(field)
        if isinstance(value, str):
            record[field] = value


def _apply_event(state: dict[str, Any], event: dict[str, Any]) -> None:
    event_type = event.get("type")
    issue = event.get("issue")
    if event.get("epic_id") and not state.get("epic_id"):
        state["epic_id"] = event["epic_id"]
    if event.get("envelope_revision") and not state.get("envelope_revision"):
        state["envelope_revision"] = event["envelope_revision"]

    if event_type == "issue_status_changed" and isinstance(issue, str):
        record = state["issues"].setdefault(issue, {})
        record["status"] = event.get("status", record.get("status", "PENDING"))
        _copy_issue_metadata(record, event)
    elif event_type == "review_status_changed" and isinstance(issue, str):
        record = state["issues"].setdefault(issue, {})
        _copy_issue_metadata(record, event)
        review = record.setdefault("review", {})
        review["status"] = event.get("status", review.get("status", "pending"))
        review_range = event.get("range") or event.get("review_range")
        if isinstance(review_range, str):
            review["range"] = review_range
    elif event_type == "pr_created" and isinstance(issue, str):
        record = state["issues"].setdefault(issue, {})
        _copy_issue_metadata(record, event)
        if isinstance(event.get("pr"), str):
            record["pr"] = event["pr"]
        record["pr_opened"] = True
    elif event_type == "pr_merged" and isinstance(issue, str):
        record = state["issues"].setdefault(issue, {})
        _copy_issue_metadata(record, event)
        if isinstance(event.get("pr"), str):
            record["pr"] = event["pr"]
        if isinstance(event.get("merge_commit"), str):
            record["merge_commit"] = event["merge_commit"]
        record["pr_opened"] = True
        record["pr_merged"] = True
    elif event_type == "human_request_opened":
        state["human_requests"].append(
            {
                key: value
                for key, value in event.items()
                if key in {"id", "scope", "issue", "resource", "reason", "created_at"}
            }
        )
    elif event_type == "human_request_resolved":
        request_id = event.get("id")
        state["human_requests"] = [
            request for request in state["human_requests"] if request.get("id") != request_id
        ]


def rebuild_state_from_events(events_path: Path) -> tuple[dict[str, Any], list[str]]:
    seen: set[str] = set()
    duplicate_events = 0
    warnings: list[str] = []
    state: dict[str, Any] = {
        "schema_version": 1,
        "epic_id": None,
        "envelope_revision": None,
        "issues": {},
        "human_requests": [],
    }

    with events_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ResumeBriefInputError(f"invalid events.jsonl line {line_number}: {exc}") from exc
            event_id = event.get("event_id")
            if not isinstance(event_id, str):
                warnings.append(f"events line {line_number} missing event_id")
                continue
            if event_id in seen:
                duplicate_events += 1
                continue
            seen.add(event_id)
            _apply_event(state, event)

    if state["epic_id"] is None:
        state["epic_id"] = "unknown"
    if state["envelope_revision"] is None:
        state["envelope_revision"] = 1
    if duplicate_events:
        warnings.append(f"{duplicate_events} duplicate event IDs ignored")
    return state, warnings


def _list_or_none(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _status_issues(runtime: dict[str, Any], statuses: set[str]) -> list[str]:
    issues = runtime.get("issues", {})
    if not isinstance(issues, dict):
        return []
    return sorted(
        issue_id
        for issue_id, record in issues.items()
        if isinstance(record, dict) and record.get("status") in statuses
    )


def _status_counts(runtime: dict[str, Any]) -> str:
    counts: dict[str, int] = {}
    for record in runtime.get("issues", {}).values():
        if not isinstance(record, dict):
            continue
        status = record.get("status", "PENDING")
        if isinstance(status, str):
            counts[status] = counts.get(status, 0) + 1
    return ", ".join(f"{status}={counts[status]}" for status in sorted(counts)) or "no issues"


def _runtime_event_inconsistencies(
    runtime: dict[str, Any], rebuilt: dict[str, Any]
) -> list[str]:
    inconsistencies: list[str] = []
    for field in ("epic_id", "envelope_revision"):
        runtime_value = runtime.get(field)
        rebuilt_value = rebuilt.get(field)
        if runtime_value != rebuilt_value:
            inconsistencies.append(
                f"runtime/events mismatch for {field}: runtime={runtime_value} events={rebuilt_value}"
            )

    runtime_issues = runtime.get("issues", {})
    rebuilt_issues = rebuilt.get("issues", {})
    if not isinstance(runtime_issues, dict) or not isinstance(rebuilt_issues, dict):
        return inconsistencies

    for issue_id in sorted(set(runtime_issues) | set(rebuilt_issues)):
        runtime_record = runtime_issues.get(issue_id)
        rebuilt_record = rebuilt_issues.get(issue_id)
        if not isinstance(runtime_record, dict) or not isinstance(rebuilt_record, dict):
            inconsistencies.append(f"runtime/events mismatch for {issue_id}: issue missing")
            continue
        for field in (
            "status",
            "base_sha",
            "head_sha",
            "pr",
            "pr_opened",
            "pr_merged",
            "merge_commit",
        ):
            if field in rebuilt_record and runtime_record.get(field) != rebuilt_record.get(field):
                inconsistencies.append(
                    "runtime/events mismatch for "
                    f"{issue_id} {field}: runtime={runtime_record.get(field)} "
                    f"events={rebuilt_record.get(field)}"
                )
        runtime_review = runtime_record.get("review", {})
        rebuilt_review = rebuilt_record.get("review", {})
        if isinstance(runtime_review, dict) and isinstance(rebuilt_review, dict):
            for field in ("status", "range"):
                if field in rebuilt_review and runtime_review.get(field) != rebuilt_review.get(field):
                    inconsistencies.append(
                        "runtime/events mismatch for "
                        f"{issue_id} review.{field}: runtime={runtime_review.get(field)} "
                        f"events={rebuilt_review.get(field)}"
                    )

    runtime_requests = {
        request.get("id")
        for request in runtime.get("human_requests", [])
        if isinstance(request, dict) and isinstance(request.get("id"), str)
    }
    rebuilt_requests = {
        request.get("id")
        for request in rebuilt.get("human_requests", [])
        if isinstance(request, dict) and isinstance(request.get("id"), str)
    }
    if runtime_requests != rebuilt_requests:
        inconsistencies.append(
            "runtime/events mismatch for human_requests: "
            f"runtime={sorted(runtime_requests)} events={sorted(rebuilt_requests)}"
        )
    return inconsistencies


def _runtime_with_rebuilt_remote_fields(
    runtime: dict[str, Any], rebuilt: dict[str, Any]
) -> dict[str, Any]:
    effective = dict(runtime)
    runtime_issues = runtime.get("issues", {})
    rebuilt_issues = rebuilt.get("issues", {})
    if not isinstance(runtime_issues, dict) or not isinstance(rebuilt_issues, dict):
        return effective

    effective_issues: dict[str, Any] = {}
    for issue_id, record in runtime_issues.items():
        effective_record = dict(record) if isinstance(record, dict) else record
        rebuilt_record = rebuilt_issues.get(issue_id)
        if isinstance(effective_record, dict) and isinstance(rebuilt_record, dict):
            for field in ("pr", "pr_opened", "pr_merged", "merge_commit"):
                if field in rebuilt_record:
                    effective_record[field] = rebuilt_record[field]
        effective_issues[issue_id] = effective_record
    effective["issues"] = effective_issues
    return effective


def _verified_commit_ranges(runtime: dict[str, Any]) -> list[str]:
    ranges: list[str] = []
    issues = runtime.get("issues", {})
    if not isinstance(issues, dict):
        return ranges
    for issue_id, record in sorted(issues.items()):
        if not isinstance(record, dict):
            continue
        if record.get("status") not in SUCCESS_STATUSES:
            continue
        if not review_approved_or_accepted(record, "review"):
            continue
        review = record.get("review")
        if not isinstance(review, dict):
            continue
        review_range = review.get("range") or review.get("review_range")
        if isinstance(review_range, str):
            ranges.append(f"{issue_id} {review_range}")
    return ranges


def _latest_report_paths(runtime_root: Path) -> list[str]:
    paths: list[Path] = []
    for dirname in ("reports", "reviews"):
        directory = runtime_root / dirname
        if directory.exists():
            paths.extend(path for path in directory.iterdir() if path.is_file())
    paths = sorted(
        paths,
        key=lambda path: (-path.stat().st_mtime, path.relative_to(runtime_root).as_posix()),
    )
    return [path.relative_to(runtime_root).as_posix() for path in paths[:6]]


def _pending_remote_action(envelope: dict[str, Any] | None, runtime: dict[str, Any]) -> str:
    if envelope is None:
        return MISSING_ENVELOPE
    remote_policy = envelope.get("remote_write_policy", {})
    if not isinstance(remote_policy, dict):
        return "unavailable - invalid remote_write_policy"
    mode = remote_policy.get("mode")
    if mode == "local_only":
        return "none - remote policy local_only"
    pending: list[str] = []
    issues = runtime.get("issues", {})
    if isinstance(issues, dict):
        for issue_id, record in sorted(issues.items()):
            if not isinstance(record, dict):
                continue
            if record.get("status") in SUCCESS_STATUSES and not record.get("pr_opened"):
                pending.append(f"open issue PR for {issue_id}")
    return _list_or_none(pending)


def _recommended_next_operation(
    *,
    hard_inconsistencies: list[str],
    actions: dict[str, Any] | None,
    active: list[str],
    waiting_human: list[str],
    reviewable: list[str],
    fixable: list[str],
    runnable: list[str] | str,
    pending_remote_action: str,
) -> str:
    if hard_inconsistencies:
        return "resume.recover"
    if reviewable:
        return f"execute.review {reviewable[0]}"
    if fixable:
        return f"execute.fix {fixable[0]}"
    if isinstance(runnable, list) and runnable:
        return f"execute.dispatch {runnable[0]}"
    if waiting_human:
        return f"human.resolve {waiting_human[0]}"
    if active:
        return f"status.monitor {active[0]}"
    if actions is not None and pending_remote_action not in {
        "none",
        "none - remote policy local_only",
        MISSING_ENVELOPE,
    }:
        return "deliver.remote"
    return "deliver.summary"


def _overall_status(
    runtime: dict[str, Any],
    hard_inconsistencies: list[str],
    active: list[str],
    waiting_human: list[str],
    reviewable: list[str],
    fixable: list[str],
    runnable: list[str] | str,
) -> str:
    counts = _status_counts(runtime)
    if hard_inconsistencies:
        return f"needs recovery ({counts})"
    if waiting_human:
        return f"waiting human ({counts})"
    if reviewable:
        return f"reviewable ({counts})"
    if fixable:
        return f"fixable ({counts})"
    if active:
        return f"active ({counts})"
    if isinstance(runnable, list) and runnable:
        return f"runnable ({counts})"
    return counts


def build_resume_brief(
    runtime_root: str | Path,
    template_text: str,
    *,
    envelope_path: str | Path | None = None,
    max_words: int = DEFAULT_MAX_WORDS,
) -> tuple[str, int]:
    root = Path(runtime_root)
    runtime_path = root / "runtime-state.json"
    events_path = root / "events.jsonl"
    if not runtime_path.exists():
        raise ResumeBriefInputError(f"missing runtime state: {runtime_path}")
    if not events_path.exists():
        raise ResumeBriefInputError(f"missing event log: {events_path}")

    runtime = load_json(runtime_path)
    rebuilt, event_warnings = rebuild_state_from_events(events_path)
    source_warnings = list(event_warnings)
    hard_inconsistencies = _runtime_event_inconsistencies(runtime, rebuilt)
    runtime_errors = validate_runtime_state(runtime)
    hard_inconsistencies.extend(f"runtime validation: {error}" for error in runtime_errors)

    envelope: dict[str, Any] | None = None
    candidate_envelope = Path(envelope_path) if envelope_path else root / "execution-envelope.json"
    envelope_errors: list[str] = []
    if candidate_envelope.exists():
        envelope = load_json(candidate_envelope)
        envelope_errors = validate_execution_envelope(envelope)
        hard_inconsistencies.extend(
            f"execution envelope validation: {error}" for error in envelope_errors
        )
    else:
        source_warnings.append(f"execution envelope missing at {candidate_envelope}")

    active = _status_issues(runtime, ACTIVE_STATUSES)
    actions: dict[str, Any] | None = None
    if envelope is not None and not envelope_errors and not runtime_errors:
        actions = compute_next_actions(envelope, runtime)
        runnable: list[str] | str = actions["runnable"]
        reviewable = actions["reviewable"]
        fixable = actions["fixable"]
        waiting_human = actions["waiting_human"]
    else:
        runnable = MISSING_ENVELOPE if envelope is None else "unavailable - invalid envelope/runtime"
        reviewable = _status_issues(runtime, REVIEWABLE_STATUSES)
        fixable = _status_issues(runtime, {"REVIEW_CHANGES_REQUESTED"})
        waiting_human = _status_issues(runtime, {"WAITING_HUMAN"})

    remote_runtime = _runtime_with_rebuilt_remote_fields(runtime, rebuilt)
    pending_remote_action = _pending_remote_action(envelope, remote_runtime)
    recommended = _recommended_next_operation(
        hard_inconsistencies=hard_inconsistencies,
        actions=actions,
        active=active,
        waiting_human=waiting_human,
        reviewable=reviewable,
        fixable=fixable,
        runnable=runnable,
        pending_remote_action=pending_remote_action,
    )
    warnings = hard_inconsistencies + source_warnings

    substitutions = {
        "epic_id": runtime.get("epic_id", rebuilt.get("epic_id", "unknown")),
        "overall_status": _overall_status(
            runtime,
            hard_inconsistencies,
            active,
            waiting_human,
            reviewable,
            fixable,
            runnable,
        ),
        "runnable": _list_or_none(runnable) if isinstance(runnable, list) else runnable,
        "active": _list_or_none(active),
        "reviewable": _list_or_none(reviewable),
        "fixable": _list_or_none(fixable),
        "waiting_human": _list_or_none(waiting_human),
        "pending_remote_action": pending_remote_action,
        "verified_commit_ranges": _list_or_none(_verified_commit_ranges(runtime)),
        "latest_report_paths": _list_or_none(_latest_report_paths(root)),
        "recommended_next_operation": recommended,
        "inconsistencies": _list_or_none(warnings),
    }
    content = template_text.format(**substitutions)
    count = word_count(content)
    if count > max_words:
        raise ResumeBriefBudgetError(count, max_words)
    return content, count
