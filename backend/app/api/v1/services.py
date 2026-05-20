import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.service import MonitoredService
from app.repositories.service_repo import ServiceRepository
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceRead, ServiceList
from app.services import runbook_generator

router = APIRouter(tags=["services"])


@router.get("", response_model=ServiceList)
async def list_services(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    repo = ServiceRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return ServiceList(items=items, total=total)


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(body: ServiceCreate, db: AsyncSession = Depends(get_db)):
    repo = ServiceRepository(db)
    if await repo.get_by_name(body.name):
        raise HTTPException(status_code=409, detail="Service name already exists")
    service = MonitoredService(
        name=body.name,
        url=body.url,
        description=body.description,
        interval_seconds=body.interval_seconds,
    )
    return await repo.create(service)


@router.get("/{service_id}/runbook")
async def get_runbook(service_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    repo = ServiceRepository(db)
    service = await repo.get_by_id(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    runbook = await runbook_generator.generate_runbook(service_id, db)
    return {"service_id": str(service_id), "runbook": runbook}


@router.get("/{service_id}", response_model=ServiceRead)
async def get_service(service_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = ServiceRepository(db)
    service = await repo.get_by_id(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.patch("/{service_id}", response_model=ServiceRead)
async def update_service(
    service_id: uuid.UUID,
    body: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = ServiceRepository(db)
    service = await repo.get_by_id(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    await db.commit()
    await db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(service_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = ServiceRepository(db)
    service = await repo.get_by_id(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    await repo.delete(service)
