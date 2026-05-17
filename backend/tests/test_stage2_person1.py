"""Stage 2 Person 1 backend contract tests."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.approval_action import ApprovalAction
from app.models.audit_log import AuditLog
from app.models.financial_record import FinancialRecord
from app.services.notification_service import create_notification


@pytest.mark.asyncio
async def test_autopilot_config_drives_guardrails_and_creates_approval(
    client: AsyncClient,
    db_session,
    test_tenant,
    auth_headers: dict,
):
    test_tenant.jurisdiction = "IN"
    await db_session.flush()

    config_response = await client.post(
        "/api/v1/autopilot/configure",
        json={
            "category": "payment",
            "autonomy_level": "full_auto",
            "max_amount_cents": 100_000,
            "revenue_floor_cents": 0,
            "locked": False,
        },
        headers=auth_headers,
    )
    assert config_response.status_code == 200

    response = await client.post(
        "/api/v1/guardrails/validate",
        json={
            "action_type": "payment",
            "ai_output": {
                "amount_cents": 50_000,
                "currency": "USD",
                "vendor_name": "US Vendor",
            },
            "data_sources": ["financial_record:payment-test"],
            "confidence": 0.95,
            "reversible": True,
            "reasoning": "Invoice is due and cash is sufficient.",
            "expected_outcome": "Vendor payment is ready for founder review.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["approved"] is True
    assert data["requires_human_approval"] is True
    assert data["approval_action_id"] is not None
    assert any("FEMA compliance" in warning for warning in data["warnings"])

    approval_result = await db_session.execute(select(ApprovalAction))
    approval = approval_result.scalar_one()
    assert str(approval.id) == data["approval_action_id"]
    assert approval.status == "pending"
    assert approval.action_payload["amount_cents"] == 50_000


@pytest.mark.asyncio
async def test_guardrails_blocks_locked_or_threshold_exceeding_category(
    client: AsyncClient,
    db_session,
    test_tenant,
    auth_headers: dict,
):
    db_session.add(
        FinancialRecord(
            tenant_id=test_tenant.id,
            source="manual",
            source_id="stage2-revenue",
            record_type="revenue",
            category="subscription",
            amount_cents=25_000,
            currency="USD",
            description="Stage 2 revenue",
            occurred_at=test_tenant.created_at,
            synced_at=test_tenant.created_at,
        )
    )
    await db_session.flush()

    config_response = await client.post(
        "/api/v1/autopilot/configure",
        json={
            "category": "pricing",
            "autonomy_level": "full_auto",
            "max_amount_cents": 10_000,
            "revenue_floor_cents": 100_000,
            "locked": False,
        },
        headers=auth_headers,
    )
    assert config_response.status_code == 200

    response = await client.post(
        "/api/v1/guardrails/validate",
        json={
            "action_type": "pricing_change",
            "ai_output": {
                "plan_id": "starter",
                "current_price_cents": 5_000,
                "proposed_price_cents": 15_000,
                "currency": "USD",
            },
            "data_sources": ["financial_record:stage2-revenue"],
            "confidence": 0.9,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["approved"] is False
    assert data["approval_action_id"] is None
    assert any("exceeds configured maximum" in violation for violation in data["violations"])
    assert any("below revenue floor" in violation for violation in data["violations"])


@pytest.mark.asyncio
async def test_approval_review_endpoints_are_tenant_scoped_and_audited(
    client: AsyncClient,
    db_session,
    test_tenant,
    auth_headers: dict,
):
    create_response = await client.post(
        "/api/v1/guardrails/validate",
        json={
            "action_type": "payment",
            "ai_output": {"amount_cents": 1_000, "currency": "USD"},
            "data_sources": ["financial_record:approval"],
            "confidence": 0.9,
            "reversible": False,
        },
        headers=auth_headers,
    )
    action_id = create_response.json()["approval_action_id"]
    assert action_id is not None

    list_response = await client.get("/api/v1/approvals?status=pending", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == action_id

    approve_response = await client.post(
        f"/api/v1/approvals/{action_id}/approve",
        headers=auth_headers,
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    audit_result = await db_session.execute(
        select(AuditLog).where(AuditLog.action_type == "approval.approve")
    )
    assert audit_result.scalar_one().outcome == "success"


@pytest.mark.asyncio
async def test_notifications_can_be_listed_read_and_dismissed(
    client: AsyncClient,
    db_session,
    test_tenant,
    auth_headers: dict,
):
    notification = await create_notification(
        db_session,
        tenant_id=test_tenant.id,
        type="anomaly",
        severity="warning",
        title="Expense spike",
        body="Cloud spend increased.",
        data={"category": "infrastructure"},
    )
    await db_session.flush()

    list_response = await client.get("/api/v1/notifications", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == str(notification.id)

    read_response = await client.post(
        f"/api/v1/notifications/{notification.id}/read",
        headers=auth_headers,
    )
    assert read_response.status_code == 200

    dismiss_response = await client.post(
        f"/api/v1/notifications/{notification.id}/dismiss",
        headers=auth_headers,
    )
    assert dismiss_response.status_code == 200

    hidden_response = await client.get("/api/v1/notifications", headers=auth_headers)
    assert hidden_response.status_code == 200
    assert hidden_response.json() == []
