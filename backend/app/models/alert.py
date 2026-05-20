import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.core.utils import utc_now


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("monitored_services.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # metric name to watch, e.g. "latency_ms" or check status "status"
    metric_name: Mapped[str] = mapped_column(String(200), nullable=False)
    # operator: gt | lt | eq | gte | lte
    operator: Mapped[str] = mapped_column(String(10), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    # severity: info | warning | critical
    severity: Mapped[str] = mapped_column(String(20), default="warning", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    rule_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("alert_rules.id", ondelete="SET NULL"), nullable=True, index=True
    )
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("monitored_services.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    # severity: info | warning | critical
    severity: Mapped[str] = mapped_column(String(20), default="warning", nullable=False)
    # status: open | acknowledged | resolved
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False, index=True)
    fired_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
