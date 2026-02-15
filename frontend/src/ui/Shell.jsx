import React from "react";

export default function Shell({ title, user, onLogout, children, nav }) {
  return (
    <div className="min-h-screen page-bg">
      {/* ✅ minmax(0,1fr) + main min-w-0: evita estouro e cortes */}
      <div className="max-w-7xl mx-auto px-4 py-5 grid grid-cols-1 lg:grid-cols-[280px_minmax(0,1fr)] gap-4">
        <aside className="glass rounded-3xl p-4 h-fit sticky top-4">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-11 w-11 rounded-2xl bg-lilac-600 text-white grid place-items-center shadow-soft font-bold">
              PF
            </div>
            <div>
              <div className="font-semibold leading-tight">PeegFlow</div>
              <div className="text-xs text-slate-500">Psy system</div>
            </div>
          </div>

          <div className="text-xs text-slate-500 mb-3">
            {user?.email} • <span className="font-medium">{user?.role}</span>
          </div>

          {/* ✅ min-w-0 ajuda o nav a não estourar */}
          <div className="space-y-2 min-w-0">{nav}</div>

          <button
            onClick={onLogout}
            className="mt-4 w-full px-3 py-2 rounded-2xl bg-white/60 border border-lilac-100 hover:bg-lilac-50 text-slate-700 flex items-center justify-center gap-2"
          >
            Sair
          </button>
        </aside>

        {/* ✅ min-w-0 evita que conteúdo empurre/corte a sidebar */}
        <main className="min-w-0 space-y-4">
          <div className="glass rounded-3xl p-4">
            <div className="text-lg font-semibold">{title}</div>
            <div className="text-sm text-slate-500">Sistema • Área {user?.role}</div>
          </div>
          {children}
        </main>
      </div>
    </div>
  );
}