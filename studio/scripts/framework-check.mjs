// Copyright 2026 QuantumBridge Contributors. Apache-2.0.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { domains, directions, foundation, validateTaxonomy } from "../src/framework/data.js";
import { resources, directionResources, domainResources } from "../src/framework/resources.js";

assert.equal(validateTaxonomy(),true);
assert.deepEqual(domains.map(domain=>directions.filter(item=>item.domain===domain.id).length),[4,5,5,5]);
assert.equal(foundation.length,5);
assert.equal(new Set(directions.map(item=>item.id)).size,19);
for(const item of directions){
  assert.ok(item.modules.length>=3);
  assert.equal(new URL(item.source).protocol,"https:");
  for(const locale of ["zh-CN","en"]){
    assert.ok(item.name[locale]&&item.summary[locale]&&item.boundary[locale]&&item.reference[locale]);
    assert.equal(item.features[locale].length,3);
  }
}
const html=await readFile(new URL("../framework.html",import.meta.url),"utf8");
assert.ok(html.includes("src/framework/main.js")&&html.includes("src/framework/framework.css"));
const app=await readFile(new URL("../src/framework/main.js",import.meta.url),"utf8");
assert.ok(!app.includes("data-export")&&!app.includes("Export framework"));
assert.ok(app.includes("UI coverage does not establish native functionality"));
assert.ok(app.includes("showModal()")&&app.includes('role="tablist"'));
assert.ok(app.includes("domainResources(domain.id)")&&app.includes("directionResources(item.id)"));
for(const resource of resources){
  assert.ok(domains.some(domain=>domain.id===resource.domain));
  assert.ok(resource.kind==="case"?directionResources(resource.direction).includes(resource):domainResources(resource.domain).includes(resource));
}
console.log("Application framework checks passed: 4 domains, 19 bilingual directions, 5 foundation layers.");
