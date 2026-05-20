"use client";

import { useEffect, useState } from "react";
import { Activity, AlertTriangle, CheckCircle, Server, XCircle, Clock, Plus } from "lucide-react";
import Link from "next/link";
import {
  getServices,
  getAlerts,
  createService,
  updateAlertStatus,
  type Service,
  type Alert,
  type ServiceCreate,
} from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import MonitorCopilot from "@/components/monitor-copilot";

const STATUS_COLOR: Record<string, string> = {
  healthy: "bg-green-100 text-green-800",
  degraded: "bg-yellow-100 text-yellow-800",
  down: "bg-red-100 text-red-800",
  unknown: "bg-gray-100 text-gray-600",
};

const STATUS_ICON: Record<string, React.ReactNode> = {
  healthy: <CheckCircle className="w-4 h-4 text-green-600" />,
  degraded: <AlertTriangle className="w-4 h-4 text-yellow-600" />,
  down: <XCircle className="w-4 h-4 text-red-600" />,
  unknown: <Clock className="w-4 h-4 text-gray-400" />,
};

const SEVERITY_BADGE: Record<string, string> = {
  info: "bg-blue-100 text-blue-800",
  warning: "bg-yellow-100 text-yellow-800",
  critical: "bg-red-100 text-red-800",
};

export default function DashboardPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [addOpen, setAddOpen] = useState(false);
  const [form, setForm] = useState<ServiceCreate>({ name: "", url: "", interval_seconds: 60 });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    try {
      const [svcData, alertData] = await Promise.all([
        getServices(100),
        getAlerts({ status: "open", limit: 20 }),
      ]);
      setServices(svcData.items);
      setAlerts(alertData.items);
    } catch {
      // silently ignore — backend may not be running in dev
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleAddService() {
    if (!form.name.trim() || !form.url.trim()) return;
    setSaving(true);
    setError("");
    try {
      await createService(form);
      setAddOpen(false);
      setForm({ name: "", url: "", interval_seconds: 60 });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create service");
    } finally {
      setSaving(false);
    }
  }

  async function handleAcknowledge(alertId: string) {
    await updateAlertStatus(alertId, "acknowledged");
    setAlerts((prev) => prev.map((a) => a.id === alertId ? { ...a, status: "acknowledged" } : a));
  }

  const healthy = services.filter((s) => s.status === "healthy").length;
  const down = services.filter((s) => s.status === "down").length;
  const degraded = services.filter((s) => s.status === "degraded").length;
  const openAlerts = alerts.filter((a) => a.status === "open").length;

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Activity className="w-7 h-7 text-blue-600" />
            <h1 className="text-xl font-bold text-gray-900">DClaw Monitor</h1>
          </div>
          <nav className="flex items-center gap-4 text-sm font-medium text-gray-600">
            <Link href="/dashboard" className="text-blue-600 font-semibold">
              Dashboard
            </Link>
            <Link href="/alerts" className="hover:text-gray-900 transition-colors">
              Alerts
            </Link>
            <Link href="/incidents" className="hover:text-gray-900 transition-colors">
              Incidents
            </Link>
            <Link href="/copilot" className="hover:text-gray-900 transition-colors">
              AI Copilot
            </Link>
            <Button onClick={() => setAddOpen(true)} className="gap-2">
              <Plus className="w-4 h-4" /> Add Service
            </Button>
          </nav>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Summary cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Total Services</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Server className="w-5 h-5 text-gray-400" />
                <span className="text-2xl font-bold">{services.length}</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Healthy</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-2xl font-bold text-green-700">{healthy}</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Degraded / Down</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-yellow-500" />
                <span className="text-2xl font-bold text-yellow-700">{degraded + down}</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Open Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <XCircle className="w-5 h-5 text-red-500" />
                <span className="text-2xl font-bold text-red-700">{openAlerts}</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Services table */}
        <Card>
          <CardHeader>
            <CardTitle>Monitored Services</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-sm text-gray-500 py-4">Loading…</p>
            ) : services.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <Server className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm">No services yet. Add one to start monitoring.</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>URL</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Interval</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {services.map((svc) => (
                    <TableRow key={svc.id}>
                      <TableCell className="font-medium">{svc.name}</TableCell>
                      <TableCell className="text-gray-500 text-sm truncate max-w-xs">{svc.url}</TableCell>
                      <TableCell>
                        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLOR[svc.status]}`}>
                          {STATUS_ICON[svc.status]}
                          {svc.status}
                        </span>
                      </TableCell>
                      <TableCell className="text-gray-500 text-sm">{svc.interval_seconds}s</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Alerts */}
        {alerts.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Open Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Severity</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Fired</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {alerts.map((alert) => (
                    <TableRow key={alert.id}>
                      <TableCell>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${SEVERITY_BADGE[alert.severity]}`}>
                          {alert.severity}
                        </span>
                      </TableCell>
                      <TableCell className="font-medium">{alert.title}</TableCell>
                      <TableCell className="text-gray-500 text-sm">
                        {new Date(alert.fired_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Badge variant={alert.status === "open" ? "destructive" : "secondary"}>
                          {alert.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {alert.status === "open" && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleAcknowledge(alert.id)}
                          >
                            Ack
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>

      {/* AI Copilot floating widget */}
      <MonitorCopilot />

      {/* Add Service dialog */}
      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Service</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 mt-2">
            <div>
              <Label htmlFor="svc-name">Name</Label>
              <Input
                id="svc-name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="payment-api"
              />
            </div>
            <div>
              <Label htmlFor="svc-url">URL</Label>
              <Input
                id="svc-url"
                value={form.url}
                onChange={(e) => setForm({ ...form, url: e.target.value })}
                placeholder="https://api.example.com/health"
              />
            </div>
            <div>
              <Label htmlFor="svc-interval">Check interval (seconds)</Label>
              <Input
                id="svc-interval"
                type="number"
                value={form.interval_seconds}
                onChange={(e) => setForm({ ...form, interval_seconds: Number(e.target.value) })}
              />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <div className="flex gap-3 justify-end">
              <Button variant="outline" onClick={() => setAddOpen(false)}>Cancel</Button>
              <Button onClick={handleAddService} disabled={saving}>
                {saving ? "Saving…" : "Add Service"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </main>
  );
}
