import React from "react";

export default function Modal({ open, title, children, onClose, footer }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="absolute inset-0 grid place-items-center p-4">
        <div className="w-full max-w-2xl rounded-3xl bg-white shadow-xl border border-slate-200 overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
            <div className="font-semibold text-slate-900">{title}</div>
            <button onClick={onClose} className="text-slate-500 hover:text-slate-900">
              ✕
            </button>
          </div>

          <div className="p-5">{children}</div>

          {footer && <div className="px-5 py-4 border-t border-slate-200">{footer}</div>}
        </div>
      </div>
    </div>
  );
}