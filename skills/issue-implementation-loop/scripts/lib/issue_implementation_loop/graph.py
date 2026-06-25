from __future__ import annotations

from typing import Any

from .review import review_approved_or_accepted


def dependency_cycle(work_items: dict[str, Any]) -> list[str]:
    graph = {
        issue_id: [
            dep["issue"]
            for dep in item.get("dependencies", [])
            if isinstance(dep, dict) and dep.get("issue") in work_items
        ]
        for issue_id, item in work_items.items()
        if isinstance(item, dict)
    }
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in visiting:
            start = stack.index(node)
            return stack[start:] + [node]
        if node in visited:
            return None
        visiting.add(node)
        stack.append(node)
        for dep in graph.get(node, []):
            found = visit(dep)
            if found:
                return found
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for issue_id in graph:
        found = visit(issue_id)
        if found:
            return found
    return []


def issue_record(runtime: dict[str, Any], issue_id: str) -> dict[str, Any]:
    issues = runtime.get("issues", {})
    if isinstance(issues, dict) and isinstance(issues.get(issue_id), dict):
        return issues[issue_id]
    return {"status": "PENDING"}


def issue_status(runtime: dict[str, Any], issue_id: str) -> str:
    status = issue_record(runtime, issue_id).get("status", "PENDING")
    return status if isinstance(status, str) else "PENDING"


def dependency_satisfied(dep: dict[str, Any], runtime: dict[str, Any]) -> bool:
    record = issue_record(runtime, dep["issue"])
    release_on = dep.get("release_on")
    signals = record.get("signals", [])
    if release_on in signals:
        return True
    if release_on == "review_approved":
        return review_approved_or_accepted(record, "review")
    if release_on == "artifact_ready":
        return record.get("status") in {
            "ARTIFACT_READY",
            "IMPLEMENTED",
            "VERIFICATION_PASSED",
            "PR_READY",
            "COMPLETE",
            "DONE",
        }
    if release_on == "integrated":
        return record.get("status") in {"INTEGRATED", "COMPLETE", "DONE"}
    if release_on == "pr_opened":
        return bool(record.get("pr_opened") or record.get("pr"))
    if release_on == "pr_merged":
        return bool(record.get("pr_merged"))
    if release_on in {"human_decision", "external_condition"}:
        return bool(record.get(release_on))
    return False


def descendants_of(issue_id: str, work_items: dict[str, Any]) -> set[str]:
    children: dict[str, set[str]] = {key: set() for key in work_items}
    for child, item in work_items.items():
        for dep in item.get("dependencies", []):
            if isinstance(dep, dict) and dep.get("issue") in children:
                children[dep["issue"]].add(child)

    descendants: set[str] = set()
    queue = list(children.get(issue_id, set()))
    while queue:
        child = queue.pop(0)
        if child in descendants:
            continue
        descendants.add(child)
        queue.extend(children.get(child, set()))
    return descendants
