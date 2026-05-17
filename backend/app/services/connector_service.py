"""
AI CFO — Connector Service

Business logic for managing integration connectors.
Handles connect, disconnect, sync trigger, and status checking.
Connector credentials are encrypted at rest using AES-256.
"""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.connector_config import ConnectorConfig
from app.schemas.connector import ConnectRequest, ConnectorStatusResponse
from app.utils.encryption import decrypt_json, encrypt_json

logger = logging.getLogger(__name__)


async def connect_integration(
    db: AsyncSession,
    tenant_id: UUID,
    request: ConnectRequest,
) -> ConnectorConfig:
    """
    Store encrypted credentials for an integration provider.
    Creates a new connector config or updates an existing disconnected one.
    """
    # Check for existing config
    result = await db.execute(
        select(ConnectorConfig).where(
            ConnectorConfig.tenant_id == tenant_id,
            ConnectorConfig.provider == request.provider,
        )
    )
    existing = result.scalar_one_or_none()

    encrypted_creds = encrypt_json(request.credentials)

    if existing:
        existing.credentials_encrypted = encrypted_creds
        existing.status = "active"
        existing.sync_error = None
        await db.flush()
        logger.info(f"Reconnected {request.provider} for tenant {tenant_id}")
        return existing

    config = ConnectorConfig(
        tenant_id=tenant_id,
        provider=request.provider,
        credentials_encrypted=encrypted_creds,
        permissions="read_only",
        status="active",
    )
    db.add(config)
    await db.flush()

    logger.info(f"Connected {request.provider} for tenant {tenant_id}")
    return config


async def get_connector_status(
    db: AsyncSession,
    tenant_id: UUID,
) -> list[ConnectorStatusResponse]:
    """Get status of all connectors for a tenant."""
    result = await db.execute(
        select(ConnectorConfig).where(ConnectorConfig.tenant_id == tenant_id)
    )
    configs = result.scalars().all()

    return [
        ConnectorStatusResponse(
            id=config.id,
            provider=config.provider,
            status=config.status,
            permissions=config.permissions,
            last_synced_at=config.last_synced_at,
            sync_error=config.sync_error,
        )
        for config in configs
    ]


async def get_connector_config(
    db: AsyncSession,
    tenant_id: UUID,
    connector_id: UUID,
) -> ConnectorConfig | None:
    """Get a specific connector config with tenant scoping."""
    result = await db.execute(
        select(ConnectorConfig).where(
            ConnectorConfig.id == connector_id,
            ConnectorConfig.tenant_id == tenant_id,
        )
    )
    return result.scalar_one_or_none()


async def get_decrypted_credentials(config: ConnectorConfig) -> dict:
    """Decrypt and return connector credentials."""
    return decrypt_json(config.credentials_encrypted)
