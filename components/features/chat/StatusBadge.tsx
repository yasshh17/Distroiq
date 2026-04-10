interface StatusBadgeProps {
  status: string;
}

type Tier = "red" | "amber" | "green" | "blue" | "default";

const TIER_MAP: Record<string, Tier> = {
  CRITICAL: "red",
  HIGH: "red",
  PENDING: "red",
  LOW: "amber",
  WARN: "amber",
  WARNING: "amber",
  "AT RISK": "amber",
  OK: "green",
  ACTIVE: "green",
  DELIVERED: "green",
  FULFILLED: "green",
  "IN PICK": "blue",
  PICKING: "blue",
  "IN TRANSIT": "blue",
};

const TIER_STYLES: Record<Tier, { badge: string; dot: string }> = {
  red: {
    badge: "text-red-600 bg-red-50 border-red-200",
    dot: "bg-red-500",
  },
  amber: {
    badge: "text-amber-600 bg-amber-50 border-amber-200",
    dot: "bg-amber-400",
  },
  green: {
    badge: "text-emerald-600 bg-emerald-50 border-emerald-200",
    dot: "bg-emerald-400",
  },
  blue: {
    badge: "text-blue-600 bg-blue-50 border-blue-200",
    dot: "bg-blue-400",
  },
  default: {
    badge: "text-slate-600 bg-slate-50 border-slate-200",
    dot: "bg-slate-400",
  },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const tier = TIER_MAP[status.toUpperCase()] ?? "default";
  const styles = TIER_STYLES[tier];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded border px-1.5 py-0.5 font-mono text-[10.5px] font-medium uppercase tracking-wide ${styles.badge}`}
    >
      <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${styles.dot}`} />
      {status}
    </span>
  );
}
