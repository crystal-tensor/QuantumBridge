import { createLocalJsonClient } from "./localJsonClient.js";
import { createMockStudioClient } from "./mockStudioClient.js";

export function createStudioClient() {
  const local = createLocalJsonClient();
  const mock = createMockStudioClient(local);
  return {
    loadAll: () => mock.loadAll(),
    listCatalogProjects: () => mock.listCatalogProjects(),
    listWorkflows: () => mock.listWorkflows(),
    getWorkflowDetail: (workflowId) => mock.getWorkflowDetail(workflowId),
    getInputSchema: (workflowId) => mock.getInputSchema(workflowId),
    getSampleResult: (workflowId) => mock.getSampleResult(workflowId),
    runMockWorkflow: (workflowId, inputs) => mock.runMockWorkflow(workflowId, inputs),
    getBenchmarkReport: () => mock.getBenchmarkReport(),
    exportResult: (format) => mock.exportResult(format),
    mockExecute: (workflowId, inputs) => mock.mockExecute(workflowId, inputs),
  };
}

export function futureApiClient() {
  return {
    mode: "planned-local-api",
    productionServer: false,
    cloudAccess: false,
    tokenAccess: false,
    hardwareAccess: false,
  };
}
