# DClaw Monitor — v1.2 Feature Roadmap

> Based on: Y Combinator vertical SaaS principles, trending GitHub repos (prometheus, grafana), AI product research (Datadog, New Relic, Honeycomb, Highlight.io)

## Pre-Flight Checklist

- [ ] `frontend/package-lock.json` committed after any `npm install` / dependency change
- [ ] `frontend/next-env.d.ts` exists and is committed
- [ ] `docker-compose.yml` healthchecks correct
- [ ] `frontend/Dockerfile` declares `ARG NEXT_PUBLIC_API_URL` before `RUN npm run build`

## v1.0 Feature Inventory (Current)

- [ ] Service/endpoint registry
- [ ] Uptime monitoring
- [ ] Alert rules
- [ ] Basic dashboard
- [ ] Real backend CRUD (no mocks)
- [ ] Docker + Helm deployment
- [ ] Alembic migrations
- [ ] Backend tests

---

## v1.2 Roadmap

### P0 — Must Have (Ship in v1.0, demo-ready)

#### 1. AI Monitor Copilot (SRE Assistant)
**Description:** AI assistant that interprets alerts, suggests remediation steps, and answers ops questions. "Why is latency spiking on API-Gateway?"
- **AI Angle:** Log/metric analysis + RAG over runbooks. Root cause suggestion.
- **Backend:** `/api/v1/ai/monitor-chat` endpoint. Telemetry ingestion.
- **Frontend:** AI panel with alert context and suggested fixes.
- **Files:** `backend/app/services/monitor_ai.py`, `frontend/src/components/monitor-copilot.tsx`

#### 2. Synthetic Monitoring & Uptime Checks
**Description:** Ping endpoints from multiple global locations. Track response time, status codes, SSL expiry.
- **Backend:** Distributed probe system. Check scheduler.
- **Frontend:** Global status map. Uptime percentage charts.
- **Files:** `backend/app/services/synthetic.py`

#### 3. Log Aggregation & Search
**Description:** Centralized log collection with full-text search, filters, and structured parsing.
- **Backend:** Log ingestion pipeline (Loki-style). Search index.
- **Frontend:** Log explorer with query builder. Live tail view.
- **Files:** `backend/app/services/logs.py`

#### 4. Alerting & Incident Management
**Description:** Multi-channel alerts (email, SMS, Slack, PagerDuty). Alert grouping, suppression, escalation.
- **Backend:** Alert routing engine. On-call rotation management.
- **Frontend:** Alert inbox. Incident timeline.
- **Files:** `backend/app/services/alerts.py`

### P1 — Should Have (v1.1–1.2)

#### 5. AI Anomaly Detection
**Description:** AI learns normal patterns and alerts on anomalies without static thresholds.
- **AI Angle:** Statistical anomaly detection + forecasting.
- **Backend:** ML pipeline for metric anomaly detection.
- **Frontend:** Anomaly overlay on metric charts.

#### 6. Distributed Tracing
**Description:** Trace requests across microservices. Identify latency bottlenecks.
- **Backend:** Trace ingestion (OpenTelemetry). Span correlation.
- **Frontend:** Flame graph visualization. Service dependency map.

#### 7. Custom Dashboards & Visualizations
**Description:** Drag-and-drop dashboard builder with charts, gauges, and tables.
- **Backend:** Dashboard persistence. Query engine.
- **Frontend:** Dashboard builder with widget library.

#### 8. SLO/SLA Tracking
**Description:** Define service level objectives. Track error budgets and burn rates.
- **Backend:** SLO calculation engine. Burn rate alerts.
- **Frontend:** SLO dashboard with error budget gauge.

### P2 — Could Have (v1.3+)

#### 9. AI Root Cause Analysis
**Description:** AI correlates metrics, logs, and traces to pinpoint root cause automatically.

#### 10. Chaos Engineering Monitoring
**Description:** Monitor resilience experiments and measure recovery metrics.

#### 11. Mobile App Performance Monitoring
**Description:** RUM (Real User Monitoring) for mobile apps with crash analytics.

#### 12. Cost-Aware Monitoring
**Description:** Correlate performance metrics with cloud spend per service.

---

## Implementation Priority

1. **Week 1–2:** AI Monitor Copilot (P0.1) + Synthetic Monitoring (P0.2)
2. **Week 3–4:** Log Aggregation (P0.3) + Alerting (P0.4)
3. **Week 5–6:** Anomaly Detection (P1.5) + Distributed Tracing (P1.6)
4. **Week 7–8:** Dashboard Builder (P1.7) + SLO Tracking (P1.8)
