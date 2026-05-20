"""
Metrics and telemetry system for DistroIQ.

Provides comprehensive tracking of user actions, system performance,
and business metrics with support for multiple backends (StatsD, DataDog, etc.).
"""

import time
import functools
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass, field

from app.core.logging import performance_logger
from app.core.config import settings


class MetricType(str, Enum):
    """Types of metrics we track."""
    COUNTER = "counter"        # Incremental values (requests, errors, events)
    GAUGE = "gauge"           # Point-in-time values (active users, queue length)
    HISTOGRAM = "histogram"   # Distributions (response times, sizes)
    TIMING = "timing"         # Duration measurements


class MetricCategory(str, Enum):
    """Categories for organizing metrics."""
    AUTH = "auth"
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ERROR = "error"


@dataclass
class MetricEvent:
    """A single metric event."""
    name: str
    metric_type: MetricType
    category: MetricCategory
    value: Union[int, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class MetricsCollector:
    """Central metrics collection and dispatch."""

    def __init__(self):
        self.events: List[MetricEvent] = []
        self.enabled = settings.APP_ENV != "test"

    def emit(self, event: MetricEvent) -> None:
        """Emit a metric event."""
        if not self.enabled:
            return

        self.events.append(event)

        # Log for development visibility
        if settings.APP_ENV == "development":
            performance_logger.info(
                f"Metric: {event.category.value}.{event.name} = {event.value}",
                extra={
                    "metric_name": event.name,
                    "metric_type": event.metric_type.value,
                    "metric_category": event.category.value,
                    "metric_value": event.value,
                    "metric_tags": event.tags,
                    "user_id": event.user_id
                }
            )

        # In production, this would also send to:
        # - DataDog, New Relic, or Grafana
        # - Internal analytics pipeline
        # - Business intelligence dashboards

    def counter(
        self,
        name: str,
        category: MetricCategory,
        value: int = 1,
        tags: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Increment a counter metric."""
        event = MetricEvent(
            name=name,
            metric_type=MetricType.COUNTER,
            category=category,
            value=value,
            tags=tags or {},
            user_id=user_id
        )
        self.emit(event)

    def gauge(
        self,
        name: str,
        category: MetricCategory,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Set a gauge metric."""
        event = MetricEvent(
            name=name,
            metric_type=MetricType.GAUGE,
            category=category,
            value=value,
            tags=tags or {},
            user_id=user_id
        )
        self.emit(event)

    def timing(
        self,
        name: str,
        category: MetricCategory,
        duration_ms: float,
        tags: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Record a timing metric in milliseconds."""
        event = MetricEvent(
            name=name,
            metric_type=MetricType.TIMING,
            category=category,
            value=duration_ms,
            tags=tags or {},
            user_id=user_id
        )
        self.emit(event)

    def histogram(
        self,
        name: str,
        category: MetricCategory,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Record a histogram metric."""
        event = MetricEvent(
            name=name,
            metric_type=MetricType.HISTOGRAM,
            category=category,
            value=value,
            tags=tags or {},
            user_id=user_id
        )
        self.emit(event)

    @contextmanager
    def timer(
        self,
        name: str,
        category: MetricCategory,
        tags: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None
    ):
        """Context manager for timing operations."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.timing(name, category, duration_ms, tags, user_id)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of collected metrics."""
        if not self.events:
            return {"total_events": 0, "categories": {}, "recent_events": []}

        # Count by category
        category_counts = {}
        for event in self.events:
            category = event.category.value
            category_counts[category] = category_counts.get(category, 0) + 1

        # Recent events (last 10)
        recent = []
        for event in self.events[-10:]:
            recent.append({
                "name": event.name,
                "category": event.category.value,
                "type": event.metric_type.value,
                "value": event.value,
                "timestamp": event.timestamp.isoformat(),
                "tags": event.tags
            })

        return {
            "total_events": len(self.events),
            "categories": category_counts,
            "recent_events": recent
        }


# Global metrics collector instance
metrics = MetricsCollector()


# ── High-level tracking functions ─────────────────────────────────

def track_user_action(
    action: str,
    user_id: str,
    success: bool = True,
    duration_ms: Optional[float] = None,
    details: Optional[Dict[str, str]] = None
) -> None:
    """Track a user action with success/failure and timing."""
    tags = {"action": action, "status": "success" if success else "failure"}
    if details:
        tags.update(details)

    # Count the action
    metrics.counter(
        name=f"user_action_{action}",
        category=MetricCategory.BUSINESS,
        tags=tags,
        user_id=user_id
    )

    # Track timing if provided
    if duration_ms is not None:
        metrics.timing(
            name=f"user_action_{action}_duration",
            category=MetricCategory.PERFORMANCE,
            duration_ms=duration_ms,
            tags=tags,
            user_id=user_id
        )

    # Track success rate
    metrics.counter(
        name="user_actions_total",
        category=MetricCategory.BUSINESS,
        tags={"status": "success" if success else "failure"},
        user_id=user_id
    )


def track_auth_event(
    event_type: str,
    user_id: Optional[str] = None,
    success: bool = True,
    method: str = "jwt",
    ip_address: Optional[str] = None
) -> None:
    """Track authentication events."""
    tags = {
        "event_type": event_type,
        "method": method,
        "status": "success" if success else "failure"
    }

    if ip_address:
        tags["ip_class"] = _classify_ip(ip_address)

    metrics.counter(
        name=f"auth_{event_type}",
        category=MetricCategory.AUTH,
        tags=tags,
        user_id=user_id
    )


def track_api_request(
    endpoint: str,
    method: str,
    status_code: int,
    duration_ms: float,
    user_id: Optional[str] = None
) -> None:
    """Track API request metrics."""
    tags = {
        "endpoint": endpoint,
        "method": method.upper(),
        "status_code": str(status_code),
        "status_class": f"{status_code // 100}xx"
    }

    # Request count
    metrics.counter(
        name="api_requests_total",
        category=MetricCategory.API,
        tags=tags,
        user_id=user_id
    )

    # Response time
    metrics.timing(
        name="api_request_duration",
        category=MetricCategory.API,
        duration_ms=duration_ms,
        tags=tags,
        user_id=user_id
    )

    # Error tracking
    if status_code >= 400:
        metrics.counter(
            name="api_errors_total",
            category=MetricCategory.ERROR,
            tags=tags,
            user_id=user_id
        )


def track_database_operation(
    operation: str,
    table: str,
    duration_ms: float,
    rows_affected: Optional[int] = None,
    success: bool = True
) -> None:
    """Track database operation metrics."""
    tags = {
        "operation": operation,
        "table": table,
        "status": "success" if success else "failure"
    }

    # Operation count
    metrics.counter(
        name="database_operations_total",
        category=MetricCategory.DATABASE,
        tags=tags
    )

    # Duration
    metrics.timing(
        name="database_operation_duration",
        category=MetricCategory.DATABASE,
        duration_ms=duration_ms,
        tags=tags
    )

    # Rows affected (for DML operations)
    if rows_affected is not None:
        metrics.histogram(
            name="database_rows_affected",
            category=MetricCategory.DATABASE,
            value=rows_affected,
            tags=tags
        )


def track_security_event(
    event_type: str,
    severity: str,
    ip_address: Optional[str] = None,
    user_id: Optional[str] = None,
    details: Optional[Dict[str, str]] = None
) -> None:
    """Track security-related events."""
    tags = {"event_type": event_type, "severity": severity}
    if details:
        tags.update(details)

    if ip_address:
        tags["ip_class"] = _classify_ip(ip_address)

    metrics.counter(
        name=f"security_{event_type}",
        category=MetricCategory.SECURITY,
        tags=tags,
        user_id=user_id
    )


def track_business_metric(
    metric_name: str,
    value: Union[int, float],
    user_id: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None
) -> None:
    """Track business-specific metrics."""
    metrics.gauge(
        name=metric_name,
        category=MetricCategory.BUSINESS,
        value=value,
        tags=tags or {},
        user_id=user_id
    )


# ── Decorators for automatic tracking ─────────────────────────────

def track_endpoint_metrics(endpoint: str):
    """Decorator to automatically track endpoint metrics."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            status_code = 200
            user_id = None

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = getattr(e, 'status_code', 500)
                raise
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                track_api_request(
                    endpoint=endpoint,
                    method="POST",  # Could be extracted from request
                    status_code=status_code,
                    duration_ms=duration_ms,
                    user_id=user_id
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            status_code = 200
            user_id = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = getattr(e, 'status_code', 500)
                raise
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                track_api_request(
                    endpoint=endpoint,
                    method="POST",
                    status_code=status_code,
                    duration_ms=duration_ms,
                    user_id=user_id
                )

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def track_performance(category: MetricCategory, name: Optional[str] = None):
    """Decorator to track function performance."""
    def decorator(func: Callable) -> Callable:
        metric_name = name or func.__name__

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with metrics.timer(metric_name, category):
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with metrics.timer(metric_name, category):
                return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# ── Utility functions ─────────────────────────────────────────────

def _classify_ip(ip_address: str) -> str:
    """Classify IP address for privacy-safe metrics."""
    if ip_address.startswith(('127.', '192.168.', '10.')):
        return "private"
    elif ip_address.startswith('172.'):
        # Check if it's in the 172.16-31 range
        try:
            second_octet = int(ip_address.split('.')[1])
            if 16 <= second_octet <= 31:
                return "private"
        except (ValueError, IndexError):
            pass
    return "public"


# ── Specific business metrics for DistroIQ ────────────────────────

def track_account_deletion(user_id: str, success: bool, duration_ms: float) -> None:
    """Track account deletion events."""
    track_user_action("account_deletion", user_id, success, duration_ms)

    # Business metric: account deletion rate
    track_business_metric(
        "account_deletions_daily",
        1,
        user_id=user_id,
        tags={"status": "success" if success else "failure"}
    )


def track_chat_query(user_id: str, query_type: str, response_time_ms: float) -> None:
    """Track chat/query interactions."""
    track_user_action(
        "chat_query",
        user_id,
        success=True,
        duration_ms=response_time_ms,
        details={"query_type": query_type}
    )

    # Business metric: query volume by type
    track_business_metric(
        f"queries_{query_type}_hourly",
        1,
        user_id=user_id
    )


def track_data_access(user_id: str, data_source: str, record_count: int) -> None:
    """Track data access patterns."""
    track_user_action(
        "data_access",
        user_id,
        success=True,
        details={"source": data_source}
    )

    # Business metric: data usage
    track_business_metric(
        f"data_records_accessed_{data_source}",
        record_count,
        user_id=user_id
    )


# Export main interface
__all__ = [
    'metrics',
    'track_user_action',
    'track_auth_event',
    'track_api_request',
    'track_database_operation',
    'track_security_event',
    'track_business_metric',
    'track_endpoint_metrics',
    'track_performance',
    'track_account_deletion',
    'track_chat_query',
    'track_data_access',
    'MetricCategory',
    'MetricType'
]