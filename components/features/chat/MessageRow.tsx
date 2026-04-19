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
        <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-[#2a3548]">
          <span className="font-grotesk text-[8px] font-semibold text-white/60">U</span>
        </div>
      ) : (
        <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-[#2563eb]">
          <span className="font-grotesk text-[8px] font-bold text-white">DQ</span>
        </div>
      )}

      {/* Bubble + timestamp */}
      <div className={`flex flex-col gap-1 ${isUser ? "items-end" : "items-start"} min-w-0 flex-1`}>
        {children}
        {timestamp && (
          <span className="font-grotesk px-1 text-[10px] text-white/25">{timestamp}</span>
        )}
      </div>
    </div>
  );
}
