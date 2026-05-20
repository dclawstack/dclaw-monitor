import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.core.utils import utc_now


class TraceSpan(Base):
    __tablename__ = "trace_spans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    span_id: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_span_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("monitored_services.id", ondelete="SET NULL"), nullable=True, index=True
    )
    operation_name: Mapped[str] = mapped_column(String(500), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_ms: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ok", nullable=False)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
