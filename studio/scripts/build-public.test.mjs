import assert from "node:assert/strict";
import { test } from "node:test";
import { mkdtemp, readFile, readdir, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { buildPublic } from "./build-public.mjs";
import { resources } from "../src/framework/resources.js";

test("public export keeps every case and notebook, project paths, and private-document boundary", async () => {
  const directory = await mkdtemp(path.join(tmpdir(), "qb-pages-"));
  try {
    const result = await buildPublic(directory, "/QuantumBridge/");
    assert.equal(result.pages, 26);
    assert.equal(result.notebooks, 22);
    assert.ok((await readFile(path.join(directory, "framework.html"), "utf8")).includes("framework-app"));
    assert.match(await readFile(path.join(directory, "src/framework/deployment.js"), "utf8"), /publicSite = true/);
    assert.ok(!(await readdir(directory)).includes("reports"));
    for (const resource of resources) {
      const filename = path.join(directory, "examples", resource.domain, resource.file);
      const html = await readFile(filename, "utf8");
      assert.ok(html.includes(`href="/QuantumBridge/framework.html?category=${resource.domain}`));
      assert.ok(!html.includes('href="/examples/'));
      if (resource.kind !== "index") {
        const notebook = resource.file.replace(/\.html$/, ".ipynb");
        assert.ok(html.includes(`/QuantumBridge/examples/${resource.domain}/${notebook}`));
        assert.deepEqual(await readFile(path.join(directory, "examples", resource.domain, notebook)),
          await readFile(new URL(`../../output/jupyter-notebook/${resource.domain}/${notebook}`, import.meta.url)));
      }
    }
    await assert.rejects(buildPublic(directory), /must be empty/);
    await assert.rejects(buildPublic(directory, "/../"), /base path/);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
