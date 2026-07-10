"""Structured logging configuration for BookBuddy.

Uses stdlib ``logging`` (zero extra dependencies) with a JSON-line formatter
that is machine-parseable while still human-readable via ``logging.Formatter``
fallback when JSON is not needed.

Usage in any module::

    import logging
    from src.logging_config import configure_logging

    configure_logging(level=logging.DEBUG, json_output=False)
    logger = logging.getLogger(__name__)
    logger.info("message", extra={"extra_key": value})
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class _JSONFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[1]:
            payload["exception"] = repr(record.exc_info[1])
        for key in ("extra_key", "backend", "model", "rows"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, default=str)


_CONSOLE_FORMAT = "%(asctime)s [%(levelname)-7s] %(name)s | %(message)s"


def configure_logging(
    level: int = logging.INFO,
    json_output: bool = False,
) -> None:
    """Set up root logger with console handler.

    Args:
        level: Logging level (e.g. ``logging.DEBUG``).
        json_output: If ``True``, emit JSON lines; otherwise human-readable text.
    """
    root = logging.getLogger()
    root.setLevel(level)

    # Remove any previously attached handlers
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    if json_output:
        handler.setFormatter(_JSONFormatter())
    else:
        formatter = logging.Formatter(_CONSOLE_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)

    root.addHandler(handler)

    # Quiet down noisy third-party loggers
    for noisy in ("urllib3", "httpx", "httpcore", "huggingface_hub"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
