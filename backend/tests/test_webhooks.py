import pytest


WEBHOOK_PAYLOAD = {
    "name": "Slack Alerts",
    "url": "https://hooks.slack.com/services/T00/B00/xyz",
    "event_types": ["alert.firing"],
}

WEBHOOK_WITH_SECRET = {
    "name": "PagerDuty",
    "url": "https://events.pagerduty.com/v2/enqueue",
    "secret": "supersecrettoken",
    "event_types": ["alert.firing", "incident.opened"],
}


@pytest.mark.asyncio
async def test_create_webhook(client):
    resp = await client.post("/api/v1/webhooks/", json=WEBHOOK_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == WEBHOOK_PAYLOAD["name"]
    assert data["url"] == WEBHOOK_PAYLOAD["url"]
    assert data["is_active"] is True
    assert data["secret"] is None


@pytest.mark.asyncio
async def test_list_webhooks(client):
    await client.post("/api/v1/webhooks/", json=WEBHOOK_PAYLOAD)
    await client.post("/api/v1/webhooks/", json=WEBHOOK_WITH_SECRET)
    resp = await client.get("/api/v1/webhooks/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_secret_masked_in_response(client):
    resp = await client.post("/api/v1/webhooks/", json=WEBHOOK_WITH_SECRET)
    assert resp.status_code == 201
    data = resp.json()
    assert data["secret"] == "***"

    # Also verify in GET response
    wid = data["id"]
    get_resp = await client.get(f"/api/v1/webhooks/{wid}")
    assert get_resp.status_code == 200
    assert get_resp.json()["secret"] == "***"


@pytest.mark.asyncio
async def test_delete_webhook(client):
    create = await client.post("/api/v1/webhooks/", json=WEBHOOK_PAYLOAD)
    wid = create.json()["id"]

    resp = await client.delete(f"/api/v1/webhooks/{wid}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/webhooks/{wid}")
    assert resp.status_code == 404
