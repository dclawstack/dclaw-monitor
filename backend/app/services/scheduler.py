"""APScheduler-based background job scheduler."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.services.uptime_worker import run_uptime_checks
from app.services.alert_evaluator import run_alert_evaluation

_scheduler: AsyncIOScheduler | None = None


def start_scheduler() -> None:
    """Create and start the AsyncIOScheduler with configured jobs."""
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

    _scheduler.start()


def stop_scheduler() -> None:
    """Shut down the scheduler gracefully."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
