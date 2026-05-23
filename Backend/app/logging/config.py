"""
Closira — Structured JSON Logging Configuration

Provides a centralized logging setup that emits structured JSON logs.

Why structured JSON logging?
- Machine-parseable: logs can be ingested by tools like ELK, Datadog, etc.
- Consistent format: every log has timestamp, level, module, and message
- Searchable: structured fields make filtering and debugging easier
- Production-ready: demonstrates operational awareness in an internship project

Why Python's built-in logging module?
- Zero additional dependencies
- Industry standard in Python ecosystem
- Configurable handlers, formatters, and levels
"""

import logging
import json
from datetime import datetime, timezone
from contextvars import ContextVar

# Centralized thread-safe context variable for request correlation tracking
request_correlation_id: ContextVar[str] = ContextVar("request_correlation_id", default="")


class JSONFormatter(logging.Formatter):
    """
    Custom log formatter that outputs JSON-structured log lines.

    Each log line contains:
    - timestamp: ISO 8601 UTC timestamp
    - level: log level (INFO, WARNING, ERROR, etc.)
    - module: the Python module that emitted the log
    - message: the log message
    - correlation_id: injected from active HTTP requests
    - extra: any additional key-value pairs passed via the `extra` parameter
    - exception: serialized exception details if exc_info is present
      - type: fully qualified exception class name
      - message: exception str()
      - traceback: formatted stack trace string

    WHY TRACEBACK SERIALIZATION WAS ADDED:
    Previously, the formatter discarded exc_info entirely. When logger.exception()
    was called (e.g. in unexpected_exception_handler), the stack trace was either
    printed to stderr in plaintext or silently swallowed — neither is acceptable
    for a production observability system. Serializing it into the JSON payload
    keeps all debugging context in a single, machine-parseable log line.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }

        # Automatically inject correlation_id if set in the current thread context
        corr_id = request_correlation_id.get()
        if corr_id:
            log_entry["correlation_id"] = corr_id

        # Include any extra fields passed to the logger
        if hasattr(record, "extra_data"):
            log_entry["extra"] = record.extra_data

        # Serialize exception info (traceback, type, message) if present.
        # This ensures logger.exception() and logger.error(..., exc_info=True)
        # produce fully debuggable structured log lines instead of losing the
        # stack trace to plaintext stderr or dropping it silently.
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            log_entry["exception"] = {
                "type": exc_type.__qualname__ if exc_type else None,
                "message": str(exc_value) if exc_value else None,
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_entry)


def get_logger(name: str) -> logging.Logger:
    """
    Create and return a configured logger with JSON formatting.

    Args:
        name: The name of the logger (typically __name__ of the calling module).

    Returns:
        A logging.Logger instance configured with JSON output to stdout.

    Usage:
        from app.logging.config import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened")
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if get_logger is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()  # Output to stdout/stderr
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    return logger
