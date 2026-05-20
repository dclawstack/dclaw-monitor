import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.log import LogEntry
from app.repositories.log_repo import LogRepository
from app.schemas.log import LogIngest, LogRead, LogList

router = APIRouter(tags=["logs"])


@router.post("", response_model=LogRead, status_code=status.HTTP_201_CREATED)
async def ingest_log(body: LogIngest, db: AsyncSession = Depends(get_db)):
    entry = LogEntry(
        service_id=body.service_id,
        level=body.level,
        message=body.message,
        source=body.source,
        attributes=body.attributes,
    )
    repo = LogRepository(db)
    return await repo.create(entry)


@router.get("", response_model=LogList)
async def query_logs(
    q: str | None = Query(default=None, description="Full-text search in message"),
    level: str | None = None,
    service_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    repo = LogRepository(db)
    items, total = await repo.search(
        query=q,
        level=level,
        service_id=service_id,
        limit=limit,
        offset=offset,
    )
    return LogList(items=items, total=total)
