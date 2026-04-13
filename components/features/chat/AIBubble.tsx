import type { ReactNode } from "react";

interface AIBubbleProps {
  children: ReactNode;
}

export function AIBubble({ children }: AIBubbleProps) {
  return (
    <div className="max-w-[90%] rounded-lg rounded-tl-sm border border-slate-200 bg-white px-4 py-3 text-[13.5px] leading-relaxed text-slate-700 shadow-sm sm:max-w-[88%]">
      {children}
    </div>
  );
}
