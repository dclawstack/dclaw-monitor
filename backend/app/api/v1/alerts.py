import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.alert import Alert
from app.repositories.alert_repo import AlertRepository
from app.schemas.alert import AlertCreate, AlertStatusUpdate, AlertRead, AlertList

router = APIRouter(tags=["alerts"])


@router.get("/", response_model=AlertList)
async def list_alerts(
    filter_status: str | None = Query(default=None, alias="status"),
    service_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    repo = AlertRepository(db)
    if service_id is not None:
        items, total = await repo.list_by_service(service_id, limit=limit, offset=offset)
    elif filter_status == "open":
        items, total = await repo.list_open(limit=limit, offset=offset)
    else:
        items, total = await repo.list_all(limit=limit, offset=offset)
    return AlertList(items=items, total=total)


@router.post("/", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
async def create_alert(body: AlertCreate, db: AsyncSession = Depends(get_db)):
    alert = Alert(
        rule_id=body.rule_id,
        service_id=body.service_id,
        title=body.title,
        message=body.message,
        severity=body.severity,
    )
    repo = AlertRepository(db)
    return await repo.create(alert)


@router.get("/{alert_id}", response_model=AlertRead)
async def get_alert(alert_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = AlertRepository(db)
    alert = await repo.get_by_id(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/{alert_id}/status", response_model=AlertRead)
async def update_alert_status(
    alert_id: uuid.UUID,
    body: AlertStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = AlertRepository(db)
    alert = await repo.update_status(alert_id, body.status)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
