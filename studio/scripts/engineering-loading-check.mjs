import assert from "node:assert/strict";
import { readFile, mkdir } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { gunzipSync } from "node:zlib";
import { createPreviewServer } from "./serve.mjs";

const { chromium } = await import(process.env.PLAYWRIGHT_MODULE ? pathToFileURL(process.env.PLAYWRIGHT_MODULE).href : "playwright");
const server = createPreviewServer();
await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
const base = `http://127.0.0.1:${server.address().port}`;
const output = process.env.QB_QA_OUTPUT || "/tmp/qb-engineering-loading-qa";
await mkdir(output, { recursive: true });
const evidence = await readFile(new URL("../src/progress/data/manifest-evidence.json.gz", import.meta.url));
const bootstrap = JSON.parse(gunzipSync(await readFile(new URL("../src/progress/data/manifest-browser.json.gz", import.meta.url))));
let browser;
const results = [];
try {
  browser = await chromium.launch({ headless: true, ...(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}) });
  for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }]) {
    const page = await browser.newPage({ viewport });
    const errors = [], requests = [];
    page.on("pageerror", error => errors.push(error.message));
    page.on("request", request => requests.push(new URL(request.url()).pathname));
    let mode = "blocked", bodies = 0, signalStarted, release;
    const started = new Promise(resolve => { signalStarted = resolve; });
    const blocked = new Promise(resolve => { release = resolve; });
    await page.route("**/manifest-evidence.json.gz?*", async route => {
      if (route.request().method() === "HEAD") {
        await route.fulfill({ status: 200, headers: { "content-length": String(evidence.length) } }); return;
      }
      bodies++;
      if (mode === "blocked") { signalStarted(); await blocked; }
      const bytes = Buffer.from(evidence);
      if (mode === "corrupt") bytes[0] ^= 1;
      await route.fulfill({ status: 200, contentType: "application/gzip", body: bytes });
    });
    await page.goto(`${base}/framework.html?category=finance&lang=zh`);
    await page.getByRole("region", { name: "金融", exact: true }).getByRole("link", { name: "工程进展", exact: true }).click();
    await page.getByRole("heading", { name: "工程进展", exact: true }).waitFor();
    assert.equal(bodies, 0);
    assert.equal(requests.some(name => name.endsWith("/manifest.json.gz")), false);
    await page.getByRole("button", { name: "总览", exact: true }).click();
    assert.ok((await page.locator(".blockers").innerText()).includes(`${bootstrap.strict_backlog_count} 项`));
    await page.getByRole("button", { name: "测试与真机", exact: true }).click();
    await started;
    await page.getByRole("status").filter({ hasText: "正在读取完整证据" }).waitFor();
    assert.equal(await page.locator("#engineering-app").getAttribute("aria-busy"), "true");
    await page.getByRole("button", { name: "测试与真机", exact: true }).click();
    await page.getByRole("button", { name: "4 类 / 19 方向", exact: true }).click();
    await page.locator(".direction-rows article").first().waitFor();
    assert.equal(await page.locator("#domain").inputValue(), "finance");
    assert.equal(await page.locator(".direction-rows article").count(), 5);
    assert.equal(await page.locator("#engineering-app").getAttribute("aria-busy"), "false");
    mode = "valid"; release();
    await page.getByRole("button", { name: "测试与真机", exact: true }).click();
    await page.locator("#current-validation").getByRole("heading", { name: "本地融合验证与远端 CI 分开验收", exact: true }).waitFor();
    assert.equal(bodies, 1);
    assert.ok((await page.locator("#current-validation").innerText()).includes("25 项已知严格失败"));
    await page.getByRole("link", { name: "项目首页", exact: true }).click();
    await page.getByRole("heading", { name: "QuantumBridge 应用框架", exact: true }).waitFor();

    mode = "corrupt";
    await page.getByRole("region", { name: "金融", exact: true }).getByRole("link", { name: "工程进展", exact: true }).click();
    await page.getByRole("heading", { name: "工程进展", exact: true }).waitFor();
    await page.getByRole("button", { name: "测试与真机", exact: true }).click();
    await page.getByRole("alert").waitFor();
    assert.ok((await page.getByRole("alert").innerText()).includes("integrity mismatch"));
    assert.equal(await page.locator("#current-validation").count(), 0);
    assert.equal(await page.locator("#engineering-app").getAttribute("aria-busy"), "false");
    await page.screenshot({ path: `${output}/rejected-evidence-${viewport.width}.png`, fullPage: false });
    mode = "valid";
    await page.getByRole("button", { name: "重试加载", exact: true }).click();
    await page.locator("#current-validation").getByRole("heading", { name: "本地融合验证与远端 CI 分开验收", exact: true }).waitFor();
    assert.equal(bodies, 3);
    assert.ok((await page.locator("#current-validation").innerText()).includes("25 项已知严格失败"));
    assert.equal(await page.locator("[data-verification-run]").count(), 20);
    await page.getByRole("button", { name: "总览", exact: true }).click();
    assert.ok((await page.locator(".blockers").innerText()).includes(`${bootstrap.strict_backlog_count} 项`));
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await page.getByRole("link", { name: "项目首页", exact: true }).click();
    await page.getByRole("heading", { name: "QuantumBridge 应用框架", exact: true }).waitFor();
    assert.deepEqual(errors, []);
    results.push({ viewport, lazyInitialEvidence: true, sharedInFlightLoad: true, switchedViewPreserved: true, corruptEvidenceRejected: true, retryPreservesFailures: true, homePageHome: true, errors });
    await page.close();
  }
  console.log(JSON.stringify({ results, screenshots: output }, null, 2));
} finally { await browser?.close(); await new Promise(resolve => server.close(resolve)); }
