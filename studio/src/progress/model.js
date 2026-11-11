export const statuses = ["implemented", "partial", "not_implemented", "unverified"];
export const statusNames = {
  implemented: ["已实现", "Implemented"], partial: ["部分实现", "Partial"],
  not_implemented: ["未实现", "Not implemented"], unverified: ["未验证", "Unverified"],
};
export function countStatuses(rows) {
  const counts = Object.fromEntries(statuses.map(s => [s, 0]));
  rows.forEach(row => { if (row.status in counts) counts[row.status]++; });
  return counts;
}
export function filterRows(rows, filters) {
  const query = (filters.query || "").toLowerCase().trim();
  return rows.filter(row => (!filters.family || row.family === filters.family) &&
    (!filters.module || row.module === filters.module) && (!filters.status || row.status === filters.status) &&
    (!filters.kind || row.kind === filters.kind) && (!filters.hardware || row.hardware === filters.hardware) &&
    (!query || `${row.name} ${row.signature || ""} ${row.file || ""} ${(row.exposures || []).join(" ")}`.toLowerCase().includes(query)));
}
export const isStale = (generatedAt, now = Date.now()) => now - Date.parse(generatedAt) > 12 * 3600000;
export function aggregate(rows) {
  const groups = new Map();
  for (const row of rows) {
    if (!groups.has(row.family)) groups.set(row.family, []);
    groups.get(row.family).push(row);
  }
  return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([name, items]) => ({ name, total: items.length, counts: countStatuses(items) }));
}
