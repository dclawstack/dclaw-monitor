"""Z-score rolling baseline anomaly detection."""
import logging
import statistics
from uuid import UUID

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.models.alert import Alert
from app.models.metric import MetricSample

logger = logging.getLogger(__name__)

MIN_SAMPLES = 30  # cold start protection

_engine = None
_async_session = None


def _get_session_factory():
    global _engine, _async_session
    if _async_session is None:
        _engine = create_async_engine(settings.database_url, pool_pre_ping=True)
        _async_session = async_sessionmaker(_engine, expire_on_commit=False)
    return _async_session


async def check_anomaly(
    service_id: UUID | None,
    metric_name: str,
    new_value: float,
) -> bool:
    """Returns True if anomaly detected and alert was created. Uses its own DB session."""
    session_factory = _get_session_factory()
    async with session_factory() as db:
        return await _do_check(service_id, metric_name, new_value, db)


async def _do_check(
    service_id: UUID | None,
    metric_name: str,
    new_value: float,
    db,
) -> bool:
    q = (
        select(MetricSample)
        .where(MetricSample.name == metric_name)
        .order_by(MetricSample.sampled_at.desc())
        .limit(101)
    )
    if service_id is not None:
        q = q.where(MetricSample.service_id == service_id)

    result = await db.execute(q)
    samples = list(result.scalars().all())

    # Skip the newest sample (index 0, just inserted)
    baseline_samples = samples[1:] if samples else []

    if len(baseline_samples) < MIN_SAMPLES:
        return False

    values = [s.value for s in baseline_samples]
    mean = statistics.mean(values)

    try:
        stdev = statistics.stdev(values)
    except statistics.StatisticsError:
        return False

    if stdev <= 0:
        return False

    z_score = abs(new_value - mean) / stdev
    if z_score <= 3.0:
        return False

    logger.info(
        "Anomaly detected for %s: value=%.4f, z=%.2f (mean=%.4f stdev=%.4f)",
        metric_name, new_value, z_score, mean, stdev,
    )

    alert = Alert(
        service_id=service_id,
        title=f"Anomaly detected: {metric_name}",
        message=(
            f"Value {new_value:.4f} is {z_score:.1f}σ from rolling mean "
            f"({mean:.4f} ± {stdev:.4f})."
        ),
        severity="warning",
        status="open",
    )
    db.add(alert)
    await db.commit()
    return True
