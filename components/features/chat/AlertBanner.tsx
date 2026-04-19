import { AlertCircle, AlertTriangle, CheckCircle2, Info } from "lucide-react";

type AlertType = "danger" | "warn" | "ok" | "info";

interface AlertBannerProps {
  type: AlertType;
  title: string;
  message: string;
}

const ALERT_CONFIG: Record<
  AlertType,
  { color: string; bg: string; iconClass: string; Icon: React.ComponentType<{ className?: string }> }
> = {
  danger: { color: "#ef4444", bg: "rgba(239,68,68,0.08)", iconClass: "text-[#ef4444]", Icon: AlertCircle },
  warn: { color: "#f59e0b", bg: "rgba(245,158,11,0.08)", iconClass: "text-[#f59e0b]", Icon: AlertTriangle },
  ok: { color: "#22c55e", bg: "rgba(34,197,94,0.08)", iconClass: "text-[#22c55e]", Icon: CheckCircle2 },
  info: { color: "#3b82f6", bg: "rgba(59,130,246,0.08)", iconClass: "text-[#3b82f6]", Icon: Info },
};

export function AlertBanner({ type, title, message }: AlertBannerProps) {
  const config = ALERT_CONFIG[type];
  const { Icon } = config;

  return (
    <div
      className="my-1.5 flex items-start gap-2.5 rounded-r-[8px] px-3.5 py-2.5"
      style={{
        borderLeft: `3px solid ${config.color}`,
        backgroundColor: config.bg,
      }}
    >
      <Icon className={`mt-px h-4 w-4 shrink-0 ${config.iconClass}`} />
      <div>
        <p className={`font-grotesk text-[11px] font-semibold uppercase tracking-wide ${config.iconClass}`}>
          {title}
        </p>
        <p className="mt-0.5 text-[12px] leading-snug text-white/55">{message}</p>
      </div>
    </div>
  );
}
