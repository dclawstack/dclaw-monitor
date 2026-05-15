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
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });
  if (!response.ok) {
    const error = await response.text();
    throw new ApiError(`API error ${response.status}: ${error}`, response.status);
  }
  return response.json();
}

export async function getHealth() {
  return fetchJson<{ status: string }>("/health/");
}

// TODO: Add app-specific API functions here

export { ApiError };

// ── Generic typed fetch ──
// Pages reference `api<T>(path, opts)` directly. Alias of fetchJson.
export const api = fetchJson;

// ── Type stubs ──
// Permissive `any` stubs until each domain shape is locked in.
// Tighten these to real interfaces as the app stabilizes.
export type ServiceHealth = any;
