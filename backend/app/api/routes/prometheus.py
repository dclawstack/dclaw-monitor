"""Prometheus metrics export endpoint."""
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.metric import MetricSample
from app.models.service import MonitoredService

router = APIRouter(tags=["prometheus"])


@router.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics(db: AsyncSession = Depends(get_db)) -> str:
    """Export latest metric sample per (service_id, metric_name) in Prometheus format."""
    # Get the latest sampled_at per (service_id, name)
    subq = (
        select(
            MetricSample.service_id,
            MetricSample.name,
            func.max(MetricSample.sampled_at).label("max_sampled_at"),
        )
        .group_by(MetricSample.service_id, MetricSample.name)
        .subquery()
    )

    q = select(MetricSample, MonitoredService.name.label("service_name")).join(
        subq,
        (MetricSample.service_id == subq.c.service_id)
        & (MetricSample.name == subq.c.name)
        & (MetricSample.sampled_at == subq.c.max_sampled_at),
    ).outerjoin(
        MonitoredService, MetricSample.service_id == MonitoredService.id
    )

    result = await db.execute(q)
    rows = result.all()

    lines = []
    for row in rows:
        sample: MetricSample = row[0]
        service_name: str | None = row[1]

        # Sanitize metric name (replace non-alphanumeric chars with _)
        metric_name = sample.name.replace("-", "_").replace(".", "_").replace("/", "_")
        label = f'service="{service_name or "unknown"}"'

        # Convert datetime to milliseconds timestamp for Prometheus
        timestamp_ms = int(sample.sampled_at.timestamp() * 1000)

        lines.append(f"{metric_name}{{{label}}} {sample.value} {timestamp_ms}")

    return "\n".join(lines) + ("\n" if lines else "")
