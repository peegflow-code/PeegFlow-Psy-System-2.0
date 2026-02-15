import React, { useEffect, useMemo, useState } from "react";
import { api } from "../../lib/api";
import { yyyyMm } from "../../lib/dates";
import Modal from "../../ui/Modal";

export default function SessionNotes() {
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState("");
  const [month, setMonth] = useState(yyyyMm());
  const [notes, setNotes] = useState([]);

  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [content, setContent] = useState("");
  const [sessionDate, setSessionDate] = useState(new Date().toISOString().slice(0, 10));
  const [locked, setLocked] = useState(false);
  const [busy, setBusy] = useState(false);

  async function loadPatients() {
    const { data } = await api.get("/patients");
    setPatients(data);
    if (!patientId && data.length) setPatientId(String(data[0].id));
  }

  async function loadNotes(pid = patientId, m = month) {
    if (!pid) return;
    const { data } = await api.get(`/session-notes/patient/${pid}?month=${m}`);
    setNotes(data);
  }

  useEffect(() => {
    loadPatients();
  }, []);

  useEffect(() => {
    loadNotes();
  }, [patientId, month]);

  function startCreate() {
    setEditing(null);
    setContent("");
    setLocked(false);
    setSessionDate(new Date().toISOString().slice(0, 10));
    setOpen(true);
  }

  function startEdit(n) {
    setEditing(n);
    setContent(n.content || "");
    setLocked(!!n.is_locked);
    setSessionDate(n.session_date || new Date().toISOString().slice(0, 10));
    setOpen(true);
  }

  async function save() {
    setBusy(true);
    try {
      if (!patientId) return;

      if (editing) {
        await api.patch(`/session-notes/${editing.id}`, {
          content,
          is_locked: locked,
          session_date: sessionDate,
        });
      } else {
        await api.post("/session-notes", {
          patient_id: Number(patientId),
          content,
          is_locked: locked,
          session_date: sessionDate,
        });
      }
      setOpen(false);
      await loadNotes();
    } finally {
      setBusy(false);
    }
  }

  const pdfUrl = (noteId) => `${import.meta.env.VITE_API_URL}/session-notes/${noteId}/pdf`;

  return (
    <div className="space-y-4">
      <div className="glass rounded-3xl p-4 flex flex-col md:flex-row gap-3 md:items-center">
        <select
          className="rounded-2xl border border-slate-200 px-3 py-2 bg-white"
          value={patientId}
          onChange={(e) => setPatientId(e.target.value)}
        >
          {patients.map((p) => (
            <option key={p.id} value={p.id}>
              {p.full_name}
            </option>
          ))}
        </select>

        <input className="rounded-2xl border border-slate-200 px-3 py-2 bg-white" type="month" value={month} onChange={(e) => setMonth(e.target.value)} />

        <button className="ml-auto rounded-2xl px-3 py-2 bg-lilac-600 hover:bg-lilac-700 text-white" onClick={startCreate}>
          Novo prontuário
        </button>
      </div>

      <div className="glass rounded-3xl p-4 space-y-2">
        {notes.map((n) => (
          <div key={n.id} className="rounded-2xl bg-white/60 border border-lilac-100 p-3 flex items-center gap-3">
            <div className="flex-1">
              <div className="font-medium">
                #{n.id} • {n.session_date || "-"} • {n.is_locked ? "Bloqueado" : "Editável"}
              </div>
              <div className="text-xs text-slate-600 line-clamp-2">{n.content || "(sem conteúdo)"}</div>
            </div>

            <a
              className="rounded-2xl px-3 py-2 bg-white border border-slate-200"
              href={pdfUrl(n.id)}
              target="_blank"
              rel="noreferrer"
            >
              PDF
            </a>

            <button
              disabled={n.is_locked}
              className="rounded-2xl px-3 py-2 bg-white border border-slate-200 disabled:opacity-50"
              onClick={() => startEdit(n)}
            >
              Editar
            </button>
          </div>
        ))}
        {notes.length === 0 && <div className="text-sm text-slate-500">Nenhum prontuário no mês</div>}
      </div>

      <Modal
        open={open}
        title={editing ? "Editar prontuário" : "Novo prontuário"}
        onClose={() => setOpen(false)}
        footer={
          <div className="flex justify-end gap-2">
            <button className="rounded-2xl px-3 py-2 bg-white border border-slate-200" onClick={() => setOpen(false)}>
              Cancelar
            </button>
            <button disabled={busy} className="rounded-2xl px-3 py-2 bg-lilac-600 hover:bg-lilac-700 text-white" onClick={save}>
              Salvar
            </button>
          </div>
        }
      >
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div>
              <label className="text-sm text-slate-600">Data da sessão</label>
              <input className="mt-1 rounded-2xl border border-slate-200 px-3 py-2 bg-white" type="date" value={sessionDate} onChange={(e) => setSessionDate(e.target.value)} />
            </div>

            <label className="mt-6 flex items-center gap-2 text-sm text-slate-700">
              <input type="checkbox" checked={locked} onChange={(e) => setLocked(e.target.checked)} />
              Bloquear (não permite editar depois)
            </label>
          </div>

          <div>
            <label className="text-sm text-slate-600">Conteúdo</label>
            <textarea className="mt-1 w-full min-h-[180px] rounded-2xl border border-slate-200 px-3 py-2 bg-white" value={content} onChange={(e) => setContent(e.target.value)} />
          </div>
        </div>
      </Modal>
    </div>
  );
}