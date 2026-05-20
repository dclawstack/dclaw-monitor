import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SLOCreate(BaseModel):
    service_id: uuid.UUID | None = None
    name: str
    target_percent: float
    window_days: int = 30
    metric_name: str
    good_condition: str  # lt | gt
    good_threshold: float


class SLORead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_id: uuid.UUID | None
    name: str
    target_percent: float
    window_days: int
    metric_name: str
    good_condition: str
    good_threshold: float
    created_at: datetime


class SLOStatus(BaseModel):
    target_percent: float
    current_percent: float
    error_budget_remaining: float
    burn_rate: float
    total_samples: int
    good_samples: int


class SLOList(BaseModel):
    items: list[SLORead]
    total: int
