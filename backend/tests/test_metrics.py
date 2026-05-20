import pytest


@pytest.mark.asyncio
async def test_ingest_metric(client):
    resp = await client.post("/api/v1/metrics/", json={
        "name": "cpu_usage",
        "value": 72.5,
        "labels": {"host": "web-01", "region": "us-east-1"},
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "cpu_usage"
    assert data["value"] == 72.5
    assert data["labels"]["host"] == "web-01"


@pytest.mark.asyncio
async def test_ingest_metric_with_service(client):
    svc = await client.post("/api/v1/services/", json={"name": "infra-svc", "url": "http://infra.local"})
    sid = svc.json()["id"]
    resp = await client.post("/api/v1/metrics/", json={
        "service_id": sid,
        "name": "latency_p99",
        "value": 450.0,
    })
    assert resp.status_code == 201
    assert resp.json()["service_id"] == sid


@pytest.mark.asyncio
async def test_query_metrics(client):
    for v in [10.0, 20.0, 30.0]:
        await client.post("/api/v1/metrics/", json={"name": "mem_usage", "value": v})
    resp = await client.get("/api/v1/metrics/?name=mem_usage")
    assert resp.status_code == 200
    assert resp.json()["total"] == 3


@pytest.mark.asyncio
async def test_query_metrics_filter_by_service(client):
    svc = await client.post("/api/v1/services/", json={"name": "filter-svc", "url": "http://fs.local"})
    sid = svc.json()["id"]
    await client.post("/api/v1/metrics/", json={"name": "rps", "value": 100.0, "service_id": sid})
    await client.post("/api/v1/metrics/", json={"name": "rps", "value": 200.0})
    resp = await client.get(f"/api/v1/metrics/?name=rps&service_id={sid}")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_query_metrics_requires_name(client):
    resp = await client.get("/api/v1/metrics/")
    assert resp.status_code == 422
