import assert from "node:assert/strict";
import test from "node:test";
import { readFile, mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { gunzipSync } from "node:zlib";
import { createHash } from "node:crypto";
import { countStatuses, filterRows, aggregate, isStale, statuses } from "../src/progress/model.js";
import { engineeringResources, domainResources } from "../src/framework/resources.js";
import { buildPublic } from "./build-public.mjs";

const manifest = JSON.parse(await readFile(new URL("../src/progress/data/manifest.json", import.meta.url)));
test("inventory integrity, conservative states, unique IDs, no local paths or credentials", async () => {
  for (const descriptor of manifest.datasets) {
    const bytes = await readFile(new URL(`../src/progress/data/${descriptor.file}`, import.meta.url));
    assert.equal(createHash("sha256").update(bytes).digest("hex"), descriptor.sha256);
    const text = gunzipSync(bytes).toString();
    const rows = JSON.parse(text);
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
test("runtime census is not combined with the target denominator or implementation acceptance", async () => {
  const descriptor=manifest.datasets.find(x=>x.id==="runtime");
  assert.ok(descriptor.count>0);
  const rows=JSON.parse(gunzipSync(await readFile(new URL(`../src/progress/data/${descriptor.file}`,import.meta.url))));
  assert.ok(rows.every(r=>r.status==="unverified"&&r.native_mapping===null));
  assert.ok(rows.some(r=>r.runtime_observations.some(o=>o.inherited)));
  assert.ok(rows.some(r=>r.exposures.includes("pennylane.transforms.expand_multipar")));
  assert.equal(manifest.runtime_census.length,2);
  assert.ok(manifest.runtime_census.every(a=>a.census_complete===false&&a.modules.some(m=>m.name==="qiskit_finance"&&!m.available)));
});
test("recursive census retains traversal gaps, loaded identities and accessor provenance", async () => {
  const descriptor=manifest.datasets.find(x=>x.id==="runtime");
  const rows=JSON.parse(gunzipSync(await readFile(new URL(`../src/progress/data/${descriptor.file}`,import.meta.url))));
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
  assert.equal(manifest.diagnostic_observations.length,5);
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
    }else{
      assert.equal(row.kind,"arrow_coexistence_review");
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
    }
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
        assert.equal(files.size,manifest.goal_execution.latest_batch.approved_test_migration_files);
        assert.equal(run.approved_test_migrations.flatMap(m=>m.case_ids).length,manifest.goal_execution.latest_batch.approved_test_migration_cases);
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
test("public build includes progress assets, inventory and goal prompt without private paths", async () => {
  const output=await mkdtemp(path.join(tmpdir(),"qb-engineering-build-"));
  try{
    await buildPublic(output);
    for(const file of ["engineering.html","src/progress/main.js","src/progress/data/manifest.json","src/progress/data/native.json.gz","src/progress/data/target.json.gz","downloads/quantumbridge-six-month-goal.txt"]){assert.ok((await readFile(path.join(output,file))).length>0);}
    const html=await readFile(path.join(output,"engineering.html"),"utf8");assert.ok(html.includes('./src/progress/main.js'));
    const goal=await readFile(path.join(output,"downloads/quantumbridge-six-month-goal.txt"),"utf8");assert.ok(goal.startsWith('/goal\n'));assert.ok(goal.includes("2027-05-11"));
  }finally{await rm(output,{recursive:true,force:true});}
});
