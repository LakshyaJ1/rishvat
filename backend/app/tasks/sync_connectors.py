"""
AI CFO — Connector Sync Celery Tasks

Background tasks for syncing data from external integrations.
Runs every 6 hours for all active connectors.
Can also be triggered manually via the API.
"""

import logging
from uuid import UUID

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _get_sync_session():
    """Create a sync database session for Celery tasks."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.config import get_settings

    settings = get_settings()
    engine = create_engine(settings.database_url_sync, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    return Session()


def _get_connector_class(provider: str):
    """Get the appropriate connector class for a provider."""
    from app.connectors.stripe_connector import StripeConnector
    from app.connectors.plaid_connector import PlaidConnector

    connector_map = {
        "stripe": StripeConnector,
        "plaid": PlaidConnector,
    }
    return connector_map.get(provider)


@celery_app.task(
    name="app.tasks.sync_connectors.sync_connector_task",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def sync_connector_task(self, tenant_id: str, connector_id: str, provider: str):
    """
    Sync a single connector.
    Fetches data from the external API, normalizes it, and upserts to the database.

    Retries up to 3 times with 60-second delay on failure.
    """
    logger.info(
        f"Starting sync: provider={provider} tenant={tenant_id} connector={connector_id}"
    )

    session = _get_sync_session()

    try:
        from app.services.sync_service import sync_connector_records

        result = sync_connector_records(
            session=session,
            tenant_id=UUID(tenant_id),
            connector_id=UUID(connector_id),
            provider=provider,
            connector_class=_get_connector_class(provider),
        )
        logger.info("Sync complete: %s", result)
        return result

    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        raise self.retry(exc=e)

    finally:
        session.close()


@celery_app.task(name="app.tasks.sync_connectors.sync_all_connectors")
def sync_all_connectors():
    """
    Periodic task: sync all active connectors across all tenants.
    Runs every 6 hours via Celery Beat.
    """
    from app.models.connector_config import ConnectorConfig

    logger.info("Starting scheduled sync of all connectors")

    session = _get_sync_session()

    try:
        configs = session.query(ConnectorConfig).filter(
            ConnectorConfig.status == "active"
        ).all()

        logger.info(f"Found {len(configs)} active connectors to sync")

        for config in configs:
            try:
                sync_connector_task.delay(
                    str(config.tenant_id),
                    str(config.id),
                    config.provider,
                )
                logger.info(
                    f"Queued sync for {config.provider} "
                    f"(tenant={config.tenant_id})"
                )
            except Exception as e:
                logger.error(
                    f"Failed to queue sync for {config.provider}: {e}"
                )

    finally:
        session.close()

    return {"status": "queued", "connectors": len(configs)}
