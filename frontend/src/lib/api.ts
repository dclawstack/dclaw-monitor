export interface ServiceHealth {
  id: string;
  service_name: string;
  status: string;
  latency_ms: number;
  error_rate: number;
  root_cause: string;
  created_at: string;
}

export async function api<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`/api/v1${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return (await res.json()) as T;
}
