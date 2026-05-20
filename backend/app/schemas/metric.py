import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MetricIngest(BaseModel):
    service_id: uuid.UUID | None = None
    name: str
    value: float
    labels: dict | None = None


class MetricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_id: uuid.UUID | None
    name: str
    value: float
    labels: dict | None
    sampled_at: datetime


class MetricList(BaseModel):
    items: list[MetricRead]
    total: int
