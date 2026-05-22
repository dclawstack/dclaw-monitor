import pytest


@pytest.mark.asyncio
async def test_ingest_log(client):
    resp = await client.post("/api/v1/logs", json={
        "level": "error",
        "message": "Database connection refused",
        "source": "payment-worker",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["level"] == "error"
    assert data["message"] == "Database connection refused"


@pytest.mark.asyncio
async def test_ingest_log_with_service(client):
    svc = await client.post("/api/v1/services", json={"name": "log-svc", "url": "http://log.local"})
    sid = svc.json()["id"]
    resp = await client.post("/api/v1/logs", json={
        "service_id": sid,
        "level": "warning",
        "message": "Connection pool at 80%",
    })
    assert resp.status_code == 201
    assert resp.json()["service_id"] == sid


@pytest.mark.asyncio
async def test_query_logs(client):
    for msg in ["error one", "error two", "info message"]:
        await client.post("/api/v1/logs", json={"level": "info", "message": msg})
    resp = await client.get("/api/v1/logs")
    assert resp.status_code == 200
    assert resp.json()["total"] == 3


@pytest.mark.asyncio
async def test_search_logs_by_keyword(client):
    await client.post("/api/v1/logs", json={"message": "OutOfMemoryError in payment-service"})
    await client.post("/api/v1/logs", json={"message": "Request completed successfully"})
    resp = await client.get("/api/v1/logs?q=OutOfMemory")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_filter_logs_by_level(client):
    await client.post("/api/v1/logs", json={"level": "error", "message": "Crash!"})
    await client.post("/api/v1/logs", json={"level": "info", "message": "Started."})
    resp = await client.get("/api/v1/logs?level=error")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["level"] == "error"


@pytest.mark.asyncio
async def test_filter_logs_by_service(client):
    svc = await client.post("/api/v1/services", json={"name": "log-filter-svc", "url": "http://lf.local"})
    sid = svc.json()["id"]
    await client.post("/api/v1/logs", json={"service_id": sid, "message": "Service log"})
    await client.post("/api/v1/logs", json={"message": "Other log"})
    resp = await client.get(f"/api/v1/logs?service_id={sid}")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
