# DClaw Monitor — v1.2 Feature Roadmap

> **This document is the canonical implementation plan.** Updated to reflect current implementation status.

> **Stack:** FastAPI (port 8030) · Next.js 14 App Router (port 3030) · PostgreSQL (`dclaw_monitor`) · Base API path `/api/v1`

---

## Pre-Flight Checklist

- [x] `AGENTS.md` has been read in full
- [x] `frontend/package-lock.json` is committed after any `npm install` or dependency change
- [x] `frontend/next-env.d.ts` exists and is committed
- [x] `docker-compose.yml` healthchecks use `python urllib.request.urlopen()` — NOT `curl` (backend uses Python urllib; frontend uses wget on Node alpine image)
- [x] `frontend/Dockerfile` declares `ARG NEXT_PUBLIC_API_URL` before `RUN npm run build`
- [x] All new models inherit from `Base` in `app.models.base` — NOT `declarative_base()`
- [x] All new models use `Mapped[...]` + `mapped_column()` — NOT `default_factory=`
- [x] All alembic migrations generated for every new model before tests run
- [x] All tests use `localhost:5432` for PostgreSQL (CI maps port 5432 only)
- [x] `pytest-asyncio==0.24.0` is pinned — do NOT upgrade
- [x] `.github/workflows/ci.yml` is NOT deleted or modified
- [x] Pre-built UI components in `frontend/src/components/ui/` are used — do NOT install shadcn CLI

---

## Current State (as of this branch)

| Area | Status |
|------|--------|
| Health endpoint (`GET /health/`) | ✅ Implemented |
| Domain models (services, checks, alerts, metrics, logs) | ✅ Implemented |
| Incident, WebhookConfig, SLO, SyntheticJourney, TraceSpan models | ✅ Implemented |
| Repositories for all models | ✅ Implemented |
| Alembic migrations (001 → 003) | ✅ Present |
| Tests for all domain endpoints | ✅ Present (37+ tests) |
| Frontend dashboard with real data | ✅ Implemented |
| Service detail page | ✅ Implemented |
| Alert inbox UI | ✅ Implemented |
| Incidents list + detail pages | ✅ Implemented |
| AI Copilot widget + page | ✅ Implemented |
| DPanel manifest | ✅ Implemented |
| APScheduler background jobs | ✅ Implemented |
| Alert evaluation engine | ✅ Implemented |
| AI services (LLM client, RCA, anomaly, correlator) | ✅ Implemented |
| Prometheus metrics export | ✅ Implemented |
| Distributed tracing ingestion | ✅ Implemented |
| Synthetic monitoring journeys | ✅ Implemented |

---

## YC Positioning

**Problem:** Teams pay $50,000+/month for Datadog and still miss incidents due to alert fatigue. Static thresholds miss anomalies; dashboards require manual interpretation; root cause analysis is done by hand at 3 AM.

**Solution:** DClaw Monitor is 10x cheaper than Datadog and AI-native from day 0. It combines real-time metric and log ingestion with statistical anomaly detection, LLM-powered root cause analysis, and a conversational SRE copilot — all deployable on-premise with local LLM fallback (no cloud dependency required).

**Moat:**
- AI anomaly detection without static threshold configuration
- Local LLM fallback via Ollama — no vendor lock-in, no data leaving the cluster
- Prometheus-compatible ingestion — zero migration cost from existing stacks
- Semantic log search powered by embeddings — not just keyword grep

---

## Complexity Scale

| Level | Label | Description |
|-------|-------|-------------|
| **0** | Foundation | Low complexity. Core CRUD, schema, migrations, test coverage. Quick wins that unblock everything else. |
| **1** | Core Differentiators | Medium complexity. Background workers, evaluation engines, aggregation queries, frontend data views. |
| **2** | AI and Advanced | High complexity. LLM integrations, statistical models, distributed tracing, capacity forecasting. |

---

## Complexity 0 — Foundation ✅ COMPLETE

| # | Feature | Status | Files |
|---|---------|--------|-------|
| 0.1 | Service Registry | ✅ Done | `models/service.py`, `repos/service_repo.py`, `api/v1/services.py`, `schemas/service.py` |
| 0.2 | Uptime Check | ✅ Done | `models/check.py`, `repos/check_repo.py`, `api/v1/checks.py` |
| 0.3 | Alert Rules | ✅ Done | `models/alert.py` (AlertRule), `api/v1/alert_rules.py` |
| 0.4 | Alerts | ✅ Done | `models/alert.py` (Alert), `api/v1/alerts.py` — status filter covers open/acknowledged/resolved |
| 0.5 | Metric Ingestion | ✅ Done | `models/metric.py`, `api/v1/metrics.py` |
| 0.6 | Log Ingestion | ✅ Done | `models/log.py`, `api/v1/logs.py` — full-text `ILIKE` search on `message` |
| 0.7 | Replace Mock Endpoints | ✅ Done | `api/v1/monitor.py` gutted; all routers wired in `main.py`; zero `random()` calls |
| 0.8 | Alembic Migration | ✅ Done | `001_initial_schema.py` — all 6 foundation tables |
| 0.9 | Test Coverage | ✅ Done | `test_services.py`, `test_checks.py`, `test_alert_rules.py`, `test_alerts.py`, `test_metrics.py`, `test_logs.py` |
| 0.10 | dclaw-manifest.json | ✅ Done | `frontend/public/dclaw-manifest.json` |
| 0.11 | Dashboard Overview | ✅ Done | `frontend/src/app/dashboard/page.tsx` — live data, service status, open alerts, nav |
| 0.12 | Service Detail Page | ✅ Done | `frontend/src/app/services/[id]/page.tsx` — checks table, metrics section with sparklines |

---

## Complexity 1 — Core Differentiators ✅ COMPLETE

| # | Feature | Status | Files |
|---|---------|--------|-------|
| 1.1 | Uptime Check Scheduler | ✅ Done | `services/uptime_worker.py`, `services/scheduler.py` — APScheduler, configurable interval |
| 1.2 | Alert Evaluation Engine | ✅ Done | `services/alert_evaluator.py` — evaluates rules against metric mean, fires alerts |
| 1.3 | Incident Model | ✅ Done | `models/incident.py`, `repos/incident_repo.py`, `api/v1/incidents.py` — MTTR computed on resolve |
| 1.4 | Log Full-Text Search | ✅ Done | `repos/log_repo.py` — `ILIKE` on `message`; `?q=` param in `GET /api/v1/logs` |
| 1.5 | Metrics Time-Series Aggregation | ✅ Done | `repos/metric_repo.py#aggregate_by_window`, `GET /api/v1/metrics/aggregate?window=5m` |
| 1.6 | Webhook Notifications | ✅ Done | `models/webhook_config.py`, `services/webhook_dispatcher.py`, `api/v1/webhooks.py` |
| 1.7 | SLO Model | ✅ Done | `models/slo.py`, `repos/slo_repo.py`, `api/v1/slos.py` — `GET /slos/{id}/status` returns error budget |
| 1.8 | Frontend Metrics Charts | ✅ Done | `frontend/src/components/sparkline.tsx` — pure SVG sparkline |
| 1.9 | Alert Inbox UI | ✅ Done | `frontend/src/app/alerts/page.tsx` — tabbed (All/Open/Acknowledged/Resolved), acknowledge/resolve actions |
| 1.10 | Prometheus Metrics Export | ✅ Done | `api/routes/prometheus.py` — `GET /metrics` in Prometheus text exposition format |

### Migrations for Complexity 1
- `002_add_incidents_webhooks_slos.py` — incidents, webhook_configs, slos tables
- `003_add_synthetic_journeys_and_traces.py` — adds service_id to incidents; creates synthetic_journeys, trace_spans

### Tests for Complexity 1
- `test_incidents.py`, `test_slos.py`, `test_webhooks.py`

---

## Complexity 2 — AI and Advanced ✅ COMPLETE

| # | Feature | Status | Files |
|---|---------|--------|-------|
| 2.1 | AI Monitor Copilot | ✅ Done | `services/monitor_ai.py`, `services/llm_client.py`, `api/v1/ai.py` (POST /api/v1/ai/chat); frontend: `components/monitor-copilot.tsx`, `app/copilot/page.tsx` |
| 2.2 | Statistical Anomaly Detection | ✅ Done | `services/anomaly_detector.py` — Z-score with MIN_SAMPLES=30 cold-start guard; hooked into metric ingest |
| 2.3 | AI Alert Noise Reduction | ✅ Done | `services/alert_correlator.py` — LLM groups open alerts into incidents every 2 min; scheduled via APScheduler |
| 2.4 | AI Root Cause Analysis | ✅ Done | `services/rca_engine.py` — async RCA on incident create; stores in `incident.rca_summary`; frontend: `app/incidents/[id]/page.tsx` renders AI Analysis card |
| 2.5 | SLO Error Budget Forecasting | ✅ Done | `services/slo_forecaster.py` — pure-Python least-squares regression; `GET /api/v1/slos/{id}/status` includes forecast |
| 2.6 | AI Runbook Generation | ✅ Done | `services/runbook_generator.py`; `GET /api/v1/services/{id}/runbook` endpoint |
| 2.7 | Synthetic Monitoring | ✅ Done | `models/synthetic_journey.py`, `services/synthetic_runner.py`, `api/v1/synthetic.py` — CRUD + manual run; scheduled every 60s |
| 2.8 | Distributed Tracing Ingestion | ✅ Done | `models/trace_span.py`, `repos/trace_repo.py`, `api/v1/traces.py` — OTLP JSON ingest + query by trace_id |
| 2.9 | Capacity Planning Forecasts | ✅ Done | `GET /api/v1/metrics/forecast` — 30/60/90-day projection with configurable breach threshold |

### Frontend (Complexity 2)
- `frontend/src/app/incidents/page.tsx` — incidents list with Open/Resolved tabs
- `frontend/src/app/incidents/[id]/page.tsx` — incident detail with RCA card
- `frontend/src/app/copilot/page.tsx` — full-page AI chat with service selector
- `frontend/src/components/monitor-copilot.tsx` — floating chat widget on dashboard

---

## Implementation Timeline (Actual)

| Phase | Complexity | Status |
|-------|------------|--------|
| Phase 1 | 0 — Foundation | ✅ Complete (PR #2) |
| Phase 2 | 1 — Core Differentiators | ✅ Complete (this branch) |
| Phase 3 | 2 — AI and Advanced | ✅ Complete (this branch) |

---

## Architectural Constraints (Non-Negotiable)

1. All models use `Mapped[...]` + `mapped_column()` with `default=` (not `default_factory=`)
2. All models inherit from `app.models.base.Base`
3. All DB access goes through `app/repositories/` — no raw queries in routers
4. All routers use `Depends(get_db)` — no manual `AsyncSession` instantiation
5. All datetimes use `utc_now()` from `app.core.utils` — no timezone-aware datetimes in models
6. All new tables require an alembic migration before any test is written
7. All new endpoints require at least one pytest test
8. `NEXT_PUBLIC_API_URL` must never be hardcoded — always read from environment
9. Pre-built UI components in `frontend/src/components/ui/` must be used — no shadcn CLI
10. `pytest-asyncio==0.24.0` is pinned — do not upgrade

---

## Definition of Done ✅

- [x] All models created and imported in alembic `env.py` target metadata
- [x] Alembic migrations generated and applied successfully (001 → 003)
- [x] Repositories implement all required methods
- [x] All routers registered in `backend/app/api/main.py`
- [x] All endpoints return correct HTTP status codes (200, 201, 404, 422)
- [x] Pytest tests pass for all domain endpoints (66/66)
- [x] Tests added for synthetic journeys (`test_synthetic.py`) and distributed tracing (`test_traces.py`)
- [x] `grep -r "random()" backend/` returns zero results (no mock data)
- [x] `grep -r "print(" backend/app/` returns zero results (logging used everywhere)
- [x] Frontend reads from `NEXT_PUBLIC_API_URL` and renders real data
- [x] `dclaw-manifest.json` updated with all 21 features at `frontend/public/dclaw-manifest.json`
- [x] APScheduler running 4 background jobs (uptime, alert eval, alert correlation, synthetic)
- [x] Alert evaluator fires webhook dispatch on new alerts
- [x] AI services wired: LLM client → OpenRouter with Ollama fallback
- [x] Prometheus `/metrics` endpoint returns exposition format
- [x] CORS config valid (`allow_credentials` removed — incompatible with wildcard origins)
- [x] `.env.example` variable names match pydantic `Settings` fields
- [x] Backend Dockerfile: non-root `appuser` (already present)
- [x] Frontend Dockerfile: non-root `appuser` added to runner stage
- [x] `docker-compose.yml`: deprecated `version:` key removed
- [x] GitHub workflows: `build-backend.yml`, `build-frontend.yml`, `deploy.yml` added
- [x] Helm `ingress.yaml` template added
