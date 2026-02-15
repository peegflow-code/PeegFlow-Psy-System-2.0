import React from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
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
  return (
    <Shell
      title="Painel Admin"
      user={user}
      onLogout={onLogout}
      nav={
        <>
          <Tab to="/admin" label="Dashboard" />
          <Tab to="/admin/agenda" label="Agenda" />
          <Tab to="/admin/patients" label="Pacientes" />
          <Tab to="/admin/finance" label="Financeiro" />
          <Tab to="/admin/session-notes" label="Prontuários" />
        </>
      }
    >
      <Outlet />
    </Shell>
  );
}