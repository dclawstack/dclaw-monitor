import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class IncidentCreate(BaseModel):
    title: str
    severity: str = "warning"


class IncidentUpdate(BaseModel):
    status: str | None = None
    title: str | None = None
    rca_summary: str | None = None
    alert_ids: list | None = None


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    severity: str
    status: str
    opened_at: datetime
    resolved_at: datetime | None
    mttr_seconds: int | None
    alert_ids: list | None
    rca_summary: str | None


class IncidentList(BaseModel):
    items: list[IncidentRead]
    total: int
