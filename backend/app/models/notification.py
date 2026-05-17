"""
AI CFO — Notification Model

Stores anomaly alerts, runway warnings, compliance reminders, and sync errors.
Notifications are tenant-scoped and support read/dismiss state.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class Notification(Base, UUIDPrimaryKeyMixin):
    """Tenant-scoped notification for anomalies, warnings, and alerts."""

    __tablename__ = "notifications"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(50), nullable=False,
    )  # "anomaly" | "runway_warning" | "compliance" | "sync_error"
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="info",
    )  # "info" | "warning" | "critical"
    title: Mapped[str] = mapped_column(
        String(255), nullable=False,
    )
    body: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )
    data: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
    )  # structured payload for frontend rendering
    read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false"),
    )
    dismissed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("NOW()"),
        nullable=False,
    )
