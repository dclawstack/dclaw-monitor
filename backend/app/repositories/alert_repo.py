from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.alert import AlertRule, Alert
from app.repositories.base_repo import BaseRepository
from app.core.utils import utc_now


class AlertRuleRepository(BaseRepository[AlertRule]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AlertRule)

    async def list_active(self) -> list[AlertRule]:
        result = await self.db.execute(
            select(AlertRule).where(AlertRule.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def list_by_service(self, service_id: UUID) -> list[AlertRule]:
        result = await self.db.execute(
            select(AlertRule).where(AlertRule.service_id == service_id)
        )
        return list(result.scalars().all())


class AlertRepository(BaseRepository[Alert]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Alert)

    async def list_by_status(
        self, status: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[Alert], int]:
        result = await self.db.execute(
            select(Alert)
            .where(Alert.status == status)
            .order_by(Alert.fired_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = list(result.scalars().all())
        count = await self.db.execute(
            select(func.count()).select_from(Alert).where(Alert.status == status)
        )
        return items, count.scalar() or 0

    async def list_by_service(
        self, service_id: UUID, limit: int = 50, offset: int = 0
    ) -> tuple[list[Alert], int]:
        result = await self.db.execute(
            select(Alert)
            .where(Alert.service_id == service_id)
            .order_by(Alert.fired_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = list(result.scalars().all())
        count = await self.db.execute(
            select(func.count()).select_from(Alert).where(Alert.service_id == service_id)
        )
        return items, count.scalar() or 0

    async def update_status(self, alert_id: UUID, status: str) -> Alert | None:
        alert = await self.get_by_id(alert_id)
        if alert is None:
            return None
        alert.status = status
        if status == "resolved":
            alert.resolved_at = utc_now()
        await self.db.commit()
        await self.db.refresh(alert)
        return alert
