import React, { useEffect, useState } from "react";
import { api } from "../../lib/api";
import { yyyyMm } from "../../lib/dates";
import Modal from "../../ui/Modal";

export default function Finance() {
  const [month, setMonth] = useState(yyyyMm());
  const [summary, setSummary] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  const [title, setTitle] = useState("");
  const [amount, setAmount] = useState(0);
  const [spentAt, setSpentAt] = useState(new Date().toISOString().slice(0, 10));
  const [notes, setNotes] = useState("");

  async function load() {
    const s = await api.get(`/admin/finance/summary?month=${month}`);
    const e = await api.get(`/admin/expenses?month=${month}`);
    setSummary(s.data);
    setExpenses(e.data);
  }

  useEffect(() => {
    load();
  }, [month]);

  async function addExpense() {
    setBusy(true);
    try {
      await api.post("/admin/expenses", {
        title,
        amount: Number(amount),
        spent_at: spentAt,
        notes: notes || null,
      });
      setOpen(false);
      setTitle("");
      setAmount(0);
      setNotes("");
      await load();
    } finally {
      setBusy(false);
    }
  }

  async function delExpense(id) {
    if (!confirm("Deletar despesa?")) return;
    setBusy(true);
    try {
      await api.delete(`/admin/expenses/${id}`);
      await load();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="glass rounded-3xl p-4 flex items-center gap-3">
        <div className="text-sm text-slate-600">Mês</div>
        <input className="rounded-2xl border border-slate-200 px-3 py-2 bg-white" type="month" value={month} onChange={(e) => setMonth(e.target.value)} />
        <button className="ml-auto rounded-2xl px-3 py-2 bg-lilac-600 hover:bg-lilac-700 text-white" onClick={() => setOpen(true)}>
          Nova despesa
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="glass rounded-3xl p-4">
          <div className="text-sm text-slate-500">Receita</div>
          <div className="text-2xl font-semibold">R$ {Number(summary?.income_total || 0).toFixed(2)}</div>
        </div>
        <div className="glass rounded-3xl p-4">
          <div className="text-sm text-slate-500">Despesas</div>
          <div className="text-2xl font-semibold">R$ {Number(summary?.expense_total || 0).toFixed(2)}</div>
        </div>
        <div className="glass rounded-3xl p-4">
          <div className="text-sm text-slate-500">Saldo</div>
          <div className="text-2xl font-semibold">R$ {Number(summary?.cash_total || 0).toFixed(2)}</div>
        </div>
      </div>

      <div className="glass rounded-3xl p-4">
        <div className="font-semibold mb-3">Despesas do mês</div>
        <div className="space-y-2">
          {expenses.map((e) => (
            <div key={e.id} className="rounded-2xl bg-white/60 border border-lilac-100 p-3 flex items-center gap-3">
              <div className="flex-1">
                <div className="font-medium">{e.title}</div>
                <div className="text-xs text-slate-500">
                  {new Date(e.spent_at).toLocaleDateString("pt-BR")} {e.notes ? `• ${e.notes}` : ""}
                </div>
              </div>
              <div className="font-semibold">R$ {Number(e.amount).toFixed(2)}</div>
              <button disabled={busy} className="rounded-2xl px-3 py-2 bg-white border border-slate-200" onClick={() => delExpense(e.id)}>
                Deletar
              </button>
            </div>
          ))}
          {expenses.length === 0 && <div className="text-sm text-slate-500">Nenhuma despesa cadastrada</div>}
        </div>
      </div>

      <Modal
        open={open}
        title="Nova despesa"
        onClose={() => setOpen(false)}
        footer={
          <div className="flex justify-end gap-2">
            <button className="rounded-2xl px-3 py-2 bg-white border border-slate-200" onClick={() => setOpen(false)}>
              Cancelar
            </button>
            <button disabled={busy} className="rounded-2xl px-3 py-2 bg-lilac-600 hover:bg-lilac-700 text-white" onClick={addExpense}>
              Salvar
            </button>
          </div>
        }
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="md:col-span-2">
            <label className="text-sm text-slate-600">Título</label>
            <input className="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 bg-white" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div>
            <label className="text-sm text-slate-600">Valor</label>
            <input className="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 bg-white" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
          </div>
          <div>
            <label className="text-sm text-slate-600">Data</label>
            <input className="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 bg-white" type="date" value={spentAt} onChange={(e) => setSpentAt(e.target.value)} />
          </div>
          <div className="md:col-span-2">
            <label className="text-sm text-slate-600">Notas</label>
            <input className="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 bg-white" value={notes} onChange={(e) => setNotes(e.target.value)} />
          </div>
        </div>
      </Modal>
    </div>
  );
}