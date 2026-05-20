from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct

from app.models.trace_span import TraceSpan
from app.repositories.base_repo import BaseRepository


class TraceRepository(BaseRepository[TraceSpan]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, TraceSpan)

    async def ingest_batch(self, spans: list[TraceSpan]) -> list[TraceSpan]:
        for span in spans:
            self.db.add(span)
        await self.db.commit()
        for span in spans:
            await self.db.refresh(span)
        return spans

    async def list_by_trace_id(self, trace_id: str) -> list[TraceSpan]:
        result = await self.db.execute(
            select(TraceSpan)
            .where(TraceSpan.trace_id == trace_id)
            .order_by(TraceSpan.start_time.asc())
        )
        return list(result.scalars().all())

    async def list_recent_traces(self, limit: int = 20) -> list[dict]:
        """Return list of distinct recent trace_ids with span count and root op name."""
        # Get distinct trace_ids with aggregate info
        subq = (
            select(
                TraceSpan.trace_id,
                func.count(TraceSpan.id).label("span_count"),
                func.min(TraceSpan.start_time).label("earliest_start"),
            )
            .group_by(TraceSpan.trace_id)
            .order_by(func.min(TraceSpan.start_time).desc())
            .limit(limit)
            .subquery()
        )
        result = await self.db.execute(
            select(subq.c.trace_id, subq.c.span_count, subq.c.earliest_start)
        )
        rows = result.all()

        output = []
        for row in rows:
            # Fetch root span (no parent) for the operation name
            root_result = await self.db.execute(
                select(TraceSpan.operation_name)
                .where(
                    TraceSpan.trace_id == row.trace_id,
                    TraceSpan.parent_span_id.is_(None),
                )
                .limit(1)
            )
            root_op = root_result.scalar_one_or_none() or ""
            output.append(
                {
                    "trace_id": row.trace_id,
                    "span_count": row.span_count,
                    "root_operation": root_op,
                    "started_at": row.earliest_start,
                }
            )
        return output
