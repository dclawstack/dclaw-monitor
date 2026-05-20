"use client";

import { useState } from "react";
import { seedData, clearData } from "@/lib/api";

export function SeedControls() {
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState<"fill" | "clear" | null>(null);

  async function handleSeed() {
    setLoading("fill");
    setStatus(null);
    try {
      const result = await seedData();
      const s = result.seeded;
      setStatus(
        `Seeded: ${s.services} services · ${s.uptime_checks} checks · ${s.alerts} alerts · ${s.incidents} incidents · ${s.slos} SLOs · ${s.metric_samples} metrics · ${s.log_entries} logs`
      );
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setStatus(`Error: ${msg}`);
    } finally {
      setLoading(null);
    }
  }

  async function handleClear() {
    setLoading("clear");
    setStatus(null);
    try {
      await clearData();
      setStatus("All data cleared successfully.");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setStatus(`Error: ${msg}`);
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="rounded-xl border border-indigo-100 bg-indigo-50 p-6">
      <p className="text-sm font-semibold text-indigo-800 mb-1">Demo Data Controls</p>
      <p className="text-xs text-indigo-600 mb-4">
        Populate the app with realistic sample data or wipe everything for a clean state.
      </p>
      <div className="flex flex-wrap gap-3">
        <button
          onClick={handleSeed}
          disabled={loading !== null}
          className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {loading === "fill" ? "Seeding…" : "Fill with Demo Data"}
        </button>
        <button
          onClick={handleClear}
          disabled={loading !== null}
          className="px-4 py-2 rounded-lg bg-white border border-gray-300 text-gray-700 text-sm font-medium hover:bg-gray-50 disabled:opacity-50 transition-colors"
        >
          {loading === "clear" ? "Clearing…" : "Clear All Data"}
        </button>
      </div>
      {status && (
        <p className="mt-3 text-xs text-indigo-700 bg-white border border-indigo-100 rounded-lg px-3 py-2">
          {status}
        </p>
      )}
    </div>
  );
}
