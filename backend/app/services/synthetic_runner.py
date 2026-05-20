"""Execute synthetic journey steps and record uptime checks."""
import logging
import time
from uuid import UUID

import httpx

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import settings
from app.core.utils import utc_now
from app.models.check import UptimeCheck
from app.models.synthetic_journey import SyntheticJourney
from app.repositories.synthetic_repo import SyntheticJourneyRepository

logger = logging.getLogger(__name__)

_engine = None
_async_session = None


def _get_session_factory():
    global _engine, _async_session
    if _async_session is None:
        _engine = create_async_engine(settings.database_url, pool_pre_ping=True)
        _async_session = async_sessionmaker(_engine, expire_on_commit=False)
    return _async_session


async def run_journey(journey: SyntheticJourney, db: AsyncSession) -> list[UptimeCheck]:
    """Execute all steps in a synthetic journey and write UptimeCheck records."""
    steps = journey.steps or []
    checks = []

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        for step in steps:
            method = step.get("method", "GET").upper()
            url = step.get("url", "")
            expected_status = step.get("expected_status", 200)

            if not url:
                continue

            start = time.monotonic()
            status_code = None
            error = None
            check_status = "up"

            try:
                resp = await client.request(method, url)
                elapsed_ms = int((time.monotonic() - start) * 1000)
                status_code = resp.status_code
                if status_code != expected_status:
                    check_status = "down"
                    error = f"Expected {expected_status}, got {status_code}"
            except httpx.TimeoutException:
                elapsed_ms = int((time.monotonic() - start) * 1000)
                check_status = "timeout"
                error = "Request timed out"
            except Exception as e:
                elapsed_ms = int((time.monotonic() - start) * 1000)
                check_status = "error"
                error = str(e)[:1000]

            check = UptimeCheck(
                service_id=journey.service_id,
                status=check_status,
                latency_ms=elapsed_ms,
                status_code=status_code,
                error=error,
            )
            db.add(check)
            checks.append(check)

    if checks:
        await db.commit()
        for c in checks:
            await db.refresh(c)

    return checks


async def run_all_active_journeys() -> None:
    """Scheduler entry point: run all active synthetic journeys."""
    session_factory = _get_session_factory()
    async with session_factory() as db:
        repo = SyntheticJourneyRepository(db)
        journeys = await repo.list_active()
        for journey in journeys:
            try:
                checks = await run_journey(journey, db)
                logger.info(
                    "Synthetic journey %r (%s): %d checks completed",
                    journey.name,
                    journey.id,
                    len(checks),
                )
            except Exception as e:
                logger.error("Error running synthetic journey %s: %s", journey.id, e)
