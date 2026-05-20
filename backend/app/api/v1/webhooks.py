import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.webhook_config import WebhookConfig
from app.repositories.webhook_config_repo import WebhookConfigRepository
from app.schemas.webhook import WebhookCreate, WebhookRead, WebhookList

router = APIRouter(tags=["webhooks"])


@router.get("/", response_model=WebhookList)
async def list_webhooks(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    repo = WebhookConfigRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return WebhookList(items=items, total=total)


@router.post("/", response_model=WebhookRead, status_code=status.HTTP_201_CREATED)
async def create_webhook(body: WebhookCreate, db: AsyncSession = Depends(get_db)):
    repo = WebhookConfigRepository(db)
    webhook = WebhookConfig(
        name=body.name,
        url=body.url,
        secret=body.secret,
        event_types=body.event_types,
    )
    return await repo.create(webhook)


@router.get("/{webhook_id}", response_model=WebhookRead)
async def get_webhook(webhook_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = WebhookConfigRepository(db)
    webhook = await repo.get_by_id(webhook_id)
    if webhook is None:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook


@router.patch("/{webhook_id}", response_model=WebhookRead)
async def update_webhook(
    webhook_id: uuid.UUID,
    body: WebhookCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = WebhookConfigRepository(db)
    webhook = await repo.get_by_id(webhook_id)
    if webhook is None:
        raise HTTPException(status_code=404, detail="Webhook not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(webhook, field, value)
    await db.commit()
    await db.refresh(webhook)
    return webhook


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(webhook_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = WebhookConfigRepository(db)
    webhook = await repo.get_by_id(webhook_id)
    if webhook is None:
        raise HTTPException(status_code=404, detail="Webhook not found")
    await repo.delete(webhook)
