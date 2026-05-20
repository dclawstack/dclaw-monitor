import pytest
from datetime import datetime, timezone


def _span(trace_id: str, span_id: str, op: str = "http.request", parent: str | None = None):
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent,
        "operation_name": op,
        "start_time": "2026-01-01T00:00:00",
        "end_time": "2026-01-01T00:00:00.150",
        "duration_ms": 150.0,
        "status": "ok",
    }


@pytest.mark.asyncio
async def test_ingest_single_span(client):
    spans = [_span("trace-001", "span-001")]
    resp = await client.post("/api/v1/traces/ingest", json=spans)
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 1


@pytest.mark.asyncio
async def test_ingest_multiple_spans(client):
    spans = [
        _span("trace-002", "span-a", "db.query"),
        _span("trace-002", "span-b", "http.request", parent="span-a"),
    ]
    resp = await client.post("/api/v1/traces/ingest", json=spans)
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 2


@pytest.mark.asyncio
async def test_list_spans_by_trace_id(client):
    await client.post("/api/v1/traces/ingest", json=[
        _span("trace-003", "s1", "root"),
        _span("trace-003", "s2", "child", parent="s1"),
    ])
    resp = await client.get("/api/v1/traces/?trace_id=trace-003")
    assert resp.status_code == 200
    spans = resp.json()
    assert len(spans) == 2
    assert all(s["trace_id"] == "trace-003" for s in spans)


@pytest.mark.asyncio
async def test_list_spans_empty_trace(client):
    resp = await client.get("/api/v1/traces/?trace_id=nonexistent-trace")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_duration_auto_computed(client):
    span = {
        "trace_id": "trace-004",
        "span_id": "span-004",
        "operation_name": "compute",
        "start_time": "2026-01-01T00:00:00",
        "end_time": "2026-01-01T00:00:01",
        # no duration_ms — should be computed from start/end
    }
    resp = await client.post("/api/v1/traces/ingest", json=[span])
    assert resp.status_code == 200

    spans = await client.get("/api/v1/traces/?trace_id=trace-004")
    assert spans.json()[0]["duration_ms"] == pytest.approx(1000.0, abs=1.0)


@pytest.mark.asyncio
async def test_list_recent_traces(client):
    await client.post("/api/v1/traces/ingest", json=[
        _span("trace-r1", "s1"),
        _span("trace-r2", "s2"),
    ])
    resp = await client.get("/api/v1/traces/recent")
    assert resp.status_code == 200
    trace_ids = {t["trace_id"] for t in resp.json()}
    assert "trace-r1" in trace_ids
    assert "trace-r2" in trace_ids
