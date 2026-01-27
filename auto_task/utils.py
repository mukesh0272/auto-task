from __future__ import annotations

import json
import logging
import os
import time
from typing import Any


def setup_logging(level: str = "INFO") -> None:
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def read_json_file(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def abspath(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


class Debouncer:
    """
    Simple time-based debouncer: returns True only if enough time passed since last "allow".
    """
    def __init__(self, debounce_ms: int) -> None:
        self.debounce_ms = max(0, int(debounce_ms))
        self._last_allowed = 0.0

    def allow(self) -> bool:
        if self.debounce_ms <= 0:
            return True
        now = time.time()
        if (now - self._last_allowed) * 1000.0 >= self.debounce_ms:
            self._last_allowed = now
            return True
        return False
