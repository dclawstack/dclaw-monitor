"use client";

import { useEffect, useState } from "react";
import { Activity, ArrowLeft, Bot } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { getIncident, type Incident, type IncidentSeverity, type IncidentStatus } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const SEVERITY_CLASS: Record<IncidentSeverity, string> = {
  low: "bg-blue-100 text-blue-800",
  medium: "bg-yellow-100 text-yellow-800",
  high: "bg-orange-100 text-orange-800",
  critical: "bg-red-100 text-red-800",
};

const STATUS_CLASS: Record<IncidentStatus, string> = {
  open: "bg-red-100 text-red-800",
  resolved: "bg-green-100 text-green-800",
};

function formatMttr(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
}

export default function IncidentDetailPage() {
  const params = useParams();
  const id = typeof params.id === "string" ? params.id : Array.isArray(params.id) ? params.id[0] : "";

  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getIncident(id)
      .then((data) => setIncident(data))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load incident"))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header / Nav */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Activity className="w-7 h-7 text-blue-600" />
            <h1 className="text-xl font-bold text-gray-900">DClaw Monitor</h1>
          </div>
          <nav className="flex items-center gap-4 text-sm font-medium text-gray-600">
            <Link href="/dashboard" className="hover:text-gray-900 transition-colors">
              Dashboard
            </Link>
            <Link href="/alerts" className="hover:text-gray-900 transition-colors">
              Alerts
            </Link>
            <Link href="/incidents" className="text-blue-600 font-semibold">
              Incidents
            </Link>
            <Link href="/copilot" className="hover:text-gray-900 transition-colors">
              AI Copilot
            </Link>
          </nav>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* Back button */}
        <Link
          href="/incidents"
          className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Incidents
        </Link>

        {loading && <p className="text-sm text-gray-500">Loading…</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}

        {incident && (
          <>
            {/* Incident header */}
            <Card>
              <CardHeader>
                <div className="flex flex-wrap items-start gap-3">
                  <CardTitle className="flex-1 text-xl">{incident.title}</CardTitle>
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${SEVERITY_CLASS[incident.severity]}`}
                    >
                      {incident.severity}
                    </span>
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_CLASS[incident.status]}`}
                    >
                      {incident.status}
                    </span>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-gray-600">
                <p>
                  <span className="font-medium text-gray-700">Opened:</span>{" "}
                  {new Date(incident.opened_at).toLocaleString()}
                </p>
                {incident.resolved_at && (
                  <p>
                    <span className="font-medium text-gray-700">Resolved:</span>{" "}
                    {new Date(incident.resolved_at).toLocaleString()}
                  </p>
                )}
                {incident.mttr_seconds !== null && (
                  <p>
                    <span className="font-medium text-gray-700">Resolved in:</span>{" "}
                    {formatMttr(incident.mttr_seconds)}
                  </p>
                )}
              </CardContent>
            </Card>

            {/* RCA Summary */}
            {incident.rca_summary && (
              <Card className="border-l-4 border-blue-500">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Bot className="w-5 h-5 text-blue-600" />
                    AI Root Cause Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {incident.rca_summary}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Alert IDs */}
            {incident.alert_ids && incident.alert_ids.length > 0 && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">Associated Alerts</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {incident.alert_ids.map((alertId) => (
                      <Badge key={alertId} variant="outline" className="font-mono text-xs">
                        {alertId}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    </main>
  );
}
