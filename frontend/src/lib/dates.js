export function yyyyMm(date = new Date()) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  return `${y}-${m}`;
}

export function yyyyMmDd(date = new Date()) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function addDays(date, days) {
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return d;
}

export function startOfWeek(date) {
  const d = new Date(date);
  const day = d.getDay(); // 0 domingo
  const diff = (day === 0 ? -6 : 1) - day; // segunda como início
  return addDays(d, diff);
}

export function formatBr(dt) {
  const d = new Date(dt);
  return d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}