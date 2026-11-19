import test from "node:test";
import assert from "node:assert/strict";
import { currentVerification, abnormalObservations, originalChildFollowup } from "../src/progress/model.js";
import { restoreMigrationPool } from "../src/progress/migration-pool.js";
import { createHash } from "node:crypto";

const fingerprint = "a".repeat(64);
function migrationWire(){
  const table=[{file:"tests/original.py",case_ids:["original::case"],owner_approved:true,unknown:{kept:[false,null]}}];
  const text=JSON.stringify(table), key=createHash("sha256").update(text).digest("hex");
  const expected={verification:[{name:"old",failed:1,recorded_at:"old-date",approved_test_migrations:structuredClone(table)},
    {name:"new",failed:0,recorded_at:"new-date",approved_test_migrations:structuredClone(table)}],unknown:{preserved:true}};
  const wire={...expected,verification:expected.verification.map(({approved_test_migrations,...row})=>({...row,approved_test_migrations_ref:key})),
    verification_migration_pool:{schema:1,encoding:"approved-test-migrations-pool-v1",contexts:{[key]:{sha256:key,bytes:Buffer.byteLength(text),json:text}}}};
  return {wire,expected,key};
}
test("migration-table transport restores exact records without merging identities or mutable tables",async()=>{
  const {wire,expected}=migrationWire(), frozen=JSON.stringify(wire);
  const result=await restoreMigrationPool(wire);
  assert.deepEqual(result,expected);assert.equal(JSON.stringify(wire),frozen);
  result.verification[0].approved_test_migrations[0].file="changed";
  assert.equal(result.verification[1].approved_test_migrations[0].file,"tests/original.py");
});
test("unpooled migration evidence remains unchanged",async()=>{
  const value={verification:[],unknown:"kept"};assert.equal(await restoreMigrationPool(value),value);
});
test("unopened migration tables stay lazy while reads and assignments retain independent ordinary values",async()=>{
  const {wire}=migrationWire(), result=await restoreMigrationPool(wire);
  const [first,second]=result.verification;
  assert.equal(typeof Object.getOwnPropertyDescriptor(first,"approved_test_migrations").get,"function");
  assert.equal(typeof Object.getOwnPropertyDescriptor(second,"approved_test_migrations").get,"function");
  const table=first.approved_test_migrations;
  assert.equal(first.approved_test_migrations,table);
  table[0].file="only first";
  assert.equal(typeof Object.getOwnPropertyDescriptor(second,"approved_test_migrations").get,"function");
  second.approved_test_migrations=[{file:"assigned"}];
  assert.equal(second.approved_test_migrations[0].file,"assigned");
  assert.equal(first.approved_test_migrations[0].file,"only first");
  assert.equal(Object.getOwnPropertyDescriptor(second,"approved_test_migrations").writable,true);
  delete second.approved_test_migrations;
  assert.equal(Object.hasOwn(second,"approved_test_migrations"),false);
});
for(const mutation of ["hash","size","boolean_size","missing","ambiguous","schema","encoding","unused","orphan","table"]){
  test(`migration-table transport rejects ${mutation}`,async()=>{
    const {wire,key}=migrationWire(), pool=wire.verification_migration_pool, context=pool.contexts[key];
    if(mutation==="hash")context.json+=" ";
    if(mutation==="size")context.bytes++;
    if(mutation==="boolean_size")context.bytes=true;
    if(mutation==="missing")pool.contexts={};
    if(mutation==="ambiguous")wire.verification[0].approved_test_migrations=[];
    if(mutation==="schema")pool.schema=true;
    if(mutation==="encoding")pool.encoding="future";
    if(mutation==="unused")wire.verification=[];
    if(mutation==="orphan")delete wire.verification_migration_pool;
    if(mutation==="table"){
      const text=JSON.stringify({not:"a table"}), changed=createHash("sha256").update(text).digest("hex");
      pool.contexts={[changed]:{sha256:changed,bytes:Buffer.byteLength(text),json:text}};
      wire.verification.forEach(row=>{row.approved_test_migrations_ref=changed;});
    }
    await assert.rejects(restoreMigrationPool(wire));
  });
}
function childFollowupFixture() {
  const profiles = ["main", "alternate", "main-native-only-no-user-site", "alternate-native-only-no-user-site"];
  const verification = profiles.map(profile => {
    const supplemental = profile.endsWith("-no-user-site"), count = supplemental ? 5 : 20;
    const version = supplemental ? "1.26.4" : "2.4.6";
    const prefix = supplemental ? "tests.primitives.test_public_primitive_reentry::" : "tests.derivative_execution.test_memory_ticket_handoff::";
    return {name:"followup-"+profile, profile, evidence_hash:profile, source_manifest_sha256:"manifest", source_match:true,
      total:count, passed:count, failed:0, skipped:0, environment:{numpy:version}, environment_validation:{verified:true},
      process_terminal_validation:{exit:0}, child_execution_validation:{verified:true,
        children:[{process_exit:0,original_probe_executed:true,loaded_dependencies:{numpy:{reported_version:version}}}]},
      cases:Array.from({length:count},(_,index)=>({id:prefix+index,status:"passed"}))};
  });
  return {source:{fingerprint},verification,goal_execution:{original_child_followup_validation:{source_fingerprint:fingerprint,
    source_manifest_sha256:"manifest",results:verification.map(({name,profile,evidence_hash})=>({name,profile,evidence_hash})),
    unadmitted_executions:["main","alternate"].map(profile=>({profile,execution_admitted:false,terminal_exit:0,timed_out:false}))}}};
}

test("original-child follow-up binds baseline and Native-only receipts without adding their populations",()=>{
  const manifest=childFollowupFixture(), before=JSON.stringify(manifest), result=originalChildFollowup(manifest);
  assert.equal(result.rows.length,4);
  assert.deepEqual(result.rows.map(row=>row.total),[20,20,5,5]);
  assert.equal(result.unadmitted.length,2);
  assert.equal(JSON.stringify(manifest),before);
});
test("a later Native source cannot refresh historical original-child evidence",()=>{
  const manifest=childFollowupFixture();
  manifest.source.fingerprint="b".repeat(64);
  manifest.verification.forEach(row=>{row.source_match=false;});
  const before=JSON.stringify(manifest);
  assert.equal(originalChildFollowup(manifest),null);
  assert.equal(manifest.goal_execution.original_child_followup_validation.source_fingerprint,fingerprint);
  assert.equal(manifest.verification.length,4);
  assert.equal(JSON.stringify(manifest),before);
});
for(const mutation of ["source","manifest","missing","duplicate","environment","child_exit","terminal_exit",
    "child_dependency","unadmitted_count","promoted_rejection","wrong_cases","wrong_count"]){
  test(`original-child follow-up rejects ${mutation} evidence`,()=>{
    const manifest=childFollowupFixture(), batch=manifest.goal_execution.original_child_followup_validation, proof=manifest.verification[0];
    if(mutation==="source")batch.source_fingerprint="b".repeat(64);
    if(mutation==="manifest")proof.source_manifest_sha256="other";
    if(mutation==="missing")manifest.verification.pop();
    if(mutation==="duplicate")batch.results[3]=batch.results[2];
    if(mutation==="environment")proof.environment.numpy="1.26.4";
    if(mutation==="child_exit")proof.child_execution_validation.children[0].process_exit=-11;
    if(mutation==="terminal_exit")proof.process_terminal_validation.exit=-11;
    if(mutation==="child_dependency")proof.child_execution_validation.children[0].loaded_dependencies.numpy.reported_version="1.26.4";
    if(mutation==="unadmitted_count")batch.unadmitted_executions.pop();
    if(mutation==="promoted_rejection")batch.unadmitted_executions[0].execution_admitted=true;
    if(mutation==="wrong_cases")proof.cases[0].id="unrelated::case";
    if(mutation==="wrong_count")proof.total=21;
    assert.equal(originalChildFollowup(manifest),null);
  });
}
function fixture() {
  const run = (name, profile, status, recorded_at) => ({name, profile, recorded_at,
    source_match:true, environment_validation:{verified:true}, source_manifest_sha256:"manifest",
    evidence_hash:name, passed:status==="passed"?1:0, failed:status==="failed"?1:0,
    cases:[{id:"original-case",status}]});
  return {source:{fingerprint},goal_execution:{latest_core_validation_key:"new_core",
    new_core:{checkpoint:"current",source_fingerprint:fingerprint,source_manifest_sha256:"manifest"},
    latest_verification_batch:{checkpoint:"old",source_fingerprint:"old"}},
    verification:[run("old-main","main","failed","2026-11-12T00:00:00Z"),
      run("old-alternate","alternate","failed","2026-11-12T00:00:00Z"),
      run("new-main","main","passed","2026-11-13T00:00:00Z")]};
}

test("the explicit current core pointer retains old evidence and follows later canonical receipts",()=>{
  const manifest=fixture(), original=JSON.stringify(manifest), value=currentVerification(manifest);
  assert.equal(value.batch.checkpoint,"current");
  assert.equal(value.batchMatches,true);
  assert.deepEqual(value.failures,{main:[],alternate:["original-case"]});
  assert.equal(value.rows.length,3);
  assert.equal(value.reports.length,3);
  assert.equal(value.reviewMatches,false);
  assert.equal(JSON.stringify(manifest),original);
  manifest.verification.reverse();
  assert.deepEqual(currentVerification(manifest).failures,value.failures);
});

test("runtime variants do not resolve canonical failures without a canonical receipt",()=>{
  const manifest=fixture();
  manifest.verification.at(-1).profile="main-tf-interop2";
  assert.deepEqual(currentVerification(manifest).failures,{main:["original-case"],alternate:["original-case"]});
});

test("unadmitted module summaries cannot become canonical case outcomes",()=>{
  const manifest=fixture();
  const baseline=currentVerification(manifest);
  manifest.goal_execution.new_core.profiles=[{profile:"alternate",unadmitted_module_count:1,
    unadmitted_modules:["tests/blocked_child.py"],all_selected_module_executions_admitted:false}];
  const value=currentVerification(manifest);
  assert.deepEqual(value.failures,baseline.failures);
  assert.equal(value.rows.length,baseline.rows.length);
  assert.equal(value.rows.some(row=>row.cases.some(item=>item.id.includes("blocked_child"))),false);
  assert.equal(value.reviewMatches,false);
});

test("mismatched source or missing worker metadata cannot promote the new batch",()=>{
  const manifest=fixture();
  manifest.verification.at(-1).environment_validation.verified=false;
  assert.deepEqual(currentVerification(manifest).failures.main,["original-case"]);
  manifest.source.fingerprint="other";
  assert.equal(currentVerification(manifest).batchMatches,false);
});

test("abnormal processes from new checkpoints preserve all original crash identities",()=>{
  const old={selection:"old",recorded_at:"original",source_fingerprint:"old-source",crash_report_sha256:"first",accepted_as_verification:false};
  const newer={selection:"new",recorded_at:"new-time",source_fingerprint:fingerprint,crash_report_sha256:"second",process_exit:-11,accepted_as_verification:false};
  const goal={latest_batch:{abnormal_process_observations:[old]},new_core:{abnormal_process_observations:[newer]},
    alias:{abnormal_process_observations:[old]},
    publication_receipt:{abnormal_process_observations:4}};
  assert.deepEqual(abnormalObservations(goal),[old,newer]);
  assert.equal(abnormalObservations(goal)[0].recorded_at,"original");
});

test("summary reports cannot replace the canonical source-bound worker receipt",()=>{
  const manifest=fixture();
  manifest.goal_execution.new_core.profiles=[{profile:"main",reports:{selected:{
    evidence_hash:"new-main",source_manifest_sha256:"untrusted-summary",passed:999}}}];
  const current=currentVerification(manifest);
  assert.equal(current.reports.length,1);
  assert.equal(current.reports[0].scope,"selected");
  assert.equal(current.reports[0].report,manifest.verification.at(-1));
  assert.equal(current.reports[0].report.source_manifest_sha256,"manifest");
  assert.equal(current.reports[0].report.passed,1);
  assert.equal(current.reports[0].recordedAt,manifest.verification.at(-1).recorded_at);
});

function referenceFixture(){
  const manifest=fixture();
  manifest.goal_execution.new_core.profiles=[{profile:"main",public_reference_failure_ids:["public-case"],
    separate_reference_scope:{configuration_id:"main-arrow25-reference-v1",modules:1,total:1,passed:0,failed:1,skipped:0}}];
  manifest.verification.push({name:"actual-reference",profile:"main-arrow25-reference-v1",source_match:true,
    environment_validation:{verified:true},source_manifest_sha256:"manifest",recorded_at:"2026-11-14T00:00:00Z",
    reference_execution_identity_validation:{verified:true,configuration_id:"main-arrow25-reference-v1"},
    cases:[{id:"public-case",status:"failed"}]});
  return manifest;
}
test("separate SDK failures require exact canonical identities and never replace Native failures",()=>{
  const manifest=referenceFixture(),value=currentVerification(manifest);
  assert.deepEqual(value.failures,{main:[],alternate:["original-case"]});
  assert.equal(value.references.length,1);
  assert.equal(value.references[0].matches,true);
  assert.deepEqual(value.references[0].counts,{total:1,passed:0,failed:1,skipped:0});
  assert.deepEqual(value.references[0].failureIds,["public-case"]);
});
test("an exact reference receipt selection excludes overlapping local replays",()=>{
  const manifest=referenceFixture(), proof=manifest.verification.at(-1);
  proof.evidence_hash="c".repeat(64);
  manifest.goal_execution.new_core.profiles[0].separate_reference_scope.execution_evidence=[
    {name:proof.name,profile:proof.profile,evidence_hash:proof.evidence_hash}];
  manifest.verification.push({...proof,name:"overlapping-local-replay",evidence_hash:"d".repeat(64),
    cases:[{id:"unrelated-local-case",status:"passed"}]});
  const value=currentVerification(manifest).references[0];
  assert.equal(value.matches,true);
  assert.equal(value.proofCount,1);
  assert.deepEqual(value.counts,{total:1,passed:0,failed:1,skipped:0});
});
for(const change of [rows=>rows.push({...rows[0]}),rows=>{rows[0].evidence_hash="missing";},
    rows=>{rows[0].name="other";},rows=>{rows[0].profile="other";}]){
  test("an invalid exact reference receipt selection cannot certify a group",()=>{
    const manifest=referenceFixture(),proof=manifest.verification.at(-1);
    proof.evidence_hash="c".repeat(64);
    const selection=[{name:proof.name,profile:proof.profile,evidence_hash:proof.evidence_hash}];
    change(selection);
    manifest.goal_execution.new_core.profiles[0].separate_reference_scope.execution_evidence=selection;
    assert.equal(currentVerification(manifest).references[0].matches,false);
  });
}
test("missing, stale or unrelated SDK identity cannot certify a reference group",()=>{
  for(const change of [row=>{delete row.reference_execution_identity_validation;},row=>{row.source_match=false;},
    row=>{row.reference_execution_identity_validation.configuration_id="other";},row=>{row.source_manifest_sha256="other";}]){
    const manifest=referenceFixture();change(manifest.verification.at(-1));
    const value=currentVerification(manifest).references[0];
    assert.equal(value.matches,false);assert.equal(value.counts.total,0);
  }
});
test("declared SDK counts and failure identities cannot overwrite actual outcomes",()=>{
  const manifest=referenceFixture();
  manifest.goal_execution.new_core.profiles[0].separate_reference_scope.failed=999;
  assert.equal(currentVerification(manifest).references[0].matches,false);
  assert.equal(currentVerification(manifest).references[0].counts.failed,1);
  manifest.goal_execution.new_core.profiles[0].separate_reference_scope.failed=1;
  manifest.goal_execution.new_core.profiles[0].public_reference_failure_ids=["invented-case"];
  assert.equal(currentVerification(manifest).references[0].matches,false);
});

function currentNativeReviewFixture() {
  const manifest = fixture();
  manifest.goal_execution.latest_strict_review = { checkpoint: "historical-review",
    source_fingerprint: "old", current_selected_unique_failures_each_profile: 99 };
  manifest.goal_execution.new_core.profiles = ["main", "alternate"].map(profile => ({ profile,
    native_strict_failures: 1, current_selected_unique_failure_ids: ["current-failure"] }));
  manifest.verification = ["main", "alternate"].map(profile => ({ profile, source_match: true,
    environment_validation: { verified: true }, source_manifest_sha256: "manifest",
    recorded_at: "2026-11-14T00:00:00Z", cases: [{ id: "current-failure", status: "failed" }] }));
  return manifest;
}

test("the explicit current core review supersedes an older strict-summary pointer", () => {
  const manifest = currentNativeReviewFixture(), before = JSON.stringify(manifest);
  const current = currentVerification(manifest);
  assert.equal(current.review, manifest.goal_execution.new_core);
  assert.equal(current.reviewBatch, manifest.goal_execution.new_core);
  assert.equal(current.reviewMatches, true);
  assert.deepEqual(current.reviewCounts, { main: 1, alternate: 1 });
  assert.equal(JSON.stringify(manifest), before);
});

test("current core review requires independently declared numeric counts and exact case identities", () => {
  for (const change of [
    row => { row.native_strict_failures = 2; },
    row => { row.native_strict_failures = "1"; },
    row => { delete row.native_strict_failures; },
    row => { row.current_selected_unique_failure_ids = ["different-case"]; },
    row => { delete row.current_selected_unique_failure_ids; },
  ]) {
    const manifest = currentNativeReviewFixture();
    change(manifest.goal_execution.new_core.profiles[0]);
    assert.equal(currentVerification(manifest).reviewMatches, false);
  }
});

test("a missing or stale explicit core pointer cannot fall back to an older matching review", () => {
  for (const change of [
    manifest => { manifest.goal_execution.new_core.source_fingerprint = "stale"; },
    manifest => { manifest.goal_execution.latest_core_validation_key = "missing"; },
    manifest => { manifest.verification[0].environment_validation.verified = false; },
    manifest => { manifest.goal_execution.new_core.profiles.push({ ...manifest.goal_execution.new_core.profiles[0] }); },
  ]) {
    const manifest = currentNativeReviewFixture();
    manifest.goal_execution.latest_strict_review = { checkpoint: "legacy", source_fingerprint: fingerprint,
      current_selected_unique_failures_each_profile: 1 };
    manifest.goal_execution.legacy = { checkpoint: "legacy", source_fingerprint: fingerprint,
      profiles: structuredClone(manifest.goal_execution.new_core.profiles) };
    change(manifest);
    assert.equal(currentVerification(manifest).reviewMatches, false);
  }
});
