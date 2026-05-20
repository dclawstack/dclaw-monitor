---
tags: [meta, prd, revised, swarm]
version: 2.3
date: 2026-05-16
app_id: monitor
app_name: DClaw Monitor
category: Observability
status: Future
---

# 📘 DClaw Monitor — Revised PRD v2.3

> **The single document every agent must read before writing code for this app.**
> Generated from DClaw Master PRD v2.2. Read the Master PRD first: https://raw.githubusercontent.com/dclawstack/dclaw-prd/main/DClaw-Master-PRD.md

---

## 1. Product Identity

| Field | Value |
|-------|-------|
| **App ID** | `monitor` |
| **Name** | DClaw Monitor |
| **Category** | Observability |
| **Tagline** | AI-powered alerting |
| **Color** | #3B82F6 |
| **Phase** | Future |
| **Port (Frontend Dev)** | 3030 |
| **Port (Backend Dev)** | 8030 |
| **Maturity Tier** | 🟡 Tier 2 — Partial |

---

## 2. Current State Assessment

### 2.1 Scaffold Status
| Component | Status | Notes |
|-----------|--------|-------|
| `frontend/` | ✅ | Next.js 14+ app |
| `backend/` | ✅ | FastAPI + SQLAlchemy 2.0 |
| `docs/` | ✅ | getting-started, guides, reference, releases |
| `helm/` | ✅ | K8s deployment manifests |
| `.github/workflows/` | ✅ | CI/CD + Claude integration |
| `AGENTS.md` | ✅ | Per-repo agent instructions |
| `PLAN-v1.2.md` | ✅ | Feature roadmap |
| `docker-compose.yml` | ✅ | Local dev stack |
| `tests/` | ✅ | pytest + pytest-asyncio |
| `alembic/` | ✅ | Database migrations |
| `dclaw-manifest.json` | ❌ | DPanel registration |

### 2.2 Code Maturity
| Metric | Value |
|--------|-------|
| Python source files (backend) | ~22 |
| TypeScript/TSX files (frontend) | ~16 |
| Total source files | ~38 |
| Tests | ✅ Present |
| Alembic migrations | ✅ Present |
| DPanel manifest | ❌ Missing |

### 2.3 Feature Maturity
- **P0 Foundation:** Partially implemented
- **P1 Platform:** Not yet started
- **P2 Vertical:** Not yet started

---

## 3. Gap Analysis

| # | Gap | Severity | Fix |
|---|-----|----------|-----|
| 1 | Missing `dclaw-manifest.json` | 🔴 | Create frontend/public/dclaw-manifest.json for DPanel |
| 2 | Partial implementation — needs more domain features | 🟡 | Expand backend services and frontend pages per P0 roadmap |

---

## 4. Sacred Architecture & Tech Stack

> **NON-NEGOTIABLE. Every DClaw product MUST use this exact stack.**

| Layer | Technology | Version |
|-------|------------|---------|
| **Frontend** | Next.js 14+ | App Router, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI | Pydantic v2, SQLAlchemy 2.0, asyncpg |
| **Database** | PostgreSQL 16 | CloudNativePG operator in K8s |
| **Vector DB** | Qdrant / pgvector | Only if RAG / semantic search |
| **Cache / Bus** | Redis | 7.x |
| **Object Storage** | MinIO | Latest |
| **Workflow** | Temporal.io | Only if automation/orchestration |
| **Auth** | Logto | JWT validation on all protected routes |
| **Billing** | Stripe | Metered or per-seat |
| **K8s Operator** | Go + controller-runtime | 0.18 |
| **LLM Local** | Ollama | Apple Silicon |
| **LLM Cloud** | OpenRouter + Kimi K2.5 | Fallback |
| **Monitoring** | Prometheus + Grafana | Latest |

### 4.1 Python Rules
- `ruff` formatting enforced
- Type hints on ALL public APIs
- `pydantic` v2 for schemas
- `sqlalchemy` 2.0 style (`Mapped`, `mapped_column`)
- `pytest` + `pytest-asyncio` for tests
- Functions < 50 lines
- No `print()` — use `structlog`

### 4.2 TypeScript / Next.js Rules
- Strict TypeScript (`strict: true`)
- Tailwind for ALL styling
- `cn()` utility for conditional classes
- No `any` without `// @ts-ignore`

### 4.3 Docker Standards
- Port mappings MUST match container listen port
- Healthchecks MUST use binaries present in base image
- `docker compose config` must pass before shipping
- Service type MUST be `ClusterIP`
- TLS required on all ingress

---

## 5. P0 Foundation Features (Must Have — Demo Ready)

> **Every P0 MUST include an AI Copilot per YC S25/W26 RFS.**

| # | Feature | Description | AI Component | Acceptance Criteria |
|---|---------|-------------|--------------|---------------------|
| P0.1 | **AI Monitor Copilot** | Detect anomalies, predict incidents, and suggest fixes. | Time-series anomaly detection + LLM root-cause analysis | Detect anomaly in <1min; predict incident 30min ahead |
| P0.2 | **Metrics Dashboard** | Collect and visualize metrics from apps, infrastructure, and business. | AI dashboard-layout optimization + insight extraction | 1000+ metrics; 20+ visualization types; custom formulas |
| P0.3 | **Log Management** | Centralized log aggregation with AI-powered search and pattern detection. | AI log-pattern clustering + error-classification | Ingest 1M logs/min; search in <1s; auto-classify errors |
| P0.4 | **Alerting & On-Call** | Smart alerting with escalation, suppression, and runbook linking. | AI alert-noise reduction + severity scoring | Reduce false positives 70%; auto-link runbooks |

---

## 6. P1 Platform Features (Should Have — v1.1–1.2)

| # | Feature | Description | AI Component | Acceptance Criteria |
|---|---------|-------------|--------------|---------------------|
| P1.1 | **Distributed Tracing** | Trace requests across microservices with latency breakdown. | AI latency-bottleneck identification + optimization suggestion | Trace 100% of requests; flame graphs; service map |
| P1.2 | **SLO Management** | Define, track, and alert on service-level objectives. | AI SLO-recommendation + error-budget forecasting | Track 50 SLOs; error-budget burn alerts; auto-adjust |
| P1.3 | **Incident Management** | Track incidents from detection to resolution with post-mortems. | AI incident-similarity detection + resolution-suggestion | Auto-create incident; suggest past fixes; track MTTR |
| P1.4 | **Integration** | Connect to Prometheus, Datadog, New Relic, and CloudWatch. | AI connector-health monitoring + metric-mapping | 20+ integrations; bi-directional sync; custom exporters |

---

## 7. P2 Vertical / Scale Features (Could Have — v1.3+)

| # | Feature | Description | AI Component | Acceptance Criteria |
|---|---------|-------------|--------------|---------------------|
| P2.1 | **AI Runbooks** | Auto-generate and execute runbooks for common incidents. | LLM runbook-generation + step-execution | Generate runbook from 5 incidents; execute automatically |
| P2.2 | **Capacity Planning** | Forecast resource needs based on growth and seasonality. | AI capacity-forecasting + optimization | Forecast 6 months; suggest scaling; cost estimate |
| P2.3 | **Synthetic Monitoring** | Simulate user journeys to detect downtime and slowdowns. | AI test-script generation from user behavior | Monitor 50 journeys; check every 60s; global locations |
| P2.4 | **Cost Monitoring** | Track and optimize observability infrastructure costs. | AI cost-anomaly detection + retention optimization | Track spend by source; suggest retention policies; alert on spikes |

---

## 8. Scaffold Checklist

Before marking this app "shipped", confirm:

- [ ] `frontend/` with Next.js 14+, Tailwind, shadcn/ui
- [ ] `backend/` with FastAPI, Pydantic v2, SQLAlchemy 2.0, asyncpg
- [ ] `docs/` with getting-started, guides, reference, releases, troubleshooting
- [ ] `helm/` with Chart.yaml, values.yaml, templates (deployment, service, ingress, cloudnativepg)
- [ ] `.github/workflows/` with build-backend.yml, build-frontend.yml, deploy.yml, claude.yml
- [ ] `frontend/public/dclaw-manifest.json` for DPanel registration
- [ ] `backend/tests/` with pytest + pytest-asyncio
- [ ] `backend/alembic/` with initial migration
- [ ] `Dockerfile` + `docker-compose.yml` with correct healthchecks
- [ ] Health endpoint at `/health` returning `{"status":"ok"}`
- [ ] `AGENTS.md` with per-repo instructions
- [ ] `PLAN-v1.2.md` with feature roadmap
- [ ] Port assigned from registry and documented
- [ ] No hardcoded secrets — use `.env.example` + K8s Secrets
- [ ] Non-root containers in Dockerfile

---

## 9. AI Copilot Mandate (YC S25/W26 Requirement)

Every DClaw app MUST have an AI Copilot as its first P0 feature. The copilot must:
1. Be contextually aware of the app's domain data
2. Use RAG over the app's knowledge base where applicable
3. Suggest next actions, not just answer questions
4. Be accessible from every page via floating chat or sidebar
5. Fall back to local Ollama when cloud is unavailable

---

## 10. Next Tasks for Vibe Coders

1. **Complete P0 features**: Finish any incomplete P0 backend services and frontend pages.
2. **Add missing scaffold**: Fill gaps identified above (docs, helm, tests, manifest, etc.).
3. **Start P1 features**: Implement the first 2 P1 features to deepen domain capability.
4. **Polish and integrate**: Ensure health endpoints, Docker builds, and DPanel manifest are production-ready.

---

## 11. Domain Research Notes

Inspired by Datadog, Grafana, New Relic, PagerDuty. AI observability reduces MTTR by 60%.

---

## 12. Links & Resources

| Resource | URL |
|----------|-----|
| **Master PRD** | https://raw.githubusercontent.com/dclawstack/dclaw-prd/main/DClaw-Master-PRD.md |
| **GitHub Org** | https://github.com/dclawstack |
| **DPanel** | https://dpanel.dclawstack.io |
| **Port Registry** | See `dclaw-platform/PORT_REGISTRY.md` |
| **App PRD Template** | Obsidian Vault → `00-META/📐 App PRD Template.md` |
| **Scaffold Source** | `dclaw-scaffold/` in DClaw-Stack |

---

*Revised PRD version: 2.3*
*Generated: 2026-05-16 by DClaw Stack Generator*
*Next review: When P0 features are complete or architecture changes*
