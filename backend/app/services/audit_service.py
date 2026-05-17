"""
AI CFO — Audit Service

Writes append-only audit log entries.
This is the ONLY module that writes to the audit_logs table.
No other module should insert, update, or delete audit records.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


async def write_audit_log(
    db: AsyncSession,
    tenant_id: UUID,
    action_type: str,
    outcome: str,
    user_id: UUID | None = None,
    action_detail: dict | None = None,
    data_sources: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """
    Write an immutable audit log entry.

    This function is the single entry point for all audit logging.
    Every AI recommendation, action, approval, rejection, and guardrail
    decision MUST use this function.

    Args:
        db: Database session
        tenant_id: Tenant this action belongs to
        action_type: Dot-notated action type (e.g., "auth.login", "connector.sync")
        outcome: Result of the action ("success", "failure", "pending", "blocked")
        user_id: User who triggered this (None for system actions)
        action_detail: Structured detail of what happened
        data_sources: Which data points/documents were used
        ip_address: Client IP address
    """
    entry = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action_type=action_type,
        action_detail=action_detail,
        data_sources=data_sources,
        outcome=outcome,
        ip_address=ip_address,
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    await db.flush()

    logger.info(
        f"Audit: {action_type} [{outcome}] tenant={tenant_id}"
    )

    return entry
