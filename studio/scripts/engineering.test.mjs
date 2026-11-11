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
});
test("hardware receipts keep domain acceptance separate and redact sensitive payloads", () => {
  assert.ok(manifest.hardware.length >= 5);
  assert.ok(manifest.hardware.every(x => x.task_id && x.artifact_hash && x.acceptance === "INCONCLUSIVE"));
  for(const r of manifest.hardware){assert.equal(r.shots,r.count_sum);assert.equal(r.domain,"finance");assert.ok(!("openqasm" in r));}
});
test("goal and selected verification never masquerade as final acceptance", () => {
  assert.equal(manifest.core_execution,"active");
  assert.equal(manifest.goal_execution.scope_reduced,false);
  assert.equal(manifest.acceptance_scope.final_gates.length,9);
  assert.ok(manifest.acceptance_scope.final_gates.every(g=>g.state!=="COMPLETE"));
  assert.ok(manifest.strict_backlog.length>=47);
  for(const run of manifest.verification){
    assert.equal(run.source_match,run.source_fingerprint===manifest.source.fingerprint);
    assert.equal(run.total,run.passed+run.failed+run.skipped);
    assert.equal(run.cases.length,run.total);
    assert.equal(run.protected_tests_unchanged,true);
    assert.equal(run.scope,"selected_strict_batch_not_full_contract_or_full_suite");
  }
  const text=JSON.stringify(manifest);
  assert.ok(!text.includes("/Users/")&&!text.includes("site-packages/"));
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
