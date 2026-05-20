from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.check import UptimeCheck
from app.repositories.base_repo import BaseRepository


class CheckRepository(BaseRepository[UptimeCheck]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, UptimeCheck)

    async def list_by_service(
        self, service_id: UUID, limit: int = 50, offset: int = 0
    ) -> tuple[list[UptimeCheck], int]:
        result = await self.db.execute(
            select(UptimeCheck)
            .where(UptimeCheck.service_id == service_id)
            .order_by(UptimeCheck.checked_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = list(result.scalars().all())
        count = await self.db.execute(
            select(func.count()).select_from(UptimeCheck).where(UptimeCheck.service_id == service_id)
        )
        return items, count.scalar() or 0

    async def latest_for_service(self, service_id: UUID) -> UptimeCheck | None:
        result = await self.db.execute(
            select(UptimeCheck)
            .where(UptimeCheck.service_id == service_id)
            .order_by(UptimeCheck.checked_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
