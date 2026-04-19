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

const TIER_COLORS: Record<Tier, { text: string; bg: string; dot: string }> = {
  red: { text: "#ef4444", bg: "rgba(239,68,68,0.15)", dot: "#ef4444" },
  amber: { text: "#f59e0b", bg: "rgba(245,158,11,0.15)", dot: "#f59e0b" },
  green: { text: "#22c55e", bg: "rgba(34,197,94,0.15)", dot: "#22c55e" },
  blue: { text: "#3b82f6", bg: "rgba(59,130,246,0.15)", dot: "#3b82f6" },
  default: { text: "rgba(255,255,255,0.5)", bg: "rgba(255,255,255,0.08)", dot: "rgba(255,255,255,0.4)" },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const tier = TIER_MAP[status.toUpperCase()] ?? "default";
  const colors = TIER_COLORS[tier];

  return (
    <span
      className="font-grotesk inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide"
      style={{ borderRadius: "6px", color: colors.text, backgroundColor: colors.bg }}
    >
      <span
        className="h-1.5 w-1.5 shrink-0 rounded-full"
        style={{ backgroundColor: colors.dot }}
      />
      {status}
    </span>
  );
}
