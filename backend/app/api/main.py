from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import health
from app.api.routes import prometheus
from app.api.v1 import services, checks, alert_rules, alerts, metrics, logs
from app.api.v1 import incidents, webhooks, slos
from app.api.v1 import ai, synthetic, traces
from app.services.scheduler import start_scheduler, stop_scheduler

# Import all models so SQLAlchemy metadata and Alembic can discover them
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(prometheus.router, prefix="", tags=["prometheus"])
app.include_router(services.router, prefix="/api/v1/services", tags=["services"])
app.include_router(checks.router, prefix="/api/v1/checks", tags=["checks"])
app.include_router(alert_rules.router, prefix="/api/v1/alert-rules", tags=["alert-rules"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["logs"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["incidents"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(slos.router, prefix="/api/v1/slos", tags=["slos"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(synthetic.router, prefix="/api/v1/synthetic", tags=["synthetic"])
app.include_router(traces.router, prefix="/api/v1/traces", tags=["traces"])
