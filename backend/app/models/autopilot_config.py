"""
AI CFO — AutopilotConfig Model

Per-category autonomy settings for a tenant.
Controls which actions the AI can execute autonomously vs. which require
founder approval.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AutopilotConfig(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Per-category autonomy configuration for a tenant."""

    __tablename__ = "autopilot_configs"
    __table_args__ = (
        UniqueConstraint("tenant_id", "category", name="uq_autopilot_tenant_category"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False,
    )  # "payment", "pricing", "reporting", "categorization", "alerts"
    autonomy_level: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="advisory",
    )  # "advisory" | "semi_auto" | "full_auto"
    max_amount_cents: Mapped[int] = mapped_column(
        BigInteger, nullable=False, server_default=text("0"),
    )
    revenue_floor_cents: Mapped[int] = mapped_column(
        BigInteger, nullable=False, server_default=text("0"),
    )
    locked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false"),
    )  # founder-locked categories can never run autonomously
