"""Guardrails threshold rules — checks action amounts against AutopilotConfig limits."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RuleResult:
    """Result from a single guardrails rule check."""
    blocked: bool = False
    requires_human: bool = False
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def check_threshold(
    action_amount_cents: int | None,
    max_amount_cents: int,
    revenue_floor_cents: int,
    current_revenue_cents: int | None = None,
) -> RuleResult:
    """Check that an action's monetary value is within configured limits.

    Rules:
      - If action_amount_cents exceeds max_amount_cents, block the action.
      - If current revenue is below the revenue floor, block pricing changes.
    """
    result = RuleResult()

    if action_amount_cents is not None and max_amount_cents > 0:
        if action_amount_cents > max_amount_cents:
            result.blocked = True
            result.violations.append(
                f"Action amount ({action_amount_cents} cents) exceeds "
                f"configured maximum ({max_amount_cents} cents)"
            )

    if current_revenue_cents is not None and revenue_floor_cents > 0:
        if current_revenue_cents < revenue_floor_cents:
            result.blocked = True
            result.violations.append(
                f"Current revenue ({current_revenue_cents} cents) is below "
                f"revenue floor ({revenue_floor_cents} cents) — pricing changes blocked"
            )

    return result
