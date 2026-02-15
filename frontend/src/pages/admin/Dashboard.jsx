import React, { useEffect, useMemo, useState } from "react";
import { api } from "../../lib/api";
import { yyyyMm } from "../../lib/dates";

function Card({ label, value, sub }) {
  return (
    <div className="glass rounded-3xl p-4">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="text-2xl font-semibold mt-1">{value}</div>
      {sub && <div className="text-xs text-slate-500 mt-1">{sub}</div>}
    </div>
  );
}

export default function Dashboard() {
  const [month, setMonth] = useState(yyyyMm());
  const [data, setData] = useState(null);

  async function load() {
    const { data } = await api.get(`/admin/finance/summary?month=${month}`);
    setData(data);
  }

  useEffect(() => {
    load();
  }, [month]);

  const status = data?.status_counts || {};
  const totalAppts = Object.values(status).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-4">
      <div className="glass rounded-3xl p-4 flex items-center gap-3">
        <div className="text-sm text-slate-600">Período</div>
        <input
          className="rounded-2xl border border-slate-200 px-3 py-2 bg-white"
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
        />
        <div className="text-xs text-slate-500 ml-auto">{data?.period}</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <Card label="Receita" value={`R$ ${data?.income_total?.toFixed?.(2) ?? "0.00"}`} />
        <Card label="Despesas" value={`R$ ${data?.expense_total?.toFixed?.(2) ?? "0.00"}`} />
        <Card label="Saldo" value={`R$ ${data?.cash_total?.toFixed?.(2) ?? "0.00"}`} sub={`Total consultas no período: ${totalAppts}`} />
      </div>

      <div className="glass rounded-3xl p-4">
        <div className="font-semibold mb-2">Status das consultas</div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-sm">
          {["available", "booked", "done", "canceled", "no_show"].map((k) => (
            <div key={k} className="rounded-2xl bg-white/60 border border-lilac-100 px-3 py-2">
              <div className="text-slate-500 text-xs">{k}</div>
              <div className="font-semibold">{status[k] ?? 0}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass rounded-3xl p-4">
        <div className="font-semibold mb-2">Receita diária (mini gráfico)</div>
        <div className="space-y-2">
          {(data?.daily_income || []).slice(-14).map((row) => (
            <div key={row.day} className="flex items-center gap-3">
              <div className="w-24 text-xs text-slate-500">{row.day}</div>
              <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-2 bg-lilac-600"
                  style={{ width: `${Math.min(100, (row.income || 0) / 5)}%` }}
                />
              </div>
              <div className="w-24 text-right text-xs text-slate-700">R$ {Number(row.income || 0).toFixed(2)}</div>
            </div>
          ))}
          {!data?.daily_income?.length && (
            <div className="text-sm text-slate-500">Sem série diária para esse período.</div>
          )}
        </div>
      </div>
    </div>
  );
}