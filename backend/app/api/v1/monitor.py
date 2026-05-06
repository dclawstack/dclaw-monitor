import uuid
import random
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["monitor"])


class CheckServiceRequest(BaseModel):
    service_name: str


class ServiceHealth(BaseModel):
    id: str
    service_name: str
    status: str
    latency_ms: int
    error_rate: float
    root_cause: str
    created_at: str


class HistoryItem(BaseModel):
    timestamp: str
    status: str
    latency_ms: int


class HistoryResponse(BaseModel):
    history: list[HistoryItem]


@router.post("/services", response_model=ServiceHealth)
async def check_service(req: CheckServiceRequest):
    return ServiceHealth(
        id=str(uuid.uuid4()),
        service_name=req.service_name,
        status="degraded",
        latency_ms=random.randint(50, 500),
        error_rate=round(random.uniform(0.01, 0.15), 4),
        root_cause="Database connection pool exhausted",
        created_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/services/{id}/history", response_model=HistoryResponse)
async def get_service_history(id: str):
    now = datetime.now(timezone.utc)
    statuses = ["healthy", "healthy", "degraded", "healthy", "degraded"]
    history = [
        HistoryItem(
            timestamp=(now - timedelta(minutes=i * 5)).isoformat(),
            status=statuses[i],
            latency_ms=random.randint(50, 500),
        )
        for i in range(5)
    ]
    return HistoryResponse(history=history)
