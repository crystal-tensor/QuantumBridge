// Copyright 2026 QuantumBridge Contributors. Apache-2.0.
import { cp, mkdir, readFile, writeFile, readdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { resources, resourceHref } from "../src/framework/resources.js";
import { readArtifact, artifactPage } from "./artifact-pages.mjs";

export async function buildPublic(destination, basePath = "/QuantumBridge/") {
  if (!/^\/(?:[A-Za-z0-9_-]+\/)*$/.test(basePath)) throw new Error("Invalid public base path");
  const root = fileURLToPath(new URL("../", import.meta.url));
  const output = path.resolve(destination);
  // Never recursively copy the workspace, private proposals, or temporary receipts.
  await mkdir(output, { recursive: true });
  if ((await readdir(output)).length) throw new Error("Public output directory must be empty");
  for (const name of ["src", "assets", "framework.html", "ecosystem.html", "index.html"]) {
    await cp(path.join(root, name), path.join(output, name), { recursive: true });
  }
  await writeFile(path.join(output, "src/framework/deployment.js"), "export const publicSite = true;\nexport const privateDocuments = false;\n");
  const framework = await readFile(path.join(root, "framework.html"), "utf8");
  await writeFile(path.join(output, "progress.html"), await readFile(path.join(root, "index.html")));
  await writeFile(path.join(output, "index.html"), framework);
  const main = path.join(output, "src/framework/main.js");
  await writeFile(main, (await readFile(main, "utf8")).replace('href="./index.html"', 'href="./progress.html"'));
  for (const resource of resources) {
    const artifact = await readArtifact(resourceHref(resource));
    const directory = path.join(output, "examples", resource.domain);
    await mkdir(directory, { recursive: true });
    await writeFile(path.join(directory, resource.file), artifactPage(artifact.body.toString("utf8"), resource, "zh-CN", basePath));
    if (resource.kind !== "index") {
      const notebook = await readArtifact(resourceHref(resource, true));
      await writeFile(path.join(directory, path.basename(notebook.filename)), notebook.body);
    }
  }
  await writeFile(path.join(output, ".nojekyll"), "");
  return { output, basePath, pages: resources.length, notebooks: resources.filter(item => item.kind !== "index").length };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (!process.argv[2]) throw new Error("Usage: node scripts/build-public.mjs EMPTY_DIRECTORY [BASE_PATH]");
  console.log(JSON.stringify(await buildPublic(process.argv[2], process.argv[3]), null, 2));
}
