import type { ReactNode } from "react";

interface MessageRowProps {
  role: "user" | "ai";
  children: ReactNode;
  timestamp?: string;
}

export function MessageRow({ role, children, timestamp }: MessageRowProps) {
  const isUser = role === "user";

  return (
    <div className={`flex gap-2.5 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      {/* Avatar */}
      {isUser ? (
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-700 shadow-sm">
          <span className="font-mono text-[10px] font-semibold text-white">U</span>
        </div>
      ) : (
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-blue-600 shadow-sm">
          <span className="font-mono text-[10px] font-bold text-white">DQ</span>
        </div>
      )}

      {/* Bubble + timestamp */}
      <div className={`flex flex-col gap-1 ${isUser ? "items-end" : "items-start"}`}>
        {children}
        {timestamp && (
          <span className="px-1 font-mono text-[10px] text-slate-400">{timestamp}</span>
        )}
      </div>
    </div>
  );
}
