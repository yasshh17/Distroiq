"use client";

import { useState } from "react";
import type { ReactNode } from "react";
import { AlertCircle, AlertTriangle, Menu, X } from "lucide-react";

import { QuickQueriesPanel } from "@/components/features/sidebar/QuickQueriesPanel";
import { UserChip } from "@/components/features/auth/UserChip";

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

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[#0f1623]">
      {/* ── Header ─────────────────────────────────────────────────── */}
      <header className="flex h-14 shrink-0 items-stretch border-b border-white/[0.06]">
        {/* Brand column — fixed width on desktop, auto on mobile */}
        <div className="flex shrink-0 items-center gap-2.5 border-r border-white/[0.08] px-4 lg:w-[260px]">
          {/* Hamburger — mobile only */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="mr-0.5 flex h-8 w-8 items-center justify-center rounded-md text-slate-400 transition-colors hover:text-white lg:hidden"
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-lg bg-blue-600">
            <span className="font-mono text-[11px] font-bold text-white">DQ</span>
          </div>
          <span className="text-[15px] font-semibold text-white">DistroIQ</span>
        </div>

        {/* Center label — hidden on mobile, flex on desktop */}
        <div className="flex flex-1 items-center justify-center">
          <span className="hidden font-mono text-[13px] tracking-wide text-slate-300 lg:block">
            AI Operations Assistant · Distribution
          </span>
        </div>

        {/* Right controls */}
        <div className="flex shrink-0 items-center gap-3 px-4 sm:px-5">
          <span className="hidden rounded border border-emerald-500/25 bg-emerald-500/10 px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-emerald-400 sm:inline-flex">
            RAG · LIVE DATA
          </span>
          <UserChip />
        </div>
      </header>

      {/* ── Body ───────────────────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">
        {/* Mobile backdrop — click to close */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/60 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* ── Sidebar ──────────────────────────────────────────────── */}
        {/* On mobile: fixed overlay that slides in from left.        */}
        {/* On desktop (lg+): static flex child, always visible.      */}
        <aside
          className={`fixed inset-y-0 left-0 z-50 flex w-[260px] shrink-0 flex-col overflow-y-auto border-r border-white/[0.06] bg-[#0f1623] pb-4 transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          {/* Close button — mobile only */}
          <div className="flex items-center justify-between px-4 pb-1 pt-4 lg:hidden">
            <span className="font-mono text-[10px] font-semibold uppercase tracking-widest text-slate-500">
              Menu
            </span>
            <button
              onClick={() => setSidebarOpen(false)}
              className="flex h-7 w-7 items-center justify-center rounded-md text-slate-400 transition-colors hover:text-white"
              aria-label="Close menu"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

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
                  <span className="flex-1 truncate text-[12.5px] text-slate-300">
                    {s.name}
                  </span>
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
                  className={`cursor-pointer rounded-md border-l-2 bg-white/[0.03] py-2 pl-3 pr-2.5 transition-colors hover:bg-white/[0.06] ${
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
                  <p className="mt-0.5 text-[11px] leading-snug text-slate-400">
                    {a.desc}
                  </p>
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
            <QuickQueriesPanel />
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
