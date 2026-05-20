from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.service import MonitoredService
from app.repositories.base_repo import BaseRepository


class ServiceRepository(BaseRepository[MonitoredService]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, MonitoredService)

    async def get_by_name(self, name: str) -> MonitoredService | None:
        result = await self.db.execute(
            select(MonitoredService).where(MonitoredService.name == name)
        )
        return result.scalar_one_or_none()

    async def list_active(self, limit: int = 100, offset: int = 0) -> list[MonitoredService]:
        result = await self.db.execute(
            select(MonitoredService)
            .where(MonitoredService.is_active.is_(True))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update_status(self, service_id: UUID, status: str) -> MonitoredService | None:
        service = await self.get_by_id(service_id)
        if service is None:
            return None
        service.status = status
        await self.db.commit()
        await self.db.refresh(service)
        return service
