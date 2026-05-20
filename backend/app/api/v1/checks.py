import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.check import UptimeCheck
from app.repositories.check_repo import CheckRepository
from app.repositories.service_repo import ServiceRepository
from app.schemas.check import CheckCreate, CheckRead, CheckList

router = APIRouter(tags=["checks"])


@router.post("/", response_model=CheckRead, status_code=status.HTTP_201_CREATED)
async def record_check(body: CheckCreate, db: AsyncSession = Depends(get_db)):
    svc_repo = ServiceRepository(db)
    service = await svc_repo.get_by_id(body.service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    check = UptimeCheck(
        service_id=body.service_id,
        status=body.status,
        latency_ms=body.latency_ms,
        status_code=body.status_code,
        error=body.error,
    )
    repo = CheckRepository(db)
    saved = await repo.create(check)

    # up → healthy, hard failures → down, transient failures → degraded
    if body.status == "up":
        new_status = "healthy"
    elif body.status in ("down", "error"):
        new_status = "down"
    else:  # timeout
        new_status = "degraded"
    await svc_repo.update_status(body.service_id, new_status)

    return saved


@router.get("/service/{service_id}", response_model=CheckList)
async def list_checks_for_service(
    service_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    svc_repo = ServiceRepository(db)
    if await svc_repo.get_by_id(service_id) is None:
        raise HTTPException(status_code=404, detail="Service not found")

    repo = CheckRepository(db)
    items, total = await repo.list_by_service(service_id, limit=limit, offset=offset)
    return CheckList(items=items, total=total)
