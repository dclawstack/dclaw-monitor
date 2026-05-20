"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Activity, ArrowLeft } from "lucide-react";
import { getService, getChecksForService, getMetrics, type Service, type UptimeCheck, type MetricSample } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Sparkline } from "@/components/sparkline";

const CHECK_STATUS_CLASS: Record<string, string> = {
  up: "bg-green-100 text-green-800",
  down: "bg-red-100 text-red-800",
  timeout: "bg-yellow-100 text-yellow-800",
  error: "bg-orange-100 text-orange-800",
};

const SERVICE_STATUS_CLASS: Record<string, string> = {
  healthy: "bg-green-100 text-green-800",
  degraded: "bg-yellow-100 text-yellow-800",
  down: "bg-red-100 text-red-800",
  unknown: "bg-gray-100 text-gray-600",
};

function relativeTime(dateStr: string): string {
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

interface MetricGroup {
  name: string;
  values: number[];
}

export default function ServiceDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [service, setService] = useState<Service | null>(null);
  const [checks, setChecks] = useState<UptimeCheck[]>([]);
  const [metricGroups, setMetricGroups] = useState<MetricGroup[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    async function load() {
      setLoading(true);
      try {
        const [svc, checkData] = await Promise.all([
          getService(id),
          getChecksForService(id, 20),
        ]);
        setService(svc);
        setChecks(checkData.items);

        const metricNames = ["latency_ms", "error_rate", "request_count"];
        const groups: MetricGroup[] = [];
        for (const name of metricNames) {
          try {
            const result = await getMetrics(name, { service_id: id, limit: 50 });
            if (result.items.length > 0) {
              groups.push({ name, values: result.items.map((m: MetricSample) => m.value) });
            }
          } catch {
            // metric may not exist
          }
        }
        setMetricGroups(groups);
      } catch {
        // silently handle
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Activity className="w-8 h-8 text-blue-600 animate-spin" />
      </main>
    );
  }

  if (!service) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Service not found.</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center gap-4">
          <a href="/dashboard">
            <Button variant="ghost" size="sm" className="gap-1">
              <ArrowLeft className="w-4 h-4" /> Dashboard
            </Button>
          </a>
          <div className="flex items-center gap-3 flex-1">
            <h1 className="text-xl font-bold text-gray-900">{service.name}</h1>
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${SERVICE_STATUS_CLASS[service.status]}`}>
              {service.status}
            </span>
            {service.is_active ? (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">Active</span>
            ) : (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">Inactive</span>
            )}
          </div>
        </div>
        <div className="max-w-5xl mx-auto mt-1 pl-24">
          <p className="text-sm text-gray-500">{service.url}</p>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recent Uptime Checks</CardTitle>
          </CardHeader>
          <CardContent>
            {checks.length === 0 ? (
              <p className="text-sm text-gray-400 py-4 text-center">No checks recorded yet.</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Latency</TableHead>
                    <TableHead>HTTP Code</TableHead>
                    <TableHead>Error</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {checks.map((check) => (
                    <TableRow key={check.id}>
                      <TableCell className="text-gray-500 text-sm">{relativeTime(check.checked_at)}</TableCell>
                      <TableCell>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${CHECK_STATUS_CLASS[check.status]}`}>
                          {check.status}
                        </span>
                      </TableCell>
                      <TableCell className="text-sm">
                        {check.latency_ms != null ? `${check.latency_ms}ms` : "—"}
                      </TableCell>
                      <TableCell className="text-sm text-gray-600">
                        {check.status_code ?? "—"}
                      </TableCell>
                      <TableCell className="text-sm text-red-600 max-w-xs truncate">
                        {check.error ?? "—"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Latest Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            {metricGroups.length === 0 ? (
              <p className="text-sm text-gray-400 py-4 text-center">No metrics ingested yet.</p>
            ) : (
              <div className="space-y-4">
                {metricGroups.map((group) => (
                  <div key={group.name} className="flex items-center justify-between py-2 border-b last:border-0">
                    <div>
                      <p className="text-sm font-medium text-gray-700">{group.name}</p>
                      <p className="text-xs text-gray-400">{group.values.length} samples</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-gray-600">
                        latest: {group.values[0]?.toFixed(2) ?? "—"}
                      </span>
                      <Sparkline data={[...group.values].reverse()} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
