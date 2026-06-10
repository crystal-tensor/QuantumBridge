import fs from "node:fs";
import path from "node:path";

const root = process.cwd().endsWith(`${path.sep}studio`) ? process.cwd() : path.join(process.cwd(), "studio");
const requiredFiles = [
  "index.html",
  "src/App.js",
  "src/api/studioClient.js",
  "src/api/mockStudioClient.js",
  "src/api/localJsonClient.js",
  "src/pages/CatalogPage.js",
  "src/pages/WorkflowsPage.js",
  "src/pages/WorkflowDetailPage.js",
  "src/pages/ExecutePage.js",
  "src/pages/BenchmarksPage.js",
  "src/pages/ResultsPage.js",
  "src/pages/ExportsPage.js",
  "src/data/sampleCatalog.json",
  "src/data/sampleWorkflows.json",
  "src/data/sampleResults.json",
  "src/data/sampleBenchmarkReport.json",
  "src/data/seedData.js",
  "src/styles/globals.css",
];

for (const file of requiredFiles) {
  assert(fs.existsSync(path.join(root, file)), `missing required file: ${file}`);
}

const catalog = readJson("src/data/sampleCatalog.json");
const workflows = readJson("src/data/sampleWorkflows.json");
const results = readJson("src/data/sampleResults.json");
const benchmark = readJson("src/data/sampleBenchmarkReport.json");

assert(Array.isArray(catalog.projects) && catalog.projects.length >= 8, "catalog project data is missing");
assert(Array.isArray(workflows.workflows) && workflows.workflows.length >= 36, "workflow registry data is incomplete");
assert(Array.isArray(workflows.details) && workflows.details.length === workflows.workflows.length, "workflow details are incomplete");
assert(Array.isArray(results.results) && results.results.length >= 1, "sample results are missing");
assert(results.exports?.json && results.exports?.markdown && results.exports?.python, "export samples are incomplete");
assert(benchmark.benchmark?.suite_id, "benchmark report is missing");

const sourceText = requiredFiles
  .filter((file) => /\.(js|css|html|json)$/.test(file))
  .map((file) => fs.readFileSync(path.join(root, file), "utf8"))
  .join("\n");

assert(!/carbon-components|@carbon|ibm-logo|qiskit-logo|pennylane-logo/i.test(sourceText), "forbidden branding or design-system string found");
assert(!/api[_-]?key|password|bearer\s+[a-z0-9._-]+|secret[_-]?value/i.test(sourceText), "secret-like string found");
assert(!/https?:\/\//i.test(sourceText), "external network endpoint found");

for (const forbidden of ["node_modules", "dist", "build", "coverage", ".vite"]) {
  assert(!fs.existsSync(path.join(root, forbidden)), `forbidden generated directory exists: ${forbidden}`);
}

console.log("QuantumBridge Studio frontend smoke-check passed");

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}
