import { StatusBadge } from "./StatusBadge";

interface DataTableProps {
  headers: string[];
  rows: string[][];
  statusCol?: number;
}

export function DataTable({ headers, rows, statusCol }: DataTableProps) {
  return (
    <div className="my-1 overflow-x-auto rounded-lg border border-slate-200">
      <table className="w-full text-left text-[12.5px]">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50">
            {headers.map((h, i) => (
              <th
                key={i}
                className="px-3 py-2 font-mono text-[10.5px] font-semibold uppercase tracking-wider text-slate-500"
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
              className={`border-b border-slate-100 last:border-0 ${
                ri % 2 === 0 ? "bg-white" : "bg-slate-50/50"
              } hover:bg-blue-50/30 transition-colors`}
            >
              {row.map((cell, ci) => (
                <td key={ci} className="px-3 py-2 text-slate-700">
                  {ci === statusCol ? <StatusBadge status={cell} /> : cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
