"""Guardrails reversibility rules — escalates non-reversible actions to human."""

from __future__ import annotations

from app.guardrails.rules.threshold_rules import RuleResult

# Actions that cannot be undone — always require founder approval regardless
# of autopilot settings.
NON_REVERSIBLE_ACTIONS = {
    "payment",
    "wire_transfer",
    "price_increase_existing_customers",
    "pricing_change_existing_customers",
    "subscription_cancel",
    "refund_issue",
}


def check_reversibility(action_type: str, reversible: bool) -> RuleResult:
    """Non-reversible actions always require human approval.

    Even in full_auto mode, an action that cannot be undone must be
    reviewed and approved by the founder.
    """
    result = RuleResult()

    if action_type in NON_REVERSIBLE_ACTIONS:
        result.requires_human = True
        result.warnings.append(
            f"Action type '{action_type}' is classified as non-reversible "
            "and requires founder approval regardless of autonomy level"
        )

    if not reversible:
        result.requires_human = True
        if not result.warnings:
            result.warnings.append(
                "Action is marked as non-reversible and requires founder approval"
            )

    return result
