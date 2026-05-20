import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.alert import AlertRule
from app.repositories.alert_repo import AlertRuleRepository
from app.schemas.alert import AlertRuleCreate, AlertRuleUpdate, AlertRuleRead, AlertRuleList

router = APIRouter(tags=["alert-rules"])


@router.get("", response_model=AlertRuleList)
async def list_alert_rules(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    repo = AlertRuleRepository(db)
    items, total = await repo.list_all(limit=limit, offset=offset)
    return AlertRuleList(items=items, total=total)


@router.post("", response_model=AlertRuleRead, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(body: AlertRuleCreate, db: AsyncSession = Depends(get_db)):
    rule = AlertRule(
        name=body.name,
        service_id=body.service_id,
        metric_name=body.metric_name,
        operator=body.operator,
        threshold=body.threshold,
        severity=body.severity,
    )
    repo = AlertRuleRepository(db)
    return await repo.create(rule)


@router.get("/{rule_id}", response_model=AlertRuleRead)
async def get_alert_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = AlertRuleRepository(db)
    rule = await repo.get_by_id(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return rule


@router.patch("/{rule_id}", response_model=AlertRuleRead)
async def update_alert_rule(
    rule_id: uuid.UUID,
    body: AlertRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = AlertRuleRepository(db)
    rule = await repo.get_by_id(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = AlertRuleRepository(db)
    rule = await repo.get_by_id(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    await repo.delete(rule)
