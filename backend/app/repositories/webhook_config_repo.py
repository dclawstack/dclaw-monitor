from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.webhook_config import WebhookConfig
from app.repositories.base_repo import BaseRepository


class WebhookConfigRepository(BaseRepository[WebhookConfig]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, WebhookConfig)

    async def list_active(self) -> list[WebhookConfig]:
        result = await self.db.execute(
            select(WebhookConfig).where(WebhookConfig.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def list_by_event_type(self, event_type: str) -> list[WebhookConfig]:
        """Return active webhooks whose event_types array contains event_type."""
        # Fetch all active and filter in Python (JSON array containment)
        active = await self.list_active()
        return [
            wh for wh in active
            if wh.event_types and event_type in wh.event_types
        ]
