"""SRE Copilot context builder and chat service."""
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.alert import Alert
from app.models.log import LogEntry
from app.services import llm_client

logger = logging.getLogger(__name__)


async def build_context(service_id: UUID | None, db: AsyncSession) -> str:
    """Build context string from live data for LLM."""
    lines = []

    # Fetch recent open alerts (last 20)
    alert_q = (
        select(Alert)
        .where(Alert.status == "open")
        .order_by(Alert.fired_at.desc())
        .limit(20)
    )
    if service_id is not None:
        alert_q = alert_q.where(Alert.service_id == service_id)
    alert_result = await db.execute(alert_q)
    alerts = list(alert_result.scalars().all())

    if alerts:
        lines.append("=== Open Alerts ===")
        for a in alerts:
            lines.append(
                f"[{a.severity.upper()}] {a.title}: {a.message} (fired: {a.fired_at})"
            )
    else:
        lines.append("=== Open Alerts: none ===")

    # Fetch last 50 error/critical logs for service
    log_q = (
        select(LogEntry)
        .where(LogEntry.level.in_(["error", "critical"]))
        .order_by(LogEntry.logged_at.desc())
        .limit(50)
    )
    if service_id is not None:
        log_q = log_q.where(LogEntry.service_id == service_id)
    log_result = await db.execute(log_q)
    logs = list(log_result.scalars().all())

    if logs:
        lines.append("\n=== Recent Error Logs ===")
        for entry in logs:
            source = f" [{entry.source}]" if entry.source else ""
            lines.append(f"{entry.logged_at}{source} {entry.level.upper()}: {entry.message}")
    else:
        lines.append("\n=== Recent Error Logs: none ===")

    return "\n".join(lines)


async def chat(message: str, service_id: UUID | None, db: AsyncSession) -> str:
    """One-shot chat using live context."""
    context = await build_context(service_id, db)
    system = (
        "You are an expert SRE assistant. Answer questions about the monitoring system "
        "using the provided context. Be concise."
    )
    prompt = f"Context:\n{context}\n\nQuestion: {message}"
    return await llm_client.complete(prompt, system)
