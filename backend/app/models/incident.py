import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.core.utils import utc_now


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    # status: open | investigating | resolved
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="warning", nullable=False)
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("monitored_services.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # JSON list of alert UUIDs (as strings) associated with this incident
    alert_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    rca_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
