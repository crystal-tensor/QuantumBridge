import assert from "node:assert/strict";
import test from "node:test";
import { readFile, mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { gunzipSync } from "node:zlib";
import { createHash } from "node:crypto";
import { isDeepStrictEqual } from "node:util";
import { countStatuses, filterRows, aggregate, isStale, statuses, decodeDataset, verificationWindow, currentVerification, abnormalObservations, restoreManifest, deferredManifestFields, validDeferredManifestFields } from "../src/progress/model.js";
import { readManifestEvidence } from "./read-manifest-evidence.mjs";
import { engineeringResources, engineeringReviewDownload, domainResources } from "../src/framework/resources.js";
import { buildPublic } from "./build-public.mjs";
import { readProgressSnapshot, readProgressSnapshotBytes } from "./read-progress-snapshot.mjs";
import { restoreMigrationPool } from "../src/progress/migration-pool.js";

const manifest = await readProgressSnapshot(new URL("../src/progress/data/manifest.json", import.meta.url));
// These report sections deliberately retain their original frozen validation.
const historicalReportSource = "20f14692052afb89a2f84b45486e9ad6f9ba22756bf837a492e5eaf5d0e2cba7";
const supplementConfigBytes = await readFile(new URL("../../docs/engineering/native_supplement_configurations.json", import.meta.url));
const supplementConfigurations = JSON.parse(supplementConfigBytes);
const supplementConfigHash = createHash("sha256").update(supplementConfigBytes).digest("hex");
function historicalRegistry(report, key) {
  const artifact=report.historical_migration_registries[key];
  assert.equal(Buffer.byteLength(artifact.json),artifact.bytes);
  assert.equal(createHash("sha256").update(artifact.json).digest("hex"),artifact.sha256);
  const registry=JSON.parse(artifact.json);
  for(const row of registry.migrations)assert.equal(artifact.test_hashes[row.file],row.after_sha256);
  return {artifact,registry};
}
function assertVerificationScope(run) {
  const standardScope = "selected_strict_batch_not_full_contract_or_full_suite";
  if (run.scope === standardScope) {
    assert.equal(run.supplemental_configuration, undefined);
    return;
  }
  assert.equal(run.scope, "owner_approved_native_only_supplement_not_sdk_reference_or_numpy246_baseline");
  assert.equal(supplementConfigurations.canonical_dependency_profiles_unchanged, true);
  assert.equal(supplementConfigurations.new_sdk_reference_configuration, false);
  const supplement = run.supplemental_configuration;
  const configuration = supplementConfigurations.configurations.find(row => row.id === supplement?.id);
  assert.ok(configuration?.owner_approved);
  assert.equal(supplement.owner_approved, true);
  assert.equal(supplement.configuration_sha256, supplementConfigHash);
  assert.equal(supplement.sdk_reference, false);
  assert.equal(supplement.canonical_dependency_profiles_changed, false);
  assert.equal(supplement.parent_no_user_site, true);
  assert.equal(configuration.original_numpy_246_acceptance_replaced, false);
  assert.ok(configuration.profiles.includes(run.profile));
  assert.equal(run.original_record_scope, standardScope);
  assert.equal(run.environment.numpy, configuration.numpy_version);
  assert.equal(run.environment_validation.interpreter_flags.no_user_site, true);
  assert.equal(run.process_terminal_validation.exit, 0);
  assert.equal(run.child_execution_validation.verified, true);
  assert.equal(run.child_execution_validation.children.length, 1);
  for (const child of run.child_execution_validation.children) {
    assert.equal(child.process_exit, 0);
    assert.deepEqual(child.sdk_modules_loaded, configuration.required_sdk_modules_loaded);
    assert.equal(child.loaded_dependencies.numpy.reported_version, configuration.numpy_version);
    assert.equal(child.loaded_dependencies.numpy.entry_sha256, configuration.numpy_entry_sha256);
    assert.equal(child.loaded_dependencies.numpy.entry_verified_in_distribution, true);
  }
}
function assertCallBoundaryDiagnostic(row) {
  const report = row.report;
  assert.equal(row.kind,"tf_call_boundary_control");
  assert.equal(report.classification,"REJECTED_CALL_BOUNDARY_AND_MULTILINEAR_CANDIDATES");
  assert.equal(report.controls.length,22);
  assert.equal(report.controls.filter(value=>value.passed).length,1);
  assert.ok(report.controls.every(value=>value.terminal_exit===(value.passed?0:1)&&
    /^[0-9a-f]{64}$/.test(value.terminal_sha256)&&/^[0-9a-f]{64}$/.test(value.result_sha256)&&
    value.results.length===3));
  assert.equal(report.actual_native_quantum_kernel_executed_by_controls,false);
  assert.equal(report.candidate.private_binding_replaced,true);
  assert.equal(report.candidate.native_accepted,false);
  assert.equal(report.candidate.canonical_verification,false);
  assert.deepEqual(report.candidate.counts,{total:45,passed:29,failed:16,skipped:0});
  assert.deepEqual(report.unchanged_baseline.counts,{total:45,passed:41,failed:4,skipped:0});
  assert.equal(report.candidate.added_failure_ids.length,12);
  assert.ok(report.candidate.added_failure_ids.every(id=>report.candidate.failed_ids.includes(id)));
  for(const key of ["source_patch_promoted","original_tests_or_tolerances_changed",
    "installed_framework_source_or_global_config_changed","native_accepted","full_function_accepted"]){
    assert.equal(report[key],false);
  }
  assert.equal(report.current_selected_strict_failures,5);
}
test("the small initial manifest losslessly restores every evidence field without refreshing dates", async () => {
  const base = new URL("../src/progress/data/", import.meta.url);
  const bytes = await readFile(new URL("manifest-browser.json.gz", base));
  assert.ok(bytes.length < 100 * 1024);
  const bootstrap = JSON.parse(gunzipSync(bytes));
  assert.ok(deferredManifestFields.every(name => !Object.hasOwn(bootstrap, name)));
  assert.equal(bootstrap.strict_backlog_count, manifest.strict_backlog.length);
  const descriptor = bootstrap.deferred_evidence;
  const raw = await readFile(new URL(descriptor.file, base));
  assert.equal(raw.length, descriptor.bytes);
  assert.equal(createHash("sha256").update(raw).digest("hex"), descriptor.sha256);
  const payload = await readManifestEvidence(base, descriptor);
  assert.deepEqual(await restoreMigrationPool(restoreManifest(bootstrap, payload)), manifest);
  assert.equal(bootstrap.generated_at, manifest.generated_at);
  assert.ok(validDeferredManifestFields(descriptor.fields));
  assert.ok(descriptor.fields.every(name=>!Object.hasOwn(bootstrap,name)));
  const before = JSON.stringify(bootstrap);
  const mutate = change => { const value = structuredClone(payload); change(value); return value; };
  for (const changed of [mutate(value => { value.generated_at = "new time"; }),
    mutate(value => { value.source_fingerprint = "0".repeat(64); }),
    mutate(value => { delete value.fields.verification; }),
    mutate(value => { value.fields.source = {}; }),
    mutate(value => { value.fields.strict_backlog = []; }),
    mutate(value => { value.schema = 2; })]) {
    assert.throws(() => restoreManifest(bootstrap, changed), /does not match/);
  }
  assert.throws(() => restoreManifest({ ...bootstrap, verification: [] }, payload), /does not match/);
  assert.equal(JSON.stringify(bootstrap), before);
});
test("compressed manifest and lazy runtime details preserve the complete snapshot", async () => {
  const base=new URL("../src/progress/data/",import.meta.url);
  const raw=await readProgressSnapshotBytes(new URL("manifest.json",base));
  const compressed=await readFile(new URL("manifest.json.gz",base));
  assert.deepEqual(gunzipSync(compressed),raw);
  assert.ok(compressed.length<raw.length/3);
  const descriptor=manifest.datasets.find(row=>row.id==="runtime");
  async function load(item){
    const bytes=await readFile(new URL(item.file,base));
    assert.equal(createHash("sha256").update(bytes).digest("hex"),item.sha256);
    return decodeDataset(JSON.parse(gunzipSync(bytes)));
  }
  const full=await load(descriptor),index=await load(descriptor.browser);
  assert.equal(index.length,full.length);
  const buckets=new Map();
  for(const [key,item] of Object.entries(descriptor.browser.details)){
    const rows=await load(item);
    assert.equal(rows.length,item.count);
    buckets.set(key,new Map(rows.map(row=>[row.id,row.runtime_observations])));
  }
  for(let i=0;i<full.length;i++){
    const {runtime_observations,...searchable}=full[i];
    const {detail_bucket,...projected}=index[i];
    assert.deepEqual(projected,searchable);
    assert.deepEqual(buckets.get(detail_bucket).get(projected.id),runtime_observations);
  }
  assert.equal([...buckets.values()].reduce((sum,rows)=>sum+rows.size,0),full.length);
});
test("inventory integrity, conservative states, unique IDs, no local paths or credentials", async () => {
  for (const descriptor of manifest.datasets) {
    const bytes = await readFile(new URL(`../src/progress/data/${descriptor.file}`, import.meta.url));
    assert.equal(createHash("sha256").update(bytes).digest("hex"), descriptor.sha256);
    const text = gunzipSync(bytes).toString();
    const rows = decodeDataset(JSON.parse(text));
    assert.equal(rows.length, descriptor.count);
    assert.equal(new Set(rows.map(r => r.id)).size, rows.length);
    assert.ok(rows.every(r => statuses.includes(r.status)));
    assert.ok(rows.filter(r => r.status === "implemented").every(r => r.review?.source_hash === r.source_hash && r.review?.strict_tests_pass && r.review?.native_independent && r.review?.contract_complete && r.review?.versions_verified && r.review?.evidence_hash));
    assert.ok(!text.includes("/Users/") && !text.includes("QUAFU_TOKEN") && !text.includes("site-packages/"));
    assert.equal(Object.values(countStatuses(rows)).reduce((a,b)=>a+b,0), rows.length);
    assert.equal(aggregate(rows).reduce((a,b)=>a+b.total,0), rows.length);
  }
  assert.equal(manifest.census_complete, false);
  assert.ok(manifest.tests.some(x => x.failed > 0));
  assert.ok(manifest.tests.every(x => x.source_match === false));
});
test("filters and snapshot age are explicit, not fabricated completion percentages", () => {
  const rows = [{name:"qiskit.C.f",family:"qiskit",module:"qiskit.C",kind:"method",status:"partial",hardware:"unverified"}];
  assert.equal(filterRows(rows,{query:"c.f",family:"qiskit",module:"qiskit.C",status:"partial",kind:"method",hardware:"unverified"}).length,1);
  for (const filters of [{query:"absent"},{family:"pennylane"},{status:"implemented"},{module:"other"},{kind:"class"},{hardware:"passed"}]) assert.equal(filterRows(rows,filters).length,0);
  assert.equal(isStale("2026-11-11T00:00:00Z",Date.parse("2026-11-11T12:00:01Z")),true);
  assert.equal(isStale("2026-11-11T00:00:00Z",Date.parse("2026-11-11T11:59:59Z")),false);
  assert.equal(filterRows([{name:"canonical",exposures:["public.alias"]}],{query:"public.alias"}).length,1);
});
test("repository collection stays separate from executed tests and the public API denominator", async () => {
  const census = manifest.goal_execution.test_execution_census;
  assert.equal(census.public_api_denominator_closed, false);
  assert.equal(census.execution_complete, false);
  assert.equal(census.complete_function_acceptances, 0);
  assert.equal(census.profiles.length, 2);
  for (const row of census.profiles) {
    assert.equal(row.module_count, 1307);
    assert.equal(row.collected_modules, row.module_count);
    assert.ok(row.item_count > 35000);
  }
  const runs = manifest.verification.filter(row => row.name.startsWith("test-census-"));
  assert.equal(runs.length, 14);
  assert.equal(runs.filter(row => row.source_match).length, 0);
  for (const profile of ["main", "alternate"]) {
    const frozen = runs.filter(row => row.profile === profile && row.name.includes("execute-v3-"));
    assert.equal(frozen.reduce((sum, row) => sum + row.passed, 0), 756);
    assert.equal(frozen.reduce((sum, row) => sum + row.failed, 0), 1);
    assert.equal(frozen.find(row => row.name.includes("approved-mps-memory")).passed, 13);
    assert.ok(frozen.every(row => row.source_fingerprint !== manifest.source.fingerprint && !row.source_match && !row.test_context_match && row.process_terminal_match));
  }
  const script = await readFile(new URL("../src/progress/main.js", import.meta.url), "utf8");
  assert.ok(script.includes("Test collection is not a passing test run"));
  assert.ok(script.includes("Full execution remains incomplete"));
});
test("compiler execution reconciles exact cases while preserving timeouts and strict failures", () => {
  const compiler = manifest.goal_execution.compiler_execution;
  assert.equal(compiler.full_compiler_accepted, false);
  assert.equal(compiler.full_suite_accepted, false);
  assert.equal(compiler.strict_selected_failure_count_still, 23);
  assert.equal(compiler.normal_recorded_workers, 152);
  assert.equal(compiler.incomplete_module_attempts.length, 2);
  assert.ok(compiler.incomplete_module_attempts.every(row => row.timed_out && row.exit === -9 && row.tests === 0 && !row.junit_sha256));
  assert.equal(compiler.outstanding_cases.length, 1);
  assert.ok(compiler.outstanding_cases[0].endsWith("[quantumbridge.mps-2-best]"));
  const runs = manifest.verification.filter(row => row.name.startsWith("compiler-matrix-"));
  assert.equal(runs.length, 152);
  assert.ok(runs.every(row => row.source_fingerprint !== manifest.source.fingerprint && !row.source_match && row.process_terminal_match && !row.test_context_match));
  for (const profile of ["main", "alternate"]) {
    const summary = compiler.profiles.find(row => row.profile === profile);
    assert.equal(summary.expected_compiler_cases, 1301);
    assert.equal(summary.passed_compiler_cases, 1300);
    assert.equal(summary.passed_reference_cases, 140);
    const current = runs.filter(row => row.profile === profile);
    assert.equal(current.reduce((sum, row) => sum + row.passed, 0), 1440);
    assert.ok(current.every(row => !row.failed && !row.skipped));
    const cases = current.flatMap(row => row.cases.map(item => item.id));
    assert.equal(new Set(cases).size, 1440);
    assert.ok(!cases.includes(compiler.outstanding_cases[0].replace(/\.py::/, "::").replaceAll("/", ".")));
  }
  const investigation = manifest.goal_execution.latest_rejected_prototype;
  assert.equal(investigation.accepted, false);
  assert.equal(investigation.native_source_framework_or_installed_dependencies_changed, false);
  assert.equal(investigation.cached_tf_failures_remain, 4);
});
test("CI census repair retains real child results, original bodies and frozen-context boundaries", () => {
  const repair=manifest.goal_execution.ci_workflow_repair;
  assert.equal(repair.published_fix_commit,"b8abde9a0059cf808321744ed371c4d61f664147");
  assert.equal(repair.native_changed,false);
  assert.equal(repair.production_isolation_changed,false);
  assert.equal(repair.additional_contract_migrations,0);
  assert.equal(repair.original_function_bodies_preserved.length,11);
  assert.equal(repair.final_context_normal_workers,44);
  assert.equal(repair.real_clean_children,24);
  assert.equal(repair.core_function_acceptances,0);
  assert.equal(repair.full_suite_accepted,false);
  const runs=manifest.verification.filter(row=>row.name.startsWith("ci-reference-unit-"));
  assert.equal(runs.length,44);
  assert.ok(runs.every(row=>!row.source_match&&row.source_fingerprint!==manifest.source.fingerprint&&!row.test_context_match&&row.process_terminal_match));
  for(const profile of ["main","alternate"]){
    const current=runs.filter(row=>row.profile===profile);
    assert.equal(current.reduce((sum,row)=>sum+row.passed,0),87);
    assert.equal(current.reduce((sum,row)=>sum+row.failed,0),24);
    assert.ok(current.every(row=>row.skipped===0));
  }
  assert.equal(repair.remote_snapshot_selection.main.passed,115);
  assert.equal(repair.remote_snapshot_selection.alternate.exit,-11);
  assert.equal(repair.remote_snapshot_selection.alternate.accepted,false);
});
test("resource verification retains all failures and separates published-main repair", () => {
  const batch=manifest.goal_execution.resource_validation;
  assert.notEqual(batch.source_fingerprint,manifest.source.fingerprint);
  assert.equal(batch.normal_final_source_workers,132);
  assert.equal(batch.additional_migrations,0);
  assert.equal(batch.resource_caps_changed,false);
  assert.equal(batch.algorithm_selection_changed,false);
  assert.equal(batch.full_suite_accepted,false);
  const runs=manifest.verification.filter(row=>row.name.startsWith("resource-validation-"));
  assert.equal(runs.length,134);
  for(const profile of ["main","alternate"]){
    const current=runs.filter(row=>row.profile===profile&&row.source_fingerprint===batch.source_fingerprint);
    assert.equal(current.length,66);
    assert.equal(current.reduce((sum,row)=>sum+row.passed,0),966);
    assert.equal(current.reduce((sum,row)=>sum+row.failed,0),27);
    assert.ok(current.every(row=>!row.skipped&&!row.source_match&&row.process_terminal_match));
    const earlier=runs.find(row=>row.profile===profile&&row.name.includes("fastpath-control-"));
    assert.equal(earlier.failed,3);
    assert.equal(earlier.source_match,false);
    const failureIds=new Set(current.flatMap(row=>row.cases.filter(c=>c.status==="failed").map(c=>c.id)));
    assert.equal(failureIds.size,27);
    assert.ok(earlier.cases.every(c=>failureIds.has(c.id)));
  }
  const repair=manifest.goal_execution.ci_primitive_repair;
  assert.equal(repair.published_fix_commit,"12b8781bccc7db622d7a54952b1d8c5f57188c97");
  assert.equal(repair.published_files.length,5);
  assert.equal(repair.inherited_published_test_files_unchanged,716);
  assert.equal(repair.original_assertions_changed,false);
  assert.equal(repair.full_local_fusion_accepted,false);
  assert.equal(repair.full_goal_accepted,false);
  assert.equal(repair.remote_ci.core_only_result.passed,8276);
  assert.equal(repair.remote_ci.core_only_result.skipped,2550);
  assert.equal(repair.remote_ci.jobs.find(row=>row.name==="core-only").conclusion,"success");
  assert.equal(batch.approved_memory_recheck.length,2);
  assert.ok(batch.approved_memory_recheck.every(row=>row.terminal&&row.exit===0&&row.tests===13&&!row.failures&&!row.errors&&!row.skipped));
  const approved=manifest.verification.filter(row=>row.name.startsWith("approved-memory-current-"));
  assert.equal(approved.length,2);
  assert.ok(approved.every(row=>!row.source_match&&row.passed===13&&!row.failed&&!row.skipped));
});
test("runtime census is not combined with the target denominator or implementation acceptance", async () => {
  const descriptor=manifest.datasets.find(x=>x.id==="runtime");
  assert.ok(descriptor.count>0);
  const rows=decodeDataset(JSON.parse(gunzipSync(await readFile(new URL(`../src/progress/data/${descriptor.file}`,import.meta.url)))));
  assert.ok(rows.every(r=>r.status==="unverified"&&r.native_mapping===null));
  assert.ok(rows.some(r=>r.runtime_observations.some(o=>o.inherited)));
  assert.ok(rows.some(r=>r.exposures.includes("pennylane.transforms.expand_multipar")));
  assert.equal(manifest.runtime_census.length,2);
  assert.ok(manifest.runtime_census.every(a=>a.census_complete===false&&a.modules.some(m=>m.name==="qiskit_finance"&&!m.available)));
});
test("recursive census retains traversal gaps, loaded identities and accessor provenance", async () => {
  const descriptor=manifest.datasets.find(x=>x.id==="runtime");
  const rows=decodeDataset(JSON.parse(gunzipSync(await readFile(new URL(`../src/progress/data/${descriptor.file}`,import.meta.url)))));
  assert.ok(rows.some(r=>r.runtime_observations.some(o=>o.accessor==="set")));
  assert.ok(rows.some(r=>r.runtime_observations.some(o=>o.source_hash_scope==="ancestor_module_file")));
  assert.ok(rows.some(r=>r.runtime_observations.some(o=>o.declared_in_reference_namespace===false)));
  for(const audit of manifest.runtime_census){
    assert.equal(audit.traversal_audits.length,2);
    assert.ok(audit.environment.distribution_versions.tensorflow);
    assert.ok(audit.environment.distribution_versions.pyarrow);
    for(const traversal of audit.traversal_audits){
      assert.equal(traversal.public_function_denominator_closed,false);
      assert.equal(traversal.loaded_sdk_identity.import_identity_verified,true);
      assert.equal(traversal.loaded_sdk_identity.version,audit.environment.distribution_versions[traversal.family]);
      assert.ok(traversal.namespace_mutation_history.length>0);
      assert.ok(traversal.deferred_modules.length>0);
      assert.equal(traversal.coexistence_verified,false);
    }
    assert.ok(audit.modules.some(m=>m.available===false&&m.missing_module));
  }
});
test("hardware receipts keep domain acceptance separate and redact sensitive payloads", () => {
  assert.ok(manifest.hardware.length >= 5);
  const legacy=manifest.hardware.filter(row=>!row.job_id),current=manifest.hardware.filter(row=>row.job_id);
  assert.ok(legacy.length>=5);
  assert.ok(legacy.every(row=>row.acceptance==="INCONCLUSIVE"&&row.domain==="finance"));
  assert.equal(current.length,19);
  assert.ok(current.every(row=>row.acceptance==="NOT_ACCEPTED_NO_PREREGISTERED_HARDWARE_THRESHOLD"&&row.backend==="Baihua"));
  for(const r of manifest.hardware){
    assert.ok(r.task_id&&r.artifact_hash);assert.equal(r.shots,r.count_sum);
    assert.ok(!("openqasm" in r));
    assert.ok(["science","finance","industry","security"].includes(r.domain));
  }
});
test("namespace files remain unreviewed metadata, with exact artifacts and no local paths", async () => {
  assert.equal(manifest.namespace_census.length,2);
  for(const audit of manifest.namespace_census){
    const bytes=await readFile(new URL(`../src/progress/data/${audit.file}`,import.meta.url));
    assert.equal(createHash("sha256").update(bytes).digest("hex"),audit.artifact_hash);
    const text=gunzipSync(bytes).toString();
    const value=JSON.parse(text);
    assert.equal(value.sdk_modules_imported,false);
    assert.equal(audit.census_complete,false);
    assert.equal(audit.candidate_modules,value.modules.length);
    assert.ok(audit.public_path_candidates>audit.public_path_runtime_inspected);
    assert.ok(value.modules.every(m=>m.contract_reviewed===false));
    assert.ok(audit.packages.some(p=>p.name==="qiskit_finance"&&!p.available&&p.still_in_scope));
    assert.ok(!text.includes("/Users/")&&!text.includes("site-packages/")&&!text.includes("QUAFU_TOKEN"));
  }
});
test("framework and lifetime diagnostics are not Native acceptance or test passes",async()=>{
  const declared=JSON.parse(await readFile(new URL("../../docs/engineering/diagnostic_observations.json",import.meta.url),"utf8"));
  const identity=row=>JSON.stringify([row.id,row.recorded_at,row.evidence_hash,row.source_fingerprint]);
  const retained=new Set([...declared.observations,...(declared.historical_observations||[])].map(identity));
  const published=new Set(manifest.diagnostic_observations.map(identity));
  for(const row of manifest.diagnostic_observations)assert.ok(retained.has(identity(row)),"Published diagnostic lost its original identity");
  for(const row of declared.observations){
    if(Date.parse(row.recorded_at)<=Date.parse(manifest.generated_at))assert.ok(published.has(identity(row)),"Snapshot omitted a diagnostic already recorded before generation");
  }
  const script=await readFile(new URL("../downloads/tensorflow_cached_cos_probe.py",import.meta.url));
  for(const row of manifest.diagnostic_observations){
    assert.equal(row.report.native_accepted,false);
    assert.equal(row.scope,"diagnostic_observation_not_function_or_test_acceptance");
    if(row.kind==="tf_cached_cos"){
      assert.equal(row.report.quantumbridge_or_sdks_imported,false);
      assert.equal(row.report.source_sha256,createHash("sha256").update(script).digest("hex"));
      assert.ok(row.report.rows.some(r=>r.results.some(x=>!x.matches_formula)));
    }else if(row.kind==="mps_binding_retention"){
      assert.equal(row.report.original_constructor_assertion_changed,false);
      assert.equal(row.report.constructor_after_disposal,0);
      assert.equal(row.report.constructor_before,row.report.fixed_numeric_bytes+row.report.retained_binding_allowances.reduce((sum,x)=>sum+x.bytes,0));
    }else if(row.kind==="tensor_edge_curvature_decomposition"){
      assert.equal(row.report.production_changed,false);
      assert.equal(row.report.prototype_promoted,false);
      assert.equal(row.report.cached_mixed_failures_remaining,4);
    }else if(row.kind==="native_hellinger_counts"){
      assert.equal(row.report.native_accepted,false);
      assert.ok(row.report.rows.length>0);
      if(row.report.resolved_scope){
        assert.equal(row.report.production_changed,true);
        assert.ok(row.report.actual_current_reference_cases>0&&row.report.new_independent_native_cases>0);
      }else{
        assert.equal(row.report.old_assertions_or_tolerances_changed,false);
        assert.ok(row.report.observed_cases_with_mismatch>0);
      }
    }else if(row.kind==="matrix_power_reference_roundoff"){
      assert.equal(row.report.threshold_changed,false);
      assert.equal(row.report.threshold,2e-14);
      assert.equal(row.report.observations.native.strict_2e14_pass,true);
      assert.equal(row.report.observations.actual_qiskit.strict_2e14_pass,false);
      assert.ok(row.report.observations.actual_qiskit.absolute_error>row.report.threshold);
    }else if(row.kind==="arrow_coexistence_review"){
      const code=await readFile(new URL("../downloads/arrow_qiskit_import_probe.py",import.meta.url));
      assert.equal(row.report.source_sha256,createHash("sha256").update(code).digest("hex"));
      assert.equal(row.report.review_state,"EXPERIMENTALLY_VERIFIED_NOT_PROMOTED_TO_REFERENCE_BASELINE");
      assert.equal(row.report.baseline_environments_modified,false);
      assert.equal(row.report.sdk_target_versions_changed,false);
      assert.equal(row.report.baseline_imports.length,12);
      assert.equal(row.report.candidate_imports.length,12);
      assert.equal(row.report.baseline_imports.filter(r=>r.process_exit===-11).length,4);
      assert.ok(row.report.candidate_imports.every(r=>r.process_exit===0&&r.native_accepted===false));
      assert.ok([...row.report.baseline_imports,...row.report.candidate_imports].every(r=>r.observations.quantumbridge_imported===false));
      assert.equal(row.report.candidate_public.length,2);
      assert.ok(row.report.candidate_public.every(r=>r.process_exit===1&&r.total===512&&r.passed===493&&r.failed===19&&r.skipped===0&&r.original_case_population_and_failure_ids_unchanged&&r.native_accepted===false));
    }else if(row.kind==="tf_symbolic_jvp_causal_diagnostic"){
      assert.equal(row.report.classification,"REJECTED_INCOMPLETE_CAUSAL_DIAGNOSTIC_NOT_NATIVE_ACCEPTANCE");
      assert.equal(row.report.invalid_initial_harness.mathematical_or_framework_conclusion,false);
      assert.equal(row.report.corrected_candidate.timed_out,true);
      assert.equal(row.report.corrected_candidate.complete_report,false);
      assert.equal(row.report.corrected_candidate.mathematical_or_framework_conclusion,false);
      assert.equal(row.report.production_patch_promoted,false);
      assert.equal(row.report.installed_framework_bytes_unchanged,true);
      assert.equal(row.report.old_tests_changed,false);
      assert.equal(row.report.full_function_accepted,false);
    }else if(row.kind==="tf_tangent_recording_control"){
      const code=await readFile(new URL("../../"+row.source_file,import.meta.url));
      assert.equal(row.report.source_sha256,createHash("sha256").update(code).digest("hex"));
      assert.equal(row.report.classification,"NEGATIVE_TANGENT_RECORDING_CONTROL_NOT_A_REPAIR");
      assert.equal(row.report.controls.length,16);
      assert.equal(row.report.controls.filter(control=>control.passed).length,3);
      assert.equal(row.report.controls.filter(control=>!control.passed).length,13);
      assert.ok(row.report.controls.every(control=>control.terminal_exit===(control.passed?0:1)&&
        /^[0-9a-f]{64}$/.test(control.terminal_sha256)&&/^[0-9a-f]{64}$/.test(control.result_sha256)));
      assert.equal(row.report.actual_native_quantum_kernel_executed,false);
      assert.equal(row.report.public_qiskit_or_pennylane_reference_executed,false);
      assert.equal(row.report.original_tests_or_tolerances_changed,false);
      assert.equal(row.report.installed_framework_source_or_global_config_changed,false);
      assert.equal(row.report.source_patch_promoted,false);
      assert.equal(row.report.full_function_accepted,false);
    }else if(row.kind==="tf_call_boundary_control"){
      assertCallBoundaryDiagnostic(row);
    }else if(row.kind==="tf_atomic_account_candidate_review"){
      assert.equal(row.report.classification,"REJECTED_ATOMIC_ACCOUNT_CANDIDATE_NOT_A_REPAIR");
      assert.equal(row.report.source_patch_promoted,false);
      assert.equal(row.report.original_tests_or_tolerances_changed,false);
      assert.equal(row.report.installed_framework_source_or_global_config_changed,false);
      assert.equal(row.report.canonical_verification_ledger_unchanged,true);
      assert.equal(row.report.full_function_accepted,false);
      assert.equal(row.report.public_qiskit_or_pennylane_reference_executed,false);
      assert.equal(row.report.invalid_initial_harness.mathematical_conclusion,false);
      assert.deepEqual(row.report.latest_candidate_each_profile,{total:44,passed:39,failed:5,skipped:0});
      assert.deepEqual(row.report.experiments.map(trial=>trial.trial),["v2","v3","v4"]);
      for(const trial of row.report.experiments){
        assert.match(trial.candidate_sha256,/^[0-9a-f]{64}$/);
        assert.equal(trial.workers.length,2);
        assert.equal(trial.workers.reduce((sum,worker)=>sum+worker.total,0),trial.actual_cases_each_profile);
        for(const worker of trial.workers){
          assert.equal(worker.profile,row.profile);
          assert.equal(worker.total,worker.passed+worker.failed+worker.skipped);
          assert.equal(worker.failed,worker.failed_ids.length);
          assert.equal(worker.terminal_exit,worker.failed?1:0);
          assert.equal(worker.native_accepted,false);
          assert.equal(worker.runtime_binding_replaced,true);
          assert.equal(worker.runtime_interop_threads,worker.group==="concurrency"?2:1);
          for(const key of ["junit_sha256","terminal_receipt_sha256","environment_sha256","origin_sha256","guard_sha256","experiment_sha256"]){
            assert.match(worker[key],/^[0-9a-f]{64}$/);
          }
        }
      }
      assert.equal(row.report.experiments[1].declared_count_is_stale,true);
      assert.equal(row.report.experiments[1].declared_cases_each_profile,43);
      assert.equal(row.report.experiments[1].actual_cases_each_profile,44);
      assert.ok(row.report.experiments.at(-1).workers.some(worker=>worker.failed_ids.some(id=>id.endsWith("is_a_real_refusal[2]"))));
    }else if(row.kind==="tf_registered_jet_boundary_probe"){
      const report=row.report;
      assert.equal(report.classification,"REJECTED_CLASSICAL_JET_CALLBACK_BOUNDARY_CANDIDATES");
      assert.equal(report.profile,row.profile);
      assert.equal(report.source_fingerprint,row.source_fingerprint);
      for(const key of ["actual_native_quantum_kernel_executed","public_qiskit_or_pennylane_reference_executed",
        "source_patch_promoted","original_tests_or_tolerances_changed_by_probes",
        "installed_framework_source_or_global_config_changed","full_function_accepted"]){
        assert.equal(report[key],false);
      }
      assert.equal(report.experiments.length,2);
      for(const [index,trial] of report.experiments.entries()){
        assert.equal(trial.label,(index?"taylor-":"registered-")+row.profile+"-attested");
        assert.equal(trial.tensorflow,"2.21.0");
        assert.equal(trial.total,index?20:16);
        assert.equal(trial.passed,index?16:12);
        assert.equal(trial.failed,4);
        assert.equal(trial.physical_exit,1);
        assert.deepEqual(trial.sdk_modules_loaded,[]);
        for(const key of ["terminal_sha256","result_sha256","source_script_sha256","import_receipt_sha256"]){
          assert.match(trial[key],/^[0-9a-f]{64}$/);
        }
        for(const dependency of Object.values(trial.loaded_dependencies)){
          assert.equal(dependency.loaded,true);
          assert.match(dependency.entry_sha256,/^[0-9a-f]{64}$/);
        }
        assert.equal(trial.loaded_dependencies.tensorflow.reported_version,trial.tensorflow);
        assert.equal(trial.rows.length,trial.total);
        assert.equal(trial.rows.filter(result=>result.passed).length,trial.passed);
        const failures=trial.rows.filter(result=>!result.passed);
        assert.equal(failures.length,4);
        assert.ok(failures.every(result=>result.mode==="reverse_forward"));
        const boundaries=trial.rows.filter(result=>result.kind==="genuine_third_refusal");
        assert.equal(boundaries.length,index?4:0);
        assert.ok(boundaries.every(result=>result.passed));
        assert.equal(trial.error_message_hashes.length,4);
        assert.ok(trial.error_message_hashes.every(hash=>/^[0-9a-f]{64}$/.test(hash)));
      }
    }else assert.fail("Unreviewed diagnostic kind: "+row.kind);
  }
});
test("new call-boundary diagnostics retain counterexamples without upgrading acceptance",async()=>{
  const declared=JSON.parse(await readFile(new URL("../../docs/engineering/diagnostic_observations.json",import.meta.url),"utf8"));
  const rows=declared.observations.filter(row=>row.kind==="tf_call_boundary_control");
  assert.deepEqual(rows.map(row=>row.profile).sort(),["alternate","main"]);
  for(const row of rows)assertCallBoundaryDiagnostic(row);
});
test("week-one review remains reachable and does not turn metadata into function acceptance",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  assert.equal(report.format,"quantumbridge.first-week-review.v1");
  assert.equal(report.state,"PRELIMINARY_OPEN_NOT_DENOMINATOR_CLOSURE");
  assert.equal(report.goal_complete,false);
  assert.equal(report.scope_reduced,false);
  assert.equal(report.estimated_completion_date,null);
  assert.equal(report.completed_full_contracts_in_review_register,0);
  assert.equal(report.complete_function_count_entire_goal,"UNKNOWN");
  assert.equal(report.hard_deadline,"2027-05-11T23:59:59+08:00");
  assert.equal(report.profile_counts_are_not_additive,true);
  assert.equal(report.mapping_links_do_not_prove_equivalence,true);
  assert.ok(report.reference_profiles.every(row=>row.denominator_closed===false&&row.all_tasks_unverified===true));
  assert.equal(report.industries.length,19);
  assert.equal(report.industries.reduce((sum,row)=>sum+row.registered_cases,0),29);
  assert.ok(report.industries.every(row=>row.business_acceptance==="UNVERIFIED"));
  assert.equal(report.hardware.per_function_acceptance,false);
  assert.equal(report.hardware.new_tasks,0);
  assert.equal(report.mapping_erratum.public_class_method_present,false);
  assert.equal(report.mapping_erratum.historical_observation_rewritten,false);
  assert.equal(report.mapping_reference_scope.corrected_public_exposure,"pennylane.map_wires");
  assert.equal(report.mapping_reference_scope.full_function_accepted,false);
  assert.ok(engineeringResources.every(row=>row.reviewDownload===engineeringReviewDownload));
  const source=await readFile(new URL("../src/progress/main.js",import.meta.url),"utf8");
  assert.ok(source.includes("data-first-week-review")&&source.includes("resourceHref(engineeringReviewDownload)"));
  assert.equal(engineeringReviewDownload.href,"/downloads/quantumbridge-first-week-review.json.gz");
  const reviewBytes=await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url));
  const archive=await readFile(new URL("../downloads/quantumbridge-first-week-review.json.gz",import.meta.url));
  assert.deepEqual(gunzipSync(archive),reviewBytes);
  assert.equal(JSON.stringify(report).includes("/Users/"),false);
});
test("SDK-only mixed diagnostics retain strict failures and never become Native passes",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.sdk_reference_origin_review;
  assert.equal(review.state,"SDK_ONLY_LIMITATIONS_REPRODUCED_NATIVE_FAILURES_NOT_WAIVED");
  assert.equal(review.production_native_changed,false);
  assert.equal(review.original_tests_changed,false);
  assert.equal(review.new_original_test_migrations,0);
  assert.equal(review.original_native_strict_failures_fixed,0);
  assert.equal(review.original_public_failures_waived,0);
  assert.equal(review.full_functions_accepted,0);
  assert.equal(review.full_strict_suite_accepted,false);
  assert.equal(review.public_api_denominator_closed,false);
  assert.equal(review.observer_snapshot_restamped,false);
  assert.equal(review.sdk_only_workers.length,8);
  assert.equal(review.diagnostic_observation_count,208);
  assert.equal(review.rejected_initial_harness.length,8);
  assert.ok(review.rejected_initial_harness.every(row=>row.accepted===false));
  assert.equal(review.sdk_only_workers.reduce((sum,row)=>sum+row.report.observations.length,0),208);
  for(const row of review.sdk_only_workers){
    assert.equal(row.normal_terminal,true);
    assert.equal(row.terminal_exit,0);
    assert.equal(row.reference_identity.verified,true);
    assert.equal(row.wrapper_is_not_numerical_acceptance,true);
    assert.equal(row.report.native_accepted,false);
    assert.equal(row.report.sdk_patched,false);
    assert.equal(row.report.global_configuration_changed,false);
    assert.equal(row.report.tolerances_relaxed,false);
    assert.deepEqual(row.report.native_modules_loaded,[]);
    assert.ok(row.report.observations.some(item=>item.completed===false));
    const diagonal=row.report.observations.find(item=>item.name==="rz_diagonal_vs_matrix");
    assert.equal(diagonal.completed,true);
    if(row.interface==="torch"){
      assert.equal(diagonal.result.eigenvalues.actual.dtype,"complex64");
      assert.equal(diagonal.result.eigenvalues.expected.dtype,"complex128");
      assert.equal(diagonal.result.diagonal_vs_full_matrix.original_bound_satisfied,false);
    }
  }
  for(const profile of review.profiles){
    const previous=report.selected_strict_context.profiles.find(row=>row.profile===profile.profile);
    assert.equal(profile.new_precision_regression.passed,24);
    assert.equal(profile.new_precision_regression.failed,0);
    assert.equal(profile.unchanged_tf_strict_recheck.failed,5);
    assert.deepEqual(profile.native_failure_ids,previous.unchanged_native_failure_ids);
    const frozen=report.phase_query_axes_review.profiles.find(row=>row.profile===profile.profile);
    assert.deepEqual(profile.reference_failure_ids,frozen.unchanged_public_reference_failure_ids);
    assert.ok(profile.reference_failure_ids.every(id=>previous.public_reference_failure_ids.includes(id)));
    assert.equal(profile.separate_reference_recheck.failed,profile.profile==="main"?47:59);
    assert.equal(profile.broader33module_native_context_and14module_reference_context_not_replaced,true);
  }
  assert.equal(review.new_hardware_tasks,0);
  assert.equal(review.goal_complete,false);
  assert.equal(report.completed_full_contracts_in_review_register,0);
});
test("six phase-query identities retain their historical partial revalidation",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.phase_query_contract_review;
  assert.equal(review.source_fingerprint,report.phase_query_axes_review.before_source_fingerprint);
  assert.notEqual(review.source_fingerprint,manifest.source.fingerprint);
  assert.notEqual(review.before_source_fingerprint,manifest.source.fingerprint);
  assert.equal(review.production_native_changed,true);
  assert.equal(review.original_tests_changed,false);
  assert.equal(review.new_original_test_migrations,0);
  assert.equal(review.new_native_cases_each,150);
  assert.equal(review.new_actual_reference_cases_each,50);
  assert.equal(review.signatures_and_entrypoints.length,6);
  assert.equal(review.strict_failures_fixed,0);
  assert.equal(review.full_function_acceptances_added,0);
  assert.equal(review.public_api_denominator_closed,false);
  assert.equal(review.full_strict_suite_accepted,false);
  assert.equal(review.normal_terminal_workers,110);
  assert.equal(review.before_results.length,2);
  assert.ok(review.before_results.every(row=>row.total===2&&row.failed===2&&row.source_fingerprint===review.before_source_fingerprint));
  assert.equal(review.results.length,108);
  assert.ok(review.results.every(row=>row.source_fingerprint===review.source_fingerprint&&row.environment_validation.verified));
  assert.equal(review.current_revalidation.source_fingerprint,historicalReportSource);
  assert.equal(review.current_revalidation.evidence.length,10);
  assert.equal(review.current_revalidation.full_function_accepted,false);
  const reviews=JSON.parse(await readFile(new URL("../../docs/engineering/function_reviews.json",import.meta.url),"utf8"));
  const register=report.review_register_context;
  assert.equal(register.frozen_source_fingerprint,historicalReportSource);
  assert.equal(register.frozen_observation_count,55);
  assert.equal(register.frozen_observations.length,register.frozen_observation_count);
  const remaining=reviews.slice();
  // Preserve all exact historical observations, including repeated function IDs.
  for(const frozen of register.frozen_observations){
    const index=remaining.findIndex(current=>isDeepStrictEqual(current,frozen));
    assert.ok(index>=0,`Missing or changed frozen review: ${frozen.id}`);
    assert.deepEqual(remaining.splice(index,1)[0],frozen);
  }
  for(const historical of register.later_local_observations){
    const index=remaining.findIndex(current=>isDeepStrictEqual(current,historical));
    assert.ok(index>=0,`Missing historical later review: ${historical.id}`);
    assert.deepEqual(remaining.splice(index,1)[0],historical);
  }
  const historical=[...register.frozen_observations,...register.later_local_observations];
  const latestHistorical=Math.max(...historical.map(row=>Date.parse(row.recorded_at)).filter(Number.isFinite));
  assert.equal(reviews.length,historical.length+remaining.length);
  assert.ok(remaining.every(row=>row.project_fingerprint!==historicalReportSource&&Date.parse(row.recorded_at)>=latestHistorical));
  assert.equal(register.later_observations_refresh_frozen_evidence,false);
  assert.equal(register.observation_counts_are_function_acceptance,false);
  assert.ok(register.later_local_observations.every(row=>row.project_fingerprint!==historicalReportSource));
  const current=register.frozen_observations.filter(row=>row.project_fingerprint===historicalReportSource);
  assert.equal(current.length,8);
  assert.ok(current.every(row=>row.status==="partial"&&row.contract_complete===false&&row.strict_tests_pass===false));
  const phase=current.filter(row=>row.kernel_file==="quantumbridge/qml/phase_queries.py");
  assert.equal(phase.length,6);
  assert.ok(phase.every(row=>row.prior_review_observations.at(-1).project_fingerprint===report.public_default_unitary_review.before_source_fingerprint));
  assert.ok(phase.every(row=>row.prior_review_reconstruction.prefix_length===4&&
    /^[0-9a-f]{64}$/.test(row.prior_review_reconstruction.previous_full_object_sha256)));
  assert.equal(report.completed_full_contracts_in_review_register,0);
});
test("phase axes fixes retain actual tensor-unitary and reference blockers without weakening contracts",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.phase_query_axes_review;
  assert.equal(review.source_fingerprint,report.live_unitary_source_review.before_source_fingerprint);
  assert.notEqual(review.source_fingerprint,manifest.source.fingerprint);
  assert.equal(review.before_source_fingerprint,report.phase_query_contract_review.source_fingerprint);
  assert.equal(review.fixes.length,2);
  assert.equal(review.normal_terminal_workers,116);
  assert.equal(review.before_results.length,4);
  assert.equal(review.results.length,112);
  assert.equal(review.new_partial_entries,0);
  assert.equal(review.new_native_strict_failures,16);
  assert.equal(review.new_reference_strict_failures_each,10);
  assert.equal(review.original_native_strict_failures_fixed,0);
  assert.equal(review.full_function_acceptances_added,0);
  assert.equal(review.original_tests_changed,false);
  assert.equal(review.new_original_test_migrations,0);
  for(const base of ["main","alternate"]){
    const rows=review.results.filter(row=>row.base_profile===base);
    const native=rows.find(row=>row.test_file==="tests/interfaces/test_native_phase_query_closure.py");
    const reference=rows.find(row=>row.test_file==="tests/compat/test_public_phase_query_axes.py");
    assert.deepEqual([native.total,native.passed,native.failed,native.skipped],[72,56,16,0]);
    assert.deepEqual([reference.total,reference.passed,reference.failed,reference.skipped],[56,46,10,0]);
    const priorNative=review.before_results.find(row=>row.base_profile===base&&row.lane==="native");
    const priorReference=review.before_results.find(row=>row.base_profile===base&&row.lane==="reference");
    assert.deepEqual([priorNative.total,priorNative.passed,priorNative.failed],[72,40,32]);
    assert.deepEqual([priorReference.total,priorReference.passed,priorReference.failed],[56,30,26]);
    assert.ok(native.failed_ids.every(id=>id.includes("test_static_matrix_drives_real_controlled_quantum_execution_with_absolute_phase")));
    const profile=review.profiles.find(row=>row.profile===base);
    assert.equal(profile.unchanged_native_failure_ids.length,5);
    assert.deepEqual(profile.new_composition_failure_ids,native.failed_ids);
    assert.deepEqual(profile.new_reference_failure_ids,reference.failed_ids);
    assert.equal(profile.current_selected_unique_failure_ids.length,21);
    assert.equal(profile.public_reference_failure_ids.length,base==="main"?57:69);
    assert.ok(profile.unchanged_native_failure_ids.every(id=>profile.current_selected_unique_failure_ids.includes(id)));
    assert.ok(profile.unchanged_public_reference_failure_ids.every(id=>profile.public_reference_failure_ids.includes(id)));
  }
  assert.ok(review.results.every(row=>row.source_fingerprint===review.source_fingerprint&&row.environment_validation.verified));
  assert.ok(review.before_results.every(row=>row.source_fingerprint===review.before_source_fingerprint));
  assert.equal(review.current_revalidation.source_fingerprint,historicalReportSource);
  for(const base of ["main","alternate"]){
    const closure=review.current_revalidation.evidence.find(row=>row.base_profile===base&&
      row.test_file==="tests/interfaces/test_native_phase_query_closure.py");
    assert.deepEqual([closure.total,closure.passed,closure.failed],[72,72,0]);
  }
  assert.equal(review.public_api_denominator_closed,false);
  assert.equal(review.full_strict_suite_accepted,false);
  assert.equal(review.goal_complete,false);
});
test("live general unitary evidence resolves old composition without hiding dtype or SDK gaps",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.live_unitary_source_review;
  assert.equal(review.source_fingerprint,report.unitary_precision_review.before_source_fingerprint);
  assert.notEqual(review.source_fingerprint,manifest.source.fingerprint);
  assert.equal(review.current_revalidation.source_fingerprint,historicalReportSource);
  assert.equal(review.before_source_fingerprint,report.phase_query_axes_review.source_fingerprint);
  assert.equal(review.normal_terminal_workers,314);
  assert.equal(review.current_terminal_workers,140);
  assert.equal(review.results.length,140);
  assert.equal(review.before_results.length,28);
  assert.equal(review.historical_results.length,146);
  assert.equal(review.frozen_stages.length,8);
  assert.equal(review.prepared_only_not_executed.length,2);
  assert.ok(review.prepared_only_not_executed.every(row=>row.accepted_as_verification===false));
  assert.equal(review.new_native_cases_each,77);
  assert.equal(review.new_actual_reference_cases_each,16);
  assert.equal(review.new_partial_entries,1);
  assert.equal(review.full_function_acceptances_added,0);
  assert.equal(review.resolved_selected_native_failures_each,16);
  assert.equal(review.original_five_tf_failures_fixed,0);
  assert.equal(review.new_dtype_strict_failures_each,4);
  assert.equal(review.original_tests_changed,false);
  assert.equal(review.new_original_test_migrations,0);
  assert.equal(review.fixed_numeric_owned_copy_preserved,true);
  assert.equal(review.live_tensor_identity_preserved,true);
  for(const base of ["main","alternate"]){
    const rows=review.results.filter(row=>row.base_profile===base);
    const matrix=rows.find(row=>row.test_file==="tests/interfaces/test_native_live_qubit_unitary.py");
    const boundary=rows.find(row=>row.test_file==="tests/interfaces/test_native_live_unitary_boundaries.py");
    const reference=rows.find(row=>row.test_file==="tests/compat/test_public_live_qubit_unitary.py");
    assert.deepEqual([matrix.total,matrix.passed,matrix.failed],[36,36,0]);
    assert.deepEqual([boundary.total,boundary.passed,boundary.failed],[41,37,4]);
    assert.deepEqual([reference.total,reference.passed,reference.failed],[16,15,1]);
    assert.ok(boundary.failed_ids.every(id=>id.includes("test_float32_matrix_rounding")));
    const prior=review.before_results.find(row=>row.base_profile===base&&row.test_file===boundary.test_file);
    assert.ok(boundary.failed_ids.every(id=>prior.failed_ids.includes(id)));
    const profile=review.profiles.find(row=>row.profile===base);
    assert.equal(profile.resolved_composition_failure_ids.length,16);
    assert.equal(profile.unchanged_native_failure_ids.length,5);
    assert.equal(profile.current_selected_unique_failure_ids.length,9);
    assert.ok(profile.resolved_composition_failure_ids.every(id=>!profile.current_selected_unique_failure_ids.includes(id)));
    assert.equal(profile.current_selected_scope.modules,49);
    assert.equal(profile.separate_reference_scope.modules,21);
  }
  assert.ok(review.results.every(row=>row.source_fingerprint===review.source_fingerprint&&
    row.accepted_as_current_source_verification&&row.environment_validation.verified&&row.full_function_accepted===false));
  assert.ok(review.historical_results.every(row=>!row.accepted_as_current_source_verification));
  const reviews=JSON.parse(await readFile(new URL("../../docs/engineering/function_reviews.json",import.meta.url),"utf8"));
  const entry=reviews.find(row=>row.id==="quantumbridge.qml.unitary.QubitUnitary");
  assert.equal(entry.status,"partial");
  assert.equal(entry.contract_complete,false);
  assert.equal(entry.project_fingerprint,historicalReportSource);
  assert.equal(entry.native_independent,true);
  assert.equal(review.public_api_denominator_closed,false);
  assert.equal(review.full_strict_suite_accepted,false);
  assert.equal(review.goal_complete,false);
});
test("JAX unitary validation follows actual coordinate precision without changing bounds or erasing failures",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.unitary_precision_review;
  assert.equal(review.source_fingerprint,report.public_matrix_action_review.before_source_fingerprint);
  assert.notEqual(review.source_fingerprint,manifest.source.fingerprint);
  assert.equal(review.current_revalidation.source_fingerprint,historicalReportSource);
  assert.equal(review.before_source_fingerprint,report.live_unitary_source_review.source_fingerprint);
  assert.equal(review.normal_terminal_workers,150);
  assert.equal(review.current_terminal_workers,144);
  assert.equal(review.results.length,144);
  assert.equal(review.before_results.length,6);
  assert.equal(review.new_native_cases_each,22);
  assert.equal(review.new_actual_reference_cases_each,24);
  assert.equal(review.resolved_selected_native_failures_each,2);
  assert.equal(review.original_five_tf_failures_fixed,0);
  assert.equal(review.remaining_dtype_strict_failures_each,2);
  assert.equal(review.projection_or_normalization_added,false);
  assert.equal(review.validation_constants_changed,false);
  assert.equal(review.original_tests_changed,false);
  assert.equal(review.new_original_test_migrations,0);
  assert.equal(review.full_function_acceptances_added,0);
  for(const base of ["main","alternate"]){
    const rows=review.results.filter(row=>row.base_profile===base);
    const precision=rows.find(row=>row.test_file==="tests/interfaces/test_native_unitary_precision_contract.py");
    const boundary=rows.find(row=>row.test_file==="tests/interfaces/test_native_live_unitary_boundaries.py");
    const reference=rows.find(row=>row.test_file==="tests/compat/test_public_unitary_precision_contract.py");
    assert.deepEqual([precision.total,precision.passed,precision.failed],[22,22,0]);
    assert.deepEqual([boundary.total,boundary.passed,boundary.failed],[41,39,2]);
    assert.deepEqual([reference.total,reference.passed,reference.failed],[24,18,6]);
    assert.ok(boundary.failed_ids.every(id=>id.includes("float32_matrix_rounding")&&id.includes("-autograd]")));
    assert.ok(reference.failed_ids.every(id=>id.includes("-autograd]")));
    const before=review.before_results.find(row=>row.base_profile===base&&row.test_file===precision.test_file);
    assert.deepEqual([before.total,before.passed,before.failed],[22,18,4]);
    const profile=review.profiles.find(row=>row.profile===base);
    assert.equal(profile.current_selected_scope.modules,50);
    assert.equal(profile.separate_reference_scope.modules,22);
    assert.equal(profile.current_selected_unique_failure_ids.length,7);
    assert.equal(profile.unchanged_native_failure_ids.length,5);
    assert.equal(profile.resolved_precision_failure_ids.length,2);
    assert.ok(profile.resolved_precision_failure_ids.every(id=>id.includes("-jax]")));
  }
  assert.ok(review.results.every(row=>row.source_fingerprint===review.source_fingerprint&&
    row.accepted_as_current_source_verification&&row.environment_validation.verified&&row.full_function_accepted===false));
  assert.ok(review.before_results.every(row=>row.source_fingerprint===review.before_source_fingerprint&&
    !row.accepted_as_current_source_verification));
  assert.equal(review.public_api_denominator_closed,false);
  assert.equal(review.full_strict_suite_accepted,false);
  assert.equal(review.goal_complete,false);
});
test("explicit public matrix evidence preserves default strict failures and cancelled integration history",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.public_matrix_action_review;
  assert.equal(review.source_fingerprint,report.public_default_unitary_review.before_source_fingerprint);
  assert.notEqual(review.source_fingerprint,manifest.source.fingerprint);
  assert.equal(review.before_source_fingerprint,report.unitary_precision_review.source_fingerprint);
  assert.equal(review.native_python_files,783);
  assert.equal(review.normal_terminal_workers,210);
  assert.equal(review.current_terminal_workers,150);
  assert.equal(review.results.length,150);
  assert.equal(review.historical_results.length,54);
  assert.equal(review.before_results.length,2);
  assert.equal(review.nonadditive_preflight_results.length,2);
  assert.equal(review.sdk_only_behavior_results.length,2);
  assert.equal(review.default_entry_changed,false);
  assert.equal(review.original_tests_changed,false);
  assert.equal(review.new_original_test_migrations,0);
  assert.equal(review.strict_validation_constants_changed,false);
  assert.equal(review.projection_or_normalization_added,false);
  assert.equal(review.resolved_selected_native_failures_each,0);
  assert.equal(review.original_five_tf_failures_fixed,0);
  assert.equal(review.remaining_dtype_strict_failures_each,2);
  assert.equal(review.new_native_cases_each,240);
  assert.equal(review.new_actual_reference_cases_each,48);
  assert.equal(review.sdk_only_behavior_cases_each,50);
  assert.equal(review.new_partial_entries,1);
  assert.equal(review.full_function_acceptances_added,0);
  assert.equal(review.cancelled_intermediate.accepted_as_normal_verification,false);
  assert.equal(review.cancelled_intermediate.observation.actual_tool_exit_code,137);
  assert.equal(review.cancelled_intermediate.observation.completed_normal_workers,48);
  assert.ok(review.nonadditive_preflight_results.every(row=>row.total===27&&row.passed===27));
  assert.ok(review.sdk_only_behavior_results.every(row=>row.total===50&&row.passed===50&&
    !row.accepted_as_current_source_verification&&row.full_function_accepted===false));
  assert.ok(review.before_results.every(row=>row.total===213&&row.failed===213&&
    row.source_fingerprint===review.before_source_fingerprint&&!row.accepted_as_current_source_verification));
  assert.ok(review.results.every(row=>row.source_fingerprint===review.source_fingerprint&&
    row.accepted_as_current_source_verification&&row.environment_validation.verified&&row.full_function_accepted===false));
  for(const base of ["main","alternate"]){
    const rows=review.results.filter(row=>row.base_profile===base);
    const action=rows.find(row=>row.test_file==="tests/interfaces/test_native_public_matrix_action.py");
    const boundary=rows.find(row=>row.test_file==="tests/interfaces/test_native_public_matrix_boundaries.py");
    const reference=rows.find(row=>row.test_file==="tests/compat/test_public_explicit_matrix_action.py");
    assert.deepEqual([action.total,action.passed,action.failed],[213,213,0]);
    assert.deepEqual([boundary.total,boundary.passed,boundary.failed],[27,27,0]);
    assert.deepEqual([reference.total,reference.passed,reference.failed],[48,42,6]);
    assert.ok(reference.failed_ids.every(id=>id.includes("-autograd]")));
    const profile=review.profiles.find(row=>row.profile===base);
    assert.deepEqual(profile.current_selected_scope,{modules:52,total:2478,passed:2471,failed:7,skipped:0});
    assert.equal(profile.separate_reference_scope.modules,23);
    assert.equal(profile.separate_reference_scope.total,1579);
    assert.equal(profile.public_reference_strict_failures,base==="main"?70:82);
    assert.deepEqual(profile.current_selected_unique_failure_ids,
      report.unitary_precision_review.profiles.find(row=>row.profile===base).current_selected_unique_failure_ids);
  }
  assert.equal(review.verification_ledger.before_records,5673);
  assert.equal(review.verification_ledger.after_records,5883);
  assert.equal(review.verification_ledger.original_rows_dates_and_unknown_fields_retained,true);
  assert.equal(review.public_api_denominator_closed,false);
  assert.equal(review.full_strict_suite_accepted,false);
  assert.equal(review.goal_complete,false);
});
test("public default migration keeps exact Legacy contracts and real compiler receipts",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.public_default_unitary_review;
  assert.equal(review.source_fingerprint,historicalReportSource);
  assert.equal(review.before_source_fingerprint,report.public_matrix_action_review.source_fingerprint);
  assert.equal(review.results.length,188);
  assert.equal(review.historical_results.length,112);
  assert.equal(review.normal_terminal_workers,300);
  assert.equal(review.default_entry_changed,true);
  assert.equal(review.original_tests_changed,true);
  assert.equal(review.new_original_test_migrations,2);
  assert.equal(review.approved_migration_files,30);
  assert.equal(review.approved_migration_cases,52);
  assert.equal(review.unchanged_original_test_files,1343);
  assert.equal(review.later_authored_test_migration_files,3);
  assert.equal(review.later_authored_test_migration_cases,11);
  assert.equal(review.projection_or_normalization_added,false);
  assert.equal(review.strict_validation_constants_changed,false);
  assert.equal(review.resolved_selected_native_failures_each,2);
  assert.equal(review.original_five_tf_failures_fixed,0);
  assert.equal(review.full_function_acceptances_added,0);
  assert.equal(review.renamed_public_class_not_new_function_count,true);
  assert.equal(review.cancelled_intermediate.actual_parent_tool_exit,137);
  assert.equal(review.cancelled_intermediate.completed_normal_workers,64);
  assert.equal(review.cancelled_intermediate.interrupted_workers_accepted,false);
  assert.equal(review.rejected_tensorflow_protocol.promoted_to_production,false);
  assert.equal(review.publication_target,"https://crystal-tensor.github.io/QuantumBridge/engineering.html");
  assert.equal(review.publication_read.authorization_changed,false);
  assert.equal(review.publication_read.global_configuration_changed,false);
  assert.deepEqual(review.rejected_tensorflow_protocol.each_profile,{total:16,passed:12,failed:4});
  assert.ok(review.results.every(row=>row.source_fingerprint===historicalReportSource&&
    row.accepted_as_current_source_verification&&row.environment_validation.verified&&!row.full_function_accepted));
  assert.ok(review.historical_results.every(row=>!row.accepted_as_current_source_verification));
  const original=JSON.parse(await readFile(new URL("../../docs/engineering/test_contract_migrations.json",import.meta.url),"utf8"));
  const later=JSON.parse(await readFile(new URL("../../docs/engineering/later_test_contract_migrations.json",import.meta.url),"utf8"));
  const frozen=historicalRegistry(report,"public_default_unitary_review");
  assert.equal(frozen.artifact.sha256,review.original_migration_audit.registry_sha256);
  const originalAtReview=frozen.registry.migrations;
  assert.equal(originalAtReview.length,30);
  assert.equal(originalAtReview.flatMap(row=>row.case_ids).length,52);
  const frozenRegistry=frozen.artifact.json;
  assert.equal(createHash("sha256").update(frozenRegistry).digest("hex"),review.original_migration_audit.registry_sha256);
  assert.equal(later.migrations.length,3);
  assert.equal(later.migrations.flatMap(row=>row.case_ids).length,11);
  const files=new Set(original.migrations.map(row=>row.file));
  for(const row of [...originalAtReview.slice(-2),...later.migrations]){
    assert.equal(row.ast_only_exact_target_callees_changed,true);
    assert.equal(row.mathematical_inputs_oracles_tolerances_and_assertions_preserved,true);
    const bytes=await readFile(new URL("../../"+row.file,import.meta.url));
    assert.equal(createHash("sha256").update(bytes).digest("hex"),row.after_sha256);
  }
  assert.ok(later.migrations.every(row=>!files.has(row.file)&&row.original_protected_baseline===false));
  for(const profile of review.profiles){
    assert.deepEqual(profile.current_selected_scope,{modules:66,total:2913,passed:2908,failed:5,skipped:0});
    assert.deepEqual(profile.same_prior_52_module_scope,{modules:52,total:2478,passed:2473,failed:5,skipped:0});
    assert.equal(profile.separate_reference_scope.modules,28);
    assert.equal(profile.separate_reference_scope.total,1889);
    assert.equal(profile.separate_reference_scope.failed,profile.profile==="main"?73:85);
    assert.equal(profile.newly_observed_reference_failure_ids.length,6);
    assert.equal(profile.resolved_prior_reference_failure_ids.length,3);
    assert.equal(profile.remaining_dtype_failure_ids.length,0);
    assert.equal(profile.resolved_selected_failure_ids.length,2);
    const rows=review.results.filter(row=>row.base_profile===profile.profile);
    for(const [file,total] of [["tests/compiler/test_public_matrix_unitary_compilation.py",33],
      ["tests/interfaces/test_native_default_unitary_resources.py",2],
      ["tests/interfaces/test_native_default_unitary_contract.py",55]]){
      const run=rows.find(row=>row.test_file===file);
      assert.deepEqual([run.total,run.passed,run.failed],[total,total,0]);
    }
  }
  assert.equal(review.verification_ledger.before_records,5883);
  assert.equal(review.verification_ledger.after_records,6183);
  assert.equal(review.verification_ledger.original_rows_dates_and_unknown_fields_retained,true);
  assert.equal(review.public_api_denominator_closed,false);
  assert.equal(review.full_strict_suite_accepted,false);
  assert.equal(review.new_hardware_tasks,0);
  assert.equal(review.goal_complete,false);
});
test("explicit QASM3 migrations retain old failures and do not count as Native implementation",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.qasm3_explicit_contract_migration_validation;
  const frozen=historicalRegistry(report,"qasm3_explicit_contract_migration_validation");
  const registry=frozen.registry;
  const currentRegistry=JSON.parse(await readFile(new URL("../../docs/engineering/test_contract_migrations.json",import.meta.url),"utf8"));
  assert.equal(review.source_fingerprint,report.density_pure_conversion_validation.source_fingerprint);
  assert.equal(review.production_math_changed,false);
  assert.deepEqual(review.native_files_changed,[]);
  assert.equal(review.original_tests_changed,true);
  assert.equal(review.new_original_test_migrations,2);
  assert.equal(review.approved_migration_files,32);
  assert.equal(review.approved_migration_cases,54);
  assert.equal(review.unchanged_original_test_files,1341);
  assert.deepEqual(registry.migrations.slice(30,32),review.migration_decisions);
  assert.equal(registry.migrations.slice(0,32).flatMap(row=>row.case_ids).length,54);
  for(const row of review.migration_decisions){
    assert.equal(row.owner_approved,true);
    assert.equal(row.decision_source,"standing_owner_decision_policy");
    assert.equal(row.no_separate_per_case_owner_reply_claimed,true);
    assert.equal(row.other_function_ASTs_and_parameterized_inputs_unchanged,true);
    assert.equal(row.math_tolerances_changed,false);
    assert.equal(row.production_resource_caps_changed,false);
    assert.equal(row.original_test_file_is_migrated_not_unchanged,true);
    assert.equal(row.case_ids.length,1);
    assert.equal(frozen.artifact.test_hashes[row.file],row.after_sha256);
    const current=currentRegistry.migrations.find(item=>item.file===row.file);
    assert.equal(current.owner_approved,true);
    assert.equal(current.before_sha256,row.before_sha256);
    assert.ok(row.case_ids.every(id=>current.case_ids.includes(id)));
    const bytes=await readFile(new URL("../../"+row.file,import.meta.url));
    assert.equal(createHash("sha256").update(bytes).digest("hex"),current.after_sha256);
  }
  assert.equal(review.results.length,36);
  assert.equal(review.normal_terminal_workers,36);
  assert.ok(review.results.every(row=>row.process_terminal_validation.provided&&
    row.process_terminal_validation.exit===(row.failed?1:0)&&row.environment_validation.verified));
  for(const profile of review.profiles){
    assert.deepEqual(profile.current_selected_scope,{modules:10,total:360,passed:354,failed:6,skipped:0});
    assert.equal(profile.current_selected_unique_failure_ids.length,6);
    assert.equal(profile.current_selected_unique_failure_ids.filter(id=>id.startsWith("tests.interfaces.")).length,5);
    assert.ok(profile.current_selected_unique_failure_ids.some(id=>id.includes("pow(a) @ mix")));
    assert.deepEqual(profile.separate_reference_scope,{configuration_id:profile.profile+"-arrow25-reference-v1",
      modules:2,total:111,passed:111,failed:0,skipped:0});
  }
  assert.equal(review.verification_ledger.before_records,6797);
  assert.equal(review.verification_ledger.after_records,6833);
  assert.equal(review.verification_ledger.original_rows_dates_and_unknown_fields_retained,true);
  assert.equal(review.genuine_native_failures_fixed,0);
  assert.equal(review.full_function_acceptances_added,0);
  assert.equal(review.full_strict_suite_accepted,false);
  assert.equal(review.public_api_denominator_closed,false);
  assert.equal(review.new_hardware_tasks,0);
  assert.equal(review.goal_complete,false);
});
test("atomic output precision retains new repair and all previous unresolved scopes",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.atomic_jet_transport_precision_validation;
  assert.notEqual(review.source_fingerprint,review.before_source_fingerprint);
  assert.notEqual(review.source_fingerprint,manifest.source.fingerprint);
  assert.equal(review.before_source_fingerprint,report.qasm3_explicit_contract_migration_validation.source_fingerprint);
  assert.deepEqual(review.native_files_changed,["quantumbridge/interfaces/native_atomic_jet.py"]);
  assert.equal(review.production_math_changed,false);
  assert.equal(review.production_output_validation_changed,true);
  assert.equal(review.original_tests_changed,false);
  assert.equal(review.new_original_test_migrations,0);
  assert.equal(review.normal_terminal_workers,32);
  assert.equal(review.results.length,32);
  assert.equal(review.new_regression_failures_fixed_each_profile,7);
  assert.equal(review.prior_strict_failure_ids_fixed,0);
  for(const profile of review.profiles){
    assert.deepEqual(profile.new_precision_native_before,{total:20,passed:13,failed:7,skipped:0});
    assert.deepEqual(profile.new_precision_native_after,{total:20,passed:20,failed:0,skipped:0});
    assert.deepEqual(profile.current_selected_scope,{modules:13,total:415,passed:409,failed:6,skipped:0});
    assert.deepEqual(profile.current_selected_unique_failure_ids,
      report.qasm3_explicit_contract_migration_validation.profiles.find(row=>row.profile===profile.profile).current_selected_unique_failure_ids);
    assert.equal(profile.separate_reference_scope.total,111);
    assert.equal(profile.separate_reference_scope.passed,111);
  }
  assert.ok(review.results.every(row=>row.process_terminal_validation.provided&&
    row.process_terminal_validation.exit===(row.failed?1:0)&&row.environment_validation.verified));
  assert.equal(review.verification_ledger.before_records,6833);
  assert.equal(review.verification_ledger.after_records,6865);
  assert.equal(review.verification_ledger.original_rows_dates_and_unknown_fields_retained,true);
  assert.equal(review.full_function_acceptances_added,0);
  assert.equal(review.full_strict_suite_accepted,false);
  assert.equal(review.public_api_denominator_closed,false);
  assert.equal(review.new_hardware_tasks,0);
  assert.equal(review.goal_complete,false);
  const partial=report.review_register_context.later_local_observations.find(row=>
    row.id==="quantumbridge.interfaces.native_atomic_jet.AtomicHostJet.run");
  assert.equal(partial.project_fingerprint,review.source_fingerprint);
  assert.equal(partial.status,"partial");
  assert.equal(partial.contract_complete,false);
  assert.equal(partial.target_sdk_differential_for_this_helper,false);
  assert.equal(createHash("sha256").update(await readFile(new URL("../../quantumbridge/interfaces/native_atomic_jet.py",import.meta.url))).digest("hex"),partial.source_hash);
});
test("TensorFlow output precision retains eight action paths and all previous unresolved scopes",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.tensorflow_graph_transport_precision_validation;
  assert.equal(review.before_source_fingerprint,report.atomic_jet_transport_precision_validation.source_fingerprint);
  assert.notEqual(review.source_fingerprint,review.before_source_fingerprint);
  assert.notEqual(review.source_fingerprint,manifest.source.fingerprint);
  assert.deepEqual(review.native_files_changed,["quantumbridge/interfaces/tensorflow_graph.py"]);
  assert.equal(review.production_math_changed,false);
  assert.equal(review.production_output_validation_changed,true);
  assert.equal(review.original_tests_changed,false);
  assert.equal(review.new_original_test_migrations,0);
  assert.equal(review.normal_terminal_workers,38);
  assert.equal(review.results.length,38);
  assert.equal(review.new_regression_failures_fixed_each_profile,40);
  assert.equal(review.prior_strict_failure_ids_fixed,0);
  assert.equal(review.all_new_tests_frozen_before_production_change,true);
  assert.equal(review.concurrent_owner_tests_only_interop_threads,2);
  assert.equal(review.other_worker_interop_threads,1);
  for(const profile of review.profiles){
    assert.deepEqual(profile.new_precision_native_before,{total:97,passed:57,failed:40,skipped:0});
    assert.deepEqual(profile.new_precision_native_after,{total:97,passed:97,failed:0,skipped:0});
    assert.deepEqual(profile.current_selected_scope,{modules:16,total:521,passed:515,failed:6,skipped:0});
    assert.deepEqual(profile.current_selected_unique_failure_ids,
      report.atomic_jet_transport_precision_validation.profiles.find(row=>row.profile===profile.profile).current_selected_unique_failure_ids);
    assert.equal(profile.separate_reference_scope.total,111);
    assert.equal(profile.separate_reference_scope.passed,111);
  }
  assert.ok(review.results.every(row=>row.process_terminal_validation.provided&&
    row.process_terminal_validation.exit===(row.failed?1:0)&&row.environment_validation.verified));
  assert.equal(review.verification_ledger.before_records,6865);
  assert.equal(review.verification_ledger.after_records,6903);
  assert.equal(review.verification_ledger.original_rows_dates_and_unknown_fields_retained,true);
  assert.equal(review.full_function_acceptances_added,0);
  assert.equal(review.full_strict_suite_accepted,false);
  assert.equal(review.public_api_denominator_closed,false);
  assert.equal(review.new_hardware_tasks,0);
  assert.equal(review.goal_complete,false);
  const partial=report.review_register_context.later_local_observations.find(row=>
    row.id==="quantumbridge.interfaces.tensorflow_graph.TensorFlowGraphKernel.run");
  assert.equal(partial.project_fingerprint,review.source_fingerprint);
  assert.equal(partial.status,"partial");
  assert.equal(partial.contract_complete,false);
  assert.equal(partial.target_sdk_differential_for_this_helper,false);
  assert.equal(createHash("sha256").update(await readFile(new URL("../../quantumbridge/interfaces/tensorflow_graph.py",import.meta.url))).digest("hex"),partial.source_hash);
});
test("ordinary host precision retains original children and broader unresolved contracts",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.ordinary_host_transport_precision_validation;
  assert.equal(review.before_source_fingerprint,report.tensorflow_graph_transport_precision_validation.source_fingerprint);
  assert.notEqual(review.source_fingerprint,review.before_source_fingerprint);
  assert.notEqual(review.source_fingerprint,historicalReportSource);
  assert.deepEqual(review.native_files_changed,["quantumbridge/interfaces/jax_autodiff.py",
    "quantumbridge/interfaces/jax_directional.py","quantumbridge/interfaces/tensorflow_autodiff.py"]);
  assert.equal(review.production_math_changed,false);
  assert.equal(review.original_tests_changed,false);
  assert.equal(review.new_original_test_migrations,0);
  assert.equal(review.normal_terminal_workers,80);
  assert.equal(review.results.length,80);
  assert.equal(review.new_regression_failures_fixed_each_profile,28);
  assert.equal(review.prior_strict_failure_ids_fixed,0);
  assert.equal(review.actual_original_x64_child_exits,8);
  assert.equal(review.actual_original_x64_child_source_and_dependencies_verified,true);
  for(const profile of review.profiles){
    assert.deepEqual(profile.new_precision_native_before,{total:106,passed:78,failed:28,skipped:0});
    assert.deepEqual(profile.new_precision_native_after,{total:106,passed:106,failed:0,skipped:0});
    assert.deepEqual(profile.current_selected_scope,{modules:34,total:1211,passed:1204,failed:7,skipped:0});
    assert.equal(profile.additional_broader_scope_failures_also_reproduced_before_repair.length,1);
    for(const id of report.tensorflow_graph_transport_precision_validation.profiles.find(x=>x.profile===profile.profile).current_selected_unique_failure_ids)
      assert.ok(profile.current_selected_unique_failure_ids.includes(id));
    assert.equal(profile.separate_reference_scope.total,111);
    assert.equal(profile.separate_reference_scope.failed,0);
  }
  assert.equal(review.initial_fixture_attempts.canonical_acceptance_added,0);
  assert.equal(review.initial_fixture_attempts.all_initial_sources_logs_and_exits_retained,true);
  assert.ok(review.results.every(row=>row.process_terminal_validation.provided&&
    row.process_terminal_validation.exit===(row.failed?1:0)&&row.environment_validation.verified));
  assert.equal(review.verification_ledger.before_records,6903);
  assert.equal(review.verification_ledger.after_records,6983);
  assert.equal(review.verification_ledger.original_rows_dates_and_unknown_fields_retained,true);
  assert.equal(review.full_function_acceptances_added,0);
  assert.equal(review.full_strict_suite_accepted,false);
  assert.equal(review.public_api_denominator_closed,false);
  assert.equal(review.new_hardware_tasks,0);
  assert.equal(review.goal_complete,false);
});
test("executable function packets keep exact evidence separate from complete contracts",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const packetReview=report.executable_acceptance_packets;
  assert.equal(packetReview.packet_count,7);
  assert.equal(packetReview.completed_full_functions,0);
  assert.equal(packetReview.complete_denominator_closed,false);
  assert.equal(packetReview.native_source_fingerprint,report.phase_query_contract_review.before_source_fingerprint);
  assert.notEqual(packetReview.native_source_fingerprint,manifest.source.fingerprint);
  assert.equal(packetReview.current_source_revalidation.source_fingerprint,historicalReportSource);
  assert.equal(packetReview.current_source_revalidation.original_plan_ids_and_dates_preserved,true);
  assert.equal(packetReview.current_source_revalidation.complete_functions_accepted,0);
  assert.equal(packetReview.current_source_revalidation.evidence.length,16);
  assert.ok(packetReview.current_source_revalidation.evidence.every(row=>row.source_fingerprint===historicalReportSource&&row.failed===0));
  assert.equal(packetReview.builder_terminal.exit,0);
  assert.equal(packetReview.builder_terminal.timed_out,false);
  assert.equal(packetReview.normal_module_processes,20);
  assert.equal(packetReview.new_original_test_migrations,1);
  assert.equal(packetReview.shared_module_receipts_must_not_be_multiplied_by_packet_count,true);
  const observations=new Map();
  for(const packet of packetReview.packets){
    assert.match(packet.id,/^[0-9a-f]{64}$/);
    assert.equal(packet.contract_complete,false);
    assert.equal(packet.full_function_accepted,false);
    assert.equal(Object.keys(packet.axes).length,14);
    assert.ok(Object.values(packet.axes).every(axis=>axis.state==="unverified"));
    assert.deepEqual(packet.missing_executable_axes,["broadcasting","serialization","derivatives","sdk_free_installation","composition"]);
    const native=await readFile(new URL("../../"+packet.native.file,import.meta.url));
    assert.equal(packet.native.file_sha256,createHash("sha256").update(native).digest("hex"));
    assert.equal(packet.references.length,2);
    assert.ok(packet.references.every(row=>!row.contexts_merged&&!row.runtime_execution_verified));
    assert.equal(packet.execution_evidence.length,4);
    assert.equal(packet.hardware_applicability.hardware_certified,false);
    for(const run of packet.execution_evidence){
      assert.equal(run.process_terminal_validation.exit,0);
      assert.equal(run.environment_validation.verified,true);
      assert.equal(run.failed,0);
      assert.equal(run.skipped,0);
      assert.equal(run.module_level_evidence_only,true);
      assert.equal(run.full_function_accepted,false);
      assert.equal(run.reference_definition_hash_rechecked_by_this_worker,false);
      if(run.lane==="reference"){
        const identity=run.reference_execution_identity_validation;
        assert.equal(identity.verified,true);
        assert.equal(identity.configuration_id,run.base_profile+"-arrow25-reference-v1");
        assert.deepEqual(identity.observed_sdks,["qiskit"]);
        assert.equal(identity.roots.qiskit.loaded,true);
        assert.equal(identity.roots.pennylane.loaded,false);
      }
      if(observations.has(run.name))assert.deepEqual(observations.get(run.name),run);
      observations.set(run.name,run);
    }
  }
  assert.equal(observations.size,16);
  for(const base of ["main","alternate"]){
    const runs=[...observations.values()].filter(run=>run.base_profile===base);
    assert.equal(runs.filter(run=>run.lane==="native").reduce((sum,run)=>sum+run.total,0),297);
    assert.equal(runs.filter(run=>run.lane==="reference").reduce((sum,run)=>sum+run.total,0),139);
  }
  assert.ok(report.historical_reviews.length>=1);
  assert.equal(report.historical_reviews[0].original_report.generated_at,"2026-11-16T11:11:09.345803+00:00");
  assert.equal(report.selected_strict_context.reexecuted_by_this_review,true);
  assert.deepEqual(report.selected_strict_context.profiles.map(row=>row.scope.failed),[5,5]);
  assert.equal(report.selected_strict_context.source_fingerprint,historicalReportSource);
  assert.equal(report.selected_strict_context.prior_public_scope_not_reexecuted,false);
  assert.equal(report.selected_strict_context.approved_original_contract_changes,2);
  assert.equal(report.selected_strict_context.later_authored_contract_changes,11);
  assert.ok(report.selected_strict_context.profiles.every(row=>row.scope.modules===66&&
    row.scope.passed===row.scope.total-5));
  assert.deepEqual(report.selected_strict_context.profiles.map(row=>row.public_reference_strict_failures),
    report.public_default_unitary_review.profiles.map(row=>row.public_reference_strict_failures));
  assert.deepEqual(report.prior_selected_strict_context.profiles.map(row=>row.scope.failed),[52,64]);
  assert.equal(report.prior_selected_strict_context.fresh_for_current_source,false);
  assert.notEqual(report.prior_selected_strict_context.source_fingerprint,manifest.source.fingerprint);
});
test("public partial trace keeps exact scoped receipts and original failures without claiming equivalence",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.public_partial_trace;
  assert.equal(review.state,"PARTIAL_NOT_COMPLETE_EQUIVALENCE");
  assert.equal(review.source_fingerprint,report.phase_query_contract_review.before_source_fingerprint);
  assert.notEqual(review.source_fingerprint,manifest.source.fingerprint);
  assert.equal(review.current_revalidation.source_fingerprint,historicalReportSource);
  assert.equal(review.current_revalidation.evidence.length,4);
  assert.ok(review.current_revalidation.evidence.every(row=>row.source_fingerprint===historicalReportSource&&row.failed===0));
  assert.equal(review.complete_function_accepted,false);
  assert.equal(review.goal_complete,false);
  assert.equal(review.original_tests_changed,false);
  assert.equal(review.new_original_test_migrations,0);
  assert.equal(review.unchanged_original_files,1346);
  assert.equal(review.previously_authorized_files,27);
  assert.equal(review.previously_authorized_cases,49);
  assert.equal(review.preserves_legacy,true);
  assert.equal(review.no_sdk_implementation_forwarded,true);
  assert.equal(review.new_dependencies_installed,false);
  assert.equal(review.new_hardware_tasks,0);
  assert.equal(review.normal_terminal_workers,46);
  assert.equal(review.verification_ledger.added_normal_records,46);
  assert.equal(review.before.length,2);
  assert.equal(review.after.length,4);
  const evidence=new Set();
  for(const row of [...review.before,...review.after]){
    assert.equal(row.process_terminal_validation.exit,row.failed?1:0);
    assert.equal(row.environment_validation.verified,true);
    assert.equal(row.skipped,0);
    assert.equal(row.full_function_accepted,false);
    assert.equal(evidence.has(row.evidence_hash),false);
    evidence.add(row.evidence_hash);
  }
  for(const row of review.before){
    assert.equal(row.total,172);assert.equal(row.passed,4);assert.equal(row.failed,168);
    assert.notEqual(row.source_fingerprint,manifest.source.fingerprint);
  }
  for(const row of review.after){
    assert.equal(row.total,row.lane==="native"?172:71);
    assert.equal(row.passed,row.total);assert.equal(row.failed,0);
    assert.equal(row.source_fingerprint,review.source_fingerprint);
    if(row.lane==="reference")assert.equal(row.reference_execution_identity_validation.verified,true);
  }
  assert.equal(review.strict_original_modules.length,4);
  assert.equal(review.known_reference_discrepancies.length,4);
  assert.ok(review.all_selected_profiles.every(row=>row.current_selected_scope.total===30&&
    row.current_selected_scope.passed===25&&row.current_selected_scope.failed===5&&
    row.current_selected_unique_failure_ids.length===5&&row.public_reference_strict_failures===null));
});
test("single QASM3 contract migration retains source identity, uninitialized errors and prior proof",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.qasm_scope_contract_review;
  assert.equal(review.state,"ONE_OBSOLETE_REFUSAL_MIGRATED_NOT_A_NEW_NATIVE_IMPLEMENTATION");
  assert.equal(review.source_fingerprint,report.phase_query_contract_review.before_source_fingerprint);
  assert.notEqual(review.source_fingerprint,manifest.source.fingerprint);
  assert.equal(review.current_revalidation.source_fingerprint,historicalReportSource);
  assert.equal(review.current_revalidation.evidence.length,2);
  assert.equal(review.new_migration_files,1);assert.equal(review.new_migration_cases,1);
  assert.equal(review.protected_original_files,1373);
  assert.equal(review.unchanged_original_files,1345);
  assert.equal(review.approved_files,28);assert.equal(review.approved_cases,50);
  assert.equal(review.production_native_changed,false);
  assert.equal(review.math_tolerances_changed,false);
  assert.equal(review.original_other_functions_unchanged,true);
  assert.equal(review.qasm2_refusal_preserved,true);
  assert.equal(review.default_uuid_refusal_preserved,true);
  assert.equal(review.explicit_warning_required,true);
  assert.equal(review.uninitialized_read_never_becomes_false,true);
  assert.equal(review.native_strict_failures_fixed,0);
  assert.equal(review.full_functions_accepted,0);assert.equal(review.full_goal_complete,false);
  assert.equal(review.decision.owner_approved,true);
  assert.equal(review.decision.decision_source,"standing_owner_decision_policy");
  assert.equal(review.decision.no_separate_per_case_owner_reply_claimed,true);
  assert.deepEqual(review.decision.case_ids,["tests.serialization.test_native_composed_circuit_roundtrip::test_qasm_metadata_loss_permission_cannot_silently_drop_classical_scope[3]"]);
  assert.equal(review.positive_before_migration.length,8);
  assert.equal(review.positive_after_migration.length,8);
  for(const base of ["main","alternate"]){
    const before=review.original_before.find(row=>row.base_profile===base);
    const after=review.original_after.find(row=>row.base_profile===base);
    assert.equal(before.total,10);assert.equal(before.passed,9);assert.equal(before.failed,1);
    assert.equal(after.total,10);assert.equal(after.passed,10);assert.equal(after.failed,0);
    assert.notEqual(before.source_manifest_sha256,after.source_manifest_sha256);
    assert.equal(before.source_fingerprint,after.source_fingerprint);
    for(const group of [review.positive_before_migration,review.positive_after_migration]){
      const rows=group.filter(row=>row.base_profile===base);
      assert.equal(rows.filter(row=>row.lane==="native").reduce((sum,row)=>sum+row.total,0),84);
      const reference=rows.find(row=>row.lane==="reference");
      assert.equal(reference.total,8);
      assert.equal(reference.reference_execution_identity_validation.verified,true);
      assert.ok(rows.every(row=>row.failed===0&&row.skipped===0&&row.process_terminal_validation.exit===0&&
        row.environment_validation.verified===true));
    }
  }
  assert.equal(review.baseline_ledger.added_normal_records,68);
  assert.equal(review.baseline_ledger.excluded_reference_workers.length,2);
  assert.ok(review.baseline_ledger.excluded_reference_workers.every(row=>row.accepted_as_verification===false));
  assert.equal(review.after_ledger.added_normal_records,94);
  assert.deepEqual(review.reference_selection_correction.actual_required_and_allowed,["qiskit"]);
});
test("rejected point-transport prototypes cannot become Native passes or erase strict failures",async()=>{
  const report=JSON.parse(await readFile(new URL("../downloads/quantumbridge-first-week-review.json",import.meta.url),"utf8"));
  const review=report.tf_boundary_investigation;
  assert.equal(review.state,"REJECTED_POINT_TRANSPORT_AND_EXPLICIT_OPERATION_PROTOTYPES_NOT_REPAIRS");
  assert.equal(review.production_native_changed,false);
  assert.equal(review.original_tests_changed,false);
  assert.equal(review.strict_failures_fixed,0);
  assert.equal(review.new_full_function_acceptances,0);
  assert.equal(review.candidate_passes_added_to_native_verification,0);
  assert.equal(review.public_api_denominator_closed,false);
  assert.equal(review.full_strict_suite_accepted,false);
  assert.equal(review.observations.length,8);
  assert.equal(review.baselines.length,2);
  assert.equal(review.initial_diagnostic_only_original_baselines,2);
  assert.equal(review.diagnostic_only_candidate_records,6);
  assert.match(review.original_terminal_binding_rejection,/NEW untouched baseline workers/);
  for(const base of ["main","alternate"]){
    const rows=review.observations.filter(row=>row.profile===base);
    assert.deepEqual(rows.map(row=>row.variant),["original","vjp","both","operation"]);
    for(const row of rows){
      assert.equal(row.total,22);
      assert.equal(row.passed,18);
      assert.equal(row.failed,4);
      assert.equal(row.skipped,0);
      assert.equal(row.terminal.exit,1);
      assert.equal(row.terminal.timed_out,false);
      assert.equal(row.accepted_as_native_verification,false);
      assert.equal(row.third_order_policy_qualified,false);
      assert.deepEqual(row.failed_ids,rows[0].failed_ids);
      for(const field of ["terminal_sha256","junit_sha256","log_sha256","guard_sha256","environment_sha256","origin_sha256"])
        assert.match(row[field],/^[0-9a-f]{64}$/);
    }
    const baseline=review.baselines.find(row=>row.profile===base);
    assert.equal(baseline.total,22);
    assert.equal(baseline.passed,18);
    assert.equal(baseline.failed,4);
    assert.equal(baseline.skipped,0);
    assert.equal(baseline.process_terminal_validation.exit,1);
    assert.equal(baseline.environment_validation.verified,true);
  }
  assert.equal(review.verification_ledger.after_records-review.verification_ledger.before_records,2);
  assert.equal(review.old_diagnostic_store_and_abnormal_processes_unchanged,true);
  assert.equal(review.observer_snapshot_restamped,false);
  assert.equal(review.refreshed_for_new_source,false);
  assert.notEqual(review.historical_source_fingerprint,manifest.source.fingerprint);
  assert.deepEqual(report.selected_strict_context.profiles.map(row=>row.native_strict_failures),[5,5]);
});
test("goal and selected verification never masquerade as final acceptance", () => {
  assert.equal(manifest.core_execution,"active");
  assert.equal(manifest.goal_execution.scope_reduced,false);
  assert.equal(manifest.acceptance_scope.final_gates.length,9);
  assert.ok(manifest.acceptance_scope.final_gates.every(g=>g.state!=="COMPLETE"));
  assert.ok(manifest.strict_backlog.length>=47);
  for(const row of manifest.strict_backlog.filter(x=>x.review_note)) {
    assert.equal(row.status,"current_failure");
    assert.ok(row.review_note.diagnosis&&row.review_note.next);
  }
  for(const row of manifest.strict_backlog.filter(x=>x.historical_review_note)) {
    assert.equal(row.status,"current_failure");
    assert.equal(row.historical_review_note.source_match,false);
    assert.notEqual(row.historical_review_note.source_fingerprint,manifest.source.fingerprint);
    assert.ok(row.historical_review_note.diagnosis&&row.historical_review_note.next);
    assert.equal(row.review_note,undefined);
  }
  for(const run of manifest.verification){
    assert.equal(run.source_match,run.source_fingerprint===manifest.source.fingerprint&&run.example_input_validation?.passed!==false&&run.test_context_match!==false&&run.process_terminal_match===true);
    assert.equal(run.total,run.passed+run.failed+run.skipped);
    assert.equal(run.cases.length,run.total);
    assert.equal(run.protected_tests_unchanged,true);
    assertVerificationScope(run);
    if(run.approved_test_migrations?.length){
      const files=new Set(run.approved_test_migrations.map(m=>m.file));
      assert.equal(run.protected_tests+files.size,run.original_protected_test_files);
      assert.ok(run.approved_test_migrations.every(m=>m.owner_approved&&m.before_sha256!==m.after_sha256&&m.case_ids.length));
      if(run.source_match){
        const core = manifest.goal_execution[manifest.goal_execution.latest_core_validation_key];
        // Same Native bytes can have older, still-valid per-run test contexts.
        // Only this batch's source manifest carries its newer approval ledger.
        if(!core || run.source_manifest_sha256===core.source_manifest_sha256){
          assert.equal(files.size,core?.approved_migration_files ?? manifest.goal_execution.latest_strict_review.approved_files);
          assert.equal(run.approved_test_migrations.flatMap(m=>m.case_ids).length,core?.approved_migration_cases ?? manifest.goal_execution.latest_strict_review.approved_cases);
        }
        const memory=run.approved_test_migrations.find(m=>m.file==="tests/interfaces/test_native_tf_mps_resource_contract.py");
        if(memory){
          assert.deepEqual(memory.case_ids,["tests.interfaces.test_native_tf_mps_resource_contract::test_managed_mps_queries_same_parent_cache_tiny_hessian_cap"]);
          assert.equal(memory.production_resource_accounting_changed,false);
          assert.equal(memory.math_tolerances_changed,false);
        }
      }
    }
  }
  const seen=new WeakSet();
  function privatePathsAbsent(value){
    if(typeof value==="string")assert.ok(!value.includes("/Users/")&&!value.includes("site-packages/"));
    else if(value&&typeof value==="object"&&!seen.has(value)){
      seen.add(value);
      for(const [key,item] of Object.entries(value)){privatePathsAbsent(key);privatePathsAbsent(item);}
    }
  }
  privatePathsAbsent(manifest);
  for(const observation of abnormalObservations(manifest.goal_execution)){
    assert.equal(observation.accepted_as_verification,false);
    assert.equal(observation.process_exit,-11);
    assert.ok(!manifest.verification.some(run=>run.evidence_hash===observation.junit_sha256));
  }
});
test("supplementary Native-only receipts cannot become SDK or NumPy baseline acceptance", () => {
  const supplement = manifest.verification.find(run => run.supplemental_configuration);
  assert.ok(supplement);
  assertVerificationScope(supplement);
  for (const mutate of [
    run => { run.scope = "full_sdk_acceptance"; },
    run => { run.scope = "selected_strict_batch_not_full_contract_or_full_suite"; },
    run => { run.supplemental_configuration.id = "unknown"; },
    run => { run.supplemental_configuration.owner_approved = false; },
    run => { run.supplemental_configuration.configuration_sha256 = "0".repeat(64); },
    run => { run.supplemental_configuration.sdk_reference = true; },
    run => { run.supplemental_configuration.canonical_dependency_profiles_changed = true; },
    run => { run.profile = "main"; },
    run => { run.environment.numpy = "2.4.6"; },
    run => { run.child_execution_validation.children[0].sdk_modules_loaded = ["qiskit"]; },
    run => { run.child_execution_validation.children[0].process_exit = -11; },
  ]) {
    const invalid = structuredClone(supplement);
    mutate(invalid);
    assert.throws(() => assertVerificationScope(invalid));
  }
});
test("subtle entrances are registered in all four home domains", async () => {
  assert.equal(engineeringResources.length,4);
  for(const item of engineeringResources) {assert.ok(domainResources(item.domain).includes(item));assert.equal(item.subtle,true);}
  const eco=await readFile(new URL("../src/ecosystem/main.js",import.meta.url),"utf8");
  assert.ok(eco.includes('class="engineering-dot"')&&eco.includes('./engineering.html'));
});
test("scoped contract details never promote stale or incomplete reviews", async () => {
  for(const dataset of ["target","native"]){
    const rows=JSON.parse(gunzipSync(await readFile(new URL(`../src/progress/data/${dataset}.json.gz`,import.meta.url))));
    for(const row of rows.filter(x=>x.review)){
      assert.equal(row.review.project_fingerprint,manifest.source.fingerprint);
      assert.equal(row.review.source_hash,row.source_hash);
      if(!row.review.contract_complete)assert.notEqual(row.status,"implemented");
      assert.ok(row.review.evidence_hash&&row.review.evidence_scope);
      assert.ok(row.review.remaining);
    }
  }
  const ui=await readFile(new URL("../src/progress/main.js",import.meta.url),"utf8");
  assert.ok(ui.includes("row.review.evidence_scope")&&ui.includes("row.review.native_entry")&&ui.includes("row.review.remaining"));
});
test("current worker receipts and bounded windows preserve all evidence", () => {
  const current=currentVerification(manifest);
  assert.equal(current.batchMatches,true);
  assert.equal(current.rows.length,manifest.verification.filter(row=>row.source_match&&row.environment_validation?.verified).length);
  const coreKey=manifest.goal_execution.latest_core_validation_key;
  if(coreKey){
    assert.equal(current.batch,manifest.goal_execution[coreKey]);
    assert.ok(current.reports.length>0);
    assert.ok(current.reports.every(row=>row.report.source_manifest_sha256===current.batch.source_manifest_sha256));
  }else{
    assert.equal(current.reviewMatches,true);
    assert.deepEqual(current.failures,current.reviewedFailures);
    assert.ok(current.reports.some(row=>row.scope==="inventory"));
    assert.ok(current.reports.some(row=>row.scope==="reference"));
  }
  assert.ok(current.reports.every(row=>current.rows.some(run=>run.evidence_hash===row.report.evidence_hash&&run.recorded_at===row.recordedAt)));
  const first=verificationWindow(manifest.verification,0);
  const second=verificationWindow(manifest.verification,1);
  assert.equal(first.rows.length,20);
  assert.equal(second.rows.length,20);
  assert.notEqual(first.rows[0].name,second.rows[0].name);
  assert.equal(first.total,manifest.verification.length);
  assert.equal(verificationWindow(manifest.verification,999999).index,first.pages-1);
  assert.equal(currentVerification({...manifest,source:{fingerprint:"other"}}).batchMatches,false);
  assert.equal(currentVerification({...manifest,verification:manifest.verification.map(row=>({...row,environment_validation:{verified:false}}))}).reviewMatches,false);
  const redacted=manifest.verification.flatMap(row=>row.cases).filter(row=>row.parameter_identity_redacted);
  assert.equal(manifest.verification_projection.redacted_parameter_ids,redacted.length);
  assert.ok(redacted.length>=30,"The append-only ledger must retain its historical private-parameter records");
  assert.ok(redacted.every(row=>/^[0-9a-f]{64}$/.test(row.original_id_sha256)&&
    row.id.endsWith("[private-parameter-sha256="+row.original_id_sha256+"]")));
  assert.equal(manifest.verification_projection.private_ledger_modified,false);
  for(const run of manifest.verification){
    if(!run.test_context){assert.equal(run.source_match,false);continue;}
    assert.equal(manifest.test_contexts[run.test_context.files_ref].files.length,run.test_context.file_count);
    assert.equal(manifest.test_contexts[run.test_context.files_ref].sha256,run.test_context.sha256);
  }
});
test("equal failure counts with different case identities cannot match a strict review",()=>{
  const fixture={source:{fingerprint:"fixture"},goal_execution:{latest_strict_review:{checkpoint:"review",
    source_fingerprint:"fixture",current_selected_unique_failures_each_profile:1},
    reviewed:{checkpoint:"review",source_fingerprint:"fixture",profiles:["main","alternate"].map(profile=>
      ({profile,current_selected_unique_failure_ids:["original"]}))}},
    verification:["main","alternate"].map(profile=>({profile,source_match:true,environment_validation:{verified:true},
      recorded_at:"2026-11-13T00:00:00Z",cases:[{id:"original",status:"failed"}]}))};
  assert.equal(currentVerification(fixture).reviewMatches,true);
  const changed={...fixture,verification:fixture.verification.map(run=>({...run,cases:run.cases.map(item=>
    item.status==="failed"?{...item,id:"different-case:"+item.id}:item)}))};
  const actual=currentVerification(changed);
  assert.equal(actual.failures.main.length,1);
  assert.equal(actual.failures.alternate.length,1);
  assert.equal(actual.reviewMatches,false);
});
test("profile-specific strict counts require both exact declared identities and numeric counts",()=>{
  const identities={main:["native-a","public-b"],alternate:["native-a"]};
  const fixture={source:{fingerprint:"fixture"},goal_execution:{latest_strict_review:{checkpoint:"review",
    source_fingerprint:"fixture",current_selected_unique_failures_each_profile:{main:2,alternate:1}},
    reviewed:{checkpoint:"review",source_fingerprint:"fixture",profiles:Object.entries(identities).map(([profile,ids])=>
      ({profile,current_selected_unique_failure_ids:ids}))}},
    verification:Object.entries(identities).map(([profile,ids])=>({profile,source_match:true,environment_validation:{verified:true},
      recorded_at:"2026-11-17T00:00:00Z",cases:ids.map(id=>({id,status:"failed"}))}))};
  const actual=currentVerification(fixture);
  assert.equal(actual.reviewMatches,true);
  assert.deepEqual(actual.reviewCounts,{main:2,alternate:1});
  for(const counts of [{main:1,alternate:2},{main:2},{main:2,alternate:"1"},{main:2,alternate:-1},
    {main:2,alternate:1,extra:0},[2,1],null]) {
    const changed={...fixture,goal_execution:{...fixture.goal_execution,latest_strict_review:{
      ...fixture.goal_execution.latest_strict_review,current_selected_unique_failures_each_profile:counts}}};
    assert.equal(currentVerification(changed).reviewMatches,false);
  }
  const changed={...fixture,verification:fixture.verification.map(row=>row.profile!=="alternate"?row:{...row,
    cases:[{id:"different-but-same-count",status:"failed"}]})};
  assert.equal(currentVerification(changed).reviewMatches,false);
});
test("runtime wire pooling preserves every signature and owner context", async () => {
  const descriptor=manifest.datasets.find(row=>row.id==="runtime");
  const wire=JSON.parse(gunzipSync(await readFile(new URL(`../src/progress/data/${descriptor.file}`,import.meta.url))));
  assert.equal(wire.encoding,"signature-pool-v1");
  const rows=decodeDataset(wire);
  assert.equal(rows.length,descriptor.count);
  assert.ok(Object.keys(wire.signatures).length<rows.length);
  for(let i=0;i<rows.length;i++) for(let j=0;j<rows[i].runtime_observations.length;j++){
    const before=wire.rows[i].runtime_observations[j],after=rows[i].runtime_observations[j];
    if(before.signature_ref) assert.deepEqual(after.signature,wire.signatures[before.signature_ref]);
    assert.equal(after.canonical_id,before.canonical_id);
    assert.equal(after.lookup_plane,before.lookup_plane);
  }
  assert.throws(()=>decodeDataset({schema:2,encoding:"signature-pool-v1",signatures:{},rows:[{runtime_observations:[{signature_ref:"absent"}]}]}));
  for(const audit of manifest.runtime_census){
    const descriptor=audit.object_identity_groups_artifact;
    const raw=await readFile(new URL(`../src/progress/data/${descriptor.file}`,import.meta.url));
    assert.equal(createHash("sha256").update(raw).digest("hex"),descriptor.sha256);
    const value=JSON.parse(gunzipSync(raw));
    assert.equal(value.groups.length,audit.object_identity_group_count);
    assert.equal(value.groups.reduce((sum,group)=>sum+group.record_ids.length,0),audit.records);
    assert.equal(value.native_functions_accepted,0);
  }
});
test("public build includes progress assets, inventory and goal prompt without private paths", async () => {
  const output=await mkdtemp(path.join(tmpdir(),"qb-engineering-build-"));
  try{
    await buildPublic(output);
    for(const file of ["engineering.html","src/progress/main.js","src/progress/transport.js","src/progress/data/manifest.json","src/progress/data/manifest-browser.json.gz","src/progress/data/manifest-evidence.json.gz","src/progress/data/native.json.gz","src/progress/data/target.json.gz","downloads/quantumbridge-six-month-goal.txt"]){assert.ok((await readFile(path.join(output,file))).length>0);}
    const boot=JSON.parse(gunzipSync(await readFile(path.join(output,"src/progress/data/manifest-browser.json.gz"))));
    const evidence=await readFile(path.join(output,"src/progress/data",boot.deferred_evidence.file));
    assert.equal(createHash("sha256").update(evidence).digest("hex"),boot.deferred_evidence.sha256);
    assert.deepEqual(await restoreMigrationPool(restoreManifest(boot,await readManifestEvidence(path.join(output,"src/progress/data"),boot.deferred_evidence))),manifest);
    const html=await readFile(path.join(output,"engineering.html"),"utf8");assert.ok(html.includes('./src/progress/main.js'));
    const goal=await readFile(path.join(output,"downloads/quantumbridge-six-month-goal.txt"),"utf8");assert.ok(goal.startsWith('/goal\n'));assert.ok(goal.includes("2027-05-11"));
  }finally{await rm(output,{recursive:true,force:true});}
});
