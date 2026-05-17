"""AI CFO — Anomaly Detection Celery Task

Daily scan of all tenant financial records for unusual patterns:
- Expense spikes (current 7-day > 2× rolling 30-day average per category)
- Revenue drops (current 7-day revenue < 50% of rolling 30-day average)
- Duplicate charges (same amount, same source, within 48 hours)

Writes detected anomalies to the notifications table.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _get_sync_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.config import get_settings

    settings = get_settings()
    engine = create_engine(settings.database_url_sync, pool_pre_ping=True)
    return sessionmaker(bind=engine)()


@celery_app.task(name="app.tasks.anomaly_detection.detect_anomalies")
def detect_anomalies():
    """Scan all tenants for financial anomalies. Runs daily via Beat."""
    from app.models.financial_record import FinancialRecord
    from app.models.notification import Notification
    from app.models.tenant import Tenant

    session = _get_sync_session()
    now = datetime.now(timezone.utc)
    total_anomalies = 0

    try:
        tenants = session.query(Tenant).all()
        logger.info(f"Anomaly detection: scanning {len(tenants)} tenants")

        for tenant in tenants:
            records = (
                session.query(FinancialRecord)
                .filter(
                    FinancialRecord.tenant_id == tenant.id,
                    FinancialRecord.occurred_at >= now - timedelta(days=90),
                )
                .order_by(FinancialRecord.occurred_at.desc())
                .all()
            )

            if not records:
                continue

            anomalies = []
            anomalies.extend(_detect_expense_spikes(records, now))
            anomalies.extend(_detect_revenue_drops(records, now))
            anomalies.extend(_detect_duplicate_charges(records, now))

            for anomaly in anomalies:
                session.add(Notification(
                    tenant_id=tenant.id,
                    type="anomaly",
                    severity=anomaly["severity"],
                    title=anomaly["title"],
                    body=anomaly["body"],
                    data=anomaly.get("data"),
                ))

            total_anomalies += len(anomalies)

        session.commit()
        logger.info(f"Anomaly detection complete: {total_anomalies} anomalies found")
        return {"status": "success", "anomalies_found": total_anomalies}

    except Exception as e:
        session.rollback()
        logger.error(f"Anomaly detection failed: {e}", exc_info=True)
        raise
    finally:
        session.close()


def _detect_expense_spikes(records, now):
    """Detect categories where 7-day spend > 2× the 30-day rolling average."""
    anomalies = []
    expenses = [r for r in records if r.record_type in {"expense", "fee"} and r.amount_cents < 0]

    # Group by category
    by_category = defaultdict(list)
    for r in expenses:
        by_category[r.category or "uncategorized"].append(r)

    for category, cat_records in by_category.items():
        rolling_30 = [r for r in cat_records if r.occurred_at >= now - timedelta(days=30)]
        recent_7 = [r for r in cat_records if r.occurred_at >= now - timedelta(days=7)]

        if not rolling_30:
            continue

        avg_30_weekly = sum(abs(r.amount_cents) for r in rolling_30) / (30 / 7)
        total_7 = sum(abs(r.amount_cents) for r in recent_7)

        if avg_30_weekly > 0 and total_7 > 2 * avg_30_weekly:
            anomalies.append({
                "severity": "warning",
                "title": f"Expense spike in {category}",
                "body": (
                    f"Spending in '{category}' over the last 7 days "
                    f"(${total_7 / 100:.2f}) is more than 2× the 30-day weekly "
                    f"average (${avg_30_weekly / 100:.2f})."
                ),
                "data": {
                    "category": category,
                    "recent_7d_cents": total_7,
                    "avg_weekly_cents": round(avg_30_weekly),
                },
            })

    return anomalies


def _detect_revenue_drops(records, now):
    """Detect if 7-day revenue < 50% of 30-day rolling average."""
    anomalies = []
    revenue = [r for r in records if r.record_type == "revenue" and r.amount_cents > 0]

    rolling_30 = [r for r in revenue if r.occurred_at >= now - timedelta(days=30)]
    recent_7 = [r for r in revenue if r.occurred_at >= now - timedelta(days=7)]

    if not rolling_30:
        return anomalies

    avg_30_weekly = sum(r.amount_cents for r in rolling_30) / (30 / 7)
    total_7 = sum(r.amount_cents for r in recent_7)

    if avg_30_weekly > 0 and total_7 < 0.5 * avg_30_weekly:
        anomalies.append({
            "severity": "critical",
            "title": "Revenue drop detected",
            "body": (
                f"Revenue over the last 7 days (${total_7 / 100:.2f}) is less "
                f"than 50% of the 30-day weekly average (${avg_30_weekly / 100:.2f})."
            ),
            "data": {
                "recent_7d_cents": total_7,
                "avg_weekly_cents": round(avg_30_weekly),
            },
        })

    return anomalies


def _detect_duplicate_charges(records, now):
    """Detect same amount from same source within 48 hours."""
    anomalies = []
    recent = [r for r in records if r.occurred_at >= now - timedelta(days=7)]

    # Group by (source, abs(amount_cents))
    groups = defaultdict(list)
    for r in recent:
        key = (r.source, abs(r.amount_cents))
        groups[key].append(r)

    for (source, amount), group in groups.items():
        if len(group) < 2:
            continue
        # Sort by time and check for pairs within 48h
        group.sort(key=lambda r: r.occurred_at)
        for i in range(len(group) - 1):
            delta = group[i + 1].occurred_at - group[i].occurred_at
            if delta <= timedelta(hours=48):
                anomalies.append({
                    "severity": "warning",
                    "title": f"Possible duplicate charge from {source}",
                    "body": (
                        f"Two charges of ${amount / 100:.2f} from '{source}' "
                        f"occurred within {delta.total_seconds() / 3600:.1f} hours."
                    ),
                    "data": {
                        "source": source,
                        "amount_cents": amount,
                        "source_ids": [group[i].source_id, group[i + 1].source_id],
                    },
                })
                break  # Only flag once per group

    return anomalies
