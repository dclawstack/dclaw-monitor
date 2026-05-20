import asyncio
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.incident import Incident
from app.repositories.incident_repo import IncidentRepository
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentRead, IncidentList
from app.services import rca_engine

router = APIRouter(tags=["incidents"])


@router.get("", response_model=IncidentList)
async def list_incidents(
    status: str | None = None,
    service_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    repo = IncidentRepository(db)
    if service_id is not None:
        items, total = await repo.list_by_service(service_id, limit=limit, offset=offset)
    elif status is not None:
        items, total = await repo.list_by_status(status, limit=limit, offset=offset)
    else:
        items, total = await repo.list_all(limit=limit, offset=offset)
    return IncidentList(items=items, total=total)


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
async def create_incident(body: IncidentCreate, db: AsyncSession = Depends(get_db)):
    incident = Incident(
        title=body.title,
        severity=body.severity,
        service_id=body.service_id,
        alert_ids=body.alert_ids,
    )
    repo = IncidentRepository(db)
    incident = await repo.create(incident)
    asyncio.create_task(rca_engine.analyze_incident(incident.id))
    return incident


@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = IncidentRepository(db)
    incident = await repo.get_by_id(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentRead)
async def update_incident(
    incident_id: uuid.UUID,
    body: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = IncidentRepository(db)
    incident = await repo.get_by_id(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)
    await db.commit()
    await db.refresh(incident)
    return incident


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = IncidentRepository(db)
    incident = await repo.get_by_id(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    await repo.delete(incident)


@router.post("/{incident_id}/resolve", response_model=IncidentRead)
async def resolve_incident(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = IncidentRepository(db)
    incident = await repo.update_status(incident_id, "resolved")
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
