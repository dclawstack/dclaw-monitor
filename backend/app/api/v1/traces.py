import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.trace_span import TraceSpan
from app.repositories.trace_repo import TraceRepository

router = APIRouter(tags=["traces"])


class SpanIngest(BaseModel):
    """OTLP-compatible span input."""
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    service_id: uuid.UUID | None = None
    operation_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float | None = None
    status: str = "ok"
    attributes: dict | None = None


class SpanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trace_id: str
    span_id: str
    parent_span_id: str | None
    service_id: uuid.UUID | None
    operation_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    status: str
    attributes: dict | None


class RecentTrace(BaseModel):
    trace_id: str
    span_count: int
    root_operation: str
    started_at: datetime


@router.post("/ingest")
async def ingest_spans(
    spans: list[SpanIngest],
    db: AsyncSession = Depends(get_db),
):
    repo = TraceRepository(db)
    span_objects = []
    for s in spans:
        duration = s.duration_ms
        if duration is None:
            delta = s.end_time - s.start_time
            duration = delta.total_seconds() * 1000

        span_objects.append(
            TraceSpan(
                trace_id=s.trace_id,
                span_id=s.span_id,
                parent_span_id=s.parent_span_id,
                service_id=s.service_id,
                operation_name=s.operation_name,
                start_time=s.start_time,
                end_time=s.end_time,
                duration_ms=duration,
                status=s.status,
                attributes=s.attributes,
            )
        )

    saved = await repo.ingest_batch(span_objects)
    return {"ingested": len(saved)}


@router.get("/recent", response_model=list[RecentTrace])
async def list_recent_traces(
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = TraceRepository(db)
    rows = await repo.list_recent_traces(limit=limit)
    return [RecentTrace(**r) for r in rows]


@router.get("/", response_model=list[SpanRead])
async def list_spans(
    trace_id: str = Query(..., description="Trace ID to fetch spans for"),
    db: AsyncSession = Depends(get_db),
):
    repo = TraceRepository(db)
    spans = await repo.list_by_trace_id(trace_id)
    return spans
