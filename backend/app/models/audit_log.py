"""
AI CFO — Audit Log Model

APPEND-ONLY audit log. No UPDATE or DELETE operations are permitted.
Every AI recommendation, action, approval, rejection, and guardrail
decision is logged here for investor-grade auditability.

This is the foundation for compliance and due diligence.
"""

from datetime import datetime

from datetime import timezone

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, UUIDPrimaryKeyMixin


class AuditLog(Base, UUIDPrimaryKeyMixin, TenantMixin):
    __tablename__ = "audit_logs"

    # Which tenant this log belongs to
    tenant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Which user triggered this (null for system/celery actions)
    user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Action classification
    # e.g., auth.login, auth.register, connector.sync, connector.connect,
    #        ai.recommendation, ai.ask, guardrail.block, autopilot.execute,
    #        approval.approve, approval.reject
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Structured detail of what happened
    action_detail: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Which data sources (documents, records, APIs) were used
    data_sources: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Outcome of the action
    outcome: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # success, failure, pending, blocked

    # Request IP address for security auditing
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # Timestamp — never updated, only set on creation
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_audit_logs_tenant_time", "tenant_id", "created_at"),
        Index("ix_audit_logs_tenant_action", "tenant_id", "action_type"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action_type} ({self.outcome}) at {self.created_at}>"
