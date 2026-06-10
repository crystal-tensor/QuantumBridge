import { createLocalJsonClient } from "./localJsonClient.js";
import { createMockStudioClient } from "./mockStudioClient.js";

export function createStudioClient() {
  const local = createLocalJsonClient();
  const mock = createMockStudioClient(local);
  return {
    loadAll: () => mock.loadAll(),
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
