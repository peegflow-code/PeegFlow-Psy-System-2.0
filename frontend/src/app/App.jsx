import React, { useEffect, useState } from "react";
import { Routes, Route, Navigate, useParams } from "react-router-dom";
import { api } from "../lib/api";
import { clearToken } from "../lib/auth";

import Login from "../pages/login";
import AdminShell from "../pages/admin/AdminShell";
import Dashboard from "../pages/admin/Dashboard";
import Agenda from "../pages/admin/Agenda";
import Patients from "../pages/admin/Patients";
import Finance from "../pages/admin/Finance";
import SessionNotes from "../pages/admin/SessionNotes";
import PatientHome from "../pages/patient/PatientHome";

function getTenantSlug() {
  try {
    return localStorage.getItem("tenant_slug") || "";
  } catch {
    return "";
  }
}

// ✅ Wrapper para páginas do paciente com layout igual ao seu (reaproveitável)
function PatientLayout({ user, logout }) {
  return (
    <div className="min-h-screen page-bg p-4">
      <div className="max-w-6xl mx-auto space-y-4">
        <div className="glass rounded-3xl p-4 flex items-center justify-between">
          <div>
            <div className="text-lg font-semibold">Área do Paciente</div>
            <div className="text-sm text-slate-500">{user?.email}</div>
          </div>
          <button
            onClick={logout}
            className="rounded-2xl px-3 py-2 bg-white/60 border border-lilac-100 hover:bg-lilac-50"
          >
            Sair
          </button>
        </div>
        <PatientHome />
      </div>
    </div>
  );
}

// ✅ Root do tenant: /t/:slug
function TenantRoot({ user }) {
  const { slug } = useParams();

  if (!user) return <Navigate to="/login" replace />;

  // manda para a área certa dentro do tenant
  return (
    <Navigate
      to={user.role === "admin" ? `/t/${slug}/admin` : `/t/${slug}/patient`}
      replace
    />
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function loadUser() {
    try {
      const { data } = await api.get("/auth/me");
      setUser(data);
    } catch {
      clearToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUser();
  }, []);

  function logout() {
    clearToken();
    setUser(null);
  }

  if (loading) return <div style={{ padding: 24 }}>Carregando...</div>;

  const slug = getTenantSlug();

  return (
    <Routes>
      {/* Login */}
      <Route
        path="/login"
        element={user ? <Navigate to={slug ? `/t/${slug}` : "/"} replace /> : <Login onLoggedIn={loadUser} />}
      />

      {/* ✅ NOVO: Tenant root */}
      <Route path="/t/:slug" element={<TenantRoot user={user} />} />

      {/* ✅ NOVO: Admin dentro do tenant */}
      <Route
        path="/t/:slug/admin"
        element={
          user?.role === "admin" ? (
            <AdminShell user={user} onLogout={logout} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="agenda" element={<Agenda />} />
        <Route path="patients" element={<Patients />} />
        <Route path="finance" element={<Finance />} />
        <Route path="session-notes" element={<SessionNotes />} />
      </Route>

      {/* ✅ NOVO: Patient dentro do tenant */}
      <Route
        path="/t/:slug/patient"
        element={
          user?.role === "patient" ? (
            <PatientLayout user={user} logout={logout} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      {/* ✅ COMPAT: rotas antigas redirecionam pro tenant salvo */}
      <Route
        path="/admin"
        element={
          slug ? <Navigate to={`/t/${slug}/admin`} replace /> : <Navigate to="/login" replace />
        }
      />
      <Route
        path="/patient"
        element={
          slug ? <Navigate to={`/t/${slug}/patient`} replace /> : <Navigate to="/login" replace />
        }
      />

      {/* Root */}
      <Route
        path="/"
        element={
          user ? (
            slug ? <Navigate to={`/t/${slug}`} replace /> : <Navigate to="/login" replace />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}