import pytest


JOURNEY_PAYLOAD = {
    "name": "Homepage health check",
    "steps": [{"action": "GET", "url": "https://example.com/", "expect_status": 200}],
    "interval_seconds": 60,
    "is_active": True,
}


@pytest.mark.asyncio
async def test_create_journey(client):
    resp = await client.post("/api/v1/synthetic/", json=JOURNEY_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == JOURNEY_PAYLOAD["name"]
    assert data["interval_seconds"] == 60
    assert data["is_active"] is True
    assert data["steps"] == JOURNEY_PAYLOAD["steps"]


@pytest.mark.asyncio
async def test_list_journeys_empty(client):
    resp = await client.get("/api/v1/synthetic/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_list_journeys(client):
    await client.post("/api/v1/synthetic/", json=JOURNEY_PAYLOAD)
    await client.post("/api/v1/synthetic/", json={**JOURNEY_PAYLOAD, "name": "API ping"})
    resp = await client.get("/api/v1/synthetic/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_get_journey(client):
    create = await client.post("/api/v1/synthetic/", json=JOURNEY_PAYLOAD)
    jid = create.json()["id"]
    resp = await client.get(f"/api/v1/synthetic/{jid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == jid


@pytest.mark.asyncio
async def test_get_journey_not_found(client):
    resp = await client.get("/api/v1/synthetic/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_journey(client):
    create = await client.post("/api/v1/synthetic/", json=JOURNEY_PAYLOAD)
    jid = create.json()["id"]
    resp = await client.patch(f"/api/v1/synthetic/{jid}", json={"is_active": False})
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_delete_journey(client):
    create = await client.post("/api/v1/synthetic/", json=JOURNEY_PAYLOAD)
    jid = create.json()["id"]
    del_resp = await client.delete(f"/api/v1/synthetic/{jid}")
    assert del_resp.status_code == 204
    get_resp = await client.get(f"/api/v1/synthetic/{jid}")
    assert get_resp.status_code == 404
