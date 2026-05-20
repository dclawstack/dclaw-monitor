"use client";

import { useEffect, useState } from "react";
import { Bell } from "lucide-react";
import { getAlerts, updateAlertStatus, type Alert, type AlertStatus } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

const SEVERITY_CLASS: Record<string, string> = {
  info: "bg-blue-100 text-blue-800",
  warning: "bg-yellow-100 text-yellow-800",
  critical: "bg-red-100 text-red-800",
};

const STATUS_CLASS: Record<string, string> = {
  open: "bg-red-100 text-red-800",
  acknowledged: "bg-yellow-100 text-yellow-800",
  resolved: "bg-green-100 text-green-800",
};

function relativeTime(dateStr: string): string {
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

type TabValue = "all" | "open" | "acknowledged" | "resolved";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabValue>("all");
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  async function load(tab: TabValue) {
    setLoading(true);
    try {
      const result = await getAlerts({
        status: tab === "all" ? undefined : tab,
        limit: 50,
      });
      setAlerts(result.items);
    } catch {
      // silently ignore
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(activeTab); }, [activeTab]);

  async function handleAction(alertId: string, status: AlertStatus) {
    setActionLoading(alertId);
    try {
      await updateAlertStatus(alertId, status);
      await load(activeTab);
    } catch {
      // silently ignore
    } finally {
      setActionLoading(null);
    }
  }

  const tabs: { value: TabValue; label: string }[] = [
    { value: "all", label: "All" },
    { value: "open", label: "Open" },
    { value: "acknowledged", label: "Acknowledged" },
    { value: "resolved", label: "Resolved" },
  ];

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <Bell className="w-6 h-6 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-900">Alert Inbox</h1>
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
            {alerts.length}
          </span>
          <div className="ml-auto">
            <a href="/dashboard" className="text-sm text-blue-600 hover:underline">Dashboard</a>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-8">
        <Tabs defaultValue="all">
          <TabsList>
            {tabs.map((tab) => (
              <TabsTrigger
                key={tab.value}
                value={tab.value}
                onClick={() => setActiveTab(tab.value)}
              >
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {tabs.map((tab) => (
            <TabsContent key={tab.value} value={tab.value}>
              <Card className="mt-4">
                <CardHeader>
                  <CardTitle className="text-lg">{tab.label} Alerts</CardTitle>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <p className="text-sm text-gray-400 py-4 text-center">Loading…</p>
                  ) : alerts.length === 0 ? (
                    <div className="text-center py-12 text-gray-400">
                      <Bell className="w-10 h-10 mx-auto mb-3 opacity-30" />
                      <p className="text-sm">No alerts found.</p>
                    </div>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Title</TableHead>
                          <TableHead>Service</TableHead>
                          <TableHead>Severity</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Fired At</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {alerts.map((alert) => (
                          <TableRow key={alert.id}>
                            <TableCell className="font-medium">{alert.title}</TableCell>
                            <TableCell className="text-gray-500 text-sm">{alert.service_id ?? "—"}</TableCell>
                            <TableCell>
                              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${SEVERITY_CLASS[alert.severity]}`}>
                                {alert.severity}
                              </span>
                            </TableCell>
                            <TableCell>
                              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_CLASS[alert.status]}`}>
                                {alert.status}
                              </span>
                            </TableCell>
                            <TableCell className="text-sm text-gray-500">{relativeTime(alert.fired_at)}</TableCell>
                            <TableCell>
                              <div className="flex gap-2">
                                {alert.status === "open" && (
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    disabled={actionLoading === alert.id}
                                    onClick={() => handleAction(alert.id, "acknowledged")}
                                  >
                                    Acknowledge
                                  </Button>
                                )}
                                {alert.status !== "resolved" && (
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    disabled={actionLoading === alert.id}
                                    onClick={() => handleAction(alert.id, "resolved")}
                                  >
                                    Resolve
                                  </Button>
                                )}
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </main>
  );
}
