"""
Centralized logging configuration for DistroIQ.

Provides structured logging with correlation IDs, audit trails,
and proper formatting for both development and production.
"""

import logging
import json
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar

from app.core.config import settings

# Context variable for request correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if present
        if correlation_id.get():
            log_entry["correlation_id"] = correlation_id.get()

        # Add any extra fields from the log record
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "getMessage"
            }:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


class DevelopmentFormatter(logging.Formatter):
    """Human-readable formatter for development."""

    def format(self, record: logging.LogRecord) -> str:
        # Color codes
        colors = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m', # Magenta
            'ENDC': '\033[0m'       # End color
        }

        level_color = colors.get(record.levelname, '')
        end_color = colors['ENDC']

        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]

        base_msg = f"{timestamp} {level_color}{record.levelname:8}{end_color} {record.name:20} {record.getMessage()}"

        # Add correlation ID if present
        corr_id = correlation_id.get()
        if corr_id:
            base_msg += f" [corr_id={corr_id}]"

        return base_msg


def setup_logging() -> None:
    """Configure logging for the application."""

    # Remove any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Set level based on environment
    if settings.APP_ENV == "development":
        level = logging.DEBUG
        formatter = DevelopmentFormatter()
    else:
        level = logging.INFO
        formatter = StructuredFormatter()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    # Quiet down noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


@contextmanager
def log_context(corr_id: Optional[str] = None):
    """Context manager to set correlation ID for request tracing."""
    if corr_id is None:
        corr_id = str(uuid.uuid4())[:8]

    token = correlation_id.set(corr_id)
    try:
        yield corr_id
    finally:
        correlation_id.reset(token)


# Specialized loggers
audit_logger = logging.getLogger("distroiq.audit")
security_logger = logging.getLogger("distroiq.security")
performance_logger = logging.getLogger("distroiq.performance")
auth_logger = logging.getLogger("distroiq.auth")


def log_auth_event(
    event_type: str,
    user_id: Optional[str] = None,
    success: bool = True,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> None:
    """Log authentication-related events."""
    log_data = {
        "event_type": event_type,
        "success": success,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    if user_id:
        log_data["user_id"] = user_id
    if ip_address:
        log_data["ip_address"] = ip_address
    if details:
        log_data["details"] = details

    auth_logger.info(
        f"Auth event: {event_type} ({'success' if success else 'failure'})",
        extra=log_data
    )


def log_security_event(
    event_type: str,
    severity: str,
    details: Dict[str, Any],
    user_id: Optional[str] = None
) -> None:
    """Log security-related events."""
    log_data = {
        "event_type": event_type,
        "severity": severity,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "details": details
    }

    if user_id:
        log_data["user_id"] = user_id

    security_logger.warning(
        f"Security event: {event_type} (severity: {severity})",
        extra=log_data
    )


def log_audit_event(
    action: str,
    resource: str,
    user_id: str,
    outcome: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """Log audit trail events for compliance."""
    log_data = {
        "action": action,
        "resource": resource,
        "user_id": user_id,
        "outcome": outcome,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    if details:
        log_data["details"] = details

    audit_logger.info(
        f"Audit: {action} on {resource} by {user_id} -> {outcome}",
        extra=log_data
    )