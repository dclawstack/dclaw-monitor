import uuid
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.metric import MetricSample
from app.repositories.metric_repo import MetricRepository
from app.schemas.metric import MetricIngest, MetricRead, MetricList

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
    return await repo.create(sample)


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
