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
export function decodeDataset(value) {
  if (Array.isArray(value)) return value;
  if (value?.schema !== 2 || value.encoding !== "signature-pool-v1" || !Array.isArray(value.rows)) throw Error("Unknown inventory encoding");
  return value.rows.map(row => ({ ...row, runtime_observations: row.runtime_observations.map(original => {
    const observation = { ...original };
    if (Object.hasOwn(observation, "signature_ref")) {
      if (Object.hasOwn(observation, "signature") || !Object.hasOwn(value.signatures, observation.signature_ref)) throw Error("Missing or ambiguous signature metadata");
      observation.signature = value.signatures[observation.signature_ref];
      delete observation.signature_ref;
    }
    return observation;
  }) }));
}
export function verificationWindow(rows, page = 0, size = 20) {
  const pages = Math.max(1, Math.ceil(rows.length / size));
  const index = Math.max(0, Math.min(page, pages - 1));
  return { rows: rows.slice().reverse().slice(index * size, (index + 1) * size), index, pages, total: rows.length };
}
export function currentVerification(manifest) {
  const rows = (manifest.verification || []).filter(row => row.source_match && row.environment_validation?.verified);
  const failures = Object.fromEntries(["main", "alternate"].map(profile => [profile,
    [...new Set(rows.filter(row => row.profile === profile).flatMap(row => row.cases.filter(item => item.status === "failed").map(item => item.id)))].sort()]));
  const review = manifest.goal_execution?.latest_strict_review;
  const reviewMatches = review?.source_fingerprint === manifest.source.fingerprint &&
    Object.values(failures).every(ids => ids.length === review.current_selected_unique_failures_each_profile);
  const batch = manifest.goal_execution?.latest_verification_batch;
  const batchMatches = (batch?.source_fingerprint || batch?.native_fingerprint) === manifest.source.fingerprint;
  return { rows, failures, review, reviewMatches, batch, batchMatches };
}
export function aggregate(rows) {
  const groups = new Map();
  for (const row of rows) {
    if (!groups.has(row.family)) groups.set(row.family, []);
    groups.get(row.family).push(row);
  }
  return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([name, items]) => ({ name, total: items.length, counts: countStatuses(items) }));
}
