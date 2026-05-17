"""Guardrails jurisdiction rules — validates actions against regional regulations."""

from __future__ import annotations

from app.guardrails.rules.threshold_rules import RuleResult

# Jurisdiction-specific rule sets.
# Each rule returns (check_fn_name, description).
JURISDICTION_RULES: dict[str, list[tuple[str, str]]] = {
    "IN": [
        ("gst_threshold", "GST registration required above ₹20 lakh annual turnover"),
        ("fema_foreign_payment", "FEMA compliance required for foreign currency payments"),
        ("tds_deduction", "TDS deduction required on specified payment categories"),
    ],
    "US": [
        ("sales_tax_nexus", "Sales tax obligations based on economic nexus thresholds"),
        ("estimated_tax", "Quarterly estimated tax payment deadlines"),
    ],
    "EU": [
        ("vat_return", "VAT return filing obligations"),
        ("oss_filing", "One-Stop Shop filing for cross-border EU sales"),
    ],
}


def check_jurisdiction(
    jurisdiction: str,
    action_type: str,
    action_payload: dict | None = None,
) -> RuleResult:
    """Validate an action against jurisdiction-specific regulations.

    Stage 2 implements awareness checks (warnings) for regulatory areas.
    Full compliance blocking requires richer data (Stage 3+).
    """
    result = RuleResult()
    payload = action_payload or {}

    rules = JURISDICTION_RULES.get(jurisdiction.upper(), [])

    if not rules:
        return result  # No rules for unknown jurisdictions

    # India-specific checks
    if jurisdiction.upper() == "IN":
        if action_type in {"payment", "wire_transfer"}:
            currency = payload.get("currency", "INR")
            if currency != "INR":
                result.requires_human = True
                result.warnings.append(
                    "Foreign currency payment from India jurisdiction requires "
                    "FEMA compliance review before execution"
                )

        if action_type == "pricing_change":
            amount = payload.get("amount_cents", 0)
            if amount > 20_00_000_00:  # ₹20 lakh in paise
                result.warnings.append(
                    "Pricing at this level may trigger GST registration "
                    "requirements under Indian tax law"
                )

    # US-specific checks
    if jurisdiction.upper() == "US":
        if action_type in {"pricing_change", "subscription_create"}:
            states = payload.get("target_states", [])
            if len(states) > 5:
                result.warnings.append(
                    "Selling across multiple US states may trigger sales tax "
                    "nexus obligations — consult tax advisor"
                )

    return result
