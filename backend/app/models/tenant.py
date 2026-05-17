"""
AI CFO — Tenant Model

Represents an organization (startup) using the platform.
Every data record in the system is scoped to a tenant.
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Tenant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    jurisdiction: Mapped[str] = mapped_column(
        String(10), nullable=False, default="US"
    )

    # Shadow mode: new tenants run in shadow mode for 30 days
    shadow_mode_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=30),
        nullable=False,
    )

    # Autopilot level: advisory (default), semi_auto, full_auto
    autopilot_level: Mapped[str] = mapped_column(
        String(20), default="advisory", nullable=False
    )

    # Relationships
    users = relationship("User", back_populates="tenant", lazy="selectin")
    connector_configs = relationship(
        "ConnectorConfig", back_populates="tenant", lazy="selectin"
    )

    @property
    def is_in_shadow_mode(self) -> bool:
        """Check if tenant is still in 30-day shadow mode."""
        return datetime.now(timezone.utc) < self.shadow_mode_until

    def __repr__(self) -> str:
        return f"<Tenant {self.slug} ({self.id})>"
