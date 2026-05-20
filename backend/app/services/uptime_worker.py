"""Background task: periodic uptime checks for all active MonitoredServices."""
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.check import UptimeCheck
from app.repositories.service_repo import ServiceRepository
from app.repositories.check_repo import CheckRepository
from app.core.utils import utc_now


_engine = create_async_engine(settings.database_url, pool_pre_ping=True)
_async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    _engine, expire_on_commit=False
)


async def run_uptime_checks() -> None:
    """Check all active services and record UptimeCheck results."""
    async with _async_session() as db:
        service_repo = ServiceRepository(db)
        check_repo = CheckRepository(db)

        services = await service_repo.list_active(limit=500)

        for svc in services:
            status = "up"
            latency_ms: int | None = None
            status_code: int | None = None
            error: str | None = None

            start = utc_now()
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(str(svc.url))
                end = utc_now()
                elapsed = (end - start).total_seconds()
                latency_ms = int(elapsed * 1000)
                status_code = resp.status_code
                if 200 <= resp.status_code < 300:
                    status = "up"
                else:
                    status = "down"
            except httpx.TimeoutException:
                status = "timeout"
                error = "Request timed out"
            except Exception as exc:
                status = "error"
                error = str(exc)[:500]

            check = UptimeCheck(
                service_id=svc.id,
                status=status,
                latency_ms=latency_ms,
                status_code=status_code,
                error=error,
            )
            await check_repo.create(check)

            # Update service status
            if status == "up":
                new_service_status = "healthy"
            elif status == "timeout":
                new_service_status = "degraded"
            else:
                new_service_status = "down"

            await service_repo.update_status(svc.id, new_service_status)
