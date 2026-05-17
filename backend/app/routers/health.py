"""
AI CFO — Health Endpoints

GET /health — service health check (DB, Redis, Celery)
GET /metrics — basic operational metrics

These are public endpoints (no auth required).
Used by load balancers, monitoring, and the frontend health indicator.
"""

import logging
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(tags=["health"])

# Track server start time for uptime calculation
_start_time = time.monotonic()


@router.get("/health", summary="Service health check")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Returns health status of all dependent services.
    Used by load balancers and frontend health indicator.
    """
    status_map = {}

    # Check PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        status_map["db"] = "ok"
    except Exception as e:
        status_map["db"] = f"error: {str(e)[:100]}"
        logger.error(f"Health check: DB failed: {e}")

    # Check Redis
    try:
        import redis as redis_lib
        r = redis_lib.from_url(settings.redis_url, socket_timeout=2)
        r.ping()
        status_map["redis"] = "ok"
    except Exception as e:
        status_map["redis"] = f"error: {str(e)[:100]}"
        logger.warning(f"Health check: Redis failed: {e}")

    # Check Celery (via Redis broker ping)
    try:
        import redis as redis_lib
        r = redis_lib.from_url(settings.celery_broker_url, socket_timeout=2)
        r.ping()
        status_map["celery"] = "ok"
    except Exception as e:
        status_map["celery"] = f"error: {str(e)[:100]}"
        logger.warning(f"Health check: Celery broker failed: {e}")

    # Overall status
    all_ok = all(v == "ok" for v in status_map.values())

    return {
        "status": "healthy" if all_ok else "degraded",
        "version": settings.app_version,
        "environment": settings.app_env,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **status_map,
    }


@router.get("/metrics", summary="Operational metrics stub")
async def metrics(db: AsyncSession = Depends(get_db)):
    """
    Basic operational metrics.
    In production, this would be replaced by Prometheus metrics.
    For Stage 1, returns basic counts.
    """
    try:
        # Count tenants
        result = await db.execute(text("SELECT COUNT(*) FROM tenants"))
        tenant_count = result.scalar() or 0

        # Count financial records
        result = await db.execute(text("SELECT COUNT(*) FROM financial_records"))
        record_count = result.scalar() or 0

        # Count audit logs in last 24h
        result = await db.execute(
            text(
                "SELECT COUNT(*) FROM audit_logs "
                "WHERE created_at > NOW() - INTERVAL '24 hours'"
            )
        )
        audit_24h = result.scalar() or 0

    except Exception:
        tenant_count = 0
        record_count = 0
        audit_24h = 0

    uptime = time.monotonic() - _start_time

    return {
        "active_tenants": tenant_count,
        "total_records": record_count,
        "audit_events_24h": audit_24h,
        "uptime_seconds": round(uptime, 2),
        "version": settings.app_version,
    }
