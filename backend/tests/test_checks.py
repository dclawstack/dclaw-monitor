import pytest


async def _create_service(client, name: str = "test-svc") -> str:
    resp = await client.post("/api/v1/services", json={"name": name, "url": "http://test.local"})
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_record_check_up(client):
    sid = await _create_service(client)
    resp = await client.post("/api/v1/checks", json={
        "service_id": sid,
        "status": "up",
        "latency_ms": 42,
        "status_code": 200,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "up"
    assert data["latency_ms"] == 42


@pytest.mark.asyncio
async def test_record_check_updates_service_status(client):
    sid = await _create_service(client, "monitored-svc")
    await client.post("/api/v1/checks", json={"service_id": sid, "status": "up", "latency_ms": 50})
    svc = await client.get(f"/api/v1/services/{sid}")
    assert svc.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_record_check_down_updates_status(client):
    sid = await _create_service(client, "down-svc")
    await client.post("/api/v1/checks", json={"service_id": sid, "status": "down"})
    svc = await client.get(f"/api/v1/services/{sid}")
    assert svc.json()["status"] == "down"


@pytest.mark.asyncio
async def test_record_check_unknown_service(client):
    resp = await client.post("/api/v1/checks", json={
        "service_id": "00000000-0000-0000-0000-000000000001",
        "status": "up",
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_checks_for_service(client):
    sid = await _create_service(client, "history-svc")
    for i in range(3):
        await client.post("/api/v1/checks", json={"service_id": sid, "status": "up", "latency_ms": i * 10})
    resp = await client.get(f"/api/v1/checks/service/{sid}")
    assert resp.status_code == 200
    assert resp.json()["total"] == 3


@pytest.mark.asyncio
async def test_list_checks_unknown_service(client):
    resp = await client.get("/api/v1/checks/service/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 404
