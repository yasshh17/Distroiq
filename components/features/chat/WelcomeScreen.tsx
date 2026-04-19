"use client";

import { Package, ClipboardList, Users, Zap } from "lucide-react";
import { useChatStore } from "@/stores/chat";

const MODULES = [
  {
    number: "01",
    icon: Package,
    title: "Inventory\nIntelligence",
    desc: "Real-time stock monitoring across all distribution nodes.",
    query: "Low stock SKUs",
  },
  {
    number: "02",
    icon: ClipboardList,
    title: "Order\nOrchestration",
    desc: "Track, prioritize, and resolve order fulfillment issues.",
    query: "Pending orders > 48h",
  },
  {
    number: "03",
    icon: Users,
    title: "Customer\nInsights",
    desc: "Purchase patterns, account health, and engagement analytics.",
    query: "Customer order history",
  },
  {
    number: "04",
    icon: Zap,
    title: "Automated\nActions",
    desc: "Trigger reorders, alerts, and operational workflows via AI.",
    query: "Reorder recommendations",
  },
] as const;

const ACTIVITY = [
  {
    time: "14:21:45",
    event: "SKU-4821 dropped below reorder threshold",
    source: "Warehouse ERP",
  },
  {
    time: "14:19:12",
    event: "Order ORD-8821 delayed past ETA",
    source: "Order Management",
  },
  {
    time: "14:15:03",
    event: "Supplier V-99 response rate flagged",
    source: "Supplier Portal",
  },
];

function getUtcTime(): string {
  return new Date().toISOString().replace("T", " ").substring(0, 19) + " UTC";
}

export function WelcomeScreen() {
  const sendMessage = useChatStore((s) => s.sendMessage);
  const isStreaming = useChatStore((s) => s.isStreaming);

  return (
    <div className="py-8 animate-in fade-in-0 slide-in-from-bottom-3 duration-500">
      {/* Welcome banner */}
      <div className="flex items-center gap-2.5">
        <span className="h-1.5 w-1.5 rounded-full bg-[#22c55e]" style={{ animation: "breathe 2s ease-in-out infinite" }} />
        <span className="font-grotesk text-[13px] uppercase tracking-wider text-[#22c55e]">
          Welcome, Operator — System Nominal
        </span>
      </div>
      <p className="font-grotesk mt-1 text-[11px] text-white/40">
        SESSION: IQ-921-X · TIMESTAMP: {getUtcTime()}
      </p>

      {/* Module cards */}
      <div className="mt-8 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {MODULES.map((mod) => (
          <button
            key={mod.number}
            disabled={isStreaming}
            onClick={() => sendMessage(mod.query)}
            className="group flex flex-col gap-3 rounded-[12px] border border-white/[0.08] bg-[#1f2a3d] p-4 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-[rgba(37,99,235,0.6)] disabled:cursor-not-allowed disabled:opacity-40"
          >
            <div className="flex items-start justify-between">
              <span className="font-grotesk text-[11px] uppercase tracking-widest text-white/30">
                Module {mod.number}
              </span>
              <mod.icon className="h-4 w-4 text-white/20 transition-colors group-hover:text-[#2563eb]/40" />
            </div>
            <h3
              className="whitespace-pre-line text-[24px] font-light leading-tight text-white/95"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              {mod.title}
            </h3>
            <p className="text-[12.5px] leading-snug text-white/50">{mod.desc}</p>
            <span
              className="font-grotesk mt-1 text-[12px] font-medium uppercase text-[#2563eb] transition-opacity group-hover:opacity-80"
              style={{ letterSpacing: "0.05em" }}
            >
              INITIALIZE NODE ›
            </span>
          </button>
        ))}
      </div>

      {/* Stats bar */}
      <div className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-1.5 rounded-[12px] border border-white/[0.08] bg-[#101c2e] px-4 py-3">
        <span className="font-grotesk flex items-center gap-1.5 text-[11px] uppercase tracking-wide text-[#22c55e]">
          <span className="h-1.5 w-1.5 rounded-full bg-[#22c55e]" />
          5 Sources Active
        </span>
        <span className="font-grotesk text-[11px] uppercase tracking-wide text-white/40">
          · 42,891 Total SKUs
        </span>
        <span className="font-grotesk text-[11px] uppercase tracking-wide text-white/40">
          · 1,204 Open Orders
        </span>
        <span className="font-grotesk text-[11px] uppercase tracking-wide text-white/40">
          · 8,552 Customers
        </span>
        <span className="font-grotesk ml-auto text-[10px] text-white/25">
          Last Sync: {getUtcTime()}
        </span>
      </div>

      {/* Recent activity */}
      <div className="mt-4">
        <p className="font-grotesk mb-2 text-[10px] uppercase tracking-widest text-white/30">
          Recent Activity
        </p>
        <div className="space-y-px">
          {ACTIVITY.map((item, i) => (
            <div
              key={i}
              className="flex items-center gap-3 rounded-[8px] px-3 py-2 transition-colors hover:bg-[#1f2a3d]/60"
            >
              <span className="font-grotesk shrink-0 text-[10px] tabular-nums text-white/25">
                {item.time}
              </span>
              <span className="flex-1 text-[12px] text-white/55">{item.event}</span>
              <span className="font-grotesk shrink-0 rounded border border-white/[0.08] bg-[#1f2a3d] px-2 py-0.5 text-[10px] uppercase text-white/30">
                {item.source}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
