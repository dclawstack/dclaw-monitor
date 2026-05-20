# DClaw Monitor

> System and service observability dashboard built on the DClaw Stack.

## What This Is

**DClaw Monitor** is a vertical SaaS application that provides real-time monitoring, alerting, and observability for systems and services running on the DClaw platform.

- **Backend:** FastAPI (Python 3.11) — port `8030`
- **Frontend:** Next.js 14 (App Router) — port `3030`
- **Database:** PostgreSQL 16 — `dclaw_monitor`
- **Base API Path:** `/api/v1`

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Python 3.11 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Frontend | Next.js 14 App Router |
| Styling | Tailwind CSS v3 |
| Containerisation | Docker + docker-compose |
| Orchestration | Helm / Kubernetes |
| CI | GitHub Actions |

## Quick Start

```bash
# Copy environment variables
cp .env.example .env

# Start all services
docker compose up -d

# Backend: http://localhost:8030
# Frontend: http://localhost:3030
# API docs: http://localhost:8030/docs
```

## Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.api.main:app --reload --port 8030
```

### Frontend

```bash
cd frontend
npm install
npm run dev   # starts on port 3030
```

### Database migrations

```bash
cd backend
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

### Tests

```bash
cd backend
pytest
```

## Project Structure

```
dclaw-monitor/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers
│   │   ├── core/         # config, database, utils
│   │   ├── models/       # SQLAlchemy models
│   │   ├── repositories/ # CRUD layer
│   │   ├── schemas/      # Pydantic v2 schemas
│   │   └── services/     # Business logic
│   ├── alembic/          # DB migrations
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/          # Next.js App Router pages
│       ├── components/ui/ # Pre-built UI components
│       └── lib/          # api.ts, utils.ts
├── helm/                 # Kubernetes Helm chart
├── docker-compose.yml
├── .env.example
├── AGENTS.md             # Agent development guide (read first)
├── PLAN-v1.2.md          # Feature backlog
└── REVISED-PRD.md        # Product requirements
```

## Agent Development

Read `AGENTS.md` before making any code changes. It is the source of truth for architecture rules, anti-patterns, and the feature workflow.

## Contributors

| Name | Email | Role |
|------|-------|------|
| Rajendra Machani | 01.r.machani@gmail.com | Project Lead |
