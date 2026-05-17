"""
AI CFO — ApprovalAction Model

Actions requiring founder sign-off before execution.
Created by the guardrails engine when requires_human_approval is True.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class ApprovalAction(Base, UUIDPrimaryKeyMixin):
    """Pending/completed approval action requiring founder review."""

    __tablename__ = "approval_actions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
    )  # "pricing_change" | "payment" | "report_send" | "categorization"
    action_payload: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
    )  # what the AI wants to do
    reasoning: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )  # why the AI recommends this
    data_sources: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
    )  # which records / documents triggered it
    expected_outcome: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )  # what happens if approved
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="pending",
    )  # "pending" | "approved" | "rejected"
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    rejection_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("NOW()"),
        nullable=False,
    )
