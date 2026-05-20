import pytest


ALERT_PAYLOAD = {
    "title": "CPU spike on api-gateway",
    "message": "CPU usage exceeded 90% for 5 minutes",
    "severity": "critical",
}


@pytest.mark.asyncio
async def test_create_alert(client):
    resp = await client.post("/api/v1/alerts/", json=ALERT_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == ALERT_PAYLOAD["title"]
    assert data["status"] == "open"
    assert data["resolved_at"] is None


@pytest.mark.asyncio
async def test_list_alerts_empty(client):
    resp = await client.get("/api/v1/alerts/")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_list_open_alerts(client):
    await client.post("/api/v1/alerts/", json=ALERT_PAYLOAD)
    await client.post("/api/v1/alerts/", json={**ALERT_PAYLOAD, "title": "Another alert"})
    resp = await client.get("/api/v1/alerts/?status=open")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


@pytest.mark.asyncio
async def test_acknowledge_alert(client):
    create = await client.post("/api/v1/alerts/", json=ALERT_PAYLOAD)
    aid = create.json()["id"]
    resp = await client.patch(f"/api/v1/alerts/{aid}/status", json={"status": "acknowledged"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "acknowledged"


@pytest.mark.asyncio
async def test_resolve_alert(client):
    create = await client.post("/api/v1/alerts/", json=ALERT_PAYLOAD)
    aid = create.json()["id"]
    resp = await client.patch(f"/api/v1/alerts/{aid}/status", json={"status": "resolved"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "resolved"
    assert data["resolved_at"] is not None


@pytest.mark.asyncio
async def test_get_alert_not_found(client):
    resp = await client.get("/api/v1/alerts/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_status_not_found(client):
    resp = await client.patch(
        "/api/v1/alerts/00000000-0000-0000-0000-000000000001/status",
        json={"status": "resolved"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_filter_by_resolved_and_acknowledged_status(client):
    r1 = await client.post("/api/v1/alerts/", json=ALERT_PAYLOAD)
    r2 = await client.post("/api/v1/alerts/", json={**ALERT_PAYLOAD, "title": "Second alert"})
    r3 = await client.post("/api/v1/alerts/", json={**ALERT_PAYLOAD, "title": "Third alert"})

    await client.patch(f"/api/v1/alerts/{r1.json()['id']}/status", json={"status": "resolved"})
    await client.patch(f"/api/v1/alerts/{r2.json()['id']}/status", json={"status": "acknowledged"})
    # r3 stays open

    resolved = await client.get("/api/v1/alerts/?status=resolved")
    assert resolved.status_code == 200
    assert resolved.json()["total"] == 1
    assert resolved.json()["items"][0]["status"] == "resolved"

    acknowledged = await client.get("/api/v1/alerts/?status=acknowledged")
    assert acknowledged.status_code == 200
    assert acknowledged.json()["total"] == 1
    assert acknowledged.json()["items"][0]["status"] == "acknowledged"

    open_alerts = await client.get("/api/v1/alerts/?status=open")
    assert open_alerts.status_code == 200
    assert open_alerts.json()["total"] == 1
