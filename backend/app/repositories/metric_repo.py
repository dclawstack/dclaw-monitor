from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.models.metric import MetricSample
from app.repositories.base_repo import BaseRepository


class MetricRepository(BaseRepository[MetricSample]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, MetricSample)

    async def list_by_name(
        self,
        name: str,
        service_id: UUID | None = None,
        since: datetime | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> tuple[list[MetricSample], int]:
        q = select(MetricSample).where(MetricSample.name == name)
        if service_id is not None:
            q = q.where(MetricSample.service_id == service_id)
        if since is not None:
            q = q.where(MetricSample.sampled_at >= since)
        result = await self.db.execute(
            q.order_by(MetricSample.sampled_at.desc()).limit(limit).offset(offset)
        )
        items = list(result.scalars().all())

        cq = select(func.count()).select_from(MetricSample).where(MetricSample.name == name)
        if service_id is not None:
            cq = cq.where(MetricSample.service_id == service_id)
        if since is not None:
            cq = cq.where(MetricSample.sampled_at >= since)
        count = await self.db.execute(cq)
        return items, count.scalar() or 0

    async def aggregate_by_window(
        self,
        name: str,
        service_id: UUID | None = None,
        from_ts: datetime | None = None,
        to_ts: datetime | None = None,
        window_seconds: int = 300,
    ) -> list[dict]:
        """Aggregate metric samples into time buckets using epoch-based bucketing."""
        # Build filter conditions
        conditions = [f"name = :name"]
        params: dict = {"name": name, "window": window_seconds}

        if service_id is not None:
            conditions.append("service_id = :service_id")
            params["service_id"] = str(service_id)
        if from_ts is not None:
            conditions.append("sampled_at >= :from_ts")
            params["from_ts"] = from_ts
        if to_ts is not None:
            conditions.append("sampled_at <= :to_ts")
            params["to_ts"] = to_ts

        where_clause = " AND ".join(conditions)

        sql = text(f"""
            SELECT
                to_timestamp(
                    floor(extract(epoch FROM sampled_at) / :window) * :window
                ) AS bucket,
                avg(value) AS avg,
                min(value) AS min,
                max(value) AS max,
                count(*) AS count
            FROM metric_samples
            WHERE {where_clause}
            GROUP BY bucket
            ORDER BY bucket ASC
        """)

        result = await self.db.execute(sql, params)
        rows = result.fetchall()
        return [
            {
                "bucket": row.bucket,
                "avg": float(row.avg),
                "min": float(row.min),
                "max": float(row.max),
                "count": int(row.count),
            }
            for row in rows
        ]
