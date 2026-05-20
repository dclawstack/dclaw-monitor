"""Background task: evaluate alert rules against recent metric samples."""
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.utils import utc_now
from app.models.alert import Alert
from app.repositories.alert_repo import AlertRuleRepository, AlertRepository
from app.repositories.metric_repo import MetricRepository


_engine = create_async_engine(settings.database_url, pool_pre_ping=True)
_async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    _engine, expire_on_commit=False
)

DEFAULT_WINDOW_SECONDS = 300


def _evaluate_operator(value: float, operator: str, threshold: float) -> bool:
    if operator == "gt":
        return value > threshold
    elif operator == "lt":
        return value < threshold
    elif operator == "eq":
        return value == threshold
    elif operator == "gte":
        return value >= threshold
    elif operator == "lte":
        return value <= threshold
    return False


async def run_alert_evaluation() -> None:
    """Evaluate all active alert rules and fire alerts when conditions are met."""
    async with _async_session() as db:
        rule_repo = AlertRuleRepository(db)
        alert_repo = AlertRepository(db)
        metric_repo = MetricRepository(db)

        rules = await rule_repo.list_active()

        for rule in rules:
            # Determine window
            window_seconds = getattr(rule, "window_seconds", None) or DEFAULT_WINDOW_SECONDS
            since = utc_now() - timedelta(seconds=window_seconds)

            # Query recent metric samples
            samples, _ = await metric_repo.list_by_name(
                name=rule.metric_name,
                service_id=rule.service_id,
                since=since,
                limit=10000,
            )

            if not samples:
                continue

            # Compute mean
            mean_value = sum(s.value for s in samples) / len(samples)

            # Evaluate condition
            condition_met = _evaluate_operator(mean_value, rule.operator, rule.threshold)

            if not condition_met:
                continue

            # Check if there is already an open alert for this rule
            open_alerts, _ = await alert_repo.list_by_status("open", limit=1000)
            already_firing = any(
                str(a.rule_id) == str(rule.id) for a in open_alerts
            )

            if already_firing:
                continue

            # Create new alert
            alert = Alert(
                rule_id=rule.id,
                service_id=rule.service_id,
                title=f"Alert: {rule.name}",
                message=(
                    f"Metric '{rule.metric_name}' mean={mean_value:.4f} "
                    f"{rule.operator} {rule.threshold} "
                    f"(window={window_seconds}s, samples={len(samples)})"
                ),
                severity=rule.severity,
                status="open",
            )
            await alert_repo.create(alert)
