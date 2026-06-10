export function createMockStudioClient(localJsonClient) {
  let cache = null;

  return {
    async loadAll() {
      cache = await localJsonClient.loadAll();
      return cache;
    },
    async listCatalogProjects() {
      return localJsonClient.listCatalogProjects();
    },
    async listWorkflows() {
      return localJsonClient.listWorkflows();
    },
    async getWorkflowDetail(workflowId) {
      return localJsonClient.getWorkflowDetail(workflowId);
    },
    async getInputSchema(workflowId) {
      return localJsonClient.getInputSchema(workflowId);
    },
    async getSampleResult(workflowId) {
      return localJsonClient.getSampleResult(workflowId);
    },
    async runMockWorkflow(workflowId, inputs = {}) {
      return {
        success: true,
        data: this.mockExecute(workflowId, inputs),
        error: null,
        warnings: ["Mock frontend workflow result returned from local seed data."],
        provenance: {
          source: "quantumbridge.studio.frontend.mockStudioClient",
          cloud_access: false,
          token_access: false,
          hardware_access: false,
          production_ready: false,
        },
        schema_version: cache?.schema?.schema_version,
      };
    },
    async getBenchmarkReport() {
      return localJsonClient.getBenchmarkReport();
    },
    async exportResult(format = "json") {
      return localJsonClient.exportResult(format);
    },
    mockExecute(workflowId, inputs = {}) {
      const sample = cache?.results?.results?.find((item) => item.workflow_id === workflowId) || cache?.results?.results?.[0] || {};
      const workflow = cache?.workflowDetails?.details?.find((item) => item.workflow_id === workflowId);
      return {
        ...sample,
        execution_id: `studio-ui-mock-${Date.now()}`,
        workflow_id: workflowId,
        status: "succeeded",
        ui_inputs: inputs,
        result: sample.result || { status: "sample" },
        warnings: [
          ...(workflow?.warnings || []),
          "Frontend prototype uses local JSON sample data; real execution remains in the Stage 10C Python backend API.",
        ],
        provenance: {
          ...(workflow?.provenance || {}),
          frontend_client: "mockStudioClient",
          cloud_access: false,
          token_access: false,
          hardware_access: false,
          production_ready: false,
        },
      };
    },
  };
}
