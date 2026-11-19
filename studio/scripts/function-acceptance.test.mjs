import test from "node:test";
import assert from "node:assert/strict";
import { fullContractReview } from "../src/progress/model.js";
import fs from "node:fs";
import { gunzipSync } from "node:zlib";
import { createHash } from "node:crypto";

const fingerprint = "a".repeat(64);
function row() {
  return { status:"implemented", source_hash:"b".repeat(64), review:{
    status:"implemented", source_hash:"b".repeat(64), project_fingerprint:fingerprint,
    contract_complete:true, native_independent:true, versions_verified:true,
    strict_tests_pass:true, evidence_hash:"c".repeat(64) } };
}
test("only exact current full contracts receive accepted-function presentation",()=>{
  assert.equal(fullContractReview(row(),fingerprint),true);
  for(const key of ["contract_complete","native_independent","versions_verified","strict_tests_pass"]){
    const item=row();item.review[key]=false;assert.equal(fullContractReview(item,fingerprint),false);
  }
  for(const change of [item=>{item.status="partial";},item=>{item.review.status="partial";},
    item=>{item.review.source_hash="different";},item=>{item.review.project_fingerprint="old";},
    item=>{item.review.evidence_hash="not-a-hash";},item=>{delete item.review;}]){
    const item=row();change(item);assert.equal(fullContractReview(item,fingerprint),false);
  }
});

test("the first batch has twenty distinct canonical contracts, not aliases or selected test counts",()=>{
  const batch=JSON.parse(fs.readFileSync(new URL("../../docs/engineering/first_thirty_function_batch.json",import.meta.url)));
  const reviews=JSON.parse(fs.readFileSync(new URL("../../docs/engineering/function_reviews.json",import.meta.url)));
  const accepted=batch.functions.filter(row=>row.contract_complete);
  assert.equal(batch.functions.length,30);assert.equal(accepted.length,20);
  assert.equal(batch.remaining_batch_functions,10);
  assert.equal(new Set(accepted.map(row=>row.canonical_target)).size,20);
  assert.equal(new Set(accepted.map(row=>row.native_entry)).size,20);
  assert.equal(accepted.filter(row=>row.family==="predicates").length,9);
  assert.equal(accepted.filter(row=>row.family==="analysis").length,7);
  assert.equal(accepted.filter(row=>row.family==="metrics").length,4);
  assert.equal(batch.core_source_published,false);assert.equal(batch.full_suite_passed,false);
  assert.equal(batch.new_original_test_migrations,0);
  const raw=gunzipSync(fs.readFileSync(new URL(`../src/progress/data/function-contracts-${batch.source_fingerprint}.json.gz`,import.meta.url)));
  const bundle=JSON.parse(raw);
  assert.equal(bundle.source_fingerprint,batch.source_fingerprint);
  assert.equal(bundle.functions.length,20);
  assert.doesNotMatch(raw.toString(),/\/Users\/|site-packages\//);
  const canonical=value=>value===null||typeof value!=="object"?JSON.stringify(value):Array.isArray(value)?
    "["+value.map(canonical).join(",")+"]":"{"+Object.keys(value).sort().map(key=>JSON.stringify(key)+":"+canonical(value[key])).join(",")+"}";
  for(const row of accepted){
    const proof=bundle.functions.find(item=>item.function===row.function);
    assert.equal(createHash("sha256").update(canonical(proof.evidence)).digest("hex"),row.evidence_hash);
    assert.equal(proof.evidence.full_project_strict_suite_passed,false);
    const references=proof.evidence.reference_definitions;
    assert.equal(references.main.canonical_id,references.alternate.canonical_id);
    assert.equal(references.main.canonical_id,row.canonical_target);
    assert.equal(proof.evidence.executions.length,5);
    for(const execution of proof.evidence.executions){
      assert.equal(execution.failed,0);assert.equal(execution.skipped,0);
      assert.equal(execution.process_terminal_validation.exit,0);
      assert.equal(execution.environment_validation.verified,true);
      assert.equal(execution.source_fingerprint,batch.source_fingerprint);
    }
    const ours=reviews.find(item=>item.id===row.native_entry&&item.project_fingerprint===batch.source_fingerprint);
    const target=reviews.find(item=>item.id===row.canonical_target&&item.project_fingerprint===batch.source_fingerprint);
    for(const review of [ours,target]){
      assert.ok(review);assert.equal(review.evidence_hash,row.evidence_hash);
      assert.equal(fullContractReview({status:"implemented",source_hash:review.source_hash,review},batch.source_fingerprint),true);
      assert.equal(Object.keys(review.contract_axes).length,14);
      for(const axis of Object.values(review.contract_axes))assert.ok(["VERIFIED","APPLICABILITY_REVIEWED"].includes(axis.state));
    }
  }
});
