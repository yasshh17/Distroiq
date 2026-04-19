import { Database } from "lucide-react";

interface SourceCitationProps {
  sources: string[];
}

export function SourceCitation({ sources }: SourceCitationProps) {
  if (sources.length === 0) return null;

  return (
    <div className="mt-3 flex flex-wrap items-center gap-1.5">
      <Database className="h-3 w-3 shrink-0 text-white/25" />
      <span className="font-grotesk text-[10px] uppercase tracking-wide text-white/30">Sources:</span>
      {sources.map((src) => (
        <span
          key={src}
          className="font-grotesk inline-flex items-center gap-1 rounded border border-white/[0.08] bg-[#2a3548] px-2 py-0.5 text-[10px] uppercase text-white/40"
        >
          <span className="h-1 w-1 rounded-full bg-[#22c55e]" />
          {src}
        </span>
      ))}
    </div>
  );
}
