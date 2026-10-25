"""Structured JSON logging: one JSON object per line, ready for any log collector."""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

_FIELDS_ATTR = "fields"


class JsonFormatter(logging.Formatter):
    """Render a log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "event": record.getMessage(),
        }
        entry.update(getattr(record, _FIELDS_ATTR, {}))
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Send JSON logs to stdout, the standard for containers."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    # Third-party HTTP clients log every request with its full URL: noisy, and URLs may carry
    # API keys. Our own events already record what matters.
    for noisy in ("httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def log_event(logger: logging.Logger, level: int, event: str, **fields: Any) -> None:
    """Log an event name with structured fields instead of an interpolated message."""
    logger.log(level, event, extra={_FIELDS_ATTR: fields})
