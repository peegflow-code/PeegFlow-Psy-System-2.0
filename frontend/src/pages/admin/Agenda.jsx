import React, { useEffect, useMemo, useState } from "react";
import { api } from "../../lib/api";
import { addDays, formatBr, startOfWeek, yyyyMmDd } from "../../lib/dates";
import Modal from "../../ui/Modal";

const STATUS_LABEL = {
  available: "Disponível",
  booked: "Marcada",
  done: "Concluída",
  canceled: "Cancelada/Bloqueada",
  no_show: "Faltou",
};

function Pill({ s }) {
  const cls =
    s === "available"
      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
      : s === "booked"
      ? "bg-amber-50 text-amber-700 border-amber-200"
      : s === "done"
      ? "bg-sky-50 text-sky-700 border-sky-200"
      : s === "no_show"
      ? "bg-rose-50 text-rose-700 border-rose-200"
      : "bg-slate-100 text-slate-700 border-slate-200";

  return (
    <span className={`text-xs px-2 py-1 rounded-full border ${cls}`}>
      {STATUS_LABEL[s] || s}
    </span>
  );
}

export default function Agenda() {
  const [anchor, setAnchor] = useState(new Date());
  const weekStart = useMemo(() => startOfWeek(anchor), [anchor]);
  const weekEnd = useMemo(() => addDays(weekStart, 6), [weekStart]);

  const [items, setItems] = useState([]);
  const [bulkOpen, setBulkOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  const [bulkDate, setBulkDate] = useState(yyyyMmDd());
  const [startTime, setStartTime] = useState("08:00");
  const [endTime, setEndTime] = useState("18:00");
  const [duration, setDuration] = useState(50);
  const [price, setPrice] = useState(150);

  async function load() {
    const df = yyyyMmDd(weekStart);
    const dt = yyyyMmDd(weekEnd);
    const { data } = await api.get(
      `/appointments/range?date_from=${df}&date_to=${dt}`
    );
    setItems(data);
  }

  useEffect(() => {
    load();
  }, [weekStart]);

  const grouped = useMemo(() => {
    const map = {};
    for (let i = 0; i < 7; i++) {
      const d = yyyyMmDd(addDays(weekStart, i));
      map[d] = [];
    }
    for (const a of items) {
      const key = yyyyMmDd(new Date(a.start_at));
      if (!map[key]) map[key] = [];
      map[key].push(a);
    }
    Object.values(map).forEach((arr) =>
      arr.sort((a, b) => new Date(a.start_at) - new Date(b.start_at))
    );
    return map;
  }, [items, weekStart]);

  async function doBulk() {
    setBusy(true);
    try {
      await api.post("/appointments/bulk", {
        date: bulkDate,
        start_time: startTime,
        end_time: endTime,
        duration_minutes: Number(duration),
        price: Number(price),
      });
      setBulkOpen(false);
      await load();
    } finally {
      setBusy(false);
    }
  }

  async function cancelSlot(id) {
    setBusy(true);
    try {
      await api.post("/appointments/cancel", { appointment_id: id });
      await load();
    } finally {
      setBusy(false);
    }
  }

  async function setStatus(id, status) {
    setBusy(true);
    try {
      await api.post("/appointments/set-status", {
        appointment_id: id,
        status,
      });
      await load();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="glass rounded-3xl p-4 flex flex-col md:flex-row md:items-center gap-3">
        <div className="flex items-center gap-2">
          <button
            className="rounded-2xl px-3 py-2 bg-white/60 border border-lilac-100 hover:bg-lilac-50 text-sm"
            onClick={() => setAnchor(addDays(anchor, -7))}
          >
            ◀ Semana
          </button>

          <button
            className="rounded-2xl px-3 py-2 bg-white/60 border border-lilac-100 hover:bg-lilac-50 text-sm"
            onClick={() => setAnchor(new Date())}
          >
            Hoje
          </button>

          <button
            className="rounded-2xl px-3 py-2 bg-white/60 border border-lilac-100 hover:bg-lilac-50 text-sm"
            onClick={() => setAnchor(addDays(anchor, 7))}
          >
            Semana ▶
          </button>
        </div>

        <div className="text-sm text-slate-600 md:ml-auto">
          {yyyyMmDd(weekStart)} → {yyyyMmDd(weekEnd)}
        </div>

        <button
          className="rounded-2xl px-4 py-2 bg-lilac-600 hover:bg-lilac-700 text-white text-sm font-medium"
          onClick={() => setBulkOpen(true)}
        >
          Criar horários em lote
        </button>
      </div>

      {/* Week Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-7 gap-3">
        {Object.entries(grouped).map(([day, arr]) => (
          <div
            key={day}
            className="glass rounded-3xl p-3 flex flex-col h-[620px] overflow-hidden"
          >
            {/* Day Header */}
            <div className="sticky top-0 z-10 bg-white/70 backdrop-blur rounded-2xl p-2 mb-2 border border-lilac-100">
              <div className="flex items-center justify-between">
                <div className="font-semibold text-sm">{day}</div>
                <div className="text-[11px] text-slate-500">
                  {arr.length} itens
                </div>
              </div>
            </div>

            {/* Scroll Area */}
            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
              {arr.length === 0 && (
                <div className="text-xs text-slate-500">
                  Sem horários
                </div>
              )}

              {arr.map((a) => (
                <div
                  key={a.id}
                  className="rounded-2xl bg-white/60 border border-lilac-100 p-3 space-y-2"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="text-sm font-medium">
                      {formatBr(a.start_at)} →{" "}
                      {new Date(a.end_at).toLocaleTimeString("pt-BR", {
                        timeStyle: "short",
                      })}
                    </div>
                    <Pill s={a.status} />
                  </div>

                  <div className="text-xs text-slate-600">
                    R$ {Number(a.price || 0).toFixed(2)}
                    {a.patient_name &&
                      ` • ${a.patient_name} (${a.patient_email || "-"})`}
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {(a.status === "available" ||
                      a.status === "booked") && (
                      <button
                        disabled={busy}
                        className="text-xs rounded-2xl px-3 py-2 bg-white border border-slate-200 hover:bg-slate-50"
                        onClick={() => cancelSlot(a.id)}
                      >
                        {a.status === "available"
                          ? "Bloquear"
                          : "Cancelar"}
                      </button>
                    )}

                    {a.status === "booked" && (
                      <>
                        <button
                          disabled={busy}
                          className="text-xs rounded-2xl px-3 py-2 bg-white border border-slate-200 hover:bg-slate-50"
                          onClick={() =>
                            setStatus(a.id, "done")
                          }
                        >
                          Marcar done
                        </button>

                        <button
                          disabled={busy}
                          className="text-xs rounded-2xl px-3 py-2 bg-white border border-slate-200 hover:bg-slate-50"
                          onClick={() =>
                            setStatus(a.id, "no_show")
                          }
                        >
                          Marcar no_show
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      <Modal
        open={bulkOpen}
        title="Criar horários em lote"
        onClose={() => setBulkOpen(false)}
        footer={
          <div className="flex justify-end gap-2">
            <button
              className="rounded-2xl px-3 py-2 bg-white border border-slate-200"
              onClick={() => setBulkOpen(false)}
            >
              Cancelar
            </button>
            <button
              disabled={busy}
              className="rounded-2xl px-3 py-2 bg-lilac-600 hover:bg-lilac-700 text-white"
              onClick={doBulk}
            >
              Criar
            </button>
          </div>
        }
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input type="date" value={bulkDate} onChange={(e) => setBulkDate(e.target.value)} className="rounded-2xl border px-3 py-2"/>
          <input type="number" value={duration} onChange={(e) => setDuration(e.target.value)} className="rounded-2xl border px-3 py-2"/>
          <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} className="rounded-2xl border px-3 py-2"/>
          <input type="time" value={endTime} onChange={(e) => setEndTime(e.target.value)} className="rounded-2xl border px-3 py-2"/>
          <input type="number" value={price} onChange={(e) => setPrice(e.target.value)} className="rounded-2xl border px-3 py-2 md:col-span-2"/>
        </div>
      </Modal>
    </div>
  );
}