"""AI CFO — Expense Categorization Celery Task

Rule-based auto-categorization of uncategorized financial records.
Stage 2 uses keyword matching against known SaaS vendors and expense types.
Stage 3 replaces this with a fine-tuned sentence-transformer classifier.

Runs after each connector sync and can also be triggered manually.
"""

import logging
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

# Keyword → category mapping for rule-based classification.
# Keys are matched case-insensitively against the record description.
CATEGORY_RULES: list[tuple[str, str]] = [
    # Infrastructure
    ("aws", "infrastructure"),
    ("amazon web services", "infrastructure"),
    ("google cloud", "infrastructure"),
    ("gcp", "infrastructure"),
    ("azure", "infrastructure"),
    ("digitalocean", "infrastructure"),
    ("heroku", "infrastructure"),
    ("vercel", "infrastructure"),
    ("netlify", "infrastructure"),
    ("cloudflare", "infrastructure"),
    ("github", "infrastructure"),
    ("gitlab", "infrastructure"),
    ("docker", "infrastructure"),
    # Payroll
    ("gusto", "payroll"),
    ("rippling", "payroll"),
    ("deel", "payroll"),
    ("remote.com", "payroll"),
    ("payroll", "payroll"),
    ("salary", "payroll"),
    ("darwinbox", "payroll"),
    # Marketing
    ("google ads", "marketing"),
    ("meta ads", "marketing"),
    ("facebook ads", "marketing"),
    ("linkedin ads", "marketing"),
    ("twitter ads", "marketing"),
    ("hubspot", "marketing"),
    ("mailchimp", "marketing"),
    ("sendgrid", "marketing"),
    ("advertising", "marketing"),
    # Sales
    ("salesforce", "sales"),
    ("pipedrive", "sales"),
    ("apollo", "sales"),
    # Legal
    ("legal", "legal"),
    ("lawyer", "legal"),
    ("attorney", "legal"),
    ("compliance", "legal"),
    # G&A (General & Administrative)
    ("notion", "g_and_a"),
    ("slack", "g_and_a"),
    ("zoom", "g_and_a"),
    ("office", "g_and_a"),
    ("gsuite", "g_and_a"),
    ("google workspace", "g_and_a"),
    ("1password", "g_and_a"),
    ("figma", "g_and_a"),
    ("linear", "g_and_a"),
    ("jira", "g_and_a"),
    ("atlassian", "g_and_a"),
    # Fees
    ("stripe fee", "fee"),
    ("transaction fee", "fee"),
    ("processing fee", "fee"),
    ("razorpay fee", "fee"),
]


def categorize_by_description(description: str) -> str:
    """Match a description against known vendor/category keywords.

    Returns the matched category or 'uncategorized' if no match.
    """
    if not description:
        return "uncategorized"

    desc_lower = description.lower()
    for keyword, category in CATEGORY_RULES:
        if keyword in desc_lower:
            return category
    return "uncategorized"


def _get_sync_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.config import get_settings

    settings = get_settings()
    engine = create_engine(settings.database_url_sync, pool_pre_ping=True)
    return sessionmaker(bind=engine)()


@celery_app.task(name="app.tasks.categorize_expenses.categorize_tenant_expenses")
def categorize_tenant_expenses(tenant_id: str):
    """Categorize all uncategorized records for a tenant.

    Called after each connector sync. Can also be triggered manually.
    """
    from uuid import UUID
    from app.models.financial_record import FinancialRecord

    session = _get_sync_session()
    categorized = 0

    try:
        records = (
            session.query(FinancialRecord)
            .filter(
                FinancialRecord.tenant_id == UUID(tenant_id),
                FinancialRecord.category.in_(["uncategorized", None]),
            )
            .all()
        )

        for record in records:
            # Skip records with a manual override
            metadata = record.metadata_json or {}
            if metadata.get("manual_category"):
                continue

            new_category = categorize_by_description(record.description or "")
            if new_category != "uncategorized":
                record.category = new_category
                categorized += 1

        session.commit()
        logger.info(
            f"Categorization complete: tenant={tenant_id} "
            f"categorized={categorized} of {len(records)} uncategorized records"
        )
        return {"status": "success", "categorized": categorized, "total": len(records)}

    except Exception as e:
        session.rollback()
        logger.error(f"Categorization failed: {e}", exc_info=True)
        raise
    finally:
        session.close()
