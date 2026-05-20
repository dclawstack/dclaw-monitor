"""LLM-based alert noise reduction — groups correlated alerts into incidents."""
import json
import logging
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select

from app.core.config import settings
from app.core.utils import utc_now
from app.models.alert import Alert
from app.models.incident import Incident
from app.services import llm_client

logger = logging.getLogger(__name__)

# Module-level engine/session factory (lazy-initialised to avoid import-time side effects)
_engine = None
_async_session = None


def _get_session_factory():
    global _engine, _async_session
    if _async_session is None:
        from sqlalchemy.ext.asyncio import async_sessionmaker

        _engine = create_async_engine(settings.database_url, pool_pre_ping=True)
        _async_session = async_sessionmaker(_engine, expire_on_commit=False)
    return _async_session


async def correlate_alerts() -> None:
    """Run every 2 minutes via scheduler. Groups open alerts into incidents."""
    session_factory = _get_session_factory()
    async with session_factory() as db:
        await _do_correlate(db)


async def _do_correlate(db: AsyncSession) -> None:
    cutoff = utc_now() - timedelta(minutes=5)
    result = await db.execute(
        select(Alert)
        .where(Alert.status == "open", Alert.fired_at >= cutoff)
        .order_by(Alert.fired_at.asc())
    )
    alerts = list(result.scalars().all())

    if len(alerts) < 2:
        logger.debug("Not enough open alerts to correlate (%d)", len(alerts))
        return

    # Build prompt
    alert_lines = "\n".join(
        f"{i}: title={a.title!r} message={a.message!r} severity={a.severity}"
        for i, a in enumerate(alerts)
    )
    system = (
        "You are an SRE assistant. Your job is to group related alerts into incidents. "
        "Return ONLY valid JSON — a list of objects with keys 'group_label' (string) and "
        "'alert_indices' (list of integers). Do not include any explanation."
    )
    prompt = (
        f"Here are {len(alerts)} open alerts:\n{alert_lines}\n\n"
        "Group related alerts into incidents. Return JSON only."
    )

    groups: list[dict] = []
    try:
        raw = await llm_client.complete(prompt, system)
        # Strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        groups = json.loads(raw)
        if not isinstance(groups, list):
            raise ValueError("LLM response is not a list")
    except Exception as e:
        logger.warning("LLM correlation failed (%s), falling back to one incident per alert", e)
        # Fallback: one incident per alert
        groups = [
            {"group_label": alerts[i].title, "alert_indices": [i]} for i in range(len(alerts))
        ]

    for group in groups:
        try:
            indices = group.get("alert_indices", [])
            label = group.get("group_label", "Correlated incident")
            if not indices:
                continue

            group_alert_ids = [str(alerts[i].id) for i in indices if i < len(alerts)]

            if len(group_alert_ids) < 2:
                continue

            # Check if an incident already covers these alert_ids
            existing = await db.execute(
                select(Incident).where(Incident.status == "open").limit(100)
            )
            existing_incidents = list(existing.scalars().all())

            already_grouped = False
            for inc in existing_incidents:
                if inc.alert_ids and set(group_alert_ids).issubset(set(inc.alert_ids)):
                    already_grouped = True
                    break

            if already_grouped:
                continue

            # Pick severity from the highest-severity alert
            severity_rank = {"info": 0, "warning": 1, "critical": 2}
            severities = [alerts[i].severity for i in indices if i < len(alerts)]
            max_severity = max(severities, key=lambda s: severity_rank.get(s, 0))

            incident = Incident(
                title=label,
                status="open",
                severity=max_severity,
                alert_ids=group_alert_ids,
            )
            db.add(incident)
            logger.info("Created correlated incident %r covering %d alerts", label, len(group_alert_ids))
        except Exception as e:
            logger.error("Error processing alert group: %s", e)

    await db.commit()
