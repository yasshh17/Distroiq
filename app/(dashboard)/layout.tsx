import type { ReactNode } from "react";
import { ChevronRight, AlertCircle, AlertTriangle } from "lucide-react";

const SOURCES = [
  { name: "Warehouse ERP", status: "green" as const, count: "2.4k" },
  { name: "Order Management", status: "green" as const, count: "847" },
  { name: "Customer DB", status: "amber" as const, count: "12.1k" },
  { name: "Supplier Portal", status: "green" as const, count: "326" },
  { name: "Analytics DW", status: "amber" as const, count: "89" },
];

const ALERTS = [
  {
    level: "red" as const,
    title: "Stock Critical",
    desc: "SKU-4821 below reorder point",
    Icon: AlertCircle,
  },
  {
    level: "amber" as const,
    title: "Order Delays",
    desc: "14 shipments past ETA",
    Icon: AlertTriangle,
  },
  {
    level: "amber" as const,
    title: "Supplier Drop",
    desc: "Response rate down 23%",
    Icon: AlertTriangle,
  },
];

const QUERIES = [
  "Inventory by warehouse",
  "Pending orders > 48h",
  "Low stock SKUs",
  "Top suppliers this week",
  "Customer order history",
  "Reorder recommendations",
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[#0f1623]">
      {/* ── Header ─────────────────────────────────────────────────── */}
      <header className="flex h-14 shrink-0 items-stretch border-b border-white/[0.06]">
        {/* Brand column — width mirrors sidebar */}
        <div className="flex w-[260px] shrink-0 items-center gap-2.5 border-r border-white/[0.08] px-4">
          <div className="flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-lg bg-blue-600">
            <span className="font-mono text-[11px] font-bold text-white">DQ</span>
          </div>
          <span className="text-[15px] font-semibold text-white">DistroIQ</span>
        </div>

        {/* Center label */}
        <div className="flex flex-1 items-center justify-center">
          <span className="font-mono text-[13px] tracking-wide text-slate-300">
            AI Operations Assistant · Distribution
          </span>
        </div>

        {/* Right controls */}
        <div className="flex shrink-0 items-center gap-3 px-5">
          <span className="rounded border border-emerald-500/25 bg-emerald-500/10 px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-emerald-400">
            RAG · LIVE DATA
          </span>

          {/* Pulsing status dot */}
          <span className="relative flex h-2 w-2 items-center justify-center">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-green-400" />
          </span>

          <span className="font-mono text-[11px] uppercase tracking-widest text-slate-400">
            OPS STAFF
          </span>
        </div>
      </header>

      {/* ── Body ───────────────────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">
        {/* ── Sidebar ──────────────────────────────────────────────── */}
        <aside className="flex w-[260px] shrink-0 flex-col overflow-y-auto border-r border-white/[0.06] bg-[#0f1623] pb-4">
          {/* Connected Sources */}
          <div className="px-3 pt-5">
            <p className="mb-2 px-1 font-mono text-[10px] uppercase tracking-widest text-slate-500">
              Connected Sources
            </p>
            <div className="flex flex-col gap-px">
              {SOURCES.map((s) => (
                <div
                  key={s.name}
                  className="group flex cursor-pointer items-center gap-2.5 rounded-md px-2 py-[7px] transition-colors hover:bg-white/[0.05]"
                >
                  <span
                    className={`h-1.5 w-1.5 shrink-0 rounded-full ${
                      s.status === "green" ? "bg-emerald-400" : "bg-amber-400"
                    }`}
                  />
                  <span className="flex-1 truncate text-[12.5px] text-slate-300">{s.name}</span>
                  <span className="rounded bg-white/[0.06] px-1.5 py-px font-mono text-[10px] text-slate-500">
                    {s.count}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="mx-3 my-3.5 border-t border-white/[0.06]" />

          {/* Live Alerts */}
          <div className="px-3">
            <p className="mb-2 px-1 font-mono text-[10px] uppercase tracking-widest text-slate-500">
              Live Alerts
            </p>
            <div className="flex flex-col gap-1.5">
              {ALERTS.map((a, i) => (
                <div
                  key={i}
                  className={`cursor-pointer rounded-md bg-white/[0.03] py-2 pl-3 pr-2.5 border-l-2 transition-colors hover:bg-white/[0.06] ${
                    a.level === "red" ? "border-l-red-500" : "border-l-amber-400"
                  }`}
                >
                  <div className="flex items-center gap-1.5">
                    <a.Icon
                      className={`h-3 w-3 shrink-0 ${
                        a.level === "red" ? "text-red-400" : "text-amber-400"
                      }`}
                    />
                    <p
                      className={`text-[11.5px] font-semibold ${
                        a.level === "red" ? "text-red-400" : "text-amber-400"
                      }`}
                    >
                      {a.title}
                    </p>
                  </div>
                  <p className="mt-0.5 text-[11px] leading-snug text-slate-400">{a.desc}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="mx-3 my-3.5 border-t border-white/[0.06]" />

          {/* Quick Queries */}
          <div className="px-3">
            <p className="mb-2 px-1 font-mono text-[10px] uppercase tracking-widest text-slate-500">
              Quick Queries
            </p>
            <div className="flex flex-col gap-0.5">
              {QUERIES.map((q, i) => (
                <button
                  key={i}
                  className="group flex items-center gap-2 rounded-md px-2 py-[7px] text-left text-[12px] text-slate-400 transition-colors hover:bg-white/[0.05] hover:text-slate-200"
                >
                  <ChevronRight className="h-3 w-3 shrink-0 text-slate-600 transition-colors group-hover:text-blue-400" />
                  {q}
                </button>
              ))}
            </div>
          </div>
        </aside>

        {/* ── Main content ─────────────────────────────────────────── */}
        <main className="flex flex-1 flex-col overflow-hidden bg-[#f8f9fb]">
          {children}
        </main>
      </div>
    </div>
  );
}
