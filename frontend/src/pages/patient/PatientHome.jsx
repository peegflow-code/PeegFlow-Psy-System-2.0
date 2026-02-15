import React, { useEffect, useMemo, useState } from "react";
import { api } from "../../lib/api";
import { formatBr } from "../../lib/dates";

export default function PatientHome() {
  const [available, setAvailable] = useState([]);
  const [mine, setMine] = useState([]);
  const [busy, setBusy] = useState(false);

  async function load() {
    const a = await api.get("/appointments/available");
    const m = await api.get("/appointments/mine");
    setAvailable(a.data);
    setMine(m.data);
  }

  useEffect(() => {
    load();
  }, []);

  // ✅ Some com horários antigos (past)
  const availableFuture = useMemo(() => {
    const now = Date.now();
    return (available || []).filter((a) => new Date(a.start_at).getTime() > now);
  }, [available]);

  async function book(id) {
    setBusy(true);
    try {
      await api.post("/appointments/book", { appointment_id: id });
      await load();
    } finally {
      setBusy(false);
    }
  }

  async function cancel(id) {
    setBusy(true);
    try {
      await api.post("/appointments/cancel", { appointment_id: id });
      await load();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div className="glass rounded-3xl p-4">
        <div className="font-semibold mb-2">Horários disponíveis</div>
        <div className="space-y-2">
          {availableFuture.map((a) => (
            <div
              key={a.id}
              className="rounded-2xl bg-white/60 border border-lilac-100 p-3 flex items-center gap-3"
            >
              <div className="flex-1">
                <div className="font-medium">{formatBr(a.start_at)}</div>
                <div className="text-xs text-slate-600">
                  R$ {Number(a.price || 0).toFixed(2)}
                </div>
              </div>
              <button
                disabled={busy}
                className="rounded-2xl px-3 py-2 bg-lilac-600 hover:bg-lilac-700 text-white"
                onClick={() => book(a.id)}
              >
                Agendar
              </button>
            </div>
          ))}

          {availableFuture.length === 0 && (
            <div className="text-sm text-slate-500">Nenhum horário disponível</div>
          )}
        </div>
      </div>

      <div className="glass rounded-3xl p-4">
        <div className="font-semibold mb-2">Minhas consultas</div>
        <div className="space-y-2">
          {mine.map((a) => (
            <div
              key={a.id}
              className="rounded-2xl bg-white/60 border border-lilac-100 p-3 flex items-center gap-3"
            >
              <div className="flex-1">
                <div className="font-medium">{formatBr(a.start_at)}</div>
                <div className="text-xs text-slate-600">Status: {a.status}</div>
              </div>
              {a.status === "booked" && (
                <button
                  disabled={busy}
                  className="rounded-2xl px-3 py-2 bg-white border border-slate-200"
                  onClick={() => cancel(a.id)}
                >
                  Cancelar
                </button>
              )}
            </div>
          ))}
          {mine.length === 0 && (
            <div className="text-sm text-slate-500">Você ainda não marcou consultas</div>
          )}
        </div>
      </div>
    </div>
  );
}