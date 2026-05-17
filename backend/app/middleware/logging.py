"""
AI CFO — Request Logging Middleware

Logs every request with timing, tenant context, and status code.
Part of the observability-from-day-one approach.
"""

import logging
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("aicfo.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs HTTP request/response with timing information."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.monotonic()

        # Extract tenant_id if available (set by auth dependency)
        tenant_id = getattr(request.state, "tenant_id", None)

        response = await call_next(request)

        duration_ms = (time.monotonic() - start_time) * 1000

        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "tenant_id": str(tenant_id) if tenant_id else None,
                "client_ip": request.client.host if request.client else None,
            },
        )

        # Add timing header for frontend observability
        response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))

        return response
