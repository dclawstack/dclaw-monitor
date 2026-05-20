"""Root Cause Analysis engine. Runs asynchronously after incident creation."""
import logging
from datetime import timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.core.utils import utc_now
from app.models.incident import Incident
from app.models.log import LogEntry
from app.models.metric import MetricSample
from app.services import llm_client

logger = logging.getLogger(__name__)

_engine = None
_async_session = None


def _get_session_factory():
    global _engine, _async_session
    if _async_session is None:
        _engine = create_async_engine(settings.database_url, pool_pre_ping=True)
        _async_session = async_sessionmaker(_engine, expire_on_commit=False)
    return _async_session


async def analyze_incident(incident_id: UUID) -> None:
    """Fetch context from a fresh DB session and store RCA in incident.rca_summary."""
    session_factory = _get_session_factory()
    async with session_factory() as db:
        await _do_analyze(incident_id, db)


async def _do_analyze(incident_id: UUID, db) -> None:
    try:
        result = await db.execute(select(Incident).where(Incident.id == incident_id))
        incident = result.scalar_one_or_none()
        if incident is None:
            logger.warning("RCA: incident %s not found", incident_id)
            return

        cutoff = utc_now() - timedelta(minutes=30)

        log_q = (
            select(LogEntry)
            .where(LogEntry.level.in_(["error", "critical"]), LogEntry.logged_at >= cutoff)
            .order_by(LogEntry.logged_at.desc())
            .limit(30)
        )
        if incident.service_id is not None:
            log_q = log_q.where(LogEntry.service_id == incident.service_id)
        logs = list((await db.execute(log_q)).scalars().all())

        metric_q = (
            select(MetricSample)
            .where(MetricSample.sampled_at >= cutoff)
            .order_by(MetricSample.sampled_at.desc())
            .limit(30)
        )
        if incident.service_id is not None:
            metric_q = metric_q.where(MetricSample.service_id == incident.service_id)
        metrics = list((await db.execute(metric_q)).scalars().all())

        lines = [f"Incident: {incident.title}", f"Severity: {incident.severity}", ""]

        if logs:
            lines.append("=== Error Logs (last 30 min) ===")
            for entry in logs:
                source = f" [{entry.source}]" if entry.source else ""
                lines.append(f"{entry.logged_at}{source}: {entry.message}")
        else:
            lines.append("=== Error Logs: none in last 30 min ===")

        if metrics:
            lines.append("\n=== Recent Metric Samples ===")
            for m in metrics:
                lines.append(f"{m.sampled_at} {m.name}={m.value}")
        else:
            lines.append("\n=== Recent Metrics: none in last 30 min ===")

        system = (
            "You are a senior SRE performing root cause analysis. "
            "Based on the incident details, error logs, and metrics provided, "
            "identify the most likely root cause and provide actionable remediation steps. "
            "Be concise and structured."
        )
        prompt = "\n".join(lines) + "\n\nProvide a root cause analysis for this incident."

        rca = await llm_client.complete(prompt, system)
        incident.rca_summary = rca
        await db.commit()
        logger.info("RCA completed for incident %s", incident_id)

    except Exception as e:
        logger.error("RCA failed for incident %s: %s", incident_id, e)
