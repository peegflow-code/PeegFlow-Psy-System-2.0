import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { saveToken } from "../lib/auth";

export default function Login({ onLoggedIn }) {
  const nav = useNavigate();
  const [email, setEmail] = useState("admin@teste.com");
  const [password, setPassword] = useState("123456");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function submit(e) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      const form = new URLSearchParams();
      form.append("username", email);
      form.append("password", password);

      const { data } = await api.post("/auth/login", form, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      saveToken(data.access_token);
      await onLoggedIn?.();
      nav("/");
    } catch (e2) {
      setErr(e2?.response?.data?.detail || "Falha no login");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen page-bg grid place-items-center p-4">
      <div className="w-full max-w-md glass rounded-[28px] p-6">
        <div className="flex items-center gap-3 mb-5">
          <div className="h-11 w-11 rounded-2xl bg-lilac-600 text-white grid place-items-center shadow-soft font-bold">
            PF
          </div>
          <div>
            <div className="text-xl font-semibold leading-tight">PeegFlow</div>
            <div className="text-sm text-slate-500">Psy System • Login</div>
          </div>
        </div>

        {err && (
          <div className="mb-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 px-3 py-2 text-sm">
            {err}
          </div>
        )}

        <form onSubmit={submit} className="space-y-3">
          <div>
            <label className="text-sm text-slate-600">Email</label>
            <input
              className="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-lilac-300"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              required
            />
          </div>

          <div>
            <label className="text-sm text-slate-600">Senha</label>
            <input
              className="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-lilac-300"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
            />
          </div>

          <button
            disabled={loading}
            className="w-full rounded-2xl bg-lilac-600 hover:bg-lilac-700 text-white px-4 py-2 font-medium"
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}