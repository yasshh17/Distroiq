"use client";

import { ChevronRight } from "lucide-react";

import { useChatStore } from "@/stores/chat";

const QUERIES = [
  "Inventory by warehouse",
  "Pending orders > 48h",
  "Low stock SKUs",
  "Top suppliers this week",
  "Customer order history",
  "Reorder recommendations",
];

export function QuickQueriesPanel() {
  const sendMessage = useChatStore((s) => s.sendMessage);
  const isStreaming = useChatStore((s) => s.isStreaming);

  return (
    <div className="flex flex-col gap-0.5">
      {QUERIES.map((q) => (
        <button
          key={q}
          disabled={isStreaming}
          onClick={() => sendMessage(q)}
          className="group flex items-center gap-2 rounded-md px-2 py-[7px] text-left text-[12px] text-slate-400 transition-colors hover:bg-white/[0.05] hover:text-slate-200 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <ChevronRight className="h-3 w-3 shrink-0 text-slate-600 transition-colors group-hover:text-blue-400" />
          {q}
        </button>
      ))}
    </div>
  );
}
