"""Generate remediation runbooks from past resolved incidents."""
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.incident_repo import IncidentRepository
from app.services import llm_client

logger = logging.getLogger(__name__)

_GENERIC_RUNBOOK = """# Generic SRE Runbook

## 1. Initial Triage
- Check service health dashboards and active alerts.
- Verify service status endpoints and uptime checks.
- Identify the scope: which services, regions, or users are affected?

## 2. Escalation
- Page on-call SRE if severity is critical.
- Notify stakeholders via status page / communication channels.

## 3. Mitigation Steps
- Check recent deployments — consider rollback if changes correlate with the incident.
- Scale out affected services if load is the likely cause.
- Restart unhealthy pods / containers if stuck in error state.
- Check downstream dependencies (databases, caches, external APIs).

## 4. Root Cause Investigation
- Collect logs from the affected service around the incident start time.
- Check infrastructure metrics: CPU, memory, disk, network.
- Review distributed traces for anomalous latency or errors.

## 5. Resolution & Follow-up
- Confirm service returns to healthy state.
- Write a post-mortem documenting timeline, root cause, and action items.
- Update runbook with any new findings.
"""


async def generate_runbook(service_id: UUID, db: AsyncSession) -> str:
    """Generate remediation runbook from past resolved incidents."""
    repo = IncidentRepository(db)
    incidents = await repo.list_resolved_by_service(service_id, limit=5)

    if not incidents:
        logger.info("No resolved incidents for service %s, returning generic runbook", service_id)
        return _GENERIC_RUNBOOK

    # Build prompt
    incident_lines = []
    for inc in incidents:
        rca = inc.rca_summary or "No RCA available."
        incident_lines.append(f"### {inc.title}\n**Severity:** {inc.severity}\n**RCA:** {rca}")

    incidents_text = "\n\n".join(incident_lines)
    system = (
        "You are a senior SRE. Generate a clear, actionable step-by-step runbook in Markdown "
        "based on past incident patterns. Include: triage steps, mitigation actions, "
        "root cause investigation hints, and resolution confirmation steps."
    )
    prompt = (
        f"Here are the {len(incidents)} most recent resolved incidents for this service:\n\n"
        f"{incidents_text}\n\n"
        "Generate a comprehensive runbook in Markdown that an on-call engineer can follow."
    )

    try:
        return await llm_client.complete(prompt, system)
    except Exception as e:
        logger.error("Runbook generation failed: %s", e)
        return _GENERIC_RUNBOOK
