from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.synthetic_journey import SyntheticJourney
from app.repositories.base_repo import BaseRepository


class SyntheticJourneyRepository(BaseRepository[SyntheticJourney]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SyntheticJourney)

    async def list_active(self) -> list[SyntheticJourney]:
        result = await self.db.execute(
            select(SyntheticJourney).where(SyntheticJourney.is_active.is_(True))
        )
        return list(result.scalars().all())
