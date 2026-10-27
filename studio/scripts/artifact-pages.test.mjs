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
