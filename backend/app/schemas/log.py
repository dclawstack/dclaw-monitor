import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

LogLevel = Literal["debug", "info", "warning", "error", "critical"]


class LogIngest(BaseModel):
    service_id: uuid.UUID | None = None
    level: LogLevel = "info"
    message: str
    source: str | None = None
    metadata_: dict | None = None


class LogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_id: uuid.UUID | None
    level: str
    message: str
    source: str | None
    metadata_: dict | None
    logged_at: datetime


class LogList(BaseModel):
    items: list[LogRead]
    total: int
