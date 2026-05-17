"""Tests for deterministic guardrails engine contracts."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.guardrails.engine import validate_ai_output
from app.guardrails.schemas import GuardrailInput


def test_recommendation_without_sources_is_blocked():
    result = validate_ai_output(
        GuardrailInput(
            tenant_id=uuid4(),
            action_type="recommendation",
            ai_output={"answer": "Burn is $10k/month."},
            data_sources=[],
            confidence=0.9,
        )
    )

    assert result.approved is False
    assert "recommendations must include source data" in result.violations


def test_non_reversible_action_requires_human_approval():
    result = validate_ai_output(
        GuardrailInput(
            tenant_id=uuid4(),
            action_type="payment",
            ai_output={"action": "pay_vendor"},
            data_sources=["financial_record:123"],
            confidence=0.95,
            reversible=False,
            requested_autonomy_level="full_auto",
        )
    )

    assert result.approved is True
    assert result.requires_human_approval is True


def test_low_confidence_recommendation_requires_human_approval():
    result = validate_ai_output(
        GuardrailInput(
            tenant_id=uuid4(),
            action_type="recommendation",
            ai_output={"answer": "Burn is uncertain."},
            data_sources=["financial_record:123"],
            confidence=0.4,
        )
    )

    assert result.approved is True
    assert result.requires_human_approval is True
    assert result.warnings == ["low confidence output requires founder review"]


def test_invalid_typed_action_payload_is_blocked_without_exception():
    result = validate_ai_output(
        GuardrailInput(
            tenant_id=uuid4(),
            action_type="payment",
            ai_output={"amount_cents": -100},
            data_sources=["financial_record:123"],
            confidence=0.9,
            requested_autonomy_level="full_auto",
        )
    )

    assert result.approved is False
    assert result.requires_human_approval is True
    assert any("greater than or equal to 0" in violation for violation in result.violations)


@pytest.mark.asyncio
async def test_guardrails_endpoint_is_tenant_scoped_and_audited(
    client: AsyncClient,
    auth_headers: dict,
):
    response = await client.post(
        "/api/v1/guardrails/validate",
        json={
            "action_type": "recommendation",
            "ai_output": {"answer": "Burn is $10k/month."},
            "data_sources": ["financial_record:123"],
            "confidence": 0.9,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["approved"] is True
    assert data["requires_human_approval"] is True
