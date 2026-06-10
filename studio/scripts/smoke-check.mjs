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
  "src/data/sampleWorkflowDetails.json",
  "src/data/sampleResults.json",
  "src/data/sampleBenchmarkReport.json",
  "src/data/sampleExports.json",
  "src/data/studioSchemaVersion.json",
  "src/data/seedData.js",
  "src/styles/globals.css",
];

for (const file of requiredFiles) {
  assert(fs.existsSync(path.join(root, file)), `missing required file: ${file}`);
}

const catalog = readJson("src/data/sampleCatalog.json");
const workflows = readJson("src/data/sampleWorkflows.json");
const workflowDetails = readJson("src/data/sampleWorkflowDetails.json");
const results = readJson("src/data/sampleResults.json");
const benchmark = readJson("src/data/sampleBenchmarkReport.json");
const exportsPayload = readJson("src/data/sampleExports.json");
const schema = readJson("src/data/studioSchemaVersion.json");

assert(schema.schema_version && schema.frontend_schema_version, "schema_version exists");
assert(Array.isArray(catalog.projects) && catalog.projects.length >= 8, "catalog project data is missing");
assert(Array.isArray(workflows.workflows) && workflows.workflows.length >= 36, "workflow registry data is incomplete");
assert(Array.isArray(workflows.details) && workflows.details.length === workflows.workflows.length, "workflow details are incomplete");
assert(Array.isArray(workflowDetails.details) && workflowDetails.details.length === workflows.workflows.length, "workflow detail file is incomplete");
assert(new Set(workflowDetails.details.map((item) => item.workflow_id)).size === workflows.workflows.length, "workflow detail count equals workflow count");
assert(Array.isArray(results.results) && results.results.length >= 10, "sample results are missing");
assert(benchmark.benchmark?.suite_id, "benchmark report is missing");
assert(exportsPayload.exports?.json && exportsPayload.exports?.markdown && exportsPayload.exports?.python && exportsPayload.exports?.notebook_stub, "export samples are incomplete");

const sourceText = requiredFiles
  .filter((file) => /\.(js|css|html|json)$/.test(file))
  .map((file) => fs.readFileSync(path.join(root, file), "utf8"))
  .join("\n");

assert(!/carbon-components|@carbon|ibm-logo|qiskit-logo|pennylane-logo/i.test(sourceText), "forbidden branding or design-system string found");
assert(!/api[_-]?key|password|bearer\s+[a-z0-9._-]+|secret[_-]?value/i.test(sourceText), "secret-like string found");
assert(!/https?:\/\//i.test(sourceText), "external network endpoint found");
assert(fileText("src/pages/ExecutePage.js").includes("warnings") && fileText("src/pages/ExecutePage.js").includes("provenance"), "ExecutePage references warnings / provenance");
assert(fileText("src/pages/WorkflowsPage.js").includes("local_only") && fileText("src/pages/WorkflowsPage.js").includes("cloud_access") && fileText("src/pages/WorkflowsPage.js").includes("token_access") && fileText("src/pages/WorkflowsPage.js").includes("hardware_access"), "WorkflowsPage references locality/cloud/token/hardware boundaries");
assert(fileText("src/pages/CatalogPage.js").toLowerCase().includes("clean-room notice"), "CatalogPage references clean-room notice");

for (const forbidden of ["node_modules", "dist", "build", "coverage", ".vite"]) {
  assert(!fs.existsSync(path.join(root, forbidden)), `forbidden generated directory exists: ${forbidden}`);
}

console.log("QuantumBridge Studio frontend smoke-check passed");

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
}

function fileText(file) {
  return fs.readFileSync(path.join(root, file), "utf8");
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}
