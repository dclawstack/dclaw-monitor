import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.slo import SLO
from app.repositories.slo_repo import SLORepository
from app.schemas.slo import SLOCreate, SLORead, SLOStatus, SLOList

router = APIRouter(tags=["slos"])


@router.get("/", response_model=SLOList)
async def list_slos(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    repo = SLORepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return SLOList(items=items, total=total)


@router.post("/", response_model=SLORead, status_code=status.HTTP_201_CREATED)
async def create_slo(body: SLOCreate, db: AsyncSession = Depends(get_db)):
    repo = SLORepository(db)
    slo = SLO(
        service_id=body.service_id,
        name=body.name,
        target_percent=body.target_percent,
        window_days=body.window_days,
        metric_name=body.metric_name,
        good_condition=body.good_condition,
        good_threshold=body.good_threshold,
    )
    return await repo.create(slo)


@router.get("/{slo_id}", response_model=SLORead)
async def get_slo(slo_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SLORepository(db)
    slo = await repo.get_by_id(slo_id)
    if slo is None:
        raise HTTPException(status_code=404, detail="SLO not found")
    return slo


@router.patch("/{slo_id}", response_model=SLORead)
async def update_slo(
    slo_id: uuid.UUID,
    body: SLOCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = SLORepository(db)
    slo = await repo.get_by_id(slo_id)
    if slo is None:
        raise HTTPException(status_code=404, detail="SLO not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(slo, field, value)
    await db.commit()
    await db.refresh(slo)
    return slo


@router.delete("/{slo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slo(slo_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SLORepository(db)
    slo = await repo.get_by_id(slo_id)
    if slo is None:
        raise HTTPException(status_code=404, detail="SLO not found")
    await repo.delete(slo)


@router.get("/{slo_id}/status", response_model=SLOStatus)
async def get_slo_status(slo_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SLORepository(db)
    result = await repo.compute_status(slo_id)
    if result is None:
        raise HTTPException(status_code=404, detail="SLO not found")
    return SLOStatus(**result)
