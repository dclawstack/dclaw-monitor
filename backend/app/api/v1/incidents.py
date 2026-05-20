import asyncio
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.utils import utc_now
from app.models.incident import Incident
from app.repositories.incident_repo import IncidentRepository
from app.services import rca_engine

router = APIRouter(tags=["incidents"])


class IncidentCreate(BaseModel):
    title: str
    severity: str = "warning"
    service_id: uuid.UUID | None = None
    alert_ids: list[str] | None = None


class IncidentStatusUpdate(BaseModel):
    status: str


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    status: str
    severity: str
    service_id: uuid.UUID | None
    alert_ids: list | None
    rca_summary: str | None
    created_at: datetime
    resolved_at: datetime | None


class IncidentList(BaseModel):
    items: list[IncidentRead]
    total: int


@router.get("/", response_model=IncidentList)
async def list_incidents(
    filter_status: str | None = None,
    service_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    repo = IncidentRepository(db)
    if service_id is not None:
        items, total = await repo.list_by_service(service_id, limit=limit, offset=offset)
    elif filter_status is not None:
        items, total = await repo.list_by_status(filter_status, limit=limit, offset=offset)
    else:
        items, total = await repo.list_all(limit=limit, offset=offset)
    return IncidentList(items=items, total=total)


@router.post("/", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
async def create_incident(body: IncidentCreate, db: AsyncSession = Depends(get_db)):
    incident = Incident(
        title=body.title,
        severity=body.severity,
        service_id=body.service_id,
        alert_ids=body.alert_ids,
    )
    repo = IncidentRepository(db)
    incident = await repo.create(incident)

    # Trigger RCA asynchronously (non-blocking)
    asyncio.create_task(rca_engine.analyze_incident(incident.id, db))

    return incident


@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = IncidentRepository(db)
    incident = await repo.get_by_id(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}/status", response_model=IncidentRead)
async def update_incident_status(
    incident_id: uuid.UUID,
    body: IncidentStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = IncidentRepository(db)
    incident = await repo.get_by_id(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = body.status
    if body.status == "resolved":
        incident.resolved_at = utc_now()
    await db.commit()
    await db.refresh(incident)
    return incident
