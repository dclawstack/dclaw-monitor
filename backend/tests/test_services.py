import pytest


@pytest.mark.asyncio
async def test_create_service(client):
    resp = await client.post("/api/v1/services", json={
        "name": "payment-api",
        "url": "https://payment.example.com/health",
        "description": "Payment processing service",
        "interval_seconds": 30,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "payment-api"
    assert data["status"] == "unknown"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_service_duplicate_name(client):
    payload = {"name": "auth-service", "url": "http://auth.local/health"}
    await client.post("/api/v1/services", json=payload)
    resp = await client.post("/api/v1/services", json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_services_empty(client):
    resp = await client.get("/api/v1/services")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_services(client):
    await client.post("/api/v1/services", json={"name": "svc-a", "url": "http://a.local"})
    await client.post("/api/v1/services", json={"name": "svc-b", "url": "http://b.local"})
    resp = await client.get("/api/v1/services")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


@pytest.mark.asyncio
async def test_get_service(client):
    create = await client.post("/api/v1/services", json={"name": "api-gw", "url": "http://gw.local"})
    sid = create.json()["id"]
    resp = await client.get(f"/api/v1/services/{sid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == sid


@pytest.mark.asyncio
async def test_get_service_not_found(client):
    resp = await client.get("/api/v1/services/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_service(client):
    create = await client.post("/api/v1/services", json={"name": "worker", "url": "http://worker.local"})
    sid = create.json()["id"]
    resp = await client.patch(f"/api/v1/services/{sid}", json={"status": "healthy", "interval_seconds": 120})
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    assert resp.json()["interval_seconds"] == 120


@pytest.mark.asyncio
async def test_delete_service(client):
    create = await client.post("/api/v1/services", json={"name": "temp-svc", "url": "http://tmp.local"})
    sid = create.json()["id"]
    resp = await client.delete(f"/api/v1/services/{sid}")
    assert resp.status_code == 204
    assert (await client.get(f"/api/v1/services/{sid}")).status_code == 404
