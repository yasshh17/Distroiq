import type { ReactNode } from "react";

interface AIBubbleProps {
  children: ReactNode;
}

export function AIBubble({ children }: AIBubbleProps) {
  return (
    <div
      className="w-full border border-white/[0.08] bg-[#1f2a3d] px-4 py-3 text-[13.5px] leading-relaxed"
      style={{ borderRadius: "2px 12px 12px 12px" }}
    >
      {children}
    </div>
  );
}
