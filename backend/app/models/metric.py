import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.core.utils import utc_now


class MetricSample(Base):
    __tablename__ = "metric_samples"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("monitored_services.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # metric name, e.g. "cpu_usage", "latency_p99", "error_rate"
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    # optional key-value labels/tags as JSON
    labels: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sampled_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
