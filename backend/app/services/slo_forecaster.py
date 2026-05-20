"""Linear regression SLO budget exhaustion forecaster."""
import logging
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.utils import utc_now
from app.models.metric import MetricSample

logger = logging.getLogger(__name__)


def linear_regression(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Pure Python least-squares. Returns (slope, intercept)."""
    n = len(xs)
    if n < 2:
        return 0.0, 0.0
    sx = sum(xs)
    sy = sum(ys)
    sxy = sum(x * y for x, y in zip(xs, ys))
    sxx = sum(x * x for x in xs)
    denom = n * sxx - sx * sx
    if denom == 0:
        return 0.0, sy / n
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    return slope, intercept


async def forecast_budget_exhaustion(
    metric_name: str,
    service_id: UUID | None,
    target_percent: float,
    db: AsyncSession,
) -> dict:
    """Returns {budget_exhaustion_date: datetime | None, confidence: float, slope: float}."""
    now = utc_now()
    since = now - timedelta(days=7)

    q = (
        select(MetricSample)
        .where(MetricSample.name == metric_name, MetricSample.sampled_at >= since)
        .order_by(MetricSample.sampled_at.asc())
    )
    if service_id is not None:
        q = q.where(MetricSample.service_id == service_id)

    result = await db.execute(q)
    samples = list(result.scalars().all())

    if not samples:
        return {"budget_exhaustion_date": None, "confidence": 0.0, "slope": 0.0}

    # Group into daily buckets
    day_buckets: dict[int, list[float]] = {}
    start_day = since.date()
    for s in samples:
        day_idx = (s.sampled_at.date() - start_day).days
        day_buckets.setdefault(day_idx, []).append(s.value)

    # Compute daily good_rate (good = value >= good threshold; here we treat value as rate 0..1)
    error_budget_threshold = 1.0 - (target_percent / 100.0)
    days_list = sorted(day_buckets.keys())
    xs = [float(d) for d in days_list]
    ys = [sum(day_buckets[d]) / len(day_buckets[d]) for d in days_list]

    if len(xs) < 2:
        return {"budget_exhaustion_date": None, "confidence": 0.0, "slope": 0.0}

    slope, intercept = linear_regression(xs, ys)

    # Project forward to find day when good_rate < error_budget_threshold
    exhaustion_date = None
    if slope < 0:
        # good_rate = slope * x + intercept < error_budget_threshold
        # x > (error_budget_threshold - intercept) / slope  (slope < 0 flips inequality)
        x_exhaustion = (error_budget_threshold - intercept) / slope
        if x_exhaustion > days_list[-1]:
            exhaustion_date = now + timedelta(days=x_exhaustion - days_list[-1])

    # Confidence: R² between 0 and 1
    y_mean = sum(ys) / len(ys)
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    if ss_tot == 0:
        confidence = 1.0
    else:
        y_pred = [slope * x + intercept for x in xs]
        ss_res = sum((y - yp) ** 2 for y, yp in zip(ys, y_pred))
        confidence = max(0.0, 1.0 - ss_res / ss_tot)

    return {
        "budget_exhaustion_date": exhaustion_date,
        "confidence": round(confidence, 4),
        "slope": round(slope, 6),
    }
