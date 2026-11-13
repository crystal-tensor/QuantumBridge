import test from "node:test";
import assert from "node:assert/strict";
import { currentVerification, abnormalObservations } from "../src/progress/model.js";

const fingerprint = "a".repeat(64);
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
    alias:{abnormal_process_observations:[old]}};
  assert.deepEqual(abnormalObservations(goal),[old,newer]);
  assert.equal(abnormalObservations(goal)[0].recorded_at,"original");
});
