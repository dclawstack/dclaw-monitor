# DClaw Monitor — v1.2 Feature Roadmap

> **This document is the canonical implementation plan.** Do not proceed to coding until this plan is reviewed and up to date.

> **Stack:** FastAPI (port 8030) · Next.js 14 App Router (port 3030) · PostgreSQL (`dclaw_monitor`) · Base API path `/api/v1`

---

## Pre-Flight Checklist

Before writing any code, verify all of the following:

- [ ] `AGENTS.md` has been read in full
- [ ] `frontend/package-lock.json` is committed after any `npm install` or dependency change
- [ ] `frontend/next-env.d.ts` exists and is committed
- [ ] `docker-compose.yml` healthchecks use `python urllib.request.urlopen()` — NOT `curl`
- [ ] `frontend/Dockerfile` declares `ARG NEXT_PUBLIC_API_URL` before `RUN npm run build`
- [ ] All new models inherit from `Base` in `app.models.base` — NOT `declarative_base()`
- [ ] All new models use `Mapped[...]` + `mapped_column()` — NOT `default_factory=`
- [ ] All alembic migrations generated for every new model before tests run
- [ ] All tests use `localhost:5432` for PostgreSQL (CI maps port 5432 only)
- [ ] `pytest-asyncio==0.24.0` is pinned — do NOT upgrade
- [ ] `.github/workflows/ci.yml` is NOT deleted or modified
- [ ] Pre-built UI components in `frontend/src/components/ui/` are used — do NOT install shadcn CLI

---

## Current State (as of v1.1)

| Area | Status |
|------|--------|
| Health endpoint (`GET /api/v1/health`) | Implemented |
| `monitor.py` (mock data with `random()`) | Exists but NOT wired into `main.py` |
| Domain models (services, checks, alerts, metrics, logs) | None |
| Repositories | None |
| Alembic migrations | None (health only) |
| Tests | None for domain features |
| Frontend pages beyond scaffold | None |

**Critical gap:** The app has no real domain functionality. The mock `monitor.py` must be replaced with real models, repositories, and endpoints before any AI or advanced features are built.

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

## Complexity 0 — Foundation (Week 1)

These items are prerequisites for all higher-complexity work. Complete them in order.

### 0.1 Service Registry

**What:** `MonitoredService` model + full CRUD API.

**Why:** Every other feature (uptime checks, alerts, metrics, logs) is scoped to a service. This is the root entity.

**Backend files:**
- `backend/app/models/monitored_service.py` — fields: `id` (UUID), `name`, `url`, `description`, `is_active`, `created_at`, `updated_at`
- `backend/app/schemas/monitored_service.py` — `MonitoredServiceCreate`, `MonitoredServiceUpdate`, `MonitoredServiceRead` with `ConfigDict(from_attributes=True)`
- `backend/app/repositories/monitored_service_repo.py` — `list`, `get`, `create`, `update`, `delete`
- `backend/app/api/v1/services.py` — `GET /api/v1/services`, `POST /api/v1/services`, `GET /api/v1/services/{id}`, `PATCH /api/v1/services/{id}`, `DELETE /api/v1/services/{id}`

**Constraints:** Paginate `GET /api/v1/services` with `skip`/`limit`. Return 404 on missing resource. No mock data.

---

### 0.2 Uptime Check

**What:** `UptimeCheck` model + endpoint to record and list check results.

**Why:** Core uptime monitoring primitive. Feeds the dashboard status badges and uptime percentage calculation.

**Backend files:**
- `backend/app/models/uptime_check.py` — fields: `id` (UUID), `service_id` (FK → `monitored_services`, `ondelete="CASCADE"`), `checked_at`, `status` (enum: `up`/`down`/`timeout`), `response_time_ms` (nullable float), `status_code` (nullable int), `error_message` (nullable str)
- `backend/app/schemas/uptime_check.py` — `UptimeCheckCreate`, `UptimeCheckRead`
- `backend/app/repositories/uptime_check_repo.py` — `list_by_service`, `create`, `get_latest_by_service`
- `backend/app/api/v1/checks.py` — `POST /api/v1/checks`, `GET /api/v1/checks?service_id=&limit=`

**Constraints:** `checked_at` must be indexed. Use `utc_now()` from `app.core.utils` — no timezone-aware datetimes.

---

### 0.3 Alert Rules

**What:** `AlertRule` model + CRUD API.

**Why:** Defines the conditions under which an alert fires. Required by the Alert Evaluation Engine (1.2).

**Backend files:**
- `backend/app/models/alert_rule.py` — fields: `id` (UUID), `service_id` (FK, nullable, `ondelete="SET NULL"`), `name`, `metric_name`, `condition` (enum: `gt`/`lt`/`eq`), `threshold` (float), `window_seconds` (int), `severity` (enum: `info`/`warning`/`critical`), `is_active`, `created_at`
- `backend/app/schemas/alert_rule.py` — `AlertRuleCreate`, `AlertRuleUpdate`, `AlertRuleRead`
- `backend/app/repositories/alert_rule_repo.py` — `list`, `get`, `create`, `update`, `delete`, `list_active`
- `backend/app/api/v1/alert_rules.py` — full CRUD at `/api/v1/alert-rules`

---

### 0.4 Alerts

**What:** `Alert` model + list/acknowledge/resolve endpoints.

**Why:** Surfaces triggered alert conditions to users and feeds the Alert Inbox UI (1.9).

**Backend files:**
- `backend/app/models/alert.py` — fields: `id` (UUID), `rule_id` (FK → `alert_rules`, `ondelete="SET NULL"`, nullable), `service_id` (FK, nullable), `title`, `body`, `severity`, `status` (enum: `firing`/`acknowledged`/`resolved`), `fired_at`, `acknowledged_at` (nullable), `resolved_at` (nullable)
- `backend/app/schemas/alert.py` — `AlertRead`, `AlertAcknowledge`, `AlertResolve`
- `backend/app/repositories/alert_repo.py` — `list` (filterable by status/severity/service), `get`, `create`, `acknowledge`, `resolve`
- `backend/app/api/v1/alerts.py` — `GET /api/v1/alerts`, `GET /api/v1/alerts/{id}`, `POST /api/v1/alerts/{id}/acknowledge`, `POST /api/v1/alerts/{id}/resolve`

**Constraints:** Paginate list. Index on `status` and `fired_at`.

---

### 0.5 Metric Ingestion

**What:** `MetricSample` model + ingest and query endpoints.

**Why:** Core time-series storage. Powers anomaly detection (2.2) and metric charts (1.8).

**Backend files:**
- `backend/app/models/metric_sample.py` — fields: `id` (UUID), `service_id` (FK, nullable, `ondelete="SET NULL"`), `metric_name`, `value` (float), `labels` (JSONB, nullable), `sampled_at`
- `backend/app/schemas/metric_sample.py` — `MetricSampleIngest`, `MetricSampleRead`, `MetricSampleBatchIngest` (list of samples)
- `backend/app/repositories/metric_sample_repo.py` — `ingest`, `ingest_batch`, `query` (filter by service, metric name, time range)
- `backend/app/api/v1/metrics.py` — `POST /api/v1/metrics` (single or batch), `GET /api/v1/metrics?service_id=&metric_name=&from=&to=&limit=`

**Constraints:** Composite index on `(service_id, metric_name, sampled_at DESC)`. `sampled_at` must be indexed. Paginate queries.

---

### 0.6 Log Ingestion

**What:** `LogEntry` model + ingest and query endpoints.

**Why:** Centralized log storage needed for full-text search (1.4) and AI root cause analysis (2.4).

**Backend files:**
- `backend/app/models/log_entry.py` — fields: `id` (UUID), `service_id` (FK, nullable, `ondelete="SET NULL"`), `level` (enum: `debug`/`info`/`warning`/`error`/`critical`), `message`, `attributes` (JSONB, nullable), `logged_at`
- `backend/app/schemas/log_entry.py` — `LogEntryIngest`, `LogEntryRead`, `LogEntryBatchIngest`
- `backend/app/repositories/log_entry_repo.py` — `ingest`, `ingest_batch`, `query` (filter by service, level, time range)
- `backend/app/api/v1/logs.py` — `POST /api/v1/logs`, `GET /api/v1/logs?service_id=&level=&from=&to=&limit=`

**Constraints:** Index on `(service_id, level, logged_at DESC)`. Paginate queries.

---

### 0.7 Replace Mock Endpoints

**What:** Delete all `random()` calls from `monitor.py`. Wire real repositories into any endpoint that previously returned mock data.

**Why:** YC judges will test the demo. Fake data is disqualifying. Contradicts `NO MOCK DATA` rule in `AGENTS.md`.

**Files to change:**
- `backend/app/services/monitor.py` — remove all `import random` and random-value generation; replace with repository calls
- `backend/app/api/main.py` — ensure all routers from 0.1–0.6 are registered

**Constraints:** After this task, `grep -r "random()" backend/` must return zero results.

---

### 0.8 Alembic Migration

**What:** Generate and commit a single initial migration covering all 6 models from 0.1–0.6.

**Why:** Without a migration, the database schema never gets created; all endpoint tests fail.

**Steps:**
1. Ensure all 6 models are imported in `alembic/env.py` target metadata
2. Run `alembic revision --autogenerate -m "initial_schema"`
3. Verify the generated migration creates all tables and indexes
4. Run `alembic upgrade head` and confirm tables exist

**Constraints:** Migration must be committed to the repo. Never edit autogenerated migration UUIDs.

---

### 0.9 Test Coverage

**What:** `pytest` tests for all 6 resource endpoints (services, checks, alert-rules, alerts, metrics, logs).

**Why:** CI gate. Ensures no regression as AI and advanced features are layered on.

**Files:**
- `backend/tests/test_services.py`
- `backend/tests/test_checks.py`
- `backend/tests/test_alert_rules.py`
- `backend/tests/test_alerts.py`
- `backend/tests/test_metrics.py`
- `backend/tests/test_logs.py`

**Constraints:**
- Use `httpx.AsyncClient` with `ASGITransport`
- Override `get_db` in `conftest.py` with a test `AsyncSession`
- Use `localhost:5432` (CI requirement)
- Mark all test functions with `@pytest.mark.asyncio`
- Cover: create, read list, read single, update (where applicable), delete (where applicable), 404 on missing

---

### 0.10 dclaw-manifest.json

**What:** Create `frontend/public/dclaw-manifest.json` for DPanel registration.

**Why:** Required for DClaw hub integration. Without it, the app does not appear in the DPanel app switcher.

**File:** `frontend/public/dclaw-manifest.json`

```json
{
  "app_id": "dclaw-monitor",
  "name": "DClaw Monitor",
  "description": "AI-native observability: uptime, metrics, logs, and anomaly detection.",
  "version": "1.2.0",
  "backend_port": 8030,
  "frontend_port": 3030,
  "database": "dclaw_monitor",
  "base_api_path": "/api/v1",
  "primary_color": "#ef4444"
}
```

---

### 0.11 Dashboard Overview Page

**What:** Frontend home page (`/`) showing real data: service list with status badges, open alert count, and overall system health indicator.

**Why:** First thing a demo evaluator sees. Must show live data from the API — not placeholders.

**Frontend files:**
- `frontend/src/lib/api.ts` — add typed fetch functions: `getServices()`, `getAlerts(status='firing')`, `getLatestChecks()`
- `frontend/src/app/page.tsx` — server component fetching services + firing alerts; render using `Card`, `Badge`, `Table` from pre-built UI

**Constraints:** Use `NEXT_PUBLIC_API_URL` from environment. No hardcoded `localhost`. Render a `Badge` with `destructive` variant for `down` services, `default` for `up`.

---

### 0.12 Service Detail Page

**What:** Per-service page (`/services/[id]`) showing uptime history (last 20 checks) and latest metric values.

**Why:** Demonstrates real time-series data and drill-down capability to investors.

**Frontend files:**
- `frontend/src/app/services/[id]/page.tsx` — fetch service detail + recent checks + recent metrics; render uptime table and metric list
- `frontend/src/lib/api.ts` — add `getService(id)`, `getChecks(serviceId)`, `getMetrics(serviceId)`

---

## Complexity 1 — Core Differentiators (Week 2)

These features differentiate DClaw Monitor from a basic health-check tool.

### 1.1 Uptime Check Scheduler

**What:** APScheduler background worker that automatically pings all active `MonitoredService` URLs on a configurable interval and writes `UptimeCheck` records.

**Why:** Without automation, uptime checks must be POSTed manually. The scheduler is what makes this a real monitor, not a CRUD app.

**Backend files:**
- `backend/app/services/scheduler.py` — APScheduler `AsyncIOScheduler`, job: `run_uptime_checks()`
- `backend/app/services/uptime_worker.py` — async HTTP GET with `httpx`, write result via `UptimeCheckRepo`
- `backend/app/api/main.py` — start/stop scheduler in `lifespan` handler

**Constraints:** Default interval: 60 seconds. Configurable via `CHECK_INTERVAL_SECONDS` in `core/config.py`. Do not block the event loop — use `asyncio` + `httpx.AsyncClient`. Handle connection errors and timeouts gracefully (write `status=timeout` or `status=down`).

---

### 1.2 Alert Evaluation Engine

**What:** Background task that reads recent `MetricSample` records, evaluates them against active `AlertRule` records, and auto-creates `Alert` records when conditions are met.

**Why:** This is the core of an alerting system. Without it, users must manually watch metrics — which defeats the product.

**Backend files:**
- `backend/app/services/alert_evaluator.py` — for each active rule: fetch samples in `window_seconds`, aggregate (mean/last), compare against threshold, create alert if condition met and no active alert exists for this rule

**Constraints:** Prevent duplicate firing alerts — check for existing `status=firing` alert for the same `rule_id` before creating. Schedule evaluation every 30 seconds via the APScheduler from 1.1.

---

### 1.3 Incident Model

**What:** `Incident` model + CRUD + auto-creation on critical alert.

**Why:** Incidents are the unit of on-call work. MTTR (Mean Time to Resolution) is a key SRE metric investors understand.

**Backend files:**
- `backend/app/models/incident.py` — fields: `id` (UUID), `title`, `severity`, `status` (enum: `open`/`investigating`/`resolved`), `opened_at`, `resolved_at` (nullable), `mttr_seconds` (nullable int, computed on resolve), `alert_ids` (JSONB array of UUIDs)
- `backend/app/schemas/incident.py`
- `backend/app/repositories/incident_repo.py`
- `backend/app/api/v1/incidents.py` — CRUD + `POST /api/v1/incidents/{id}/resolve`

**Constraints:** On resolve, compute `mttr_seconds = (resolved_at - opened_at).total_seconds()`. Index on `status` and `opened_at`.

---

### 1.4 Log Full-Text Search

**What:** Extend `GET /api/v1/logs` with `q` (search query) parameter using PostgreSQL `ILIKE`.

**Why:** Operators need to grep logs by error message. This is table-stakes for log management.

**Backend files:**
- `backend/app/repositories/log_entry_repo.py` — add `search_query: str | None` parameter; apply `LogEntry.message.ilike(f'%{q}%')` when set
- `backend/app/api/v1/logs.py` — expose `q` query param

**Constraints:** Sanitize input — do not allow raw SQL injection via `q`. Apply `ILIKE` only to `message` column. Paginate results.

---

### 1.5 Metrics Time-Series Aggregation

**What:** Add `window` query parameter to `GET /api/v1/metrics` for bucketed aggregation (e.g., `1m`, `5m`, `1h`).

**Why:** Raw samples are too noisy for charting. Bucketed averages are what frontend charts need.

**Backend files:**
- `backend/app/repositories/metric_sample_repo.py` — add `aggregate_by_window(service_id, metric_name, from_ts, to_ts, window_seconds)` using `date_trunc` or integer epoch bucketing via SQLAlchemy `func`
- `backend/app/api/v1/metrics.py` — expose `window` param (`1m`=60, `5m`=300, `1h`=3600); return list of `{bucket: datetime, avg: float, min: float, max: float}`

---

### 1.6 Webhook Notifications

**What:** When an `Alert` is created with status `firing`, POST a notification payload to configured webhook URLs (Slack, Discord, or generic HTTP).

**Why:** Alerting is useless without delivery. Slack/Discord webhooks are the fastest path to demonstrating end-to-end alert flow in a demo.

**Backend files:**
- `backend/app/models/webhook_config.py` — fields: `id`, `name`, `url`, `secret` (nullable), `is_active`, `event_types` (JSONB list: `alert.firing`, `incident.opened`, etc.)
- `backend/app/services/webhook_dispatcher.py` — async POST via `httpx`, retry once on failure, log result
- Wire into `alert_evaluator.py`: after creating alert, dispatch webhook

**Constraints:** Never expose webhook secret in API responses. Mask as `***` in read schemas.

---

### 1.7 SLO Model

**What:** `SLO` model defining a service level objective + background computation of error budget and burn rate.

**Why:** SLOs are the language of modern SRE. Showing error budget burn rate in a demo is a strong signal of product sophistication.

**Backend files:**
- `backend/app/models/slo.py` — fields: `id`, `service_id` (FK), `name`, `target_percent` (float, e.g. 99.9), `window_days` (int), `metric_name`, `good_condition` (enum: `lt`/`gt`), `good_threshold` (float), `created_at`
- `backend/app/schemas/slo.py`
- `backend/app/repositories/slo_repo.py` — `compute_error_budget(slo_id)`: count good vs total samples in window, return budget remaining and burn rate
- `backend/app/api/v1/slos.py` — CRUD + `GET /api/v1/slos/{id}/status` returning `{target, current_percent, error_budget_remaining, burn_rate}`

---

### 1.8 Frontend Metrics Charts

**What:** SVG sparkline charts on the service detail page showing metric history (no external chart library required).

**Why:** Visual time-series data is what investors and users look for first in a monitoring tool.

**Frontend files:**
- `frontend/src/components/sparkline.tsx` — pure SVG component accepting `{ data: number[], width: number, height: number, color?: string }`
- `frontend/src/app/services/[id]/page.tsx` — fetch aggregated metric data; render `Sparkline` per metric name

**Constraints:** Do NOT install chart libraries (recharts, chart.js, etc.) unless already in `package.json`. Use raw SVG path generation.

---

### 1.9 Alert Inbox UI

**What:** Frontend page (`/alerts`) listing all firing alerts with acknowledge and resolve actions.

**Why:** The Alert Inbox is the primary daily-use surface for on-call engineers. Required for demo flow.

**Frontend files:**
- `frontend/src/app/alerts/page.tsx` — fetch firing alerts; render using `Table`, `Badge` (severity), action buttons
- `frontend/src/lib/api.ts` — add `acknowledgeAlert(id)`, `resolveAlert(id)` via `POST`

**Constraints:** After acknowledge/resolve, optimistically update UI or refetch. Show `fired_at` as relative time (e.g., "3 minutes ago").

---

### 1.10 Prometheus Metrics Export

**What:** `GET /metrics` endpoint returning all recent metric samples in Prometheus text exposition format.

**Why:** Prometheus compatibility means zero migration cost for existing infrastructure teams. This is a major adoption driver and competitive differentiator.

**Backend files:**
- `backend/app/api/routes/prometheus.py` — query last sample per `(service_id, metric_name)` from `MetricSampleRepo`; format as `metric_name{service="..."} value timestamp`
- Register at `/metrics` (not `/api/v1/metrics` — Prometheus scrape convention uses root path)

**Constraints:** Content-Type must be `text/plain; version=0.0.4`. No authentication on this endpoint by default (Prometheus scrapers expect open access or token-based, not session auth).

---

## Complexity 2 — AI and Advanced (Week 3+)

These features are the YC pitch differentiators. Build on top of a working Complexity 0 and 1 foundation.

### 2.1 AI Monitor Copilot

**What:** Conversational SRE assistant. User asks "Why is latency spiking on api-gateway?" and the LLM answers using live alert and log context.

**Why:** This is the primary AI differentiator and the centerpiece of the YC demo. "AI-native from day 0" requires this to be real, not a fake chat window.

**Backend files:**
- `backend/app/services/monitor_ai.py` — build context: fetch firing alerts + last 50 error logs for named service; call OpenRouter (default) or Ollama (fallback) via `httpx`; stream response
- `backend/app/api/v1/ai.py` — `POST /api/v1/ai/chat` accepting `{ message: str, service_id?: UUID }`; return streaming response
- `backend/app/core/config.py` — add `LLM_PROVIDER` (`openrouter`/`ollama`), `LLM_MODEL`, `OPENROUTER_API_KEY`, `OLLAMA_BASE_URL`

**Frontend files:**
- `frontend/src/components/monitor-copilot.tsx` — chat panel with message history, streaming text render, service selector
- `frontend/src/app/copilot/page.tsx`

**Constraints:** Must work with `LLM_PROVIDER=ollama` and no internet access (local LLM fallback). Never send raw log data containing PII without filtering. Streaming via `StreamingResponse`.

---

### 2.2 Statistical Anomaly Detection

**What:** Z-score rolling baseline per metric. Auto-create an `Alert` when a new sample deviates more than 3 standard deviations from the rolling mean.

**Why:** Static thresholds miss subtle anomalies and generate false positives. Z-score detection is the minimum viable "AI anomaly detection" claim and is mathematically defensible in a YC interview.

**Backend files:**
- `backend/app/services/anomaly_detector.py` — for each new ingested metric sample: fetch last N samples for same `(service_id, metric_name)`; compute rolling mean and stddev; if `|new_value - mean| > 3 * stddev`, create anomaly alert via `AlertRepo`
- Hook into `POST /api/v1/metrics` after successful ingest (async, non-blocking)

**Constraints:** Require minimum 30 samples before anomaly detection activates (cold start protection). Use `statistics.mean` and `statistics.stdev` from stdlib — no ML framework dependency.

---

### 2.3 AI Alert Noise Reduction

**What:** LLM groups correlated firing alerts into a single incident, suppressing redundant notifications.

**Why:** Alert fatigue is the core pain point in the YC pitch. Demonstrating that DClaw Monitor reduces noise (not just generates alerts) is a direct answer to "how are you different from Datadog?"

**Backend files:**
- `backend/app/services/alert_correlator.py` — on each new alert creation: fetch all firing alerts in last 5 minutes; send list to LLM with prompt: "Group these alerts into incidents. Return JSON array of groups with a shared root cause label."; create or link `Incident` records per group
- Schedule via APScheduler every 2 minutes

**Constraints:** LLM output must be validated as JSON before acting on it. Use `json.loads` with try/except — never `eval`. Fallback: if LLM fails, create one incident per alert (no noise reduction, but no crash).

---

### 2.4 AI Root Cause Analysis

**What:** On `Incident` creation, automatically query logs and metrics from the past 30 minutes and ask the LLM to identify the root cause.

**Why:** Root cause analysis at 3 AM is the highest-value SRE task. Automating it is the strongest product claim and the best demo moment.

**Backend files:**
- `backend/app/services/rca_engine.py` — triggered on `Incident` creation: fetch error logs (last 30 min, affected service), fetch anomalous metric samples (last 30 min); build prompt; call LLM; store result in `Incident.rca_summary` (new nullable text column)
- Add alembic migration for `rca_summary` column on `incidents`

**Frontend files:**
- `frontend/src/app/incidents/[id]/page.tsx` — render `rca_summary` in a highlighted "AI Analysis" card if present

---

### 2.5 SLO Error Budget Forecasting

**What:** Linear regression on error rate trend to predict when the current SLO window's error budget will be exhausted.

**Why:** "Your error budget runs out in 4 days at current burn rate" is a concrete, actionable insight that no static dashboard provides. Strong demo narrative for engineering leaders.

**Backend files:**
- `backend/app/services/slo_forecaster.py` — for each SLO: fetch error rate samples over past 7 days; fit linear regression (use `numpy` if available, else pure Python least-squares); extrapolate to budget exhaustion date
- `backend/app/api/v1/slos.py` — extend `GET /api/v1/slos/{id}/status` to include `forecast: { budget_exhaustion_date: datetime | null, confidence: float }`

---

### 2.6 AI Runbook Generation

**What:** LLM generates a step-by-step remediation runbook from past resolved incidents for the same service.

**Why:** Runbooks encode institutional knowledge. Generating them automatically from incident history is a unique feature that reduces on-call ramp time.

**Backend files:**
- `backend/app/services/runbook_generator.py` — fetch last 5 resolved incidents for service; build prompt with titles + RCA summaries; ask LLM to generate a runbook; return as markdown string
- `backend/app/api/v1/services.py` — add `GET /api/v1/services/{id}/runbook` endpoint

**Frontend files:**
- `frontend/src/app/services/[id]/page.tsx` — "Generate Runbook" button that fetches and renders the markdown runbook in a `Dialog`

---

### 2.7 Synthetic Monitoring

**What:** Background scheduler runs HTTP request sequences (user journeys) against configured endpoints and records results as `UptimeCheck` records with journey labels.

**Why:** Single-endpoint pings miss application-layer failures. Journey monitoring catches checkout flow breakage, login failures, and API workflow regressions.

**Backend files:**
- `backend/app/models/synthetic_journey.py` — fields: `id`, `name`, `service_id`, `steps` (JSONB: list of `{method, url, headers, body, expected_status}`), `interval_seconds`, `is_active`
- `backend/app/services/synthetic_runner.py` — execute journey steps in sequence via `httpx`; write one `UptimeCheck` per journey run with `status` = pass/fail; abort journey on first step failure
- `backend/app/api/v1/synthetic.py` — CRUD for `SyntheticJourney`

---

### 2.8 Distributed Tracing Ingestion

**What:** OpenTelemetry span ingestion endpoint. Assembles spans into traces and stores them for query.

**Why:** Distributed tracing is table-stakes for microservices observability. Prometheus-compatible ingestion (1.10) + OTLP tracing ingestion together cover the full observability pillars: metrics, logs, traces.

**Backend files:**
- `backend/app/models/trace_span.py` — fields: `id` (UUID), `trace_id` (str), `span_id` (str), `parent_span_id` (nullable str), `service_id` (FK, nullable), `operation_name`, `start_time`, `end_time`, `duration_ms` (float), `status` (enum: `ok`/`error`/`unset`), `attributes` (JSONB)
- `backend/app/api/v1/traces.py` — `POST /api/v1/traces/ingest` (OTLP JSON format), `GET /api/v1/traces?trace_id=`, `GET /api/v1/traces/{trace_id}/spans`

**Constraints:** Index on `(trace_id, start_time)`. Accept OTLP JSON format (not protobuf) for simplicity.

---

### 2.9 Capacity Planning Forecasts

**What:** Extrapolate metric trends 30, 60, and 90 days forward using linear regression on historical samples.

**Why:** Engineering leaders make infrastructure purchasing decisions based on capacity forecasts. "Your database disk fills in 47 days" is a high-value, high-urgency insight that justifies $50k+/year spend.

**Backend files:**
- `backend/app/services/capacity_planner.py` — for a given `(service_id, metric_name)`: fetch all samples in last 30 days; fit linear trend; extrapolate to 30/60/90-day projected values; flag if any projection exceeds a configurable threshold
- `backend/app/api/v1/metrics.py` — add `GET /api/v1/metrics/forecast?service_id=&metric_name=` returning `{ p30: float, p60: float, p90: float, trend_slope: float, breach_day: int | null }`

---

## Implementation Timeline

| Week | Complexity | Items | Goal |
|------|------------|-------|------|
| Week 1 | 0 | 0.1 → 0.12 | Working CRUD API + DB schema + basic dashboard. Demo-safe foundation. |
| Week 2 | 1 | 1.1 → 1.10 | Automated checks, alert evaluation, Prometheus export. Product is a real monitor. |
| Week 3 | 2 | 2.1 → 2.4 | AI Copilot, anomaly detection, noise reduction, RCA. YC pitch differentiators live. |
| Week 4 | 2 | 2.5 → 2.9 | Forecasting, runbooks, synthetic monitoring, tracing. Full observability pillars. |

---

## Architectural Constraints (Non-Negotiable)

These rules apply to every item in this plan. Violating them will break CI or cause data loss.

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

## Definition of Done

A feature is complete when:

- [ ] Model created and imported in alembic `env.py` target metadata
- [ ] Alembic migration generated and applied successfully
- [ ] Repository implements all required methods
- [ ] Router registered in `backend/app/api/main.py`
- [ ] All endpoints return correct HTTP status codes (200, 201, 404, 422)
- [ ] Pytest tests pass for all new endpoints
- [ ] `docker compose up -d` starts cleanly with no errors
- [ ] `grep -r "random()" backend/` returns zero results (no mock data)
- [ ] Frontend (if applicable) reads from `NEXT_PUBLIC_API_URL` and renders real data

---

> **Do not proceed to coding until this plan is reviewed, updated with any project-specific changes, and this notice is removed or checked off.**
