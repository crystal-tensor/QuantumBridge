export function createMockStudioClient(localJsonClient) {
  let cache = null;

  return {
    async loadAll() {
      cache = await localJsonClient.loadAll();
      return cache;
    },
    mockExecute(workflowId, inputs = {}) {
      const sample = cache?.results?.results?.[0] || {};
      const workflow = cache?.workflows?.details?.find((item) => item.workflow_id === workflowId);
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
