import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

CheckStatus = Literal["up", "down", "timeout", "error"]


class CheckCreate(BaseModel):
    service_id: uuid.UUID
    status: CheckStatus
    latency_ms: int | None = None
    status_code: int | None = None
    error: str | None = None


class CheckRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_id: uuid.UUID
    status: str
    latency_ms: int | None
    status_code: int | None
    error: str | None
    checked_at: datetime


class CheckList(BaseModel):
    items: list[CheckRead]
    total: int
