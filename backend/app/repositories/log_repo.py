from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.log import LogEntry
from app.repositories.base_repo import BaseRepository


class LogRepository(BaseRepository[LogEntry]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, LogEntry)

    async def search(
        self,
        query: str | None = None,
        level: str | None = None,
        service_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[LogEntry], int]:
        q = select(LogEntry)
        if service_id is not None:
            q = q.where(LogEntry.service_id == service_id)
        if level is not None:
            q = q.where(LogEntry.level == level)
        if query:
            q = q.where(LogEntry.message.ilike(f"%{query}%"))

        result = await self.db.execute(
            q.order_by(LogEntry.logged_at.desc()).limit(limit).offset(offset)
        )
        items = list(result.scalars().all())

        cq = select(func.count()).select_from(LogEntry)
        if service_id is not None:
            cq = cq.where(LogEntry.service_id == service_id)
        if level is not None:
            cq = cq.where(LogEntry.level == level)
        if query:
            cq = cq.where(LogEntry.message.ilike(f"%{query}%"))
        count = await self.db.execute(cq)
        return items, count.scalar() or 0
