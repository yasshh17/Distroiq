import type { ReactNode } from "react";

interface UserBubbleProps {
  children: ReactNode;
}

export function UserBubble({ children }: UserBubbleProps) {
  return (
    <div
      className="max-w-[75%] bg-[#2563eb] px-4 py-2.5 text-[13px] leading-relaxed text-white"
      style={{ borderRadius: "12px 12px 2px 12px" }}
    >
      {children}
    </div>
  );
}
