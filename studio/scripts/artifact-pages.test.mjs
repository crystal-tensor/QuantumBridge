// Copyright 2026 QuantumBridge Contributors. Apache-2.0.
import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import { readFile, readdir } from "node:fs/promises";
import { once } from "node:events";
import { existsSync } from "node:fs";
import { domains, directions } from "../src/framework/data.js";
import { resources, privateDocumentResources, resourceHref, domainResources, directionResources } from "../src/framework/resources.js";
import { createPreviewServer } from "./serve.mjs";
import { artifactPage, readArtifact } from "./artifact-pages.mjs";

let server, base;
before(async () => {
  server = createPreviewServer();
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  base = `http://127.0.0.1:${server.address().port}`;
});
after(async () => {
  server.closeAllConnections();
  await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
});

test("project Word documents are reachable from every domain with valid downloads", {
  skip: !existsSync(new URL("../reports/qb-project/index.html", import.meta.url)) && "Owner-only proposals are not included in the public checkout",
}, async () => {
  assert.equal(privateDocumentResources.length, domains.length);
  const config = await (await fetch(base + "/src/framework/deployment.js")).text();
  assert.match(config, /privateDocuments = true/);
  for (const domain of domains) {
    const entry=privateDocumentResources.find(item=>item.domain===domain.id);
    const response=await fetch(base+resourceHref(entry));
    assert.equal(response.status,200);
    const html=await response.text();
    assert.match(html,/id="home"/);
    assert.match(html,/【客户名称】/);
    assert.match(html,/V1\.1/);
    assert.match(html,/V1\.2/);
    assert.match(html,/full replacement/);
    for (const file of ['QB项目立项申请书_公司审批版.docx','QB项目立项申请书_客户通用版.docx','QB项目立项申请书_公司审批版_V1.1图文版.docx','QB项目立项申请书_客户通用版_V1.1图文版.docx','QB项目立项申请书_公司审批版_V1.2成本测算增强版.docx']) {
      assert.ok(html.includes(`href="${file}"`));
      const download=await fetch(base+'/reports/qb-project/'+encodeURIComponent(file));
      assert.equal(download.status,200);
      assert.match(download.headers.get('content-type'),/wordprocessingml\.document/);
      const body=Buffer.from(await download.arrayBuffer());
      assert.equal(body.subarray(0,2).toString(),'PK');
      assert.deepEqual(body,await readFile(new URL('../reports/qb-project/'+file,import.meta.url)));
    }
  }
});

test("all published notebook HTML pages are registered in their home domain", async () => {
  assert.equal(new Set(resources.map(item => resourceHref(item))).size, resources.length);
  for (const domain of domains) {
    const folder = new URL(`../../output/jupyter-notebook/${domain.id}/`, import.meta.url);
    let files;
    try { files = await readdir(folder); } catch (error) { if (error.code === "ENOENT") continue; throw error; }
    const registered = resources.filter(item => item.domain === domain.id);
    assert.deepEqual(files.filter(file => file.endsWith(".html")).sort(), registered.map(item => item.file).sort());
    for (const item of registered) {
      for (const locale of ["zh-CN", "en"]) assert.ok(item.title[locale]);
      assert.match(item.file, /^[\w-]+\.html$/);
      if (item.direction) assert.equal(directions.find(direction => direction.id === item.direction)?.domain, item.domain);
      if (item.kind === "case") assert.ok(directionResources(item.direction).includes(item));
      else assert.ok(domainResources(domain.id).includes(item));
    }
  }
});

test("every registered page is served with working home links and unchanged notebook downloads", async () => {
  for (const item of resources) {
    const artifact = await readArtifact(resourceHref(item));
    const response = await fetch(base + resourceHref(item));
    assert.equal(response.status, 200, item.file);
    assert.match(response.headers.get("content-type"), /^text\/html/);
    const body = await response.text();
    assert.match(body, /id="qb-artifact-nav"/);
    assert.match(body, /返回首页/);
    const home = await fetch(`${base}/framework.html?category=${item.domain}`);
    assert.equal(home.status, 200);
    assert.match(await home.text(), /framework-app/);
    assert.deepEqual(artifact.body, await readFile(artifact.filename));
    if (item.kind !== "index") {
      const download = await fetch(base + resourceHref(item, true));
      assert.equal(download.status, 200);
      assert.match(download.headers.get("content-disposition"), /^attachment;/);
      const expected = await readArtifact(resourceHref(item, true));
      assert.deepEqual(Buffer.from(await download.arrayBuffer()), expected.body);
      assert.ok(Array.isArray(JSON.parse(expected.body).cells));
    }
    const head = await fetch(base + resourceHref(item), {method:"HEAD"});
    assert.equal(head.status, 200);
    assert.equal(await head.text(), "");
    assert.equal(Number(head.headers.get("content-length")), Buffer.byteLength(body));
  }
});

test("index includes D1, D2, D3 without rewriting scientific artifacts", async () => {
  const index = resources.find(item => item.kind === "index");
  const response = await fetch(base + resourceHref(index));
  const html = await response.text();
  for (const item of resources.filter(item => item.kind === "diagnostic")) assert.ok(html.includes(`href="${resourceHref(item)}"`));
  assert.ok(html.includes("精度尚未通过验收"));
  const sample = resources.find(item => item.direction === "risk");
  const english = artifactPage("<html><body>Evidence</body></html>", sample, "en");
  assert.match(english, /Back to home/);
  assert.match(english, /category=finance&lang=en#risk/);
  assert.match(english, /<body><style>/);
});

test("optional notebook CDN scripts do not block the case body", async () => {
  let checked = 0;
  for (const resource of resources) {
    const artifact = await readArtifact(resourceHref(resource));
    const html = artifactPage(artifact.body.toString("utf8"), resource);
    for (const [tag] of html.matchAll(/<script\b[^>]*\bsrc="https:\/\/cdnjs\.cloudflare\.com\/[^>]+>/g)) {
      assert.match(tag, /\b(?:defer|async)\b|\btype="module"/, resource.file);
      checked++;
    }
  }
  assert.ok(checked >= 2*resources.filter(item => item.kind !== "index").length);
});

test("only registered artifacts are exposed, with malformed paths and write requests rejected", async () => {
  for (const pathname of ["/examples/finance/allocation_hardware_evidence.json", "/examples/finance/not-registered.html", "/examples/finance/index.ipynb", "/examples/science/secret.html", "/examples/finance/%2e%2e%2f%2e%2e%2fREADME.md"]) {
    assert.equal((await fetch(base + pathname)).status, 404, pathname);
  }
  assert.equal((await fetch(base + "/examples/finance/%")).status, 400);
  const denied = await fetch(base + "/examples/finance/index.html", {method:"POST"});
  assert.equal(denied.status, 405);
  assert.equal(denied.headers.get("allow"), "GET, HEAD");
  for (const pathname of ["/framework.html", "/src/framework/resources.js", "/src/framework/main.js", "/src/framework/framework.css"]) assert.equal((await fetch(base + pathname)).status, 200, pathname);
});

test("real-stock CQM and QMC entries retain executed counts, provenance and hardware boundaries", async () => {
  const mapping = {
    portfolio: "dwave_portfolio.html", "financial-constraints": "dwave_constraints.html",
    pricing: "qmc_pricing.html", risk: "qmc_risk.html", "market-models": "qmc_hybrid.html",
  };
  for (const [direction, file] of Object.entries(mapping)) {
    const resource = directionResources(direction).find(item => item.file === file);
    assert.ok(resource, direction);
    const response = await fetch(base + resourceHref(resource));
    assert.equal(response.status, 200);
    const html = await response.text();
    assert.match(html, /2015/);
    assert.match(html, /NO_NEW_SUBMISSION_RECOMMENDED/);
    assert.match(html, /不是网页实时求解/);
    assert.match(html, /data:image\/png;base64,/);
    const notebook = JSON.parse((await readArtifact(resourceHref(resource, true))).body);
    assert.equal(notebook.metadata.quantumbridge.direction, direction);
    assert.equal(notebook.metadata.quantumbridge.hardware_jobs, 0);
    const cells = notebook.cells.filter(cell => cell.cell_type === "code");
    assert.ok(cells.every(cell => cell.execution_count > 0));
    assert.ok(cells.every(cell => cell.outputs.every(output => output.output_type !== "error")));
    const audit = cells.flatMap(cell => cell.outputs).filter(output => output.output_type === "stream")
      .flatMap(output => (Array.isArray(output.text) ? output.text.join("") : output.text).split("\n"))
      .find(line => line.startsWith("EVIDENCE_JSON="));
    assert.ok(audit);
    const evidence = JSON.parse(audit.slice("EVIDENCE_JSON=".length));
    assert.equal(evidence.hardware_jobs, 0);
    const source = file.startsWith("dwave") ? evidence.result.source : evidence.pricing.source;
    assert.equal(source.sha256, "60bf505fec160ce05ba959382adee32ea6e53ce14fe22886db27c58fe1b0d26b");
    if (file.startsWith("dwave")) {
      assert.equal(Object.values(evidence.result.qaoa.counts).reduce((a,b)=>a+b,0), 1024);
      assert.equal(evidence.result.candidates.length, 16);
    } else {
      assert.equal(evidence.pricing.call.counts.length, 4);
      assert.ok(evidence.pricing.call.counts.every(row=>Object.values(row).reduce((a,b)=>a+b,0)===1024));
      assert.equal(evidence.pennylane_reference.qubits, 9);
      assert.equal(evidence.pennylane_risk_reference.qubits, 9);
      assert.equal(evidence.pennylane_risk_reference.probabilities.length, 32);
      assert.ok(Math.abs(evidence.pennylane_risk_reference.cvar_discrete_reference
        - evidence.risk.raw_reference.CVaR_expected_shortfall) < 1e-10);
      assert.ok(evidence.hybrid.circuit_gradient_norms.some(value=>value>0));
    }
  }
});

test("all three local-only domains have their own bilingual return navigation", async () => {
  for (const domain of ["science", "industry", "security"]) {
    const index = resources.find(item => item.domain === domain && item.kind === "index");
    const item = resources.find(item => item.domain === domain && item.kind === "case");
    const page = artifactPage("<html><body><main>Local evidence</main></body></html>", item, "en");
    assert.ok(page.includes(index.title.en));
    assert.ok(page.includes(`${resourceHref(index)}?lang=en`));
    assert.ok(page.includes(`category=${domain}&lang=en#${item.direction}`));
    assert.ok(!page.includes("Finance cases"));
    const directory = artifactPage("<html><body><main>Local cases</main></body></html>", index);
    assert.ok(!directory.includes('id="qb-report-directory"'));
  }
});

test("Cirq finance cases stay in the five matching finance directions with executed notebooks", async () => {
  const mapping = {
    portfolio: "cirq_portfolio.html", risk: "cirq_risk.html", pricing: "cirq_pricing.html",
    "financial-constraints": "cirq_constraints.html", "market-models": "cirq_market_walk.html",
  };
  const hub = domainResources("finance").find(item => item.file === "cirq_finance.html");
  assert.ok(hub);
  const html = await (await fetch(base + resourceHref(hub))).text();
  assert.match(html, /不是 Google 官方金融产品/);
  assert.match(html, /0.*云端 \/ 真机任务/);
  const receipt = JSON.parse(await readFile(new URL("../../output/jupyter-notebook/finance/cirq_finance_evidence.json", import.meta.url), "utf8"));
  assert.equal(receipt.hardware_jobs, 0);
  assert.deepEqual(Object.keys(receipt.cases).sort(), Object.keys(mapping).sort());
  for (const [direction, file] of Object.entries(mapping)) {
    const matches = directionResources(direction).filter(item => item.file === file);
    assert.equal(matches.length, 1);
    const item = matches[0];
    assert.equal(item.domain, "finance");
    assert.equal(item.kind, "case");
    assert.ok(html.includes(`href="${file}"`));
    const artifact = await readArtifact(resourceHref(item, true));
    const notebook = JSON.parse(artifact.body);
    assert.equal(notebook.metadata.quantumbridge.domain, "finance");
    assert.equal(notebook.metadata.quantumbridge.direction, direction);
    assert.equal(notebook.metadata.quantumbridge.hardware_jobs, 0);
    const code = notebook.cells.filter(cell => cell.cell_type === "code");
    assert.ok(code.length >= 4 && code.every(cell => cell.execution_count > 0));
    assert.ok(code.every(cell => cell.outputs.every(output => output.output_type !== "error")));
    assert.ok(code.some(cell => cell.outputs.some(output => output.data?.["image/png"])));
    const streams = code.flatMap(cell => cell.outputs).filter(output => output.output_type === "stream")
      .map(output => Array.isArray(output.text) ? output.text.join("") : output.text).join("\n");
    const evidence = JSON.parse(streams.split("\n").find(line => line.startsWith("EVIDENCE_JSON=")).slice(14));
    assert.deepEqual(evidence, receipt.cases[direction]);
    assert.equal(evidence.backend, "local cirq.Simulator");
    assert.equal(evidence.hardware_jobs, 0);
    assert.equal(evidence.shots, 4096);
    assert.equal(evidence.counts.reduce((a, b) => a + b, 0), 4096);
    assert.ok(evidence.qubits >= 2 && evidence.qubits <= 5);
    const english = await (await fetch(base + resourceHref(item) + "?lang=en")).text();
    assert.ok(english.includes(`category=finance&lang=en#${direction}`));
  }
  assert.ok((await (await fetch(base + "/examples/finance/index.html")).text()).includes('href="cirq_finance.html"'));
});
