"""
AI CFO — Connector Config Model

Stores configuration and encrypted credentials for each integration.
Credentials are AES-256 encrypted at rest.
Each tenant can have at most one config per provider.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, TenantMixin, UUIDPrimaryKeyMixin


class ConnectorConfig(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "connector_configs"

    # Which integration provider
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # stripe, plaid, quickbooks, xero, razorpay

    # AES-256 encrypted JSON blob containing API keys and tokens
    credentials_encrypted: Mapped[str] = mapped_column(Text, nullable=False)

    # Permission level — read_only by default, read_write requires explicit grant
    permissions: Mapped[str] = mapped_column(
        String(20), default="read_only", nullable=False
    )

    # Connection status
    status: Mapped[str] = mapped_column(
        String(20), default="active", nullable=False
    )  # active, disconnected, error

    # Last successful sync timestamp
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Last sync error message (if any)
    sync_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Foreign key
    tenant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="connector_configs")

    __table_args__ = (
        # One config per provider per tenant
        UniqueConstraint("tenant_id", "provider", name="uq_connector_tenant_provider"),
    )

    def __repr__(self) -> str:
        return f"<ConnectorConfig {self.provider} ({self.status}) tenant={self.tenant_id}>"
