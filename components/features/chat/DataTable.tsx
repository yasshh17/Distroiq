import { StatusBadge } from "./StatusBadge";

interface DataTableProps {
  headers: string[];
  rows: string[][];
  statusCol?: number;
}

const STATUS_WORDS = new Set([
  "critical", "warning", "ok", "low", "high",
  "pending", "delivered", "urgent", "blocked", "active",
]);

function isStatusText(cell: string): boolean {
  return isNaN(Number(cell)) && STATUS_WORDS.has(cell.toLowerCase());
}

export function DataTable({ headers, rows, statusCol }: DataTableProps) {
  return (
    <div className="my-2 rounded-[8px] border border-white/[0.08]">
      <div className="overflow-x-auto w-full">
        <table className="w-full text-left text-[12.5px]">
          <thead>
            <tr className="border-b border-white/[0.08] bg-[#101c2e]">
              {headers.map((h, i) => (
                <th
                  key={i}
                  className="font-grotesk px-3 py-2 text-[10.5px] uppercase tracking-wider text-white/30"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr
                key={ri}
                className={`border-b border-white/[0.05] last:border-0 transition-colors hover:bg-white/[0.03] ${
                  ri % 2 === 0 ? "bg-[#1f2a3d]" : "bg-transparent"
                }`}
              >
                {row.map((cell, ci) => {
                  const showBadge = ci === statusCol && isStatusText(cell);
                  const isNumeric = /^\d/.test(cell) && ci !== statusCol;
                  return (
                    <td
                      key={ci}
                      className={`px-3 py-2 text-white/70 ${
                        isNumeric ? "font-grotesk text-right tabular-nums" : ""
                      }`}
                    >
                      {showBadge ? (
                        <StatusBadge status={cell} />
                      ) : (
                        ci === statusCol && !showBadge ? (
                          <span className="font-grotesk tabular-nums">{cell}</span>
                        ) : (
                          cell
                        )
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
