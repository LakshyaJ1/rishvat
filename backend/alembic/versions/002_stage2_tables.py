"""Stage 2 schema - autopilot_configs, notifications, approval_actions

Revision ID: 002_stage2_tables
Revises: 001_initial
Create Date: 2026-05-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers
revision: str = "002_stage2_tables"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Autopilot Configs ────────────────────────────────────────────────
    op.create_table(
        "autopilot_configs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("autonomy_level", sa.String(20), nullable=False, server_default="advisory"),
        sa.Column("max_amount_cents", sa.BigInteger, nullable=False, server_default=sa.text("0")),
        sa.Column("revenue_floor_cents", sa.BigInteger, nullable=False, server_default=sa.text("0")),
        sa.Column("locked", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_unique_constraint("uq_autopilot_tenant_category", "autopilot_configs", ["tenant_id", "category"])
    op.create_index("ix_autopilot_configs_tenant_id", "autopilot_configs", ["tenant_id"])

    # ── Notifications ────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="info"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("data", JSONB, nullable=True),
        sa.Column("read", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("dismissed", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_notifications_tenant_id", "notifications", ["tenant_id"])
    op.create_index("ix_notifications_tenant_type", "notifications", ["tenant_id", "type"])

    # ── Approval Actions ─────────────────────────────────────────────────
    op.create_table(
        "approval_actions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("action_payload", JSONB, nullable=True),
        sa.Column("reasoning", sa.Text, nullable=True),
        sa.Column("data_sources", JSONB, nullable=True),
        sa.Column("expected_outcome", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reviewed_by", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_approval_actions_tenant_id", "approval_actions", ["tenant_id"])
    op.create_index("ix_approval_actions_tenant_status", "approval_actions", ["tenant_id", "status"])

    # ── Financial records category index ─────────────────────────────────
    op.create_index("ix_financial_records_tenant_category", "financial_records", ["tenant_id", "category"])

    # ── RLS on new tables ────────────────────────────────────────────────
    for table in ["autopilot_configs", "notifications", "approval_actions"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation_{table} ON {table} "
            f"USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)"
        )


def downgrade() -> None:
    # Drop RLS
    for table in ["autopilot_configs", "notifications", "approval_actions"]:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    # Drop index
    op.drop_index("ix_financial_records_tenant_category", table_name="financial_records")

    # Drop tables
    op.drop_table("approval_actions")
    op.drop_table("notifications")
    op.drop_table("autopilot_configs")
