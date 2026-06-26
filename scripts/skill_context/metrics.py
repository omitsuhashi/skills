"""Context metrics for skill read sets.

The token estimator is intentionally dependency-free. It is conservative for
repository context sizing, not a model-specific tokenizer replacement.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Iterable, Mapping


WORD_RE = re.compile(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*|[^\W\s_]+", re.UNICODE)


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def _is_cjk(char: str) -> bool:
    codepoint = ord(char)
    return (
        0x3040 <= codepoint <= 0x30FF
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0xAC00 <= codepoint <= 0xD7AF
    )


def estimate_token_count(text: str) -> int:
    tokens = 0
    ascii_run = 0

    def flush_ascii() -> None:
        nonlocal ascii_run, tokens
        if ascii_run:
            tokens += math.ceil(ascii_run / 3)
            ascii_run = 0

    for char in text:
        if char.isspace():
            flush_ascii()
            continue
        if _is_cjk(char):
            flush_ascii()
            tokens += 1
        elif ord(char) < 128 and (char.isalnum() or char == "_"):
            ascii_run += 1
        elif ord(char) < 128:
            flush_ascii()
            tokens += 1
        else:
            flush_ascii()
            tokens += 1
    flush_ascii()
    return tokens


def _headroom_percent(used: int, budget: int | None) -> int | None:
    if not budget:
        return None
    return math.floor(((budget - used) / budget) * 100)


def collect_text_metrics(texts: Iterable[str], budget: Mapping[str, int | None] | None = None) -> dict:
    material_parts = list(texts)
    budget = budget or {}
    words = sum(word_count(text) for text in material_parts)
    character_count = sum(len(text) for text in material_parts)
    non_whitespace_character_count = sum(1 for text in material_parts for char in text if not char.isspace())
    estimated_tokens = sum(estimate_token_count(text) for text in material_parts)
    token_budget = budget.get("estimated_token_budget")
    character_budget = budget.get("character_budget")
    word_budget = budget.get("word_budget")
    headroom_percent = (
        _headroom_percent(estimated_tokens, token_budget)
        if token_budget
        else _headroom_percent(character_count, character_budget)
        if character_budget
        else _headroom_percent(words, word_budget)
    )
    return {
        "word_count": words,
        "character_count": character_count,
        "non_whitespace_character_count": non_whitespace_character_count,
        "estimated_token_count": estimated_tokens,
        "headroom_percent": headroom_percent,
    }


def collect_file_metrics(paths: Iterable[Path], budget: Mapping[str, int | None] | None = None) -> dict:
    path_list = list(paths)
    metrics = collect_text_metrics((path.read_text(encoding="utf-8") for path in path_list), budget)
    metrics["file_count"] = len(path_list)
    return metrics
