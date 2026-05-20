from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.incident import Incident
from app.repositories.base_repo import BaseRepository
from app.core.utils import utc_now


class IncidentRepository(BaseRepository[Incident]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Incident)

    async def list_by_status(
        self, status: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[Incident], int]:
        result = await self.db.execute(
            select(Incident)
            .where(Incident.status == status)
            .order_by(Incident.opened_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = list(result.scalars().all())
        count = await self.db.execute(
            select(func.count()).select_from(Incident).where(Incident.status == status)
        )
        return items, count.scalar() or 0

    async def list_by_service(
        self, service_id: UUID, limit: int = 50, offset: int = 0
    ) -> tuple[list[Incident], int]:
        result = await self.db.execute(
            select(Incident)
            .where(Incident.service_id == service_id)
            .order_by(Incident.opened_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = list(result.scalars().all())
        count = await self.db.execute(
            select(func.count()).select_from(Incident).where(Incident.service_id == service_id)
        )
        return items, count.scalar() or 0

    async def list_resolved_by_service(
        self, service_id: UUID, limit: int = 5
    ) -> list[Incident]:
        result = await self.db.execute(
            select(Incident)
            .where(Incident.service_id == service_id, Incident.status == "resolved")
            .order_by(Incident.resolved_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_open_recent(self, since: datetime) -> list[Incident]:
        result = await self.db.execute(
            select(Incident)
            .where(Incident.status == "open", Incident.opened_at >= since)
            .order_by(Incident.opened_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(self, incident_id: UUID, status: str) -> Incident | None:
        incident = await self.get_by_id(incident_id)
        if incident is None:
            return None
        incident.status = status
        if status == "resolved" and incident.resolved_at is None:
            now = utc_now()
            incident.resolved_at = now
            incident.mttr_seconds = int((now - incident.opened_at).total_seconds())
        await self.db.commit()
        await self.db.refresh(incident)
        return incident
