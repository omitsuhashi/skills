from __future__ import annotations


class ValidationError(Exception):
    """Raised when a validation script finds invalid input."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("\n".join(errors))
        self.errors = errors
