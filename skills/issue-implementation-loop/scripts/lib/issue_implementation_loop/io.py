from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"
