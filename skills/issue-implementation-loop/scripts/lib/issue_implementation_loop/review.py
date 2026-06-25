from __future__ import annotations

from typing import Any

from .constants import APPROVED_REVIEW_STATUSES


def has_human_risk_acceptance(record: dict[str, Any], review: dict[str, Any]) -> bool:
    return bool(
        record.get("human_risk_accepted")
        or record.get("human_risk_acceptance")
        or review.get("human_risk_accepted")
        or review.get("human_risk_acceptance")
    )


def review_approved_or_accepted(record: dict[str, Any], field: str) -> bool:
    review = record.get(field)
    if not isinstance(review, dict):
        return False
    return review.get("status") in APPROVED_REVIEW_STATUSES or has_human_risk_acceptance(record, review)
