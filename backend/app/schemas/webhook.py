import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator


class WebhookCreate(BaseModel):
    name: str
    url: str
    secret: str | None = None
    event_types: list | None = None


class WebhookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    url: str
    secret: str | None = None
    is_active: bool
    event_types: list | None
    created_at: datetime

    @model_validator(mode="after")
    def mask_secret(self) -> "WebhookRead":
        if self.secret:
            self.secret = "***"
        return self


class WebhookList(BaseModel):
    items: list[WebhookRead]
    total: int
