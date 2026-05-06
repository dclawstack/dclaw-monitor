import Link from "next/link";
import { Activity } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4">
      <div className="flex flex-col items-center text-center space-y-6">
        <Activity className="w-16 h-16" style={{ color: "#6366F1" }} />
        <h1 className="text-5xl font-bold" style={{ color: "#6366F1" }}>
          DClaw Monitor
        </h1>
        <p className="text-lg text-gray-600 max-w-md">
          AI-powered alerting & root cause
        </p>
        <Link
          href="/dashboard"
          className="inline-flex items-center justify-center rounded-md px-6 py-3 text-sm font-medium text-white transition-colors hover:opacity-90"
          style={{ backgroundColor: "#6366F1" }}
        >
          Open Dashboard
        </Link>
      </div>
    </main>
  );
}
