"use client";

import { useEffect, useRef, useState } from "react";
import { Activity, Bot, Send } from "lucide-react";
import Link from "next/link";
import { chatWithAI, getServices, type Service } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export default function CopilotPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [selectedServiceId, setSelectedServiceId] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getServices(100).then((data) => setServices(data.items)).catch(() => {});
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: ChatMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const serviceId = selectedServiceId || undefined;
      const res = await chatWithAI(text, serviceId);
      setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
    } catch (e) {
      const errText = e instanceof Error ? e.message : "Failed to get a response.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${errText}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

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
            <Link href="/incidents" className="hover:text-gray-900 transition-colors">
              Incidents
            </Link>
            <Link href="/copilot" className="text-blue-600 font-semibold">
              AI Copilot
            </Link>
          </nav>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8 flex flex-col" style={{ height: "calc(100vh - 73px)" }}>
        {/* Page title */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Bot className="w-8 h-8 text-blue-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">AI SRE Copilot</h2>
              <p className="text-sm text-gray-500">Ask questions about your services, incidents, and alerts.</p>
            </div>
          </div>

          {/* Service selector */}
          <div className="flex items-center gap-2">
            <label htmlFor="service-select" className="text-sm text-gray-600 whitespace-nowrap">
              Context:
            </label>
            <Select
              id="service-select"
              value={selectedServiceId}
              onChange={(e) => setSelectedServiceId(e.target.value)}
              className="w-48"
            >
              <option value="">All Services</option>
              {services.map((svc) => (
                <option key={svc.id} value={svc.id}>
                  {svc.name}
                </option>
              ))}
            </Select>
          </div>
        </div>

        {/* Chat area */}
        <Card className="flex-1 flex flex-col overflow-hidden">
          {/* Messages */}
          <CardContent
            ref={scrollRef}
            className="flex-1 overflow-y-auto py-4 space-y-4"
          >
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center text-gray-400 py-16 gap-3">
                <Bot className="w-12 h-12 opacity-30" />
                <p className="text-base">Start a conversation with your AI SRE Copilot.</p>
                <p className="text-sm">Ask about service health, recent incidents, or alert patterns.</p>
              </div>
            ) : (
              messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[75%] rounded-lg px-4 py-2.5 text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "bg-blue-600 text-white"
                        : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-500 rounded-lg px-4 py-2.5 text-sm animate-pulse">
                  Thinking…
                </div>
              </div>
            )}
          </CardContent>

          {/* Input row */}
          <div className="p-4 border-t border-gray-200 flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                selectedServiceId
                  ? `Ask about ${services.find((s) => s.id === selectedServiceId)?.name ?? "this service"}…`
                  : "Ask about your infrastructure…"
              }
              disabled={loading}
              className="flex-1"
            />
            <Button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="gap-2"
            >
              <Send className="w-4 h-4" />
              Send
            </Button>
          </div>
        </Card>
      </div>
    </main>
  );
}
