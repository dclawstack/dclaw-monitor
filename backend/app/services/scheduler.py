"""APScheduler-based background job scheduler."""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.services.uptime_worker import run_uptime_checks
from app.services.alert_evaluator import run_alert_evaluation
from app.services.alert_correlator import correlate_alerts
from app.services.synthetic_runner import run_all_active_journeys

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


def start_scheduler() -> None:
    global _scheduler
    _scheduler = AsyncIOScheduler()

    _scheduler.add_job(
        run_uptime_checks,
        trigger="interval",
        seconds=settings.check_interval_seconds,
        id="uptime_checks",
        replace_existing=True,
    )
    _scheduler.add_job(
        run_alert_evaluation,
        trigger="interval",
        seconds=30,
        id="alert_evaluation",
        replace_existing=True,
    )
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

    _scheduler.start()
    logger.info("Scheduler started with 4 jobs")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
        _scheduler = None
