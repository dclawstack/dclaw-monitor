"""Webhook dispatcher: sends alert payloads to configured webhook endpoints."""
import logging

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.repositories.webhook_config_repo import WebhookConfigRepository

logger = logging.getLogger(__name__)


async def dispatch_alert(alert: Alert, db_session: AsyncSession) -> None:
    """Dispatch alert.firing events to all matching active webhook configs."""
    repo = WebhookConfigRepository(db_session)
    webhooks = await repo.list_by_event_type("alert.firing")

    payload = {
        "event": "alert.firing",
        "alert": {
            "id": str(alert.id),
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity,
            "status": alert.status,
            "fired_at": alert.fired_at.isoformat() if alert.fired_at else None,
            "rule_id": str(alert.rule_id) if alert.rule_id else None,
            "service_id": str(alert.service_id) if alert.service_id else None,
        },
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        for webhook in webhooks:
            delivered = False
            for attempt in range(2):
                try:
                    resp = await client.post(webhook.url, json=payload)
                    resp.raise_for_status()
                    delivered = True
                    logger.info(
                        "Dispatched to %s (%s): status=%d",
                        webhook.name, webhook.url, resp.status_code,
                    )
                    break
                except Exception as exc:
                    if attempt == 0:
                        logger.warning(
                            "Attempt %d failed for %s: %s — retrying",
                            attempt + 1, webhook.name, exc,
                        )
                    else:
                        logger.error("All attempts failed for %s: %s", webhook.name, exc)
            if not delivered:
                logger.error("Failed to deliver to %s", webhook.name)
