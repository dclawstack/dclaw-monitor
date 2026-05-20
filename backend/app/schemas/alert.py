import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

AlertSeverity = Literal["info", "warning", "critical"]
AlertStatus = Literal["open", "acknowledged", "resolved"]
AlertOperator = Literal["gt", "lt", "eq", "gte", "lte"]


class AlertRuleCreate(BaseModel):
    name: str
    service_id: uuid.UUID | None = None
    metric_name: str
    operator: AlertOperator
    threshold: float
    severity: AlertSeverity = "warning"


class AlertRuleUpdate(BaseModel):
    name: str | None = None
    metric_name: str | None = None
    operator: AlertOperator | None = None
    threshold: float | None = None
    severity: AlertSeverity | None = None
    is_active: bool | None = None


class AlertRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    service_id: uuid.UUID | None
    metric_name: str
    operator: str
    threshold: float
    severity: str
    is_active: bool
    created_at: datetime


class AlertRuleList(BaseModel):
    items: list[AlertRuleRead]
    total: int


class AlertCreate(BaseModel):
    rule_id: uuid.UUID | None = None
    service_id: uuid.UUID | None = None
    title: str
    message: str
    severity: AlertSeverity = "warning"


class AlertStatusUpdate(BaseModel):
    status: AlertStatus


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rule_id: uuid.UUID | None
    service_id: uuid.UUID | None
    title: str
    message: str
    severity: str
    status: str
    fired_at: datetime
    resolved_at: datetime | None


class AlertList(BaseModel):
    items: list[AlertRead]
    total: int
