"""Root Cause Analysis engine. Runs asynchronously after incident creation."""
import logging
from datetime import timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.utils import utc_now
from app.models.incident import Incident
from app.models.log import LogEntry
from app.models.metric import MetricSample
from app.services import llm_client

logger = logging.getLogger(__name__)


async def analyze_incident(incident_id: UUID, db: AsyncSession) -> None:
    """Async, non-blocking. Fetches context and stores RCA in incident.rca_summary."""
    try:
        # Fetch incident
        result = await db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        incident = result.scalar_one_or_none()
        if incident is None:
            logger.warning("RCA: incident %s not found", incident_id)
            return

        cutoff = utc_now() - timedelta(minutes=30)

        # Fetch error logs for affected service (last 30 min)
        log_q = (
            select(LogEntry)
            .where(
                LogEntry.level.in_(["error", "critical"]),
                LogEntry.logged_at >= cutoff,
            )
            .order_by(LogEntry.logged_at.desc())
            .limit(30)
        )
        if incident.service_id is not None:
            log_q = log_q.where(LogEntry.service_id == incident.service_id)
        log_result = await db.execute(log_q)
        logs = list(log_result.scalars().all())

        # Fetch anomalous metric samples (last 30 min)
        metric_q = (
            select(MetricSample)
            .where(MetricSample.sampled_at >= cutoff)
            .order_by(MetricSample.sampled_at.desc())
            .limit(30)
        )
        if incident.service_id is not None:
            metric_q = metric_q.where(MetricSample.service_id == incident.service_id)
        metric_result = await db.execute(metric_q)
        metrics = list(metric_result.scalars().all())

        # Build prompt
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

        context = "\n".join(lines)
        system = (
            "You are a senior SRE performing root cause analysis. "
            "Based on the incident details, error logs, and metrics provided, "
            "identify the most likely root cause and provide actionable remediation steps. "
            "Be concise and structured."
        )
        prompt = f"{context}\n\nProvide a root cause analysis for this incident."

        rca = await llm_client.complete(prompt, system)

        # Update incident
        incident.rca_summary = rca
        await db.commit()
        logger.info("RCA completed for incident %s", incident_id)

    except Exception as e:
        logger.error("RCA failed for incident %s: %s", incident_id, e)
