"""
Production-grade error handling for DistroIQ.

Provides structured error responses, proper HTTP status codes,
and user-friendly error messages while maintaining security.
"""

import traceback
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Union

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.logging import security_logger, auth_logger


class ErrorCategory(str, Enum):
    """Categories for different types of errors."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INTERNAL = "internal"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"


class ErrorSeverity(str, Enum):
    """Severity levels for errors."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorDetail(BaseModel):
    """Structured error detail information."""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response format."""
    error: bool = True
    message: str
    category: ErrorCategory
    code: str
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    details: Optional[List[ErrorDetail]] = None
    support_info: Optional[Dict[str, str]] = None


class DistroIQException(Exception):
    """Base exception class for DistroIQ-specific errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[List[ErrorDetail]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ):
        self.message = message
        self.category = category
        self.code = code
        self.status_code = status_code
        self.details = details or []
        self.severity = severity
        self.context = context or {}
        self.user_id = user_id
        self.request_id = str(uuid.uuid4())

        super().__init__(message)

    def to_response(self) -> ErrorResponse:
        """Convert exception to structured error response."""
        return ErrorResponse(
            message=self.message,
            category=self.category,
            code=self.code,
            request_id=self.request_id,
            details=self.details,
            support_info=self._get_support_info()
        )

    def _get_support_info(self) -> Dict[str, str]:
        """Get support information based on error category."""
        base_info = {
            "documentation": "https://docs.distroiq.com/troubleshooting",
            "support_email": "support@distroiq.com"
        }

        if self.category == ErrorCategory.AUTHENTICATION:
            base_info["auth_docs"] = "https://docs.distroiq.com/authentication"
        elif self.category == ErrorCategory.EXTERNAL_SERVICE:
            base_info["status_page"] = "https://status.distroiq.com"

        return base_info


# Specific exception classes for different error types

class AuthenticationError(DistroIQException):
    """Authentication-related errors."""

    def __init__(
        self,
        message: str = "Authentication required",
        code: str = "AUTH_REQUIRED",
        details: Optional[List[ErrorDetail]] = None,
        user_id: Optional[str] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            code=code,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
            severity=ErrorSeverity.MEDIUM,
            user_id=user_id
        )


class AuthorizationError(DistroIQException):
    """Authorization-related errors."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        code: str = "INSUFFICIENT_PERMISSIONS",
        details: Optional[List[ErrorDetail]] = None,
        user_id: Optional[str] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHORIZATION,
            code=code,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
            severity=ErrorSeverity.HIGH,
            user_id=user_id
        )


class ValidationError(DistroIQException):
    """Input validation errors."""

    def __init__(
        self,
        message: str = "Invalid input",
        code: str = "VALIDATION_ERROR",
        details: Optional[List[ErrorDetail]] = None,
        field: Optional[str] = None
    ):
        if field and not details:
            details = [ErrorDetail(field=field, message=message)]

        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            code=code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            severity=ErrorSeverity.LOW
        )


class NotFoundError(DistroIQException):
    """Resource not found errors."""

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ):
        if resource_type and resource_id:
            message = f"{resource_type} '{resource_id}' not found"
            code = f"{resource_type.upper()}_NOT_FOUND"

        super().__init__(
            message=message,
            category=ErrorCategory.NOT_FOUND,
            code=code,
            status_code=status.HTTP_404_NOT_FOUND,
            severity=ErrorSeverity.LOW
        )


class ConflictError(DistroIQException):
    """Resource conflict errors."""

    def __init__(
        self,
        message: str = "Resource conflict",
        code: str = "CONFLICT",
        details: Optional[List[ErrorDetail]] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.CONFLICT,
            code=code,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
            severity=ErrorSeverity.MEDIUM
        )


class RateLimitError(DistroIQException):
    """Rate limiting errors."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: str = "RATE_LIMIT_EXCEEDED",
        retry_after: Optional[int] = None
    ):
        context = {"retry_after": retry_after} if retry_after else {}

        super().__init__(
            message=message,
            category=ErrorCategory.RATE_LIMIT,
            code=code,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            context=context,
            severity=ErrorSeverity.MEDIUM
        )


class ExternalServiceError(DistroIQException):
    """External service integration errors."""

    def __init__(
        self,
        message: str = "External service unavailable",
        code: str = "EXTERNAL_SERVICE_ERROR",
        service_name: Optional[str] = None,
        upstream_error: Optional[str] = None
    ):
        context = {}
        if service_name:
            context["service_name"] = service_name
        if upstream_error:
            context["upstream_error"] = upstream_error

        super().__init__(
            message=message,
            category=ErrorCategory.EXTERNAL_SERVICE,
            code=code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            context=context,
            severity=ErrorSeverity.HIGH
        )


class BusinessLogicError(DistroIQException):
    """Business logic validation errors."""

    def __init__(
        self,
        message: str,
        code: str,
        details: Optional[List[ErrorDetail]] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.BUSINESS_LOGIC,
            code=code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            severity=ErrorSeverity.MEDIUM
        )


# Error handler functions

async def distroiq_exception_handler(request: Request, exc: DistroIQException) -> JSONResponse:
    """Handle DistroIQ-specific exceptions."""

    # Log the error
    log_error(request, exc, exc.severity)

    # Return structured error response
    error_response = exc.to_response()

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""

    # Convert to DistroIQ format
    category = _get_category_from_status_code(exc.status_code)
    code = _get_code_from_status_code(exc.status_code)

    error_response = ErrorResponse(
        message=exc.detail if isinstance(exc.detail, str) else "HTTP error",
        category=category,
        code=code
    )

    # Log non-client errors
    if exc.status_code >= 500:
        security_logger.error(
            f"HTTP {exc.status_code}: {exc.detail}",
            extra={
                "request_id": error_response.request_id,
                "status_code": exc.status_code,
                "path": str(request.url.path)
            }
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""

    request_id = str(uuid.uuid4())

    # Log the full error
    security_logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "request_id": request_id,
            "exception_type": type(exc).__name__,
            "path": str(request.url.path),
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )

    # Return generic error (don't expose internal details)
    error_response = ErrorResponse(
        message="An unexpected error occurred. Support has been notified.",
        category=ErrorCategory.INTERNAL,
        code="INTERNAL_ERROR",
        request_id=request_id
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


def log_error(request: Request, exc: DistroIQException, severity: ErrorSeverity) -> None:
    """Log error with appropriate level and context."""

    log_data = {
        "request_id": exc.request_id,
        "error_category": exc.category.value,
        "error_code": exc.code,
        "user_id": exc.user_id,
        "path": str(request.url.path),
        "method": request.method,
        "client_ip": request.client.host if request.client else None,
        "context": exc.context
    }

    if severity == ErrorSeverity.CRITICAL:
        security_logger.critical(exc.message, extra=log_data)
    elif severity == ErrorSeverity.HIGH:
        security_logger.error(exc.message, extra=log_data)
    elif severity == ErrorSeverity.MEDIUM:
        auth_logger.warning(exc.message, extra=log_data)
    else:
        auth_logger.info(exc.message, extra=log_data)


def _get_category_from_status_code(status_code: int) -> ErrorCategory:
    """Map HTTP status code to error category."""
    if status_code == 401:
        return ErrorCategory.AUTHENTICATION
    elif status_code == 403:
        return ErrorCategory.AUTHORIZATION
    elif status_code == 404:
        return ErrorCategory.NOT_FOUND
    elif status_code == 409:
        return ErrorCategory.CONFLICT
    elif status_code == 422:
        return ErrorCategory.VALIDATION
    elif status_code == 429:
        return ErrorCategory.RATE_LIMIT
    elif 500 <= status_code < 600:
        return ErrorCategory.INTERNAL
    else:
        return ErrorCategory.BUSINESS_LOGIC


def _get_code_from_status_code(status_code: int) -> str:
    """Map HTTP status code to error code."""
    codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT"
    }
    return codes.get(status_code, f"HTTP_{status_code}")


# Convenience functions for common error scenarios

def require_authentication(message: str = "Authentication required") -> None:
    """Raise authentication error."""
    raise AuthenticationError(message=message)


def require_authorization(message: str = "Insufficient permissions") -> None:
    """Raise authorization error."""
    raise AuthorizationError(message=message)


def validate_input(condition: bool, message: str, field: Optional[str] = None) -> None:
    """Validate input condition, raise error if false."""
    if not condition:
        raise ValidationError(message=message, field=field)


def not_found(resource_type: str, resource_id: str) -> None:
    """Raise not found error for specific resource."""
    raise NotFoundError(resource_type=resource_type, resource_id=resource_id)


def external_service_error(service_name: str, message: str, upstream_error: Optional[str] = None) -> None:
    """Raise external service error."""
    raise ExternalServiceError(
        message=f"{service_name} error: {message}",
        service_name=service_name,
        upstream_error=upstream_error
    )


def business_logic_error(message: str, code: str) -> None:
    """Raise business logic error."""
    raise BusinessLogicError(message=message, code=code)


# Account deletion specific errors

class AccountDeletionError(DistroIQException):
    """Account deletion specific errors."""

    def __init__(
        self,
        message: str,
        code: str,
        user_id: Optional[str] = None,
        reason: Optional[str] = None
    ):
        details = []
        if reason:
            details.append(ErrorDetail(message=reason, code="DELETION_REASON"))

        super().__init__(
            message=message,
            category=ErrorCategory.BUSINESS_LOGIC,
            code=code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            severity=ErrorSeverity.MEDIUM,
            user_id=user_id
        )


def account_deletion_not_configured() -> None:
    """Raise error when account deletion is not configured."""
    raise AccountDeletionError(
        message=(
            "Account deletion service not configured. "
            "SUPABASE_SERVICE_ROLE_KEY environment variable is missing. "
            "Contact support if this persists."
        ),
        code="DELETION_NOT_CONFIGURED"
    )


def account_not_found(user_id: str) -> None:
    """Raise error when account to delete is not found."""
    raise AccountDeletionError(
        message="User account not found. It may have been already deleted.",
        code="ACCOUNT_NOT_FOUND",
        user_id=user_id,
        reason="Account may have been previously deleted or never existed"
    )


def account_deletion_failed(user_id: str, reason: str) -> None:
    """Raise error when account deletion fails."""
    raise AccountDeletionError(
        message="Failed to delete account due to external service error.",
        code="DELETION_FAILED",
        user_id=user_id,
        reason=reason
    )