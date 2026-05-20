"""APScheduler integration for background jobs."""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.services.alert_correlator import correlate_alerts
from app.services.synthetic_runner import run_all_active_journeys

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
        _scheduler.add_job(
            correlate_alerts,
            trigger="interval",
            seconds=120,
            id="correlate_alerts",
            replace_existing=True,
        )
        _scheduler.add_job(
            run_all_active_journeys,
            trigger="interval",
            seconds=60,
            id="synthetic_journeys",
            replace_existing=True,
        )
        logger.info("Scheduler configured with jobs: correlate_alerts, synthetic_journeys")
    return _scheduler


def start_scheduler() -> None:
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
