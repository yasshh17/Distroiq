import { Send } from "lucide-react";
import { WelcomeScreen } from "@/components/features/chat/WelcomeScreen";

const TABS = ["All", "Inventory", "Orders", "Customers", "Suppliers", "Actions"] as const;

export default function DashboardPage() {
  return (
    <>
      {/* ── Toolbar ──────────────────────────────────────────────── */}
      <div className="flex h-[50px] shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4">
        <div className="flex items-center gap-0.5">
          {TABS.map((tab) => (
            <button
              key={tab}
              className={`rounded-md px-3 py-1.5 text-[12.5px] font-medium transition-colors ${
                tab === "All"
                  ? "bg-slate-900 text-white"
                  : "text-slate-500 hover:bg-slate-100 hover:text-slate-700"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          <span className="font-mono text-[11px] text-slate-400">Session · 00:00:00</span>
        </div>
      </div>

      {/* ── Message area ─────────────────────────────────────────── */}
      <div className="flex flex-1 flex-col overflow-y-auto">
        <div className="mx-auto w-full max-w-3xl flex-1 px-6">
          {/* Welcome state — replace with message list when messages exist */}
          <WelcomeScreen />
        </div>
      </div>

      {/* ── Input bar ────────────────────────────────────────────── */}
      <div className="shrink-0 bg-white px-4 pb-4 pt-3 shadow-[0_-1px_0_0_rgb(226,232,240)]">
        <div className="mx-auto max-w-3xl">
          <div className="flex items-end gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 transition-all focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100">
            <textarea
              rows={1}
              placeholder="Ask about inventory, orders, suppliers, customers…"
              className="flex-1 resize-none bg-transparent text-[13.5px] leading-relaxed text-slate-700 placeholder:text-slate-400 focus:outline-none"
            />
            <button className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-600 shadow-sm transition-colors hover:bg-blue-700 active:bg-blue-800">
              <Send className="h-3.5 w-3.5 text-white" />
            </button>
          </div>
          <p className="mt-2 text-center font-mono text-[10px] text-slate-300">
            RAG-powered · Responses grounded in live operational data
          </p>
        </div>
      </div>
    </>
  );
}
