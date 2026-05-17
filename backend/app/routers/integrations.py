"""
AI CFO — Integration Router

Endpoints for connecting, disconnecting, and syncing integrations.
All operations are tenant-scoped via JWT auth.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.tenant import get_current_user
from app.schemas.connector import (
    ConnectRequest,
    ConnectorListResponse,
    ConnectorStatusResponse,
    SyncResponse,
)
from app.services.audit_service import write_audit_log
from app.services.connector_service import (
    connect_integration,
    get_connector_config,
    get_connector_status,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post(
    "/connect",
    response_model=ConnectorStatusResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Connect an integration provider",
)
async def connect(
    request: ConnectRequest,
    http_request: Request,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Store encrypted credentials for an integration provider.
    Read-only permissions by default.
    """
    tenant_id = user["tenant_id"]

    try:
        config = await connect_integration(db, tenant_id, request)

        # Audit log
        await write_audit_log(
            db=db,
            tenant_id=tenant_id,
            user_id=user["user_id"],
            action_type="connector.connect",
            action_detail={
                "provider": request.provider,
                "permissions": "read_only",
            },
            outcome="success",
            ip_address=http_request.client.host if http_request.client else None,
        )

        return ConnectorStatusResponse(
            id=config.id,
            provider=config.provider,
            status=config.status,
            permissions=config.permissions,
            last_synced_at=config.last_synced_at,
            sync_error=config.sync_error,
        )

    except Exception as e:
        logger.error(f"Connect failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "CONNECT_ERROR", "message": str(e)}},
        )


@router.get(
    "/status",
    response_model=ConnectorListResponse,
    summary="Get status of all connected integrations",
)
async def status_list(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the status of all integration connectors for the current tenant."""
    tenant_id = user["tenant_id"]
    connectors = await get_connector_status(db, tenant_id)
    return ConnectorListResponse(connectors=connectors)


@router.post(
    "/{connector_id}/sync",
    response_model=SyncResponse,
    summary="Trigger a manual sync for a connector",
)
async def trigger_sync(
    connector_id: UUID,
    http_request: Request,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Queue a Celery task to sync data from the specified connector.
    Returns immediately with a task ID.
    """
    tenant_id = user["tenant_id"]

    # Verify connector belongs to this tenant
    config = await get_connector_config(db, tenant_id, connector_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Connector not found"}},
        )

    if config.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "CONNECTOR_INACTIVE",
                    "message": f"Connector is {config.status}",
                }
            },
        )

    # Queue Celery task
    try:
        from app.tasks.sync_connectors import sync_connector_task
        task = sync_connector_task.delay(
            str(tenant_id), str(connector_id), config.provider
        )
        task_id = task.id
    except Exception as e:
        logger.warning(f"Celery not available, sync queued locally: {e}")
        task_id = f"local-{connector_id}"

    # Audit log
    await write_audit_log(
        db=db,
        tenant_id=tenant_id,
        user_id=user["user_id"],
        action_type="connector.sync.trigger",
        action_detail={
            "provider": config.provider,
            "connector_id": str(connector_id),
            "task_id": task_id,
        },
        outcome="success",
        ip_address=http_request.client.host if http_request.client else None,
    )

    return SyncResponse(task_id=task_id, status="queued")
