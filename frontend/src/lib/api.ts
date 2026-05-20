const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!response.ok) {
    const error = await response.text();
    throw new ApiError(`API error ${response.status}: ${error}`, response.status);
  }
  return response.json();
}

export const api = fetchJson;
export { ApiError };

// ── Domain types ──

export type ServiceStatus = "healthy" | "degraded" | "down" | "unknown";

export interface Service {
  id: string;
  name: string;
  url: string;
  description: string | null;
  status: ServiceStatus;
  interval_seconds: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ServiceCreate {
  name: string;
  url: string;
  description?: string;
  interval_seconds?: number;
}

export interface ServiceList {
  items: Service[];
  total: number;
}

export interface UptimeCheck {
  id: string;
  service_id: string;
  status: "up" | "down" | "timeout" | "error";
  latency_ms: number | null;
  status_code: number | null;
  error: string | null;
  checked_at: string;
}

export interface CheckList {
  items: UptimeCheck[];
  total: number;
}

export type AlertSeverity = "info" | "warning" | "critical";
export type AlertStatus = "open" | "acknowledged" | "resolved";

export interface AlertRule {
  id: string;
  name: string;
  service_id: string | null;
  metric_name: string;
  operator: string;
  threshold: number;
  severity: AlertSeverity;
  is_active: boolean;
  created_at: string;
}

export interface AlertRuleList {
  items: AlertRule[];
  total: number;
}

export interface Alert {
  id: string;
  rule_id: string | null;
  service_id: string | null;
  title: string;
  message: string;
  severity: AlertSeverity;
  status: AlertStatus;
  fired_at: string;
  resolved_at: string | null;
}

export interface AlertList {
  items: Alert[];
  total: number;
}

export interface MetricSample {
  id: string;
  service_id: string | null;
  name: string;
  value: number;
  labels: Record<string, string> | null;
  sampled_at: string;
}

export interface MetricList {
  items: MetricSample[];
  total: number;
}

export interface LogEntry {
  id: string;
  service_id: string | null;
  level: string;
  message: string;
  source: string | null;
  attributes: Record<string, unknown> | null;
  logged_at: string;
}

export interface LogList {
  items: LogEntry[];
  total: number;
}

// ── API functions ──

export async function getHealth() {
  return fetchJson<{ status: string }>("/health/");
}

// Services
export const getServices = (limit = 20, offset = 0) =>
  fetchJson<ServiceList>(`/api/v1/services/?limit=${limit}&offset=${offset}`);

export const createService = (data: ServiceCreate) =>
  fetchJson<Service>("/api/v1/services/", { method: "POST", body: JSON.stringify(data) });

export const getService = (id: string) =>
  fetchJson<Service>(`/api/v1/services/${id}`);

// Checks
export const getChecksForService = (serviceId: string, limit = 50) =>
  fetchJson<CheckList>(`/api/v1/checks/service/${serviceId}?limit=${limit}`);

// Alert rules
export const getAlertRules = (limit = 20, offset = 0) =>
  fetchJson<AlertRuleList>(`/api/v1/alert-rules/?limit=${limit}&offset=${offset}`);

// Alerts
export const getAlerts = (params?: { status?: string; service_id?: string; limit?: number }) => {
  const q = new URLSearchParams();
  if (params?.status) q.set("status", params.status);
  if (params?.service_id) q.set("service_id", params.service_id);
  if (params?.limit) q.set("limit", String(params.limit));
  return fetchJson<AlertList>(`/api/v1/alerts/${q.toString() ? `?${q}` : ""}`);
};

export const updateAlertStatus = (id: string, status: AlertStatus) =>
  fetchJson<Alert>(`/api/v1/alerts/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });

// Metrics
export const getMetrics = (name: string, params?: { service_id?: string; limit?: number }) => {
  const q = new URLSearchParams({ name });
  if (params?.service_id) q.set("service_id", params.service_id);
  if (params?.limit) q.set("limit", String(params.limit));
  return fetchJson<MetricList>(`/api/v1/metrics/?${q}`);
};

// Logs
export const getLogs = (params?: { q?: string; level?: string; service_id?: string; limit?: number }) => {
  const q = new URLSearchParams();
  if (params?.q) q.set("q", params.q);
  if (params?.level) q.set("level", params.level);
  if (params?.service_id) q.set("service_id", params.service_id);
  if (params?.limit) q.set("limit", String(params.limit));
  return fetchJson<LogList>(`/api/v1/logs/${q.toString() ? `?${q}` : ""}`);
};

// AI Chat
export const chatWithAI = (message: string, service_id?: string) =>
  fetchJson<{ reply: string }>("/api/v1/ai/chat", {
    method: "POST",
    body: JSON.stringify({ message, service_id }),
  });

// ── Incident types ──

export type IncidentSeverity = "low" | "medium" | "high" | "critical";
export type IncidentStatus = "open" | "resolved";

export interface Incident {
  id: string;
  title: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  opened_at: string;
  resolved_at: string | null;
  mttr_seconds: number | null;
  rca_summary: string | null;
  alert_ids: string[];
}

export interface IncidentList {
  items: Incident[];
  total: number;
}

// Incidents
export const getIncidents = (params?: { status?: string; limit?: number }) => {
  const q = new URLSearchParams();
  if (params?.status) q.set("status", params.status);
  if (params?.limit) q.set("limit", String(params.limit));
  return fetchJson<IncidentList>(`/api/v1/incidents/${q.toString() ? `?${q}` : ""}`);
};

export const getIncident = (id: string) =>
  fetchJson<Incident>(`/api/v1/incidents/${id}`);

export const resolveIncident = (id: string) =>
  fetchJson<Incident>(`/api/v1/incidents/${id}/resolve`, { method: "POST" });

// Legacy alias
export type ServiceHealth = Service;
