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
export function fullContractReview(row, fingerprint) {
  const review = row.review;
  return row.status === "implemented" && review?.status === "implemented" &&
    review.source_hash === row.source_hash && review.project_fingerprint === fingerprint &&
    ["contract_complete", "native_independent", "versions_verified", "strict_tests_pass"].every(key => review[key] === true) &&
    /^[0-9a-f]{64}$/.test(review.evidence_hash || "");
}
export function functionEvidenceFilename(review) {
  const fingerprint = review?.project_fingerprint;
  if (!/^[0-9a-f]{64}$/.test(fingerprint || "")) return null;
  const legacy = `function-contracts-${fingerprint}.json.gz`;
  if (review.evidence_bundle_file === undefined) return legacy;
  const file = review.evidence_bundle_file;
  const prefix = `function-contracts-${fingerprint}`;
  return typeof file === "string" && file.startsWith(prefix) &&
    /^function-contracts-[0-9a-f]{64}(?:-[a-z0-9]+)*\.json\.gz$/.test(file) ? file : null;
}
export const deferredManifestFields = ["verification", "test_contexts", "runtime_census", "goal_execution", "strict_backlog", "diagnostic_observations", "tests"];
export function validDeferredManifestFields(fields) {
  if (!Array.isArray(fields)) return false;
  const expected = fields.includes("verification_migration_pool") ?
    [...deferredManifestFields, "verification_migration_pool"] : deferredManifestFields;
  return fields.length === expected.length && expected.every((name, index) => fields[index] === name);
}
export function restoreManifest(bootstrap, payload) {
  const descriptor = bootstrap.deferred_evidence;
  const sameFields = fields => validDeferredManifestFields(fields) && validDeferredManifestFields(descriptor?.fields) &&
    fields.length === descriptor.fields.length && fields.every((name, index) => descriptor.fields[index] === name);
  if (!sameFields(descriptor?.fields) || payload?.schema !== 1 || payload.encoding !== "deferred-manifest-v1" ||
    typeof bootstrap.generated_at !== "string" || !/^[0-9a-f]{64}$/.test(bootstrap.source?.fingerprint || "") ||
    payload.generated_at !== bootstrap.generated_at || payload.source_fingerprint !== bootstrap.source.fingerprint ||
    !payload.fields || !sameFields(Object.keys(payload.fields)) || descriptor.fields.some(name => Object.hasOwn(bootstrap, name)) ||
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
export function pendingIntegration(manifest) {
  const key = manifest.goal_execution?.latest_pending_core_integration_key;
  const batch = key && manifest.goal_execution[key];
  const scopes = ["resource_scope", "new_runtime_scope", "lifecycle_scope", "default_original_scope",
    "explicit_opt_in_original_scope", "combined_new_scope", "related_graph_scope"];
  const countsValid = row => row && ["total", "passed", "failed", "skipped"].every(name =>
    Number.isSafeInteger(row[name]) && row[name] >= 0) && row.total === row.passed + row.failed + row.skipped &&
    row.terminal_exit === (row.failed ? 1 : 0);
  if (!batch || batch.contract_status !== "partial" || batch.explicit_public_runtime_tested !== true ||
      batch.independent_audit_exit !== 0 || !/^[0-9a-f]{64}$/.test(batch.independent_audit_report_sha256 || "") ||
      !/^[0-9a-f]{64}$/.test(batch.source_fingerprint || "") ||
      !/^[0-9a-f]{64}$/.test(batch.source_manifest_sha256 || "") ||
      batch.new_full_function_acceptances !== 0 || batch.full_strict_suite_accepted !== false ||
      batch.default_qnode_admission_changed !== false || !Array.isArray(batch.profiles) || batch.profiles.length !== 2 ||
      !["main", "alternate"].every(profile => batch.profiles.filter(row => row.profile === profile).length === 1) ||
      !batch.profiles.every(row => scopes.every(scope => countsValid(row[scope])))) return null;
  return { key, batch, scopes, sourceMatches: batch.source_fingerprint === manifest.source?.fingerprint };
}
export function approvedMigrations(manifest) {
  const all = (manifest.verification || []).filter(row => row.environment_validation?.verified && row.process_terminal_match);
  const current = all.filter(row => row.source_match);
  const key = manifest.goal_execution?.latest_core_validation_key;
  const source = key && manifest.goal_execution[key]?.source_fingerprint;
  const historical = all.filter(row => row.source_fingerprint === source).slice(-1);
  const records = current.length ? current : historical;
  const migrations = new Map();
  for (const row of records) for (const migration of row.approved_test_migrations || []) {
    migrations.set(migration.file + ":" + migration.after_sha256, migration);
  }
  return { rows: [...migrations.values()], historicalOnly: !current.length, sourceFingerprint: current.length ? manifest.source?.fingerprint : source };
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
  const coreKey = manifest.goal_execution?.latest_core_validation_key;
  const batch = coreKey ? manifest.goal_execution[coreKey] : manifest.goal_execution?.latest_verification_batch;
  const review = coreKey ? batch : manifest.goal_execution?.latest_strict_review;
  const reviewBatch = coreKey ? batch : Object.values(manifest.goal_execution || {}).find(value =>
    value?.checkpoint === review?.checkpoint && value?.source_fingerprint === manifest.source.fingerprint &&
    Array.isArray(value.profiles) && ["main", "alternate"].every(profile =>
      Array.isArray(value.profiles.find(row => row.profile === profile)?.current_selected_unique_failure_ids)));
  const failureIds = profile => Object.hasOwn(profile || {}, "current_selected_unique_failure_ids") ?
    profile.current_selected_unique_failure_ids : profile?.current_selected_unique_native_failure_ids;
  const reviewedFailures = Object.fromEntries(["main", "alternate"].map(profile => [profile,
    [...new Set(failureIds(reviewBatch?.profiles?.find(row => row.profile === profile)) || [])].sort()]));
  const reviewedProfiles = Object.fromEntries(["main", "alternate"].map(profile => [profile,
    (reviewBatch?.profiles || []).filter(row => row.profile === profile)]));
  const reviewShape = Object.values(reviewedProfiles).every(profiles => profiles.length === 1 &&
    Array.isArray(failureIds(profiles[0])));
  const nativeCounts = batch?.current_selected_unique_native_failures_each_profile;
  const declaredCounts = coreKey ? Object.fromEntries(Object.entries(reviewedProfiles).map(([profile, profiles]) =>
    [profile, profiles.length === 1 ? (Object.hasOwn(profiles[0], "native_strict_failures") ?
      profiles[0].native_strict_failures : Number.isSafeInteger(nativeCounts) ? nativeCounts : nativeCounts?.[profile]) : undefined])) :
    review?.current_selected_unique_failures_each_profile;
  const countMap = declaredCounts && typeof declaredCounts === "object" && !Array.isArray(declaredCounts) &&
    Object.keys(declaredCounts).length === 2 && ["main", "alternate"].every(profile => Object.hasOwn(declaredCounts, profile));
  const reviewCounts = Object.fromEntries(["main", "alternate"].map(profile => [profile,
    Number.isSafeInteger(declaredCounts) ? declaredCounts : countMap ? declaredCounts[profile] : undefined]));
  const reviewMatches = reviewShape && review?.source_fingerprint === manifest.source.fingerprint &&
    Object.entries(failures).every(([profile, ids]) => Number.isSafeInteger(reviewCounts[profile]) && reviewCounts[profile] >= 0 &&
      ids.length === reviewCounts[profile] &&
      ids.length === reviewedFailures[profile].length && ids.every((id, index) => id === reviewedFailures[profile][index]));
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
    return proof ? [{...item,report:proof,recordedAt:proof.recorded_at}] : [];
  });
  if (batchMatches && coreKey && !reports.length && batch.source_manifest_sha256) {
    reports = rows.filter(row => row.source_manifest_sha256 === batch.source_manifest_sha256).map(row =>
      ({ profile: row.profile, scope: row.name, report: row, checkpoint: batch.checkpoint, recordedAt: row.recorded_at }));
  }
  const references=(batch?.profiles || []).filter(profile=>profile.separate_reference_scope?.configuration_id ||
    (Array.isArray(profile.current_selected_unique_reference_failure_ids) &&
      Object.hasOwn(batch?.current_selected_unique_reference_failures_each_profile || {}, profile.profile))).map(profile=>{
    if (!profile.separate_reference_scope?.configuration_id) {
      const proofs = rows.filter(row => row.source_manifest_sha256 === batch.source_manifest_sha256 &&
        row.reference_execution_identity_validation?.verified === true &&
        row.reference_execution_identity_validation.configuration_id === row.profile &&
        row.profile.startsWith(profile.profile + "-") && row.profile !== profile.profile);
      const latestCases = new Map();
      for (const proof of proofs) for (const item of proof.cases) {
        const prior = latestCases.get(item.id);
        if (!prior || Date.parse(proof.recorded_at) >= Date.parse(prior.recorded_at))
          latestCases.set(item.id, { ...item, recorded_at: proof.recorded_at });
      }
      const cases = [...latestCases.values()];
      const counts = { total: cases.length, ...Object.fromEntries(["passed", "failed", "skipped"].map(status =>
        [status, cases.filter(item => item.status === status).length])) };
      const failureIds = cases.filter(item => item.status === "failed").map(item => item.id).sort();
      const expected = [...new Set(profile.current_selected_unique_reference_failure_ids)].sort();
      const declared = batch.current_selected_unique_reference_failures_each_profile[profile.profile];
      const identifiers = [...new Set(proofs.map(row => row.profile))];
      const matches = batchMatches && proofs.length > 0 && identifiers.length === 1 &&
        Number.isSafeInteger(declared) && declared >= 0 && counts.failed === declared &&
        failureIds.length === expected.length && failureIds.every((id, index) => id === expected[index]);
      return { profile: identifiers[0] || profile.profile, baseProfile: profile.profile,
        counts, failureIds, matches, proofCount: proofs.length, selectedCaseUnion: true };
    }
    const scope=profile.separate_reference_scope, identifier=scope.configuration_id;
    const selection=scope.execution_evidence;
    const batchCount=Object.hasOwn(scope,"execution_batch_count")?scope.execution_batch_count:scope.modules;
    const batchCountValid=Number.isSafeInteger(batchCount)&&batchCount>0;
    const selectionValid=batchCountValid&&(selection===undefined||(Array.isArray(selection)&&selection.length===batchCount&&
      selection.every(item=>typeof item.name==="string"&&item.profile===identifier&&/^[0-9a-f]{64}$/.test(item.evidence_hash))&&
      new Set(selection.map(item=>JSON.stringify([item.name,item.profile,item.evidence_hash]))).size===selection.length));
    const proofs=rows.filter(row=>row.profile===identifier&&row.source_manifest_sha256===batch.source_manifest_sha256&&
      row.reference_execution_identity_validation?.verified===true&&
      row.reference_execution_identity_validation.configuration_id===identifier&&selectionValid&&
      (selection===undefined||selection.some(item=>item.name===row.name&&item.profile===row.profile&&item.evidence_hash===row.evidence_hash)));
    const latestCases=new Map();
    for(const proof of proofs)for(const item of proof.cases){
      const previous=latestCases.get(item.id);
      if(!previous||Date.parse(proof.recorded_at)>=Date.parse(previous.recorded_at))
        latestCases.set(item.id,{...item,recorded_at:proof.recorded_at});
    }
    const cases=[...latestCases.values()];
    const counts={total:cases.length,...Object.fromEntries(["passed","failed","skipped"].map(status=>
      [status,cases.filter(item=>item.status===status).length]))};
    const failureIds=cases.filter(item=>item.status==="failed").map(item=>item.id).sort();
    const expected=[...new Set(profile.public_reference_failure_ids||[])].sort();
    const matches=batchMatches&&selectionValid&&proofs.length===batchCount&&
      Object.entries(counts).every(([key,value])=>Number.isSafeInteger(scope[key])&&value===scope[key])&&
      Array.isArray(profile.public_reference_failure_ids)&&failureIds.length===expected.length&&
      failureIds.every((id,index)=>id===expected[index]);
    return {profile:identifier,baseProfile:profile.profile,counts,failureIds,matches,proofCount:proofs.length};
  });
  return { rows, failures, review, reviewCounts, reviewMatches, reviewedFailures, reviewBatch, reports, batch, batchMatches, references };
}
export function abnormalObservations(goal = {}) {
  const observations = new Map();
  for (const value of Object.values(goal)) for (const row of Array.isArray(value?.abnormal_process_observations) ? value.abnormal_process_observations : []) {
    const key = row.crash_report_sha256 || JSON.stringify([row.profile, row.selection, row.recorded_at]);
    if (!observations.has(key)) observations.set(key, row);
  }
  return [...observations.values()];
}
export function originalChildFollowup(manifest) {
  const batch = manifest.goal_execution?.original_child_followup_validation;
  if (!batch || batch.source_fingerprint !== manifest.source?.fingerprint) return null;
  const configurations = new Set(["main", "alternate", "main-native-only-no-user-site", "alternate-native-only-no-user-site"]);
  const rows = (batch.results || []).map(item => {
    const proof = (manifest.verification || []).find(row => row.name === item.name && row.profile === item.profile &&
      row.evidence_hash === item.evidence_hash && row.source_manifest_sha256 === batch.source_manifest_sha256 &&
      row.source_match && row.environment_validation?.verified && row.process_terminal_validation?.exit === 0 &&
      row.child_execution_validation?.verified && row.child_execution_validation.children?.length === 1 &&
      row.child_execution_validation.children.every(child => child.process_exit === 0 && child.original_probe_executed === true));
    return proof && configurations.has(item.profile) && proof.failed === 0 && proof.skipped === 0 ? proof : null;
  });
  if (rows.length !== 4 || rows.some(row => !row) || new Set(rows.map(row => row.profile)).size !== 4) return null;
  if (rows.some(row => {
    const supplemental = row.profile.endsWith("-no-user-site");
    const count = supplemental ? 5 : 20;
    const prefix = supplemental ? "tests.primitives.test_public_primitive_reentry::" : "tests.derivative_execution.test_memory_ticket_handoff::";
    const child = row.child_execution_validation.children[0];
    return row.environment.numpy !== (supplemental ? "1.26.4" : "2.4.6") || row.total !== count || row.passed !== count ||
      row.cases?.length !== count || row.cases.some(item => !item.id.startsWith(prefix) || item.status !== "passed") ||
      child.loaded_dependencies?.numpy?.reported_version !== row.environment.numpy;
  })) return null;
  const unadmitted = batch.unadmitted_executions || [];
  if (unadmitted.length !== 2 || new Set(unadmitted.map(row => row.profile)).size !== 2 ||
    unadmitted.some(row => !["main", "alternate"].includes(row.profile) || row.execution_admitted !== false ||
      row.terminal_exit !== 0 || row.timed_out !== false)) return null;
  return {batch, rows, unadmitted};
}
export function aggregate(rows) {
  const groups = new Map();
  for (const row of rows) {
    if (!groups.has(row.family)) groups.set(row.family, []);
    groups.get(row.family).push(row);
  }
  return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([name, items]) => ({ name, total: items.length, counts: countStatuses(items) }));
}
