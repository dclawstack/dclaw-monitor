from uuid import UUID
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.slo import SLO
from app.models.metric import MetricSample
from app.repositories.base_repo import BaseRepository
from app.core.utils import utc_now


class SLORepository(BaseRepository[SLO]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SLO)

    async def list_by_service(self, service_id: UUID) -> list[SLO]:
        result = await self.db.execute(
            select(SLO).where(SLO.service_id == service_id)
        )
        return list(result.scalars().all())

    async def compute_status(self, slo_id: UUID) -> dict | None:
        """Compute SLOStatus metrics by querying MetricSamples."""
        slo = await self.get_by_id(slo_id)
        if slo is None:
            return None

        since = utc_now() - timedelta(days=slo.window_days)
        q = (
            select(MetricSample)
            .where(MetricSample.name == slo.metric_name)
            .where(MetricSample.sampled_at >= since)
        )
        if slo.service_id is not None:
            q = q.where(MetricSample.service_id == slo.service_id)

        result = await self.db.execute(q)
        samples = list(result.scalars().all())

        total_samples = len(samples)
        if total_samples == 0:
            return {
                "target_percent": slo.target_percent,
                "current_percent": 0.0,
                "error_budget_remaining": slo.target_percent,
                "burn_rate": 0.0,
                "total_samples": 0,
                "good_samples": 0,
            }

        # Count "good" samples based on good_condition
        if slo.good_condition == "lt":
            good_samples = sum(1 for s in samples if s.value < slo.good_threshold)
        elif slo.good_condition == "gt":
            good_samples = sum(1 for s in samples if s.value > slo.good_threshold)
        else:
            good_samples = 0

        current_percent = (good_samples / total_samples) * 100.0
        error_budget_remaining = current_percent - (100.0 - slo.target_percent)
        # burn_rate: how fast error budget is being consumed vs. expected
        # 1.0 = right on target, >1.0 = burning faster than acceptable
        error_budget_total = 100.0 - slo.target_percent
        if error_budget_total > 0:
            actual_error_rate = 100.0 - current_percent
            burn_rate = actual_error_rate / error_budget_total
        else:
            burn_rate = 0.0

        return {
            "target_percent": slo.target_percent,
            "current_percent": current_percent,
            "error_budget_remaining": error_budget_remaining,
            "burn_rate": burn_rate,
            "total_samples": total_samples,
            "good_samples": good_samples,
        }
