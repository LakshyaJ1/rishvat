"""Stable guardrails engine contracts shared with the AI layer."""

from uuid import UUID

from pydantic import BaseModel, Field


class BaseAction(BaseModel):
    """Common deterministic action fields used by guardrail rules."""

    amount_cents: int | None = Field(default=None, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    description: str | None = None


class PricingChangeAction(BaseAction):
    """AI-proposed pricing change contract."""

    plan_id: str | None = None
    current_price_cents: int | None = Field(default=None, ge=0)
    proposed_price_cents: int | None = Field(default=None, ge=0)
    target_states: list[str] = Field(default_factory=list)
    applies_to_existing_customers: bool = False


class PaymentAction(BaseAction):
    """AI-proposed payment contract."""

    vendor_id: str | None = None
    vendor_name: str | None = None
    destination_country: str | None = None
    payment_method: str | None = None


class ReportAction(BaseAction):
    """AI-proposed report or recommendation contract."""

    report_type: str | None = None
    recipients: list[str] = Field(default_factory=list)
    answer: str | None = None


class AlertAction(BaseAction):
    """AI-proposed alert or notification contract."""

    severity: str = "info"
    title: str | None = None
    body: str | None = None


ACTION_MODELS = {
    "pricing_change": PricingChangeAction,
    "pricing_change_existing_customers": PricingChangeAction,
    "price_increase_existing_customers": PricingChangeAction,
    "payment": PaymentAction,
    "wire_transfer": PaymentAction,
    "report": ReportAction,
    "report_send": ReportAction,
    "recommendation": ReportAction,
    "alert": AlertAction,
}


class GuardrailInput(BaseModel):
    """Input contract for validating AI recommendations and actions."""

    tenant_id: UUID
    action_type: str
    ai_output: dict
    data_sources: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    reversible: bool = True
    requested_autonomy_level: str = "advisory"
    category: str | None = None


class GuardrailValidateRequest(BaseModel):
    """Authenticated API request contract; tenant comes from JWT."""

    action_type: str
    ai_output: dict
    data_sources: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    reversible: bool = True
    requested_autonomy_level: str = "advisory"
    category: str | None = None
    reasoning: str | None = None
    expected_outcome: str | None = None


class GuardrailResult(BaseModel):
    """Deterministic validation result."""

    approved: bool
    modified_output: dict | None = None
    violations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    requires_human_approval: bool
    reason: str
    approval_action_id: UUID | None = None
