import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.synthetic_journey import SyntheticJourney
from app.repositories.synthetic_repo import SyntheticJourneyRepository
from app.services import synthetic_runner

router = APIRouter(tags=["synthetic"])


class JourneyCreate(BaseModel):
    name: str
    service_id: uuid.UUID | None = None
    steps: list[dict] | None = None
    interval_seconds: int = 60
    is_active: bool = True


class JourneyUpdate(BaseModel):
    name: str | None = None
    service_id: uuid.UUID | None = None
    steps: list[dict] | None = None
    interval_seconds: int | None = None
    is_active: bool | None = None


class JourneyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    service_id: uuid.UUID | None
    steps: list | None
    interval_seconds: int
    is_active: bool
    created_at: datetime


class JourneyList(BaseModel):
    items: list[JourneyRead]
    total: int


@router.get("", response_model=JourneyList)
async def list_journeys(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    repo = SyntheticJourneyRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return JourneyList(items=items, total=total)


@router.post("", response_model=JourneyRead, status_code=status.HTTP_201_CREATED)
async def create_journey(body: JourneyCreate, db: AsyncSession = Depends(get_db)):
    journey = SyntheticJourney(
        name=body.name,
        service_id=body.service_id,
        steps=body.steps,
        interval_seconds=body.interval_seconds,
        is_active=body.is_active,
    )
    repo = SyntheticJourneyRepository(db)
    return await repo.create(journey)


@router.get("/{journey_id}", response_model=JourneyRead)
async def get_journey(journey_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SyntheticJourneyRepository(db)
    journey = await repo.get_by_id(journey_id)
    if journey is None:
        raise HTTPException(status_code=404, detail="Journey not found")
    return journey


@router.patch("/{journey_id}", response_model=JourneyRead)
async def update_journey(
    journey_id: uuid.UUID,
    body: JourneyUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = SyntheticJourneyRepository(db)
    journey = await repo.get_by_id(journey_id)
    if journey is None:
        raise HTTPException(status_code=404, detail="Journey not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(journey, field, value)
    await db.commit()
    await db.refresh(journey)
    return journey


@router.delete("/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journey(journey_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SyntheticJourneyRepository(db)
    journey = await repo.get_by_id(journey_id)
    if journey is None:
        raise HTTPException(status_code=404, detail="Journey not found")
    await repo.delete(journey)


@router.post("/{journey_id}/run")
async def run_journey(journey_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SyntheticJourneyRepository(db)
    journey = await repo.get_by_id(journey_id)
    if journey is None:
        raise HTTPException(status_code=404, detail="Journey not found")
    checks = await synthetic_runner.run_journey(journey, db)
    return {
        "journey_id": str(journey_id),
        "checks_run": len(checks),
        "results": [
            {
                "status": c.status,
                "latency_ms": c.latency_ms,
                "status_code": c.status_code,
                "error": c.error,
            }
            for c in checks
        ],
    }
