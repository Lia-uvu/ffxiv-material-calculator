export function clampPositiveInteger(raw) {
  const value = Number(raw);
  if (!Number.isFinite(value)) return 1;
  return Math.max(1, Math.floor(value));
}
