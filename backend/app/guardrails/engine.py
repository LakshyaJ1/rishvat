"""Deterministic guardrails engine.

This module must remain independent from LLM logic. It validates whether an AI
answer or action is allowed to reach the user or execute.

Stage 2 expansion adds threshold, reversibility, and jurisdiction rule checks.
"""

from pydantic import ValidationError

from app.guardrails.rules.jurisdiction_rules import check_jurisdiction
from app.guardrails.rules.reversibility_rules import check_reversibility
from app.guardrails.rules.threshold_rules import RuleResult, check_threshold
from app.guardrails.schemas import ACTION_MODELS, GuardrailInput, GuardrailResult


ALLOWED_AUTONOMY_LEVELS = {"advisory", "semi_auto", "full_auto"}
NON_REVERSIBLE_ACTION_TYPES = {"payment", "pricing_change_existing_customers"}


def _extract_action_amount_cents(payload: GuardrailInput) -> int | None:
    """Return the monetary value guardrails should compare to limits."""
    if not payload.ai_output:
        return None
    if payload.action_type in {
        "pricing_change",
        "pricing_change_existing_customers",
        "price_increase_existing_customers",
    }:
        return payload.ai_output.get("proposed_price_cents") or payload.ai_output.get(
            "amount_cents"
        )
    return payload.ai_output.get("amount_cents")


def validate_ai_output(
    payload: GuardrailInput,
    *,
    max_amount_cents: int = 0,
    revenue_floor_cents: int = 0,
    current_revenue_cents: int | None = None,
    jurisdiction: str = "US",
    category_locked: bool = False,
) -> GuardrailResult:
    """Validate an AI output with deterministic product rules.

    The function runs all rule checks in sequence and composes the final result.
    Extra keyword arguments allow the caller to inject per-tenant config; when
    called from the API layer without config, all values default to safe passthrough.
    """
    violations: list[str] = []
    warnings: list[str] = []

    # ── Core checks (Stage 1) ────────────────────────────────────────────
    if payload.requested_autonomy_level not in ALLOWED_AUTONOMY_LEVELS:
        violations.append("requested_autonomy_level is not supported")

    if not payload.ai_output:
        violations.append("ai_output is required")

    if payload.action_type == "recommendation" and not payload.data_sources:
        violations.append("recommendations must include source data")

    action_model = ACTION_MODELS.get(payload.action_type)
    if action_model:
        try:
            validation = action_model.model_validate(payload.ai_output)
            payload.ai_output.update(validation.model_dump(exclude_none=True))
        except ValidationError as exc:
            violations.extend(
                f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
                for error in exc.errors()
            )

    if payload.confidence < 0.5:
        warnings.append("low confidence output requires founder review")

    # ── Locked category check ────────────────────────────────────────────
    if category_locked:
        violations.append(
            "This action category is locked by the founder and cannot run autonomously"
        )

    # ── Threshold rules (Stage 2) ────────────────────────────────────────
    action_amount = _extract_action_amount_cents(payload)
    threshold_result = check_threshold(
        action_amount_cents=action_amount,
        max_amount_cents=max_amount_cents,
        revenue_floor_cents=revenue_floor_cents,
        current_revenue_cents=current_revenue_cents,
    )
    violations.extend(threshold_result.violations)
    warnings.extend(threshold_result.warnings)

    # ── Reversibility rules (Stage 2) ────────────────────────────────────
    reversibility_result = check_reversibility(
        action_type=payload.action_type,
        reversible=payload.reversible,
    )
    warnings.extend(reversibility_result.warnings)

    # ── Jurisdiction rules (Stage 2) ─────────────────────────────────────
    jurisdiction_result = check_jurisdiction(
        jurisdiction=jurisdiction,
        action_type=payload.action_type,
        action_payload=payload.ai_output,
    )
    violations.extend(jurisdiction_result.violations)
    warnings.extend(jurisdiction_result.warnings)

    # ── Compose final result ─────────────────────────────────────────────
    requires_human_approval = (
        payload.requested_autonomy_level == "advisory"
        or not payload.reversible
        or payload.action_type in NON_REVERSIBLE_ACTION_TYPES
        or reversibility_result.requires_human
        or jurisdiction_result.requires_human
        or threshold_result.blocked
        or bool(warnings)
    )

    approved = not violations
    if not approved:
        reason = "Blocked by deterministic guardrails."
    elif requires_human_approval:
        reason = "Allowed for display, but human approval is required before execution."
    else:
        reason = "Approved by deterministic guardrails."

    return GuardrailResult(
        approved=approved,
        modified_output=payload.ai_output if approved else None,
        violations=violations,
        warnings=warnings,
        requires_human_approval=requires_human_approval,
        reason=reason,
    )
