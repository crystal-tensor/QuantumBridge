import assert from "node:assert/strict";
import test from "node:test";
import { readFile, mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { gunzipSync } from "node:zlib";
import { createHash } from "node:crypto";
import { countStatuses, filterRows, aggregate, isStale, statuses, decodeDataset, verificationWindow, currentVerification, restoreManifest, deferredManifestFields } from "../src/progress/model.js";
import { engineeringResources, domainResources } from "../src/framework/resources.js";
import { buildPublic } from "./build-public.mjs";

const manifest = JSON.parse(await readFile(new URL("../src/progress/data/manifest.json", import.meta.url)));
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
  const payload = JSON.parse(gunzipSync(raw));
  assert.deepEqual(restoreManifest(bootstrap, payload), manifest);
  assert.equal(bootstrap.generated_at, manifest.generated_at);
  assert.deepEqual(descriptor.fields, deferredManifestFields);
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
  const raw=await readFile(new URL("manifest.json",base));
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
  const investigation = manifest.goal_execution.current_investigation;
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
  assert.ok(manifest.hardware.every(x => x.task_id && x.artifact_hash && x.acceptance === "INCONCLUSIVE"));
  for(const r of manifest.hardware){assert.equal(r.shots,r.count_sum);assert.equal(r.domain,"finance");assert.ok(!("openqasm" in r));}
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
  assert.equal(manifest.diagnostic_observations.length,13);
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
    }else assert.fail("Unreviewed diagnostic kind: "+row.kind);
  }
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
    assert.equal(run.scope,"selected_strict_batch_not_full_contract_or_full_suite");
    if(run.approved_test_migrations?.length){
      const files=new Set(run.approved_test_migrations.map(m=>m.file));
      assert.equal(run.protected_tests+files.size,run.original_protected_test_files);
      assert.ok(run.approved_test_migrations.every(m=>m.owner_approved&&m.before_sha256!==m.after_sha256&&m.case_ids.length));
      if(run.source_match){
        assert.equal(files.size,manifest.goal_execution.latest_strict_review.approved_files);
        assert.equal(run.approved_test_migrations.flatMap(m=>m.case_ids).length,manifest.goal_execution.latest_strict_review.approved_cases);
        const memory=run.approved_test_migrations.find(m=>m.file==="tests/interfaces/test_native_tf_mps_resource_contract.py");
        if(memory){
          assert.deepEqual(memory.case_ids,["tests.interfaces.test_native_tf_mps_resource_contract::test_managed_mps_queries_same_parent_cache_tiny_hessian_cap"]);
          assert.equal(memory.production_resource_accounting_changed,false);
          assert.equal(memory.math_tolerances_changed,false);
        }
      }
    }
  }
  const text=JSON.stringify(manifest);
  assert.ok(!text.includes("/Users/")&&!text.includes("site-packages/"));
  for(const observation of manifest.goal_execution.latest_batch.abnormal_process_observations || []){
    assert.equal(observation.accepted_as_verification,false);
    assert.equal(observation.process_exit,-11);
    assert.ok(!manifest.verification.some(run=>run.evidence_hash===observation.junit_sha256));
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
  assert.equal(current.reviewMatches,true);
  assert.equal(current.rows.length,98);
  assert.equal(current.failures.main.length,25);
  assert.equal(current.failures.alternate.length,25);
  assert.deepEqual(current.failures,current.reviewedFailures);
  assert.ok(current.reports.some(row=>row.scope==="inventory"));
  assert.ok(current.reports.some(row=>row.scope==="reference"));
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
  assert.equal(redacted.length,30);
  assert.ok(redacted.every(row=>row.id.endsWith(row.original_id_sha256+"]")));
  assert.equal(manifest.verification_projection.private_ledger_modified,false);
  for(const run of manifest.verification){
    if(!run.test_context){assert.equal(run.source_match,false);continue;}
    assert.equal(manifest.test_contexts[run.test_context.files_ref].files.length,run.test_context.file_count);
    assert.equal(manifest.test_contexts[run.test_context.files_ref].sha256,run.test_context.sha256);
  }
});
test("equal failure counts with different case identities cannot match a strict review",()=>{
  const changed={...manifest,verification:manifest.verification.map(run=>({...run,cases:run.cases.map(item=>
    item.status==="failed"?{...item,id:"different-case:"+item.id}:item)}))};
  const actual=currentVerification(changed);
  assert.equal(actual.failures.main.length,25);
  assert.equal(actual.failures.alternate.length,25);
  assert.equal(actual.reviewMatches,false);
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
    assert.deepEqual(restoreManifest(boot,JSON.parse(gunzipSync(evidence))),manifest);
    const html=await readFile(path.join(output,"engineering.html"),"utf8");assert.ok(html.includes('./src/progress/main.js'));
    const goal=await readFile(path.join(output,"downloads/quantumbridge-six-month-goal.txt"),"utf8");assert.ok(goal.startsWith('/goal\n'));assert.ok(goal.includes("2027-05-11"));
  }finally{await rm(output,{recursive:true,force:true});}
});
