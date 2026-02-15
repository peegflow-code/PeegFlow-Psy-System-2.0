import React, { useEffect, useMemo, useState } from "react";
import { api } from "../../lib/api";
import Modal from "../../ui/Modal";

const EMPTY = {
  full_name: "",
  phone: "",
  email: "",
  birth_date: "",
  sex: "",
  marital_status: "",
  address: "",
  occupation: "",
  emergency_name: "",
  emergency_phone: "",
  document_id: "",
  create_user: true,
  user_password: "123456",
};

export default function Patients() {
  const [items, setItems] = useState([]);
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);

  async function load() {
    const { data } = await api.get("/patients");
    setItems(data);
  }

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s) return items;
    return items.filter(
      (p) =>
        (p.full_name || "").toLowerCase().includes(s) ||
        (p.email || "").toLowerCase().includes(s)
    );
  }, [items, q]);

  function startCreate() {
    setEditing(null);
    setForm(EMPTY);
    setOpen(true);
  }

  function startEdit(p) {
    setEditing(p);
    setForm({
      full_name: p.full_name || "",
      phone: p.phone || "",
      email: p.email || "",
      birth_date: p.birth_date || "",
      sex: p.sex || "",
      marital_status: p.marital_status || "",
      address: p.address || "",
      occupation: p.occupation || "",
      emergency_name: p.emergency_name || "",
      emergency_phone: p.emergency_phone || "",
      document_id: p.document_id || "",
      create_user: false,
      user_password: "123456",
    });
    setOpen(true);
  }

  async function save() {
    setBusy(true);
    try {
      if (editing) {
        await api.patch(`/patients/${editing.id}`, form);
      } else {
        await api.post("/patients", form);
      }
      setOpen(false);
      await load();
    } finally {
      setBusy(false);
    }
  }

  async function removeAccess(p) {
    if (!confirm("Remover acesso do paciente? (ele não conseguirá mais logar)")) return;
    setBusy(true);
    try {
      await api.delete(`/patients/${p.id}/access`);
      await load();
    } finally {
      setBusy(false);
    }
  }

  async function restoreAccess(p) {
    if (!p.email) {
      alert("Esse paciente não tem email. Adicione um email para criar/reativar acesso.");
      return;
    }
    const pwd = prompt("Senha para o acesso do paciente:", "123456");
    if (pwd === null) return;

    setBusy(true);
    try {
      await api.post(`/patients/${p.id}/access`, { password: pwd || "123456" });
      await load();
    } finally {
      setBusy(false);
    }
  }

  async function deletePatient(p) {
    if (!confirm(`Excluir o paciente "${p.full_name}"? Essa ação remove o cadastro.`)) return;
    setBusy(true);
    try {
      await api.delete(`/patients/${p.id}`);
      await load();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="glass rounded-3xl p-4 flex flex-col md:flex-row gap-3 md:items-center">
        <input
          className="flex-1 rounded-2xl border border-slate-200 px-3 py-2 bg-white"
          placeholder="Buscar por nome/email…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button
          className="rounded-2xl px-3 py-2 bg-lilac-600 hover:bg-lilac-700 text-white"
          onClick={startCreate}
        >
          Novo paciente
        </button>
      </div>

      <div className="glass rounded-3xl p-4 overflow-x-auto">
        <table className="min-w-[980px] w-full text-sm">
          <thead className="text-left text-slate-500">
            <tr>
              <th className="py-2">Nome</th>
              <th>Email</th>
              <th>Telefone</th>
              <th>Acesso</th>
              <th className="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((p) => (
              <tr key={p.id} className="border-t border-slate-200">
                <td className="py-3 font-medium">{p.full_name}</td>
                <td>{p.email || "-"}</td>
                <td>{p.phone || "-"}</td>
                <td>{p.user_id ? "Ativo" : "Sem acesso"}</td>
                <td className="text-right">
                  <div className="flex justify-end gap-2 flex-wrap">
                    <button
                      className="rounded-2xl px-3 py-2 bg-white border border-slate-200"
                      onClick={() => startEdit(p)}
                    >
                      Editar
                    </button>

                    {p.user_id ? (
                      <button
                        disabled={busy}
                        className="rounded-2xl px-3 py-2 bg-white border border-slate-200"
                        onClick={() => removeAccess(p)}
                      >
                        Remover acesso
                      </button>
                    ) : (
                      <button
                        disabled={busy}
                        className="rounded-2xl px-3 py-2 bg-white border border-slate-200"
                        onClick={() => restoreAccess(p)}
                      >
                        Reativar acesso
                      </button>
                    )}

                    <button
                      disabled={busy}
                      className="rounded-2xl px-3 py-2 bg-white border border-rose-200 text-rose-700 hover:bg-rose-50"
                      onClick={() => deletePatient(p)}
                    >
                      Excluir
                    </button>
                  </div>
                </td>
              </tr>
            ))}

            {filtered.length === 0 && (
              <tr>
                <td colSpan={5} className="py-6 text-center text-slate-500">
                  Nenhum paciente encontrado
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <Modal
        open={open}
        title={editing ? "Editar paciente" : "Novo paciente"}
        onClose={() => setOpen(false)}
        footer={
          <div className="flex justify-end gap-2">
            <button
              className="rounded-2xl px-3 py-2 bg-white border border-slate-200"
              onClick={() => setOpen(false)}
            >
              Cancelar
            </button>
            <button
              disabled={busy}
              className="rounded-2xl px-3 py-2 bg-lilac-600 hover:bg-lilac-700 text-white"
              onClick={save}
            >
              Salvar
            </button>
          </div>
        }
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            ["full_name", "Nome completo"],
            ["email", "Email"],
            ["phone", "Telefone"],
            ["birth_date", "Nascimento"],
            ["sex", "Sexo"],
            ["marital_status", "Estado civil"],
            ["occupation", "Profissão"],
            ["document_id", "Documento"],
            ["emergency_name", "Contato emergência"],
            ["emergency_phone", "Tel emergência"],
          ].map(([k, label]) => (
            <div key={k}>
              <label className="text-sm text-slate-600">{label}</label>
              <input
                className="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 bg-white"
                value={form[k] || ""}
                onChange={(e) => setForm((s) => ({ ...s, [k]: e.target.value }))}
                type={k === "birth_date" ? "date" : "text"}
              />
            </div>
          ))}

          <div className="md:col-span-2">
            <label className="text-sm text-slate-600">Endereço</label>
            <input
              className="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 bg-white"
              value={form.address || ""}
              onChange={(e) => setForm((s) => ({ ...s, address: e.target.value }))}
            />
          </div>

          {!editing && (
            <div className="md:col-span-2 rounded-2xl border border-slate-200 bg-white/60 p-3">
              <div className="flex items-center justify-between">
                <div className="font-medium">Criar acesso do paciente</div>
                <input
                  type="checkbox"
                  checked={!!form.create_user}
                  onChange={(e) =>
                    setForm((s) => ({ ...s, create_user: e.target.checked }))
                  }
                />
              </div>
              {form.create_user && (
                <div className="mt-3">
                  <label className="text-sm text-slate-600">Senha inicial</label>
                  <input
                    className="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 bg-white"
                    value={form.user_password || ""}
                    onChange={(e) =>
                      setForm((s) => ({ ...s, user_password: e.target.value }))
                    }
                    type="text"
                  />
                </div>
              )}
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
}