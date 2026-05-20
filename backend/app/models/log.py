import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.core.utils import utc_now


class LogEntry(Base):
    __tablename__ = "log_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("monitored_services.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # level: debug | info | warning | error | critical
    level: Mapped[str] = mapped_column(String(20), default="info", nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(500), nullable=True)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
