import pytest


RULE_PAYLOAD = {
    "name": "High Latency",
    "metric_name": "latency_ms",
    "operator": "gt",
    "threshold": 500.0,
    "severity": "warning",
}


@pytest.mark.asyncio
async def test_create_alert_rule(client):
    resp = await client.post("/api/v1/alert-rules", json=RULE_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "High Latency"
    assert data["operator"] == "gt"
    assert data["threshold"] == 500.0
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_list_alert_rules(client):
    await client.post("/api/v1/alert-rules", json=RULE_PAYLOAD)
    await client.post("/api/v1/alert-rules", json={**RULE_PAYLOAD, "name": "Error Rate"})
    resp = await client.get("/api/v1/alert-rules")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


@pytest.mark.asyncio
async def test_get_alert_rule(client):
    create = await client.post("/api/v1/alert-rules", json=RULE_PAYLOAD)
    rid = create.json()["id"]
    resp = await client.get(f"/api/v1/alert-rules/{rid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == rid


@pytest.mark.asyncio
async def test_get_alert_rule_not_found(client):
    resp = await client.get("/api/v1/alert-rules/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_alert_rule(client):
    create = await client.post("/api/v1/alert-rules", json=RULE_PAYLOAD)
    rid = create.json()["id"]
    resp = await client.patch(f"/api/v1/alert-rules/{rid}", json={"threshold": 1000.0, "is_active": False})
    assert resp.status_code == 200
    assert resp.json()["threshold"] == 1000.0
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_delete_alert_rule(client):
    create = await client.post("/api/v1/alert-rules", json=RULE_PAYLOAD)
    rid = create.json()["id"]
    resp = await client.delete(f"/api/v1/alert-rules/{rid}")
    assert resp.status_code == 204
    assert (await client.get(f"/api/v1/alert-rules/{rid}")).status_code == 404
