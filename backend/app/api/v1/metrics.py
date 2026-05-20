import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.utils import utc_now
from app.models.metric import MetricSample
from app.repositories.metric_repo import MetricRepository
from app.schemas.metric import MetricIngest, MetricRead, MetricList
from app.services.anomaly_detector import check_anomaly
from app.services.slo_forecaster import linear_regression

router = APIRouter(tags=["metrics"])


def _parse_window(window: str) -> int:
    """Parse window string like '1m', '5m', '1h' into seconds."""
    window = window.strip().lower()
    if window.endswith("h"):
        return int(window[:-1]) * 3600
    elif window.endswith("m"):
        return int(window[:-1]) * 60
    elif window.endswith("s"):
        return int(window[:-1])
    return int(window)


@router.post("/", response_model=MetricRead, status_code=status.HTTP_201_CREATED)
async def ingest_metric(body: MetricIngest, db: AsyncSession = Depends(get_db)):
    sample = MetricSample(
        service_id=body.service_id,
        name=body.name,
        value=body.value,
        labels=body.labels,
    )
    repo = MetricRepository(db)
    sample = await repo.create(sample)

    # Non-blocking anomaly detection
    asyncio.create_task(check_anomaly(body.service_id, body.name, body.value))

    return sample


@router.get("/forecast")
async def forecast_metric(
    name: str = Query(..., description="Metric name to forecast"),
    service_id: uuid.UUID | None = None,
    breach_threshold: float | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Project metric values 30/60/90 days forward using linear regression."""
    now = utc_now()
    since = now - timedelta(days=30)

    q = (
        select(MetricSample)
        .where(MetricSample.name == name, MetricSample.sampled_at >= since)
        .order_by(MetricSample.sampled_at.asc())
    )
    if service_id is not None:
        q = q.where(MetricSample.service_id == service_id)

    result = await db.execute(q)
    samples = list(result.scalars().all())

    if not samples:
        return {
            "p30": None,
            "p60": None,
            "p90": None,
            "trend_slope": 0.0,
            "breach_day": None,
            "breach_threshold": breach_threshold,
        }

    # Build daily averages
    start_date = samples[0].sampled_at.date()
    day_buckets: dict[int, list[float]] = {}
    for s in samples:
        day_idx = (s.sampled_at.date() - start_date).days
        day_buckets.setdefault(day_idx, []).append(s.value)

    days_list = sorted(day_buckets.keys())
    xs = [float(d) for d in days_list]
    ys = [sum(day_buckets[d]) / len(day_buckets[d]) for d in days_list]

    slope, intercept = linear_regression(xs, ys)

    # Current "day index" from start
    current_day = (now.date() - start_date).days

    def predict(days_ahead: int) -> float:
        return slope * (current_day + days_ahead) + intercept

    p30 = predict(30)
    p60 = predict(60)
    p90 = predict(90)

    # Compute breach_day if threshold provided
    breach_day = None
    if breach_threshold is not None and slope != 0:
        # predict(d) == breach_threshold  =>  slope * (current_day + d) + intercept = threshold
        # d = (threshold - intercept) / slope - current_day
        raw_d = (breach_threshold - intercept) / slope - current_day
        if raw_d > 0:
            breach_day = int(raw_d)

    return {
        "p30": round(p30, 4),
        "p60": round(p60, 4),
        "p90": round(p90, 4),
        "trend_slope": round(slope, 6),
        "breach_day": breach_day,
        "breach_threshold": breach_threshold,
    }


@router.get("/", response_model=MetricList)
async def query_metrics(
    name: str = Query(..., description="Metric name to query"),
    service_id: uuid.UUID | None = None,
    since: datetime | None = None,
    limit: int = 200,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    repo = MetricRepository(db)
    items, total = await repo.list_by_name(
        name=name,
        service_id=service_id,
        since=since,
        limit=limit,
        offset=offset,
    )
    return MetricList(items=items, total=total)


@router.get("/aggregate", response_model=list[dict[str, Any]])
async def aggregate_metrics(
    name: str = Query(..., description="Metric name to aggregate"),
    service_id: uuid.UUID | None = None,
    from_ts: datetime | None = Query(None, alias="from"),
    to_ts: datetime | None = Query(None, alias="to"),
    window: str = Query("5m", description="Bucket size: 1m, 5m, 1h, etc."),
    db: AsyncSession = Depends(get_db),
):
    window_seconds = _parse_window(window)
    repo = MetricRepository(db)
    buckets = await repo.aggregate_by_window(
        name=name,
        service_id=service_id,
        from_ts=from_ts,
        to_ts=to_ts,
        window_seconds=window_seconds,
    )
    return buckets
