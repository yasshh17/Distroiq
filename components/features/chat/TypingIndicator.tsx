export function TypingIndicator() {
  return (
    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-blue-600 shadow-sm">
      <span className="font-mono text-[10px] font-bold text-white">DQ</span>
    </div>
  );
}

export function TypingBubble() {
  return (
    <div className="flex items-center gap-2.5">
      <TypingIndicator />
      <div className="flex items-center gap-1.5 rounded-lg rounded-tl-sm border border-slate-200 bg-white px-4 py-3 shadow-sm">
        <span className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce-dot" />
        <span className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce-dot [animation-delay:0.2s]" />
        <span className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce-dot [animation-delay:0.4s]" />
      </div>
    </div>
  );
}
