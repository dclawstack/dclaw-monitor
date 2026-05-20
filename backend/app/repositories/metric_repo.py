from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

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
