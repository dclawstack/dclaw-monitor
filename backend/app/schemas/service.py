import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator

ServiceStatus = Literal["healthy", "degraded", "down", "unknown"]


class ServiceCreate(BaseModel):
    name: str
    url: str
    description: str | None = None
    interval_seconds: int = 60

    @field_validator("interval_seconds")
    @classmethod
    def validate_interval(cls, v: int) -> int:
        if v < 10:
            raise ValueError("interval_seconds must be >= 10")
        return v


class ServiceUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    description: str | None = None
    status: ServiceStatus | None = None
    interval_seconds: int | None = None
    is_active: bool | None = None


class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    url: str
    description: str | None
    status: str
    interval_seconds: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ServiceList(BaseModel):
    items: list[ServiceRead]
    total: int
