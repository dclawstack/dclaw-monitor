"""Z-score rolling baseline anomaly detection."""
import logging
import statistics
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.alert import Alert
from app.models.metric import MetricSample

logger = logging.getLogger(__name__)

MIN_SAMPLES = 30  # cold start protection


async def check_anomaly(
    service_id: UUID | None,
    metric_name: str,
    new_value: float,
    db: AsyncSession,
) -> bool:
    """Returns True if anomaly detected and alert was created."""
    # Fetch last 100 samples for this (service_id, metric_name) EXCLUDING the newest
    q = (
        select(MetricSample)
        .where(MetricSample.name == metric_name)
        .order_by(MetricSample.sampled_at.desc())
        .limit(101)  # fetch 101 to exclude the one we just inserted
    )
    if service_id is not None:
        q = q.where(MetricSample.service_id == service_id)

    result = await db.execute(q)
    samples = list(result.scalars().all())

    # Skip the newest sample (index 0, which is the one we just inserted)
    baseline_samples = samples[1:] if samples else []

    if len(baseline_samples) < MIN_SAMPLES:
        logger.debug(
            "Anomaly check skipped for %s (only %d baseline samples, need %d)",
            metric_name,
            len(baseline_samples),
            MIN_SAMPLES,
        )
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

    # Anomaly detected — create an alert
    logger.info(
        "Anomaly detected for metric %s: value=%.4f, mean=%.4f, stdev=%.4f, z=%.2f",
        metric_name,
        new_value,
        mean,
        stdev,
        z_score,
    )

    alert = Alert(
        service_id=service_id,
        title=f"Anomaly detected: {metric_name}",
        message=(
            f"Value {new_value:.4f} is {z_score:.1f} standard deviations from the "
            f"rolling mean ({mean:.4f} ± {stdev:.4f})."
        ),
        severity="warning",
        status="open",
    )
    db.add(alert)
    await db.commit()
    return True
