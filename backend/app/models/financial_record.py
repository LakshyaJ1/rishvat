"""
AI CFO — Financial Record Model

The canonical internal financial schema.
ALL external data sources normalize into this single table.
This is the foundation for deterministic financial computations.

Key design decisions:
- amount_cents stored as BIGINT to avoid floating point errors
- source + source_id uniquely identifies the external record (for upserts)
- metadata_json stores source-specific fields we don't want to lose
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, TenantMixin, UUIDPrimaryKeyMixin


class FinancialRecord(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "financial_records"

    # Which integration produced this record
    source: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # stripe, plaid, quickbooks, xero, razorpay, manual

    # External ID from the source system (for deduplication and upserts)
    source_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Canonical record type
    record_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # revenue, expense, transfer, refund, fee

    # Expense/revenue category
    category: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # payroll, infrastructure, marketing, legal, r_and_d, g_and_a

    # Amount in smallest currency unit (cents for USD, paise for INR)
    # Positive = inflow, Negative = outflow
    amount_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # ISO 4217 currency code
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    # Human-readable description
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # When the transaction actually occurred (not when we synced it)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Source-specific metadata we don't want to lose
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # When we last synced this record from the source
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Foreign key
    tenant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        # Prevent duplicate records from the same source
        UniqueConstraint(
            "tenant_id",
            "source",
            "source_id",
            name="uq_financial_records_tenant_source",
        ),
        # Query patterns: by tenant + time, tenant + source, tenant + type
        Index("ix_financial_records_tenant_time", "tenant_id", "occurred_at"),
        Index("ix_financial_records_tenant_source", "tenant_id", "source"),
        Index("ix_financial_records_tenant_type", "tenant_id", "record_type"),
        Index("ix_financial_records_tenant_category", "tenant_id", "category"),
    )

    def __repr__(self) -> str:
        return (
            f"<FinancialRecord {self.record_type} {self.amount_cents} "
            f"{self.currency} from {self.source}>"
        )
