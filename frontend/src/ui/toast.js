let listeners = [];
export function toast(message, type = "info") {
  listeners.forEach((fn) => fn({ id: crypto.randomUUID(), message, type }));
}
export function subscribeToasts(fn) {
  listeners.push(fn);
  return () => (listeners = listeners.filter((x) => x !== fn));
}