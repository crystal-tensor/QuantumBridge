import {
  sampleBenchmarkReport,
  sampleCatalog,
  sampleExports,
  sampleResults,
  sampleWorkflowDetails,
  sampleWorkflows,
  studioSchemaVersion,
} from "../data/seedData.js";

export function createLocalJsonClient() {
  return {
    async loadAll() {
      return {
        catalog: sampleCatalog,
        workflows: sampleWorkflows,
        workflowDetails: sampleWorkflowDetails,
        results: sampleResults,
        benchmark: sampleBenchmarkReport,
        exports: sampleExports,
        schema: studioSchemaVersion,
      };
    },
    async listCatalogProjects() {
      return response(sampleCatalog.projects || []);
    },
    async listWorkflows() {
      return response(sampleWorkflows.workflows || []);
    },
    async getWorkflowDetail(workflowId) {
      return response(findWorkflowDetail(workflowId));
    },
    async getInputSchema(workflowId) {
      return response(findWorkflowDetail(workflowId).input_schema || {});
    },
    async getSampleResult(workflowId) {
      return response(findSampleResult(workflowId));
    },
    async getBenchmarkReport() {
      return response(sampleBenchmarkReport.benchmark || {});
    },
    async exportResult(format = "json") {
      const normalized = format === "notebook" ? "notebook_stub" : format;
      return response((sampleExports.exports || {})[normalized] || null);
    },
  };
}

function findWorkflowDetail(workflowId) {
  const detail = (sampleWorkflowDetails.details || []).find((item) => item.workflow_id === workflowId);
  if (!detail) {
    throw structuredError("workflow_not_found", `Unknown workflow: ${workflowId}`);
  }
  return detail;
}

function findSampleResult(workflowId) {
  return (
    (sampleResults.results || []).find((item) => item.workflow_id === workflowId) ||
    (sampleResults.results || [])[0] ||
    null
  );
}

export function response(data, warnings = [], provenance = {}) {
  return {
    success: true,
    data,
    error: null,
    warnings,
    provenance: {
      source: "quantumbridge.studio.frontend.localJsonClient",
      cloud_access: false,
      token_access: false,
      hardware_access: false,
      production_ready: false,
      ...provenance,
    },
    schema_version: studioSchemaVersion.frontend_schema_version || studioSchemaVersion.schema_version,
  };
}

export function structuredError(code, message, details = {}) {
  const error = new Error(message);
  error.studioError = { code, message, details };
  return error;
}
