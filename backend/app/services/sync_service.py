"""Synchronous connector sync service used by Celery and tests."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Protocol
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.connector_config import ConnectorConfig
from app.models.financial_record import FinancialRecord
from app.utils.encryption import decrypt_json

logger = logging.getLogger(__name__)


class ConnectorClass(Protocol):
    def __init__(self, tenant_id: UUID, credentials: dict): ...

    async def sync(self, since: datetime | None = None) -> list[FinancialRecord]: ...


def write_sync_audit_log(
    session: Session,
    tenant_id: UUID,
    outcome: str,
    action_detail: dict,
) -> None:
    """Write a system audit entry from sync code running outside FastAPI."""
    session.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=None,
            action_type="connector.sync",
            action_detail=action_detail,
            data_sources={"provider": action_detail.get("provider")},
            outcome=outcome,
            created_at=datetime.now(timezone.utc),
        )
    )


def sync_connector_records(
    *,
    session: Session,
    tenant_id: UUID,
    connector_id: UUID,
    provider: str,
    connector_class: type[ConnectorClass] | None,
) -> dict:
    """Fetch, normalize, and upsert connector records for one tenant.

    The function is intentionally sync because Celery workers use a sync DB
    session. Tests can call this directly with a test-only connector class.
    """
    config = (
        session.query(ConnectorConfig)
        .filter(
            ConnectorConfig.id == connector_id,
            ConnectorConfig.tenant_id == tenant_id,
        )
        .one_or_none()
    )

    if not config:
        result = {"status": "error", "message": "Connector not found"}
        logger.error("Connector config not found: %s", connector_id)
        return result

    if config.status != "active":
        result = {
            "status": "skipped",
            "provider": provider,
            "message": f"Connector is {config.status}",
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
        }
        write_sync_audit_log(session, tenant_id, "pending", result)
        session.commit()
        return result

    if connector_class is None:
        result = {
            "status": "error",
            "provider": provider,
            "message": f"Unknown provider: {provider}",
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
        }
        config.status = "error"
        config.sync_error = result["message"]
        write_sync_audit_log(session, tenant_id, "failure", result)
        session.commit()
        return result

    try:
        credentials = decrypt_json(config.credentials_encrypted)
        connector = connector_class(tenant_id=tenant_id, credentials=credentials)
        records = asyncio.run(connector.sync(since=config.last_synced_at))

        inserted = 0
        updated = 0
        skipped = 0
        seen_keys: set[tuple[str, str]] = set()

        for record in records:
            key = (record.source, record.source_id)
            if key in seen_keys:
                skipped += 1
                continue
            seen_keys.add(key)

            existing = (
                session.query(FinancialRecord)
                .filter(
                    FinancialRecord.tenant_id == tenant_id,
                    FinancialRecord.source == record.source,
                    FinancialRecord.source_id == record.source_id,
                )
                .one_or_none()
            )

            if existing:
                existing.record_type = record.record_type
                existing.amount_cents = record.amount_cents
                existing.currency = record.currency
                existing.description = record.description
                existing.category = record.category
                existing.occurred_at = record.occurred_at
                existing.metadata_json = record.metadata_json
                existing.synced_at = record.synced_at
                updated += 1
            else:
                session.add(record)
                inserted += 1

        config.status = "active"
        config.last_synced_at = datetime.now(timezone.utc)
        config.sync_error = None

        result = {
            "status": "success",
            "provider": provider,
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
        }
        write_sync_audit_log(session, tenant_id, "success", result)
        session.commit()
        return result

    except Exception as exc:
        session.rollback()
        config = session.query(ConnectorConfig).filter(ConnectorConfig.id == connector_id).one_or_none()
        if config:
            config.status = "error"
            config.sync_error = str(exc)[:500]
        result = {
            "status": "error",
            "provider": provider,
            "message": str(exc),
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
        }
        write_sync_audit_log(session, tenant_id, "failure", result)
        session.commit()
        raise

