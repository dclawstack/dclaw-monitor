"use client";

import { useCallback, useEffect, useState } from "react";
import { Activity, AlertTriangle } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  getIncidents,
  resolveIncident,
  type Incident,
  type IncidentSeverity,
  type IncidentStatus,
} from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

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

function formatRelativeTime(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);
  if (diffSec < 60) return `${diffSec}s ago`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay}d ago`;
}

function formatMttr(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
}

interface IncidentRowProps {
  incident: Incident;
  onResolve: (id: string) => void;
  resolving: string | null;
}

function IncidentRow({ incident, onResolve, resolving }: IncidentRowProps) {
  const router = useRouter();

  function handleRowClick() {
    router.push(`/incidents/${incident.id}`);
  }

  function handleResolveClick(e: React.MouseEvent) {
    e.stopPropagation();
    onResolve(incident.id);
  }

  return (
    <TableRow
      onClick={handleRowClick}
      className="cursor-pointer hover:bg-gray-50 transition-colors"
    >
      <TableCell className="font-medium">{incident.title}</TableCell>
      <TableCell>
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${SEVERITY_CLASS[incident.severity]}`}
        >
          {incident.severity}
        </span>
      </TableCell>
      <TableCell>
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_CLASS[incident.status]}`}
        >
          {incident.status}
        </span>
      </TableCell>
      <TableCell className="text-gray-500 text-sm">
        {formatRelativeTime(incident.opened_at)}
      </TableCell>
      <TableCell className="text-gray-500 text-sm">
        {incident.mttr_seconds !== null ? formatMttr(incident.mttr_seconds) : "—"}
      </TableCell>
      <TableCell>
        {incident.status === "open" && (
          <Button
            variant="outline"
            size="sm"
            disabled={resolving === incident.id}
            onClick={handleResolveClick}
          >
            {resolving === incident.id ? "Resolving…" : "Resolve"}
          </Button>
        )}
      </TableCell>
    </TableRow>
  );
}

function IncidentTable({
  incidents,
  onResolve,
  resolving,
}: {
  incidents: Incident[];
  onResolve: (id: string) => void;
  resolving: string | null;
}) {
  if (incidents.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <AlertTriangle className="w-12 h-12 mx-auto mb-3 opacity-30" />
        <p className="text-sm">No incidents found.</p>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Title</TableHead>
          <TableHead>Severity</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Opened</TableHead>
          <TableHead>MTTR</TableHead>
          <TableHead>Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {incidents.map((inc) => (
          <IncidentRow
            key={inc.id}
            incident={inc}
            onResolve={onResolve}
            resolving={resolving}
          />
        ))}
      </TableBody>
    </Table>
  );
}

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [resolving, setResolving] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getIncidents({ limit: 100 });
      setIncidents(data.items);
    } catch {
      // backend may not be running
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleResolve(id: string) {
    setResolving(id);
    try {
      const updated = await resolveIncident(id);
      setIncidents((prev) =>
        prev.map((inc) => (inc.id === id ? updated : inc))
      );
    } catch {
      // silently ignore
    } finally {
      setResolving(null);
    }
  }

  const open = incidents.filter((i) => i.status === "open");
  const resolved = incidents.filter((i) => i.status === "resolved");

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

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {/* Page heading */}
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-bold text-gray-900">Incidents</h2>
          <Badge variant="secondary">{incidents.length}</Badge>
        </div>

        {loading ? (
          <p className="text-sm text-gray-500 py-4">Loading…</p>
        ) : (
          <Card>
            <CardHeader className="pb-0">
              <CardTitle className="sr-only">Incidents list</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <Tabs defaultValue="open">
                <TabsList className="mb-4">
                  <TabsTrigger value="open">
                    Open ({open.length})
                  </TabsTrigger>
                  <TabsTrigger value="resolved">
                    Resolved ({resolved.length})
                  </TabsTrigger>
                </TabsList>
                <TabsContent value="open">
                  <IncidentTable
                    incidents={open}
                    onResolve={handleResolve}
                    resolving={resolving}
                  />
                </TabsContent>
                <TabsContent value="resolved">
                  <IncidentTable
                    incidents={resolved}
                    onResolve={handleResolve}
                    resolving={resolving}
                  />
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  );
}
