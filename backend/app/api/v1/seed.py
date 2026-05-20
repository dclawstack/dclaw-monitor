import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.core.database import get_db
from app.models.service import MonitoredService
from app.models.check import UptimeCheck
from app.models.alert import AlertRule, Alert
from app.models.metric import MetricSample
from app.models.log import LogEntry
from app.models.incident import Incident
from app.models.slo import SLO

router = APIRouter()

_SERVICES = [
    {"name": "API Gateway", "url": "https://api.example.com/health", "description": "Public-facing API gateway routing all client traffic", "status": "healthy", "interval_seconds": 30},
    {"name": "Auth Service", "url": "https://auth.example.com/health", "description": "JWT authentication and session management service", "status": "healthy", "interval_seconds": 60},
    {"name": "Payment Service", "url": "https://payments.example.com/health", "description": "Stripe integration and transaction processing", "status": "degraded", "interval_seconds": 60},
    {"name": "Notification Service", "url": "https://notify.example.com/health", "description": "Email, SMS, and push notification dispatcher", "status": "healthy", "interval_seconds": 120},
    {"name": "Database Proxy", "url": "https://dbproxy.example.com/health", "description": "PgBouncer connection pooler for PostgreSQL", "status": "down", "interval_seconds": 30},
    {"name": "Frontend CDN", "url": "https://cdn.example.com/health", "description": "Static asset delivery via Cloudflare CDN", "status": "healthy", "interval_seconds": 300},
]


def _ago(minutes: int = 0, hours: int = 0, days: int = 0) -> datetime:
    return datetime.utcnow() - timedelta(minutes=minutes, hours=hours, days=days)


@router.post("")
async def seed_data(db: AsyncSession = Depends(get_db)):
    rng = random.Random(42)

    # Services
    services = []
    for s in _SERVICES:
        svc = MonitoredService(**s, is_active=True)
        db.add(svc)
        services.append(svc)
    await db.flush()

    api_svc, auth_svc, pay_svc, notify_svc, db_svc, cdn_svc = services

    # Uptime checks — 20 checks per service spanning last 24h
    check_statuses = {
        api_svc.id: (["up"] * 18 + ["timeout", "up"], [45, 52, 48, 41, 60, 55, 49, 43, 51, 47, 44, 53, 46, 50, 42, 48, 1200, 55, 49, 44]),
        auth_svc.id: (["up"] * 20, [120, 115, 118, 122, 119, 121, 116, 123, 117, 120, 118, 115, 122, 119, 121, 116, 120, 118, 121, 117]),
        pay_svc.id: (["up"] * 14 + ["error", "up", "up", "error", "up", "up"], [800, 750, 820, 900, 780, 810, 760, 840, 770, 830, 2100, 1900, 1800, 850, None, 750, 780, None, 800, 790]),
        notify_svc.id: (["up"] * 20, [200, 195, 210, 205, 198, 202, 208, 196, 203, 207, 200, 195, 201, 204, 199, 203, 198, 206, 201, 200]),
        db_svc.id: (["up"] * 12 + ["down"] * 8, [5, 6, 5, 7, 6, 5, 6, 5, 7, 6, 5, 6, None, None, None, None, None, None, None, None]),
        cdn_svc.id: (["up"] * 20, [8, 7, 9, 8, 7, 8, 9, 7, 8, 7, 9, 8, 7, 8, 9, 7, 8, 7, 8, 9]),
    }

    for svc_id, (statuses, latencies) in check_statuses.items():
        for i, (st, lat) in enumerate(zip(statuses, latencies)):
            code = 200 if st == "up" else (504 if st == "timeout" else 500)
            err = None if st == "up" else ("Request timeout" if st == "timeout" else "Connection refused")
            db.add(UptimeCheck(
                service_id=svc_id,
                status=st,
                latency_ms=lat,
                status_code=code if st != "down" else None,
                error=err,
                checked_at=_ago(minutes=i * 72),
            ))

    # Alert rules
    rules = [
        AlertRule(name="High Latency — API Gateway", service_id=api_svc.id, metric_name="latency_ms", operator="gt", threshold=500, severity="warning", is_active=True),
        AlertRule(name="Critical Latency — Payment", service_id=pay_svc.id, metric_name="latency_ms", operator="gt", threshold=1500, severity="critical", is_active=True),
        AlertRule(name="Error Rate Spike", service_id=pay_svc.id, metric_name="error_rate", operator="gt", threshold=5.0, severity="critical", is_active=True),
        AlertRule(name="DB Proxy Down", service_id=db_svc.id, metric_name="status", operator="eq", threshold=0, severity="critical", is_active=True),
        AlertRule(name="Auth CPU High", service_id=auth_svc.id, metric_name="cpu_usage", operator="gt", threshold=80, severity="warning", is_active=True),
        AlertRule(name="CDN Cache Miss Rate", service_id=cdn_svc.id, metric_name="cache_miss_rate", operator="gt", threshold=30, severity="info", is_active=True),
    ]
    for r in rules:
        db.add(r)
    await db.flush()

    # Alerts
    alerts = [
        Alert(rule_id=rules[3].id, service_id=db_svc.id, title="Database Proxy is DOWN", message="dclaw-dbproxy failed 3 consecutive health checks. Connection refused on port 5432.", severity="critical", status="open", fired_at=_ago(hours=4)),
        Alert(rule_id=rules[2].id, service_id=pay_svc.id, title="Payment Error Rate > 5%", message="Error rate reached 8.3% over last 15 min. Transaction failures increasing.", severity="critical", status="acknowledged", fired_at=_ago(hours=6)),
        Alert(rule_id=rules[1].id, service_id=pay_svc.id, title="Payment Latency Critical", message="P99 latency at 2100ms, SLO breach imminent. Threshold 1500ms exceeded.", severity="critical", status="resolved", fired_at=_ago(hours=8), resolved_at=_ago(hours=7)),
        Alert(rule_id=rules[0].id, service_id=api_svc.id, title="API Gateway Timeout Spike", message="Timeout rate 10% over last 5 min. Upstream service degraded.", severity="warning", status="resolved", fired_at=_ago(hours=2), resolved_at=_ago(hours=1, minutes=45)),
        Alert(rule_id=rules[4].id, service_id=auth_svc.id, title="Auth Service CPU Elevated", message="CPU usage at 82% for 10 minutes. Token validation latency increasing.", severity="warning", status="open", fired_at=_ago(hours=1)),
        Alert(rule_id=rules[5].id, service_id=cdn_svc.id, title="CDN Cache Miss Rate High", message="Cache miss rate at 34% — origin servers under increased load.", severity="info", status="resolved", fired_at=_ago(days=1), resolved_at=_ago(hours=20)),
    ]
    for a in alerts:
        db.add(a)
    await db.flush()

    # Incidents
    incidents = [
        Incident(
            title="[P1] Database Proxy Total Outage",
            severity="critical",
            status="open",
            service_id=db_svc.id,
            opened_at=_ago(hours=4),
            alert_ids=[str(alerts[0].id)],
            rca_summary=None,
        ),
        Incident(
            title="[P2] Payment Service Degradation",
            severity="high",
            status="open",
            service_id=pay_svc.id,
            opened_at=_ago(hours=6),
            alert_ids=[str(alerts[1].id), str(alerts[2].id)],
            rca_summary="Suspected memory leak in payment processor after v2.4.1 deploy. Rollback initiated.",
        ),
        Incident(
            title="[P3] API Gateway Timeout Spike — Resolved",
            severity="warning",
            status="resolved",
            service_id=api_svc.id,
            opened_at=_ago(hours=2),
            resolved_at=_ago(hours=1, minutes=40),
            mttr_seconds=1200,
            alert_ids=[str(alerts[3].id)],
            rca_summary="Upstream auth service CPU spike caused request queuing. Auto-scaled and recovered.",
        ),
        Incident(
            title="[P4] CDN Cache Miss Rate — Resolved",
            severity="low",
            status="resolved",
            service_id=cdn_svc.id,
            opened_at=_ago(days=1),
            resolved_at=_ago(hours=20),
            mttr_seconds=14400,
            alert_ids=[str(alerts[5].id)],
            rca_summary="Stale cache after assets deployment. Purge triggered and TTLs adjusted.",
        ),
    ]
    for inc in incidents:
        db.add(inc)

    # SLOs
    slos = [
        SLO(service_id=api_svc.id, name="API Gateway Availability", target_percent=99.9, window_days=30, metric_name="status", good_condition="eq", good_threshold=1.0),
        SLO(service_id=api_svc.id, name="API Gateway Latency P99 < 500ms", target_percent=99.5, window_days=7, metric_name="latency_ms", good_condition="lt", good_threshold=500),
        SLO(service_id=auth_svc.id, name="Auth Service Availability", target_percent=99.99, window_days=30, metric_name="status", good_condition="eq", good_threshold=1.0),
        SLO(service_id=pay_svc.id, name="Payment Success Rate", target_percent=99.5, window_days=7, metric_name="error_rate", good_condition="lt", good_threshold=0.5),
        SLO(service_id=cdn_svc.id, name="CDN Availability", target_percent=99.95, window_days=30, metric_name="status", good_condition="eq", good_threshold=1.0),
    ]
    for s in slos:
        db.add(s)

    # Metric samples — 50 samples per key metric
    metric_defs = [
        (api_svc.id, "latency_ms", 45, 80, {"service": "api-gateway"}),
        (api_svc.id, "request_rate", 800, 400, {"service": "api-gateway"}),
        (api_svc.id, "error_rate", 0.5, 1.0, {"service": "api-gateway"}),
        (auth_svc.id, "latency_ms", 115, 30, {"service": "auth"}),
        (auth_svc.id, "cpu_usage", 62, 25, {"service": "auth"}),
        (pay_svc.id, "latency_ms", 780, 600, {"service": "payments"}),
        (pay_svc.id, "error_rate", 4.5, 5.0, {"service": "payments"}),
        (notify_svc.id, "queue_depth", 120, 80, {"service": "notify"}),
        (cdn_svc.id, "cache_hit_rate", 78, 15, {"service": "cdn"}),
        (cdn_svc.id, "latency_ms", 8, 3, {"service": "cdn"}),
    ]
    for svc_id, name, base, spread, labels in metric_defs:
        for i in range(50):
            val = max(0, base + rng.uniform(-spread, spread))
            db.add(MetricSample(
                service_id=svc_id,
                name=name,
                value=round(val, 2),
                labels=labels,
                sampled_at=_ago(minutes=i * 15),
            ))

    # Log entries
    log_defs = [
        (api_svc.id, "info", "Request routed to auth-service", "nginx"),
        (api_svc.id, "warning", "Upstream timeout on /api/v1/orders — retrying", "nginx"),
        (api_svc.id, "error", "Circuit breaker opened for payment-service", "nginx"),
        (auth_svc.id, "info", "JWT issued for user 0xf3a1...", "auth-service"),
        (auth_svc.id, "warning", "Rate limit approaching for IP 192.168.1.42", "rate-limiter"),
        (pay_svc.id, "error", "Stripe webhook delivery failed: ECONNRESET", "payment-worker"),
        (pay_svc.id, "critical", "Payment processor returned 503 — fallback activated", "payment-processor"),
        (pay_svc.id, "info", "Transaction TXN-88241 completed successfully", "payment-service"),
        (notify_svc.id, "info", "Email dispatched to user@example.com", "mailer"),
        (notify_svc.id, "warning", "SMS queue depth at 350 — above threshold", "sms-worker"),
        (db_svc.id, "critical", "All connections exhausted — max_connections reached", "pgbouncer"),
        (db_svc.id, "error", "Health check failed: Connection refused", "health-probe"),
        (cdn_svc.id, "info", "Cache purged for /assets/main.*.js", "cdn-worker"),
        (cdn_svc.id, "warning", "Cache miss rate 34% — high origin load", "cache-analytics"),
        (api_svc.id, "info", "Deployment v3.2.1 health check passed", "deployer"),
    ]
    for i, (svc_id, level, msg, src) in enumerate(log_defs):
        for j in range(5):
            db.add(LogEntry(
                service_id=svc_id,
                level=level,
                message=msg,
                source=src,
                attributes={"replica": f"pod-{rng.randint(1,3)}", "trace_id": f"tr-{rng.randint(100000,999999)}"},
                logged_at=_ago(minutes=(i * 5 + j * 37)),
            ))

    await db.commit()

    return {
        "seeded": {
            "services": len(services),
            "uptime_checks": len(services) * 20,
            "alert_rules": len(rules),
            "alerts": len(alerts),
            "incidents": len(incidents),
            "slos": len(slos),
            "metric_samples": len(metric_defs) * 50,
            "log_entries": len(log_defs) * 5,
        }
    }


@router.delete("")
async def clear_data(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(UptimeCheck))
    await db.execute(delete(Alert))
    await db.execute(delete(AlertRule))
    await db.execute(delete(MetricSample))
    await db.execute(delete(LogEntry))
    await db.execute(delete(Incident))
    await db.execute(delete(SLO))
    await db.execute(delete(MonitoredService))
    await db.commit()
    return {"cleared": True}
