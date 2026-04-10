const CARDS = [
  {
    label: "INVENTORY",
    labelStyle: "text-blue-500 bg-blue-500/8 border-blue-500/20",
    query: "Check stock levels across all warehouses",
  },
  {
    label: "ORDERS",
    labelStyle: "text-violet-500 bg-violet-500/8 border-violet-500/20",
    query: "View pending and delayed shipments",
  },
  {
    label: "CUSTOMERS",
    labelStyle: "text-emerald-600 bg-emerald-500/8 border-emerald-500/20",
    query: "Analyze top customer purchase patterns",
  },
  {
    label: "ACTIONS",
    labelStyle: "text-amber-600 bg-amber-500/8 border-amber-500/20",
    query: "Trigger bulk reorder for low-stock items",
  },
] as const;

const CARD_DELAYS = ["[animation-delay:60ms]", "[animation-delay:120ms]", "[animation-delay:180ms]", "[animation-delay:240ms]"];

export function WelcomeScreen() {
  return (
    <div className="flex flex-col items-center py-12 text-center animate-in fade-in-0 slide-in-from-bottom-3 duration-500">
      {/* DQ icon tile */}
      <div
        className="flex h-[52px] w-[52px] items-center justify-center rounded-2xl bg-blue-600"
        style={{
          boxShadow:
            "0 0 0 6px rgba(37,99,235,0.10), 0 8px 28px rgba(37,99,235,0.30)",
        }}
      >
        <span className="font-mono text-[15px] font-bold tracking-tight text-white">DQ</span>
      </div>

      {/* Heading */}
      <h1 className="mt-5 text-[26px] font-semibold tracking-tight text-slate-800">
        DistroIQ
      </h1>

      {/* Subtitle */}
      <p className="mt-2 max-w-[340px] text-[13px] leading-relaxed text-slate-400">
        AI Operations Assistant · Ask anything about inventory, orders, customers, or
        suppliers
      </p>

      {/* 2×2 card grid */}
      <div className="mt-8 grid w-full max-w-[400px] grid-cols-2 gap-3">
        {CARDS.map((card, i) => (
          <button
            key={card.label}
            className={`group flex flex-col items-start gap-2 rounded-xl border border-slate-200 bg-white p-3.5 text-left shadow-sm transition-all hover:border-slate-300 hover:shadow-md active:scale-[0.98] animate-in fade-in-0 slide-in-from-bottom-2 duration-500 fill-mode-both ${CARD_DELAYS[i]}`}
          >
            <span
              className={`rounded border px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider ${card.labelStyle}`}
            >
              {card.label}
            </span>
            <p className="text-[12.5px] leading-snug text-slate-600 group-hover:text-slate-800">
              {card.query}
            </p>
          </button>
        ))}
      </div>

    </div>
  );
}
