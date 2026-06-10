import { createStudioClient } from "./api/studioClient.js";
import { Header } from "./components/Header.js";
import { Layout } from "./components/Layout.js";
import { Sidebar } from "./components/Sidebar.js";
import { CatalogPage } from "./pages/CatalogPage.js";
import { WorkflowsPage } from "./pages/WorkflowsPage.js";
import { WorkflowDetailPage } from "./pages/WorkflowDetailPage.js";
import { ExecutePage } from "./pages/ExecutePage.js";
import { BenchmarksPage } from "./pages/BenchmarksPage.js";
import { ResultsPage } from "./pages/ResultsPage.js";
import { ExportsPage } from "./pages/ExportsPage.js";

const ROUTES = {
  catalog: CatalogPage,
  workflows: WorkflowsPage,
  detail: WorkflowDetailPage,
  execute: ExecutePage,
  benchmarks: BenchmarksPage,
  results: ResultsPage,
  exports: ExportsPage,
};

export async function createApp(root) {
  const client = createStudioClient();
  const state = {
    route: "catalog",
    selectedWorkflowId: "aer.qasm_counts_native",
    selectedResultId: null,
    data: await client.loadAll(),
  };

  function navigate(route, payload = {}) {
    state.route = route;
    Object.assign(state, payload);
    render();
  }

  function render() {
    const Page = ROUTES[state.route] || CatalogPage;
    root.innerHTML = Layout({
      sidebar: Sidebar({ route: state.route, navigate }),
      header: Header({ data: state.data }),
      body: Page({ state, client, navigate }),
    });
    wireEvents(root, state, client, navigate, render);
  }

  render();
}

function wireEvents(root, state, client, navigate, render) {
  root.querySelectorAll("[data-route]").forEach((button) => {
    button.addEventListener("click", () => navigate(button.dataset.route));
  });
  root.querySelectorAll("[data-workflow-id]").forEach((button) => {
    button.addEventListener("click", () => navigate("detail", { selectedWorkflowId: button.dataset.workflowId }));
  });
  root.querySelectorAll("[data-execute-workflow]").forEach((button) => {
    button.addEventListener("click", () => navigate("execute", { selectedWorkflowId: button.dataset.executeWorkflow }));
  });
  root.querySelectorAll("[data-result-id]").forEach((button) => {
    button.addEventListener("click", () => navigate("results", { selectedResultId: button.dataset.resultId }));
  });
  root.querySelectorAll("[data-search]").forEach((input) => {
    input.addEventListener("input", () => {
      state[input.dataset.search] = input.value;
      render();
    });
  });
  root.querySelectorAll("[data-filter]").forEach((input) => {
    input.addEventListener("change", () => {
      state[input.dataset.filter] = input.value;
      render();
    });
  });
  const runButton = root.querySelector("[data-run-local]");
  if (runButton) {
    runButton.addEventListener("click", () => {
      state.selectedWorkflowId = root.querySelector("[data-workflow-select]")?.value || state.selectedWorkflowId;
      state.mockExecution = client.mockExecute(state.selectedWorkflowId, collectFormInputs(root));
      state.selectedResultId = state.mockExecution.execution_id;
      render();
    });
  }
}

function collectFormInputs(root) {
  const payload = {};
  root.querySelectorAll("[data-input-name]").forEach((input) => {
    const name = input.dataset.inputName;
    if (input.type === "number") {
      payload[name] = Number(input.value);
    } else if (input.type === "checkbox") {
      payload[name] = Boolean(input.checked);
    } else {
      payload[name] = input.value;
    }
  });
  return payload;
}
