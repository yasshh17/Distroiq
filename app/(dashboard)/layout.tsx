"use client";

import { useState, useEffect } from "react";
import type { ReactNode } from "react";
import {
  Menu,
  X,
  Database,
  AlertTriangle,
  MessageSquare,
  Activity,
  AlertCircle,
  Bell,
  Settings2,
  Plus,
  ChevronRight,
  ChevronLeft,
} from "lucide-react";

import { QuickQueriesPanel } from "@/components/features/sidebar/QuickQueriesPanel";
import { UserChip } from "@/components/features/auth/UserChip";
import { useChatStore } from "@/stores/chat";
import type { FilterTab } from "@/types";

const TABS: FilterTab[] = ["All", "Inventory", "Orders", "Customers", "Suppliers", "Actions"];

const SOURCES = [
  { name: "Warehouse ERP", status: "ok" as const, count: "2.4k" },
  { name: "Order Management", status: "ok" as const, count: "847" },
  { name: "Customer DB", status: "warn" as const, count: "12.1k" },
  { name: "Supplier Portal", status: "ok" as const, count: "326" },
  { name: "Analytics DW", status: "warn" as const, count: "89" },
];

const ALERTS = [
  {
    level: "critical" as const,
    title: "Stock Critical",
    desc: "SKU-4821 below reorder point",
    Icon: AlertCircle,
    query: "What is the stock level for SKU-4821 and what is the reorder threshold?",
  },
  {
    level: "warning" as const,
    title: "Order Delays",
    desc: "14 shipments past ETA",
    Icon: AlertTriangle,
    query: "Show me all delayed shipments past their ETA",
  },
  {
    level: "warning" as const,
    title: "Supplier Drop",
    desc: "Response rate down 23%",
    Icon: AlertTriangle,
    query: "Analyze supplier response rate changes and identify the affected suppliers",
  },
];

const NAV_ITEMS = [
  { icon: Database, label: "Data Sources" },
  { icon: AlertTriangle, label: "Operational Alerts", active: true },
  { icon: MessageSquare, label: "Quick Queries" },
  { icon: Activity, label: "System Logs" },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  const activeTab = useChatStore((s) => s.activeTab);
  const setActiveTab = useChatStore((s) => s.setActiveTab);
  const sendMessage = useChatStore((s) => s.sendMessage);
  const clearMessages = useChatStore((s) => s.clearMessages);
  const isStreaming = useChatStore((s) => s.isStreaming);

  // Persist collapse state across refreshes
  useEffect(() => {
    const stored = localStorage.getItem("sidebar-collapsed");
    if (stored !== null) setCollapsed(stored === "true");
  }, []);

  useEffect(() => {
    localStorage.setItem("sidebar-collapsed", String(collapsed));
  }, [collapsed]);

  const sidebarWidth = collapsed ? 64 : 240;

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[#071325]">
      {/* ── Header ─────────────────────────────────────────────────── */}
      <header className="flex h-12 shrink-0 items-stretch border-b border-white/[0.08] bg-[#071325]">
        {/* Brand */}
        <div className="flex shrink-0 items-center gap-2 px-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="mr-1 flex h-7 w-7 items-center justify-center rounded-lg text-white/30 transition-colors hover:bg-white/[0.05] hover:text-white lg:hidden"
            aria-label="Open menu"
          >
            <Menu className="h-4 w-4" />
          </button>
          <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-[#2563eb]">
            <span className="font-grotesk text-[9px] font-bold text-white">DQ</span>
          </div>
          <span className="font-grotesk text-[14px] font-bold text-white">DISTROIQ</span>
          <div className="mx-2 hidden h-4 w-px bg-white/[0.12] lg:block" />
          <span className="font-grotesk hidden text-[10px] uppercase tracking-widest text-white/30 lg:block">
            AI Operations Assistant · Distribution
          </span>
        </div>

        {/* Center — tab navigation */}
        <div className="hidden flex-1 items-end justify-center gap-0.5 px-4 lg:flex">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`font-grotesk border-b-2 px-3 pb-3 pt-2 text-[12px] uppercase tracking-wider transition-colors ${
                tab === activeTab
                  ? "border-[#2563eb] text-white/95"
                  : "border-transparent text-white/30 hover:text-white/95"
              }`}
              style={tab === activeTab ? { borderBottomColor: "var(--kp-accent)" } : undefined}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Right controls */}
        <div className="flex shrink-0 items-center gap-2 px-4">
          <span className="hidden items-center gap-1.5 rounded-[8px] border border-[#22c55e]/25 bg-[#22c55e]/10 px-2 py-1 sm:inline-flex">
            <span
              className="h-1.5 w-1.5 rounded-full bg-[#22c55e]"
              style={{ animation: "breathe 2s ease-in-out infinite" }}
            />
            <span className="font-grotesk text-[10px] uppercase tracking-wider text-[#22c55e]">
              RAG · Live Data
            </span>
          </span>
          <UserChip />
          <button className="flex h-7 w-7 items-center justify-center rounded-lg text-white/30 transition-colors hover:bg-white/[0.05] hover:text-white">
            <Bell className="h-3.5 w-3.5" />
          </button>
          <button className="flex h-7 w-7 items-center justify-center rounded-lg text-white/30 transition-colors hover:bg-white/[0.05] hover:text-white">
            <Settings2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </header>

      {/* ── Body ───────────────────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">
        {/* Mobile backdrop */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/60 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* ── Sidebar ──────────────────────────────────────────────── */}
        <aside
          className={`fixed inset-y-0 left-0 z-50 flex shrink-0 flex-col bg-[#101c2e] lg:relative lg:z-auto ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
          }`}
          style={{
            width: `${sidebarWidth}px`,
            minWidth: `${sidebarWidth}px`,
            transition:
              "width 0.25s ease, min-width 0.25s ease, transform 0.2s ease-in-out",
          }}
        >
          {/* Mobile close */}
          <div className="flex items-center justify-between px-4 pb-1 pt-4 lg:hidden">
            <span className="font-grotesk text-[10px] uppercase tracking-widest text-white/30">
              Menu
            </span>
            <button
              onClick={() => setSidebarOpen(false)}
              className="flex h-6 w-6 items-center justify-center rounded-lg text-white/30 hover:text-white"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Scrollable sidebar content */}
          <div className="flex flex-1 flex-col overflow-x-hidden overflow-y-auto pb-4">
            {/* ── Brand section ──────────────────────────────────── */}
            <div
              className={`flex flex-col pt-5 ${
                collapsed ? "items-center px-2" : "px-4"
              }`}
            >
              {/* DQ icon tile — always visible */}
              <div className="flex h-8 w-8 items-center justify-center rounded-[10px] bg-[#2563eb]">
                <span className="font-grotesk text-[10px] font-bold text-white">DQ</span>
              </div>

              {/* Tagline — expanded only */}
              {!collapsed && (
                <p className="font-grotesk mt-1.5 text-[10px] uppercase tracking-widest text-[#2563eb]">
                  Kinetic Precision
                </p>
              )}

              {/* NEW ANALYSIS button */}
              <div className={`${collapsed ? "mt-4 w-full" : "mt-4 w-full"}`}>
                {collapsed ? (
                  <button
                    onClick={clearMessages}
                    title="New Analysis"
                    className="flex h-9 w-full items-center justify-center rounded-[12px] bg-[#2563eb] transition-colors hover:bg-[#1d4ed8]"
                  >
                    <Plus className="h-4 w-4 text-white" />
                  </button>
                ) : (
                  <button
                    onClick={clearMessages}
                    className="font-grotesk flex w-full items-center justify-center gap-2 rounded-[12px] bg-[#2563eb] py-2.5 text-[12px] font-semibold uppercase tracking-wider text-white transition-colors hover:bg-[#1d4ed8]"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    New Analysis
                  </button>
                )}
              </div>
            </div>

            <div className={`border-t border-white/[0.06] ${collapsed ? "mx-2 my-3" : "mx-4 my-4"}`} />

            {/* ── Navigation ─────────────────────────────────────── */}
            <div className={collapsed ? "px-2" : "px-3"}>
              {!collapsed && (
                <p className="font-grotesk mb-2 px-2 text-[10px] uppercase tracking-widest text-white/30">
                  Navigation
                </p>
              )}
              <div className="flex flex-col gap-px">
                {NAV_ITEMS.map((item) =>
                  collapsed ? (
                    <div
                      key={item.label}
                      title={item.label}
                      className={`flex cursor-pointer items-center justify-center rounded-[8px] p-2.5 transition-colors ${
                        item.active
                          ? "bg-[#1f2a3d] text-[#2563eb]"
                          : "text-white/40 hover:bg-white/[0.04] hover:text-white/70"
                      }`}
                    >
                      <item.icon className="h-4 w-4 shrink-0" />
                    </div>
                  ) : (
                    <div
                      key={item.label}
                      className={`flex cursor-pointer items-center gap-2.5 rounded-[8px] px-2.5 py-2 transition-colors ${
                        item.active
                          ? "border-l-[3px] border-[#2563eb] bg-[#1f2a3d] pl-[7px]"
                          : "text-white/40 hover:bg-white/[0.04] hover:text-white/70"
                      }`}
                    >
                      <item.icon
                        className={`h-3.5 w-3.5 shrink-0 ${item.active ? "text-[#2563eb]" : ""}`}
                      />
                      <span className={`text-[12.5px] ${item.active ? "text-white/90" : ""}`}>
                        {item.label}
                      </span>
                    </div>
                  ),
                )}
              </div>
            </div>

            <div className={`border-t border-white/[0.06] ${collapsed ? "mx-2 my-3" : "mx-4 my-4"}`} />

            {/* ── Connected Sources ───────────────────────────────── */}
            <div className={collapsed ? "px-2" : "px-3"}>
              {!collapsed && (
                <p className="font-grotesk mb-2 px-2 text-[10px] uppercase tracking-widest text-white/30">
                  Connected Sources
                </p>
              )}
              {collapsed ? (
                <div className="flex flex-col items-center gap-2 py-1">
                  {SOURCES.map((s) => (
                    <span
                      key={s.name}
                      title={s.name}
                      className="h-2 w-2 shrink-0 rounded-full"
                      style={{
                        backgroundColor: s.status === "ok" ? "#22c55e" : "#f59e0b",
                      }}
                    />
                  ))}
                </div>
              ) : (
                <div className="rounded-[8px] bg-[#1f2a3d] px-3 py-2">
                  {SOURCES.map((s) => (
                    <div key={s.name} className="flex items-center gap-2 py-[3px]">
                      <span
                        className="h-1.5 w-1.5 shrink-0 rounded-full"
                        style={{
                          backgroundColor: s.status === "ok" ? "#22c55e" : "#f59e0b",
                        }}
                      />
                      <span className="flex-1 truncate text-[11px] text-white/50">
                        {s.name}
                      </span>
                      <span className="font-grotesk text-[9px] text-white/30">
                        {s.count}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className={`border-t border-white/[0.06] ${collapsed ? "mx-2 my-3" : "mx-4 my-4"}`} />

            {/* ── Active Alerts ───────────────────────────────────── */}
            <div className={collapsed ? "px-2" : "px-3"}>
              {!collapsed && (
                <p className="font-grotesk mb-2 px-2 text-[10px] uppercase tracking-widest text-white/30">
                  Active Alerts
                </p>
              )}
              {collapsed ? (
                <div className="flex flex-col gap-1.5">
                  {ALERTS.map((a, i) => (
                    <button
                      key={i}
                      disabled={isStreaming}
                      onClick={() => {
                        sendMessage(a.query);
                        setSidebarOpen(false);
                      }}
                      title={`${a.title}: ${a.desc}`}
                      className="flex h-8 w-full items-center justify-center rounded-[8px] bg-[#1f2a3d] transition-colors hover:bg-[#2a3548] disabled:cursor-not-allowed disabled:opacity-40"
                      style={{
                        borderLeft: `3px solid ${
                          a.level === "critical" ? "#ef4444" : "#f59e0b"
                        }`,
                      }}
                    >
                      <a.Icon
                        className="h-3.5 w-3.5 shrink-0"
                        style={{
                          color: a.level === "critical" ? "#ef4444" : "#f59e0b",
                        }}
                      />
                    </button>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col gap-2">
                  {ALERTS.map((a, i) => (
                    <button
                      key={i}
                      disabled={isStreaming}
                      onClick={() => {
                        sendMessage(a.query);
                        setSidebarOpen(false);
                      }}
                      className="group w-full cursor-pointer rounded-[8px] bg-[#1f2a3d] px-3 py-2.5 text-left transition-colors hover:bg-[#2a3548] disabled:cursor-not-allowed disabled:opacity-40"
                      style={{
                        borderLeft: `3px solid ${
                          a.level === "critical" ? "#ef4444" : "#f59e0b"
                        }`,
                        animation: "alertPulse 3s ease-in-out infinite",
                      }}
                    >
                      <div className="flex items-center gap-1.5">
                        <a.Icon
                          className="h-3 w-3 shrink-0"
                          style={{
                            color: a.level === "critical" ? "#ef4444" : "#f59e0b",
                          }}
                        />
                        <span
                          className="font-grotesk text-[10px] uppercase tracking-wide"
                          style={{
                            color: a.level === "critical" ? "#ef4444" : "#f59e0b",
                          }}
                        >
                          {a.level === "critical" ? "Critical" : "Warning"}
                        </span>
                      </div>
                      <p className="mt-1 text-[12px] font-medium text-white/90">
                        {a.title}
                      </p>
                      <p className="mt-0.5 text-[11px] leading-snug text-white/45">
                        {a.desc}
                      </p>
                      <div className="mt-1.5 flex items-center gap-1 text-[10px] text-white/25 opacity-0 transition-opacity group-hover:opacity-100">
                        <ChevronRight className="h-3 w-3" />
                        <span className="font-grotesk uppercase tracking-wide">
                          Ask DistroIQ
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Queries — expanded only */}
            {!collapsed && (
              <>
                <div className="mx-4 my-4 border-t border-white/[0.06]" />
                <div className="px-3">
                  <p className="font-grotesk mb-2 px-2 text-[10px] uppercase tracking-widest text-white/30">
                    Quick Queries
                  </p>
                  <QuickQueriesPanel />
                </div>
              </>
            )}

            {/* Spacer */}
            <div className="flex-1" />

            {/* ── Bottom — collapse toggle (desktop only) ──────────── */}
            <div className={`hidden pt-3 lg:block ${collapsed ? "px-2 pb-3" : "px-3 pb-3"}`}>
              <div className="mx-1 mb-3 border-t border-white/[0.06]" />
              {collapsed ? (
                <button
                  onClick={() => setCollapsed(false)}
                  title="Expand sidebar"
                  className="flex h-8 w-full items-center justify-center rounded-[8px] border border-white/[0.08] bg-[#1f2a3d] text-white/30 transition-colors hover:border-[#2563eb]/40 hover:text-white/70"
                >
                  <ChevronRight className="h-3.5 w-3.5" />
                </button>
              ) : (
                <button
                  onClick={() => setCollapsed(true)}
                  className="flex h-8 w-full items-center justify-center gap-2 rounded-[8px] border border-white/[0.08] bg-[#1f2a3d] text-white/30 transition-colors hover:border-[#2563eb]/40 hover:text-white/70"
                >
                  <ChevronLeft className="h-3.5 w-3.5" />
                  <span className="font-grotesk text-[10px] uppercase tracking-widest">
                    Collapse
                  </span>
                </button>
              )}
            </div>
          </div>
        </aside>

        {/* ── Main content ─────────────────────────────────────────── */}
        <main
          className="flex flex-1 flex-col overflow-hidden bg-[#071325]"
          style={{
            backgroundImage:
              "radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px)",
            backgroundSize: "24px 24px",
          }}
        >
          {children}
        </main>
      </div>
    </div>
  );
}
