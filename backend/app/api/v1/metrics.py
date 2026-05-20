import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.metric import MetricSample
from app.repositories.metric_repo import MetricRepository
from app.schemas.metric import MetricIngest, MetricRead, MetricList

router = APIRouter(tags=["metrics"])


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
