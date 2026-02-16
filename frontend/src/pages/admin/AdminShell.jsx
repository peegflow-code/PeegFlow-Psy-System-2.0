import React from "react";
import { Link, Outlet, useLocation, useParams } from "react-router-dom";
import Shell from "../../ui/Shell";

function Tab({ to, label }) {
  const loc = useLocation();
  const active = loc.pathname === to || loc.pathname.startsWith(to + "/");

  return (
    <Link
      to={to}
      className={[
        "block w-full text-center px-3 py-2 rounded-2xl text-sm font-medium transition",
        active
          ? "bg-lilac-600 text-white shadow-soft"
          : "bg-white/60 border border-lilac-100 hover:bg-lilac-50 text-slate-700",
      ].join(" ")}
    >
      {label}
    </Link>
  );
}

export default function AdminShell({ user, onLogout }) {
  const { slug } = useParams(); // ✅ /t/:slug/admin/...

  const base = slug ? `/t/${slug}/admin` : "/admin";

  return (
    <Shell
      title="Painel Admin"
      user={user}
      onLogout={onLogout}
      nav={
        <>
          <Tab to={`${base}`} label="Dashboard" />
          <Tab to={`${base}/agenda`} label="Agenda" />
          <Tab to={`${base}/patients`} label="Pacientes" />
          <Tab to={`${base}/finance`} label="Financeiro" />
          <Tab to={`${base}/session-notes`} label="Prontuários" />
        </>
      }
    >
      <Outlet />
    </Shell>
  );
}