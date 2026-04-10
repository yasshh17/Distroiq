import { AlertCircle, AlertTriangle, CheckCircle2, Info } from "lucide-react";

type AlertType = "danger" | "warn" | "ok" | "info";

interface AlertBannerProps {
  type: AlertType;
  title: string;
  message: string;
}

const ALERT_STYLES: Record<
  AlertType,
  { container: string; icon: string; title: string; Icon: React.ComponentType<{ className?: string }> }
> = {
  danger: {
    container: "border-l-red-500 bg-red-50/60 border-red-200/60",
    icon: "text-red-500",
    title: "text-red-700",
    Icon: AlertCircle,
  },
  warn: {
    container: "border-l-amber-400 bg-amber-50/60 border-amber-200/60",
    icon: "text-amber-500",
    title: "text-amber-700",
    Icon: AlertTriangle,
  },
  ok: {
    container: "border-l-emerald-500 bg-emerald-50/60 border-emerald-200/60",
    icon: "text-emerald-500",
    title: "text-emerald-700",
    Icon: CheckCircle2,
  },
  info: {
    container: "border-l-blue-500 bg-blue-50/60 border-blue-200/60",
    icon: "text-blue-500",
    title: "text-blue-700",
    Icon: Info,
  },
};

export function AlertBanner({ type, title, message }: AlertBannerProps) {
  const styles = ALERT_STYLES[type];
  const { Icon } = styles;

  return (
    <div
      className={`my-1 flex items-start gap-2.5 rounded-r-lg border border-l-[3px] px-3.5 py-2.5 ${styles.container}`}
    >
      <Icon className={`mt-px h-4 w-4 shrink-0 ${styles.icon}`} />
      <div>
        <p className={`text-[12.5px] font-semibold ${styles.title}`}>{title}</p>
        <p className="mt-0.5 text-[12px] leading-snug text-slate-600">{message}</p>
      </div>
    </div>
  );
}
