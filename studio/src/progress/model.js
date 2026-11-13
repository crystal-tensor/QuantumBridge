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
export const deferredManifestFields = ["verification", "test_contexts", "runtime_census", "goal_execution", "strict_backlog", "diagnostic_observations", "tests"];
export function restoreManifest(bootstrap, payload) {
  const descriptor = bootstrap.deferred_evidence;
  const sameFields = fields => Array.isArray(fields) && fields.length === deferredManifestFields.length &&
    deferredManifestFields.every(name => fields.includes(name));
  if (!sameFields(descriptor?.fields) || payload?.schema !== 1 || payload.encoding !== "deferred-manifest-v1" ||
    typeof bootstrap.generated_at !== "string" || !/^[0-9a-f]{64}$/.test(bootstrap.source?.fingerprint || "") ||
    payload.generated_at !== bootstrap.generated_at || payload.source_fingerprint !== bootstrap.source.fingerprint ||
    !payload.fields || !sameFields(Object.keys(payload.fields)) || deferredManifestFields.some(name => Object.hasOwn(bootstrap, name)) ||
    !Array.isArray(payload.fields.strict_backlog) || payload.fields.strict_backlog.length !== bootstrap.strict_backlog_count) {
    throw new Error("Deferred evidence does not match the snapshot");
  }
  const result = { ...bootstrap, ...payload.fields };
  delete result.deferred_evidence;
  delete result.strict_backlog_count;
  return result;
}
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
  const latest = new Map();
  for (const row of rows) for (const item of row.cases) {
    const key = JSON.stringify([row.profile, item.id]);
    const prior = latest.get(key);
    if (!prior || Date.parse(row.recorded_at) >= Date.parse(prior.recorded_at)) {
      latest.set(key, { ...item, profile: row.profile, recorded_at: row.recorded_at });
    }
  }
  const failures = Object.fromEntries(["main", "alternate"].map(profile => [profile,
    [...latest.values()].filter(item => item.profile === profile && item.status === "failed").map(item => item.id).sort()]));
  const review = manifest.goal_execution?.latest_strict_review;
  const reviewBatch = Object.values(manifest.goal_execution || {}).find(value =>
    value?.checkpoint === review?.checkpoint && value?.source_fingerprint === manifest.source.fingerprint &&
    Array.isArray(value.profiles) && ["main", "alternate"].every(profile =>
      Array.isArray(value.profiles.find(row => row.profile === profile)?.current_selected_unique_failure_ids)));
  const reviewedFailures = Object.fromEntries(["main", "alternate"].map(profile => [profile,
    [...new Set(reviewBatch?.profiles.find(row => row.profile === profile)?.current_selected_unique_failure_ids || [])].sort()]));
  const reviewMatches = review?.source_fingerprint === manifest.source.fingerprint &&
    Object.entries(failures).every(([profile, ids]) => ids.length === review.current_selected_unique_failures_each_profile &&
      ids.length === reviewedFailures[profile].length && ids.every((id, index) => id === reviewedFailures[profile][index]));
  const coreKey = manifest.goal_execution?.latest_core_validation_key;
  const batch = coreKey ? manifest.goal_execution[coreKey] : manifest.goal_execution?.latest_verification_batch;
  const batchMatches = (batch?.source_fingerprint || batch?.native_fingerprint) === manifest.source.fingerprint;
  const batches = [batch, reviewBatch].filter((value, index, all) => value &&
    all.findIndex(other => other?.checkpoint === value.checkpoint) === index);
  let reports = batches.flatMap(value => [
    ...(value.profiles || []).flatMap(profile => Object.entries(profile.reports || {}).map(([scope, report]) =>
      ({profile:profile.profile,scope,report,checkpoint:value.checkpoint}))),
    ...(value.source_bound_regressions || []).map(report =>
      ({profile:report.profile,scope:report.stage,report,checkpoint:value.checkpoint})),
  ]).flatMap(item => {
    const proof = rows.find(row => row.profile === item.profile && row.evidence_hash === item.report.evidence_hash);
    return proof ? [{...item,recordedAt:proof.recorded_at}] : [];
  });
  if (batchMatches && coreKey && !reports.length && batch.source_manifest_sha256) {
    reports = rows.filter(row => row.source_manifest_sha256 === batch.source_manifest_sha256).map(row =>
      ({ profile: row.profile, scope: row.name, report: row, checkpoint: batch.checkpoint, recordedAt: row.recorded_at }));
  }
  return { rows, failures, review, reviewMatches, reviewedFailures, reviewBatch, reports, batch, batchMatches };
}
export function abnormalObservations(goal = {}) {
  const observations = new Map();
  for (const value of Object.values(goal)) for (const row of value?.abnormal_process_observations || []) {
    const key = row.crash_report_sha256 || JSON.stringify([row.profile, row.selection, row.recorded_at]);
    if (!observations.has(key)) observations.set(key, row);
  }
  return [...observations.values()];
}
export function aggregate(rows) {
  const groups = new Map();
  for (const row of rows) {
    if (!groups.has(row.family)) groups.set(row.family, []);
    groups.get(row.family).push(row);
  }
  return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([name, items]) => ({ name, total: items.length, counts: countStatuses(items) }));
}
