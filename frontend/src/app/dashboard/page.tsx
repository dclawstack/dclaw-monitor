"use client";

import { useState } from "react";
import { Activity } from "lucide-react";
import { api, ServiceHealth } from "@/lib/api";

export default function DashboardPage() {
  const [serviceName, setServiceName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ServiceHealth | null>(null);
  const [history, setHistory] = useState<{ timestamp: string; status: string; latency_ms: number }[]>([]);
  const [error, setError] = useState("");

  async function handleCheck() {
    if (!serviceName.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await api<ServiceHealth>("/services", {
        method: "POST",
        body: JSON.stringify({ service_name: serviceName.trim() }),
      });
      setResult(data);
      const hist = await api<{ history: { timestamp: string; status: string; latency_ms: number }[] }>(`/services/${data.id}/history`);
      setHistory(hist.history);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-8">
      <div className="max-w-2xl mx-auto space-y-8">
        <div className="flex items-center gap-3">
          <Activity className="w-8 h-8" style={{ color: "#6366F1" }} />
          <h1 className="text-3xl font-bold" style={{ color: "#6366F1" }}>
            DClaw Monitor
          </h1>
        </div>

        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <label className="block text-sm font-medium text-gray-700">
            Service name
          </label>
          <input
            type="text"
            value={serviceName}
            onChange={(e) => setServiceName(e.target.value)}
            placeholder="e.g. payment-api"
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent"
            style={{ "--tw-ring-color": "#6366F1" } as React.CSSProperties}
          />
          <button
            onClick={handleCheck}
            disabled={loading || !serviceName.trim()}
            className="inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white transition-colors hover:opacity-90 disabled:opacity-50"
            style={{ backgroundColor: "#6366F1" }}
          >
            {loading ? "Checking..." : "Check Health"}
          </button>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>

        {result && (
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Health Result</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-gray-50 rounded-md">
                <p className="text-xs text-gray-500 uppercase">Status</p>
                <p className="text-sm font-medium text-gray-900">{result.status}</p>
              </div>
              <div className="p-3 bg-gray-50 rounded-md">
                <p className="text-xs text-gray-500 uppercase">Latency</p>
                <p className="text-sm font-medium text-gray-900">{result.latency_ms} ms</p>
              </div>
              <div className="p-3 bg-gray-50 rounded-md">
                <p className="text-xs text-gray-500 uppercase">Error rate</p>
                <p className="text-sm font-medium text-gray-900">{result.error_rate.toFixed(2)}</p>
              </div>
              <div className="p-3 bg-gray-50 rounded-md">
                <p className="text-xs text-gray-500 uppercase">Suggested root cause</p>
                <p className="text-sm font-medium text-gray-900">{result.root_cause}</p>
              </div>
            </div>
          </div>
        )}

        {history.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">History</h2>
            <ul className="space-y-2">
              {history.map((h, i) => (
                <li key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <span className="text-sm text-gray-700">{new Date(h.timestamp).toLocaleString()}</span>
                  <span className="text-sm font-medium text-gray-900">{h.status} — {h.latency_ms} ms</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </main>
  );
}
