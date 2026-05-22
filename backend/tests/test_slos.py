import pytest


SLO_PAYLOAD = {
    "name": "API Latency SLO",
    "target_percent": 99.0,
    "window_days": 30,
    "metric_name": "latency_ms",
    "good_condition": "lt",
    "good_threshold": 200.0,
}


@pytest.mark.asyncio
async def test_create_slo(client):
    resp = await client.post("/api/v1/slos", json=SLO_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == SLO_PAYLOAD["name"]
    assert data["target_percent"] == 99.0
    assert data["good_condition"] == "lt"
    assert data["service_id"] is None


@pytest.mark.asyncio
async def test_list_slos(client):
    await client.post("/api/v1/slos", json=SLO_PAYLOAD)
    await client.post("/api/v1/slos", json={**SLO_PAYLOAD, "name": "Error Rate SLO"})
    resp = await client.get("/api/v1/slos")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_get_slo_status(client):
    create = await client.post("/api/v1/slos", json=SLO_PAYLOAD)
    sid = create.json()["id"]

    resp = await client.get(f"/api/v1/slos/{sid}/status")
    assert resp.status_code == 200
    data = resp.json()
    # With no metrics, should return sensible defaults
    assert data["total_samples"] == 0
    assert data["good_samples"] == 0
    assert data["current_percent"] == 0.0
    assert data["target_percent"] == 99.0
    assert "error_budget_remaining" in data
    assert "burn_rate" in data


@pytest.mark.asyncio
async def test_delete_slo(client):
    create = await client.post("/api/v1/slos", json=SLO_PAYLOAD)
    sid = create.json()["id"]

    resp = await client.delete(f"/api/v1/slos/{sid}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/slos/{sid}")
    assert resp.status_code == 404
