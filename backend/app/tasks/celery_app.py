"""
AI CFO — Celery Application

Celery app factory for background tasks.
Used for:
- Scheduled connector syncs (every 6 hours)
- Health check periodic tasks
- Expense categorization jobs
- Compliance deadline checks
"""

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ai_cfo",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task behavior
    task_track_started=True,
    task_acks_late=True,  # For reliability — ack after completion
    worker_prefetch_multiplier=1,

    # Results expiry
    result_expires=3600,  # 1 hour

    # Retry on connection error
    broker_connection_retry_on_startup=True,

    # Beat schedule — periodic tasks
    beat_schedule={
        "health-check-every-5-min": {
            "task": "app.tasks.health_check.celery_health_check",
            "schedule": 300.0,  # Every 5 minutes
        },
        "sync-all-connectors-every-6h": {
            "task": "app.tasks.sync_connectors.sync_all_connectors",
            "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
