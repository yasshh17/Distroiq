import { Mail } from "lucide-react";

interface EmailCardProps {
  to: string;
  cc?: string;
  subject: string;
  body: string;
}

export function EmailCard({ to, cc, subject, body }: EmailCardProps) {
  return (
    <div className="my-1 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      {/* Header bar */}
      <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50 px-3.5 py-2">
        <Mail className="h-3.5 w-3.5 shrink-0 text-slate-400" />
        <span className="font-mono text-[10.5px] font-semibold uppercase tracking-wider text-slate-500">
          Email Draft
        </span>
      </div>

      {/* Fields */}
      <div className="divide-y divide-slate-100 border-b border-slate-100 px-3.5">
        <div className="flex items-baseline gap-3 py-2">
          <span className="w-10 shrink-0 font-mono text-[10.5px] uppercase tracking-wider text-slate-400">
            To
          </span>
          <span className="text-[12.5px] text-slate-700">{to}</span>
        </div>
        {cc && (
          <div className="flex items-baseline gap-3 py-2">
            <span className="w-10 shrink-0 font-mono text-[10.5px] uppercase tracking-wider text-slate-400">
              Cc
            </span>
            <span className="text-[12.5px] text-slate-500">{cc}</span>
          </div>
        )}
        <div className="flex items-baseline gap-3 py-2">
          <span className="w-10 shrink-0 font-mono text-[10.5px] uppercase tracking-wider text-slate-400">
            Re
          </span>
          <span className="text-[12.5px] font-medium text-slate-700">{subject}</span>
        </div>
      </div>

      {/* Body */}
      <div className="px-3.5 py-3">
        <p className="whitespace-pre-wrap text-[12.5px] leading-relaxed text-slate-600">{body}</p>
      </div>
    </div>
  );
}
