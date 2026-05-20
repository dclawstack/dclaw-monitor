import Link from "next/link";
import {
  Activity,
  AlertTriangle,
  Bell,
  BarChart2,
  Bot,
  CheckCircle2,
  Clock,
  FileText,
  Globe,
  Shield,
  Zap,
  ArrowRight,
  TrendingUp,
  Network,
} from "lucide-react";
// ── SEED CONTROLS — remove this import (and the <SeedControls> block below) to hide ──
import { SeedControls } from "@/components/SeedControls";
// ── END SEED CONTROLS IMPORT ──

const features = [
  {
    icon: Globe,
    title: "Service Registry",
    description:
      "Centrally register every HTTP, gRPC, or TCP service. Track health, ownership, and dependencies across your entire infrastructure.",
    color: "text-blue-600",
    bg: "bg-blue-50",
  },
  {
    icon: CheckCircle2,
    title: "Uptime Monitoring",
    description:
      "Continuous health checks at configurable intervals from 10s to 5min. Instant status tracking with full response history.",
    color: "text-green-600",
    bg: "bg-green-50",
  },
  {
    icon: Bell,
    title: "Smart Alert Engine",
    description:
      "Define threshold-based alert rules on any metric — latency, error rate, saturation. Multi-severity with deduplication.",
    color: "text-amber-600",
    bg: "bg-amber-50",
  },
  {
    icon: AlertTriangle,
    title: "Incident Management",
    description:
      "Auto-create incidents from correlated alerts. Track MTTR, attach RCA summaries, and drive resolution workflows end-to-end.",
    color: "text-red-600",
    bg: "bg-red-50",
  },
  {
    icon: TrendingUp,
    title: "SLO Tracking",
    description:
      "Define Service Level Objectives with error budgets. Burn rate alerts warn you before you breach your SLA commitments.",
    color: "text-indigo-600",
    bg: "bg-indigo-50",
  },
  {
    icon: Bot,
    title: "AI Copilot",
    description:
      "Natural language queries over your monitoring data. Ask \"What caused the payment spike?\" and get instant RCA answers.",
    color: "text-violet-600",
    bg: "bg-violet-50",
  },
  {
    icon: BarChart2,
    title: "Metrics & Logs",
    description:
      "Ingest custom metrics and structured logs via REST API. Full-text search, level filtering, and time-series visualization.",
    color: "text-cyan-600",
    bg: "bg-cyan-50",
  },
  {
    icon: Network,
    title: "Synthetic Monitoring",
    description:
      "Script multi-step user journeys and run them on a schedule. Catch broken flows before real users hit them.",
    color: "text-teal-600",
    bg: "bg-teal-50",
  },
  {
    icon: Zap,
    title: "Distributed Tracing",
    description:
      "Collect and visualize OpenTelemetry trace spans. Pinpoint latency hotspots and cross-service bottlenecks instantly.",
    color: "text-orange-600",
    bg: "bg-orange-50",
  },
  {
    icon: Shield,
    title: "Prometheus Export",
    description:
      "Expose all metrics via a /metrics endpoint in Prometheus format. Drop-in compatible with Grafana, Alertmanager, and more.",
    color: "text-gray-600",
    bg: "bg-gray-100",
  },
  {
    icon: Clock,
    title: "Anomaly Detection",
    description:
      "Baseline-aware anomaly engine flags unusual patterns automatically — no manual threshold tuning required.",
    color: "text-pink-600",
    bg: "bg-pink-50",
  },
  {
    icon: FileText,
    title: "Webhook Integrations",
    description:
      "Push alert events to Slack, PagerDuty, or any HTTP endpoint. Fully configurable payload templates.",
    color: "text-emerald-600",
    bg: "bg-emerald-50",
  },
];

const steps = [
  {
    step: "01",
    title: "Register Your Services",
    description:
      "Add services via the dashboard or REST API. Provide a URL and interval — DClaw Monitor takes care of the rest.",
  },
  {
    step: "02",
    title: "Define Alerts & SLOs",
    description:
      "Set threshold rules on any metric. Configure error budgets and get alerted before SLA breaches occur.",
  },
  {
    step: "03",
    title: "Investigate with AI",
    description:
      "When incidents fire, ask the AI Copilot for root cause analysis. Get correlated insights in seconds, not hours.",
  },
];

const stats = [
  { label: "Services Monitored", value: "500+", icon: Globe },
  { label: "Checks per Minute", value: "12K", icon: CheckCircle2 },
  { label: "Avg Alert Latency", value: "< 3s", icon: Bell },
  { label: "Uptime Guarantee", value: "99.9%", icon: Activity },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white font-sans">
      {/* Nav */}
      <header className="border-b border-gray-100 sticky top-0 bg-white/95 backdrop-blur z-10">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-6 w-6 text-indigo-600" />
            <span className="font-bold text-gray-900 text-lg">DClaw Monitor</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-gray-600">
            <Link href="#features" className="hover:text-gray-900 transition-colors">Features</Link>
            <Link href="#how-it-works" className="hover:text-gray-900 transition-colors">How it works</Link>
            <Link href="/dashboard" className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors font-medium">
              Open Dashboard
            </Link>
          </nav>
          <Link href="/dashboard" className="md:hidden px-3 py-1.5 text-sm rounded-lg bg-indigo-600 text-white">
            Dashboard
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="bg-gradient-to-br from-indigo-50 via-white to-blue-50 py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 text-indigo-700 text-sm font-medium mb-6">
            <Zap className="h-3.5 w-3.5" />
            Full-stack observability platform
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 leading-tight mb-6">
            Monitor everything.
            <br />
            <span className="text-indigo-600">Fix it faster.</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10 leading-relaxed">
            DClaw Monitor gives you uptime checks, metrics, logs, tracing, SLOs, and an AI copilot — all in one
            platform. Know before your users do.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition-colors shadow-md shadow-indigo-200"
            >
              Go to Dashboard <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/alerts"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 font-semibold hover:bg-gray-50 transition-colors"
            >
              View Alerts <Bell className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="bg-indigo-600 py-10 px-6">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map(({ label, value, icon: Icon }) => (
            <div key={label} className="text-center text-white">
              <Icon className="h-5 w-5 mx-auto mb-2 text-indigo-200" />
              <div className="text-3xl font-bold">{value}</div>
              <div className="text-sm text-indigo-200 mt-0.5">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features grid */}
      <section id="features" className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Everything you need to observe</h2>
            <p className="text-lg text-gray-500 max-w-2xl mx-auto">
              From uptime checks to distributed traces — DClaw Monitor covers the full observability stack with no
              separate tools to stitch together.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map(({ icon: Icon, title, description, color, bg }) => (
              <div
                key={title}
                className="rounded-2xl border border-gray-100 p-6 hover:shadow-md transition-shadow bg-white group"
              >
                <div className={`inline-flex p-2.5 rounded-xl ${bg} mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className={`h-5 w-5 ${color}`} />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2 text-lg">{title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-24 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Up and running in minutes</h2>
            <p className="text-lg text-gray-500">
              No agents to install, no complex configuration. Just point, click, and observe.
            </p>
          </div>
          <div className="space-y-8">
            {steps.map(({ step, title, description }) => (
              <div key={step} className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-12 h-12 rounded-2xl bg-indigo-600 text-white font-bold text-lg flex items-center justify-center">
                  {step}
                </div>
                <div className="pt-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
                  <p className="text-gray-500 leading-relaxed">{description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Quick navigation */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">Explore the platform</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { href: "/dashboard", label: "Dashboard", icon: Activity, color: "text-indigo-600", bg: "bg-indigo-50" },
              { href: "/alerts", label: "Alerts", icon: Bell, color: "text-amber-600", bg: "bg-amber-50" },
              { href: "/incidents", label: "Incidents", icon: AlertTriangle, color: "text-red-600", bg: "bg-red-50" },
              { href: "/copilot", label: "AI Copilot", icon: Bot, color: "text-violet-600", bg: "bg-violet-50" },
            ].map(({ href, label, icon: Icon, color, bg }) => (
              <Link
                key={href}
                href={href}
                className="flex flex-col items-center gap-3 p-6 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:shadow-md transition-all group text-center"
              >
                <div className={`p-3 rounded-xl ${bg} group-hover:scale-110 transition-transform`}>
                  <Icon className={`h-6 w-6 ${color}`} />
                </div>
                <span className="font-medium text-gray-800">{label}</span>
                <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-indigo-600 transition-colors" />
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-gradient-to-br from-indigo-600 to-blue-700">
        <div className="max-w-2xl mx-auto text-center text-white">
          <h2 className="text-4xl font-bold mb-4">Ready to get started?</h2>
          <p className="text-indigo-200 text-lg mb-10">
            Open the dashboard and start monitoring your services in seconds.
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-white text-indigo-700 font-bold hover:bg-indigo-50 transition-colors shadow-lg"
          >
            Open Dashboard <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* ── SEED CONTROLS — remove this section (and the SeedControls import at top) to hide ── */}
      <section className="py-16 px-6 border-t border-gray-100 bg-gray-50">
        <div className="max-w-lg mx-auto">
          <SeedControls />
        </div>
      </section>
      {/* ── END SEED CONTROLS ── */}

      {/* Footer */}
      <footer className="border-t border-gray-100 py-8 px-6 bg-white">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-indigo-600" />
            <span className="font-medium text-gray-700">DClaw Monitor</span>
            <span>— Full-stack observability for DClaw Platform</span>
          </div>
          <nav className="flex gap-6">
            <Link href="/dashboard" className="hover:text-gray-900 transition-colors">Dashboard</Link>
            <Link href="/alerts" className="hover:text-gray-900 transition-colors">Alerts</Link>
            <Link href="/incidents" className="hover:text-gray-900 transition-colors">Incidents</Link>
            <Link href="/copilot" className="hover:text-gray-900 transition-colors">AI Copilot</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
