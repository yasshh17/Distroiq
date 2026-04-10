import { Database } from "lucide-react";

interface SourceCitationProps {
  sources: string[];
}

export function SourceCitation({ sources }: SourceCitationProps) {
  if (sources.length === 0) return null;

  return (
    <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
      <Database className="h-3 w-3 shrink-0 text-slate-400" />
      <span className="font-mono text-[10px] text-slate-400">Sources:</span>
      {sources.map((src) => (
        <span
          key={src}
          className="inline-flex items-center gap-1 rounded border border-slate-200 bg-slate-50 px-2 py-0.5 font-mono text-[10px] text-slate-500"
        >
          <span className="h-1 w-1 rounded-full bg-emerald-400" />
          {src}
        </span>
      ))}
    </div>
  );
}
