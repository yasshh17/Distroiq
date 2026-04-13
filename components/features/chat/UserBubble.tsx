import type { ReactNode } from "react";

interface UserBubbleProps {
  children: ReactNode;
}

export function UserBubble({ children }: UserBubbleProps) {
  return (
    <div className="max-w-[90%] rounded-lg rounded-tr-sm bg-blue-600 px-4 py-2.5 text-[13.5px] leading-relaxed text-white shadow-sm sm:max-w-[75%]">
      {children}
    </div>
  );
}
