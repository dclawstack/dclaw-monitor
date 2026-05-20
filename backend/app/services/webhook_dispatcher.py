"""Webhook dispatcher: sends alert payloads to configured webhook endpoints."""
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.repositories.webhook_config_repo import WebhookConfigRepository


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
            success = False
            for attempt in range(2):  # one retry
                try:
                    resp = await client.post(webhook.url, json=payload)
                    resp.raise_for_status()
                    success = True
                    print(
                        f"[webhook_dispatcher] Dispatched to {webhook.name} ({webhook.url}): "
                        f"status={resp.status_code}"
                    )
                    break
                except Exception as exc:
                    if attempt == 0:
                        print(
                            f"[webhook_dispatcher] Attempt {attempt+1} failed for "
                            f"{webhook.name}: {exc}. Retrying..."
                        )
                    else:
                        print(
                            f"[webhook_dispatcher] All attempts failed for "
                            f"{webhook.name}: {exc}"
                        )
            if not success:
                print(f"[webhook_dispatcher] Failed to deliver to {webhook.name}")
