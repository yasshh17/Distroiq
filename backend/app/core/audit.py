"""
Audit logging system for security-critical actions.

Provides structured audit trails for compliance, security monitoring,
and operational visibility into user actions.
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, asdict

from app.core.logging import audit_logger, log_audit_event


class AuditAction(str, Enum):
    """Standardized audit action types."""

    # Authentication actions
    LOGIN_ATTEMPT = "auth.login.attempt"
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    TOKEN_REFRESH = "auth.token.refresh"

    # Account management
    ACCOUNT_CREATE = "account.create"
    ACCOUNT_DELETE = "account.delete"
    ACCOUNT_DELETE_ATTEMPT = "account.delete.attempt"
    PASSWORD_CHANGE = "account.password.change"
    EMAIL_CHANGE = "account.email.change"

    # Data access
    DATA_QUERY = "data.query"
    DATA_EXPORT = "data.export"
    SENSITIVE_DATA_ACCESS = "data.sensitive.access"

    # Administrative actions
    CONFIG_CHANGE = "admin.config.change"
    USER_IMPERSONATION = "admin.impersonate"
    BULK_OPERATION = "admin.bulk.operation"

    # Security events
    UNAUTHORIZED_ACCESS = "security.unauthorized.access"
    RATE_LIMIT_EXCEEDED = "security.rate_limit.exceeded"
    SUSPICIOUS_ACTIVITY = "security.suspicious.activity"


class AuditOutcome(str, Enum):
    """Standardized audit outcomes."""
    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"
    PARTIAL = "partial"


@dataclass
class AuditEvent:
    """Structured audit event data."""

    # Core identifiers
    event_id: str
    timestamp: datetime
    action: AuditAction
    outcome: AuditOutcome

    # Actor information
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Resource information
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None

    # Context and details
    details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    risk_level: str = "low"

    # Compliance fields
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None

    def __post_init__(self):
        """Validate and normalize the audit event."""
        if not self.event_id:
            self.event_id = str(uuid.uuid4())

        if not isinstance(self.timestamp, datetime):
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat() + 'Z'
        return data


class AuditLogger:
    """High-level audit logging interface."""

    @staticmethod
    def log_event(event: AuditEvent) -> None:
        """Log an audit event."""
        # Log to structured audit logger
        audit_logger.info(
            f"Audit: {event.action} -> {event.outcome}",
            extra=event.to_dict()
        )

        # Also log to the general audit function for backwards compatibility
        log_audit_event(
            action=event.action.value,
            resource=event.resource_type or "unknown",
            user_id=event.user_id or "anonymous",
            outcome=event.outcome.value,
            details=event.details
        )

    @staticmethod
    def log_auth_event(
        action: AuditAction,
        outcome: AuditOutcome,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Log authentication-related events."""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=action,
            outcome=outcome,
            user_id=user_id,
            ip_address=ip_address,
            resource_type="authentication",
            details=details,
            error_message=error_message,
            risk_level="medium" if outcome == AuditOutcome.FAILURE else "low"
        )

        AuditLogger.log_event(event)

    @staticmethod
    def log_account_deletion(
        user_id: str,
        outcome: AuditOutcome,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Log account deletion attempts and results."""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=AuditAction.ACCOUNT_DELETE,
            outcome=outcome,
            user_id=user_id,
            ip_address=ip_address,
            resource_type="user_account",
            resource_id=user_id,
            details=details,
            error_message=error_message,
            risk_level="high"  # Account deletion is always high-risk
        )

        AuditLogger.log_event(event)

    @staticmethod
    def log_data_access(
        action: AuditAction,
        outcome: AuditOutcome,
        user_id: str,
        query: str,
        result_count: Optional[int] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log data access events."""
        event_details = details or {}
        event_details.update({
            "query": query,
            "result_count": result_count
        })

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=action,
            outcome=outcome,
            user_id=user_id,
            ip_address=ip_address,
            resource_type="data",
            details=event_details,
            risk_level="medium" if "sensitive" in query.lower() else "low"
        )

        AuditLogger.log_event(event)

    @staticmethod
    def log_security_event(
        action: AuditAction,
        outcome: AuditOutcome,
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        risk_level: str = "high"
    ) -> None:
        """Log security-related events."""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=action,
            outcome=outcome,
            user_id=user_id,
            ip_address=ip_address,
            resource_type="security",
            details=details,
            risk_level=risk_level
        )

        AuditLogger.log_event(event)


class AuditContext:
    """Context manager for grouping related audit events."""

    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())[:8]
        self.events: List[AuditEvent] = []

    def log_event(
        self,
        action: AuditAction,
        outcome: AuditOutcome,
        **kwargs
    ) -> None:
        """Log an event within this audit context."""
        kwargs['correlation_id'] = self.correlation_id

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=action,
            outcome=outcome,
            **kwargs
        )

        self.events.append(event)
        AuditLogger.log_event(event)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Log a summary event
        summary_event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=AuditAction.BULK_OPERATION,  # Generic for multi-step operations
            outcome=AuditOutcome.SUCCESS if exc_type is None else AuditOutcome.FAILURE,
            correlation_id=self.correlation_id,
            details={
                "event_count": len(self.events),
                "actions": [e.action.value for e in self.events],
                "exception": str(exc_val) if exc_val else None
            }
        )

        AuditLogger.log_event(summary_event)


# Convenience functions for common audit scenarios

def audit_login_attempt(email: str, ip_address: str, success: bool) -> None:
    """Audit a login attempt."""
    AuditLogger.log_auth_event(
        action=AuditAction.LOGIN_ATTEMPT,
        outcome=AuditOutcome.SUCCESS if success else AuditOutcome.FAILURE,
        ip_address=ip_address,
        details={"email": email}
    )


def audit_account_deletion_attempt(
    user_id: str,
    ip_address: str,
    success: bool,
    error_details: Optional[str] = None
) -> None:
    """Audit an account deletion attempt."""
    AuditLogger.log_account_deletion(
        user_id=user_id,
        outcome=AuditOutcome.SUCCESS if success else AuditOutcome.FAILURE,
        ip_address=ip_address,
        error_message=error_details,
        details={
            "deletion_method": "user_initiated",
            "verification_required": True
        }
    )


def audit_sensitive_data_access(
    user_id: str,
    query_type: str,
    ip_address: str,
    result_count: int
) -> None:
    """Audit access to sensitive data."""
    AuditLogger.log_data_access(
        action=AuditAction.SENSITIVE_DATA_ACCESS,
        outcome=AuditOutcome.SUCCESS,
        user_id=user_id,
        query=query_type,
        result_count=result_count,
        ip_address=ip_address
    )


def audit_unauthorized_access(
    endpoint: str,
    ip_address: str,
    user_agent: str,
    reason: str
) -> None:
    """Audit unauthorized access attempts."""
    AuditLogger.log_security_event(
        action=AuditAction.UNAUTHORIZED_ACCESS,
        outcome=AuditOutcome.BLOCKED,
        ip_address=ip_address,
        details={
            "endpoint": endpoint,
            "user_agent": user_agent,
            "block_reason": reason
        }
    )