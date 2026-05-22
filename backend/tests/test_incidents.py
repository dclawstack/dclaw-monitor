import pytest


INCIDENT_PAYLOAD = {
    "title": "Database connection pool exhausted",
    "severity": "critical",
}


@pytest.mark.asyncio
async def test_create_incident(client):
    resp = await client.post("/api/v1/incidents", json=INCIDENT_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == INCIDENT_PAYLOAD["title"]
    assert data["severity"] == "critical"
    assert data["status"] == "open"
    assert data["resolved_at"] is None
    assert data["mttr_seconds"] is None


@pytest.mark.asyncio
async def test_list_incidents(client):
    await client.post("/api/v1/incidents", json=INCIDENT_PAYLOAD)
    await client.post("/api/v1/incidents", json={**INCIDENT_PAYLOAD, "title": "Second incident"})
    resp = await client.get("/api/v1/incidents")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_by_status_filter(client):
    r1 = await client.post("/api/v1/incidents", json=INCIDENT_PAYLOAD)
    r2 = await client.post("/api/v1/incidents", json={**INCIDENT_PAYLOAD, "title": "Another"})

    # Resolve r1
    await client.post(f"/api/v1/incidents/{r1.json()['id']}/resolve")

    open_resp = await client.get("/api/v1/incidents?status=open")
    assert open_resp.status_code == 200
    assert open_resp.json()["total"] == 1

    resolved_resp = await client.get("/api/v1/incidents?status=resolved")
    assert resolved_resp.status_code == 200
    assert resolved_resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_resolve_incident(client):
    create = await client.post("/api/v1/incidents", json=INCIDENT_PAYLOAD)
    iid = create.json()["id"]

    resp = await client.post(f"/api/v1/incidents/{iid}/resolve")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "resolved"
    assert data["resolved_at"] is not None
    assert data["mttr_seconds"] is not None
    assert data["mttr_seconds"] >= 0


@pytest.mark.asyncio
async def test_get_not_found(client):
    resp = await client.get("/api/v1/incidents/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 404
