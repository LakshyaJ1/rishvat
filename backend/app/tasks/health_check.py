"""
AI CFO — Health Check Celery Task

Periodic task that verifies system components are operational.
Logs results for monitoring.
"""

import logging
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.health_check.celery_health_check")
def celery_health_check():
    """
    Periodic health check task.
    Confirms Celery workers are running and can execute tasks.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info(f"Celery health check OK at {timestamp}")

    return {
        "status": "ok",
        "timestamp": timestamp,
        "worker": "celery",
    }
